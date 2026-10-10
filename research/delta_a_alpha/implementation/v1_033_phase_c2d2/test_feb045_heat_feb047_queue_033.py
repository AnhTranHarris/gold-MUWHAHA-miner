"""Executable, quote-causal FEB045 physical heat and FEB047 L7-profit queue fixtures.

These assert deterministic component correctness, NOT a Feb-optimized PnL replay.
"""
import unittest
from datetime import datetime, timezone
from v1_funded_core_033c import Quote, Structure, Proposal, Limits, FundedEngine
from feb045_physical_heat_feb047_queue_033 import (
    FEB045PhysicalHeatL3,PhysicalHeatConfig045,FEB047QueuedProfitReduceL7,
    StrictQueue047,original_feb_source)
from feb045_source_native_context_033 import (FEB045NativeQualityL3,CausalFeatures045)


def quote(ms, bid=1000000, ask=None):
    return Quote(ms, bid+200 if ask is None else ask, bid)


def structure(ms):
    return Structure('ASIA',1,1,-1,1,ms-500000,'native',
                     completed_bar_end_ms=(ms-500000,)*4)


def limits(**kw):
    base=dict(balance_usd=100000.,max_open=200,max_layer_open=200,
        max_per_source_open=200,max_same_direction=200,max_per_cell_side=200,
        max_orders_per_second=10,max_orders_per_tick=1,max_spread_usd=1,
        max_equity_drawdown_usd=1e6,max_underwater_open_usd=1e6)
    base.update(kw)
    return Limits(**base)


def propose(src=22,side=1,ident='x',ttl_ms=500000):
    return Proposal('L3',f'ORIGINAL_F045_S{src:02d}','native',side,0,0,ttl_ms,
                    source_event_key=ident)


class SourceStub:
    def __init__(self, props=()):self.events=list(props);self.physical=[]
    def on_market_quote(self,q,engine):pass
    def propose(self,q,s,engine):
        out=self.events[:];self.events.clear();return out
    def on_funded_entry(self,p,q,s,engine):self.physical.append(p.id)
    def on_funded_close(self,c,engine):pass


class StaticFeatures:
    def __init__(self,prior=25,imp=1):self.prior=prior;self.imp=imp;self.current=None
    def on_market_quote(self,q,engine):
        self.current=CausalFeatures045(q.time_ms,q.time_ms-1,self.prior,self.imp,10)


class NativeFEBTests(unittest.TestCase):
    def setUp(self):
        self.t=1_800_000_000

    def _heat(self,src=22,side=1,**kwargs):
        stub=SourceStub()
        native=FEB045NativeQualityL3(stub,features=StaticFeatures(),s22_state_cap=200)
        heat=FEB045PhysicalHeatL3(native,PhysicalHeatConfig045(**kwargs))
        engine=FundedEngine(limits(),[heat],broker_contract_verified=True)
        return stub,heat,engine

    def test_original_source_isolation_and_funded_entry_callback(self):
        stub,heat,engine=self._heat(source_cooldown_ms=60000)
        stub.events=[propose(22,ident='first')]
        engine.process_quote(quote(self.t),structure(self.t))
        self.assertEqual(len(engine.positions),1)
        self.assertEqual(stub.physical,[1])
        self.assertIn((22,1),heat.last_actual_entry)
        self.assertEqual(original_feb_source(next(iter(engine.positions.values()))),22)
        stub.events=[propose(22,ident='two')]
        engine.process_quote(quote(self.t+1000),structure(self.t+1000))
        self.assertEqual(len(engine.positions),1)
        self.assertGreaterEqual(heat.denials['FEB045_SAME_SOURCE_FUNDED_COOLDOWN'],1)

    def test_original_source_gap_and_rearm_after_actual_fund(self):
        stub,heat,engine=self._heat(same_source_min_gap_usd=2)
        stub.events=[propose(22,ident='one')]
        engine.process_quote(quote(self.t),structure(self.t))
        stub.events=[propose(22,ident='two')]
        engine.process_quote(quote(self.t+1000,bid=1000500),structure(self.t+1000))
        self.assertEqual(len(engine.positions),1)
        self.assertIn('FEB045_SAME_SOURCE_FUNDED_PRICE_GAP',heat.denials)
        stub.events=[propose(22,ident='three')]
        engine.process_quote(quote(self.t+2000,bid=1003000),structure(self.t+2000))
        self.assertEqual(len(engine.positions),2)

    def test_original_long_down_and_short_up_stress_are_separate(self):
        stub,heat,engine=self._heat(heat_global_usd=5,shock_usd=1)
        # Pre-existing real funded long with entry 1000.2 at bid 1000.
        stub.events=[propose(22,ident='one')]
        engine.process_quote(quote(self.t),structure(self.t))
        stub.events=[propose(22,ident='two')]
        engine.process_quote(quote(self.t+1000,bid=998000),structure(self.t+1000))
        self.assertEqual(len(engine.positions),2)  # 1.2 stressed loss below $5
        stub.events=[propose(22,ident='three')]
        engine.process_quote(quote(self.t+2000,bid=996000),structure(self.t+2000))
        self.assertEqual(len(engine.positions),2)
        self.assertGreater(heat.denials['FEB045_ACCOUNT_DIRECTIONAL_STRESS'],0)

    def test_per_source_stress_and_actual_inventory_not_shadow(self):
        stub,heat,engine=self._heat(heat_s22_usd=1,shock_usd=1)
        stub.events=[propose(22,ident='one')]
        engine.process_quote(quote(self.t),structure(self.t))
        stub.events=[propose(22,ident='two')]
        engine.process_quote(quote(self.t+1000,bid=999000),structure(self.t+1000))
        self.assertEqual(len(engine.positions),1)
        self.assertGreater(heat.denials['FEB045_SOURCE_PHYSICAL_STRESS'],0)
        # Shadow proposals and rejected physical offers NEVER update last actual fill.
        self.assertEqual(heat.last_actual_entry[(22,1)][1],self.t)

    def test_causal_source_policy_does_not_use_calendar_month(self):
        rows=[]
        for m in (1,2,6):
            t=int(datetime(2026,m,9,6,10,tzinfo=timezone.utc).timestamp()*1000)
            stub=SourceStub([propose(22,ident='k')]);native=FEB045NativeQualityL3(stub,features=StaticFeatures())
            h=FEB045PhysicalHeatL3(native,PhysicalHeatConfig045(shock_usd=0.5))
            e=FundedEngine(limits(),[h],broker_contract_verified=True)
            e.process_quote(quote(t),structure(t))
            rows.append((len(e.positions),dict(h.denials)))
        self.assertEqual(rows,[rows[0]]*3)
        self.assertEqual(rows[0][0],1)

    def _fund_many(self,engine,n,t0):
        for i in range(n):
            t=t0+i*1000
            engine.process_quote(quote(t),structure(t),proposals=[propose(22,ident=f'i{i}')])
        self.assertEqual(len(engine.positions),n)

    def test_original_unmodified_feb047_function_agrees_on_first_real_close(self):
        # Execute the ORIGINAL FEB047 source function on an independent tiny
        # accepted-event tape. AST isolates the unchanged function from the
        # original module's research-only absolute-path loading side effects.
        import ast
        import hashlib
        from pathlib import Path
        import numpy as np
        original=Path(__file__).parent/'verified_original_sources'/'FEB047'/'queued_reduce_only_047.py'
        raw=original.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
            '1e3fff9546bb5d5dde0c19ce1340b0b3def284ebaf47e5b570023e275c06f315')
        tree=ast.parse(raw.decode())
        source=next(z for z in tree.body if isinstance(z,ast.FunctionDef) and z.name=='run')
        ns={'njit':lambda fn:fn,'np':np}
        exec(compile(ast.Module(body=[source],type_ignores=[]),str(original),'exec'),ns)
        t=self.t
        tick_ms=np.array([t+i*1000 for i in range(15)],dtype=np.int64)
        bids=np.array([1000000]*15,dtype=np.int32)
        bids[5:10]=1015000;bids[10:]=1011000
        asks=bids+200
        E=np.arange(4,dtype=np.int64);X=np.full(4,14,dtype=np.int64)
        R=asks[E].copy();D=np.ones(4,dtype=np.int8)
        P=np.full(4,(bids[14]-R[0])/1000-.02,dtype=np.float64)
        S=np.full(4,22,dtype=np.int32)
        monitor=np.array([0,5,10],dtype=np.int64)
        ex,px,closed,actions,maxclose,maxorders=ns['run'](
            E,X,R,D,P,S,tick_ms,asks,bids,np.arange(4,dtype=np.int64),
            monitor,2.0,36,7.0,32,60.0,4,True,0.0,10)
        self.assertEqual(closed,1)
        self.assertEqual(actions,1)
        self.assertEqual(ex[0],10)
        self.assertAlmostEqual(px[0],10.78,places=6)
        self.assertEqual(maxclose,1)
        adapter=FEB047QueuedProfitReduceL7(StrictQueue047(
            retreat_usd=2,window_samples=36,min_profit_usd=7,
            close_batch=32,cooldown_seconds=60,side_limit=4))
        e=FundedEngine(limits(),[adapter],broker_contract_verified=True)
        for i in range(15):
            q=Quote(int(tick_ms[i]),int(asks[i]),int(bids[i]))
            entries=[propose(22,ident=f'orig-e{i}') ] if i<4 else ()
            e.process_quote(q,structure(q.time_ms),proposals=entries)
        self.assertEqual(adapter.early_actual_exits,closed)
        early=[c for c in e.closed if c.reason=='FEB047_PROFIT_REDUCE']
        self.assertEqual(len(early),1)
        self.assertEqual(early[0].position_id,1)
        self.assertEqual(early[0].time_ms,int(tick_ms[int(ex[0])]))
        self.assertAlmostEqual(early[0].net_usd,float(px[0]),places=6)

    def test_actual_feb047_profitable_reduce_closes_only_funded(self):
        adapter=FEB047QueuedProfitReduceL7(StrictQueue047(retreat_usd=2,window_samples=36,
            min_profit_usd=7,close_batch=32,cooldown_seconds=60,side_limit=4))
        e=FundedEngine(limits(),[adapter],broker_contract_verified=True)
        self._fund_many(e,4,self.t)
        # Max midpoint after monitor rises $15, then retracts $4; exit remains profitable.
        e.process_quote(quote(self.t+5000,bid=1015000),structure(self.t+5000))
        e.process_quote(quote(self.t+10000,bid=1011000),structure(self.t+10000))
        self.assertEqual(adapter.actions,1)
        self.assertEqual(adapter.early_actual_exits,1)
        self.assertEqual(len(e.positions),3)
        close=e.closed[0]
        self.assertEqual(close.reason,'FEB047_PROFIT_REDUCE')
        self.assertGreaterEqual(close.net_usd,7)
        self.assertEqual(e.score()['combined_max_orders_sec'],1)
        self.assertEqual(e.gross_profit,close.net_usd)

    def test_original_feb047_profitable_short_uses_executable_ask(self):
        adapter=FEB047QueuedProfitReduceL7(StrictQueue047(
            retreat_usd=2,window_samples=36,min_profit_usd=7,
            close_batch=32,cooldown_seconds=60,side_limit=4))
        e=FundedEngine(limits(),[adapter],broker_contract_verified=True)
        for i in range(4):
            t=self.t+i*1000
            e.process_quote(quote(t),structure(t),proposals=[propose(25,side=-1,ident=f'short{i}')])
        e.process_quote(quote(self.t+5000,bid=990000),structure(self.t+5000))
        e.process_quote(quote(self.t+10000,bid=992000),structure(self.t+10000))
        self.assertEqual(adapter.early_actual_exits,1)
        c=e.closed[0]
        self.assertEqual(c.reason,'FEB047_PROFIT_REDUCE')
        self.assertEqual(c.exit_raw,992200)
        self.assertAlmostEqual(c.net_usd,7.78,places=6)

    def test_l7_at_most_one_combined_entry_close_same_quote(self):
        adapter=FEB047QueuedProfitReduceL7(StrictQueue047(
            retreat_usd=2,min_profit_usd=7,side_limit=4,close_batch=32))
        e=FundedEngine(limits(max_orders_per_second=1),[adapter],broker_contract_verified=True)
        self._fund_many(e,4,self.t)
        e.process_quote(quote(self.t+5000,bid=1015000),structure(self.t+5000))
        e.process_quote(quote(self.t+10000,bid=1011000),structure(self.t+10000),
             proposals=[propose(22,ident='same-exit-quote')])
        self.assertEqual(adapter.early_actual_exits,1)
        self.assertEqual(len(e.positions),3)
        self.assertGreater(e.reject_counts.get('ORDER_RATE',0),0)
        self.assertEqual(e.combined_order_rate_max,1)

    def test_delayed_profit_floor_rechecks_executable_bid(self):
        e=FundedEngine(limits(max_orders_per_second=1),broker_contract_verified=True)
        t=self.t
        e.process_quote(quote(t),structure(t),proposals=[propose(22,ident='guard')])
        e.request_profit_reduce(1,minimum_net_usd=7)
        # No remaining order/second, L7 queues protective reduce; different quote, same second.
        e.process_quote(quote(t+100,bid=1011000),structure(t+100))
        self.assertIn(1,e.positions)
        self.assertEqual(len(e._reduction_queue),1)
        # Quote reverses before new order slot. Must CANCEL rather than settle loss.
        e.process_quote(quote(t+1000,bid=1001000),structure(t+1000))
        self.assertIn(1,e.positions)
        self.assertEqual(len(e._reduction_queue),0)
        self.assertEqual(e.closed,[])
        self.assertNotIn(1,e._profit_reduce_guards)
        self.assertIn('FEB047_PROFIT_FLOOR_NOT_EXECUTABLE',[x.get('reason') for x in e.events])

    def test_delayed_profit_guard_settles_only_if_still_profitable(self):
        e=FundedEngine(limits(max_orders_per_second=1),broker_contract_verified=True)
        t=self.t
        e.process_quote(quote(t),structure(t),proposals=[propose(22,ident='guard')])
        e.request_profit_reduce(1,minimum_net_usd=7)
        e.process_quote(quote(t+100,bid=1011000),structure(t+100))
        self.assertEqual(len(e.closed),0)
        e.process_quote(quote(t+1000,bid=1009000),structure(t+1000))
        self.assertEqual(len(e.closed),1)
        self.assertEqual(e.closed[0].reason,'FEB047_PROFIT_REDUCE')
        self.assertGreaterEqual(e.closed[0].net_usd,7)

    def test_unconditional_l7_still_closes_loss_no_new_profit_guard(self):
        e=FundedEngine(limits(),broker_contract_verified=True)
        e.process_quote(quote(self.t),structure(self.t),proposals=[propose(22,ident='a')])
        e.request_reduce(1)
        e.process_quote(quote(self.t+1000,bid=997000),structure(self.t+1000))
        self.assertEqual(len(e.closed),1)
        self.assertEqual(e.closed[0].reason,'L7_REDUCE')
        self.assertLess(e.closed[0].net_usd,0)

    def test_pending_profit_floor_can_never_mask_unconditional_safety_exit(self):
        e=FundedEngine(limits(max_orders_per_second=1),broker_contract_verified=True)
        t=self.t
        e.process_quote(quote(t),structure(t),proposals=[propose(22,ident='safety')])
        e.request_profit_reduce(1,minimum_net_usd=7)
        e.process_quote(quote(t+100,bid=1011000),structure(t+100))
        self.assertIn(1,e._profit_reduce_guards)
        self.assertIn(1,e._reduction_queue)
        # Risk governor observes an independent, unconditional reduce signal.
        e.request_reduce(1)
        self.assertNotIn(1,e._profit_reduce_guards)
        e.process_quote(quote(t+1000,bid=996000),structure(t+1000))
        self.assertEqual(e.closed[0].reason,'L7_REDUCE')
        self.assertLess(e.closed[0].net_usd,0)

    def test_protective_stop_override_after_profitable_reduce_is_rate_limited(self):
        e=FundedEngine(limits(max_orders_per_second=1),broker_contract_verified=True)
        t=self.t
        p=Proposal('L3','ORIGINAL_F045_S22','native',1,0.0,2.0,500000,
                   source_event_key='stop')
        e.process_quote(quote(t),structure(t),proposals=[p])
        e.request_profit_reduce(1,minimum_net_usd=7)
        e.process_quote(quote(t+100,bid=1011000),structure(t+100))
        e.process_quote(quote(t+1000,bid=995000),structure(t+1000))
        self.assertEqual(len(e.closed),1)
        self.assertEqual(e.closed[0].reason,'SL')
        self.assertLess(e.closed[0].net_usd,0)

    def test_profit_request_never_converts_pending_emergency_to_conditional(self):
        e=FundedEngine(limits(),broker_contract_verified=True)
        t=self.t
        e.process_quote(quote(t),structure(t),proposals=[propose(22,ident='priority')])
        e.request_reduce(1)
        e.request_profit_reduce(1,minimum_net_usd=7)
        self.assertNotIn(1,e._profit_reduce_guards)
        e.process_quote(quote(t+1000,bid=995000),structure(t+1000))
        self.assertEqual(e.closed[0].reason,'L7_REDUCE')
        self.assertLess(e.closed[0].net_usd,0)

    def test_strict_feb047_shared_order_configuration_fail_closed(self):
        a=FEB047QueuedProfitReduceL7()
        e=FundedEngine(limits(max_orders_per_tick=2),[a],broker_contract_verified=True)
        with self.assertRaisesRegex(ValueError,'requires shared'):
            e.process_quote(quote(self.t),structure(self.t))
        b=FEB047QueuedProfitReduceL7()
        e=FundedEngine(limits(max_orders_per_second=11),[b],broker_contract_verified=True)
        with self.assertRaisesRegex(ValueError,'requires shared'):
            e.process_quote(quote(self.t),structure(self.t))

    def test_queue_profit_protection_stays_configured_through_week_and_month(self):
        from datetime import timedelta
        dates=(datetime(2026,1,29,12,tzinfo=timezone.utc),
               datetime(2026,2,3,12,tzinfo=timezone.utc),
               datetime(2026,6,3,12,tzinfo=timezone.utc))
        out=[]
        for dt in dates:
            t=int(dt.timestamp()*1000)
            a=FEB047QueuedProfitReduceL7(StrictQueue047(
                retreat_usd=2,min_profit_usd=7,side_limit=4,close_batch=32))
            e=FundedEngine(limits(),[a],broker_contract_verified=True)
            self._fund_many(e,4,t)
            e.process_quote(quote(t+5000,bid=1015000),structure(t+5000))
            e.process_quote(quote(t+10000,bid=1011000),structure(t+10000))
            out.append((a.early_actual_exits,e.closed[0].net_usd,e.closed[0].reason))
        self.assertEqual(out,[out[0]]*3)

    def test_feb047_does_not_reduce_january_or_unrelated_positions(self):
        adapter=FEB047QueuedProfitReduceL7(StrictQueue047(
            retreat_usd=2,min_profit_usd=7,side_limit=4,close_batch=32))
        e=FundedEngine(limits(),[adapter],broker_contract_verified=True)
        for i in range(4):
            t=self.t+i*1000
            e.process_quote(quote(t),structure(t),proposals=[Proposal('L3','JAN039_S26','native',1,0,0,500000,source_event_key=f'jan{i}')])
        e.process_quote(quote(self.t+5000,bid=1015000),structure(self.t+5000))
        e.process_quote(quote(self.t+10000,bid=1011000),structure(self.t+10000))
        self.assertEqual(len(e.positions),4)
        self.assertEqual(adapter.early_actual_exits,0)
        self.assertEqual(adapter.actions,1)  # monitor still observes stress, but only source-owned PnL can reduce

    def test_feb047_no_shadow_positions_no_generated_trades(self):
        adapter=FEB047QueuedProfitReduceL7(StrictQueue047(side_limit=1))
        e=FundedEngine(limits(),[adapter],broker_contract_verified=True)
        for i in range(10):
            t=self.t+i*5000
            e.process_quote(quote(t,1000000+(i%2)*4000),structure(t))
        self.assertEqual(e.positions,{})
        self.assertEqual(adapter.early_actual_exits,0)
        self.assertEqual(e.score()['trades'],0)
        self.assertEqual(e.combined_order_rate_max,0)

if __name__=='__main__':unittest.main()
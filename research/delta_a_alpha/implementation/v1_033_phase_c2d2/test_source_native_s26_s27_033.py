"""Source 26/27 frozen original JAN039 rules, causal inventory and month-blind replay."""
from __future__ import annotations
import json
import unittest
from pathlib import Path
from v1_funded_core_033c import Quote, Structure, Proposal, FundedEngine, Limits
from source_native_s26_s27_033 import (
    S26,S27,SourceNativeS26S27Policy,original_phase,
    S26_LIMIT,S26_NET_FIRST_HIT,S27_NET_FIRST_HIT_BY_PHASE,S27_POSITION_CAP_BY_PHASE)

DATA=Path(__file__).with_name('JAN039_SELECTED_VERIFIED.json')
class SingleSource:
    def __init__(self, source, tp=7):self.source=source;self.tp=tp;self.calls=0
    def propose(self,q,s,e):
        self.calls += 1
        return (Proposal('L3',self.source,'NATIVE_L3',1,self.tp,200,600000,
                         source_event_key=f'ORIGINAL_ORACLE:{self.calls}'),)
    def on_funded_close(self,c,e):pass

class NativeMechanismTests(unittest.TestCase):
    def setUp(self):
        self.frozen=json.loads(DATA.read_text())
        self.params=self.frozen['params']

    def test_matches_frozen_original_source_parameters(self):
        p=self.params
        self.assertEqual(S26_LIMIT,p['original_L3_S26']['source_wide_simultaneous_position_cap'])
        self.assertEqual(S26_NET_FIRST_HIT,p['original_L3_S26']['first_executable_favorable_profit_hit_usd'])
        s=p['original_L3_S27']
        self.assertEqual(S27_NET_FIRST_HIT_BY_PHASE,{0:s['phase0_first_executable_favorable_profit_hit_usd'],2:s['phase2_3_first_executable_favorable_profit_hit_usd'],3:s['phase2_3_first_executable_favorable_profit_hit_usd'],4:s['phase4_first_executable_favorable_profit_hit_usd']})
        self.assertEqual(S27_POSITION_CAP_BY_PHASE,{0:s['phase0_simultaneous_position_cap'],5:s['phase5_simultaneous_position_cap']})

    def _feed(self, src, iso_t, q_prices=((100020,100000),), *, max_open=20):
        import datetime as dt
        base=int(dt.datetime.fromisoformat(iso_t.replace('Z','+00:00')).timestamp()*1000)
        upstream=SingleSource(src)
        policy=SourceNativeS26S27Policy(upstream)
        eng=FundedEngine(Limits(max_open=max_open,max_orders_per_second=30,
             max_orders_per_tick=1,max_margin_fraction_of_equity=.9),[policy],broker_contract_verified=True)
        s=Structure('LONDON',1,1,-1,1,base-1,'ORIGINAL_GRID',completed_bar_end_ms=(base-1,)*4)
        for k,(a,b) in enumerate(q_prices):
            eng.process_quote(Quote(base+k*1000,a,b),s)
        return eng,policy,upstream

    def test_january_and_february_same_phase_identical_mechanism(self):
        # 12:00 is phase0 for BOTH months, no parameter selection by month.
        for day in ['2026-01-09T12:00:00Z','2026-02-09T12:00:00Z','2026-06-09T12:00:00Z']:
            engine,policy,_=self._feed(S27,day)
            self.assertEqual(len(engine.positions),1)
            p=next(iter(engine.positions.values()))
            self.assertEqual(p.tp_raw,60020)
            self.assertEqual(policy._phase_by_funded_id[p.id],0)

    def test_s26_profit_first_hit_is_executable_net_not_hindsight(self):
        eng,policy,_=self._feed(S26,'2026-02-09T12:00:00Z',
                          ((100020,100000),(135060,135040)))
        # Need profit $35.02 gross to hit $35 NET, accounting 0.02 fee.
        self.assertEqual(len(eng.closed),1)
        self.assertGreaterEqual(eng.closed[0].net_usd,35.)
        self.assertEqual(len(eng.positions),0)  # exit used this tick's order budget
        self.assertEqual(eng.reject_counts['ORDER_RATE'],1)

    def test_phase_specific_targets_and_unmatched_phase_passthrough(self):
        for phase,expected in [(0,60),(2,50),(3,50),(4,35),(5,7)]:
            h=12;minute=phase*10
            date=f'2026-02-09T{h:02d}:{minute:02d}:00Z'
            engine,_,_=self._feed(S27,date)
            p=next(iter(engine.positions.values()))
            self.assertEqual(p.tp_raw,round((expected+.02 if phase!=5 else expected)*1000))

    def test_funded_only_phase_inventory_blocks_future_source_proposals(self):
        eng,policy,upstream=self._feed(S27,'2026-01-09T12:00:00Z')
        # Inject genuine paid physical inventory for phase0, no forecast wins.
        p=next(iter(eng.positions.values()))
        for i in range(S27_POSITION_CAP_BY_PHASE[0]-1):
            from dataclasses import replace
            eng.positions[-i-1]=replace(p,id=-i-1)
            policy._phase_by_funded_id[-i-1]=0
        q=Quote(p.entry_ms+1000,100020,100000)
        s=Structure('LONDON',1,1,-1,1,q.time_ms-1,'ORIGINAL_GRID',completed_bar_end_ms=(q.time_ms-1,)*4)
        self.assertEqual(tuple(policy.propose(q,s,eng)),())
        self.assertEqual(policy.denied_source_cap,1)
        self.assertEqual(upstream.calls,2)

    def test_absent_original_source_means_zero_trades(self):
        class Empty(SingleSource):
            def propose(self,q,s,e):return ()
        p=SourceNativeS26S27Policy(Empty(S27))
        t=1770638400000;s=Structure('NY',1,1,-1,1,t-1,'ORIGINAL_GRID',completed_bar_end_ms=(t-1,)*4)
        eng=FundedEngine(Limits(),[p],broker_contract_verified=True)
        eng.process_quote(Quote(t,100020,100000),s)
        self.assertEqual(len(eng.positions),0)
        self.assertEqual(p.forwarded,0)

if __name__=='__main__':unittest.main()

"""Offline deterministic L0-L7 funded-event kernel contract tests.
Not original 131E/134K strategy parity or a broker fill certification.
"""
import unittest
from dataclasses import replace
from v1_funded_core_033 import (FundedEngine, Limits, Proposal, Quote, Structure,
                                OriginalHourlyHeartbeatL3, NullAdapter)


def st(t=2_000_000, h4=1, h1=1, m15=-1, m5=-1, cell='cell'):
    return Structure('LONDON', h4, h1, m15, m5, t - 1000, cell, 0,
                     (t-100000, t-50000, t-10000, t-2000))


def q(t=2_000_000, bid=100000, spread=100):
    return Quote(t, bid+spread, bid)


def p(**kw):
    return Proposal('L3','L3_SOURCE', 'cell', 1, 1.0, 2.0, 120000, **kw)


def engine(**kw):
    return FundedEngine(replace(Limits(), **kw), broker_contract_verified=True)

class Trace(NullAdapter):
    def __init__(self):self.closed=[]
    def on_funded_close(self, close, engine): self.closed.append(close)


class KernelTests(unittest.TestCase):
    def test_owner_contract_fixed_lot(self):
        with self.assertRaises(ValueError):Limits(fixed_lot=0.02)
    def test_absent_broker_details_fails_closed(self):
        e=FundedEngine(Limits());e.process_quote(q(),st(),proposals=[p()]);self.assertFalse(e.positions)
        self.assertEqual(e.reject_counts['BROKER_CONTRACT_UNKNOWN'],1)
    def test_missing_completed_history_fails_closed(self):
        e=engine();s=replace(st(), completed_bar_end_ms=None)
        e.process_quote(q(),s,proposals=[p()]);self.assertFalse(e.positions)
        e.process_quote(q(2_301_000),s);self.assertTrue(e.readiness_deadline_missed)
    def test_actual_quote_bidask_profit_and_fee(self):
        e=engine();e.process_quote(q(),st(),proposals=[p()]);self.assertEqual(len(e.positions),1)
        # Long filled at ask 100.100; bid now 101.200 -> gross +1.10, net +1.08.
        e.process_quote(q(2_001_000,101200),st(2_001_000));self.assertEqual(len(e.positions),0)
        self.assertAlmostEqual(e.closed[0].net_usd,1.08,places=6)
        self.assertAlmostEqual(e.balance,100001.08)
        self.assertAlmostEqual(e.score()['net'],1.08)
    def test_short_quote_side(self):
        e=engine();s=st();p0=Proposal('L3','S','c',-1,1,2,60000)
        e.process_quote(q(),s,proposals=[p0])
        e.process_quote(q(2_001_000,98600),st(2_001_000))
        # short at bid 100; exit at ask 98.700 -> net +1.28
        self.assertAlmostEqual(e.closed[0].net_usd,1.28)
    def test_shadow_parent_never_credits_watchdog(self):
        e=engine(max_open=1)
        e.process_quote(q(),st(),proposals=[p()]);self.assertEqual(set(e.positions),{1})
        e.process_quote(q(2_001_000,100050),st(2_001_000),proposals=[p(parent_id=1234)])
        self.assertNotIn(1234,e._funded_ids)
        self.assertEqual(e.reject_counts['UNFUNDED_OR_UNEARNED_GENEALOGY'],1)
        self.assertFalse(e.campaigns['cell'].earned)
    def test_realized_funded_close_unlocks_watchdog(self):
        e=engine(min_scout_funded_wins=1)
        scout=Proposal('L4','WATCHDOG','wc',1,0.1,10,60000,first_scout=True)
        e.process_quote(q(),st(cell='wc'),proposals=[scout]);self.assertFalse(e.campaigns['wc'].earned)
        e.process_quote(q(2_001_000,100300),st(2_001_000,cell='wc'))
        self.assertTrue(e.campaigns['wc'].earned)
        parent=e.campaigns['wc'].last_good_parent_id; self.assertEqual(parent,1)
        child=Proposal('L4','WATCHDOG','wc',1,0.1,10,60000,parent_id=parent,requires_earned_watchdog=True)
        e.process_quote(q(2_002_000),st(2_002_000,cell='wc'),proposals=[child]);self.assertIn(2,e.positions)
    def test_stop_relocks_earned_watchdog(self):
        e=engine(min_scout_funded_wins=1)
        scout=Proposal('L4','WD','cell',1,1,2,120000,first_scout=True)
        e.process_quote(q(),st(),proposals=[scout])
        e.process_quote(q(2_001_000,101200),st(2_001_000));self.assertTrue(e.campaigns['cell'].earned)
        child=Proposal('L4','WD','cell',1,1,2,120000,parent_id=1,requires_earned_watchdog=True)
        e.process_quote(q(2_002_000),st(2_002_000),proposals=[child])
        e.process_quote(q(2_003_000,97000),st(2_003_000))
        self.assertFalse(e.campaigns['cell'].earned)
        self.assertGreater(e.campaigns['cell'].relocks,0)
    def test_actual_failure_required_for_recovery(self):
        e=engine(max_orders_per_tick=2)
        rec=Proposal('L6','REC','cell',-1,1,1,60000,recovery_of=1)
        e.process_quote(q(),st(),proposals=[rec]);self.assertFalse(e.positions)
        e.process_quote(q(2_001_000),st(2_001_000),proposals=[p()]);self.assertIn(1,e.positions)
        e.process_quote(q(2_002_000,99500),st(2_002_000),proposals=[rec]);self.assertNotIn(2,e.positions)
        self.assertTrue(e.mark_failure(1,q(2_002_000, 99500),st(2_002_000)))
        e.process_quote(q(2_003_000),st(2_003_000),proposals=[rec]);self.assertIn(2,e.positions)
        self.assertEqual(e.positions[2].side,-1)
    def test_reduction_is_physical_exit_not_free_inventory(self):
        e=engine(max_orders_per_second=1, max_orders_per_tick=1)
        e.process_quote(q(),st(),proposals=[p()]);e.request_reduce(1)
        # Same second, combined entry+exit would be 2, so liquidation is queued.
        e.process_quote(q(2_000_100, 99500),st(2_000_100));self.assertIn(1,e.positions)
        e.process_quote(q(2_001_000,99500),st(2_001_000));self.assertNotIn(1,e.positions)
        self.assertEqual(e.combined_order_rate_max,1)
    def test_exact_tick_equity_drawdown_before_recovery(self):
        e=engine()
        e.process_quote(q(),st(),proposals=[Proposal('L3','SRC','cell',1,10,20,60000)])
        e.process_quote(q(2_001_000,95000),st(2_001_000))
        self.assertGreater(e.dd_max,5)
        e.process_quote(q(2_002_000,110200),st(2_002_000))
        self.assertAlmostEqual(e.score()['max_equity_dd'],5.12,places=6)
    def test_portfolio_heat_and_margin_denials(self):
        e=engine(max_underwater_open_usd=0.2)
        e.process_quote(q(),st(),proposals=[p()])
        self.assertEqual(e.reject_counts['PORTFOLIO_HEAT'],1)
        e=engine(balance_usd=100,max_margin_fraction_of_equity=0.1, leverage=10)
        e.process_quote(q(),st(),proposals=[p()])
        self.assertEqual(e.reject_counts['INSUFFICIENT_MARGIN_OR_EQUITY'],1)
    def test_same_second_entry_rate_unified(self):
        e=engine(max_orders_per_second=1,max_orders_per_tick=2)
        e.process_quote(q(),st(),proposals=[p()])
        e.process_quote(q(2_000_200),st(2_000_200),proposals=[Proposal('L3','S2','cell',1,1,2,10000)])
        self.assertEqual(len(e.positions),1)
        self.assertEqual(e.reject_counts['ORDER_RATE'],1)
    def test_original_hourly_source_hours(self):
        hb=OriginalHourlyHeartbeatL3(50)
        t=7*3600*1000+2000
        # Initial 7:00 UTC London heartbeat, eligible already-completed structure.
        e=engine(max_spread_usd=10)
        e.adapters=[hb]
        e.process_quote(q(t),st(t,h4=1,h1=1,m15=-1,m5=-1))
        e.process_quote(q(t+100,101500),st(t+100,h4=1,h1=1,m15=-1,m5=-1))
        self.assertEqual(len(e.positions),1)
        self.assertEqual(next(iter(e.positions.values())).source,'ORIGINAL_HB_019_UTC07')
    def test_source_feedback_receives_only_actual_closes(self):
        x=Trace();e=FundedEngine(Limits(),[x],broker_contract_verified=True)
        e.process_quote(q(),st(),proposals=[p()]);self.assertEqual(len(x.closed),0)
        e.process_quote(q(2_001_000,101200),st(2_001_000));self.assertEqual(len(x.closed),1)
        self.assertEqual(x.closed[0].position_id,1)
    def test_no_trade_month_label_feature(self):
        e=engine();self.assertFalse(hasattr(e,'month'))
        self.assertTrue(e.score()['month_blind'])

if __name__=='__main__':unittest.main(verbosity=2)

# Extra regression tests after Python main guard: unittest discovery executes these.
class CooperationTests(unittest.TestCase):
    class OriginalLikeWd(NullAdapter):
        def __init__(self): self.child_emitted=False
        def propose(self,q,s,e):
            c=e.campaigns['wdcell']
            if q.time_ms==2_000_000:
                return (Proposal('L4','WDSCOUT','wdcell',1,0.1,2,30000,first_scout=True),)
            if c.earned and q.time_ms >= 2_002_000 and not self.child_emitted:
                self.child_emitted=True
                return (Proposal('L4','WDEARNED','wdcell',1,1,2,30000,
                                 parent_id=c.last_good_parent_id,requires_earned_watchdog=True),)
            return ()
    def test_rejected_scout_never_creates_paid_child(self):
        wd=self.OriginalLikeWd();e=FundedEngine(replace(Limits(),max_open=1,min_scout_funded_wins=1),[wd],broker_contract_verified=True)
        e.process_quote(q(1_999_000),st(1_999_000),proposals=[p()]);self.assertEqual(len(e.positions),1)
        e.process_quote(q(2_000_000),st(2_000_000))
        self.assertEqual(e.reject_counts['GLOBAL_CAP'],1)
        e.process_quote(q(2_001_000,101200),st(2_001_000))
        e.process_quote(q(2_002_000),st(2_002_000));self.assertFalse(wd.child_emitted)
        self.assertFalse(e.campaigns['wdcell'].earned)
        self.assertFalse(any(x['event']=='FILL' and x['source']=='WDEARNED' for x in e.events))
    def test_executed_child_cashflow_controls_next_proposal(self):
        def run(profitable):
            wd=self.OriginalLikeWd();e=FundedEngine(replace(Limits(),min_scout_funded_wins=1),[wd],broker_contract_verified=True)
            e.process_quote(q(),st());self.assertEqual(len(e.positions),1)
            # same clock/structural permissions but different actually executed outcome
            e.process_quote(q(2_001_000,100300 if profitable else 99600),st(2_001_000))
            e.process_quote(q(2_002_000),st(2_002_000))
            return any(v['event']=='FILL' and v['source']=='WDEARNED' for v in e.events)
        self.assertTrue(run(True));self.assertFalse(run(False))
    def test_scout_family_can_earn_four_realisations(self):
        e=engine(min_scout_funded_wins=4, max_orders_per_second=3)
        root=Proposal('L4','SCOUT','cell',1,.10,4,30000,first_scout=True)
        e.process_quote(q(),st(),proposals=[root]);self.assertFalse(e.campaigns['cell'].earned)
        for k in range(1,4):
            t=2_000_000+2*k*1000
            child=Proposal('L4','SCOUT_CHILD','cell',1,.1,4,30000,first_scout=True,parent_id=1)
            e.process_quote(q(t),st(t),proposals=[child])
        # Advance positive tick: all four closes are actual and paid; combined
        # quote-order cap queues remaining exits, so needs 4 consecutive quotes.
        for k in range(8,12):
            t=2_000_000+k*1000
            e.process_quote(q(t,101000),st(t))
        self.assertEqual(len(e.closed),4)
        self.assertTrue(e.campaigns['cell'].earned)
    def test_recovery_parent_budget_is_one(self):
        e=engine(max_orders_per_second=4,max_orders_per_tick=3)
        e.process_quote(q(),st(),proposals=[p()])
        badq=q(2_002_000,99500);e.process_quote(badq,st(2_002_000))
        self.assertTrue(e.mark_failure(1,badq,st(2_002_000)))
        rec=Proposal('L6','RC','cell',-1,1,2,10000,recovery_of=1)
        e.process_quote(q(2_003_000,99500),st(2_003_000),proposals=[rec]);self.assertIn(2,e.positions)
        e.process_quote(q(2_004_000,99500),st(2_004_000),proposals=[rec])
        self.assertEqual(e._recovery_counts[1],1)
        self.assertEqual(e.reject_counts['UNFUNDED_OR_UNEARNED_GENEALOGY'],1)
    def test_profit_from_other_layer_not_paid_watchdog_credit(self):
        e=engine(min_scout_funded_wins=1)
        e.process_quote(q(),st(),proposals=[p()]);e.process_quote(q(2_001_000,101200),st(2_001_000))
        self.assertFalse(e.campaigns['cell'].earned)
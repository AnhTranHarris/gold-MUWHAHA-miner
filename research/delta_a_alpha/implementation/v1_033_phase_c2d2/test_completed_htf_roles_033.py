"""DAA033: source-neutral causal L2 completed OHLC ROLE interfaces, no signal voting."""
from __future__ import annotations
import unittest
from v1_funded_core_033c import Quote
from completed_htf_roles_033 import CompletedHTFRoles


def feed(x,t,b=100000,spread=50):
    x.on_quote(Quote(t,b+spread,b))


class CompletedHTFRolesTests(unittest.TestCase):
    def test_only_completed_bars_and_initial_partial_cannot_be_used(self):
        x=CompletedHTFRoles()
        feed(x,60000)
        self.assertIsNone(x.snapshot(60000))
        with self.assertRaises(ValueError):x.snapshot(60001)
        # At first boundary the first H4 is derived from an incomplete bar.
        feed(x,14_400_000)
        self.assertIsNone(x.snapshot(14_400_000))
        feed(x,17_000_000)
        self.assertIsNone(x.snapshot(17_000_000))
        feed(x,28_800_000)
        self.assertIsNone(x.snapshot(28_800_000))  # boundary quote is not past bar end
        feed(x,28_800_001)
        snap=x.snapshot(28_800_001)
        self.assertIsNotNone(snap)
        self.assertEqual((snap.h4_environment.interval_start_ms,
                          snap.h4_environment.interval_end_ms),
                          (14_400_000,28_800_000))
        self.assertEqual(tuple(snap.bars()),('H4','H1','M15','M5'))

    def test_no_synthetic_bars_during_quote_gap(self):
        x=CompletedHTFRoles()
        feed(x,0)
        feed(x,60_000,b=100100)
        feed(x,36_000_000,b=101000)
        self.assertGreater(x.missing_intervals['M5'],0)
        self.assertEqual(x._completed['M5'].interval_end_ms,300000)
        self.assertEqual(x._completed['M5'].close_bid,100100)
        self.assertFalse(x._completed['M5'].observed_from_bucket_start)
        self.assertIsNone(x.snapshot(36_000_000))

    def test_ohlc_true_bid_ask_and_complete_role_separation(self):
        x=CompletedHTFRoles()
        for t,b in [(0,100000),(14_400_000,100100),(17_000_000,100200),
                    (20_000_000,99700),(24_000_000,100900),
                    (28_800_000,100500),(28_800_001,100300)]:
            feed(x,t,b=b)
        s=x.snapshot(28_800_001)
        self.assertEqual(s.h4_environment.high_bid,100900)
        self.assertEqual(s.h4_environment.low_bid,99700)
        self.assertEqual(s.h4_environment.open_bid,100100)
        self.assertEqual(s.h4_environment.close_bid,100900)
        self.assertEqual(s.h4_environment.high_ask,100950)
        self.assertEqual(s.h4_environment.role,'environment')
        self.assertEqual(s.h1_parent_location.role,'parent_location')
        self.assertEqual(s.m15_phase.role,'phase')
        self.assertEqual(s.m5_transfer.role,'transfer')

    def test_requires_all_role_classifiers_not_ema_sign_proxy(self):
        x=CompletedHTFRoles()
        for t in [0,14_400_000,17_000_000,20_000_000,28_800_000,28_800_001]:
            feed(x,t)
        with self.assertRaises(ValueError):
            x.as_structure(session='ASIA',grid_key='GRID1',classify={'H4':lambda b:1})
        seen=[]
        def classify(name):
            def fn(bar):
                seen.append((name,bar.role,bar.interval_end_ms))
                return {'H4':1,'H1':-1,'M15':0,'M5':1}[name]
            return fn
        result=x.as_structure(session='ASIA',grid_key='GRID1',
                              classify={tf:classify(tf) for tf in ('H4','H1','M15','M5')})
        self.assertEqual((result.h4,result.h1,result.m15,result.m5),(1,-1,0,1))
        self.assertTrue(result.valid_at(28_800_001))
        self.assertEqual(len(seen),4)

    def test_strict_order_and_no_lookahead(self):
        x=CompletedHTFRoles()
        feed(x,1_000_000)
        with self.assertRaises(ValueError):feed(x,999_999)
        with self.assertRaises(ValueError):x.snapshot(1_000_001)

    def test_l2_context_controls_physical_l7_entry_after_missing_history(self):
        from v1_funded_core_033c import FundedEngine, Limits, Proposal
        roles=CompletedHTFRoles()
        engine=FundedEngine(Limits(max_orders_per_second=20), broker_contract_verified=True)
        classify={tf:(lambda bar:1) for tf in ('H4','H1','M15','M5')}
        valid_entries=0
        for i,t in enumerate((0,14_400_000,17_000_000,20_000_000,28_800_000,28_800_001)):
            q=Quote(t,100050,100000)
            roles.on_quote(q)
            context=roles.as_structure(session='TEST',grid_key='SOURCED_GRID',classify=classify)
            offered=(Proposal('L3','TEST_SOURCE','SOURCED_GRID',1,0.5,0.5,60000,
                      source_event_key=f'C2D3D_FIXTURE:{i}'),)
            engine.process_quote(q,context,proposals=offered)
            if context is None:self.assertEqual(len(engine.positions),0)
            else:valid_entries+=1
        self.assertEqual(valid_entries,1)
        self.assertEqual(len(engine.positions),1)
        self.assertTrue(engine.readiness_deadline_missed)
        self.assertTrue(engine.had_ready_context)
        self.assertGreater(engine.history_missing,0)

if __name__ == '__main__':unittest.main()

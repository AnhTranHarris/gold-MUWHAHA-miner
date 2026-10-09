"""V1 L0/L7 invariant: exits, floating mark and queued risk cuts are unconditional.

Tests use deterministic synthetic quotes; they do not certify Coinexx fills or
full native original 049/119/131E/134K source generation.
"""
import unittest
from dataclasses import replace
from test_v1_funded_core_033 import q, st, p, engine
from v1_funded_core_033 import Proposal


class OfflineContextFailureTests(unittest.TestCase):
    def test_take_profit_executes_even_without_completed_structure(self):
        e = engine()
        e.process_quote(q(), st(), proposals=[p()])
        assert 1 in e.positions
        e.process_quote(q(2_001_000, 101200), None)
        self.assertEqual(len(e.positions), 0)
        self.assertEqual(e.closed[0].reason, 'TP')
        self.assertAlmostEqual(e.score()['net'], 1.08, 7)

    def test_stop_loss_executes_during_incomplete_history(self):
        e = engine()
        e.process_quote(q(), st(), proposals=[p()])
        absent = replace(st(2_001_000), completed_bar_end_ms=None)
        e.process_quote(q(2_001_000, 97700), absent)
        self.assertEqual(e.closed[0].reason, 'SL')
        self.assertAlmostEqual(e.closed[0].net_usd, -2.42)

    def test_expiration_executes_without_structure(self):
        e = engine()
        short_life = Proposal('L3', 'test', 'cell', 1, 10, 10, 500)
        e.process_quote(q(), st(), proposals=[short_life])
        e.process_quote(q(2_000_500, 100000), None)
        self.assertEqual(e.closed[0].reason, 'TIME')
        self.assertEqual(len(e.positions), 0)

    def test_reduce_only_executes_without_htf_data(self):
        e = engine()
        e.process_quote(q(), st(), proposals=[p()])
        e.request_reduce(1)
        e.process_quote(q(2_000_100), None)
        self.assertEqual(e.closed[0].reason, 'L7_REDUCE')

    def test_exit_remains_funded_and_exposed_when_order_rate_exhausted(self):
        e = engine(max_orders_per_second=1)
        # Wide protective stop prevents the SL taking priority over the queued L7 reduction.
        e.process_quote(q(), st(), proposals=[Proposal('L3','SRC','cell',1,50,50,60000)])
        e.request_reduce(1)
        e.process_quote(q(2_000_100, 95000), None)
        self.assertIn(1, e.positions)
        self.assertGreater(e.dd_max, 5)
        self.assertEqual(e.combined_order_rate_max, 1)
        e.process_quote(q(2_001_000, 95000), None)
        self.assertNotIn(1, e.positions)
        self.assertEqual(e.closed[0].reason, 'L7_REDUCE')

    def test_source_proposals_fail_closed_during_htf_dropout(self):
        e = engine()
        e.process_quote(q(), st(), proposals=[p()])
        e.process_quote(q(2_001_000,101200), None, proposals=[Proposal('L3','bad','cell',1,1,1,5000)])
        self.assertEqual(len(e.closed),1)
        self.assertEqual(len(e.positions),0)
        self.assertEqual(len([x for x in e.events if x['event']=='FILL']),1)

    def test_direct_enter_cannot_claim_future_quote(self):
        e = engine()
        e.process_quote(q(),st())
        self.assertIsNone(e.enter(q(2_002_000),st(2_002_000),p()))
        self.assertEqual(e.reject_counts['NOT_CURRENT_QUOTE'],1)
        self.assertFalse(e.positions)

    def test_missing_htf_no_entry_dd_capture_and_no_phantom_close(self):
        e = engine(max_orders_per_second=1)
        e.process_quote(q(), st(), proposals=[Proposal('L3','src','cell',1,50,50,20000)])
        e.process_quote(q(2_000_100,95000), None)
        self.assertGreaterEqual(e.dd_max,5.1)
        self.assertEqual(len(e.closed),0)
        self.assertEqual(len(e.positions),1)


if __name__ == '__main__':
    unittest.main()
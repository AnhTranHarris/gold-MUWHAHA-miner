"""C2D3 deterministic combined-order queue stress — research broker only.

No real-Dukascopy backtest, no broker acceptance certification.  These tests
are intentionally separate from original 084 geometry source parity: L7
denials and physical-order limits must cause *causal divergence*.
"""
import unittest

from test_funded_084_l7_bridge_033c2d2 import (
    T, Funded084L7Bridge, drive, engine, parent
)


class CombinedPhysicalQueueStress(unittest.TestCase):

    def test_parent_close_and_child_reduce_share_same_second_order_budget(self):
        wd = Funded084L7Bridge()
        e = engine(wd, per_second=1, per_tick=1)
        drive(e, T, proposals=(parent('C2D3:P0'),))
        owner = next(iter(wd.windows))
        drive(e, T + 1000)
        child = wd.actual_live_child[owner]
        e.request_reduce(owner)
        drive(e, T + 2000, bid=100000)
        self.assertNotIn(owner, e.positions)
        self.assertIn(child, e.positions)
        # The child cannot be *assumed* liquidated at the parent exit, nor at
        # another quote in that already consumed order second.
        drive(e, T + 2001, bid=99000)
        self.assertIn(child, e.positions)
        self.assertEqual(len(wd.funded_close_events), 0)
        self.assertGreater(e.dd_max, 0)
        drive(e, T + 3000, bid=99000)
        self.assertNotIn(child, e.positions)
        self.assertEqual(len(wd.funded_close_events), 1)
        self.assertLess(wd.funded_close_events[0][5], 0)
        self.assertLessEqual(e.combined_order_rate_max, 1)

    def test_denied_child_at_global_cap_never_enters_084_ledger(self):
        wd = Funded084L7Bridge()
        e = engine(wd, cap=1)
        drive(e, T, proposals=(parent('C2D3:P0'),))
        owner = next(iter(wd.windows))
        drive(e, T + 1000)
        self.assertGreater(e.reject_counts['GLOBAL_CAP'], 0)
        self.assertEqual(wd.children_funded[owner], 0)
        self.assertNotIn(owner, wd.actual_live_child)
        self.assertEqual(wd.funded_entry_events, [])
        self.assertEqual(wd.funded_close_events, [])
        self.assertFalse(wd.cell_earned[wd.windows[owner].cell])

    def test_spread_rejection_does_not_backfill_favorable_exit(self):
        wd = Funded084L7Bridge()
        e = engine(wd)
        drive(e, T, proposals=(parent('C2D3:P0'),))
        owner = next(iter(wd.windows))
        drive(e, T + 1000, bid=100000, spread=5000)
        self.assertGreater(e.reject_counts['SPREAD'], 0)
        self.assertEqual(wd.children_funded[owner], 0)
        # Favorable movement occurred before physical L7 acceptance.
        # The new order must enter at the executable NOW quote, not old price.
        drive(e, T + 2000, bid=102000)
        self.assertEqual(wd.children_funded[owner], 1)
        self.assertEqual(len(wd.funded_close_events), 0)
        live = e.positions[wd.actual_live_child[owner]]
        self.assertEqual(live.entry_raw, 102100)
        drive(e, T + 3000, bid=102100)
        self.assertEqual(len(wd.funded_close_events), 0)
        drive(e, T + 4000, bid=103500)
        self.assertEqual(len(wd.funded_close_events), 1)

    def test_tp_exit_queued_after_same_second_entry_remains_marked(self):
        wd = Funded084L7Bridge()
        e = engine(wd, per_second=1, per_tick=1)
        drive(e, T, proposals=(parent('C2D3:P0'),))
        drive(e, T + 1)
        self.assertEqual(len(wd.funded_entry_events), 0)
        drive(e, T + 1000)
        owner = next(iter(wd.windows))
        child = wd.actual_live_child[owner]
        # Favorable TP appears within the same order-rate second.
        drive(e, T + 1001, bid=102000)
        self.assertIn(child, e.positions)
        self.assertEqual(len(wd.funded_close_events), 0)
        drive(e, T + 2000, bid=102000)
        self.assertNotIn(child, e.positions)
        self.assertEqual(len(wd.funded_close_events), 1)
        self.assertLessEqual(e.combined_order_rate_max, 1)


if __name__ == '__main__':
    unittest.main()

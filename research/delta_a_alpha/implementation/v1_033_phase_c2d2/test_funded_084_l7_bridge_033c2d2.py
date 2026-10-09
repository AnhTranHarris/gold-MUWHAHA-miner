"""C2D2 physical-acceptance and changed-outcome regression tests.

These are deterministic research-broker fixtures, not Coinexx certification.
They exercise the C2C funded kernel's actual L7 entry/exit callbacks.
"""
import unittest
from dataclasses import replace
from v1_funded_core_033c import Quote, Structure, Proposal, Limits, FundedEngine
from funded_084_l7_bridge_033c2d2 import Funded084L7Bridge

T = 1769191200000


def q(t, bid=100000, spread=100):
    return Quote(t, bid + spread, bid)


def s(t):
    return Structure('NY', 1, 1, -1, -1, t-1, 'grid', 0,
                     (t-14400001, t-3600001, t-900001, t-300001))


def parent(key):
    return Proposal('L3', 'ORIGINAL_049_UNION_UTC17', 'grid', 1, 0, 0,
                    120000, source_event_key=key)


def engine(wd, *, cap=40, per_tick=1, per_second=5):
    lim = replace(Limits(), max_open=cap, max_layer_open=cap,
                  max_per_source_open=cap, max_same_direction=cap,
                  max_per_cell_side=cap, max_orders_per_tick=per_tick,
                  max_orders_per_second=per_second)
    return FundedEngine(lim, [wd], broker_contract_verified=True)


def drive(e, t, bid=100000, spread=100, proposals=()):
    e.process_quote(q(t, bid, spread), s(t), proposals=proposals)


class PhysicallyFunded084(unittest.TestCase):
    def test_first_child_requires_next_quote_after_real_parent_fill(self):
        wd = Funded084L7Bridge()
        e = engine(wd)
        drive(e, T, proposals=(parent('P:0'),))
        self.assertEqual(wd.admitted_parent_windows, 1)
        self.assertEqual(len(wd.funded_entry_events), 0)
        self.assertEqual(sum(p.layer == 'L4' for p in e.positions.values()), 0)
        drive(e, T+1000)
        self.assertEqual(len(wd.funded_entry_events), 1)
        self.assertEqual(wd.funded_entry_events[0][0], 1)
        self.assertEqual(wd.children_funded[next(iter(wd.windows))], 1)

    def test_spread_denial_cannot_consume_first_child_or_rearm_credit(self):
        wd = Funded084L7Bridge()
        e = engine(wd)
        drive(e, T, proposals=(parent('P:0'),))
        owner = next(iter(wd.windows))
        drive(e, T+1000, spread=5000)
        self.assertGreater(e.reject_counts['SPREAD'], 0)
        self.assertNotIn(owner, wd.actual_live_child)
        self.assertEqual(wd.children_funded[owner], 0)
        self.assertEqual(wd.funded_entry_events, [])
        self.assertEqual(wd.funded_close_events, [])
        self.assertFalse(e.campaigns[wd.windows[owner].cell].scout_consumed)
        drive(e, T+2000)
        self.assertEqual(wd.children_funded[owner], 1)
        self.assertEqual(len(wd.funded_entry_events), 1)

    def test_actual_close_controls_next_child_and_altered_exit_diverges(self):
        wa, wb = Funded084L7Bridge(), Funded084L7Bridge()
        ea, eb = engine(wa), engine(wb)
        for e in (ea, eb):
            drive(e, T, proposals=(parent('P:0'),))
            drive(e, T+1000)
        drive(ea, T+2000, bid=102000)  # Actual favorable TP close
        drive(eb, T+2000, bid=100000)  # No observed TP close
        self.assertEqual(len(wa.funded_close_events), 1)
        self.assertEqual(len(wb.funded_close_events), 0)
        drive(ea, T+3000, bid=102000)  # New child can be funded after close
        drive(eb, T+3000, bid=102000)  # Only NOW closes old child
        self.assertEqual(len(wa.funded_entry_events), 2)
        self.assertEqual(len(wb.funded_entry_events), 1)
        self.assertEqual(len(wb.funded_close_events), 1)

    def test_rearm_requires_executable_favorable_quote_after_real_exit(self):
        wd = Funded084L7Bridge(rearm_raw=200)
        e = engine(wd)
        drive(e, T, proposals=(parent('P:0'),))
        drive(e, T+1000)
        drive(e, T+2000, bid=102000)  # actually funded L4 TP
        self.assertEqual(len(wd.funded_entry_events), 1)
        drive(e, T+3000, bid=102100)  # below 200 raw from real exit
        self.assertEqual(len(wd.funded_entry_events), 1)
        drive(e, T+4000, bid=102200)
        self.assertEqual(len(wd.funded_entry_events), 2)

    def test_adverse_reduce_relocks_window_without_phantom_win(self):
        wd = Funded084L7Bridge()
        e = engine(wd)
        drive(e, T, proposals=(parent('P:0'),))
        drive(e, T+1000)
        owner = next(iter(wd.windows))
        child = wd.actual_live_child[owner]
        e.request_reduce(child)
        drive(e, T+2000, bid=99000)
        self.assertEqual(len(wd.funded_close_events), 1)
        self.assertLess(wd.funded_close_events[0][5], 0)
        self.assertIn(owner, wd.invalid_terminated_windows)
        drive(e, T+3000, bid=103000)
        self.assertEqual(wd.children_funded[owner], 1)
        self.assertFalse(wd.cell_earned[wd.windows[owner].cell])

    def test_parent_close_queues_actual_child_exit_subject_to_order_limit(self):
        wd = Funded084L7Bridge()
        e = engine(wd, per_tick=1)
        drive(e, T, proposals=(parent('P:0'),))
        drive(e, T+1000)
        owner = next(iter(wd.windows))
        child = wd.actual_live_child[owner]
        e.request_reduce(owner)
        drive(e, T+2000, bid=100000)
        self.assertNotIn(owner, e.positions)
        self.assertIn(child, e.positions)  # one/tick, no phantom liquidation
        self.assertFalse(wd.windows[owner].active)
        drive(e, T+3000, bid=99500)
        self.assertNotIn(child, e.positions)
        self.assertEqual(len(wd.funded_close_events), 1)
        self.assertEqual(len(wd.funded_entry_events), 1)
        self.assertLessEqual(e.combined_order_rate_max, e.limits.max_orders_per_second)

    def test_rejected_second_parent_is_not_window_or_credit(self):
        wd = Funded084L7Bridge()
        e = engine(wd, cap=1)
        drive(e, T, proposals=(parent('P:0'),))
        drive(e, T+1000, proposals=(parent('P:1'),))
        self.assertEqual(wd.admitted_parent_windows, 1)
        self.assertGreater(e.reject_counts['GLOBAL_CAP'], 0)
        self.assertEqual(wd.children_funded[next(iter(wd.windows))], 0)
        self.assertEqual(wd.earned_parent_admissions, 0)

    def test_protective_closes_work_when_completed_history_disappears(self):
        wd = Funded084L7Bridge()
        e = engine(wd)
        drive(e, T, proposals=(parent('P:0'),))
        drive(e, T+1000)
        e.process_quote(q(T+2000, bid=102000), None)
        self.assertEqual(len(wd.funded_close_events), 1)
        self.assertEqual(len(wd.funded_entry_events), 1)  # new trade fail closed
        self.assertGreater(e.history_missing, 0)
        self.assertEqual(len([x for x in e.positions.values() if x.layer == 'L4']), 0)


if __name__ == '__main__':
    unittest.main()

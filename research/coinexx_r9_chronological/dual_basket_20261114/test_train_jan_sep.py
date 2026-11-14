"""Fast 100%-synthetic invariant tests. No raw files or data downloads."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
for sub in ("src", "variable_cash_horizon_20261114", "dual_basket_20261114"):
    sys.path.insert(0, str(ROOT / sub))

from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config
from on_policy_cash_replay import ResearchCash
from dual_basket import DualBasketBaseline, FEATURE_NAMES
from train_jan_sep import (
    CUTOFF_QUANTILES, FIT_MONTHS, FROZEN_MONTH,
    LabeledEntry, MONTHS, FrozenAdmission, choose_predeclared_cutoff,
    diag, embargoed_fit, labeled_positions, main,
)


def feature(side=1):
    return (side, 15., 25., 2., -999., 15., 1., 1., 6.,
            200., 13., 3., .5, -.4)


def entry(month="01", net=0., ordinal=1, time_msc=150_000):
    return LabeledEntry(month, ordinal, time_msc, feature(), net, 1)


def quote(n, second, bid):
    return Tick(n, second, 1000 * second + n, bid, bid + 10)


class FakeModel:
    def __init__(self, value=-.5):
        self.value = value

    def predict(self, arr):
        return [self.value] * len(arr)


class EntryTrainingTests(unittest.TestCase):
    def test_fixed_month_split_and_disjoint_holdout(self):
        self.assertEqual(FIT_MONTHS, ("01", "02", "03", "04", "05", "06"))
        self.assertNotIn(FROZEN_MONTH, FIT_MONTHS)
        self.assertEqual(len(MONTHS), 9)

    def test_entry_features_are_asof_and_full_schema(self):
        sim = DualBasketBaseline(R9Config())
        sim._start_minute_cycle(quote(1, 120, 1000))
        sim._qualifying_lanes = ("5s_basket_15s_breakout",)
        # Direct deterministic feature generation does not need future bars.
        sim._breakout_levels = lambda now, width: None
        snap = sim.entry_features(quote(2, 122, 1050), 1)
        self.assertEqual(len(snap), len(FEATURE_NAMES))
        self.assertEqual(snap[0], 1.)
        self.assertEqual(snap[1], 50.)
        self.assertEqual(snap[2], 50.)
        self.assertEqual(snap[3], -999.)
        self.assertEqual(snap[4], -999.)
        self.assertEqual(snap[6], 1.)
        self.assertEqual(snap[7], 2.)
        self.assertEqual(snap[8], 2.)

    def test_new_entry_capture_cannot_pull_future_exit(self):
        sim = DualBasketBaseline(R9Config())
        sim._start_minute_cycle(quote(1, 120, 1000))
        sim._gate = lambda tick: True
        sim._quality = lambda side: True
        sim._breakout_levels = lambda now, window: (2010, 2000)
        sim._process_entries(quote(2, 121, 1050))
        self.assertEqual(len(sim.entries), 1)
        observed = sim.entries[0]
        self.assertEqual(len(observed["features"]), len(FEATURE_NAMES))
        self.assertNotIn("net_cash", observed)
        self.assertNotIn("exit_price_u", observed)

    def test_selector_rejection_keeps_risk_slots_and_position_empty(self):
        sim = DualBasketBaseline(R9Config())
        sim._start_minute_cycle(quote(1, 120, 1000))
        sim._gate = lambda tick: True
        sim._quality = lambda side: True
        sim._breakout_levels = lambda now, width: (2010, 2000)
        sim.entry_selector = FrozenAdmission(FakeModel(-1.), cutoff=0.)
        sim._process_entries(quote(2, 121, 1050))
        self.assertEqual(len(sim.entries), 0)
        self.assertIsNone(sim.position)
        self.assertEqual(sim._entries_in_minute, 0)
        self.assertEqual(sim.stats["dual_frozen_model_reject"], 1)
        # A later favorable quote is re-evaluated, never synthetically filled.
        sim.entry_selector = FrozenAdmission(FakeModel(1.), cutoff=0.)
        sim._process_entries(quote(3, 122, 1070))
        self.assertEqual(len(sim.entries), 1)
        self.assertEqual(sim._entries_in_minute, 1)

    def test_same_model_acceptance_never_fabricates_missing_features(self):
        selector = FrozenAdmission(FakeModel(), 0.)
        with self.assertRaises(ValueError):
            selector.accept((1., 2.))

    def test_trade_labels_exactly_join_entry_ordinal_and_month(self):
        rows = [{
            "ordinal": 12, "features": list(feature()),
            "time_msc": 123456789, "side": 1
        }, {
            "ordinal": 32, "features": list(feature(-1)),
            "time_msc": 223456789, "side": -1
        }]
        trades = [
            SimpleNamespace(entry_ordinal=12, entry_time_msc=123456789,
                            net_price_u=50, side=1),
            SimpleNamespace(entry_ordinal=32, entry_time_msc=223456789,
                            net_price_u=-70, side=-1),
        ]
        bounds = [20, 40] + [50 + n for n in range(7)]
        found = labeled_positions(rows, trades, bounds, MONTHS, ResearchCash())
        self.assertEqual([r.month for r in found], ["01", "02"])
        self.assertAlmostEqual(found[0].modeled_net_cash, .30)
        self.assertAlmostEqual(found[1].modeled_net_cash, -.90)

    def test_duplicate_ordinal_is_hard_failure(self):
        d = {"ordinal": 1, "features": list(feature())}
        with self.assertRaises(ValueError):
            labeled_positions([d, d], [], list(range(1, 10)), MONTHS,
                              ResearchCash())

    def test_120_second_embargo_purges_june_boundary(self):
        cutover = 1_000_000
        data = [
            entry("06", ordinal=1, time_msc=cutover - 120_001),
            entry("06", ordinal=2, time_msc=cutover - 120_000),
            entry("06", ordinal=3, time_msc=cutover - 40),
            entry("07", ordinal=4, time_msc=cutover + 1),
        ]
        self.assertEqual([r.ordinal for r in embargoed_fit(data, cutover)], [1])

    def test_no_gate_fallback_if_july_never_positive(self):
        data = [entry("07", net=-.20, ordinal=i) for i in range(100)]
        predicted = [float(i) for i in range(100)]
        cutoffs = {q: 0. if q else float("-inf") for q in CUTOFF_QUANTILES}
        winner, audit = choose_predeclared_cutoff(data, predicted, cutoffs)
        self.assertEqual(winner, 0.)
        self.assertIn("0.05", audit)
        self.assertLessEqual(audit["0.05"]["offline_original_net"], 0.)

    def test_gating_offline_subset_is_marked_not_on_policy(self):
        data = [entry("07", net=x, ordinal=i) for i, x in enumerate((1., -.5))]
        result = diag(data, [2., 1.], 1.5)
        self.assertEqual(result["offline_kept"], 1)
        self.assertIn("OFF-POLICY", result["warning"])

    def test_missing_original_month_files_fail_before_training(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = SimpleNamespace(months=list(MONTHS), data=Path(tmp),
                                   receipt=Path(tmp) / "receipt.zip")
            with self.assertRaises(FileNotFoundError):
                main(args)

    def test_required_month_order_cannot_be_permuted(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = SimpleNamespace(months=list(reversed(MONTHS)),
                                   data=Path(tmp), receipt=Path(tmp) / "r.zip")
            with self.assertRaises(ValueError):
                main(args)


if __name__ == "__main__":
    unittest.main()

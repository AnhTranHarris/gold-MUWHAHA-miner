"""Micro180 V12 causal event-clock acceptance tests (fixtures, not history)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent
for p in (
    PARENT / "src", PARENT / "variable_cash_horizon_20261114",
    PARENT / "dual_basket_20261114", ROOT,
):
    sys.path.insert(0, str(p))

from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config, R9HybridGateBaseline
from v12_coinexx_virtualclock_entry import (
    CompletedSecondHorizon, FEATURE_NAMES, Micro180V12VirtualClock,
    V12EntrySpec, FrozenLightGBMScore,
)


def tick(i: int, msec: int, bid: int, spread: int = 19) -> Tick:
    return Tick(i, msec // 1000, msec, bid, bid + spread)


class BuyOnly:
    def score(self, x):
        # A frozen stand-in model explicitly dependent on side-adjusted
        # directional barrier, never teacher time, target price or labels.
        return .95 if x[3] >= -10 and x[4] >= 0 else .02


class AlwaysHigh:
    def score(self, x):
        return .98


class VirtualClockContracts(unittest.TestCase):
    def test_research_contract_rejects_real_orders_and_teacher_signal(self):
        for kwargs in ({"permit_broker_orders": True},
                       {"teacher_reference_at_decision": True},
                       {"max_legs_per_minute": 3},
                       {"threshold": 0}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                V12EntrySpec(**kwargs)

    def make(self, **kwargs):
        return Micro180V12VirtualClock(
            R9Config(use_regime_gate=False, max_same_minute_rearms=1),
            scorer=AlwaysHigh(),
            spec=V12EntrySpec(**kwargs),
        )

    def test_only_next_real_quote_executes_an_autonomous_signal(self):
        m = self.make()
        t0 = tick(1, 120035, 10000, 19)
        m.on_tick(t0)
        self.assertEqual(m.v12_counts["independent_signal_committed"], 1)
        self.assertEqual(len(m.entries), 0)
        self.assertEqual(m.entry_intent.next_second_start_ms, 121000)
        m.on_tick(tick(2, 120700, 10005, 19))
        self.assertEqual(len(m.entries), 0)
        m.on_tick(tick(3, 121204, 10008, 19))
        self.assertEqual(len(m.entries), 1)
        e = m.entries[0]
        self.assertEqual(e["time_msc"], 121204)
        self.assertEqual(e["price_u"], 10027)  # observed executable Ask
        self.assertEqual(e["v12_signal_ms"], 120035)
        self.assertEqual(e["v12_target_second_start_ms"], 121000)
        self.assertEqual(e["v12_actual_quote_delay_ms"], 1169)
        self.assertTrue(e["v12_no_teacher_event_at_decision"])
        self.assertEqual(e["v10_entry_authority"],
                         "v12_independent_micro180_multi_horizon_hazard")

    def test_model_does_not_call_R9_or_V11_legacy_entry_gates(self):
        m = self.make()
        with patch.object(R9HybridGateBaseline, "_process_entries",
                          side_effect=AssertionError("Original R9 entries used")):
            m.on_tick(tick(0, 240050, 10000, 19))
            m.on_tick(tick(1, 241050, 10001, 19))
        self.assertEqual(len(m.entries), 1)

    def test_missing_next_second_quote_drops_stale_entry(self):
        m = self.make(max_quote_lag_ms=100)
        m.on_tick(tick(1, 240020, 10000))
        m.on_tick(tick(2, 241150, 10005))
        self.assertEqual(len(m.entries), 0)
        self.assertEqual(m.v12_counts["pending_source_tick_stale_cancelled"], 1)

    def test_signal_minute_expiry_prohibits_next_minute_fill(self):
        m = self.make()
        m.on_tick(tick(0, 59915, 10000))
        self.assertIsNotNone(m.entry_intent)
        m.on_tick(tick(1, 60009, 10002))
        self.assertEqual(len(m.entries), 0)
        self.assertEqual(m.v12_counts["prior_minute_intent_expired"], 1)

    def test_completed_seconds_and_no_unobserved_gap_filling(self):
        h = CompletedSecondHorizon()
        for i, (s, b) in enumerate((
            (1, 10000), (2, 10005), (5, 10011), (12, 10030),
        )):
            h.update(tick(i, s * 1000 + 35, b))
        self.assertEqual(len(h.completed_bid), 3)
        self.assertEqual(len(h.seconds), 3)
        self.assertEqual(h._past(12, 3), 10011 + 9.5)  # sec 5 is TOO stale? see below

    def test_feature_vector_current_price_only_and_previous_history(self):
        m = self.make()
        for s in range(25):
            m.on_tick(tick(s, 120000 + s*1000 + 20, 10000+2*s))
        t = tick(100, 145020, 10080)
        m._push_second(t)
        a = m.horizon.features(t, 1, m.atr.atr_u or 0)
        b = m.horizon.features(t, -1, m.atr.atr_u or 0)
        self.assertEqual(len(a), len(FEATURE_NAMES))
        self.assertEqual(a[0], 25)
        self.assertEqual(a[1], 19)
        self.assertEqual(a[5], -b[5])
        self.assertAlmostEqual(a[6], b[6])
        self.assertEqual(a[7], b[7])
        self.assertGreaterEqual(a[6], 0)

    def test_identical_history_fixes_signal_time_future_quotes_only_affect_fill(self):
        a, b = self.make(), self.make()
        initial = tick(0, 360100, 10000)
        a.on_tick(initial); b.on_tick(initial)
        self.assertEqual(a.entry_intent, b.entry_intent)
        a.on_tick(tick(1, 361020, 10012))
        b.on_tick(tick(1, 361020, 9970))
        self.assertEqual(a.entries[0]["v12_signal_ms"], b.entries[0]["v12_signal_ms"])
        self.assertNotEqual(a.entries[0]["price_u"], b.entries[0]["price_u"])
        self.assertEqual(a.entries[0]["v12_target_second_start_ms"],
                         b.entries[0]["v12_target_second_start_ms"])


if __name__ == "__main__":
    unittest.main()

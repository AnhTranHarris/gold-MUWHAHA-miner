"""Deterministic source-causal contracts for the new Micro180 V12 entry engine.

These tests verify the independent entry controller and exact quote-side price
behavior; they do not claim teacher recall on the entire nine-month archive.
"""
from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
for p in (BASE / "src", BASE / "variable_cash_horizon_20261114",
          BASE / "dual_basket_20261114", HERE):
    sys.path.insert(0, str(p))

from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9HybridGateBaseline
from v12_micro180_quant_entry import (
    Micro180V12QuantEntry, V12EntrySpec, MEANS, FACTOR_NAMES,
    factor_probability, INTERCEPT,
)


def tick(n: int, msc: int, bid: int = 10000, ask: int = 10020,
         atr: str = "4.0") -> Tick:
    return Tick(
        ordinal=n, time_s=msc // 1000, time_msc=msc,
        bid_u=bid, ask_u=ask,
        source_extras={"atr": atr},
    )


class CausalV12Tests(unittest.TestCase):
    def test_explicit_finite_factor_score(self):
        expected = 1 / (1 + math.exp(-INTERCEPT))
        self.assertAlmostEqual(factor_probability(MEANS), expected, places=11)
        self.assertEqual(len(FACTOR_NAMES), 19)
        for invalid in ((float("nan"),)*19, (1.,2.)):
            with self.assertRaises(ValueError):
                factor_probability(invalid)

    def test_no_live_or_historical_teacher_entry_injection(self):
        with self.assertRaises(ValueError):
            V12EntrySpec(allow_live_orders=True)
        with self.assertRaises(ValueError):
            V12EntrySpec(allow_teacher_signal_injection=True)
        with self.assertRaises(ValueError):
            V12EntrySpec(first_leg_min_score=1.)

    def test_entry_independence_and_actual_executable_quote(self):
        sim = Micro180V12QuantEntry()
        with patch.object(
            R9HybridGateBaseline, "_process_entries",
            side_effect=AssertionError("Inherited R9 entry path unexpectedly called"),
        ), patch(
            "v12_micro180_quant_entry.factor_probability",
            return_value=.98,
        ):
            sim.on_tick(tick(0, 120001, bid=10000, ask=10020))
        self.assertEqual(len(sim.entries), 1)
        e = sim.entries[0]
        self.assertEqual(e["time_msc"], 120001)
        self.assertEqual(e["side"], 1)
        self.assertEqual(e["price_u"], 10020)
        self.assertEqual(e["v12_executable_quote_u"], 10020)
        self.assertEqual(e["v12_entry_authority"],
                         "independent_micro180_19_factor")
        self.assertFalse(e["v11_complete_cycle_family_known_at_entry"])
        self.assertEqual(len(e["v11_factor_vector"]), 19)
        self.assertNotIn("teacher_entry_time", e)

    def test_first_quote_per_second_score_clock(self):
        sim = Micro180V12QuantEntry()
        with patch(
            "v12_micro180_quant_entry.factor_probability", return_value=.001
        ) as scoring:
            sim.on_tick(tick(1, 121001))
            sim.on_tick(tick(2, 121040))
            sim.on_tick(tick(3, 121600))
            self.assertEqual(scoring.call_count, 2)  # two sides, one second
            sim.on_tick(tick(4, 122005))
            self.assertEqual(scoring.call_count, 4)

    def test_wide_spread_and_no_asof_atr_do_not_trigger(self):
        for q in (tick(1, 120100, ask=10060), tick(2, 120100, atr="")):
            sim = Micro180V12QuantEntry()
            with patch(
                "v12_micro180_quant_entry.factor_probability",
                return_value=.99,
            ):
                sim.on_tick(q)
            self.assertFalse(sim.entries)

    def test_actual_s1_and_active_basket_feature_vector_causal(self):
        sim = Micro180V12QuantEntry()
        sim.on_tick(tick(1, 180001))
        vectors = sim._causal_factors(tick(2, 180001), 1, 400.)
        self.assertEqual(len(vectors), 19)
        self.assertEqual(vectors[0], 0.)
        self.assertEqual(vectors[3], 0.)
        self.assertEqual(vectors[4], 0.)
        self.assertTrue(math.isfinite(factor_probability(vectors)))
        self.assertEqual(sim._asof_completed_m5_atr_u(tick(3, 180001)), 400.)

    def test_frozen_prior_entry_unchanged_by_future_quotes(self):
        sim = Micro180V12QuantEntry()
        with patch("v12_micro180_quant_entry.factor_probability", return_value=.99):
            sim.on_tick(tick(1, 180002))
        frozen = dict(sim.entries[0])
        for j in range(2, 20):
            sim.on_tick(tick(j, 180002 + j*1000, bid=9800+j, ask=9820+j))
        self.assertEqual(sim.entries[0], frozen)

    def test_rearm_only_after_observed_first_close(self):
        sim = Micro180V12QuantEntry()
        with patch("v12_micro180_quant_entry.factor_probability", return_value=.001):
            sim.on_tick(tick(1, 240001))
        sim.rearms = 1
        sim.pending_mode = -1
        with patch("v12_micro180_quant_entry.factor_probability", return_value=.99):
            sim.on_tick(tick(2, 241001))
        self.assertFalse(sim.entries)  # no first-close state, no reverse order


if __name__ == "__main__":
    unittest.main()

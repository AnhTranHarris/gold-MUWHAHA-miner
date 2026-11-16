"""Deterministic causal entry contracts for independent Micro180 V11.

Runs without downloading, reconstructing or reformatting original market data.
These fixtures verify code properties, NOT 9-month Coinexx trader recall.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
for path in (PROJECT / "src", PROJECT / "variable_cash_horizon_20261114",
             PROJECT / "dual_basket_20261114", ROOT):
    sys.path.insert(0, str(path))

from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config, R9HybridGateBaseline
from v11_micro180_independent_dual_entry import (
    Micro180V11DualEntry, V11DualEntrySpec,
)


def tick(ordinal: int, msec: int, bid: int, spread: int = 20) -> Tick:
    return Tick(ordinal, msec // 1000, msec, bid, bid + spread)


def cfg() -> R9Config:
    return R9Config(
        use_regime_gate=False, velocity_lookback_sec=2, range_lookback_sec=2,
        min_velocity_pips=0, min_directional_eff=0, min_range_pips=0,
        max_turns=99, max_same_minute_rearms=1,
    )


def real_quote_fixture():
    ordinal = 0
    for sec in range(180):
        within = sec % 60
        pattern = within if within <= 30 else 60 - within
        for offset, n in ((35, 0), (710, 1)):
            yield tick(ordinal, sec * 1000 + offset, 10000 + 5 * pattern + n)
            ordinal += 1


class IndependentDualCausal(unittest.TestCase):
    def test_rejects_live_and_hindsight_routing(self):
        for kwargs in (
            {"live_orders_enabled": True},
            {"allow_future_teacher_entries": True},
            {"allow_extra_basket_entries": True},
            {"max_cycle_legs": 4},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                V11DualEntrySpec(**kwargs)

    def test_dual_micro_engine_does_not_call_inherited_r9_entry_controller(self):
        model = Micro180V11DualEntry(cfg())
        model._gate = lambda _: True
        model._completed_second_quality = lambda _: True
        with patch.object(R9HybridGateBaseline, "_process_entries",
                          side_effect=AssertionError("R9 entry proxy was called")):
            model.on_tick(tick(0, 120001, 10000))
            model.on_tick(tick(1, 120045, 10006))
        self.assertEqual(len(model.entries), 1)
        entry = model.entries[0]
        self.assertEqual(entry["v11_entry_route"], "minute_seed_previous_completed_S1")
        self.assertEqual(entry["v11_quote_side"], "ask")
        self.assertEqual(entry["price_u"], 10026)
        self.assertEqual(entry["time_msc"], 120045)
        self.assertLess(entry["v11_basket5_observed_ms"], 5000)
        self.assertLess(entry["v11_basket15_observed_ms"], 15000)
        self.assertEqual(entry["v10_entry_authority"],
                         "v11_independent_micro180_dual_basket")
        self.assertFalse(entry["v11_complete_cycle_family_known_at_entry"])

    def test_source_quote_parity_against_r9_algorithm_for_first_two_legs(self):
        ref, independent = R9HybridGateBaseline(cfg()), Micro180V11DualEntry(cfg())
        for t in real_quote_fixture():
            ref.on_tick(t)
            independent.on_tick(t)
            self.assertEqual(len(ref.entries), len(independent.entries))
            self.assertEqual(len(ref.trades), len(independent.trades))
            self.assertEqual(ref.position is None, independent.position is None)
            if ref.position is not None:
                self.assertEqual(ref.position.sl_u, independent.position.sl_u)
        self.assertGreater(len(ref.entries), 0)
        self.assertGreater(len(ref.trades), 0)
        keys = ("ordinal", "time_msc", "side", "price_u", "sl_u",
                "cycle_minute", "rearm_number")
        for actual, predicted in zip(ref.entries, independent.entries):
            self.assertEqual(tuple(actual[k] for k in keys),
                             tuple(predicted[k] for k in keys))
            self.assertIn("v11_basket5_signed_mid_move_u", predicted)
            self.assertIn("v11_basket15_signed_mid_move_u", predicted)
            self.assertIn("v11_s1_bid_efficiency", predicted)
            self.assertEqual(predicted["v11_quote_side"],
                             "ask" if predicted["side"] == 1 else "bid")
            self.assertIn(predicted["v11_asof_regime"],
                          ("early_probe", "transition", "mature_directional"))
        self.assertEqual(ref.trades, independent.trades)
        self.assertEqual(len(independent.close_observations), len(ref.trades))
        self.assertLessEqual(max(x["rearm_number"] for x in independent.entries), 1)

    def test_early_5s_warmup_does_not_block_breakout(self):
        model = Micro180V11DualEntry(cfg())
        model._gate = lambda _: True
        model._completed_second_quality = lambda _: True
        for t in (tick(0, 240010, 10000), tick(1, 240080, 10006)):
            model.on_tick(t)
        self.assertEqual(model.entries[0]["v11_asof_regime"], "early_probe")
        self.assertEqual(model.entries[0]["v11_basket5_observed_ms"], 70)
        self.assertEqual(model.entries[0]["v11_basket15_observed_ms"], 70)

    def test_observed_first_leg_sign_can_drive_next_phase_only_after_exit(self):
        for quote_move, state in ((-30, "post_adverse_first_quote_exit"),
                                  (40, "post_favorable_first_quote_exit")):
            with self.subTest(state=state):
                sim = Micro180V11DualEntry(cfg())
                sim.on_tick(tick(1, 180100, 10000))
                sim._open_trade(tick(2, 180150, 1_0000), 1)
                self.assertIsNotNone(sim.position)
                sim._record_close(tick(3, 181100, 10000 + quote_move), "test_close",
                                  10000 + quote_move)
                self.assertIsNone(sim.position)
                sim.rearms = 1
                sim._open_trade(tick(4, 182100, 10000 + quote_move), -1)
                self.assertEqual(sim.entries[-1]["v11_reentry_state"], state)
                self.assertEqual(sim.entries[-1]["v11_flat_interval_ms"], 1000)

    def test_reference_future_cannot_rewrite_past_entry(self):
        prefix = list(real_quote_fixture())[:140]
        a, b = Micro180V11DualEntry(cfg()), Micro180V11DualEntry(cfg())
        for t in prefix:
            a.on_tick(t); b.on_tick(t)
        frozen = [dict(entry) for entry in a.entries]
        now = prefix[-1].time_msc
        for i in range(15):
            a.on_tick(tick(1000 + i, now + (i + 1) * 1000, 10100 + i))
            b.on_tick(tick(2000 + i, now + (i + 1) * 1000, 9800 - i))
        self.assertEqual(a.entries[:len(frozen)], frozen)
        self.assertEqual(b.entries[:len(frozen)], frozen)

    def test_max_two_legs_per_minute(self):
        model = Micro180V11DualEntry(cfg())
        model.rearms = 1
        model.pending_mode = -1
        model._arm_opposite_after_exit()
        self.assertEqual(model.pending_mode, 0)
        self.assertEqual(model.v11_stats["cycle_leg_cap"], 1)


if __name__ == "__main__":
    unittest.main()

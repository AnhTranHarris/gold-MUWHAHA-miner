"""V10 contract tests: R9 quote-entry parity, dual-basket no-veto, merged accounting.

No historical future-family labels, synthetic fills, fee substitutions, raw
source downloads, or demo/live orders. All market examples are local fixtures.
"""
from __future__ import annotations

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
for p in (
    PROJECT / "src",
    PROJECT / "variable_cash_horizon_20261114",
    PROJECT / "dual_basket_20261114",
    ROOT,
):
    sys.path.insert(0, str(p))

from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config, R9HybridGateBaseline
from v10_r9_dual_concordance import Micro180V10R9Causal, V10Spec
from v10_merged_entry_concordance import compare_merged_entries


def r9_cfg() -> R9Config:
    return R9Config(
        use_regime_gate=False,
        velocity_lookback_sec=2,
        range_lookback_sec=2,
        min_velocity_pips=0,
        min_directional_eff=0,
        min_range_pips=0,
        max_turns=99,
    )


def tick(ordinal: int, ms: int, bid: int, spread: int = 20) -> Tick:
    return Tick(ordinal, ms // 1000, ms, bid, bid + spread)


def quote_stream():
    # Same-ms and time-ordered prices, with directional reversals.
    i = 0
    for sec in range(180):
        m = sec % 60
        mid = m if m <= 30 else 60 - m
        for offset, delta in ((35, 0), (710, 1)):
            yield tick(i, sec * 1000 + offset, 10000 + mid * 5 + delta)
            i += 1


class V10CausalParityTests(unittest.TestCase):
    def test_guard_prevents_live_mode_or_basket_veto(self):
        for settings in ({"allow_broker_orders": True}, {"dual_as_entry_veto": True}):
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                V10Spec(**settings)

    def test_quote_by_quote_r9_entry_exit_rearm_parity(self):
        baseline = R9HybridGateBaseline(r9_cfg())
        v10 = Micro180V10R9Causal(r9_cfg())
        for current in quote_stream():
            baseline.on_tick(current)
            v10.on_tick(current)
            self.assertEqual(len(baseline.entries), len(v10.entries))
            self.assertEqual(len(baseline.trades), len(v10.trades))
            if baseline.position is None:
                self.assertIsNone(v10.position)
            else:
                self.assertIsNotNone(v10.position)
                self.assertEqual(baseline.position.sl_u, v10.position.sl_u)
        self.assertGreater(len(baseline.entries), 0)
        self.assertGreater(len(baseline.trades), 0)
        keys = ("ordinal", "time_msc", "side", "price_u", "sl_u",
                "cycle_minute", "rearm_number")
        for a, b in zip(baseline.entries, v10.entries):
            self.assertEqual(tuple(a[k] for k in keys),
                             tuple(b[k] for k in keys))
            self.assertEqual(b["v10_executable_entry_quote_u"], b["price_u"])
            self.assertIn("v10_dual_aligned_lanes", b)
            self.assertIn("v10_directional_quant_score", b)
            self.assertIn("v10_market_phase", b)
        self.assertEqual(baseline.trades, v10.trades)
        self.assertEqual(len(v10.close_observations), len(v10.trades))
        for close in v10.close_observations:
            self.assertGreaterEqual(close["mfe_u"], 0)
            self.assertGreaterEqual(close["mae_u"], 0)
        self.assertFalse(v10.concordance_summary()["live_broker_enabled"])

    def test_future_ticks_cannot_change_existing_entries(self):
        left = Micro180V10R9Causal(r9_cfg())
        right = Micro180V10R9Causal(r9_cfg())
        prefix = list(quote_stream())[:160]
        for t in prefix:
            left.on_tick(t)
            right.on_tick(t)
        frozen = [dict(entry) for entry in left.entries]
        self.assertEqual(frozen, right.entries)
        start = prefix[-1].time_msc + 1000
        for i in range(12):
            left.on_tick(tick(10000 + i, start + 1000 * i, 11000 + i))
            right.on_tick(tick(20000 + i, start + 1000 * i, 9000 - i))
        self.assertEqual(frozen, left.entries[:len(frozen)])
        self.assertEqual(frozen, right.entries[:len(frozen)])

    def test_same_timestamp_quote_ordinal_is_retained(self):
        sim = Micro180V10R9Causal(r9_cfg())
        for i, ms in enumerate((1000, 1000, 1000, 1020, 2090, 3001, 4001)):
            sim.on_tick(tick(i, ms, 10000 + i * 2))
        self.assertEqual(sim.rolling.n, 7)
        self.assertEqual(sim.path.rows, 7)


class MergedReferenceConcordanceTests(unittest.TestCase):
    def setUp(self):
        self.dt = datetime(2026, 1, 2, 13, 1, 5, tzinfo=timezone.utc)
        self.minute = int(self.dt.timestamp()) // 60 * 60
        self.mark_ms = int(self.dt.timestamp() * 1000) + 1000

    def row(self, **changes):
        item = {
            "entry_time_broker": self.dt.strftime("%Y-%m-%d %H:%M:%S"),
            "side": "buy", "leg": "1",
            "equote_ms": str(self.mark_ms),
            "q_entry_u": "12345",
            "net_usd": "1.37",
        }
        item.update(changes)
        return item

    def candidate(self, **changes):
        item = {
            "cycle_minute": self.minute,
            "rearm_number": 0,
            "side": 1,
            "time_msc": self.mark_ms,
            "price_u": 12345,
        }
        item.update(changes)
        return item

    def test_exact_quote_match_and_original_pnl_unchanged(self):
        report = compare_merged_entries(
            [self.row()], [self.candidate()], expected_teacher_rows=1
        )
        self.assertEqual(report["original_r9_net_usd_unchanged"], "1.37")
        self.assertEqual(report["counts"]["exact_executable_quote_price_and_clock"], 1)
        self.assertTrue(report["certified_exact_replication"])
        self.assertFalse(report["original_fee_or_swap_changes"])

    def test_wrong_quote_price_is_not_declared_equal(self):
        result = compare_merged_entries(
            [self.row()], [self.candidate(price_u=12346)], expected_teacher_rows=1
        )
        self.assertEqual(result["counts"].get("exact_executable_quote_price_and_clock", 0), 0)
        self.assertEqual(result["counts"]["clock_match_quote_price_differs"], 1)
        self.assertFalse(result["certified_exact_replication"])

    def test_missing_original_quote_keeps_net_in_denominator(self):
        rows = [
            self.row(),
            self.row(leg="2", side="sell", net_usd="-0.22",
                     equote_ms="-1", q_entry_u="0"),
        ]
        result = compare_merged_entries(
            rows,
            [self.candidate(), self.candidate(rearm_number=1, side=-1)],
            expected_teacher_rows=2,
        )
        self.assertEqual(result["counts"]["original_teacher_rows"], 2)
        self.assertEqual(result["counts"]["source_quote_missing"], 1)
        self.assertEqual(result["original_r9_net_usd_unchanged"], "1.15")
        self.assertFalse(result["certified_exact_replication"])

    def test_does_not_select_hindsight_winning_family(self):
        mixed = [
            self.row(net_usd="-2.00", leg="1"),
            self.row(net_usd="0.40", leg="2", side="sell",
                     equote_ms=str(self.mark_ms + 2000), q_entry_u="12280"),
        ]
        cands = [self.candidate(),
                 self.candidate(rearm_number=1, side=-1,
                                time_msc=self.mark_ms + 2000, price_u=12280)]
        report = compare_merged_entries(mixed, cands, expected_teacher_rows=2)
        self.assertEqual(report["counts"]["exact_executable_quote_price_and_clock"], 2)
        self.assertEqual(report["original_r9_net_usd_unchanged"], "-1.60")
        self.assertEqual(report["same_cycle_entry_coverage"], 1.0)

    def test_duplicate_quote_candidate_is_not_double_counted(self):
        with self.assertRaises(ValueError):
            compare_merged_entries([self.row()],
                [self.candidate(), self.candidate(price_u=12346)])


if __name__ == "__main__":
    unittest.main()

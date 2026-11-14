"""Bounded deterministic invariants for the four-lane dual-basket R9 pilot."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "variable_cash_horizon_20261114"))
sys.path.insert(0, str(ROOT / "dual_basket_20261114"))

from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config, R9HybridGateBaseline
from on_policy_cash_replay import ResearchCash
from cash_ladder import AccountSnapshot, CurrentPosition, CashLadderSpec, VariableCashHorizonPolicy
from dual_basket import (
    DualBasketSpec, DualBasketBaseline, DualBasketCash, ProtectedStretchCashPolicy,
)


def quote(n: int, second: int, bid: int, spread: int = 20) -> Tick:
    return Tick(n, second, second * 1000 + n, bid, bid + spread)


def config() -> R9Config:
    return R9Config(use_regime_gate=False, velocity_lookback_sec=2,
                    range_lookback_sec=2, min_velocity_pips=0,
                    min_directional_eff=0, min_range_pips=0, max_turns=99)


def position(bid: float, stop: float = 9.70) -> CurrentPosition:
    return CurrentPosition(
        side=1, entry_executed_price=10.0,
        liquidation_bid=bid, liquidation_ask=bid + .1,
        original_or_current_stop_price=stop,
        cash_per_xau_price_dollar=1.0,
        additional_roundtrip_cost_cash=.20, age_seconds=2,
        since_last_quote_ms=10, min_legal_stop_distance_xau=.01)


def account() -> AccountSnapshot:
    return AccountSnapshot(100000., 100000., 100000., 0., 100000.)


class DualBasketTests(unittest.TestCase):
    def test_only_approved_clock_grid_and_parameters(self):
        for kw in (
            {"basket_seconds": (5, 30)},
            {"breakout_seconds": (5, 30)},
            {"minimum_mid_displacement_cents": 0},
            {"minimum_completed_30s": 7},
            {"max_entries_per_minute": 0},
        ):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                DualBasketSpec(**kw)

    def test_5s_and_15s_anchor_independence(self):
        sim = DualBasketBaseline(config())
        sim._start_minute_cycle(quote(1, 120, 1000))
        self.assertEqual(sim.baskets[5], (120, 2020))
        self.assertEqual(sim.baskets[15], (120, 2020))
        sim._start_minute_cycle(quote(2, 125, 1020))
        self.assertEqual(sim.baskets[5], (125, 2060))
        self.assertEqual(sim.baskets[15], (120, 2020))
        sim._start_minute_cycle(quote(3, 135, 1030))
        self.assertEqual(sim.baskets[5], (135, 2080))
        self.assertEqual(sim.baskets[15], (135, 2080))

    def test_both_breakout_windows_complete_and_stale_fail(self):
        sim = DualBasketBaseline(config())
        for n, sec in enumerate(range(100, 131), 1):
            sim.on_tick(quote(n, sec, 1200 if sec == 106 else 1000))
        lv15 = sim._breakout_levels(131, 15)
        lv30 = sim._breakout_levels(131, 30)
        self.assertIsNotNone(lv15)
        self.assertIsNotNone(lv30)
        self.assertLess(lv15[0], lv30[0])
        # Neither current incomplete-second quote nor a gap is backfilled.
        sim.on_tick(quote(40, 131, 9999))
        self.assertEqual(sim._breakout_levels(131, 15), lv15)
        self.assertIsNone(sim._breakout_levels(150, 15))

    def test_all_four_lanes_contribute_one_order_not_four(self):
        sim = DualBasketBaseline(config())
        sim.on_tick(quote(1, 120, 1000))
        sim._gate = lambda tick: True
        sim._quality = lambda side: True
        sim._breakout_levels = lambda now, width: (2010, 2010)
        sim.on_tick(quote(2, 121, 1030))
        self.assertEqual(len(sim.entries), 1)
        self.assertEqual(sim.entries[0]["side"], 1)
        self.assertEqual(len(sim.entries[0]["breakout_lanes"].split("|")), 4)
        self.assertEqual(sim.stats["dual_positions_opened"], 1)

    def test_conflicting_direction_votes_abstain(self):
        sim = DualBasketBaseline(config())
        sim._start_minute_cycle(quote(1, 120, 1000))
        # Synthetic lane contradiction isolates arbitration, not market feasibility.
        sim.baskets[15] = (120, 2100)
        sim._gate = lambda tick: True
        sim._quality = lambda side: True
        sim._breakout_levels = (lambda now, width:
                                (2000, 1900) if width == 15 else (2200, 2100))
        sim._process_entries(quote(2, 121, 1020))
        self.assertEqual(len(sim.entries), 0)
        self.assertEqual(sim.stats["dual_conflicting_direction_wait"], 1)

    def test_per_minute_risk_cap_is_not_reset_by_5s_clock(self):
        sim = DualBasketBaseline(config())
        for i in range(4):
            t = quote(i + 1, 121 + i, 1030)
            sim._start_minute_cycle(t)
            sim._open_trade(t, 1)
            self.assertIsNotNone(sim.position)
            sim.position = None  # test fixture: free slot without changing cap
        sim._start_minute_cycle(quote(9, 125, 1030))
        sim._open_trade(quote(10, 125, 1030), 1)
        self.assertEqual(len(sim.entries), 4)
        self.assertEqual(sim.stats["dual_risk_cap_block"], 1)
        self.assertEqual(sim.pending_mode, 0)

    def test_no_opposite_rearm_across_either_basket_boundary(self):
        sim = DualBasketBaseline(config())
        t = quote(1, 120, 1000)
        sim._start_minute_cycle(t)
        sim._open_trade(quote(2, 121, 1030), 1)
        crossed = quote(3, 125, 1020)
        sim._record_close(crossed, "timeout", crossed.bid_u)
        sim._start_minute_cycle(crossed)
        sim._arm_opposite_after_exit()
        self.assertEqual(sim.pending_mode, 2)
        self.assertEqual(sim.stats["dual_same_basket_rearms"], 0)

    def test_cash_minimum_and_preferred_max_with_protective_stop(self):
        s = CashLadderSpec(min_net_profit=.10, stretch_net_profit=1.75)
        harvest = VariableCashHorizonPolicy(s)
        self.assertEqual(harvest.decide(position(10.30), account()).action, "CLOSE_NOW")
        guarded = ProtectedStretchCashPolicy(s)
        self.assertEqual(guarded.decide(position(10.70), account()).action,
                         "TIGHTEN_STOP")
        self.assertEqual(guarded.decide(position(11.95), account()).action,
                         "CLOSE_NOW")
        # A 10-cent gain cannot always be guaranteed with broker-stop distance.
        unprotected = ProtectedStretchCashPolicy(s)
        self.assertEqual(unprotected.decide(position(10.30), account()).action,
                         "CLOSE_NOW")

    def test_cash_account_controller_is_position_scoped(self):
        sim = DualBasketCash(config(), ResearchCash(), protected_stretch=True)
        sim._start_minute_cycle(quote(1, 120, 1000))
        sim._open_trade(quote(2, 121, 1030), 1)
        self.assertIsNotNone(sim.position)
        ctrl = sim.controllers[sim.position.entry_ordinal]
        self.assertIsInstance(ctrl, ProtectedStretchCashPolicy)
        self.assertEqual(ctrl.spec.min_net_profit, .10)
        self.assertEqual(ctrl.spec.stretch_net_profit, 1.75)

    def test_original_baseline_remains_separate(self):
        original = R9HybridGateBaseline(config())
        self.assertNotIsInstance(original, DualBasketBaseline)
        for i in range(7):
            original.on_tick(quote(i + 1, 120 + i, 1000 + i))
        self.assertNotIn("dual_positions_opened", original.stats)


if __name__ == "__main__":
    unittest.main()

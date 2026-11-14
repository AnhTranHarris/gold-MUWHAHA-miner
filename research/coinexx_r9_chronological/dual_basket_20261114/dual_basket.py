"""R9 research-only dual 5s/15s baskets x 15s/30s completed-quote breakout.

Four causal candidate lanes share ONE position, protective stop and risk budget.
The original R9 engine, v1.94 EA, and prior 15s experiment are untouched.
No fabricated volume, tick reconstruction, or speculative 155-model scores.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import sin, cos, tau
from typing import Optional

from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config, R9HybridGateBaseline
from on_policy_cash_replay import ManagedR9, ResearchCash
FEATURE_NAMES = (
    'side', 'mid_disp_5s_cents', 'mid_disp_15s_cents',
    'excess_breakout_15s_cents', 'excess_breakout_30s_cents',
    'spread_cents', 'qualifying_lane_count', 'elapsed_5s', 'elapsed_15s',
    'm5_atr_cents', 'recent_completed_mid_range_cents',
    'recent_completed_mid_impulse_cents', 'time_sin', 'time_cos',
)

from cash_ladder import (
    AccountSnapshot, CashLadderSpec, CurrentPosition, ExitDecision,
    VariableCashHorizonPolicy,
)


@dataclass(frozen=True)
class DualBasketSpec:
    basket_seconds: tuple[int, int] = (5, 15)
    breakout_seconds: tuple[int, int] = (15, 30)
    minimum_mid_displacement_cents: int = 10
    breakout_extra_cents: int = 1
    minimum_completed_15s: int = 4
    minimum_completed_30s: int = 8
    max_completed_second_age: int = 2
    max_entries_per_minute: int = 4

    def __post_init__(self) -> None:
        if self.basket_seconds != (5, 15) or self.breakout_seconds != (15, 30):
            raise ValueError("Only the owner-approved 5/15 basket x 15/30 breakout grid")
        if not all(type(n) is int for n in (
            self.minimum_mid_displacement_cents, self.breakout_extra_cents,
            self.minimum_completed_15s, self.minimum_completed_30s,
            self.max_completed_second_age, self.max_entries_per_minute,
        )):
            raise ValueError("Geometry must use integral quote-price cents")
        if (self.minimum_mid_displacement_cents <= 0 or self.breakout_extra_cents < 0
            or self.minimum_completed_15s < 4 or self.minimum_completed_30s < 8
            or not 0 <= self.max_completed_second_age <= 2
            or self.max_entries_per_minute < 1):
            raise ValueError("Invalid causal basket/breakout contract")


class MinimumCashHarvestPolicy(VariableCashHorizonPolicy):
    """Keep the inherited risk semantics, but label the revised $0.10 target."""
    def decide(self, position: CurrentPosition, account: AccountSnapshot,
               evidence=None) -> ExitDecision:
        decision = super().decide(position, account, evidence)
        if decision.action == "CLOSE_NOW" and decision.reason.startswith("Take $"):
            return ExitDecision(
                "CLOSE_NOW", "Harvest available $0.10 net; no approved runner",
                decision.observed_liquidation_net_cash)
        return decision


class ProtectedStretchCashPolicy(MinimumCashHarvestPolicy):
    """Experimental lock-$0.10, pursue-$1.75 branch; never bypass base safety.

    Base controller first evaluates gross-loss/account, stranded-quote, age and
    preferred-target exits. Only a base *minimum-profit harvest* can be changed
    into a legal tighter stop or HOLD with an already-protective stop.
    This is NOT evidence of profitable continuation.
    """
    def decide(self, position: CurrentPosition, account: AccountSnapshot,
               evidence=None) -> ExitDecision:
        # Bypass label rewrite so only the genuine minimum-harvest decision
        # can be upgraded to a protective, tighter stop.
        baseline = VariableCashHorizonPolicy.decide(self, position, account, evidence)
        if (baseline.action != "CLOSE_NOW"
            or not baseline.reason.startswith("Take $")
            or baseline.observed_liquidation_net_cash >= self.spec.stretch_net_profit - 1e-9):
            return baseline
        minimum = self.spec.min_net_profit
        desired = min(self.spec.stretch_net_profit,
                      max(minimum, self.peak_observed_cash -
                          self.spec.incremental_trailing_gap_cash))
        proposed = position.stop_price_at_min_net_cash(desired)
        if position.stop_is_legal_and_tighter(proposed):
            return ExitDecision(
                "TIGHTEN_STOP", "Experimental protected stretch, not approved",
                baseline.observed_liquidation_net_cash, proposed, desired)
        old = position.original_or_current_stop_price
        if old is not None and position.net_cash(old) >= desired - 1e-9:
            return ExitDecision(
                "HOLD", "Existing stop protects experimental stretch",
                baseline.observed_liquidation_net_cash, old, desired)
        return ExitDecision(
            "CLOSE_NOW", "Cannot protect $0.10 net; harvest now",
            baseline.observed_liquidation_net_cash)


class DualBasketMixin:
    """One state machine; the four lanes contribute candidate evidence only.

    At every quote, each basket has an independent first-observed-quote anchor.
    The two breakout tests use only completed one-second quote CLOSE midpoints.
    OR across valid same-side lanes preserves throughput; disagreement => WAIT.
    A strict per-source-minute entry cap prevents the 5s clock multiplying risk
    without bound. No opposite-side rearm crosses a 5s OR 15s basket boundary.
    """

    def __init__(self, *args, dual_spec: DualBasketSpec, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.dual_spec = dual_spec
        self.baskets: dict[int, tuple[int, int]] = {}
        self._last_entry_starts: Optional[tuple[int, int]] = None
        self._last_close_starts: Optional[tuple[int, int]] = None
        self._closed_entry_starts: Optional[tuple[int, int]] = None
        self._entry_minute: Optional[int] = None
        self._entries_in_minute = 0
        self._cached_second: Optional[int] = None
        self._cached_windows: dict[int, Optional[tuple[int, int]]] = {}
        self._qualifying_lanes: tuple[str, ...] = ()
        self._candidate_features: tuple[float, ...] = ()
        self.entry_selector = None  # Optional frozen training-only gate.

    def _starts(self, t: Tick) -> tuple[int, int]:
        return tuple(t.time_s - t.time_s % width
                     for width in self.dual_spec.basket_seconds)

    def _cap(self) -> int:
        return min(self.dual_spec.max_entries_per_minute,
                   self.cfg.max_same_minute_rearms + 1)

    def _start_minute_cycle(self, t: Tick) -> None:
        minute = t.time_s - t.time_s % 60
        if minute != self._entry_minute:
            self._entry_minute = minute
            self.cycle_minute = minute
            self._entries_in_minute = 0
            self.rearms = 0
            self.pending_mode = 2
            self.stats["dual_minute_starts"] += 1

        changed = False
        for width in self.dual_spec.basket_seconds:
            start = t.time_s - t.time_s % width
            previous = self.baskets.get(width)
            if previous is None or start != previous[0]:
                self.baskets[width] = (start, t.bid_u + t.ask_u)
                self.stats[f"basket_{width}s_starts"] += 1
                changed = True

        if changed:
            self._cached_second = None
            self._cached_windows.clear()
            if self.position is None:
                self.pending_mode = 2 if self._entries_in_minute < self._cap() else 0
        self.cycle_buy_u = self.cycle_sell_u = 0  # Original bracket is not used.

    def _breakout_levels(self, now: int, width: int) -> Optional[tuple[int, int]]:
        if now != self._cached_second:
            self._cached_second = now
            self._cached_windows.clear()
        if width in self._cached_windows:
            return self._cached_windows[width]
        points = [b for b in self.micro if 0 < now - b.second <= width]
        need = (self.dual_spec.minimum_completed_15s if width == 15
                else self.dual_spec.minimum_completed_30s)
        if (len(points) < need or
            now - points[-1].second > self.dual_spec.max_completed_second_age):
            result = None
        else:
            # Each Bid/Ask CLOSE is from the same observed source-second.
            result = (max(b.bid_close_u + b.ask_close_u for b in points),
                      min(b.bid_close_u + b.ask_close_u for b in points))
        self._cached_windows[width] = result
        return result

    def entry_features(self, t: Tick, side: int) -> tuple[float, ...]:
        """Past/current quote-only model inputs evaluated BEFORE trade placement."""
        mid2 = t.bid_u + t.ask_u
        a5 = self.baskets[5][1]
        a15 = self.baskets[15][1]
        b15 = self._breakout_levels(t.time_s, 15)
        b30 = self._breakout_levels(t.time_s, 30)
        def excess(levels):
            if levels is None:
                return -999.0  # Explicit unavailable-window sentinel.
            return (mid2 - levels[0]) / 2 if side > 0 else (levels[1] - mid2) / 2
        recent = [b for b in self.micro if 0 < t.time_s - b.second <= 5]
        mids = [(b.bid_close_u + b.ask_close_u) / 2 for b in recent]
        span = max(mids) - min(mids) if mids else 0.
        impulse = side * (mids[-1] - mids[0]) if len(mids) > 1 else 0.
        angle = tau * (t.time_s % 86400) / 86400
        return (
            float(side),
            float(side * (mid2 - a5) / 2),
            float(side * (mid2 - a15) / 2),
            float(excess(b15)), float(excess(b30)),
            float(t.ask_u - t.bid_u),
            float(len(self._qualifying_lanes)),
            float(t.time_s - self.baskets[5][0]),
            float(t.time_s - self.baskets[15][0]),
            float(self.atr.atr_u) if self.atr.ready else -999.,
            float(span), float(impulse),
            sin(angle), cos(angle),
        )

    def _process_entries(self, t: Tick) -> None:
        if self.pending_mode == 0 or self._entries_in_minute >= self._cap():
            self.stats["dual_entry_cap_or_pending"] += 1
            return
        account = getattr(self, "account", None)
        if (account is not None and self.cash.governor and
            (account.day_lock or account.permanent_lock)):
            self.stats["dual_governor_block"] += 1
            return
        if not self._gate(t):
            return

        mid2 = t.bid_u + t.ask_u
        delta2 = 2 * self.dual_spec.minimum_mid_displacement_cents
        extra2 = 2 * self.dual_spec.breakout_extra_cents
        votes = {1: [], -1: []}
        for bw in self.dual_spec.basket_seconds:
            anchor2 = self.baskets[bw][1]
            for breakout in self.dual_spec.breakout_seconds:
                extremes = self._breakout_levels(t.time_s, breakout)
                if extremes is None:
                    self.stats[f"missing_{breakout}s_completed"] += 1
                    continue
                high2, low2 = extremes
                lane = f"{bw}s_basket_{breakout}s_breakout"
                if (self.pending_mode in (1, 2)
                    and mid2 >= anchor2 + delta2
                    and mid2 >= high2 + extra2):
                    votes[1].append(lane)
                if (self.pending_mode in (-1, 2)
                    and mid2 <= anchor2 - delta2
                    and mid2 <= low2 - extra2):
                    votes[-1].append(lane)

        if votes[1] and votes[-1]:
            self.stats["dual_conflicting_direction_wait"] += 1
            return
        side = 1 if votes[1] else -1 if votes[-1] else 0
        if not side:
            self.stats["dual_no_breakout"] += 1
            return
        if not self._quality(side):
            self.stats["dual_gate_s1"] += 1
            return
        self._qualifying_lanes = tuple(votes[side])
        self._candidate_features = self.entry_features(t, side)
        try:
            if (self.entry_selector is not None and
                not self.entry_selector.accept(self._candidate_features)):
                self.stats["dual_frozen_model_reject"] += 1
                return
            self._open_trade(t, side)
        finally:
            self._qualifying_lanes = ()
            self._candidate_features = ()

    def _open_trade(self, t: Tick, side: int) -> None:
        if self._entries_in_minute >= self._cap():
            self.stats["dual_risk_cap_block"] += 1
            return
        before = self.position
        super()._open_trade(t, side)
        if self.position is None or self.position is before:
            return  # ManagedR9 may reject a risk-ineligible order.
        self._entries_in_minute += 1
        self._last_entry_starts = self._starts(t)
        self.entries[-1].update({
            "basket_start_5s": self._last_entry_starts[0],
            "basket_start_15s": self._last_entry_starts[1],
            "breakout_lanes": "|".join(self._qualifying_lanes),
            "features": list(self._candidate_features),
        })
        for lane in self._qualifying_lanes:
            self.stats[f"accepted_{lane}"] += 1
        self.stats["dual_positions_opened"] += 1

    def _record_close(self, t: Tick, reason: str, exit_u: int) -> None:
        if self.position is not None:
            self._closed_entry_starts = self._last_entry_starts
            self._last_close_starts = self._starts(t)
        super()._record_close(t, reason, exit_u)

    def _arm_opposite_after_exit(self) -> None:
        current = tuple(self.baskets[w][0] for w in self.dual_spec.basket_seconds)
        same = (self._closed_entry_starts is not None and
                self._closed_entry_starts == current == self._last_close_starts)
        if same and self._entries_in_minute < self._cap():
            super()._arm_opposite_after_exit()
            self.stats["dual_same_basket_rearms"] += 1
        else:
            self.stats["dual_no_stale_cross_basket_rearm"] += 1
            self.pending_mode = 2 if self._entries_in_minute < self._cap() else 0


class DualBasketBaseline(DualBasketMixin, R9HybridGateBaseline):
    def __init__(self, cfg: R9Config, spec: DualBasketSpec = DualBasketSpec()):
        super().__init__(cfg, dual_spec=spec)


class DualBasketCash(DualBasketMixin, ManagedR9):
    """Both cash arms use actual modeled liquidation side, never price 'pips'."""

    def __init__(self, cfg: R9Config, cash: ResearchCash,
                 protected_stretch: bool = False,
                 spec: DualBasketSpec = DualBasketSpec()) -> None:
        super().__init__(cfg, cash, "cash_harvest", dual_spec=spec)
        self.protected_stretch = protected_stretch
        self.cash_spec = CashLadderSpec(min_net_profit=0.10,
                                        stretch_net_profit=1.75)

    def _open_trade(self, t: Tick, side: int) -> None:
        before = self.position
        super()._open_trade(t, side)
        if self.position is not None and self.position is not before:
            policy = (ProtectedStretchCashPolicy(self.cash_spec)
                      if self.protected_stretch else
                      MinimumCashHarvestPolicy(self.cash_spec))
            self.controllers[self.position.entry_ordinal] = policy

    def report(self) -> dict:
        r = super().report()
        r["cash_profit_minimum"] = self.cash_spec.min_net_profit
        r["cash_profit_preferred_max"] = self.cash_spec.stretch_net_profit
        r["protected_stretch_experimental"] = self.protected_stretch
        r["target_ge_0_10"] = sum(v >= 0.10 - 1e-9 for v in self._net_values)
        r["model_assisted_runner_approved"] = False
        return r

"""Micro180 V10: causal R9 entry concordance with four-lane dual-basket evidence.

Research-only. An R9 v1.90 decision remains the entry authority; the existing
5s/15s x 15s/30s dual baskets and V9 quant descriptors are observed as-of each
entry, NOT hindsight filters. Thus entry-parity can be tested before authorizing
changes to the exit or rearm policy. No merged teacher entry is injected as an
order and no source cost is replaced or re-estimated.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config, R9HybridGateBaseline
from dual_basket import DualBasketSpec
from micro180 import RollingThreeMinute
from v5_ms_path import MsQuarterPath
from v9_volume_router import V9Spec, directional_quant


@dataclass(frozen=True)
class V10Spec:
    """One safe research configuration; no live mode or future-family switch."""

    dual_as_entry_veto: bool = False
    allow_broker_orders: bool = False

    def __post_init__(self) -> None:
        if self.dual_as_entry_veto or self.allow_broker_orders:
            raise ValueError("V10 parity stage is research-only; no basket veto or orders")


class Micro180V10R9Causal(R9HybridGateBaseline):
    """Exact R9 entry/position state machine, with Micro180 dual-basket telemetry.

    The inherited on_tick() is unchanged. Under identical Tick and R9Config
    streams its entry time, side, entry quote and close/rearm order MUST equal the
    original R9HybridGateBaseline. Any mismatch is a parity failure, not an
    opportunity to optimize a threshold.

    The V9 5/15 basket features are retained as four-lane observations; their
    warmup or stale quotes never silently delete an R9-eligible entry.
    """

    def __init__(
        self,
        cfg: R9Config | None = None,
        *,
        dual: DualBasketSpec | None = None,
        v9: V9Spec | None = None,
        spec: V10Spec = V10Spec(),
    ) -> None:
        super().__init__(cfg)
        self.dual_spec = dual or DualBasketSpec()
        self.v9 = v9 or V9Spec()
        self.v10 = spec
        self.rolling = RollingThreeMinute()
        self.path = MsQuarterPath()
        self.v10_stats: Counter[str] = Counter()
        self.close_observations: list[dict[str, Any]] = []
        self._last_close: dict[str, Any] | None = None
        self._path_in_position: dict[str, int] | None = None

    def _push_second(self, t: Tick) -> None:
        # The inherited R9 completed-S1 builder remains authoritative.
        super()._push_second(t)
        self.rolling.update(t)
        self.path.update(t)

    def _four_lane_vote(self, t: Tick) -> dict[int, tuple[str, ...]]:
        levels15, levels30 = self.rolling.price_levels(
            t.time_msc,
            self.dual_spec.minimum_completed_15s,
            self.dual_spec.minimum_completed_30s,
            self.dual_spec.max_completed_second_age * 1000 + 999,
        )
        votes: dict[int, list[str]] = {1: [], -1: []}
        if levels15 is None or levels30 is None:
            return {1: (), -1: ()}
        for width, bar, minimum_span in (
            (5, self.rolling.current.get(5000), self.v9.min_5s_span_ms),
            (15, self.rolling.current.get(15000), self.v9.min_15s_span_ms),
        ):
            if bar is None:
                continue
            if (bar.last_ms - bar.first_ms < minimum_span
                    or bar.max_gap_ms > self.v9.min_15s_span_ms + 500):
                continue
            movement2 = bar.bid_close + bar.ask_close - bar.bid_open - bar.ask_open
            for age, level in ((15, levels15), (30, levels30)):
                lane = f"{width}s_basket_{age}s_breakout"
                if (movement2 >= 2 * self.dual_spec.minimum_mid_displacement_cents
                        and t.bid_u >= level[0] + self.dual_spec.breakout_extra_cents):
                    votes[1].append(lane)
                if (movement2 <= -2 * self.dual_spec.minimum_mid_displacement_cents
                        and t.ask_u <= level[1] - self.dual_spec.breakout_extra_cents):
                    votes[-1].append(lane)
        return {side: tuple(lanes) for side, lanes in votes.items()}

    def _entry_context(self, t: Tick, side: int) -> dict[str, Any]:
        votes = self._four_lane_vote(t)
        aligned = votes[side]
        opposing = votes[-side]
        score = directional_quant(self.rolling, self.path, t, side)
        previous = self._last_close
        same_minute_rearm = (
            self.rearms > 0
            and previous is not None
            and previous["minute"] == self.cycle_minute
            and previous["side"] == -side
            and previous["time_msc"] <= t.time_msc
        )
        context: dict[str, Any] = {
            "v10_entry_authority": "R9_v190_completed_S1_M5_minute_bracket",
            "v10_dual_aligned_lanes": "|".join(aligned),
            "v10_dual_opposing_lanes": "|".join(opposing),
            "v10_dual_vote_aligned": bool(aligned),
            "v10_dual_vote_opposes": bool(opposing),
            "v10_directional_quant_usable": bool(score.usable),
            "v10_directional_quant_score": score.score if score.usable else None,
            "v10_quote_ordinal": t.ordinal,
            "v10_quote_time_msc": t.time_msc,
            "v10_executable_entry_quote_u": t.ask_u if side > 0 else t.bid_u,
            "v10_leg": self.rearms + 1,
            "v10_market_phase": "initial_directional_entry",
        }
        if same_minute_rearm:
            delta2 = (t.bid_u + t.ask_u) - previous["mid2"]
            context.update({
                "v10_market_phase": (
                    "opposite_after_favorable_first_mark"
                    if previous["signed_quote_move_u"] > 0
                    else "opposite_after_adverse_first_mark"
                ),
                "v10_previous_exit_reason": previous["reason"],
                "v10_previous_first_mfe_u": previous["mfe_u"],
                "v10_previous_first_mae_u": previous["mae_u"],
                "v10_flat_interval_ms": t.time_msc - previous["time_msc"],
                "v10_opposite_mid_movement_u": side * delta2 / 2.0,
            })
        return context

    def _open_trade(self, t: Tick, side: int) -> None:
        # Only the inherited R9 gate/entry state can invoke this method.
        context = self._entry_context(t, side)
        before = len(self.entries)
        super()._open_trade(t, side)
        if len(self.entries) == before:
            self.v10_stats["r9_entry_rejected"] += 1
            return
        self.entries[-1].update(context)
        self._path_in_position = {"mfe_u": 0, "mae_u": 0}
        self.v10_stats["r9_entries"] += 1
        self.v10_stats[
            "dual_alignment_at_r9_entry" if context["v10_dual_vote_aligned"]
            else "r9_entry_without_dual_confirmation"
        ] += 1
        if context["v10_leg"] > 1:
            self.v10_stats["r9_opposite_reentries"] += 1

    def _observe_position(self, t: Tick) -> None:
        p = self.position
        if p is None or self._path_in_position is None:
            return
        liq_u = t.bid_u if p.side > 0 else t.ask_u
        signed_u = p.side * (liq_u - p.entry_price_u)
        self._path_in_position["mfe_u"] = max(self._path_in_position["mfe_u"], signed_u)
        self._path_in_position["mae_u"] = max(self._path_in_position["mae_u"], -signed_u)

    def on_tick(self, t: Tick) -> None:
        # Observation-only; do not alter R9's broker-stop-before-EA event order.
        self._observe_position(t)
        super().on_tick(t)

    def _record_close(self, t: Tick, reason: str, exit_u: int) -> None:
        p = self.position
        if p is None:
            return
        latest = dict(self._path_in_position or {"mfe_u": 0, "mae_u": 0})
        signed_u = p.side * (exit_u - p.entry_price_u)
        latest["mfe_u"] = max(latest["mfe_u"], signed_u)
        latest["mae_u"] = max(latest["mae_u"], -signed_u)
        record: dict[str, Any] = {
            "minute": p.entry_time_s - p.entry_time_s % 60,
            "time_msc": t.time_msc,
            "entry_time_msc": p.entry_time_msc,
            "side": p.side,
            "mid2": t.bid_u + t.ask_u,
            "signed_quote_move_u": signed_u,
            "mfe_u": latest["mfe_u"],
            "mae_u": latest["mae_u"],
            "reason": reason,
        }
        super()._record_close(t, reason, exit_u)
        self.close_observations.append(record)
        self._last_close = record
        self._path_in_position = None

    def concordance_summary(self) -> dict[str, Any]:
        return {
            "entry_authority": "frozen_R9_v190_python",
            "dual_basket_role": "causal_entry_evidence_no_veto",
            "micro180_v9_untouched": True,
            "live_broker_enabled": False,
            "merged_trade_labels_used_at_entry": False,
            "entries": len(self.entries),
            "closes": len(self.trades),
            "counters": dict(self.v10_stats),
        }

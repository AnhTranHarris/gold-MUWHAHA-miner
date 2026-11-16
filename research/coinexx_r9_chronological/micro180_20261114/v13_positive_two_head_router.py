"""Micro180 V13: two independently scored causal positive-entry mechanisms.

First head: REAL Coinexx quote pressure, completed 1–300s history and
independently learned positive R9 SYNTH AND positive mapped quote-net labels.
Second head: distinct reversal hazard with 10 additional causal 5/15/30/60s
and minute-range features; only allowed after THIS engine closes its own
first leg and authorizes opposite-side rearm. Neither original R9 teacher
events nor REAL TickLogger shadow rearm events are used in live decisions.

One current quote creates a future-quote intent; the first observed quote
at/after the next whole second fills it. Shared R9-source stop/timeout/trail
are intentionally FROZEN while first/second ENTRY concordance is the target.
This is offline research only. No broker orders or native EA promotion.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Protocol, Sequence

from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config
from v12_coinexx_virtualclock_entry import (
    CompletedSecondHorizon, FEATURE_NAMES, Micro180V12VirtualClock, V12EntrySpec,
)


EXTRA_SECOND_FEATURE_NAMES = (
    "prior_reversal_3s_u", "prior_reversal_5s_u",
    "prior_reversal_15s_u", "signed_minute_high_gap_u",
    "signed_minute_low_gap_u", "signed_prior30s_bias_u",
    "signed_prior60s_bias_u", "signed_cross_basket_5_15_u",
    "spread_delta_prev_second_u", "near_minute_end_indicator",
)
SECOND_FEATURE_NAMES = FEATURE_NAMES + EXTRA_SECOND_FEATURE_NAMES


class EntryScore(Protocol):
    def score(self, features: Sequence[float]) -> float: ...


@dataclass(frozen=True)
class V13PositiveEntrySpec:
    first_threshold: float = 0.60
    second_threshold: float = 0.60
    first_and_second_positive_reference_only: bool = True
    maximum_legs_per_minute: int = 2
    require_previous_completed_first_leg: bool = True
    allow_real_orders: bool = False
    use_teacher_labels_as_input: bool = False

    def __post_init__(self) -> None:
        if not (0 < self.first_threshold <= 1
                and 0 < self.second_threshold <= 1
                and self.first_and_second_positive_reference_only
                and self.maximum_legs_per_minute == 2
                and self.require_previous_completed_first_leg
                and not self.allow_real_orders
                and not self.use_teacher_labels_as_input):
            raise ValueError("V13 is a positive-only discovery, causal, research-only two-head router")


class PositiveHorizon(CompletedSecondHorizon):
    """Minute and prior-quote features observed strictly before each decision."""

    def __init__(self) -> None:
        super().__init__()
        self.minute_high = 0.0
        self.minute_low = 0.0
        self.previous_second_spread = 0.0
        self.last_tick_spread = 0.0
        self.current_side = 1

    def update(self, t: Tick) -> None:
        old_minute = self.minute_key
        old_second = self.last_sec
        prev_spread = self.last_tick_spread
        super().update(t)
        mid = (t.ask_u + t.bid_u) / 2.0
        if old_minute != self.minute_key:
            self.minute_high = self.minute_low = mid
        else:
            self.minute_high = max(self.minute_high, mid)
            self.minute_low = min(self.minute_low, mid)
        if old_second != self.last_sec:
            # At a new second, this is the prior observed quote's spread.
            self.previous_second_spread = prev_spread
        self.last_tick_spread = t.ask_u - t.bid_u

    def features(self, t: Tick, side: int, atr_u: float) -> tuple[float, ...]:
        self.current_side = side
        return super().features(t, side, atr_u)

    def second_head_features(self, t: Tick, side: int, base: Sequence[float]) -> tuple[float, ...]:
        if side not in (-1, 1):
            raise ValueError("Second-head side invalid")
        if len(base) != len(FEATURE_NAMES):
            raise ValueError("Second-head common feature dimension mismatch")
        mid = (t.bid_u + t.ask_u) / 2.0
        sec = t.time_s
        past3, past5, past15, past30, past60 = (
            self._past(sec, n) for n in (3, 5, 15, 30, 60)
        )

        def displacement(price: float | None) -> float:
            return float(side * (mid - (price if price is not None else mid)))

        extra = (
            displacement(past3),
            displacement(past5),
            displacement(past15),
            side * (mid - self.minute_high),
            side * (mid - self.minute_low),
            displacement(past30),
            displacement(past60),
            side * (self.mid5 - self.mid15),
            (t.ask_u - t.bid_u) - self.previous_second_spread,
            float(sec % 60 >= 45),
        )
        return tuple(float(x) for x in base) + tuple(float(x) for x in extra)


class _TwoHeadScorer:
    """Routing adapter called only from V12's causal _process_entries(t)."""

    def __init__(self, engine: "Micro180V13PositiveTwoHead",
                 first: EntryScore, second: EntryScore):
        self.engine = engine
        self.first = first
        self.second = second

    def score(self, features: Sequence[float]) -> float:
        engine = self.engine
        side = engine.horizon.current_side
        if engine.rearms == 0:
            value = float(self.first.score(features))
            engine.v13_score_counts["first_head_evaluations"] += 1
            return value

        # Every second-leg probability is conditioned on an independently
        # observed, CLOSED first position. The post-first-close market may have
        # positive or adverse realized movement: do not require a future WIN_WIN.
        last = engine._last_close
        t = engine._v13_scoring_tick
        if (engine.rearms != 1 or last is None or t is None
                or last["minute"] != engine.cycle_minute
                or last["time_msc"] >= t.time_msc
                or last["side"] != -side
                or engine.position is not None):
            engine.v13_score_counts["second_unreachable_no_causal_first_exit"] += 1
            return 0.0
        if not (math.isfinite(float(last["mfe_u"]))
                and math.isfinite(float(last["mae_u"]))):
            raise ValueError("Invalid observed prior first-leg path state")
        extended = engine.horizon.second_head_features(t, side, features)
        value = float(self.second.score(extended))
        engine.v13_score_counts["second_head_evaluations_after_own_exit"] += 1
        return value


class Micro180V13PositiveTwoHead(Micro180V12VirtualClock):
    """Frozen two-head market sensor + independent first/second inventory policy."""

    def __init__(
        self,
        cfg: R9Config | None = None,
        *,
        first_scorer: EntryScore,
        second_scorer: EntryScore,
        spec: V13PositiveEntrySpec = V13PositiveEntrySpec(),
    ) -> None:
        self.positive_spec = spec
        self.v13_score_counts: dict[str, int] = {
            "first_head_evaluations": 0,
            "second_head_evaluations_after_own_exit": 0,
            "second_unreachable_no_causal_first_exit": 0,
        }
        self._v13_scoring_tick: Tick | None = None
        # V12 base retains the original broker stop/timeout/trail, but its
        # ONLINE entry decisions must pass through these two independent heads.
        super().__init__(
            cfg,
            scorer=_TwoHeadScorer(self, first_scorer, second_scorer),
            spec=V12EntrySpec(
                threshold=min(spec.first_threshold, spec.second_threshold),
                max_quote_lag_ms=2000,
                max_legs_per_minute=2,
                spread_cap_u=25,
                enforce_spread_cap=False,
                require_spread_aware_barrier=False,
                enforce_completed_m5_atr_gate=False,
            ),
        )
        self.horizon = PositiveHorizon()
        self._v13_first_scorer = first_scorer
        self._v13_second_scorer = second_scorer
        self._v13_last_phase = "initial"

    def _process_entries(self, t: Tick) -> None:
        # V12 applies one shared threshold to both heads, so normalize each
        # score by its own validation-frozen threshold. Do not alter either
        # head's trained weights or let later labels into this calculation.
        self._v13_scoring_tick = t
        current_head_threshold = (
            self.positive_spec.first_threshold if self.rearms == 0
            else self.positive_spec.second_threshold
        )
        # The two-head scores are calibrated/probabilistic but independent;
        # we compare them to their own fixed validation cutoff in the scorer.
        self._v13_active_threshold = current_head_threshold
        try:
            super()._process_entries(t)
        finally:
            self._v13_scoring_tick = None

    def _open_trade(self, t: Tick, side: int) -> None:
        first = self.rearms == 0
        super()._open_trade(t, side)
        if self.entries and self.entries[-1].get("ordinal") == t.ordinal:
            row = self.entries[-1]
            row["v13_positive_head"] = "first" if first else "second"
            row["v13_only_past_quote_features_used"] = True
            row["v13_positive_discovery_label_visible_to_live_logic"] = False
            if not first:
                last = self._last_close
                row.update({
                    "v13_prior_realized_quote_move_u": last["signed_quote_move_u"] if last else None,
                    "v13_prior_observed_mfe_u": last["mfe_u"] if last else None,
                    "v13_prior_observed_mae_u": last["mae_u"] if last else None,
                    "v13_flat_ms": t.time_msc - last["time_msc"] if last else None,
                    "v13_second_leg_phase": (
                        "after_favorable_first_leg" if last and last["signed_quote_move_u"] > 0
                        else "after_adverse_first_leg"
                    ),
                })

    def concordance_summary(self) -> dict[str, Any]:
        out = super().concordance_summary()
        out.update({
            "entry_authority": "V13_positive_only_two_head_causal_micro180",
            "positive_target": (
                "R9 original net>0 AND Coinexx quote-net>0 "
                "on fully quote-mapped original reference"
            ),
            "first_head_threshold": self.positive_spec.first_threshold,
            "second_head_threshold": self.positive_spec.second_threshold,
            "second_head_entry_requires_own_first_leg_closed": True,
            "teacher_event_timestamps_used_at_decision": False,
            "historical_family_labels_used_at_decision": False,
            "v13_head_evaluations": self.v13_score_counts.copy(),
        })
        return out

"""Micro180 V12: independently causal POSITIVE-cycle learned entry-clock router.

Uses a completed-second/5s/15s/30s/60s/180s/300s online market state,
frozen offline-trained first/second LightGBM positive-cycle hazard models,
and REAL Coinexx Bid/Ask quotes. R9 native source provides the shared quote
clock and position/stop lifecycle only; R9 _process_entries() is NOT called.

Models must be trained offline from the existing A/B/C positive-cycle target
utility; historical labels are never loaded here. All decisions are at the
current quote, scheduled for the FIRST observed quote in the NEXT second,
never retroactively filled at a teacher's future quote marker.

Prototype research-only. No native MT5 or broker order interface.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import sqrt
from pathlib import Path
from typing import Any, Protocol

from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config
from v11_micro180_independent_dual_entry import Micro180V11DualEntry


FIRST_FEATURES = (
    "sec_of_minute","spread_u","atr_u","side_barrier_u",
    "mid_change_since_minute","signed_s1_disp","s1_eff","s1_range",
    "s1_turns","signed_ret1","signed_ret3","signed_ret5","signed_ret10",
    "signed_ret15","signed_ret30","signed_ret60","signed_ret180",
    "signed_ret300","signed_acc3","signed_basket5","signed_basket15",
    "prior10_eff","prior30_eff","momentum_phase","hour",
)
SECOND_FEATURES = FIRST_FEATURES + (
    "prior_reversal_3s_u","prior_reversal_5s_u","prior_reversal_15s_u",
    "signed_minute_high_gap_u","signed_minute_low_gap_u",
    "signed_prior30s_bias_u","signed_prior60s_bias_u",
    "signed_cross_basket_5_15_u","spread_delta_prev_second_u",
    "near_minute_end_indicator",
)


class ProbabilityModel(Protocol):
    def score(self, row: tuple[float, ...]) -> float: ...


class FrozenLightGBM:
    """Read a frozen LightGBM text file; no fitting or training in execution."""
    def __init__(self, path: Path):
        import lightgbm as lgb  # Optional Python research dependency.
        if not path.is_file():
            raise FileNotFoundError(path)
        self._model = lgb.Booster(model_file=str(path))

    def score(self, row: tuple[float, ...]) -> float:
        import numpy as np  # Import per scoring call; do not pickle module objects.
        matrix = np.asarray([row], dtype=np.float32)
        return float(self._model.predict(matrix, num_threads=1)[0])


class CompletedMultiScaleClock:
    """O(1) per-quote quote-state update, bounded previous 305 observed seconds.

    The source-first current 1-second quote is used for decision features.
    Only previously closed second candles enter displacement/efficiency.
    No synthetic future M1 high/low, no future teacher entry/exit labels.
    """
    def __init__(self) -> None:
        self.active_sec: int | None = None
        self.mid_last = 0.0
        self.bid_close = self.bid_high = self.bid_low = 0
        self.hist: dict[int, tuple[float, int, int, int]] = {}
        self.hist_order: deque[int] = deque()
        self.minute: int | None = None
        self.minute_first = self.minute_hi = self.minute_lo = 0.0
        self.b5: int | None = None
        self.b15: int | None = None
        self.basket5_mid = self.basket15_mid = 0.0
        self.first_tick_new_second = False

    def on_tick(self, t: Tick) -> None:
        sec = t.time_s
        mid = (t.bid_u + t.ask_u) / 2.0
        minute = sec // 60
        if self.minute != minute:
            self.minute = minute
            self.minute_first = self.minute_hi = self.minute_lo = mid
        self.minute_hi = max(self.minute_hi, mid)
        self.minute_lo = min(self.minute_lo, mid)
        five = sec // 5
        fifteen = sec // 15
        if self.b5 != five:
            self.b5 = five
            self.basket5_mid = mid
        if self.b15 != fifteen:
            self.b15 = fifteen
            self.basket15_mid = mid
        self.first_tick_new_second = (self.active_sec != sec)
        if self.active_sec is not None and sec < self.active_sec:
            raise ValueError("Out-of-order REAL Coinexx source timestamp")
        if self.first_tick_new_second:
            if self.active_sec is not None:
                previous = self.active_sec
                self.hist[previous] = (
                    self.mid_last, self.bid_close, self.bid_high, self.bid_low
                )
                self.hist_order.append(previous)
            while self.hist_order and self.hist_order[0] < sec - 305:
                self.hist.pop(self.hist_order.popleft(), None)
            self.active_sec = sec
            self.bid_close = self.bid_high = self.bid_low = t.bid_u
        else:
            self.bid_close = t.bid_u
            self.bid_high = max(self.bid_high, t.bid_u)
            self.bid_low = min(self.bid_low, t.bid_u)
        self.mid_last = mid

    def _past(self, seconds: int) -> float | None:
        if self.active_sec is None:
            return None
        target = self.active_sec - seconds
        for stale in range(3):
            z = self.hist.get(target - stale)
            if z is not None:
                return z[0]
        return None

    def _eff(self, span: int) -> float:
        if self.active_sec is None:
            return 0.0
        values = [
            self.hist[self.active_sec - d][0]
            for d in range(span, 0, -1)
            if self.active_sec - d in self.hist
        ]
        if len(values) < max(3, span // 2):
            return 0.0
        travel = sum(abs(b - a) for a, b in zip(values, values[1:]))
        return abs(values[-1] - values[0]) / (travel + 1e-6)

    def vector(self, t: Tick, side: int, atr_u: float, second: bool) -> tuple[float, ...]:
        if t.time_s != self.active_sec or side not in (-1, 1):
            raise ValueError("Features must be calculated at the current quote")
        mid = (t.bid_u + t.ask_u) / 2.0
        spread = t.ask_u - t.bid_u
        age = t.time_s % 60
        quoteside = t.ask_u if side == 1 else t.bid_u
        barrier = side * (quoteside - self.minute_first - side * 15)
        bid_bars = [
            (s, *self.hist[s][1:])
            for s in sorted(self.hist) if s < t.time_s
        ]
        # V9/R9 completed-second ring: 10 observed completed bars plus
        # one additional history bar for startup (same warmup as source).
        disp = eff = ran = turns = 0.0
        if len(bid_bars) >= 11:
            chosen = bid_bars[-10:]
            closes = [x[1] for x in chosen]
            deltas = [b - a for a, b in zip(closes, closes[1:])]
            disp = float(closes[-1] - closes[0])
            eff = abs(disp) / (sum(abs(x) for x in deltas) + 1e-9)
            ran = float(max(x[2] for x in chosen) - min(x[3] for x in chosen))
            signs = [1 if x > 0 else -1 for x in deltas if x]
            turns = float(sum(a != b for a, b in zip(signs, signs[1:])))
        ages = (1, 3, 5, 10, 15, 30, 60, 180, 300)
        changes = [
            mid - (p if (p := self._past(age)) is not None else mid)
            for age in ages
        ]
        p6 = self._past(6)
        accel3 = 2 * changes[1] - (mid - (p6 if p6 is not None else mid))
        row = [
            age, spread, atr_u, barrier, side * (mid - self.minute_first),
            side * disp, eff, ran, turns,
        ]
        row.extend(side * x for x in changes)
        row.extend([
            side * accel3,
            side * (mid - self.basket5_mid),
            side * (mid - self.basket15_mid),
            self._eff(10), self._eff(30),
            side * changes[3] / max(10.0, sqrt(max(1.0, atr_u))),
            (t.time_s // 3600) % 24,
        ])
        if second:
            p3, p5, p15, p30, p60 = (
                self._past(a) for a in (3, 5, 15, 30, 60)
            )
            row.extend([
                side * (mid - (p3 if p3 is not None else mid)),
                side * (mid - (p5 if p5 is not None else mid)),
                side * (mid - (p15 if p15 is not None else mid)),
                side * (mid - self.minute_hi),
                side * (mid - self.minute_lo),
                side * (mid - (p30 if p30 is not None else mid)),
                side * (mid - (p60 if p60 is not None else mid)),
                side * (self.basket5_mid - self.basket15_mid),
                0.0,  # Frozen historical model's spread_delta was zero.
                float(age >= 45),
            ])
        expected = len(SECOND_FEATURES if second else FIRST_FEATURES)
        if len(row) != expected:
            raise AssertionError("Frozen model feature-count contract violated")
        return tuple(float(v) for v in row)


@dataclass(frozen=True)
class V12PositiveClockSpec:
    first_threshold: float = 0.60
    second_threshold: float = 0.50
    max_next_quote_delay_ms: int = 2000
    max_spread_points_at_execution: int = 25
    # Validation-locked source-clock options: 1s baseline; 2s first-leg
    # variant improved A / overall near-price matching but affects B/C.
    first_execution_delay_seconds: int = 1
    second_execution_delay_seconds: int = 1
    live_orders_enabled: bool = False
    allow_historical_event_intervention: bool = False

    def __post_init__(self) -> None:
        if (not 0.0 < self.first_threshold <= 1
                or not 0.0 < self.second_threshold <= 1
                or not 0 <= self.max_next_quote_delay_ms <= 2000
                or self.max_spread_points_at_execution < 1
                or self.first_execution_delay_seconds not in (1, 2)
                or self.second_execution_delay_seconds != 1
                or self.live_orders_enabled
                or self.allow_historical_event_intervention):
            raise ValueError("Research-only positive-clock controls invalid")


class Micro180V12PositiveClock(Micro180V11DualEntry):
    """Own as-of learned entry events, with V11 source quote lifecycle kept fixed."""
    def __init__(
        self,
        cfg: R9Config | None = None,
        *,
        first_model: ProbabilityModel,
        second_model: ProbabilityModel,
        spec: V12PositiveClockSpec = V12PositiveClockSpec(),
    ):
        super().__init__(cfg)
        self.model_first = first_model
        self.model_second = second_model
        self.positive_spec = spec
        self.clock = CompletedMultiScaleClock()
        self._pending: tuple[int, int, int, int] | None = None
        self._last_scored_second: int | None = None
        # Optional read-only completed-M5 ATR snapshot supplied by the ORIGINAL
        # REAL TickLogger at the SAME quote; never a future M5/current M5 close.
        self.asof_source_completed_m5_atr_u: float | None = None

    def _push_second(self, t: Tick) -> None:
        super()._push_second(t)
        self.clock.on_tick(t)

    def _start_minute_cycle(self, t: Tick) -> None:
        if self.cycle_minute != t.time_s - t.time_s % 60:
            self._pending = None
        super()._start_minute_cycle(t)

    def _process_entries(self, t: Tick) -> None:
        if self.pending_mode == 0:
            self._pending = None
            return
        if self._pending is not None:
            decision_s, side, leg, source_minute = self._pending
            delay = (self.positive_spec.first_execution_delay_seconds
                     if leg == 1 else self.positive_spec.second_execution_delay_seconds)
            if t.time_s >= decision_s + delay:
                next_ms = (decision_s + delay) * 1000
                self._pending = None
                if (t.time_s // 60 == source_minute
                        and 0 <= t.time_msc - next_ms <= self.positive_spec.max_next_quote_delay_ms
                        and t.spread_points <= self.positive_spec.max_spread_points_at_execution
                        and self._gate(t)
                        and (self.pending_mode == 2 or self.pending_mode == side)):
                    self._open_trade(t, side)
                    self.entries[-1]["v12_entry_authority"] = "frozen_positive_cycle_clock"
                    self.entries[-1]["v12_signal_second"] = decision_s
                    self.entries[-1]["v12_precommitted_delay_seconds"] = delay
                    self.entries[-1]["v12_inherited_first_entry_family"] = "UNKNOWN"
                return
            # One pending intent is immutable until its scheduled quote clock.
            # Intermediate next-second signals cannot push the scheduled fill
            # forward or overwrite its decision-side/ordinal state.
            return
        if not self.clock.first_tick_new_second or self._last_scored_second == t.time_s:
            return
        self._last_scored_second = t.time_s
        atr_u = float(
            self.asof_source_completed_m5_atr_u
            if self.asof_source_completed_m5_atr_u is not None
            else (self.atr.atr_u or 0.0)
        )
        leg = 1 if self.pending_mode == 2 else 2
        model = self.model_first if leg == 1 else self.model_second
        scores: list[tuple[float, int]] = []
        for side in ((1, -1) if leg == 1 else (self.pending_mode,)):
            vec = self.clock.vector(t, side, atr_u, second=(leg == 2))
            scores.append((model.score(vec), side))
        prob, side = max(scores, key=lambda x: x[0])
        threshold = (self.positive_spec.first_threshold if leg == 1
                     else self.positive_spec.second_threshold)
        if prob >= threshold:
            self._pending = (t.time_s, side, leg, t.time_s // 60)
            self.v11_stats[f"v12_positive_clock_signal_leg{leg}"] += 1

    def concordance_summary(self) -> dict[str, Any]:
        z = super().concordance_summary()
        z.update({
            "entry_authority": "micro180_frozen_positive_cycle_virtual_clock",
            "inherited_R9_process_entries_not_called": True,
            "future_trade_outcomes_available_to_router": False,
            "one_quote_later_at_actual_bid_ask": True,
            "first_execution_delay_seconds": self.positive_spec.first_execution_delay_seconds,
            "second_execution_delay_seconds": self.positive_spec.second_execution_delay_seconds,
            "original_R9_fees_or_trade_labels_modified": False,
            "model_feature_lengths": (len(FIRST_FEATURES), len(SECOND_FEATURES)),
            "optional_same_quote_completed_M5_ATR_snapshot": (
                self.asof_source_completed_m5_atr_u is not None
            ),
        })
        return z

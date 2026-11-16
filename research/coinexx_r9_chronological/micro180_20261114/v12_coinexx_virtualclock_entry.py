"""Micro180 V12 — autonomous multi-horizon entry hazard + Coinexx virtual clock.

ENTRY ONLY research fork. No future R9 reference event may reach on_tick().
R9 v1.90 is retained for shared, known-causal quote sequencing, position
bookkeeping and temporarily frozen exit/rearm accounting; its entry controller
is never called. The independent Micro180 1s/5s/15s/30s/60s/180s/300s
feature clock creates an entry INTENT on one quote; only a LATER actual source
quote at the NEXT completed second can fill it. There is no synthetic tick
price or invented fill.

The signature feature order matches V12 source-replay research. A frozen
LightGBM Booster may be loaded for offline testing; the model is an optional
plug-in, never a pretrained claim or live order provider.
"""
from __future__ import annotations

import collections
import math
from dataclasses import dataclass
from typing import Any, Callable, Protocol, Sequence

from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config
from v11_micro180_independent_dual_entry import Micro180V11DualEntry


FEATURE_NAMES = (
    "sec_of_minute", "spread_u", "atr_u", "side_barrier_u",
    "mid_change_since_minute", "signed_s1_disp", "s1_eff",
    "s1_range", "s1_turns", "signed_ret1", "signed_ret3",
    "signed_ret5", "signed_ret10", "signed_ret15", "signed_ret30",
    "signed_ret60", "signed_ret180", "signed_ret300",
    "signed_acc3", "signed_basket5", "signed_basket15",
    "prior10_eff", "prior30_eff", "momentum_phase", "hour",
)
LOOKBACKS = (1, 3, 5, 10, 15, 30, 60, 180, 300)


class CausalScore(Protocol):
    def score(self, features: Sequence[float]) -> float: ...


class FrozenLightGBMScore:
    """A serialized training model; never fit/update on incoming future ticks."""
    def __init__(self, model_file: str):
        import lightgbm as lgb
        self.booster = lgb.Booster(model_file=model_file)
        if self.booster.num_feature() != len(FEATURE_NAMES):
            raise ValueError("Frozen hazard feature dimensionality mismatch")

    def score(self, features: Sequence[float]) -> float:
        import numpy as np
        # Deliberately a frozen single quote; infer once per source second.
        a = np.asarray([features], dtype=np.float32)
        return float(self.booster.predict(a)[0])


@dataclass(frozen=True)
class V12EntrySpec:
    threshold: float = 0.70
    max_quote_lag_ms: int = 2000
    max_legs_per_minute: int = 2
    spread_cap_u: int = 25
    enforce_spread_cap: bool = True
    require_spread_aware_barrier: bool = False
    enforce_completed_m5_atr_gate: bool = False
    permit_broker_orders: bool = False
    teacher_reference_at_decision: bool = False

    def __post_init__(self) -> None:
        if not (0 < self.threshold <= 1 and self.max_quote_lag_ms >= 0
                and self.spread_cap_u > 0 and self.max_legs_per_minute == 2
                and not self.permit_broker_orders
                and not self.teacher_reference_at_decision):
            raise ValueError("V12 is two-leg causal entry research only")


@dataclass(frozen=True)
class EntryIntent:
    signal_ordinal: int
    signal_ms: int
    signal_minute: int
    side: int
    next_second_start_ms: int
    hazard_score: float
    features: tuple[float, ...]


class CompletedSecondHorizon:
    """O(1) quote updates; bounded 305 observed completed-second closes.

    Gaps are not backfilled with invented 1-second candles. Completed S1 uses
    R9's last ten OBSERVED finished seconds (requires 11 warmup observations);
    longer features use time-indexed past closes with at most 2s stale tolerance.
    """
    def __init__(self) -> None:
        self.seconds: dict[int, float] = {}
        self.order: collections.deque[int] = collections.deque()
        self.last_sec: int | None = None
        self.last_mid: float = 0.0
        self.cur_bid_hi: int = 0
        self.cur_bid_lo: int = 0
        self.cur_bid_close: int = 0
        self.completed_bid: collections.deque[tuple[int, int, int, int]] = (
            collections.deque(maxlen=305)
        )
        self.minute_key: int | None = None
        self.minute_mid: float = 0.0
        self.bucket5: int | None = None
        self.bucket15: int | None = None
        self.mid5: float = 0.0
        self.mid15: float = 0.0
        self.first_tick_this_second: bool = False

    def update(self, t: Tick) -> None:
        sec = t.time_s
        mid = (t.bid_u + t.ask_u) / 2.0
        minute = sec // 60
        if self.last_sec is not None and sec < self.last_sec:
            raise ValueError("Source quotes must be in chronological order")
        if self.minute_key != minute:
            self.minute_key = minute
            self.minute_mid = mid
        if self.bucket5 != sec // 5:
            self.bucket5 = sec // 5
            self.mid5 = mid
        if self.bucket15 != sec // 15:
            self.bucket15 = sec // 15
            self.mid15 = mid
        self.first_tick_this_second = sec != self.last_sec
        if self.first_tick_this_second:
            if self.last_sec is not None:
                self.seconds[self.last_sec] = self.last_mid
                self.order.append(self.last_sec)
                self.completed_bid.append((
                    self.last_sec, self.cur_bid_close,
                    self.cur_bid_hi, self.cur_bid_lo,
                ))
                while self.order and self.order[0] < sec - 305:
                    del self.seconds[self.order.popleft()]
            self.last_sec = sec
            self.cur_bid_hi = self.cur_bid_lo = self.cur_bid_close = t.bid_u
        else:
            self.cur_bid_hi = max(self.cur_bid_hi, t.bid_u)
            self.cur_bid_lo = min(self.cur_bid_lo, t.bid_u)
            self.cur_bid_close = t.bid_u
        self.last_mid = mid

    def _past(self, sec: int, length: int) -> float | None:
        # Equivalent to the experiment's latest COMPLETED <= (sec-length)
        # close with no more than two seconds of stale carry.
        for offset in (0, 1, 2):
            price = self.seconds.get(sec - length - offset)
            if price is not None:
                return price
        return None

    def _efficiency(self, sec: int, length: int) -> float:
        mids = [self.seconds[sec - j]
                for j in range(length, 0, -1) if sec - j in self.seconds]
        if len(mids) < max(3, length // 2):
            return 0.0
        travel = sum(abs(b - a) for a, b in zip(mids, mids[1:]))
        return abs(mids[-1] - mids[0]) / (travel + 1e-6)

    def _s1(self) -> tuple[float, float, float, float]:
        if len(self.completed_bid) < 11:
            return 0.0, 0.0, 0.0, 0.0
        last10 = list(self.completed_bid)[-10:]
        closes = [x[1] for x in last10]
        displacement = closes[-1] - closes[0]
        steps = [b - a for a, b in zip(closes, closes[1:])]
        travel = sum(abs(x) for x in steps)
        signs = [(1 if x > 0 else -1) for x in steps if x != 0]
        turns = sum(a != b for a, b in zip(signs, signs[1:]))
        price_range = max(x[2] for x in last10) - min(x[3] for x in last10)
        return displacement, abs(displacement) / (travel + 1e-9), price_range, turns

    def features(self, t: Tick, side: int, atr_u: float) -> tuple[float, ...]:
        if side not in (-1, 1) or t.time_s != self.last_sec:
            raise ValueError("Feature side or as-of quote state invalid")
        sec = t.time_s
        mid = (t.bid_u + t.ask_u) / 2.0
        displacement, efficiency, price_range, turns = self._s1()
        actual_entry_quote = t.ask_u if side > 0 else t.bid_u
        barrier = side * (
            actual_entry_quote -
            (self.minute_mid + (15 if side > 0 else -15))
        )
        changes: list[float] = []
        for h in LOOKBACKS:
            previous = self._past(sec, h)
            changes.append(mid - previous if previous is not None else 0.0)
        r3 = changes[1]
        past6 = self._past(sec, 6)
        r6 = mid - (past6 if past6 is not None and past6 != 0 else mid)
        acceleration = 2 * r3 - r6
        return tuple(float(x) for x in (
            sec % 60, t.ask_u - t.bid_u, atr_u, barrier,
            side * (mid - self.minute_mid), side * displacement,
            efficiency, price_range, turns,
            *(side * x for x in changes),
            side * acceleration, side * (mid - self.mid5),
            side * (mid - self.mid15),
            self._efficiency(sec, 10), self._efficiency(sec, 30),
            side * changes[3] / max(10, math.sqrt(max(1, atr_u))),
            (sec // 3600) % 24,
        ))


class Micro180V12VirtualClock(Micro180V11DualEntry):
    """No original R9 entry call; independently scored, next-quote order intents."""

    def __init__(
        self,
        cfg: R9Config | None = None,
        *,
        scorer: CausalScore,
        spec: V12EntrySpec = V12EntrySpec(),
    ) -> None:
        super().__init__(cfg)
        self.v12_spec = spec
        self.scorer = scorer
        self.horizon = CompletedSecondHorizon()
        self.entry_intent: EntryIntent | None = None
        self.v12_counts: collections.Counter[str] = collections.Counter()
        self._v12_scored_second: int | None = None

    def _push_second(self, t: Tick) -> None:
        super()._push_second(t)
        self.horizon.update(t)

    def _process_entries(self, t: Tick) -> None:
        # V11 and R9 _process_entries are never delegated to.
        current_minute = t.time_s - t.time_s % 60
        if self.entry_intent is not None:
            pending = self.entry_intent
            if current_minute != pending.signal_minute:
                self.entry_intent = None
                self.v12_counts["pending_crossed_minute_cancelled"] += 1
                return
            if t.time_msc < pending.next_second_start_ms:
                return
            if t.time_msc > pending.next_second_start_ms + self.v12_spec.max_quote_lag_ms:
                self.entry_intent = None
                self.v12_counts["pending_source_tick_stale_cancelled"] += 1
                return
            if self.pending_mode not in (2, pending.side):
                self.entry_intent = None
                self.v12_counts["pending_inventory_state_changed"] += 1
                return
            # Actual BUY Ask / SELL Bid at the first *subsequent* observed quote.
            self._v11_pending_receipt = {
                "source_signal_ms": pending.signal_ms,
                "signal_score": pending.hazard_score,
                "signal_quote_ordinal": pending.signal_ordinal,
                "virtual_quote_delay_ms": t.time_msc - pending.signal_ms,
                "asof_regime": "early_probe" if t.time_s % 60 <= 5 else (
                    "transition" if t.time_s % 60 < 15 else "mature_directional"
                ),
            }
            before = len(self.entries)
            self._open_trade(t, pending.side)
            if len(self.entries) > before:
                self.entries[-1].update({
                    "v10_entry_authority": "v12_independent_micro180_multi_horizon_hazard",
                    "v11_entry_route": "v12_multi_horizon_virtual_real_quote_clock",
                    "v12_independent_hazard_score": pending.hazard_score,
                    "v12_signal_ms": pending.signal_ms,
                    "v12_target_second_start_ms": pending.next_second_start_ms,
                    "v12_actual_queued_quote_ms": t.time_msc,
                    "v12_actual_quote_delay_ms": t.time_msc - pending.signal_ms,
                    "v12_no_teacher_event_at_decision": True,
                })
                self.v12_counts["executed_on_real_quote"] += 1
            self.entry_intent = None
            self._v11_pending_receipt = None
            return

        if self.pending_mode == 0 or not self.horizon.first_tick_this_second:
            return
        if self._v12_scored_second == t.time_s:
            return
        self._v12_scored_second = t.time_s

        if self.v12_spec.enforce_completed_m5_atr_gate and not self._gate(t):
            self.v12_counts["atr_or_regime_rejected"] += 1
            return
        if (self.v12_spec.enforce_spread_cap
                and t.ask_u - t.bid_u > self.v12_spec.spread_cap_u):
            self.v12_counts["spread_rejected"] += 1
            return
        scores: list[tuple[float, int, tuple[float, ...]]] = []
        for side in (1, -1):
            if self.pending_mode not in (2, side):
                continue
            fv = self.horizon.features(t, side, self.atr.atr_u or 0.0)
            if self.v12_spec.require_spread_aware_barrier and fv[3] < 0:
                continue
            value = float(self.scorer.score(fv))
            if not (math.isfinite(value) and 0.0 <= value <= 1.0):
                raise ValueError("Non-finite or non-probabilistic causal hazard")
            scores.append((value, side, fv))
        if not scores:
            return
        confidence, side, vector = max(scores, key=lambda x: x[0])
        if confidence < self.v12_spec.threshold:
            return
        self.entry_intent = EntryIntent(
            signal_ordinal=t.ordinal,
            signal_ms=t.time_msc,
            signal_minute=current_minute,
            side=side,
            next_second_start_ms=(t.time_s + 1) * 1000,
            hazard_score=confidence,
            features=vector,
        )
        self.v12_counts["independent_signal_committed"] += 1
        self.v12_counts[
            "early_second_signal" if t.time_s % 60 <= 5
            else "mature_second_signal"
        ] += 1

    def _start_minute_cycle(self, t: Tick) -> None:
        old_minute = self.cycle_minute
        super()._start_minute_cycle(t)
        if old_minute and self.cycle_minute != old_minute:
            if self.entry_intent is not None:
                self.v12_counts["prior_minute_intent_expired"] += 1
                self.entry_intent = None

    def concordance_summary(self) -> dict[str, Any]:
        base = super().concordance_summary()
        base.update({
            "entry_authority": "micro180_independently_trained_multi_horizon_hazard",
            "decision_source": "past_completed_Bid_seconds_live_bid_ask_M5_ATR",
            "five_minute_lookback": True,
            "next_real_source_second_execution": True,
            "future_synthetic_teacher_timestamps_used_by_engine": False,
            "native_order_execution_authorized": False,
            "v12": dict(self.v12_counts),
        })
        return base

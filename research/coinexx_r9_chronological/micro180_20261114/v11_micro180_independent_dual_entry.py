"""Micro180 V11: independently evaluated, zero-warmup dual-basket seed router.

The R9 v1.90 Python baseline provides a common quote clock, completed-M5 ATR,
broker-side exit emulation and same-minute inventory lifecycle. V11 OVERRIDES
both entry evaluation and minute-anchor construction: no R9 _process_entries()
decision is called. Two active 5s/15s baskets and past-only completed 1s bars
supply entry-state evidence.

Why a minute-seed lane? The original R9-Coinexx merged reference contains
80,680/192,487 FIRST entries by minute second 5 (41.9%), and B first entries
occur at median minute second 2. Requiring a mature *current* 5/15s basket
would structurally miss these events. The zero-warmup seed lane is a strict,
causal price threshold based on the first source quote of the minute and
PREVIOUSLY completed seconds; it does not read any teacher event timestamp.

R9 entry-price equivalence remains a hypothesis to be measured on actual
source ticks, not inferred from the combined teacher's future quote marks.
All exit/stop code is temporarily frozen to isolate ENTRY concordance.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config
from v10_r9_dual_concordance import Micro180V10R9Causal


@dataclass(frozen=True)
class V11DualEntrySpec:
    max_cycle_legs: int = 2
    live_orders_enabled: bool = False
    allow_future_teacher_entries: bool = False
    # Do not activate extra four-lane-only entries until full reference precision
    # and on-policy whole-system net support that expansion.
    allow_extra_basket_entries: bool = False

    def __post_init__(self) -> None:
        if (self.max_cycle_legs != 2 or self.live_orders_enabled
                or self.allow_future_teacher_entries or self.allow_extra_basket_entries):
            raise ValueError("Only two-leg causal entry-concordance research is authorized")


class Micro180V11DualEntry(Micro180V10R9Causal):
    """Independently generated micro180 dual-basket entries, not V10 R9 signals.

    Minute-seed is the immediate path for the early B/C opportunity classes.
    Basket 5/15 phase, four 5/15 x 15/30 lanes, R9-like completed-S1
    displacement/efficiency and completed-M5 regime are evaluated as-of.

    Family A/B/C is never known at entry. Once the first REAL-quote position
    closes, the observed first-leg sign/MAE/MFE/flat interval can supply
    PRE-REENTRY phase evidence (not the future second-leg outcome).
    """

    def __init__(
        self,
        cfg: R9Config | None = None,
        *,
        spec: V11DualEntrySpec = V11DualEntrySpec(),
    ) -> None:
        super().__init__(cfg)
        self.v11_spec = spec
        self._v11_minute_mid2: int | None = None
        self._v11_pending_receipt: dict[str, Any] | None = None
        self._v11_quality_snapshot: dict[str, Any] | None = None
        self.v11_stats: Counter[str] = Counter()

    def _start_minute_cycle(self, t: Tick) -> None:
        """Minute thresholds independently formed from current Coinexx quote."""
        minute = (t.time_s // 60) * 60
        if minute == self.cycle_minute:
            return
        self.cycle_minute = minute
        self.rearms = 0
        self.pending_mode = 2
        self._v11_minute_mid2 = t.bid_u + t.ask_u
        self.cycle_buy_u = self._round_half_positive(
            self._v11_minute_mid2 + self.cfg.gap_pips, 2
        )
        self.cycle_sell_u = self._round_half_positive(
            self._v11_minute_mid2 - self.cfg.gap_pips, 2
        )
        self.v11_stats["independent_minute_anchor"] += 1

    def _completed_second_quality(self, side: int) -> bool:
        """Independent R9-like S1 quant, calculated from micro180 180s ring.

        Completed BAR Bid closes/highs/lows only; active second is excluded.
        Preserve original R9 arithmetic first, rather than guessing at gains
        from altered coefficients. Dual-basket displacement is a separate as-of
        feature; it does not cause early-minute lookahead.
        """
        cfg = self.cfg
        length = max(cfg.velocity_lookback_sec, cfg.range_lookback_sec) + 1
        source = self.rolling.finished[1000]
        if len(source) < length:
            self.v11_stats["insufficient_completed_seconds"] += 1
            return False
        recent = list(source)
        vel = recent[-cfg.velocity_lookback_sec:]
        closes = [x.bid_close for x in vel]
        signed = closes[-1] - closes[0]
        steps = [b - a for a, b in zip(closes, closes[1:])]
        travel = sum(abs(x) for x in steps)
        eff = abs(signed) / (travel + 1e-9)
        prev = 0
        turns = 0
        for step in steps:
            sign = (1 if step > 0 else -1 if step < 0 else 0)
            if sign:
                if prev and prev != sign:
                    turns += 1
                prev = sign
        range_bars = recent[-cfg.range_lookback_sec:]
        amplitude = max(x.bid_hi for x in range_bars) - min(x.bid_lo for x in range_bars)
        self._v11_quality_snapshot = {
            "s1_bid_displacement_u": signed,
            "s1_bid_travel_u": travel,
            "s1_bid_efficiency": round(eff, 8),
            "s1_turns": turns,
            "s1_bid_range_u": amplitude,
        }
        if eff + 1e-12 < cfg.min_directional_eff:
            return False
        if turns > cfg.max_turns or amplitude < cfg.min_range_pips:
            return False
        if side > 0 and signed < cfg.min_velocity_pips:
            return False
        if side < 0 and signed > -cfg.min_velocity_pips:
            return False
        return True

    def _seed_signal(self, t: Tick) -> tuple[int, int]:
        """Independent first-minute mid bracket plus executable quote condition.

        Uses one contemporaneously built price anchor; no teacher trading
        timestamp, source_s1 or future quote mark. Returns side and penetration.
        """
        if self._v11_minute_mid2 is None:
            return 0, 0
        buy = self._round_half_positive(
            self._v11_minute_mid2 + self.cfg.gap_pips, 2
        )
        sell = self._round_half_positive(
            self._v11_minute_mid2 - self.cfg.gap_pips, 2
        )
        if self.pending_mode in (2, 1) and t.ask_u >= buy:
            return 1, t.ask_u - buy
        if self.pending_mode in (2, -1) and t.bid_u <= sell:
            return -1, sell - t.bid_u
        return 0, 0

    def _basket_snapshot(self, t: Tick, side: int, penetration: int) -> dict[str, Any]:
        """Current as-of 5s/15s state, independent of eventual trade outcome."""
        state: dict[str, Any] = {
            "entry_clock_source": "coinexx_live_quote_order",
            "zero_warmup_minute_seed": True,
            "seed_penetration_price_u": penetration,
            "seed_minute_mid2": self._v11_minute_mid2,
            "entry_second_of_minute": t.time_s % 60,
            "asof_regime": "early_probe" if t.time_s % 60 <= 5 else (
                "transition" if t.time_s % 60 < 15 else "mature_directional"
            ),
        }
        for seconds, width in ((5, 5000), (15, 15000)):
            candle = self.rolling.current.get(width)
            if candle is None:
                raise RuntimeError("Micro180 current basket unexpectedly absent")
            state[f"basket{seconds}_first_ms"] = candle.first_ms
            state[f"basket{seconds}_observed_ms"] = candle.last_ms - candle.first_ms
            state[f"basket{seconds}_signed_mid_move_u"] = (
                side * (candle.bid_close + candle.ask_close
                        - candle.bid_open - candle.ask_open) / 2.0
            )
            state[f"basket{seconds}_quote_count"] = candle.n
        state["previous_completed_5s_available"] = bool(self.rolling.finished[5000])
        state["previous_completed_15s_available"] = bool(self.rolling.finished[15000])
        return state

    def _process_entries(self, t: Tick) -> None:
        """Own entry decision: unlike V10, never call R9 _process_entries()."""
        if self.pending_mode == 0:
            return
        if not self._gate(t):  # completed M5 ATR / spread / session, as-of
            self.v11_stats["regime_gate_rejection"] += 1
            return
        side, penetration = self._seed_signal(t)
        if side == 0:
            self.v11_stats["seed_not_crossed"] += 1
            return
        if not self._completed_second_quality(side):
            self.v11_stats["completed_s1_rejected"] += 1
            return
        self._v11_pending_receipt = {
            **self._basket_snapshot(t, side, penetration),
            **(self._v11_quality_snapshot or {}),
        }
        try:
            self._open_trade(t, side)
        finally:
            self._v11_pending_receipt = None
            self._v11_quality_snapshot = None

    def _open_trade(self, t: Tick, side: int) -> None:
        before = len(self.entries)
        # Parent only records the opened position, plus V10 as-of features.
        # It is NOT the entry authority.
        super()._open_trade(t, side)
        if len(self.entries) == before:
            self.v11_stats["attempted_entry_not_opened"] += 1
            return
        receipt = dict(self._v11_pending_receipt or {})
        data = self.entries[-1]
        data.update({f"v11_{key}": value for key, value in receipt.items()})
        data["v10_entry_authority"] = "v11_independent_micro180_dual_basket"
        data["v11_entry_route"] = "minute_seed_previous_completed_S1"
        data["v11_current_five_fifteen_baskets_evaluated"] = True
        data["v11_quote_side"] = "ask" if side > 0 else "bid"
        data["v11_complete_cycle_family_known_at_entry"] = False
        if self.rearms > 0:
            # This uses the already closed first leg ONLY, never future outcome.
            prior = self._last_close
            data["v11_reentry_state"] = (
                "post_favorable_first_quote_exit"
                if prior is not None and prior["signed_quote_move_u"] > 0
                else "post_adverse_first_quote_exit"
            )
            data["v11_flat_interval_ms"] = (
                t.time_msc - prior["time_msc"] if prior else None
            )
        else:
            data["v11_reentry_state"] = "not_applicable"
        self.v11_stats["independent_entries"] += 1
        self.v11_stats[f"entry_phase_{data.get('v11_asof_regime', 'unknown')}"] += 1
        self.v11_stats[f"entry_leg_{self.rearms + 1}"] += 1

    def _arm_opposite_after_exit(self) -> None:
        # Reference merge supports no more than two legs per entry minute.
        if self.rearms >= self.v11_spec.max_cycle_legs - 1:
            self.pending_mode = 0
            self.v11_stats["cycle_leg_cap"] += 1
            return
        super()._arm_opposite_after_exit()

    def concordance_summary(self) -> dict[str, Any]:
        out = super().concordance_summary()
        out.update({
            "entry_authority": "independent_micro180_dual_basket_seed_router",
            "native_broker_orders_enabled": False,
            "reference_teacher_labels_used_at_entry": False,
            "early_current_basket_maturity_required": False,
            "max_legs_per_minute": self.v11_spec.max_cycle_legs,
            "additional_non_reference_lanes_enabled": False,
            "v11_counters": dict(self.v11_stats),
        })
        return out

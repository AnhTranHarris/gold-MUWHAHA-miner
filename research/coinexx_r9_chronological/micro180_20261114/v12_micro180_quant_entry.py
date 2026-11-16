"""Micro180 V12 — independent multiscale causal entry router.

Research only.  A frozen, fully transparent 19-factor logistic score uses:
minute-opening dislocation, active 5s/15s basket pressure, completed S1
directional efficiency/velocity/range, volatility-normalized accelerations,
within-minute quote-update imbalance, spread, and as-of completed M5 ATR.

The original 200k January 2 Coinexx logger quotes supplied a TRAIN portion
for provisional coefficients; its later same-day quotes were a tiny early
holdout, NOT certified generalization.  At runtime NO teacher date, entry
timestamp, exit outcome, market family, or future price is an input.

Unlike V11 (whose minute-seed entry replicated R9 quality), V12 takes entries
from its OWN micro180 factor score. Original R9 is common stop/rearm research
plumbing only. Three realized-cycle families must be scored after decisions.
"""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Any

from coinexx_r9.models import Tick
from v11_micro180_independent_dual_entry import Micro180V11DualEntry

# StandardScaler parameters and LogisticRegression coefficients are printed,
# inspectable numeric constants: no hidden pickle, native black box, future
# labels, or commercial indicator dependencies.
FACTOR_NAMES = (
    "minute_clock", "early_five_seconds", "minute_displacement",
    "active_five_second_impulse", "active_fifteen_second_impulse",
    "completed_s1_velocity", "completed_s1_efficiency",
    "completed_s1_range", "quote_direction_imbalance",
    "execution_side_spread", "current_spread", "completed_m5_atr",
    "s1_atr_displacement", "five_second_atr_impulse",
    "fifteen_second_atr_impulse", "minute_envelope_excess",
    "s1_direction_alignment", "five_second_alignment", "fifteen_second_alignment",
)
MEANS = (
    .4904716335825175,.10137182963790078,0.,0.,0.,0.,
    .39123753308145337,.7509496881211916,0.,
    .3964276582122676,.7928553164245352,.9921709026806775,
    0.,0.,0.,-.0801210984199965,
    .49397830594991227,.37611660551922155,.45471765831871114,
)
SCALES = (
    .2885768822353912,.30182044628186877,
    1.8891958405149918,1.0458662033715558,1.1792520572716523,
    .8832387917507951,.2586253056486634,.6152245581629933,
    .22570105101561963,.15014391851152845,.3002878370230569,
    .23078360916643245,.13420156039698347,.26804181276238914,
    .3019156618402048,1.313463558645725,
    .4999637378859184,.4844098518528111,.49794528768910334,
)
WEIGHTS = (
    -1.2014902009233035,.09443413042079202,
    -.7628507705123698,.1452725601222841,
    -.45397892135776063,.005423713267142589,
    -.006944128669258939,.12511299038665807,
    -.01651868918231816,-.1351716372356011,
    -.1351716372356011,.19020518472790982,
    .3009629966388154,-.2502989515199171,
    .16382410159456282,1.5362708552600817,
    -.05256598491325849,.13415118795264006,.24393557011986455,
)
INTERCEPT = -1.0530486303929627
assert len(FACTOR_NAMES) == len(MEANS) == len(SCALES) == len(WEIGHTS) == 19


def factor_probability(factors: tuple[float, ...]) -> float:
    """Completely reproducible, bounded logistic; no machine-learning runtime."""
    if len(factors) != len(WEIGHTS):
        raise ValueError("Wrong causal feature count")
    if any(not math.isfinite(x) for x in factors):
        raise ValueError("Nonfinite causal market feature")
    logit = INTERCEPT + sum(
        weight * ((value - mean) / scale)
        for value, mean, scale, weight in zip(factors, MEANS, SCALES, WEIGHTS)
    )
    return 1.0 / (1.0 + math.exp(-max(-36., min(36., logit))))


@dataclass(frozen=True)
class V12EntrySpec:
    first_leg_min_score: float = 0.80
    favorable_first_reentry_score: float = 0.78
    adverse_first_reentry_score: float = 0.76
    max_spread_u: int = 25
    allow_live_orders: bool = False
    allow_teacher_signal_injection: bool = False

    def __post_init__(self) -> None:
        if not all(0.0 < x < 1.0 for x in (
            self.first_leg_min_score, self.favorable_first_reentry_score,
            self.adverse_first_reentry_score
        )):
            raise ValueError("Invalid entry score thresholds")
        if self.allow_live_orders or self.allow_teacher_signal_injection:
            raise ValueError("Historical teacher labels and live orders are forbidden")
        if self.max_spread_u <= 0:
            raise ValueError("Invalid spread cap")


class Micro180V12QuantEntry(Micro180V11DualEntry):
    """Source-ordered dual-basket entry decisions independent of R9 entry gate.

    The first eligible quote of each observed second is evaluated. The
    5s/15s active basket values are current *as-of* observations. Only
    previously completed seconds enter the S1 direction/efficiency measures.
    Completed M5 ATR from as-of TickLogger metadata (if available) or
    rolling M5 input is a regime denominator, not a teacher future feature.
    """

    def __init__(self, *args: Any, v12: V12EntrySpec = V12EntrySpec(), **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.v12_spec = v12
        self._score_second: int | None = None
        self._flow_minute: int | None = None
        self._flow_previous_bid: int | None = None
        self._flow_up = 0
        self._flow_down = 0
        self.v12_counts: Counter[str] = Counter()

    def _push_second(self, t: Tick) -> None:
        minute = t.time_s // 60
        if minute != self._flow_minute:
            self._flow_minute = minute
            self._flow_up = self._flow_down = 0
        if self._flow_previous_bid is not None:
            if t.bid_u > self._flow_previous_bid:
                self._flow_up += 1
            elif t.bid_u < self._flow_previous_bid:
                self._flow_down += 1
        self._flow_previous_bid = t.bid_u
        super()._push_second(t)

    def _asof_completed_m5_atr_u(self, t: Tick) -> float | None:
        extras = t.source_extras or {}
        # The ORIGINAL REAL TickLogger records the tester's already-completed
        # iATR observation on each source tick. This does not require
        # intrasecond OHLC generation or opening the next source quote.
        source = extras.get("atr")
        if source not in (None, ""):
            try:
                atr = float(source) * 100.0
                if math.isfinite(atr) and atr > 0:
                    return atr
            except (ValueError, TypeError):
                pass
        if self.atr.ready and self.atr.atr_u is not None:
            return float(self.atr.atr_u)
        return None

    def _causal_factors(self, t: Tick, side: int, atr_u: float) -> tuple[float, ...]:
        if self._v11_minute_mid2 is None:
            raise ValueError("No independent source-minute anchor")
        mid = (t.ask_u + t.bid_u) * .5
        minute_open_mid = self._v11_minute_mid2 * .5
        min_move = mid - minute_open_mid
        five = self.rolling.current.get(5000)
        fifteen = self.rolling.current.get(15000)
        if five is None or fifteen is None:
            raise ValueError("Incomplete current source basket")
        impulse5 = (five.bid_close + five.ask_close - five.bid_open - five.ask_open) * .5
        impulse15 = (fifteen.bid_close + fifteen.ask_close
                     - fifteen.bid_open - fifteen.ask_open) * .5
        closes = list(self.rolling.finished[1000])[-10:]
        if len(closes) >= 10:
            closing_bids = [bar.bid_close for bar in closes]
            displacement = closing_bids[-1] - closing_bids[0]
            increments = [b-a for a,b in zip(closing_bids, closing_bids[1:])]
            travel = sum(abs(v) for v in increments)
            efficiency = abs(displacement) / (travel + .0001)
            amplitude = max(closing_bids) - min(closing_bids)
        else:
            displacement, efficiency, amplitude = 0., 0., 0.
        flow = (self._flow_up - self._flow_down) / max(
            1, self._flow_up + self._flow_down
        )
        quote = t.ask_u if side > 0 else t.bid_u
        envelope_excess = side * ((quote-mid) + min_move - 15*side)
        return (
            (t.time_s % 60) / 60.,
            float(t.time_s % 60 <= 5),
            side * min_move / 50.,
            side * impulse5 / 25.,
            side * impulse15 / 40.,
            side * displacement / 60.,
            efficiency,
            amplitude / 70.,
            side * flow,
            side * (quote-mid) / 25.,
            t.spread_points / 25.,
            atr_u / 400.,
            side * displacement / max(100., atr_u),
            side * impulse5 / max(60., .25 * atr_u),
            side * impulse15 / max(100., .4 * atr_u),
            max(-3., min(3., envelope_excess / 60.)),
            float(side * displacement > 0),
            float(side * impulse5 > 0),
            float(side * impulse15 > 0),
        )

    def _process_entries(self, t: Tick) -> None:
        if not self.pending_mode:
            return
        if t.time_s == self._score_second:
            return
        self._score_second = t.time_s
        if t.spread_points > self.v12_spec.max_spread_u:
            self.v12_counts["spread_rejected"] += 1
            return
        atr_u = self._asof_completed_m5_atr_u(t)
        if atr_u is None or atr_u < self._session_atr_min_u(t.time_s):
            self.v12_counts["asof_atr_regime_rejected"] += 1
            return
        decisions = []
        permitted = (1,-1) if self.pending_mode == 2 else (self.pending_mode,)
        for side in permitted:
            factors = self._causal_factors(t, side, atr_u)
            score = factor_probability(factors)
            # The rearm phase is observable only after first quote-side exit.
            # The B/C historic family label is never consulted.
            if self.rearms:
                prior = self._last_close
                if prior is None or prior["time_msc"] > t.time_msc:
                    continue
                first_was_favorable = prior["signed_quote_move_u"] > 0
                threshold = (
                    self.v12_spec.favorable_first_reentry_score
                    if first_was_favorable
                    else self.v12_spec.adverse_first_reentry_score
                )
            else:
                threshold = self.v12_spec.first_leg_min_score
            if score >= threshold:
                decisions.append((score, side, factors))
        if not decisions:
            self.v12_counts["score_below_entry_threshold"] += 1
            return
        # No hindsight: simultaneous BUY/SELL scores use only THIS quote.
        score, side, factors = max(decisions, key=lambda item: item[0])
        # Build the existing 5s/15s and S1 receipt at the decision quote;
        # this affects evidence only; it cannot invoke any R9 entry gate.
        self._v11_pending_receipt = {
            **self._basket_snapshot(t, side, 0),
            "factor_score": score,
            "factor_vector": tuple(round(v, 6) for v in factors),
            "factor_names": FACTOR_NAMES,
            "signal_mode": "independent_causal_dual_basket_quant",
        }
        try:
            before = len(self.entries)
            self._open_trade(t, side)
            if len(self.entries) > before:
                self.entries[-1]["v12_entry_authority"] = "independent_micro180_19_factor"
                self.entries[-1]["v12_entry_score"] = round(score, 9)
                self.entries[-1]["v12_executable_quote_u"] = (
                    t.ask_u if side > 0 else t.bid_u
                )
                self.v12_counts["autonomous_quant_entries"] += 1
        finally:
            self._v11_pending_receipt = None

    def concordance_summary(self) -> dict[str, Any]:
        result = super().concordance_summary()
        result.update({
            "entry_authority": "micro180_v12_independent_multiscale_factor_router",
            "uses_teacher_event_or_outcome_at_runtime": False,
            "asof_m5_atr_source": "original_ticklogger_if_present_else_completed_M5",
            "factor_count": len(FACTOR_NAMES),
            "native_mt5_orders_enabled": False,
            "training_scope": "2026-01-02_first_half_200k_quote_bounded_sample",
            "v12_counts": dict(self.v12_counts),
        })
        return result

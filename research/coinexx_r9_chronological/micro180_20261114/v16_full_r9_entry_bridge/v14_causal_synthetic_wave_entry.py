"""MICRO180 V14 entry-only research: causal inverse synthetic-wave opportunity engine.

Does NOT generate fake trade prices or infer finished current M1 OHLC, use R9
historical trade times/events at runtime, manage exits, or send MT5 orders.
Source inputs are chronological REAL Coinexx quote updates (integer cents), an
as-of COMPLETED M5 ATR, and an explicit independent flat/closed inventory state.

Offline prior: probability of a SECOND within the observed R9 historical
entry population, not the probability of an entry given *all* quote seconds.
The output is scored, next-observed-second, executable quote-side research
entry candidates; parameters are UNCALIBRATED and default to shadow mode.
"""
from __future__ import annotations

import json
import math
from collections import deque
from dataclasses import dataclass
from pathlib import Path


def _normal_cdf(z: float) -> float:
    return 0.5 * math.erfc(-z / math.sqrt(2.0))


def first_passage_probability(gap: float, signed_drift: float,
                              sigma_per_sqrt_second: float,
                              seconds_ahead: float) -> float:
    """Drifted Brownian *forecast* threshold-touch probability, no future data.

    gap / drift / sigma are price cents, cents/s, and cents/sqrt(s).
    The forecast is a hypothesis for real-quote accessibility, not a forecast
    of the actual MT5 generator's future constructed prices.
    """
    if gap <= 0:
        return 1.0
    if sigma_per_sqrt_second <= 0 or seconds_ahead <= 0:
        return 0.0
    scale = sigma_per_sqrt_second * math.sqrt(seconds_ahead)
    z1 = (signed_drift * seconds_ahead - gap) / scale
    z2 = (-signed_drift * seconds_ahead - gap) / scale
    exponent = min(700.0, 2.0 * signed_drift * gap / sigma_per_sqrt_second**2)
    answer = _normal_cdf(z1) + math.exp(exponent) * _normal_cdf(z2)
    return max(0.0, min(1.0, answer))


@dataclass(frozen=True)
class Quote:
    time_msc: int
    bid_cents: int
    ask_cents: int
    completed_m5_atr_cents: float | None = None
    session_m5_atr_floor_cents: float | None = None  # as-of R9 session floor

    @property
    def second(self) -> int:
        return self.time_msc // 1000

    @property
    def minute(self) -> int:
        return self.second // 60

    @property
    def mid(self) -> float:
        return 0.5 * (self.bid_cents + self.ask_cents)

    @property
    def spread(self) -> int:
        return self.ask_cents - self.bid_cents


@dataclass(frozen=True)
class EntryState:
    time_msc: int
    minute: int
    second_of_minute: int
    leg: int
    side: int
    teacher_clock_prior: float
    tick_volume_progress: float
    generator_phase_proxy: str
    signed_10s_cents: float
    signed_60s_cents: float
    signed_300s_cents: float
    signed_latent_velocity_cents_per_second: float
    signed_m1_momentum_cents: float
    minute_barrier_gap_cents: float
    prospective_barrier_touch_probability: float
    spread_cents: int
    completed_m5_atr_cents: float | None
    score: float


@dataclass(frozen=True)
class EntryIntent:
    time_msc: int
    origin_time_msc: int
    minute: int
    leg: int
    side: int
    price_cents: int  # BUY observed Ask, SELL observed Bid, NEVER synthetic.
    score: float


class _LocalLinearFilter:
    """Two-state Kalman filter with strictly forward observation updates."""
    def __init__(self) -> None:
        self.pos: float | None = None
        self.vel = 0.0
        self.p00 = 100.0
        self.p01 = 0.0
        self.p11 = 40.0
        self.last_s: int | None = None

    def update(self, sec: int, mid: float, spread: int, innovation_q: float) -> None:
        if self.last_s is None:
            self.pos = mid
            self.last_s = sec
            return
        d = sec - self.last_s
        if d <= 0:
            raise ValueError("Kalman filter updates only when a new second is observed")
        self.last_s = sec
        q = max(0.1, min(500.0, innovation_q))
        xp = self.pos + self.vel * d
        p00 = self.p00 + 2 * d * self.p01 + d * d * self.p11 + q * d**3 / 3
        p01 = self.p01 + d * self.p11 + q * d**2 / 2
        p11 = self.p11 + q * d
        r = max(4.0, (spread / 2.0) ** 2)
        innovation = mid - xp
        k0, k1 = p00 / (p00 + r), p01 / (p00 + r)
        self.pos = xp + k0 * innovation
        self.vel += k1 * innovation
        self.p00 = max(1e-6, (1 - k0) * p00)
        self.p01 = (1 - k0) * p01
        self.p11 = max(1e-6, p11 - k1 * p01)


class CausalSyntheticWaveEntry:
    """Ingest real quotes, emit research entry intent only on *later* real quote.

    Inventory changes MUST be acknowledged externally by notify_closed().
    Nothing in this class opens/closes/manages a brokerage position.
    """
    def __init__(self, clock_priors: dict, *, shadow: bool = True,
                 score_threshold: float = 0.65, max_spread_cents: int = 25,
                 max_quote_lag_ms: int = 2000, require_touch_gate: bool = True) -> None:
        self.priors = clock_priors
        for key in ("first", "second"):
            a = self.priors[key]
            if len(a) != 60 or any((v <= 0 or not math.isfinite(v)) for v in a):
                raise ValueError(f"Invalid {key} 60-second prior")
        self.shadow = shadow
        self.score_threshold = score_threshold
        self.max_spread_cents = max_spread_cents
        self.max_quote_lag_ms = max_quote_lag_ms
        self.require_touch_gate = require_touch_gate
        self.last_msc = -1
        self.last_sec: int | None = None
        self.last_mid = 0.0
        self.closed_seconds: deque[tuple[int, float]] = deque()
        self.current_minute: int | None = None
        self.minute_start_mid = 0.0
        self.minute_tick_count = 0
        self.prior_minute_counts: deque[int] = deque(maxlen=5)
        self.m1_open = self.m1_high = self.m1_low = self.m1_close = 0.0
        self.closed_m1: deque[tuple[float, float, float, float]] = deque(maxlen=5)
        self.filter = _LocalLinearFilter()
        self.first_done = False
        self.second_done = False
        self.own_position_side: int | None = None
        self.rearm_side: int | None = None
        self.pending: tuple[int, int, int, float, int] | None = None
        self.last_scored_sec: int | None = None
        self.states: list[EntryState] = []  # Small bounded research fixtures only.

    @classmethod
    def from_prior_file(cls, path: str | Path, **kwargs) -> "CausalSyntheticWaveEntry":
        return cls(json.loads(Path(path).read_text(encoding="utf-8"))["clock_prior"], **kwargs)

    def notify_closed(self, at_msc: int, side: int) -> None:
        """External own-inventory close; authorizes same-minute opposite leg."""
        if self.own_position_side != side or at_msc < self.last_msc:
            raise ValueError("Close must correspond to existing own position and observed quote clock")
        self.own_position_side = None
        self.rearm_side = -side if at_msc // 60000 == self.current_minute and self.first_done else None

    def _observed(self, sec: int, age: int) -> float | None:
        target = sec - age
        for t, x in reversed(self.closed_seconds):
            if t > target:
                continue
            return x if target - t <= 2 else None
        return None

    def _sigma(self) -> float:
        data = list(self.closed_seconds)[-61:]
        sq = [(data[i][1] - data[i - 1][1])**2 /
              max(1, data[i][0] - data[i - 1][0])
              for i in range(1, len(data))]
        return math.sqrt(max(1., sum(sq) / max(1, len(sq))))

    def _score(self, q: Quote, leg: int, side: int) -> EntryState:
        sec = q.second
        age = sec % 60
        mid = q.mid
        prior = self.priors["first" if leg == 1 else "second"][age]
        o10 = self._observed(sec, 10)
        o60 = self._observed(sec, 60)
        o300 = self._observed(sec, 300)
        z10 = side * (mid - (o10 if o10 is not None else mid))
        z60 = side * (mid - (o60 if o60 is not None else mid))
        z300 = side * (mid - (o300 if o300 is not None else mid))
        sigma = self._sigma()
        m1mom = (self.closed_m1[-1][3] - self.closed_m1[-2][3]
                 if len(self.closed_m1) >= 2 else 0.0)
        m1mom *= side
        barrier = self.minute_start_mid + side * 15
        gap = side * (barrier - (q.ask_cents if side == 1 else q.bid_cents))
        drift = side * self.filter.vel
        p_touch = first_passage_probability(gap, drift, sigma, max(1, 59-age))
        avg_tick_rate = (sum(self.prior_minute_counts) / (60 * len(self.prior_minute_counts))
                         if self.prior_minute_counts else 1.0)
        elapsed = age + 1
        post_rate = (20 * avg_tick_rate + self.minute_tick_count) / (20 + elapsed)
        projected_ticks = self.minute_tick_count + post_rate * max(0, 60-elapsed)
        progress = self.minute_tick_count / max(1.0, projected_ticks)
        # Tentative 3/5/3 *reference-point* phase; normalized quote tick count
        # is only a proxy, NOT claimed to equal generated reference-point time.
        phase = "opening_shadow" if progress < 3/11 else (
            "range_waves" if progress < 8/11 else "closing_shadow")
        # Hypothesis-based score (NOT fit or calibrated). Coefficients are
        # explicit to make the next quoted-tick comparison falsifiable.
        log_clock = math.log(max(1e-9, 60 * prior))
        model = (0.24 * math.tanh(z10 / max(15, 4*sigma))
                 + 0.20 * math.tanh(z60 / max(30, 8*sigma))
                 + 0.10 * math.tanh(z300 / max(60, 16*sigma))
                 + 0.12 * math.tanh(drift / max(2, sigma))
                 + 0.07 * math.tanh(m1mom / max(30, 8*sigma))
                 + 0.23 * (2*p_touch-1)
                 + 0.04 * math.tanh(log_clock))
        score = 1 / (1 + math.exp(-4 * model))
        return EntryState(q.time_msc,q.minute,age,leg,side,prior,progress,phase,
                          z10,z60,z300,drift,m1mom,gap,p_touch,q.spread,
                          q.completed_m5_atr_cents,score)

    def on_quote(self, q: Quote) -> list[EntryIntent]:
        if q.time_msc < self.last_msc:
            raise ValueError("Out-of-order quote; source ordinal order required")
        if q.bid_cents <= 0 or q.spread < 0:
            raise ValueError("Invalid source Bid/Ask")
        self.last_msc = q.time_msc
        sec = q.second
        if self.current_minute != q.minute:
            if self.current_minute is not None:
                self.prior_minute_counts.append(self.minute_tick_count)
                self.closed_m1.append((self.m1_open,self.m1_high,self.m1_low,self.m1_close))
            self.current_minute = q.minute
            self.minute_start_mid = q.mid
            self.minute_tick_count = 0
            self.m1_open=self.m1_high=self.m1_low=self.m1_close=q.mid
            self.first_done = False
            self.second_done = False
            self.rearm_side = None
            self.pending = None
        self.minute_tick_count += 1
        self.m1_high=max(self.m1_high,q.mid)
        self.m1_low=min(self.m1_low,q.mid)
        self.m1_close=q.mid
        new_sec = self.last_sec != sec
        if new_sec:
            if self.last_sec is not None:
                self.closed_seconds.append((self.last_sec,self.last_mid))
            while self.closed_seconds and self.closed_seconds[0][0] < sec-305:
                self.closed_seconds.popleft()
            self.filter.update(sec,q.mid,q.spread,self._sigma()**2)
        self.last_sec = sec
        self.last_mid = q.mid
        intents=[]
        # Pending decision is triggered only at the *first* observed quote
        # of a new second, with actual original Bid/Ask and no forced fill.
        if new_sec and self.pending is not None:
            decision_s,leg,side,score,orig_msc=self.pending
            if sec >= decision_s+1:
                self.pending=None
                delta=q.time_msc-(decision_s+1)*1000
                if (q.minute==decision_s//60 and
                    0 <= delta <= self.max_quote_lag_ms and
                    q.spread<=self.max_spread_cents and
                    self.own_position_side is None and
                    ((leg==1 and not self.first_done) or
                     (leg==2 and self.first_done and not self.second_done
                      and self.rearm_side==side))):
                    intent=EntryIntent(q.time_msc,orig_msc,q.minute,leg,side,
                                       q.ask_cents if side==1 else q.bid_cents,score)
                    intents.append(intent)
                    # Research inventory state must be confirmed by external
                    # source-path simulator before an opposite leg can arm.
                    self.own_position_side=side
                    if leg==1:self.first_done=True
                    else:
                        self.second_done=True
                        self.rearm_side=None
        if not new_sec or self.last_scored_sec==sec:
            return intents
        self.last_scored_sec=sec
        if self.own_position_side is not None or self.pending is not None:
            return intents
        if q.spread>self.max_spread_cents:
            return intents
        if (q.completed_m5_atr_cents is None or
            q.session_m5_atr_floor_cents is None or
            q.completed_m5_atr_cents < q.session_m5_atr_floor_cents):
            return intents
        leg=1 if not self.first_done else 2 if self.rearm_side is not None and not self.second_done else 0
        if leg == 0:
            return intents
        allowed=(1,-1) if leg==1 else (self.rearm_side,)
        candidates=[self._score(q,leg,s) for s in allowed]
        if self.shadow and len(self.states) < 10000:
            self.states.extend(candidates[:max(0, 10000-len(self.states))])
        best=max(candidates,key=lambda x:x.score)
        if best.score>=self.score_threshold and (not self.require_touch_gate or best.prospective_barrier_touch_probability>=0.5):
            self.pending=(sec,leg,best.side,best.score,q.time_msc)
        return intents

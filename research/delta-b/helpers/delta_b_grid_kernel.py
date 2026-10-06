from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
from statistics import median
from typing import Deque, Iterable, Mapping, Sequence
from zoneinfo import ZoneInfo


class Importance(str, Enum):
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class EventPhase(str, Enum):
    NORMAL = "NORMAL"
    PRE_MEDIUM = "PRE_MEDIUM"
    PRE_HIGH = "PRE_HIGH"
    RELEASE_MEDIUM = "RELEASE_MEDIUM"
    RELEASE_HIGH = "RELEASE_HIGH"
    DISCOVERY_MEDIUM = "DISCOVERY_MEDIUM"
    DISCOVERY_HIGH = "DISCOVERY_HIGH"
    STABILIZATION_MEDIUM = "STABILIZATION_MEDIUM"
    STABILIZATION_HIGH = "STABILIZATION_HIGH"


class Session(str, Enum):
    ASIA = "ASIA"
    LONDON_OPEN = "LONDON_OPEN_TRANSITION"
    LONDON = "LONDON"
    OVERLAP = "LONDON_NY_OVERLAP"
    NEW_YORK = "NEW_YORK"
    ROLLOVER = "ROLLOVER_OFFSESSION"


class GridState(str, Enum):
    TRANSIT = "TRANSIT"
    ROTATION = "ROTATION"
    ESCAPE = "ESCAPE"
    RECLAIM = "FAILED_ESCAPE_RECLAIM"
    CHURN_SHOCK = "CHURN_SHOCK"


@dataclass(frozen=True)
class CalendarEvent:
    time_utc: datetime
    importance: Importance
    currency: str = "USD"
    name: str = ""
    event_id: str = ""

    def __post_init__(self) -> None:
        if self.time_utc.tzinfo is None:
            raise ValueError("time_utc must be timezone-aware")


@dataclass(frozen=True)
class EventWindow:
    pre_min: int
    release_min: int
    discovery_min: int
    stabilization_min: int


@dataclass(frozen=True)
class ContextAdjustment:
    q_mult: float = 1.0
    hysteresis_mult: float = 1.0
    confirmation_mult: float = 1.0
    cost_buffer_mult: float = 1.0
    entry_authority: float = 1.0

    def combine(self, other: "ContextAdjustment") -> "ContextAdjustment":
        return ContextAdjustment(
            self.q_mult * other.q_mult,
            self.hysteresis_mult * other.hysteresis_mult,
            self.confirmation_mult * other.confirmation_mult,
            self.cost_buffer_mult * other.cost_buffer_mult,
            min(self.entry_authority, other.entry_authority),
        )


DEFAULT_EVENT_ADJUSTMENTS: Mapping[EventPhase, ContextAdjustment] = {
    EventPhase.NORMAL: ContextAdjustment(),
    EventPhase.PRE_MEDIUM: ContextAdjustment(1.10, 1.10, 1.05, 1.10, 0.80),
    EventPhase.PRE_HIGH: ContextAdjustment(1.20, 1.20, 1.10, 1.20, 0.60),
    EventPhase.RELEASE_MEDIUM: ContextAdjustment(1.40, 1.30, 1.15, 1.30, 0.45),
    EventPhase.RELEASE_HIGH: ContextAdjustment(1.80, 1.60, 1.30, 1.50, 0.20),
    EventPhase.DISCOVERY_MEDIUM: ContextAdjustment(1.25, 1.15, 1.05, 1.20, 0.60),
    EventPhase.DISCOVERY_HIGH: ContextAdjustment(1.45, 1.30, 1.15, 1.35, 0.40),
    EventPhase.STABILIZATION_MEDIUM: ContextAdjustment(1.08, 1.05, 1.00, 1.05, 0.85),
    EventPhase.STABILIZATION_HIGH: ContextAdjustment(1.15, 1.10, 1.05, 1.10, 0.75),
}


@dataclass(frozen=True)
class GridConfig:
    q_floor: float = 0.01
    q_ceiling: float = 50.0
    cost_mult: float = 1.35
    noise_mult: float = 6.0
    noise_window: int = 128
    path_window: int = 64
    spread_window: int = 256
    interval_window: int = 128
    shock_quantile: float = 0.95
    shock_min_components: int = 2
    scales: tuple[float, ...] = (1.0, 2.0, 4.0, 8.0)
    medium_window: EventWindow = EventWindow(20, 5, 20, 45)
    high_window: EventWindow = EventWindow(45, 10, 30, 60)
    event_adjustments: Mapping[EventPhase, ContextAdjustment] = field(
        default_factory=lambda: DEFAULT_EVENT_ADJUSTMENTS
    )
    session_adjustments: Mapping[Session, ContextAdjustment] = field(
        default_factory=lambda: {s: ContextAdjustment() for s in Session}
    )

    def __post_init__(self) -> None:
        if self.q_floor <= 0 or self.q_ceiling <= self.q_floor:
            raise ValueError("invalid Q clamps")
        if self.cost_mult <= 0 or self.noise_mult <= 0:
            raise ValueError("multipliers must be positive")
        if min(self.noise_window, self.path_window, self.spread_window, self.interval_window) < 8:
            raise ValueError("rolling windows must be >= 8")
        if not 0.5 < self.shock_quantile < 1.0:
            raise ValueError("shock_quantile must be in (0.5, 1)")


def _quantile(values: Sequence[float], p: float) -> float:
    if not values:
        return 0.0
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * p
    lo = int(pos)
    hi = min(lo + 1, len(xs) - 1)
    f = pos - lo
    return xs[lo] * (1 - f) + xs[hi] * f


def classify_session(ts_utc: datetime) -> Session:
    if ts_utc.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    u = ts_utc.astimezone(timezone.utc)
    lon = u.astimezone(ZoneInfo("Europe/London"))
    ny = u.astimezone(ZoneInfo("America/New_York"))
    tokyo = u.astimezone(ZoneInfo("Asia/Tokyo"))
    lon_m = lon.hour * 60 + lon.minute
    ny_m = ny.hour * 60 + ny.minute
    tokyo_m = tokyo.hour * 60 + tokyo.minute

    if 16 * 60 + 50 <= ny_m < 17 * 60 + 20:
        return Session.ROLLOVER
    london_active = 8 * 60 <= lon_m < 16 * 60 + 30
    ny_active = 8 * 60 <= ny_m < 17 * 60
    if london_active and ny_active:
        return Session.OVERLAP
    if 7 * 60 <= lon_m < 8 * 60:
        return Session.LONDON_OPEN
    if london_active:
        return Session.LONDON
    if ny_active:
        return Session.NEW_YORK
    if 8 * 60 <= tokyo_m < 16 * 60:
        return Session.ASIA
    return Session.ROLLOVER


def classify_event_phase(
    ts_utc: datetime,
    events: Iterable[CalendarEvent],
    cfg: GridConfig,
    currencies: frozenset[str] = frozenset({"USD"}),
) -> EventPhase:
    if ts_utc.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    now = ts_utc.astimezone(timezone.utc)
    rank = {
        EventPhase.NORMAL: 0,
        EventPhase.STABILIZATION_MEDIUM: 1,
        EventPhase.PRE_MEDIUM: 2,
        EventPhase.DISCOVERY_MEDIUM: 3,
        EventPhase.RELEASE_MEDIUM: 4,
        EventPhase.STABILIZATION_HIGH: 5,
        EventPhase.PRE_HIGH: 6,
        EventPhase.DISCOVERY_HIGH: 7,
        EventPhase.RELEASE_HIGH: 8,
    }
    best = EventPhase.NORMAL
    for event in events:
        if event.currency.upper() not in currencies:
            continue
        window = cfg.high_window if event.importance is Importance.HIGH else cfg.medium_window
        delta_min = (now - event.time_utc.astimezone(timezone.utc)).total_seconds() / 60.0
        phase = EventPhase.NORMAL
        if -window.pre_min <= delta_min < 0:
            phase = EventPhase.PRE_HIGH if event.importance is Importance.HIGH else EventPhase.PRE_MEDIUM
        elif 0 <= delta_min < window.release_min:
            phase = EventPhase.RELEASE_HIGH if event.importance is Importance.HIGH else EventPhase.RELEASE_MEDIUM
        elif window.release_min <= delta_min < window.release_min + window.discovery_min:
            phase = EventPhase.DISCOVERY_HIGH if event.importance is Importance.HIGH else EventPhase.DISCOVERY_MEDIUM
        elif window.release_min + window.discovery_min <= delta_min < window.release_min + window.discovery_min + window.stabilization_min:
            phase = EventPhase.STABILIZATION_HIGH if event.importance is Importance.HIGH else EventPhase.STABILIZATION_MEDIUM
        if rank[phase] > rank[best]:
            best = phase
    return best


@dataclass(frozen=True)
class QSnapshot:
    q_base: float
    q_context: float
    friction: float
    noise: float
    path_noise_ratio: float
    spread_percentile: float
    shock_score: int
    shock_active: bool
    session: Session
    event_phase: EventPhase
    adjustment: ContextAdjustment


class AdaptiveQEstimator:
    def __init__(self, cfg: GridConfig) -> None:
        self.cfg = cfg
        self.last_mid: float | None = None
        self.last_ts: datetime | None = None
        self.abs_moves: Deque[float] = deque(maxlen=cfg.noise_window)
        self.mids: Deque[float] = deque(maxlen=cfg.path_window)
        self.spreads: Deque[float] = deque(maxlen=cfg.spread_window)
        self.intervals: Deque[float] = deque(maxlen=cfg.interval_window)

    def update(
        self,
        *,
        ts_utc: datetime,
        bid: float,
        ask: float,
        commission_equiv: float = 0.0,
        slippage_buffer: float = 0.0,
        session: Session | None = None,
        event_phase: EventPhase = EventPhase.NORMAL,
    ) -> QSnapshot:
        if ts_utc.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        if not all(isfinite(x) and x >= 0 for x in (bid, ask, commission_equiv, slippage_buffer)):
            raise ValueError("prices/costs must be finite and nonnegative")
        if ask < bid:
            raise ValueError("ask must be >= bid")

        mid = (bid + ask) / 2.0
        spread = ask - bid
        self.spreads.append(spread)
        self.mids.append(mid)
        if self.last_mid is not None:
            self.abs_moves.append(abs(mid - self.last_mid))
        if self.last_ts is not None:
            dt = (ts_utc.astimezone(timezone.utc) - self.last_ts).total_seconds()
            if dt >= 0:
                self.intervals.append(dt)

        noise = median(self.abs_moves) if self.abs_moves else 0.0
        mids = list(self.mids)
        if len(mids) > 1:
            gross = sum(abs(b - a) for a, b in zip(mids, mids[1:]))
            net = abs(mids[-1] - mids[0])
            path_noise = gross / max(net, self.cfg.q_floor)
        else:
            path_noise = 1.0

        friction = spread + commission_equiv + slippage_buffer
        churn_amp = min(max(path_noise - 1.0, 0.0), 6.0)
        q_noise = self.cfg.noise_mult * noise * (1.0 + 0.15 * churn_amp)
        q_base = min(
            self.cfg.q_ceiling,
            max(self.cfg.q_floor, self.cfg.cost_mult * friction, q_noise),
        )

        spreads = list(self.spreads)
        moves = list(self.abs_moves)
        intervals = list(self.intervals)
        spread_cut = _quantile(spreads[:-1], self.cfg.shock_quantile) if len(spreads) > 16 else float("inf")
        move_cut = _quantile(moves[:-1], self.cfg.shock_quantile) if len(moves) > 16 else float("inf")
        old_intervals = [x for x in intervals[:-1] if x > 0]
        fast_cut = _quantile(old_intervals, 1.0 - self.cfg.shock_quantile) if len(old_intervals) > 16 else 0.0

        shock_score = 0
        if spread > spread_cut:
            shock_score += 1
        if moves and moves[-1] > move_cut:
            shock_score += 1
        if intervals and fast_cut > 0 and 0 < intervals[-1] < fast_cut:
            shock_score += 1
        if path_noise >= 4.0:
            shock_score += 1
        shock_active = shock_score >= self.cfg.shock_min_components

        session = session or classify_session(ts_utc)
        adj = self.cfg.session_adjustments[session].combine(self.cfg.event_adjustments[event_phase])
        if shock_active:
            adj = adj.combine(ContextAdjustment(1.35, 1.30, 1.15, 1.25, 0.50))

        q_context = min(self.cfg.q_ceiling, max(self.cfg.q_floor, q_base * adj.q_mult))
        spread_pct = sum(x <= spread for x in spreads) / len(spreads)

        self.last_mid = mid
        self.last_ts = ts_utc.astimezone(timezone.utc)
        return QSnapshot(
            q_base,
            q_context,
            friction,
            noise,
            path_noise,
            spread_pct,
            shock_score,
            shock_active,
            session,
            event_phase,
            adj,
        )


@dataclass(frozen=True)
class DirectionalChangeEvent:
    scale: float
    direction: int
    time_utc: datetime
    price: float
    threshold: float
    previous_extreme: float
    overshoot: float


class DirectionalChangeTracker:
    """Dynamic-Q tracker: threshold may widen mid-leg but cannot shrink mid-leg."""

    def __init__(self, scale: float) -> None:
        if scale <= 0:
            raise ValueError("scale must be positive")
        self.scale = scale
        self.direction = 0
        self.anchor: float | None = None
        self.high: float | None = None
        self.low: float | None = None
        self.confirm_price: float | None = None
        self.active_threshold: float | None = None

    def update(self, ts: datetime, mid: float, q: float) -> DirectionalChangeEvent | None:
        th_now = self.scale * q
        if self.anchor is None:
            self.anchor = self.high = self.low = mid
            self.active_threshold = th_now
            return None

        assert self.high is not None and self.low is not None and self.active_threshold is not None
        self.active_threshold = max(self.active_threshold, th_now)

        if self.direction == 0:
            self.high = max(self.high, mid)
            self.low = min(self.low, mid)
            if mid >= self.anchor + self.active_threshold:
                old = self.anchor
                self.direction = 1
                self.confirm_price = self.high = self.low = mid
                self.active_threshold = th_now
                return DirectionalChangeEvent(self.scale, 1, ts, mid, th_now, old, 0.0)
            if mid <= self.anchor - self.active_threshold:
                old = self.anchor
                self.direction = -1
                self.confirm_price = self.high = self.low = mid
                self.active_threshold = th_now
                return DirectionalChangeEvent(self.scale, -1, ts, mid, th_now, old, 0.0)
            return None

        if self.direction > 0:
            self.high = max(self.high, mid)
            if mid <= self.high - self.active_threshold:
                extreme = self.high
                overshoot = max(0.0, extreme - (self.confirm_price or extreme))
                self.direction = -1
                self.confirm_price = self.high = self.low = mid
                self.active_threshold = th_now
                return DirectionalChangeEvent(self.scale, -1, ts, mid, th_now, extreme, overshoot)
            return None

        self.low = min(self.low, mid)
        if mid >= self.low + self.active_threshold:
            extreme = self.low
            overshoot = max(0.0, (self.confirm_price or extreme) - extreme)
            self.direction = 1
            self.confirm_price = self.high = self.low = mid
            self.active_threshold = th_now
            return DirectionalChangeEvent(self.scale, 1, ts, mid, th_now, extreme, overshoot)
        return None


@dataclass(frozen=True)
class GridSnapshot:
    q: QSnapshot
    directions: tuple[int, ...]
    coherence: float
    state: GridState
    events: tuple[DirectionalChangeEvent, ...]


class IntrinsicGridKernel:
    """Research-only state engine. It deliberately has no order-placement interface."""

    def __init__(self, cfg: GridConfig | None = None) -> None:
        self.cfg = cfg or GridConfig()
        self.q = AdaptiveQEstimator(self.cfg)
        self.trackers = [DirectionalChangeTracker(s) for s in self.cfg.scales]

    def update(
        self,
        *,
        ts_utc: datetime,
        bid: float,
        ask: float,
        events: Iterable[CalendarEvent] = (),
        commission_equiv: float = 0.0,
        slippage_buffer: float = 0.0,
    ) -> GridSnapshot:
        session = classify_session(ts_utc)
        phase = classify_event_phase(ts_utc, events, self.cfg)
        qs = self.q.update(
            ts_utc=ts_utc,
            bid=bid,
            ask=ask,
            commission_equiv=commission_equiv,
            slippage_buffer=slippage_buffer,
            session=session,
            event_phase=phase,
        )
        mid = (bid + ask) / 2.0
        pre_dirs = tuple(t.direction for t in self.trackers)
        new_events = []
        for tracker in self.trackers:
            ev = tracker.update(ts_utc, mid, qs.q_context)
            if ev is not None:
                new_events.append(ev)

        dirs = tuple(t.direction for t in self.trackers)
        active = [d for d in dirs if d]
        coherence = abs(sum(active)) / len(active) if active else 0.0

        # RECLAIM is a transition, not a persistent disagreement state.
        l0_event = next((e for e in new_events if e.scale == self.cfg.scales[0]), None)
        higher_pre = [d for d in pre_dirs[1:] if d]
        higher_sign = 0
        if higher_pre:
            signed = sum(higher_pre)
            higher_sign = 1 if signed > 0 else -1 if signed < 0 else 0

        if qs.shock_active:
            state = GridState.CHURN_SHOCK
        elif (
            l0_event is not None
            and pre_dirs[0] != 0
            and l0_event.direction == -pre_dirs[0]
            and higher_sign != 0
        ):
            state = GridState.RECLAIM
        elif new_events and len(active) >= 3 and coherence >= 0.75:
            state = GridState.ESCAPE
        elif len(active) >= 3 and coherence >= 0.75:
            state = GridState.TRANSIT
        else:
            state = GridState.ROTATION

        return GridSnapshot(qs, dirs, coherence, state, tuple(new_events))

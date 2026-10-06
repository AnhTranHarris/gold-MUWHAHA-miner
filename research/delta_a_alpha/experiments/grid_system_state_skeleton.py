from __future__ import annotations

"""Delta-A-alpha BUILD-01: neutral whole-grid state/lifecycle skeleton.

Architecture only. This module does not create orders, generate alpha, change
lot size, or authorize risk. It provides deterministic state, finite lifecycle,
event genealogy, specialist-routing payloads, and category-ledger hooks.
"""

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
import hashlib
import json
from typing import Any

SYMBOL = "XAUUSD"
FIXED_LOT = 0.01


class SessionState(str, Enum):
    UNKNOWN = "UNKNOWN"
    ASIA = "ASIA"
    LONDON_OPEN = "LONDON_OPEN"
    LONDON = "LONDON"
    OVERLAP = "OVERLAP"
    NEW_YORK = "NEW_YORK"
    LATE_NY = "LATE_NY"
    ROLLOVER = "ROLLOVER"


class RegimeState(str, Enum):
    UNKNOWN = "UNKNOWN"
    RANGE_QUIET = "RANGE_QUIET"
    RANGE_ACTIVE = "RANGE_ACTIVE"
    TREND_QUIET = "TREND_QUIET"
    TREND_VOLATILE = "TREND_VOLATILE"
    TRANSITION = "TRANSITION"
    EVENT_SHOCK = "EVENT_SHOCK"
    TOXIC = "TOXIC"


class TimeframeRole(str, Enum):
    ENVIRONMENT = "ENVIRONMENT"
    STRUCTURE = "STRUCTURE"
    OPPORTUNITY = "OPPORTUNITY"
    EXECUTION = "EXECUTION"


class StructureState(str, Enum):
    UNKNOWN = "UNKNOWN"
    INTERIOR = "INTERIOR"
    PRIOR_DAY_HIGH = "PRIOR_DAY_HIGH"
    PRIOR_DAY_LOW = "PRIOR_DAY_LOW"
    PRIOR_SESSION_HIGH = "PRIOR_SESSION_HIGH"
    PRIOR_SESSION_LOW = "PRIOR_SESSION_LOW"
    SWING_HIGH = "SWING_HIGH"
    SWING_LOW = "SWING_LOW"
    BOS_UP = "BOS_UP"
    BOS_DOWN = "BOS_DOWN"
    CHOCH_UP = "CHOCH_UP"
    CHOCH_DOWN = "CHOCH_DOWN"
    SWEEP_HIGH = "SWEEP_HIGH"
    SWEEP_LOW = "SWEEP_LOW"
    RECLAIM_HIGH = "RECLAIM_HIGH"
    RECLAIM_LOW = "RECLAIM_LOW"


class TrendPhase(str, Enum):
    UNKNOWN = "UNKNOWN"
    UP_IMPULSE = "UP_IMPULSE"
    DOWN_IMPULSE = "DOWN_IMPULSE"
    UP_PULLBACK = "UP_PULLBACK"
    DOWN_PULLBACK = "DOWN_PULLBACK"
    RANGE = "RANGE"
    EXHAUSTION = "EXHAUSTION"
    TRANSITION = "TRANSITION"


class NewsState(str, Enum):
    NORMAL = "NORMAL"
    PRE_EVENT = "PRE_EVENT"
    RELEASE_WINDOW = "RELEASE_WINDOW"
    POST_EVENT_SHOCK = "POST_EVENT_SHOCK"
    POST_EVENT_DISCOVERY = "POST_EVENT_DISCOVERY"
    NORMALIZED = "NORMALIZED"


class RiskState(str, Enum):
    OBSERVE_ONLY = "OBSERVE_ONLY"
    OPEN_NEW_RISK = "OPEN_NEW_RISK"
    HOLD_EXISTING = "HOLD_EXISTING"
    REDUCE_ONLY = "REDUCE_ONLY"
    EXIT = "EXIT"
    HALT = "HALT"


class DirectionHypothesis(str, Enum):
    UNCLASSIFIED = "UNCLASSIFIED"
    LONG = "LONG"
    SHORT = "SHORT"
    ABSTAIN = "ABSTAIN"


class EventInterpretation(str, Enum):
    UNCLASSIFIED = "UNCLASSIFIED"
    MEAN_REVERSION = "MEAN_REVERSION"
    CONTINUATION = "CONTINUATION"
    OBSERVE = "OBSERVE"


class RecoveryState(str, Enum):
    NONE = "NONE"
    DEGRADED = "DEGRADED"
    WAIT = "WAIT"
    RECLASSIFY = "RECLASSIFY"
    RETIRED = "RETIRED"


class CrossingDirection(str, Enum):
    UNKNOWN = "UNKNOWN"
    UP = "UP"
    DOWN = "DOWN"


class CycleStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    RESTARTED = "RESTARTED"
    CLOSED = "CLOSED"


@dataclass(frozen=True)
class TimeframeState:
    timeframe: str
    role: TimeframeRole
    state: str = "UNKNOWN"
    updated_ms: int | None = None


@dataclass
class GeometryState:
    parent_anchor_raw: int | None = None
    child_gap_raw: int | None = None
    min_gap_raw: int | None = None
    max_gap_raw: int | None = None
    long_asymmetry: float = 1.0
    short_asymmetry: float = 1.0
    center_raw: int | None = None
    last_update_ms: int | None = None
    reason: str = "NEUTRAL"


@dataclass
class FrictionState:
    spread_raw: int | None = None
    commission_entry_usd: float = 0.01
    commission_exit_usd: float = 0.01
    slippage_raw: int = 0
    estimated_roundtrip_usd: float | None = None


@dataclass
class ContextSnapshot:
    timestamp_ms: int
    session: SessionState = SessionState.UNKNOWN
    regime: RegimeState = RegimeState.UNKNOWN
    structure: StructureState = StructureState.UNKNOWN
    trend_phase: TrendPhase = TrendPhase.UNKNOWN
    news_state: NewsState = NewsState.NORMAL
    timeframe_states: tuple[TimeframeState, ...] = field(default_factory=tuple)


@dataclass
class SpecialistRoute:
    event_id: str
    primary_direction: DirectionHypothesis = DirectionHypothesis.UNCLASSIFIED
    alternative_direction: DirectionHypothesis = DirectionHypothesis.ABSTAIN
    interpretation: EventInterpretation = EventInterpretation.UNCLASSIFIED
    horizon_ms: int | None = None
    risk_state: RiskState = RiskState.OBSERVE_ONLY
    recovery_state: RecoveryState = RecoveryState.NONE


@dataclass
class GridEvent:
    event_id: str
    cycle_id: str
    sequence: int
    birth_ms: int
    last_update_ms: int
    parent_cell: str = "UNKNOWN"
    child_cell: str = "UNKNOWN"
    crossing_direction: CrossingDirection = CrossingDirection.UNKNOWN
    recross_count: int = 0
    penetration_raw: int = 0
    physical_owner: bool = False
    rearm_eligible: bool = False
    expired: bool = False
    context_at_birth: ContextSnapshot | None = None
    route: SpecialistRoute | None = None

    def touch(self, now_ms: int) -> None:
        _require_monotonic(self.last_update_ms, now_ms, "event")
        self.last_update_ms = now_ms

    def recross(self, now_ms: int, penetration_raw: int = 0) -> None:
        self.touch(now_ms)
        self.recross_count += 1
        self.penetration_raw = int(penetration_raw)

    def expire(self, now_ms: int) -> None:
        self.touch(now_ms)
        self.expired = True
        self.rearm_eligible = False


@dataclass
class GridCycle:
    cycle_id: str
    generation: int
    start_ms: int
    last_update_ms: int
    status: CycleStatus = CycleStatus.ACTIVE
    restart_reason: str = "INITIAL"
    event_sequence: int = 0

    def touch(self, now_ms: int) -> None:
        _require_monotonic(self.last_update_ms, now_ms, "cycle")
        self.last_update_ms = now_ms


@dataclass
class LedgerCell:
    events: int = 0
    trades: int = 0
    net_profit: float = 0.0
    gross_profit: float = 0.0
    gross_loss: float = 0.0


@dataclass
class CategoryLedger:
    cells: dict[str, LedgerCell] = field(default_factory=dict)

    def _key(self, dimension: str, value: str) -> str:
        return f"{dimension}={value}"

    def record_event(self, context: ContextSnapshot) -> None:
        for dimension, value in _category_pairs(context):
            cell = self.cells.setdefault(self._key(dimension, value), LedgerCell())
            cell.events += 1

    def record_trade(self, context: ContextSnapshot, pnl: float) -> None:
        for dimension, value in _category_pairs(context):
            cell = self.cells.setdefault(self._key(dimension, value), LedgerCell())
            cell.trades += 1
            cell.net_profit += float(pnl)
            if pnl > 0:
                cell.gross_profit += float(pnl)
            elif pnl < 0:
                cell.gross_loss += float(pnl)


@dataclass
class GridSystemState:
    """Neutral sidecar state.

    No method in this class emits an order or computes an alpha decision.
    Future BUILD units may populate states around this contract.
    """

    start_ms: int
    symbol: str = SYMBOL
    lot_size: float = FIXED_LOT
    session: SessionState = SessionState.UNKNOWN
    regime: RegimeState = RegimeState.UNKNOWN
    structure: StructureState = StructureState.UNKNOWN
    trend_phase: TrendPhase = TrendPhase.UNKNOWN
    news_state: NewsState = NewsState.NORMAL
    risk_state: RiskState = RiskState.OBSERVE_ONLY
    geometry: GeometryState = field(default_factory=GeometryState)
    friction: FrictionState = field(default_factory=FrictionState)
    timeframe_states: dict[str, TimeframeState] = field(default_factory=dict)
    events: dict[str, GridEvent] = field(default_factory=dict)
    closed_cycle_ids: list[str] = field(default_factory=list)
    ledger: CategoryLedger = field(default_factory=CategoryLedger)
    cycle: GridCycle = field(init=False)

    def __post_init__(self) -> None:
        if self.symbol != SYMBOL:
            raise ValueError(f"BUILD-01 is XAUUSD only, got {self.symbol}")
        if abs(self.lot_size - FIXED_LOT) > 1e-12:
            raise ValueError(f"lot_size must remain {FIXED_LOT}")
        self.timeframe_states = _default_timeframe_states()
        self.cycle = _new_cycle(self.symbol, generation=0, start_ms=self.start_ms, reason="INITIAL")

    def context(self, timestamp_ms: int) -> ContextSnapshot:
        _require_monotonic(self.cycle.last_update_ms, timestamp_ms, "system")
        ordered = tuple(self.timeframe_states[k] for k in sorted(self.timeframe_states))
        return ContextSnapshot(
            timestamp_ms=timestamp_ms,
            session=self.session,
            regime=self.regime,
            structure=self.structure,
            trend_phase=self.trend_phase,
            news_state=self.news_state,
            timeframe_states=ordered,
        )

    def update_timeframe_state(
        self, timeframe: str, state: str, now_ms: int
    ) -> None:
        if timeframe not in self.timeframe_states:
            raise KeyError(f"unregistered timeframe role: {timeframe}")
        self.cycle.touch(now_ms)
        old = self.timeframe_states[timeframe]
        self.timeframe_states[timeframe] = TimeframeState(
            timeframe=timeframe,
            role=old.role,
            state=str(state),
            updated_ms=now_ms,
        )

    def new_event(
        self,
        now_ms: int,
        parent_cell: str = "UNKNOWN",
        child_cell: str = "UNKNOWN",
        crossing_direction: CrossingDirection = CrossingDirection.UNKNOWN,
        penetration_raw: int = 0,
    ) -> GridEvent:
        self.cycle.touch(now_ms)
        self.cycle.event_sequence += 1
        seq = self.cycle.event_sequence
        event_id = _event_id(
            self.cycle.cycle_id, seq, now_ms, parent_cell, child_cell, crossing_direction.value
        )
        if event_id in self.events:
            raise RuntimeError("deterministic event ID collision")
        context = self.context(now_ms)
        route = SpecialistRoute(event_id=event_id)
        event = GridEvent(
            event_id=event_id,
            cycle_id=self.cycle.cycle_id,
            sequence=seq,
            birth_ms=now_ms,
            last_update_ms=now_ms,
            parent_cell=str(parent_cell),
            child_cell=str(child_cell),
            crossing_direction=crossing_direction,
            penetration_raw=int(penetration_raw),
            context_at_birth=context,
            route=route,
        )
        self.events[event_id] = event
        self.ledger.record_event(context)
        return event

    def expire_events(self, now_ms: int, max_age_ms: int) -> list[str]:
        if max_age_ms < 0:
            raise ValueError("max_age_ms must be >= 0")
        self.cycle.touch(now_ms)
        expired: list[str] = []
        for event_id, event in self.events.items():
            if not event.expired and now_ms - event.birth_ms >= max_age_ms:
                event.expire(now_ms)
                expired.append(event_id)
        return expired

    def restart_cycle(self, now_ms: int, reason: str) -> tuple[str, str]:
        if not reason or reason == "INITIAL":
            raise ValueError("restart requires an explicit non-INITIAL reason")
        self.cycle.touch(now_ms)
        old_id = self.cycle.cycle_id
        self.cycle.status = CycleStatus.RESTARTED
        self.cycle.restart_reason = str(reason)
        self.closed_cycle_ids.append(old_id)
        for event in self.events.values():
            if event.cycle_id == old_id and not event.expired:
                event.expire(now_ms)
        generation = self.cycle.generation + 1
        self.cycle = _new_cycle(self.symbol, generation, now_ms, str(reason))
        return old_id, self.cycle.cycle_id

    def routing_payload(self, event_id: str) -> dict[str, Any]:
        event = self.events[event_id]
        if event.route is None or event.context_at_birth is None:
            raise RuntimeError("event route/context missing")
        payload = {
            "event_id": event.event_id,
            "cycle_id": event.cycle_id,
            "session": self.session.value,
            "regime": self.regime.value,
            "structure": self.structure.value,
            "trend_phase": self.trend_phase.value,
            "news_state": self.news_state.value,
            "geometry": _jsonable(self.geometry),
            "primary_direction": event.route.primary_direction.value,
            "alternative_direction": event.route.alternative_direction.value,
            "interpretation": event.route.interpretation.value,
            "horizon_ms": event.route.horizon_ms,
            "friction": _jsonable(self.friction),
            "risk_state": self.risk_state.value,
            "recovery_state": event.route.recovery_state.value,
            "lot_size": self.lot_size,
        }
        return payload

    def record_external_trade_result(
        self, event_id: str, pnl: float, context: ContextSnapshot | None = None
    ) -> None:
        """Ledger hook only. Does not create/modify a trade."""
        event = self.events[event_id]
        ctx = context or event.context_at_birth
        if ctx is None:
            raise RuntimeError("missing context")
        self.ledger.record_trade(ctx, pnl)

    def to_dict(self) -> dict[str, Any]:
        return _jsonable(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))


def _default_timeframe_states() -> dict[str, TimeframeState]:
    roles = {
        "D1": TimeframeRole.ENVIRONMENT,
        "H4": TimeframeRole.ENVIRONMENT,
        "H1": TimeframeRole.STRUCTURE,
        "M15": TimeframeRole.STRUCTURE,
        "M5": TimeframeRole.OPPORTUNITY,
        "M1": TimeframeRole.OPPORTUNITY,
        "TICK": TimeframeRole.EXECUTION,
    }
    return {tf: TimeframeState(tf, role) for tf, role in roles.items()}


def _new_cycle(symbol: str, generation: int, start_ms: int, reason: str) -> GridCycle:
    raw = f"{symbol}|{generation}|{start_ms}".encode("utf-8")
    cycle_id = "C-" + hashlib.sha256(raw).hexdigest()[:20]
    return GridCycle(
        cycle_id=cycle_id,
        generation=generation,
        start_ms=int(start_ms),
        last_update_ms=int(start_ms),
        restart_reason=str(reason),
    )


def _event_id(
    cycle_id: str,
    sequence: int,
    birth_ms: int,
    parent_cell: str,
    child_cell: str,
    crossing: str,
) -> str:
    raw = (
        f"{cycle_id}|{sequence}|{birth_ms}|{parent_cell}|{child_cell}|{crossing}"
    ).encode("utf-8")
    return "E-" + hashlib.sha256(raw).hexdigest()[:24]


def _require_monotonic(previous_ms: int, now_ms: int, label: str) -> None:
    if int(now_ms) < int(previous_ms):
        raise ValueError(
            f"{label} timestamp moved backwards: {now_ms} < {previous_ms}"
        )


def _category_pairs(context: ContextSnapshot) -> list[tuple[str, str]]:
    pairs = [
        ("session", context.session.value),
        ("regime", context.regime.value),
        ("structure", context.structure.value),
        ("trend_phase", context.trend_phase.value),
        ("news_state", context.news_state.value),
    ]
    for tf in context.timeframe_states:
        pairs.append((f"timeframe_role:{tf.timeframe}", f"{tf.role.value}:{tf.state}"))
    return pairs


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {k: _jsonable(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


def build01_self_check() -> dict[str, Any]:
    """Deterministic synthetic QA fixture; no market alpha."""
    state = GridSystemState(start_ms=1_000)
    e1 = state.new_event(
        1_100,
        parent_cell="P0",
        child_cell="C0",
        crossing_direction=CrossingDirection.UP,
        penetration_raw=5,
    )
    e1.recross(1_150, penetration_raw=7)
    state.record_external_trade_result(e1.event_id, 1.25)
    old_cycle, new_cycle = state.restart_cycle(2_000, "SYNTHETIC_STATE_CHANGE")
    e2 = state.new_event(
        2_100,
        parent_cell="P1",
        child_cell="C1",
        crossing_direction=CrossingDirection.DOWN,
    )
    return {
        "symbol": state.symbol,
        "lot_size": state.lot_size,
        "default_risk": RiskState.OBSERVE_ONLY.value,
        "old_cycle": old_cycle,
        "new_cycle": new_cycle,
        "cycle_changed": old_cycle != new_cycle,
        "event_ids_unique": e1.event_id != e2.event_id,
        "event1_expired_on_restart": e1.expired,
        "event2_sequence": e2.sequence,
        "route_is_neutral": (
            e2.route is not None
            and e2.route.primary_direction == DirectionHypothesis.UNCLASSIFIED
            and e2.route.risk_state == RiskState.OBSERVE_ONLY
        ),
        "ledger_cells": len(state.ledger.cells),
        "json_deterministic": state.to_json() == state.to_json(),
        "order_authority_present": False,
    }


if __name__ == "__main__":
    print(json.dumps(build01_self_check(), indent=2, sort_keys=True))

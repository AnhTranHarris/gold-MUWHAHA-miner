from __future__ import annotations

"""Delta-A-alpha BUILD-02: session/timeframe morphing router.

Extends BUILD-01's neutral state contract. It classifies a grid crossing and
populates an event route; it does not talk to MT5 or send orders.
"""

from dataclasses import dataclass
from enum import IntEnum

try:
    from grid_system_state_skeleton import (
        DirectionHypothesis,
        EventInterpretation,
        GridEvent,
        GridSystemState,
        RiskState,
        SessionState,
    )
except ImportError:
    from .grid_system_state_skeleton import (  # type: ignore
        DirectionHypothesis,
        EventInterpretation,
        GridEvent,
        GridSystemState,
        RiskState,
        SessionState,
    )

DAY_MS = 86_400_000


class TrendSign(IntEnum):
    DOWN = -1
    FLAT = 0
    UP = 1


@dataclass(frozen=True)
class RouteSpec:
    route_id: str
    gap_raw: int
    tp_raw: int
    sl_raw: int
    horizon_ms: int


ROUTES: dict[str, RouteSpec] = {
    "ASIA_REVERSAL_INIT": RouteSpec("ASIA_REVERSAL_INIT", 750, 2500, 1000, 300_000),
    "LONDON_MICRO_RELAY": RouteSpec("LONDON_MICRO_RELAY", 1000, 2500, 1000, 300_000),
    "OVERLAP_LOWER_TAKEOVER": RouteSpec("OVERLAP_LOWER_TAKEOVER", 750, 2500, 1000, 300_000),
    "NY_MIXED_MICRO_RELAY": RouteSpec("NY_MIXED_MICRO_RELAY", 1500, 2000, 1000, 300_000),
    "LATE_LOWER_TAKEOVER": RouteSpec("LATE_LOWER_TAKEOVER", 500, 2500, 1000, 300_000),
}


@dataclass(frozen=True)
class TimeframeSnapshot:
    h4: int
    h1: int
    m15: int
    m5: int
    h4_efficiency: float
    h1_efficiency: float


@dataclass(frozen=True)
class RouteDecision:
    route_id: str | None
    eligible: bool
    direction: int
    gap_raw: int | None = None
    tp_raw: int | None = None
    sl_raw: int | None = None
    horizon_ms: int | None = None
    reason: str = "ABSTAIN"


def session_from_utc_ms(timestamp_ms: int) -> SessionState:
    hour = (timestamp_ms % DAY_MS) / 3_600_000.0
    if hour >= 23.0 or hour < 7.0:
        return SessionState.ASIA
    if hour < 9.0:
        return SessionState.LONDON_OPEN
    if hour < 13.5:
        return SessionState.LONDON
    if hour < 16.0:
        return SessionState.OVERLAP
    if hour < 20.0:
        return SessionState.NEW_YORK
    if hour < 22.0:
        return SessionState.LATE_NY
    return SessionState.ROLLOVER


def classify_crossing(
    session: SessionState,
    crossing_direction: int,
    tf: TimeframeSnapshot,
) -> RouteDecision:
    d = 1 if crossing_direction > 0 else -1 if crossing_direction < 0 else 0
    if d == 0 or session == SessionState.ROLLOVER:
        return RouteDecision(None, False, 0, reason="NO_DIRECTION_OR_ROLLOVER")

    macro_aligned = tf.h4 != 0 and tf.h4 == tf.h1
    route: str | None = None

    if session == SessionState.ASIA:
        if (
            macro_aligned
            and tf.h1 == tf.m15 == tf.m5
            and d == -tf.h1
            and tf.h4_efficiency >= 0.30
            and tf.h1_efficiency >= 0.25
        ):
            route = "ASIA_REVERSAL_INIT"

    elif session in (SessionState.LONDON_OPEN, SessionState.LONDON):
        if macro_aligned and tf.m15 == tf.h1 and tf.m5 == -tf.h1 and d == tf.m5:
            route = "LONDON_MICRO_RELAY"

    elif session == SessionState.OVERLAP:
        if macro_aligned and tf.m15 == tf.m5 == -tf.h1 and d == tf.m5:
            route = "OVERLAP_LOWER_TAKEOVER"

    elif session == SessionState.NEW_YORK:
        if (not macro_aligned) and tf.m15 != 0 and tf.m5 == -tf.m15 and d == tf.m5:
            route = "NY_MIXED_MICRO_RELAY"

    elif session == SessionState.LATE_NY:
        if macro_aligned and tf.m15 == tf.m5 == -tf.h1 and d == tf.m5:
            route = "LATE_LOWER_TAKEOVER"

    if route is None:
        return RouteDecision(None, False, d, reason="SESSION_TF_STATE_NOT_ELIGIBLE")

    spec = ROUTES[route]
    return RouteDecision(
        route_id=route,
        eligible=True,
        direction=d,
        gap_raw=spec.gap_raw,
        tp_raw=spec.tp_raw,
        sl_raw=spec.sl_raw,
        horizon_ms=spec.horizon_ms,
        reason="ELIGIBLE_FIRST_TOUCH",
    )


def apply_decision_to_event(
    state: GridSystemState,
    event: GridEvent,
    decision: RouteDecision,
) -> None:
    """Populate BUILD-01 route metadata; never sends an order."""
    if event.route is None:
        raise RuntimeError("BUILD-01 event is missing its route contract")

    if not decision.eligible:
        event.route.primary_direction = DirectionHypothesis.ABSTAIN
        event.route.interpretation = EventInterpretation.OBSERVE
        event.route.risk_state = RiskState.OBSERVE_ONLY
        return

    event.route.primary_direction = (
        DirectionHypothesis.LONG if decision.direction > 0 else DirectionHypothesis.SHORT
    )
    event.route.alternative_direction = DirectionHypothesis.ABSTAIN
    event.route.interpretation = EventInterpretation.CONTINUATION
    event.route.horizon_ms = decision.horizon_ms
    event.route.risk_state = RiskState.OPEN_NEW_RISK
    state.risk_state = RiskState.OPEN_NEW_RISK
    event.rearm_eligible = False


def build02_self_check() -> dict[str, object]:
    tf = TimeframeSnapshot(-1, -1, -1, -1, 0.50, 0.45)
    asia = classify_crossing(SessionState.ASIA, 1, tf)
    tf2 = TimeframeSnapshot(1, 1, 1, -1, 0.40, 0.30)
    london = classify_crossing(SessionState.LONDON, -1, tf2)
    rollover = classify_crossing(SessionState.ROLLOVER, 1, tf2)
    return {
        "asia_route": asia.route_id,
        "london_route": london.route_id,
        "rollover_eligible": rollover.eligible,
        "route_count": len(ROUTES),
        "timer_rearm_present": False,
        "order_authority_present": False,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(build02_self_check(), indent=2, sort_keys=True))

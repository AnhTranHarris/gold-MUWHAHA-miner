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



def trend_label(value: int) -> str:
    if value > 0:
        return "UP"
    if value < 0:
        return "DOWN"
    return "FLAT"


def apply_timeframe_snapshot(
    state: GridSystemState,
    snapshot: TimeframeSnapshot,
    now_ms: int,
) -> None:
    """Populate BUILD-01 role fields from completed-bar right-edge states."""
    state.update_timeframe_state("H4", trend_label(snapshot.h4), now_ms)
    state.update_timeframe_state("H1", trend_label(snapshot.h1), now_ms)
    state.update_timeframe_state("M15", trend_label(snapshot.m15), now_ms)
    state.update_timeframe_state("M5", trend_label(snapshot.m5), now_ms)


def update_session_phase(state: GridSystemState, now_ms: int) -> tuple[SessionState, bool]:
    """Apply the UTC session phase and restart the finite grid cycle on handoff.

    The first classification from UNKNOWN initializes the phase without a restart.
    Later changes are explicit new-information boundaries and expire prior-cycle
    event ownership through BUILD-01's restart contract.
    """
    new_session = session_from_utc_ms(now_ms)
    old_session = state.session
    if new_session == old_session:
        return new_session, False

    if old_session != SessionState.UNKNOWN:
        state.restart_cycle(
            now_ms,
            f"SESSION_PHASE:{old_session.value}->{new_session.value}",
        )
    state.session = new_session
    return new_session, True

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
    state = GridSystemState(start_ms=0)
    _, changed0 = update_session_phase(state, 1_000)
    first_cycle = state.cycle.cycle_id
    _, changed1 = update_session_phase(state, 7 * 3_600_000)
    second_cycle = state.cycle.cycle_id
    apply_timeframe_snapshot(state, tf2, 7 * 3_600_000)

    return {
        "asia_route": asia.route_id,
        "london_route": london.route_id,
        "rollover_eligible": rollover.eligible,
        "route_count": len(ROUTES),
        "session_initialized": changed0,
        "session_handoff_restart": changed1 and first_cycle != second_cycle,
        "h4_state": state.timeframe_states["H4"].state,
        "m5_state": state.timeframe_states["M5"].state,
        "timer_rearm_present": False,
        "order_authority_present": False,
    }


# ---------------------------------------------------------------------------
# BUILD-02 refinement 001: sleeve-local session/timeframe ownership
# ---------------------------------------------------------------------------
# STMR-001 remains above as the historical parent floor.  The refinement below
# expands the same role-separated architecture into semantic sleeves.  A price
# cell is first-touch within a sleeve, so a genuinely different ownership state
# may create a new opportunity without timer-only rearming.

@dataclass(frozen=True)
class SleeveSpec:
    sleeve_id: str
    gap_raw: int
    tp_raw: int
    sl_raw: int
    horizon_ms: int = 300_000


SLEEVE_SPECS: dict[str, SleeveSpec] = {
    "ASIA_LOWER_TAKEOVER": SleeveSpec("ASIA_LOWER_TAKEOVER", 750, 4000, 1000),
    "ASIA_M15_DIVERGE_M5_RECLAIM": SleeveSpec("ASIA_M15_DIVERGE_M5_RECLAIM", 750, 4000, 1500),
    "LONDON_M5_TAKEOVER": SleeveSpec("LONDON_M5_TAKEOVER", 1000, 4000, 750),
    "LONDON_M5_RECLAIM": SleeveSpec("LONDON_M5_RECLAIM", 1000, 3000, 750),
    "OVERLAP_LOWER_TAKEOVER": SleeveSpec("OVERLAP_LOWER_TAKEOVER", 750, 4000, 1500),
    "OVERLAP_ALIGNED_COUNTERCROSS": SleeveSpec("OVERLAP_ALIGNED_COUNTERCROSS", 750, 3000, 750),
    "NY_LOWER_TRANSFER": SleeveSpec("NY_LOWER_TRANSFER", 1500, 4000, 1500),
    "NY_LOWER_COUNTERCROSS": SleeveSpec("NY_LOWER_COUNTERCROSS", 1500, 2500, 1500),
    "LATE_ALIGNED_MOMENTUM": SleeveSpec("LATE_ALIGNED_MOMENTUM", 500, 4000, 1500),
    "LATE_MACRO_SPLIT_TRANSFER": SleeveSpec("LATE_MACRO_SPLIT_TRANSFER", 500, 4000, 1500),
    "LATE_M5_REJECTION": SleeveSpec("LATE_M5_REJECTION", 500, 4000, 1500),
    "LATE_LOWER_TAKEOVER": SleeveSpec("LATE_LOWER_TAKEOVER", 500, 2500, 1250),
}


@dataclass(frozen=True)
class SleeveDecision:
    sleeve_id: str | None
    eligible: bool
    direction: int
    gap_raw: int | None = None
    tp_raw: int | None = None
    sl_raw: int | None = None
    horizon_ms: int | None = None
    reason: str = "ABSTAIN"


def _sleeve_candidate(
    session: SessionState,
    crossing_direction: int,
    tf: TimeframeSnapshot,
) -> tuple[str | None, int]:
    """Return the semantic sleeve and its expected crossing direction.

    H4/H1 own the slower environment, M15 owns intraday phase, and M5 owns a
    causal transfer/reclaim.  Deliberate disagreement is therefore information,
    not an automatic veto.
    """
    d = 1 if crossing_direction > 0 else -1 if crossing_direction < 0 else 0
    if d == 0:
        return None, 0

    macro = tf.h4 != 0 and tf.h4 == tf.h1
    sleeve: str | None = None
    expected = 0

    if session == SessionState.ASIA:
        if macro and tf.m15 == tf.m5 == -tf.h1:
            sleeve, expected = "ASIA_LOWER_TAKEOVER", tf.m5
        elif macro and tf.m15 == -tf.h1 and tf.m5 == tf.h1:
            sleeve, expected = "ASIA_M15_DIVERGE_M5_RECLAIM", tf.m5

    elif session == SessionState.LONDON:
        if macro and tf.m15 == tf.h1 and tf.m5 == -tf.h1:
            sleeve, expected = "LONDON_M5_TAKEOVER", tf.m5
        elif macro and tf.m15 == -tf.h1 and tf.m5 == tf.h1:
            sleeve, expected = "LONDON_M5_RECLAIM", tf.m5

    elif session == SessionState.OVERLAP:
        if macro and tf.m15 == tf.m5 == -tf.h1:
            sleeve, expected = "OVERLAP_LOWER_TAKEOVER", tf.m5
        elif macro and tf.m15 == tf.m5 == tf.h1:
            sleeve, expected = "OVERLAP_ALIGNED_COUNTERCROSS", -tf.m5

    elif session == SessionState.NEW_YORK:
        if tf.h4 != 0 and tf.h1 != 0 and tf.h4 != tf.h1:
            if tf.m15 != 0 and tf.m5 == -tf.m15:
                sleeve, expected = "NY_LOWER_TRANSFER", tf.m5
            elif tf.m15 == tf.m5 and tf.m15 != 0:
                sleeve, expected = "NY_LOWER_COUNTERCROSS", -tf.m5

    elif session == SessionState.LATE_NY:
        if tf.h4 == tf.h1 == tf.m15 == tf.m5 and tf.h4 != 0:
            sleeve, expected = "LATE_ALIGNED_MOMENTUM", tf.m5
        elif (
            tf.h4 != 0
            and tf.h1 != 0
            and tf.h4 != tf.h1
            and tf.m15 != 0
            and tf.m5 == -tf.m15
        ):
            sleeve, expected = "LATE_MACRO_SPLIT_TRANSFER", tf.m5
        elif macro and tf.m15 == tf.h1 and tf.m5 == -tf.h1:
            sleeve, expected = "LATE_M5_REJECTION", -tf.m5
        elif macro and tf.m15 == tf.m5 == -tf.h1:
            sleeve, expected = "LATE_LOWER_TAKEOVER", tf.m5

    return sleeve, expected


def sleeve_phase_gate(sleeve_id: str, timestamp_ms: int) -> bool:
    """Targeted gates retained only where January halves supported them."""
    minute = (timestamp_ms % DAY_MS) // 60_000
    if sleeve_id == "ASIA_LOWER_TAKEOVER":
        return minute >= 1380  # 23:00-00:00 UTC
    if sleeve_id == "LONDON_M5_TAKEOVER":
        return 660 <= minute < 720  # 11:00-12:00 UTC
    return True


def classify_sleeve_crossing(
    session: SessionState,
    crossing_direction: int,
    tf: TimeframeSnapshot,
    timestamp_ms: int,
) -> SleeveDecision:
    """Classify one sleeve-local first-touch crossing.

    London Open and rollover are deliberately observe-only.  This function does
    not manage first-touch memory itself; event genealogy owns that state.
    """
    d = 1 if crossing_direction > 0 else -1 if crossing_direction < 0 else 0
    if d == 0 or session in (SessionState.LONDON_OPEN, SessionState.ROLLOVER):
        return SleeveDecision(None, False, d, reason="OBSERVE_ONLY_SESSION")

    sleeve, expected = _sleeve_candidate(session, d, tf)
    if sleeve is None or d != expected:
        return SleeveDecision(None, False, d, reason="OWNERSHIP_STATE_NOT_ELIGIBLE")
    if not sleeve_phase_gate(sleeve, timestamp_ms):
        return SleeveDecision(sleeve, False, d, reason="TARGETED_SUBPHASE_GATE")

    spec = SLEEVE_SPECS[sleeve]
    return SleeveDecision(
        sleeve_id=sleeve,
        eligible=True,
        direction=d,
        gap_raw=spec.gap_raw,
        tp_raw=spec.tp_raw,
        sl_raw=spec.sl_raw,
        horizon_ms=spec.horizon_ms,
        reason="ELIGIBLE_SLEEVE_FIRST_TOUCH",
    )


def build02_refinement_self_check() -> dict[str, object]:
    asia = TimeframeSnapshot(1, 1, -1, -1, 0.0, 0.0)
    london = TimeframeSnapshot(1, 1, 1, -1, 0.0, 0.0)
    overlap = TimeframeSnapshot(1, 1, -1, -1, 0.0, 0.0)
    return {
        "asia_first_hour": classify_sleeve_crossing(
            SessionState.ASIA, -1, asia, 23 * 3_600_000
        ).sleeve_id,
        "asia_after_gate": classify_sleeve_crossing(
            SessionState.ASIA, -1, asia, 1 * 3_600_000
        ).eligible,
        "london_11utc": classify_sleeve_crossing(
            SessionState.LONDON, -1, london, 11 * 3_600_000
        ).sleeve_id,
        "overlap_takeover": classify_sleeve_crossing(
            SessionState.OVERLAP, -1, overlap, 14 * 3_600_000
        ).sleeve_id,
        "sleeve_count": len(SLEEVE_SPECS),
        "timer_rearm_present": False,
        "order_authority_present": False,
    }


if __name__ == "__main__":
    import json
    print(json.dumps({"parent": build02_self_check(), "refinement": build02_refinement_self_check()}, indent=2, sort_keys=True))

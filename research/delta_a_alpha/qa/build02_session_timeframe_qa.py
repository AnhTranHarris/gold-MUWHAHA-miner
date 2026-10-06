from __future__ import annotations

"""Runtime QA for Delta-A-alpha BUILD-02 session/timeframe state routing."""

import json
from pathlib import Path
import sys

EXPERIMENTS = Path(__file__).resolve().parents[1] / "experiments"
sys.path.insert(0, str(EXPERIMENTS))

import grid_system_session_timeframe as s  # noqa: E402
import grid_system_state_skeleton as g  # noqa: E402


def main() -> dict:
    assert len(s.ROUTES) == 5
    assert s.ROUTES["ASIA_REVERSAL_INIT"].gap_raw == 750
    assert s.ROUTES["LONDON_MICRO_RELAY"].gap_raw == 1000
    assert s.ROUTES["OVERLAP_LOWER_TAKEOVER"].gap_raw == 750
    assert s.ROUTES["NY_MIXED_MICRO_RELAY"].gap_raw == 1500
    assert s.ROUTES["LATE_LOWER_TAKEOVER"].gap_raw == 500

    assert s.session_from_utc_ms(1_000) == g.SessionState.ASIA
    assert s.session_from_utc_ms(7 * 3_600_000) == g.SessionState.LONDON_OPEN
    assert s.session_from_utc_ms(14 * 3_600_000) == g.SessionState.OVERLAP
    assert s.session_from_utc_ms(22 * 3_600_000) == g.SessionState.ROLLOVER

    asia_tf = s.TimeframeSnapshot(-1, -1, -1, -1, 0.50, 0.45)
    asia = s.classify_crossing(g.SessionState.ASIA, 1, asia_tf)
    assert asia.eligible and asia.route_id == "ASIA_REVERSAL_INIT"

    london_tf = s.TimeframeSnapshot(1, 1, 1, -1, 0.40, 0.30)
    london = s.classify_crossing(g.SessionState.LONDON, -1, london_tf)
    assert london.eligible and london.route_id == "LONDON_MICRO_RELAY"

    rollover = s.classify_crossing(g.SessionState.ROLLOVER, 1, london_tf)
    assert rollover.eligible is False

    state = g.GridSystemState(start_ms=0)
    phase0, changed0 = s.update_session_phase(state, 1_000)
    old_cycle = state.cycle.cycle_id
    phase1, changed1 = s.update_session_phase(state, 7 * 3_600_000)
    new_cycle = state.cycle.cycle_id
    assert changed0 is True and phase0 == g.SessionState.ASIA
    assert changed1 is True and phase1 == g.SessionState.LONDON_OPEN
    assert old_cycle != new_cycle

    s.apply_timeframe_snapshot(state, london_tf, 7 * 3_600_000)
    assert state.timeframe_states["H4"].state == "UP"
    assert state.timeframe_states["M5"].state == "DOWN"

    e = state.new_event(7 * 3_600_000, "P0", "C1", g.CrossingDirection.DOWN)
    s.apply_decision_to_event(state, e, london)
    assert e.route is not None
    assert e.route.primary_direction == g.DirectionHypothesis.SHORT
    assert e.route.risk_state == g.RiskState.OPEN_NEW_RISK
    assert e.rearm_eligible is False

    self_check = s.build02_self_check()
    assert self_check["asia_route"] == "ASIA_REVERSAL_INIT"
    assert self_check["london_route"] == "LONDON_MICRO_RELAY"
    assert self_check["rollover_eligible"] is False
    assert self_check["session_handoff_restart"] is True
    assert self_check["timer_rearm_present"] is False
    assert self_check["order_authority_present"] is False

    return {
        "status": "PASS",
        "unit": "DAA_GRID_SYSTEM_BUILD_02_SESSION_TIMEFRAME_AWARENESS",
        "routes": len(s.ROUTES),
        "session_handoff_restart": True,
        "timeframe_role_population": True,
        "timer_only_rearm": False,
        "order_authority_present": False,
    }


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, sort_keys=True))

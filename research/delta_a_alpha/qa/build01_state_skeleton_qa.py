from __future__ import annotations

"""QA harness for Delta-A-alpha BUILD-01 neutral state skeleton."""

import inspect
import json
from pathlib import Path
import sys

EXPERIMENTS = Path(__file__).resolve().parents[1] / "experiments"
sys.path.insert(0, str(EXPERIMENTS))

import grid_system_state_skeleton as g  # noqa: E402


def must_raise(exc_type, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc_type:
        return
    raise AssertionError(f"expected {exc_type.__name__}")


def main() -> dict:
    assert g.SYMBOL == "XAUUSD"
    assert g.FIXED_LOT == 0.01

    a = g.GridSystemState(start_ms=1000)
    b = g.GridSystemState(start_ms=1000)

    assert a.risk_state == g.RiskState.OBSERVE_ONLY
    assert a.session == g.SessionState.UNKNOWN
    assert a.regime == g.RegimeState.UNKNOWN
    assert a.structure == g.StructureState.UNKNOWN
    assert a.trend_phase == g.TrendPhase.UNKNOWN
    assert a.news_state == g.NewsState.NORMAL

    expected_roles = {
        "D1": g.TimeframeRole.ENVIRONMENT,
        "H4": g.TimeframeRole.ENVIRONMENT,
        "H1": g.TimeframeRole.STRUCTURE,
        "M15": g.TimeframeRole.STRUCTURE,
        "M5": g.TimeframeRole.OPPORTUNITY,
        "M1": g.TimeframeRole.OPPORTUNITY,
        "TICK": g.TimeframeRole.EXECUTION,
    }
    assert {k: v.role for k, v in a.timeframe_states.items()} == expected_roles

    e1a = a.new_event(
        1100, "P0", "C0", g.CrossingDirection.UP, penetration_raw=5
    )
    e1b = b.new_event(
        1100, "P0", "C0", g.CrossingDirection.UP, penetration_raw=5
    )
    assert a.cycle.cycle_id == b.cycle.cycle_id
    assert e1a.event_id == e1b.event_id
    assert a.to_json() == b.to_json()

    # Direct event mutation cannot allow a backward cycle restart.
    e1a.recross(1200, penetration_raw=8)
    old_cycle = a.cycle.cycle_id
    must_raise(ValueError, a.restart_cycle, 1150, "BACKWARD_INVALID")
    assert a.cycle.cycle_id == old_cycle
    assert a.cycle.status == g.CycleStatus.ACTIVE

    # State timestamps are right-edge monotonic.
    must_raise(ValueError, a.update_timeframe_state, "M1", "UP", 999)

    # Fixed-lot and XAUUSD invariants are revalidated after construction.
    c = g.GridSystemState(start_ms=1000)
    c.lot_size = 0.02
    must_raise(ValueError, c.to_json)

    d = g.GridSystemState(start_ms=1000)
    d.symbol = "EURUSD"
    must_raise(ValueError, d.to_json)

    # Finite lifecycle produces a new cycle and retires old active events.
    old_id, new_id = a.restart_cycle(2000, "STRUCTURE_CHANGE")
    assert old_id != new_id
    assert e1a.expired is True
    assert old_id in a.closed_cycle_ids

    e2 = a.new_event(2100, "P1", "C1", g.CrossingDirection.DOWN)
    assert e2.sequence == 1
    assert e2.event_id != e1a.event_id
    assert e2.route is not None
    assert e2.route.primary_direction == g.DirectionHypothesis.UNCLASSIFIED
    assert e2.route.alternative_direction == g.DirectionHypothesis.ABSTAIN
    assert e2.route.risk_state == g.RiskState.OBSERVE_ONLY

    risk_before = a.risk_state
    route_before = e2.route.primary_direction
    a.record_external_trade_result(e2.event_id, -1.25)
    assert a.risk_state == risk_before
    assert e2.route.primary_direction == route_before
    assert len(a.ledger.cells) > 0

    # JSON-safe deterministic serialization.
    payload1 = a.to_json()
    payload2 = a.to_json()
    assert payload1 == payload2
    json.loads(payload1)

    # The architecture module contains no order/signal authority.
    banned_callables = {
        "buy", "sell", "place_order", "send_order", "execute_order",
        "open_position", "close_position", "generate_signal", "signal"
    }
    public_callables = {
        name
        for name, obj in inspect.getmembers(g)
        if callable(obj) and not name.startswith("_")
    }
    assert banned_callables.isdisjoint(public_callables)

    required_news = {
        "NORMAL", "PRE_EVENT", "RELEASE_WINDOW", "POST_EVENT_SHOCK",
        "POST_EVENT_DISCOVERY", "NORMALIZED"
    }
    assert required_news.issubset({x.value for x in g.NewsState})

    required_risk = {
        "OBSERVE_ONLY", "OPEN_NEW_RISK", "HOLD_EXISTING",
        "REDUCE_ONLY", "EXIT", "HALT"
    }
    assert required_risk.issubset({x.value for x in g.RiskState})

    self_check = g.build01_self_check()
    assert self_check["cycle_changed"] is True
    assert self_check["event_ids_unique"] is True
    assert self_check["route_is_neutral"] is True
    assert self_check["json_deterministic"] is True
    assert self_check["order_authority_present"] is False

    return {
        "status": "PASS",
        "unit": "DAA_GRID_SYSTEM_BUILD_01_STATE_SKELETON",
        "fixed_lot": g.FIXED_LOT,
        "symbol": g.SYMBOL,
        "deterministic_ids": True,
        "finite_cycle_restart": True,
        "monotonic_time_guard": True,
        "contract_mutation_guard": True,
        "json_serialization": True,
        "category_ledger": True,
        "order_authority_present": False,
    }


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, sort_keys=True))

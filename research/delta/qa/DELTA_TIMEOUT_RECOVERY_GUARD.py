"""DELTA timeout-recovery cursor guard.

This gate prevents a missing ChatGPT delivery from being mistaken for missing research.
It validates the durable in-flight cursor against CURRENT_STATE and checks that every
phase-appropriate repository artifact already exists before later phases are claimed.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STATE = ROOT / "CURRENT_STATE.json"
INFLIGHT = ROOT / "research" / "delta" / "CURRENT_INFLIGHT.json"
POINTER = ROOT / "research" / "delta" / "handoffs" / "DELTA_R037_TIMEOUT_RECOVERY_POINTER.json"

PHASE_RANK = {
    "PREREGISTERED": 1,
    "PRODUCER_COMMITTED": 2,
    "RESULT_COMMITTED": 3,
    "REPORT_COMMITTED": 4,
    "MANIFEST_COMMITTED": 5,
    "READY_TO_ADVANCE": 6,
    "IDLE": 0,
    "COMPLETE": 7,
}

REQUIRED_BY_PHASE = (
    (1, "prereg"),
    (2, "producer"),
    (3, "result"),
    (4, "report"),
    (5, "manifest"),
)


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"DELTA_TIMEOUT_GUARD FAIL: missing {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"DELTA_TIMEOUT_GUARD FAIL: invalid JSON {path.relative_to(ROOT)}: {exc}") from exc


def safe_repo_path(value: str) -> Path:
    p = Path(value)
    if p.is_absolute() or ".." in p.parts:
        raise SystemExit(f"DELTA_TIMEOUT_GUARD FAIL: unsafe repo path {value!r}")
    out = ROOT / p
    try:
        out.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"DELTA_TIMEOUT_GUARD FAIL: escaped repo path {value!r}") from exc
    return out


def main() -> int:
    state = load(STATE)
    inflight = load(INFLIGHT)
    pointer = load(POINTER)

    if inflight.get("schema") != "delta-timeout-recovery-inflight-v1":
        raise SystemExit("DELTA_TIMEOUT_GUARD FAIL: unsupported in-flight schema")

    if pointer.get("schema") != "delta-timeout-recovery-pointer-v1":
        raise SystemExit("DELTA_TIMEOUT_GUARD FAIL: unsupported recovery-pointer schema")

    durable = pointer.get("durable_cursor")
    if not isinstance(durable, dict):
        raise SystemExit("DELTA_TIMEOUT_GUARD FAIL: recovery pointer missing durable_cursor")
    expected_durable = {
        "last_verified_durable_unit": state.get("last_verified_durable_unit"),
        "current_phase": state.get("current_phase"),
        "first_incomplete_unit": state.get("first_incomplete_unit"),
        "active_rebuild_manifest": state.get("active_rebuild_manifest_path"),
    }
    for key, expected in expected_durable.items():
        if durable.get(key) != expected:
            raise SystemExit(
                f"DELTA_TIMEOUT_GUARD FAIL: stale recovery pointer durable_cursor.{key}: "
                f"{durable.get(key)!r} != {expected!r}"
            )

    pointer_inflight = pointer.get("in_flight_unit")
    if not isinstance(pointer_inflight, dict):
        raise SystemExit("DELTA_TIMEOUT_GUARD FAIL: recovery pointer missing in_flight_unit")
    if pointer_inflight.get("unit") != inflight.get("unit"):
        raise SystemExit("DELTA_TIMEOUT_GUARD FAIL: recovery pointer in-flight unit is stale")
    if pointer_inflight.get("status") != inflight.get("phase"):
        raise SystemExit("DELTA_TIMEOUT_GUARD FAIL: recovery pointer in-flight phase is stale")
    if int(pointer_inflight.get("phase_rank", -1)) != int(inflight.get("phase_rank", -2)):
        raise SystemExit("DELTA_TIMEOUT_GUARD FAIL: recovery pointer in-flight phase_rank is stale")
    if pointer_inflight.get("parent_durable_unit") != inflight.get("parent_durable_unit"):
        raise SystemExit("DELTA_TIMEOUT_GUARD FAIL: recovery pointer parent durable unit is stale")

    status = inflight.get("status")
    phase = inflight.get("phase")
    if phase not in PHASE_RANK:
        raise SystemExit(f"DELTA_TIMEOUT_GUARD FAIL: unknown phase {phase!r}")
    rank = PHASE_RANK[phase]

    if int(inflight.get("phase_rank", -1)) != rank:
        raise SystemExit("DELTA_TIMEOUT_GUARD FAIL: phase_rank does not match phase")

    if status == "INFLIGHT":
        if inflight.get("unit") != state.get("first_incomplete_unit"):
            raise SystemExit(
                "DELTA_TIMEOUT_GUARD FAIL: in-flight unit does not match CURRENT_STATE first_incomplete_unit"
            )
        if inflight.get("parent_durable_unit") != state.get("last_verified_durable_unit"):
            raise SystemExit(
                "DELTA_TIMEOUT_GUARD FAIL: in-flight parent does not match CURRENT_STATE last_verified_durable_unit"
            )
    elif status not in {"COMPLETE", "IDLE"}:
        raise SystemExit(f"DELTA_TIMEOUT_GUARD FAIL: unsupported status {status!r}")

    for min_rank, key in REQUIRED_BY_PHASE:
        if rank < min_rank:
            continue
        obj = inflight.get(key)
        if not isinstance(obj, dict) or not obj.get("path"):
            raise SystemExit(f"DELTA_TIMEOUT_GUARD FAIL: phase {phase} requires {key}.path")
        p = safe_repo_path(obj["path"])
        if not p.is_file():
            raise SystemExit(
                f"DELTA_TIMEOUT_GUARD FAIL: phase {phase} references missing {p.relative_to(ROOT)}"
            )

    if inflight.get("august_2026") != "SEALED":
        raise SystemExit("DELTA_TIMEOUT_GUARD FAIL: August must remain SEALED")
    if inflight.get("mql5_authorized") is not False:
        raise SystemExit("DELTA_TIMEOUT_GUARD FAIL: MQL5 authorization changed unexpectedly")

    print(
        "DELTA_TIMEOUT_GUARD PASS "
        f"status={status} phase={phase} "
        f"unit={inflight.get('unit')} parent={inflight.get('parent_durable_unit')} pointer=consistent"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

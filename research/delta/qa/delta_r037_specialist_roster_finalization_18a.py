"""DELTA R037 specialist-roster finalization QA — Checkpoint 18A.

Deterministic repository-only validator. It performs no market replay and accesses no
tick data. Its job is to prove that the four frozen specialist closure manifests are
rebuild-ready, the timeout-stale 17DE-17DG unit is actually complete/retired, and the
current shared helper set contains no unfinished implementation markers.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

CLOSURE_MANIFESTS = {
    "DH05-S06": "research/delta/artifacts/DELTA_R037_DH05_PROBE_ATTEMPT_COUNTER_PROVENANCE_DECISION_CHECKPOINT_10F_MANIFEST.json",
    "DH02-S11": "research/delta/artifacts/DELTA_R037_DH02_S11_FAILURE_STATE_MEMORY_PROVENANCE_DECISION_CHECKPOINT_11G_MANIFEST.json",
    "DH02-S08": "research/delta/artifacts/DELTA_R037_DH02_S08_PARENT_DIRECTION_PROVENANCE_DECISION_CHECKPOINT_12C_MANIFEST.json",
    "DH03-S06": "research/delta/artifacts/DELTA_R037_DH03_S06_SIGNAL_GENERATOR_PROVENANCE_DECISION_CHECKPOINT_13H_MANIFEST.json",
}

HELPERS = (
    "research/delta/qa/delta_bounded_python_runner.py",
    "research/delta/experiments/delta_r037_dh05_runtime_primitives.py",
    "research/delta/experiments/delta_r037_dh03_s06_engine.py",
    "research/delta/experiments/delta_r037_dh03_s06_structure.py",
    "research/delta/experiments/delta_r037_r032_full_specialist_parent_parity.py",
)

ASIA_RESULT = (
    "research/delta/reference/"
    "DELTA_R037_ASIA_RANGE_DIRECTIONALITY_CHECKPOINT_17DE_17DG.json"
)

# Bare pass is allowed only in the explicit FileNotFoundError cleanup primitive.
UNFINISHED = re.compile(r"\b(TODO|FIXME|NotImplemented|placeholder|stub)\b", re.I)


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="\n",
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
        ) as tmp:
            tmp_name = tmp.name
            json.dump(payload, tmp, indent=2)
            tmp.write("\n")
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_name, path)
        tmp_name = None
    finally:
        if tmp_name is not None:
            try:
                os.unlink(tmp_name)
            except FileNotFoundError:
                pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path)
    ns = ap.parse_args()

    closures = {}
    for name, rel in CLOSURE_MANIFESTS.items():
        m = load_json(rel)
        ready = m.get("python_rebuild_ready") is True
        missing = m.get("missing_required_artifacts") or []
        if not ready or missing:
            raise SystemExit(
                f"{name} closure not rebuild-ready: ready={ready} missing={missing}"
            )
        closures[name] = {
            "manifest": rel,
            "status": m.get("status"),
            "python_rebuild_ready": ready,
            "missing_required_artifacts": missing,
        }

    helper_qa = {}
    for rel in HELPERS:
        p = ROOT / rel
        text = p.read_text(encoding="utf-8")
        hits = [
            {"line": i, "text": line.strip()}
            for i, line in enumerate(text.splitlines(), 1)
            if UNFINISHED.search(line)
        ]
        if hits:
            raise SystemExit(f"unfinished marker(s) in {rel}: {hits}")
        helper_qa[rel] = {"exists": True, "unfinished_markers": []}

    asia = load_json(ASIA_RESULT)
    finding = asia.get("finding") or {}
    if asia.get("status") != "COMPLETE_FAST_CAUSAL_STAGE_A_SCREEN":
        raise SystemExit(f"17DE-17DG not complete: {asia.get('status')}")
    if finding.get("decision") != "RETIRE_ASIA_RANGE_DIRECTIONALITY_NO_STAGE_A_SURVIVOR":
        raise SystemExit(f"17DE-17DG disposition mismatch: {finding}")

    out = {
        "schema": "delta-r037-specialist-roster-finalization-qa-18a-v1",
        "status": "PASS",
        "market_replay_performed": False,
        "august_accessed": False,
        "closure_manifests": closures,
        "helper_qa": helper_qa,
        "timeout_reconciliation": {
            "unit": asia.get("unit"),
            "status": asia.get("status"),
            "decision": finding.get("decision"),
            "survivors": finding.get("survivors"),
        },
        "next": "R037_SPECIALIST_REFINEMENT_AND_INTEGRATION_PLAN",
    }

    if ns.output:
        atomic_json(ns.output, out)
    print(json.dumps(out, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

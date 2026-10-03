"""DELTA R037 DH02-S11 failure-state memory provenance decision — 11G.

Deterministic provenance-only unit. No market replay, no threshold tuning, no August.
The decision closes unsupported same-sample failure-memory recuts while preserving
only independently source-supported semantics and the separately labeled 11D
source-compatible challenger.
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path


EXPECTED_SCHEMA = "delta-r037-dh02-s11-failure-state-memory-provenance-evidence-11g-v1"


def atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    if evidence.get("schema") != EXPECTED_SCHEMA:
        raise SystemExit("unexpected evidence schema")
    if evidence.get("vector_fingerprint") != "50d1bb2e656e":
        raise SystemExit("unexpected S11 vector fingerprint")

    src = evidence["source_grounding"]
    p = evidence["provenance_conclusion"]
    c11f = evidence["checkpoint_11f"]
    c11d = evidence["checkpoint_11d"]

    gates = {
        "whitepaper_requires_causal_failure_acceptance": (
            "completed S1/S5 acceptance" in src["original_whitepaper"]["failure_rule"]
            and src["original_whitepaper"]["initial_hold_rule"].startswith("A single adverse tick is not enough")
        ),
        "immutable_s11_category_is_tick_persistence": (
            src["immutable_s11"]["failure_acceptance"] == "tick persistence"
        ),
        "exact_tick_memory_reset_semantics_missing": (
            src["original_whitepaper"]["exact_tick_memory_reset_semantics_preserved"] is False
            and src["preregistration"]["exact_tick_memory_reset_semantics_preserved"] is False
            and p["independent_exact_tick_memory_algorithm_found"] is False
        ),
        "11f_latch_selection_failed": c11f["selection_rule_pass"] is False,
        "11f_loss_tail_not_repaired": abs(
            float(c11f["latch"]["gross_loss"]) - float(c11f["control"]["gross_loss"])
        ) < 0.05,
        "11d_challenger_remains_nonpromoting": (
            c11d["challenger"]["status"] == "NON_PROMOTING_SOURCE_COMPATIBLE_CHALLENGER"
        ),
    }
    if not all(gates.values()):
        raise SystemExit("provenance gate mismatch: " + json.dumps(gates, sort_keys=True))

    out = {
        "schema": "delta-r037-dh02-s11-failure-state-memory-provenance-decision-11g-v1",
        "status": "COMPLETE_PROVENANCE_LIMITATION_FREEZE",
        "unit": evidence["unit"],
        "raw_ticks_accessed": False,
        "numeric_vector_retune": False,
        "vector_fingerprint": evidence["vector_fingerprint"],
        "gates": gates,
        "decision": {
            "promote_failure_memory_latch_semantic": False,
            "run_more_same_sample_failure_memory_recuts": False,
            "freeze_general_failure_semantic": p["preserve_general_semantic"],
            "preserve_11d_challenger_separately": True,
            "promote_11d_as_historical_truth": False,
            "s11_stream_disposition": p["candidate_surrogate_disposition"],
            "claim_exact_historical_s11_parity": False,
            "reason": (
                "The immutable S11 vector preserves only the categorical label "
                "'tick persistence'; surviving source material does not encode an "
                "exact tick-memory/reset algorithm. Checkpoint 11F changes the "
                "failure-memory state but removes a winner and leaves the residual "
                "gross-loss tail unchanged. More same-sample memory recuts would be "
                "retrospective fitting rather than source reconstruction."
            ),
            "next": evidence["proposed_next"],
        },
        "checkpoint_11d_challenger": c11d["challenger"],
        "checkpoint_11f": {
            "control": c11f["control"],
            "latch": c11f["latch"],
            "selection_rule_pass": c11f["selection_rule_pass"],
        },
        "august_2026": evidence["august_2026"],
        "sorb_integrated_replay_started": False,
        "mql5_authorized": False,
    }
    atomic_write_json(args.output, out)
    print(json.dumps(out["decision"], separators=(",", ":")))


if __name__ == "__main__":
    main()

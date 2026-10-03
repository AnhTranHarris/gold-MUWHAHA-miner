"""DELTA R037 DH05 residual probe-attempt counter provenance decision — Checkpoint 10F.

Evidence-synthesis only. No raw tick access and no threshold fitting.

Question:
Does any independent surviving historical source justify another universal DH05
probe-attempt counter/reset semantic after Checkpoints 10D/10E bracketed the
contact edge?

Decision rule:
- PROMOTE_ANOTHER_COUNTER_SEMANTIC only if a pre-10D independent source
  explicitly encodes that semantic.
- Otherwise freeze the 09Z attempt counter as the strongest reconstructible,
  non-promoting surrogate and record the remaining probe residual as a source
  provenance limitation.
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path


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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--r003-whitepapers", type=Path, required=True)
    ap.add_argument("--r006", type=Path, required=True)
    ap.add_argument("--r032", type=Path, required=True)
    ap.add_argument("--c09a", type=Path, required=True)
    ap.add_argument("--c09z", type=Path, required=True)
    ap.add_argument("--c10d", type=Path, required=True)
    ap.add_argument("--c10e", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    r003 = args.r003_whitepapers.read_text(encoding="utf-8")
    r006 = args.r006.read_text(encoding="utf-8")
    r032 = args.r032.read_text(encoding="utf-8")
    c09a = json.loads(args.c09a.read_text(encoding="utf-8"))
    c09z = json.loads(args.c09z.read_text(encoding="utf-8"))
    c10d = json.loads(args.c10d.read_text(encoding="utf-8"))
    c10e = json.loads(args.c10e.read_text(encoding="utf-8"))

    source_bytes_missing = not bool(
        c09a.get("source_recovery", {}).get("authoritative_bytes_found", True)
    )
    whitepaper_single_chain = (
        "IDLE -> PROBE -> FAILURE_CANDIDATE -> REENTRY -> RECLAIM_CONFIRMED"
        in r003
    )
    whitepaper_has_attempt_counter = any(
        token in r003
        for token in (
            "same-boundary attempt",
            "probe-attempt counter",
            "boundary-touch rearm",
            "strict pre-break reset",
        )
    )
    r006_has_attempt_counter = any(
        token in r006
        for token in (
            "same-boundary attempt",
            "probe-attempt counter",
            "boundary-touch rearm",
            "strict pre-break reset",
        )
    )
    r032_has_attempt_counter = any(
        token in r032
        for token in (
            "same-boundary attempt",
            "probe-attempt counter",
            "boundary-touch rearm",
            "strict pre-break reset",
        )
    )

    z = c09z.get("candidate", {})
    z_stage = z.get("stage_abs_error", {})
    d_profiles = c10d.get("profiles", {})
    e_profiles = c10e.get("profiles", {})

    control_probe = int(c10e["control_09z"]["probe_abs_error"])
    control_total = int(c10e["control_09z"]["total_abs_error"])

    strict_candidates = [
        int(v["probe_abs_error"]) for v in d_profiles.values()
        if isinstance(v, dict) and "probe_abs_error" in v
    ]
    touch_candidates = [
        int(v["probe_abs_error"]) for v in e_profiles.values()
        if isinstance(v, dict) and "probe_abs_error" in v
    ]
    strict_rejected = bool(strict_candidates and min(strict_candidates) > control_probe)
    touch_rejected = bool(touch_candidates and min(touch_candidates) > control_probe)

    independent_exact_counter_provenance = bool(
        whitepaper_has_attempt_counter
        or r006_has_attempt_counter
        or r032_has_attempt_counter
    )

    freeze_residual = bool(
        source_bytes_missing
        and whitepaper_single_chain
        and not independent_exact_counter_provenance
        and strict_rejected
        and touch_rejected
    )

    out = {
        "schema": "delta-r037-dh05-probe-attempt-counter-provenance-decision-10f-v1",
        "status": (
            "COMPLETE_PROVENANCE_LIMITATION_FREEZE"
            if freeze_residual
            else "COMPLETE_PROVENANCE_REVIEW_FURTHER_EVIDENCE_REQUIRED"
        ),
        "unit": "R037_DH05_PROBE_RESIDUAL_ATTEMPT_COUNTER_PROVENANCE_DECISION",
        "raw_ticks_accessed": False,
        "numeric_vector_retune": False,
        "evidence": {
            "authoritative_historical_source_bytes_missing": source_bytes_missing,
            "r003_whitepaper_single_chain_present": whitepaper_single_chain,
            "r003_exact_attempt_counter_semantic_present": whitepaper_has_attempt_counter,
            "r006_exact_attempt_counter_semantic_present": r006_has_attempt_counter,
            "r032_exact_attempt_counter_semantic_present": r032_has_attempt_counter,
            "independent_exact_counter_provenance": independent_exact_counter_provenance,
            "10d_strict_beyond_candidates_all_worse_than_09z": strict_rejected,
            "10e_touch_reset_candidates_all_worse_than_09z": touch_rejected,
        },
        "09z_control": {
            "probe_abs_error": control_probe,
            "total_abs_error": control_total,
            "stage_abs_error": z_stage,
            "aggregate_trade_count_abs_error": z.get("aggregate_trade_count_abs_error"),
        },
        "decision": {
            "promote_another_universal_attempt_counter_semantic": False,
            "freeze_09z_attempt_counter_as_best_reconstructible_surrogate": freeze_residual,
            "claim_exact_historical_dh05_parity": False,
            "record_remaining_probe_error_as_provenance_limitation": freeze_residual,
            "remaining_probe_abs_error": control_probe,
            "reason": (
                "No surviving independent pre-10D source encodes another exact universal "
                "probe-attempt counter/reset rule; authoritative producer bytes remain "
                "missing, while 10D and 10E causally bracket the contact edge and both "
                "alternative universal recuts worsen parity. Further same-sample recuts "
                "would be retrospective fitting rather than source reconstruction."
            ),
            "dh05_stream_disposition": (
                "PROVENANCE_LIMITED_BEST_RECONSTRUCTION_09Z_NON_PROMOTING"
                if freeze_residual
                else "OPEN"
            ),
            "next": (
                "R037_DH02_S11_CLEANROOM_PARITY_RECONSTRUCTION"
                if freeze_residual
                else "R037_DH05_PROBE_RESIDUAL_ATTEMPT_COUNTER_PROVENANCE_DECISION"
            ),
        },
        "august_2026": "SEALED",
        "sorb_integrated_replay_started": False,
        "mql5_authorized": False,
    }

    atomic_write_json(args.output, out)
    print(json.dumps(out["decision"], separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

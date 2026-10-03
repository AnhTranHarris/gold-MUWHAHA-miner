"""DELTA R037 DH05 residual probe-attempt counter provenance decision — Checkpoint 10F.

Evidence-synthesis only. No raw tick access and no threshold fitting.

This producer consumes the frozen provenance-evidence ledger committed before the
official decision. Another universal counter/reset semantic is eligible only when an
independent surviving source explicitly encodes it. Otherwise the 09Z counter remains
the strongest reconstructible non-promoting surrogate and the residual is recorded as
an unrecoverable historical-helper limitation rather than fitted retrospectively.
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
    ap.add_argument("--evidence", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    e = json.loads(args.evidence.read_text(encoding="utf-8"))
    if e.get("schema") != "delta-r037-dh05-probe-attempt-counter-provenance-evidence-10f-v1":
        raise SystemExit("unexpected evidence schema")
    if e.get("raw_ticks_accessed") is not False:
        raise SystemExit("provenance unit must not access raw ticks")
    if e.get("august_2026") != "SEALED":
        raise SystemExit("August must remain SEALED")

    by_name = {}
    for src in e.get("sources", []):
        key = src.get("name") or src.get("path")
        by_name[key] = src.get("findings", {})

    wp = by_name["DH-05 White Paper — Failed-Break Reversal Specialist"]
    r003 = by_name["research/delta/research/DELTA_R003_DIRECTION_HOLD_CAUSAL_GRAMMAR_WHITEPAPERS.md"]
    r006 = by_name["research/delta/research/DELTA_R006_STAGE_A_DIRECTION_HOLD_SPEEDRUN_RESULTS.md"]
    r032 = by_name["research/delta/research/DELTA_R032_AUTHORITATIVE_BASKET_RESULTS.md"]
    c09a = by_name["research/delta/reference/DELTA_R037_DH05_SOURCE_DURABILITY_RECOVERY_CHECKPOINT_09A.json"]
    c09z = by_name["research/delta/reference/DELTA_R037_DH05_SHORT_PROBE_RELATIVE_ACCEPTANCE_BAR_OWNERSHIP_CHECKPOINT_09Z.json"]
    c10d = by_name["research/delta/reference/DELTA_R037_DH05_PROBE_ATTEMPT_STRICT_BEYOND_CHECKPOINT_10D.json"]
    c10e = by_name["research/delta/reference/DELTA_R037_DH05_PROBE_ATTEMPT_TOUCH_RESET_CHECKPOINT_10E.json"]

    independent_exact_counter = any([
        bool(wp.get("explicit_repeated_same_boundary_attempt_counter_semantic")),
        bool(wp.get("explicit_touch_reset_semantic")),
        bool(wp.get("explicit_strict_prebreak_reset_semantic")),
        bool(r003.get("explicit_attempt_counter_semantic")),
        bool(r006.get("exact_attempt_counter_semantic_documented")),
        bool(r032.get("exact_attempt_counter_semantic_documented")),
    ])

    source_gap = (
        c09a.get("authoritative_producer_bytes_found") is False
        and c09a.get("cleanroom_rebuild_required") is True
    )
    bracket_pass = (
        c10d.get("strict_beyond_candidates_all_worse") is True
        and c10e.get("touch_reset_candidates_all_worse") is True
    )
    whitepaper_constraint = (
        wp.get("probe_age_defined_since_first_cross") is True
        and wp.get("state_machine_is_single_probe_chain") is True
        and wp.get("expired_probes_go_to_EXPIRED") is True
    )

    freeze = bool(
        source_gap
        and bracket_pass
        and whitepaper_constraint
        and not independent_exact_counter
    )

    probe_error = int(c09z["probe_abs_error"])
    total_error = int(c09z["total_funnel_abs_error"])
    trade_error = int(c09z["aggregate_trade_count_abs_error"])

    out = {
        "schema": "delta-r037-dh05-probe-attempt-counter-provenance-decision-10f-v1",
        "status": (
            "COMPLETE_PROVENANCE_LIMITATION_FREEZE"
            if freeze
            else "COMPLETE_PROVENANCE_REVIEW_FURTHER_EVIDENCE_REQUIRED"
        ),
        "unit": "R037_DH05_PROBE_RESIDUAL_ATTEMPT_COUNTER_PROVENANCE_DECISION",
        "raw_ticks_accessed": False,
        "numeric_vector_retune": False,
        "evidence_schema": e["schema"],
        "evidence_cutoff": e["evidence_cutoff"],
        "gates": {
            "authoritative_historical_producer_bytes_missing": source_gap,
            "whitepaper_first_cross_single_chain_constraint": whitepaper_constraint,
            "independent_exact_counter_provenance_found": independent_exact_counter,
            "10d_10e_universal_counter_bracket_pass": bracket_pass,
        },
        "09z_best_reconstruction": {
            "probe_abs_error": probe_error,
            "total_funnel_abs_error": total_error,
            "aggregate_trade_count_abs_error": trade_error,
            "promoted": False,
        },
        "decision": {
            "promote_another_universal_attempt_counter_semantic": False,
            "freeze_09z_attempt_counter_as_best_reconstructible_surrogate": freeze,
            "claim_exact_historical_dh05_parity": False,
            "record_remaining_probe_error_as_provenance_limitation": freeze,
            "remaining_probe_abs_error": probe_error,
            "dh05_stream_disposition": (
                "PROVENANCE_LIMITED_BEST_RECONSTRUCTION_09Z_NON_PROMOTING"
                if freeze
                else "OPEN"
            ),
            "reason": (
                "No surviving independent historical source encodes another exact "
                "universal probe-attempt counter/reset semantic. The original source "
                "bytes remain missing, while 10D and 10E bracket the contact edge and "
                "both alternative universal recuts worsen parity. Additional same-sample "
                "counter recuts would be retrospective fitting rather than reconstruction."
            ),
            "next": (
                "R037_DH02_S11_CLEANROOM_PARITY_RECONSTRUCTION"
                if freeze
                else "R037_DH05_PROBE_RESIDUAL_ATTEMPT_COUNTER_PROVENANCE_DECISION"
            ),
        },
        "august_2026": "SEALED",
        "sorb_integrated_replay_started": False,
        "mql5_authorized": False,
    }

    if freeze and e.get("expected_decision") != (
        "FREEZE_09Z_ATTEMPT_COUNTER_AS_BEST_RECONSTRUCTIBLE_NON_PROMOTING_SURROGATE_"
        "AND_RECORD_449_PROBE_RESIDUAL_AS_PROVENANCE_LIMITATION"
    ):
        raise SystemExit("evidence ledger expected decision mismatch")

    atomic_write_json(args.output, out)
    print(json.dumps(out["decision"], separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

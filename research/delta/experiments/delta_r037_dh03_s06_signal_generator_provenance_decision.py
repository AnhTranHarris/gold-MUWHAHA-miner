"""DELTA R037 DH03-S06 signal-generator residual provenance decision — 13H.

Deterministic provenance-only unit. No raw ticks, threshold fitting, August, SORB,
or MQL5. It decides whether more same-Stage-A semantic recuts remain justified
after 13C-13G, or whether the best source-compatible DH03 reconstruction must be
frozen as provenance-limited.
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

EXPECTED_SCHEMA = "delta-r037-dh03-s06-signal-generator-residual-provenance-evidence-13h-v1"
EXPECTED_VECTOR = "a3a086b7344c"
EXPECTED_DECISION = (
    "FREEZE_13C_STRICT_AS_BEST_RECONSTRUCTIBLE_NON_PROMOTING_SURROGATE_"
    "AND_RECORD_DH03_SIGNAL_GENERATOR_RESIDUAL_AS_PROVENANCE_LIMITATION"
)


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

    e = json.loads(args.evidence.read_text(encoding="utf-8"))
    if e.get("schema") != EXPECTED_SCHEMA:
        raise SystemExit("unexpected 13H evidence schema")
    if e.get("vector_fingerprint") != EXPECTED_VECTOR:
        raise SystemExit("unexpected DH03-S06 vector fingerprint")
    if e.get("raw_ticks_accessed") is not False:
        raise SystemExit("13H must not access raw ticks")
    if e.get("august_2026") != "SEALED":
        raise SystemExit("August must remain SEALED")

    src = e["source_grounding"]
    wp = src["dh03_whitepaper"]
    hp = src["historical_provenance"]
    cp = e["checkpoints"]
    pc = e["provenance_conclusion"]
    target = e["historical_target"]

    c13 = cp["13C"]
    f13 = cp["13F"]
    g13 = cp["13G"]

    gates = {
        "historical_producer_bytes_missing": (
            hp["source_bytes_recovered"] is False
            and hp["output_bytes_recovered"] is False
            and hp["preserved_hashes_and_fingerprints"] is True
        ),
        "whitepaper_exact_reclaim_rearm_algorithm_missing": (
            wp["exact_fast_pivot_algorithm_preserved"] is False
            and wp["exact_reclaim_level_ownership_algorithm_preserved"] is False
            and wp["exact_same_pullback_rearm_algorithm_preserved"] is False
            and wp["exact_pivot_reuse_or_consumption_algorithm_preserved"] is False
        ),
        "13c_reconstructs_economic_scale": (
            abs(float(c13["net_gap"])) < 0.25
            and abs(float(c13["dd_gap"])) < 0.25
            and abs(int(c13["trade_gap"])) <= 50
            and abs(int(c13["raw_win_gap"])) <= 16
        ),
        "13f_brackets_target_activity": (
            int(f13["strict"]["trades"]) < int(target["trades"])
            and int(f13["inherited_first"]["trades"]) > int(target["trades"])
            and float(f13["inherited_first"]["net_profit"]) < float(c13["net_profit"])
        ),
        "13g_edge_and_consumption_rejected": (
            int(g13["best_new"]["trades"]) < int(c13["trades"])
            and int(g13["best_new"]["raw_positive_wins"]) < int(c13["raw_positive_wins"])
            and g13["conclusion"].startswith("literal S5 edge crossing")
        ),
        "independent_exact_algorithm_absent": (
            pc["independent_exact_historical_fast_pivot_rearm_algorithm_found"] is False
        ),
        "same_sample_recuts_exhausted": (
            pc["source_compatible_state_space_materially_bracketed"] is True
            and pc["further_same_sample_semantic_recuts_would_be_retrospective_fitting"] is True
        ),
    }
    if not all(gates.values()):
        raise SystemExit("13H provenance gate mismatch: " + json.dumps(gates, sort_keys=True))

    if e.get("expected_decision") != EXPECTED_DECISION:
        raise SystemExit("13H expected decision mismatch")

    out = {
        "schema": "delta-r037-dh03-s06-signal-generator-residual-provenance-decision-13h-v1",
        "status": "COMPLETE_PROVENANCE_LIMITATION_FREEZE",
        "unit": e["unit"],
        "raw_ticks_accessed": False,
        "numeric_vector_retune": False,
        "vector_fingerprint": e["vector_fingerprint"],
        "gates": gates,
        "historical_target": target,
        "best_reconstructible_surrogate": {
            "profile": pc["best_reconstructible_surrogate"],
            "checkpoint": pc["best_reconstructible_checkpoint"],
            "actual": {
                "signals": int(c13["signals"]),
                "trades": int(c13["trades"]),
                "raw_positive_wins": int(c13["raw_positive_wins"]),
                "gross_profit": float(c13["gross_profit"]),
                "gross_loss": float(c13["gross_loss"]),
                "net_profit": float(c13["net_profit"]),
                "max_balance_drawdown": float(c13["max_balance_drawdown"]),
            },
            "trade_gap": int(c13["trade_gap"]),
            "raw_positive_win_gap": int(c13["raw_win_gap"]),
            "net_gap": float(c13["net_gap"]),
            "drawdown_gap": float(c13["dd_gap"]),
            "promoted_as_historical_truth": False,
        },
        "diagnostic_bound": {
            "profile": "INHERITED_FIRST_ATTEMPT_ONLY",
            "trades": int(f13["inherited_first"]["trades"]),
            "raw_positive_wins": int(f13["inherited_first"]["raw_positive_wins"]),
            "net_profit": float(f13["inherited_first"]["net_profit"]),
            "promoted": False,
        },
        "decision": {
            "run_more_same_sample_dh03_generator_semantic_recuts": False,
            "freeze_general_dh03_semantic": pc["preserve_general_semantic"],
            "freeze_13c_strict_as_best_reconstructible_surrogate": True,
            "preserve_13f_inherited_first_as_diagnostic_bound": True,
            "promote_surrogate_as_historical_truth": False,
            "claim_exact_historical_dh03_parity": False,
            "record_residual_as_provenance_limitation": True,
            "dh03_stream_disposition": pc["dh03_stream_disposition"],
            "reason": (
                "The historical r005 specialist producer/output bytes are unavailable and "
                "the surviving DH03 white paper does not encode the exact fast-pivot, "
                "same-pullback rearm, reclaim ownership, or pivot reuse algorithm. 13C "
                "reconstructs the historical economic scale to within $0.21 net and $0.11 "
                "drawdown while remaining 50 trades and 16 raw-positive wins low. 13F "
                "brackets the target population but its inherited-first alternative worsens "
                "economics, and 13G shows literal edge-cross and one-use pivot semantics "
                "collapse activity. Further Stage-A recuts would be retrospective fitting."
            ),
            "next": e["proposed_next"],
        },
        "august_2026": "SEALED",
        "sorb_integrated_replay_started": False,
        "mql5_authorized": False,
    }

    atomic_write_json(args.output, out)
    print(json.dumps(out["decision"], separators=(",", ":")))


if __name__ == "__main__":
    main()

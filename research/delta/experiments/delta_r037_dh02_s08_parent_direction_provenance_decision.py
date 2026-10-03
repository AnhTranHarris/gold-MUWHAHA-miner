"""DELTA R037 DH02-S08 parent-direction provenance decision — 12C.

Deterministic provenance-only unit. It closes unsupported same-sample parent-context
recuts unless surviving source material independently defines the missing historical
DH01 aggregation/veto algorithm.

No raw ticks. No numeric retuning. No August. No SORB. No MQL5.
"""
from __future__ import annotations
import argparse, json, os, tempfile
from pathlib import Path

EXPECTED_SCHEMA="delta-r037-dh02-s08-parent-direction-provenance-evidence-12c-v1"

def atomic_write_json(path:Path,payload:dict)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp_name=None
    try:
        with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",newline="\n",prefix=f".{path.name}.",suffix=".tmp",dir=path.parent,delete=False) as tmp:
            tmp_name=tmp.name
            json.dump(payload,tmp,indent=2); tmp.write("\n"); tmp.flush(); os.fsync(tmp.fileno())
        os.replace(tmp_name,path); tmp_name=None
    finally:
        if tmp_name is not None:
            try: os.unlink(tmp_name)
            except FileNotFoundError: pass

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--evidence",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    e=json.loads(args.evidence.read_text(encoding="utf-8"))
    if e.get("schema")!=EXPECTED_SCHEMA: raise SystemExit("unexpected evidence schema")
    if e.get("vector_fingerprint")!="7c70b5304ff7": raise SystemExit("unexpected S08 fingerprint")

    ps=e["preserved_sources"]; p=e["provenance_conclusion"]; c12b=e["checkpoint_12b"]
    wins={k:int(v["wins"]) for k,v in c12b["profiles"].items()}
    gates={
      "dh02_requires_parent_context_at_entry": "context rules remain valid" in ps["dh02_whitepaper"]["entry_rule"],
      "s08_vector_requires_dh01_parent_direction": ps["immutable_s08"]["parent_context"]=="DH-01 parent direction",
      "exact_parent_algorithm_missing": (
        ps["dh02_whitepaper"]["exact_parent_aggregation_algorithm_preserved"] is False
        and ps["dh01_whitepaper"]["exact_dh02_s08_parent_veto_algorithm_preserved"] is False
        and ps["r004_prereg"]["exact_dh02_s08_parent_veto_algorithm_preserved"] is False
        and ps["immutable_s08"]["exact_parent_aggregation_algorithm_preserved"] is False
        and ps["historical_r005_specialist_source_bytes_recovered"] is False
        and p["independent_exact_parent_direction_algorithm_found"] is False
      ),
      "12b_all_placements_fail_to_recover_winners": all(v==37 for v in wins.values()),
      "historical_winner_target_is_42": int(e["historical_target"]["raw_positive_wins"])==42,
      "r032_incremental_s08_ownership_is_stable_71": (
        int(e["r032_ownership_fingerprint"]["incremental_s08_owned_entries"])==71
        and int(e["r032_ownership_fingerprint"]["incremental_s08_owned_entries_with_s11_present"])==71
      )
    }
    if not all(gates.values()): raise SystemExit("provenance gate mismatch: "+json.dumps(gates,sort_keys=True))

    out={
      "schema":"delta-r037-dh02-s08-parent-direction-provenance-decision-12c-v1",
      "status":"COMPLETE_PROVENANCE_LIMITATION_FREEZE",
      "unit":e["unit"],
      "raw_ticks_accessed":False,
      "numeric_vector_retune":False,
      "vector_fingerprint":e["vector_fingerprint"],
      "gates":gates,
      "decision":{
        "run_more_same_sample_parent_context_recuts":False,
        "freeze_general_parent_context_semantic":p["preserve_general_semantic"],
        "source_compatible_surrogate":p["source_compatible_surrogate"],
        "promote_surrogate_as_historical_truth":False,
        "claim_exact_historical_s08_parity":False,
        "s08_stream_disposition":p["s08_stream_disposition"],
        "preserve_r032_incremental_ownership_fingerprint":71,
        "reason":"Surviving source material preserves the requirement for DH01 parent context at entry but not the exact historical aggregation/veto algorithm. 12B moves that context requirement across every bounded source-grounded lifecycle placement and all variants remain stuck at 37 winners versus the historical 42. Further same-sample context permutations would be retrospective fitting rather than reconstruction.",
        "next":e["proposed_next"]
      },
      "august_2026":e["august_2026"],
      "sorb_integrated_replay_started":False,
      "mql5_authorized":False
    }
    atomic_write_json(args.output,out)
    print(json.dumps(out["decision"],separators=(",",":")))

if __name__=="__main__":
    main()

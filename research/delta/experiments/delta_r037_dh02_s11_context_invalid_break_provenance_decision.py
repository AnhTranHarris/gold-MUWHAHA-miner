"""DELTA R037 DH02-S11 invalid-context break provenance decision — Checkpoint 11E.

Deterministic provenance gate. No market replay, no threshold tuning, no August access.
It accepts only independently source-supported semantics as frozen historical grammar.
"""
from __future__ import annotations
import argparse, hashlib, json, os, tempfile
from pathlib import Path

EXPECTED_EVIDENCE_SHA256 = None

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_name=None
    try:
        with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",newline="\n",prefix=f".{path.name}.",suffix=".tmp",dir=path.parent,delete=False) as tmp:
            tmp_name=tmp.name
            json.dump(payload,tmp,indent=2)
            tmp.write("\n"); tmp.flush(); os.fsync(tmp.fileno())
        os.replace(tmp_name,path); tmp_name=None
    finally:
        if tmp_name is not None:
            try: os.unlink(tmp_name)
            except FileNotFoundError: pass

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--evidence",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ns=ap.parse_args()
    ev=json.loads(ns.evidence.read_text(encoding="utf-8"))
    if ev.get("schema")!="delta-r037-dh02-s11-context-invalid-break-provenance-evidence-11e-v1":
        raise SystemExit("unexpected evidence schema")
    se=ev["source_evidence"]
    if not (se["armed_requires_context_permission"] and se["broken_transition_requires_armed_event"] and se["no_transition_can_skip_broken"]):
        raise SystemExit("insufficient source support for causal admission principle")
    if se["historical_post_invalid_break_boundary_consumption_rule_preserved"]:
        raise SystemExit("evidence contradiction: consumption rule unexpectedly preserved")
    out={
      "schema":"delta-r037-dh02-s11-context-invalid-break-provenance-decision-11e-v1",
      "status":"COMPLETE_PROVENANCE_DECISION",
      "unit":ev["unit"],
      "decision":{
        "frozen_semantic":"NO_RETROSPECTIVE_VALIDATION_OF_CONFLICT_PERIOD_BREAK",
        "historical_consumption_rule_promoted":False,
        "challenger":"CONFLICT_BREAK_CONSUME_UNTIL_NEW_BOUNDARY",
        "challenger_status":"NON_PROMOTING_SOURCE_COMPATIBLE_CHALLENGER",
        "reason":"surviving state grammar requires valid context before BROKEN, but does not preserve the historical ownership action after an invalid-context qualifying break"
      },
      "checkpoint_11d":ev["checkpoint_11d"],
      "numeric_vector_retune":False,
      "august_accessed":False,
      "next":ev["next_unit"],
      "mql5_authorized":False
    }
    atomic_write_json(ns.output,out)
    print(json.dumps(out["decision"],separators=(",",":")))

if __name__=="__main__":
    main()

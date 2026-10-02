"""DELTA_001 deterministic evidence preflight.

This unit performs no strategy computation. It verifies the registered source/evidence
identities and freezes the minimum metric/data-wall schema used by later DELTA units.
"""
from __future__ import annotations
import json
from pathlib import Path

EXPECTED={
 "hybrid":"7eecb5f1947017a01ce85b2520725de54749e523",
 "logger":"5c7655cd3357f9126e8bffd97c34374dfb29f83e",
 "dukas":{
  1:"d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5",
  2:"ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d",
  3:"814ba35e72f219a58badd806ed5c0f30ef0fb4ffe56a48205d873706513bd177",
  4:"30375098f62aed6cabc32ec6b67c57c20baec9b6d9be1ce0a204e09806c1ec0f",
  5:"3a50e0f1eba3076154238290ec02842cf3744ab192e5c9a2acc1cc07367c6a0d",
  6:"34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2",
  7:"e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7"}}

def main():
 root=Path(__file__).resolve().parents[3]
 registry=json.loads((root/"research/delta/reference/R9_EVIDENCE_REGISTRY.json").read_text())
 duk=json.loads((root/"research/delta/reference/DUKASCOPY_JAN_JUL_SOURCE_MANIFEST.json").read_text())
 func=json.loads((root/"research/delta/reference/R9_MT5_EA_FUNCTIONAL_FAST_REFERENCE.json").read_text())
 real=json.loads((root/"research/delta/reference/R9_REAL_PERFORMANCE_FAST_REFERENCE.json").read_text())
 synth=json.loads((root/"research/delta/reference/R9_SYNTH_PERFORMANCE_FAST_REFERENCE.json").read_text())
 checks={
  "hybrid_identity":registry["r9_mt5"]["hybridgate"]["source_blob_sha"]==EXPECTED["hybrid"]==func["legacy_gamma_inspection"]["hybrid_blob_sha"],
  "logger_identity":registry["r9_mt5"]["ticklogger"]["source_blob_sha"]==EXPECTED["logger"]==func["legacy_gamma_inspection"]["logger_blob_sha"],
  "dukas_hashes":all(x["sha256"]==EXPECTED[x["month"]] for x in duk["months"]),
  "real_ready":real["status"].startswith("AUTHORITATIVE"),
  "synth_ready":synth["status"].startswith("AUTHORITATIVE"),
  "overfit_quarantined":registry["roles"]["R9_OVERFIT_ORACLE"].lower().startswith("quarantined"),
  "august_sealed":registry["roles"]["AUGUST_2026"].lower().startswith("sealed")
 }
 out={"schema":"delta-001-results-v1","pass":all(checks.values()),"checks":checks}
 p=root/"research/delta/checkpoints/DELTA_001_RESULTS.json"; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(out,indent=2)+"\n")
 if not out["pass"]: raise SystemExit(2)
 print(json.dumps(out,indent=2))
if __name__=="__main__": main()

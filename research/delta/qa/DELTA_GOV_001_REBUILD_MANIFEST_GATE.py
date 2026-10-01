#!/usr/bin/env python3
"""DELTA GOV-001 manifest durability gate."""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
STATE=ROOT/"CURRENT_STATE.json"
POLICY=ROOT/"research/delta/governance/DELTA_GOV_001_CAUSAL_DURABLE_MT5_RESEARCH_CONTRACT.md"
TEMPLATE=ROOT/"research/delta/artifacts/DELTA_RESEARCH_UNIT_MANIFEST_TEMPLATE.json"

REQ={"schema","unit_id","status","python_rebuild_ready","mt5_translation_ready",
"missing_required_artifacts","sealed_data_status","trade_count_gate","primary_metrics",
"source_code","helpers","inputs","intermediate_surfaces","models","outputs","qa",
"reconstruction","mt5_translation_contract","human_qa","github_commits","drive_artifacts","verification"}

def die(x):
    print("DELTA_GOV_001 FAIL:",x,file=sys.stderr); raise SystemExit(1)

def load(p):
    try:return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:die(f"{p}: {e}")

def main():
    if not POLICY.exists(): die("policy missing")
    if not TEMPLATE.exists(): die("manifest template missing")
    s=load(STATE)
    if s.get("schema")!="delta-research-status-v1": die("CURRENT_STATE is not DELTA")
    if s.get("branch")!="delta": die("branch cursor is not delta")
    if s.get("beta_lineage_status")!="CLOSED_HISTORICAL": die("BETA must remain closed historical")
    if s.get("august_2026")!="SEALED": die("August must remain SEALED")
    unit=s.get("last_verified_durable_unit")
    if unit=="DELTA_BOOTSTRAP_000":
        print("DELTA_GOV_001 PASS: bootstrap baseline active; future-unit gate armed."); return
    rel=s.get("active_rebuild_manifest_path")
    if not rel: die("missing active_rebuild_manifest_path")
    m=load(ROOT/rel)
    miss=sorted(REQ-set(m))
    if miss: die(f"manifest missing keys {miss}")
    if m.get("unit_id")!=unit: die("manifest unit_id != current durable unit")
    if m.get("python_rebuild_ready") is not True: die("python_rebuild_ready must be true")
    if m.get("missing_required_artifacts"): die("missing_required_artifacts must be empty")
    if not m.get("source_code"): die("source_code must identify producing source")
    if not m.get("outputs"): die("outputs required")
    if not m.get("qa"): die("qa required")
    if not m.get("github_commits"): die("github_commits required")
    tc=m.get("trade_count_gate")
    if not isinstance(tc,dict) or not tc.get("reference_name"): die("trade_count_gate/reference required")
    r=m.get("reconstruction") or {}
    if not r.get("entry_point") or not r.get("timing_semantics"): die("reconstruction contract incomplete")
    v=m.get("verification") or {}
    if v.get("github_readback") is not True or v.get("hashes_verified") is not True: die("GitHub/hash verification incomplete")
    if (m.get("drive_artifacts") or []) and v.get("drive_readback") is not True: die("Drive readback required")
    print("DELTA_GOV_001 PASS:",rel)
if __name__=="__main__": main()

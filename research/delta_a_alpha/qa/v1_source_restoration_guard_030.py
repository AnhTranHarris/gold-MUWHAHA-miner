#!/usr/bin/env python3
"""Fail-closed SOURCE RECOVERY gate for V1, NOT a trading-simulation certificate.

Unlike the historical 024-029 reconstructions, this script NEVER designs or
simulates substitute hourly/native/Watchdog/recovery rules. It verifies source
identity and refuses to call a reconstruction a complete V1 EA.
"""
import argparse
import hashlib
import json
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WHITEPAPER = ROOT / "research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt"
MANIFEST = ROOT / "research/delta_a_alpha/artifacts/DAA_VERTICAL_GRID_SYSTEM_V1_MANIFEST.json"
SPINE = [
    "ordered_ticks",
    "session_specific_grid_geometry",
    "completed_H4_H1_M15_M5_structure",
    "london_overlap_ny_hourly_high_volume_harvesting_plus_separate_asia_geometry",
    "watchdog_regime_renewal",
    "trend_within_trend_native_routing",
    "wrong_direction_recovery",
    "portfolio_heat_capital_governor",
]
LABELS = [
    "LAYER 0 — ORDERED TICK EXECUTION ROOT",
    "LAYER 1 — SESSION-SPECIFIC GRID GEOMETRY",
    "LAYER 2 — COMPLETED MULTI-TIMEFRAME STRUCTURE",
    "LAYER 3 — HOURLY HIGH-VOLUME HARVESTING",
    "LAYER 4 — WATCHDOG / REGIME RENEWAL",
    "LAYER 5 — TREND-WITHIN-TREND NATIVE ROUTING",
    "LAYER 6 — WRONG-DIRECTION RECOVERY",
    "LAYER 7 — PORTFOLIO HEAT / CAPITAL GOVERNOR",
]
SOURCE_SHA = {
    "april_helpers": "1f3ea46dca4889dfc0b5efea6ae10b37672573ab4c8d2f40041d8258851037fc",
    "march_stream": "9b16fe06de5b3f85d2f8ea03eaff661de65d15485fd7cbc6563ba029335b795e",
}
REQUIRED_HELPERS = [
    "apr_campaign_transition_map_136t0_fast.py",
    "apr_transition_rlph_cap_frontier_136t2.py",
    "apr_native_conviction_136d.py",
    "apr_renewal_owner_stream_136s0.py",
    "apr_rule_family_parametric_combine_136v2.py",
    "apr_hierarchical_shadow_context_136x_block.py",
]
def digest(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1048576), b""):
            h.update(b)
    return h.hexdigest()
def validate(whitepaper, manifest, april=None, march=None):
    results = {}
    text = whitepaper.read_text(encoding="utf-8-sig")
    indexes = [text.find(x) for x in LABELS]
    results["full_owner_whitepaper_layers_original_L0_to_L7"] = (
        all(i >= 0 for i in indexes) and indexes == sorted(indexes)
    )
    results["whitepaper_keeps_hourly_and_independent_asia"] = (
        "LAYER 3 — HOURLY HIGH-VOLUME HARVESTING" in text
        and "Asia and London/NY are explicitly different families." in text
    )
    results["whitepaper_keeps_trend_and_failure_conditioned_recovery"] = (
        "The purpose is to allow a lower-timeframe scalping process" in text
        and "Recovery is part of the permanent spine, but generic reversal is forbidden." in text
    )
    results["whitepaper_bans_toxic_sizing"] = (
        "Martingale: prohibited" in text
        and "Loss-dependent sizing: prohibited" in text
    )
    obj = json.loads(manifest.read_text(encoding="utf-8"))
    results["machine_manifest_exact_eight_stage_order"] = obj.get("permanent_spine") == SPINE
    results["main_delta_read_only"] = obj.get("owner_override", {}).get("main_delta") == "READ_ONLY"
    results["original_fallback_preserved"] = obj.get("fallback", {}).get("branch") == "delta-A-alpha-v1-vertical-grid-spine"
    if april:
        results["april_helpers_exact_sha256"] = digest(april) == SOURCE_SHA["april_helpers"]
        with tarfile.open(april, "r:gz") as a:
            names = set(a.getnames())
        results["april_216_exact_files"] = len(names) == 216
        results["april_required_real_helper_bytes"] = all(x in names for x in REQUIRED_HELPERS)
    if march:
        results["march_114_array_archive_sha256"] = digest(march) == SOURCE_SHA["march_stream"]
        import numpy as np
        with np.load(march) as z:
            names = set(z.files)
        results["march_114_named_arrays"] = len(names) == 114
        results["march_full_component_streams"] = all(any(key.startswith(prefix) for key in names) for prefix in ("WDQ_", "NAT_", "HV2_", "ASIA_", "REC1_", "COLD_", "COVQ_"))
    return results
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--whitepaper",type=Path,default=WHITEPAPER)
    ap.add_argument("--manifest",type=Path,default=MANIFEST)
    ap.add_argument("--april",type=Path)
    ap.add_argument("--march",type=Path)
    args=ap.parse_args()
    checks=validate(args.whitepaper,args.manifest,args.april,args.march)
    ok=all(checks.values())
    print(json.dumps({"status":"SOURCE_INTEGRITY_PASS" if ok else "SOURCE_INTEGRITY_FAIL",
                      "checks":checks,
                      "FULL_FUNDED_V1_PARITY_CERTIFIED":False,
                      "note":"Passing this audit never certifies economic/funded L0-L7 replay or MT5."},indent=2))
    raise SystemExit(0 if ok else 2)
if __name__=="__main__":main()

"""DELTA R037 PLSR C01 later-January independent validation — Checkpoint 16B.

Frozen candidate: R037-PLSR-C01_PDH_PDL_S5_RECLAIM.
No Stage-A threshold changes, no PDH/PDL split, no August.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd

import delta_r037_sorb_c04_dual30_independent_validation as val
import delta_r037_plsr_stage_a as plsr

WARMUP_START_MS=1768348800000
HOLDOUT_START_MS=1768737600000
JAN_END_MS=1769904000000
CANDIDATE_ID="R037-PLSR-C01_PDH_PDL_S5_RECLAIM"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    sha=val.base.sha256_file(a.source)
    if sha!=val.base.CANONICAL_JAN_SHA256:
        raise SystemExit("canonical January SHA mismatch: "+sha)

    df=pd.read_csv(a.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
    df=df[(df.timestamp_ms_utc>=WARMUP_START_MS)&(df.timestamp_ms_utc<JAN_END_MS)]
    t=df.timestamp_ms_utc.to_numpy(np.int64)
    if t.size==0 or np.any(t[1:]<t[:-1]):
        raise SystemExit(f"16B chronology mismatch: {t.size}")
    holdout_ticks=int(np.sum(t>=HOLDOUT_START_MS))
    if holdout_ticks<=0:
        raise SystemExit("16B holdout contains no ticks")

    ask,bid=val.base.p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64))
    feat=val.parent.build_parent_features(t,ask,bid)
    streams=val.generate_streams(t,ask,bid)
    d3t,d3s=streams["DH03_S06"]; d5t,d5s=streams["DH05_S06"]
    s11t,s11s=streams["DH02_S11"]; s08t,s08s=streams["DH02_S08"]

    zi=np.empty(0,np.int64); zs=np.empty(0,np.int8)
    p=val.pack_sorb(val.run_integrated_sorb(
        t,ask,bid,feat["impulse250"],feat["h1_netatr"],feat["m30_netatr"],
        d3t,d3s,d5t,d5s,s11t,s11s,s08t,s08s,zi,zs,zs,
        1,1,1,1,1,HOLDOUT_START_MS))

    all_props=plsr.generate_proposals(t,ask,bid,CANDIDATE_ID)
    props=[x for x in all_props if x.decision_index<len(t) and int(t[x.decision_index])>=HOLDOUT_START_MS]
    sp=plsr.supply(props)
    ep=[x for x in props if x.eligible]
    ii=np.asarray([x.decision_index for x in ep],np.int64)
    ss=np.asarray([x.side for x in ep],np.int8)
    sk=np.asarray([1 if x.level_kind=="PDH" else 2 for x in ep],np.int8)

    c=val.pack_sorb(val.run_integrated_sorb(
        t,ask,bid,feat["impulse250"],feat["h1_netatr"],feat["m30_netatr"],
        d3t,d3s,d5t,d5s,s11t,s11s,s08t,s08s,ii,ss,sk,
        1,1,1,1,1,HOLDOUT_START_MS))
    d=val.decision(p,c,sp)

    contrib=c.pop("sorb_session_contribution")
    c["plsr_entries"]=c.pop("sorb_entries")
    c["plsr_net"]=c.pop("sorb_net")
    c["plsr_level_contribution"]={"PDH":contrib["LONDON"],"PDL":contrib["COMEX_GOLD"]}
    d["incremental_net_per_plsr_entry"]=d.pop("incremental_net_per_sorb_entry")
    validation_pass=bool(
        sp["proposals"]>=6 and sp["distinct_days"]>=4 and c["plsr_entries"]>=5
        and d["combined_trade_count_not_lower"] and d["winner_or_quality_gate_ok"]
        and d["net_delta"]>=0.0 and d["drawdown_deterioration_within_1pct"]
    )

    out={
      "schema":"delta-r037-plsr-c01-independent-validation-16b-v1",
      "status":"COMPLETE_INDEPENDENT_VALIDATION",
      "unit":"R037_PLSR_C01_INDEPENDENT_LATER_JAN_VALIDATION",
      "candidate":CANDIDATE_ID,
      "parent_checkpoint":"R037_PLSR_STAGE_A_SCREEN_CHECKPOINT_16A",
      "surrogate_parent":"14A_BACKBONE_FIRST_C03_WITH_FROZEN_PROVENANCE_LIMITED_SPECIALISTS",
      "promotable":False,
      "source_sha256":sha,
      "surface":"DUKAS_COINEXX_LIKE_P75",
      "warmup_start_ms":WARMUP_START_MS,
      "holdout_start_ms":HOLDOUT_START_MS,
      "holdout_end_ms_exclusive":JAN_END_MS,
      "loaded_ticks":int(t.size),
      "holdout_ticks":holdout_ticks,
      "candidate_retuned":False,
      "posthoc_level_split":False,
      "august_accessed":False,
      "parent_control":p,
      "supply":sp,
      "combined":c,
      "decision":{
        **d,
        "independent_validation_pass":validation_pass,
        "next":"R037_PLSR_C01_MONTH_BY_MONTH_SURROGATE_VALIDATION" if validation_pass else "RETIRE_PLSR_C01_AND_HARVEST_NEXT_INDEPENDENT_ENTRY_SOURCE"
      },
      "mql5_authorized":False
    }
    val.base.atomic_write_json(a.output,out)
    print(json.dumps({
      "supply":sp,
      "parent":{"trades":p["trades"],"official_wins":p["official_wins"],"net_profit":p["net_profit"],"max_equity_drawdown":p["max_equity_drawdown"]},
      "combined":{"trades":c["trades"],"official_wins":c["official_wins"],"net_profit":c["net_profit"],"max_equity_drawdown":c["max_equity_drawdown"],"plsr_entries":c["plsr_entries"],"plsr_net":c["plsr_net"],"levels":c["plsr_level_contribution"]},
      "decision":out["decision"]
    },separators=(",",":")))

if __name__=="__main__": main()

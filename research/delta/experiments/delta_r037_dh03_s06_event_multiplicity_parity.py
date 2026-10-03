"""DELTA R037 DH03-S06 pullback-event multiplicity/reset parity — Checkpoint 13C.

Research-only bounded semantic diagnostic. No numeric retuning.
13B S5 reclaim timing is frozen. This unit changes only post-signal event lifecycle:
consume the pullback episode vs causally rearm attempts inside the still-valid original
pullback until parent/structural invalidation or original max-pullback age.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

import delta_r037_dh02_s08_cleanroom_parity as base
import delta_r037_dh03_s06_structure as structure
import delta_r037_dh03_s06_event_multiplicity_engine as engine

FP="a3a086b7344c"
TARGET={
    "trades":1563,
    "raw_positive_wins":690,
    "gross_profit":151.82,
    "gross_loss":-490.75,
    "net_profit":-338.93,
    "max_balance_drawdown":339.25,
}

PROFILES=(
    ("POST_PULLBACK_SINGLE_ENTRY_CONTROL",0,0),
    ("POST_PULLBACK_REARM_FRESH_EXHAUSTION",0,1),
    ("POST_PULLBACK_REARM_PERSISTENT_EXHAUSTION",0,2),
    ("POST_PULLBACK_REARM_NEW_ADVERSE_THEN_EXHAUSTION",0,3),
    ("ANY_CAUSAL_REARM_FRESH_EXHAUSTION",1,1),
    ("ANY_CAUSAL_REARM_PERSISTENT_EXHAUSTION",1,2),
)

def score(actual):
    er={q:abs(actual[q]-TARGET[q]) for q in TARGET}
    sc=(100.0*er["trades"]+25.0*er["raw_positive_wins"]+
        er["gross_profit"]+er["gross_loss"]+er["net_profit"]+er["max_balance_drawdown"])
    return er,float(sc)

def episode_metrics(ids):
    if ids.size==0:
        return {
            "unique_signal_episodes":0,
            "multi_signal_episodes":0,
            "max_signals_per_episode":0,
            "signals_per_signal_episode":0.0,
        }
    _,counts=np.unique(ids,return_counts=True)
    return {
        "unique_signal_episodes":int(counts.size),
        "multi_signal_episodes":int(np.sum(counts>1)),
        "max_signals_per_episode":int(np.max(counts)),
        "signals_per_signal_episode":float(ids.size/counts.size),
    }

def pack(st,ss,se,c,x):
    a={
        "signals":int(len(st)),
        "signal_sha256":base.signal_sha(st,ss,se),
        "pullback_episodes":int(c[0]),
        "exhaustion":int(c[1]),
        "reclaim":int(c[2]),
        "reacceleration_signal":int(c[3]),
        "parent_invalid":int(c[4]),
        "structural_invalid":int(c[5]),
        "expired":int(c[6]),
        "depth_ready_observations":int(c[7]),
        "countereff_ready_observations":int(c[8]),
        "no_new_extreme_ready_observations":int(c[9]),
        "pivot_unavailable_observations":int(c[10]),
        "rearms_after_signal":int(c[11]),
        "new_adverse_retry_satisfied":int(c[12]),
        "trades":int(x[0]),
        "raw_positive_wins":int(x[1]),
        "official_wins":int(x[2]),
        "gross_profit":float(x[3]),
        "gross_loss":float(x[4]),
        "net_profit":float(x[5]),
        "max_balance_drawdown":float(x[6]),
    }
    a.update(episode_metrics(se))
    a["signals_suppressed_by_one_position_ledger"]=int(a["signals"]-a["trades"])
    er,sc=score(a)
    return {"actual":a,"abs_error":er,"parity_score":sc}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--evidence",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()

    ev=json.loads(a.evidence.read_text(encoding="utf-8"))
    if ev.get("schema")!="delta-r037-dh03-s06-pullback-event-multiplicity-evidence-13c-v1":
        raise SystemExit("13C evidence schema mismatch")
    if ev["vector"]["fingerprint"]!=FP:
        raise SystemExit("13C vector fingerprint mismatch")

    sh=base.sha256_file(a.source)
    if sh!=base.CANONICAL_JAN_SHA256:
        raise SystemExit("canonical January SHA mismatch")

    df=pd.read_csv(
        a.source,compression="gzip",
        usecols=["timestamp_ms_utc","ask_raw","bid_raw"],
        dtype=np.int64,
    )
    df=df[df.timestamp_ms_utc<base.STAGE_A_END_MS]
    t=df.timestamp_ms_utc.to_numpy(np.int64)
    if len(t)!=4_205_709:
        raise SystemExit(f"Stage-A tick mismatch: {len(t)}")

    ask,bid=base.p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64))
    mid=ask+bid

    b5=base.bars(t,mid,5_000)
    b15=base.bars(t,mid,15_000)
    b30=base.bars(t,mid,30_000)
    m5=base.bars(t,mid,300_000)
    m15=base.bars(t,mid,900_000)
    m30=base.bars(t,mid,1_800_000)

    e5=base.signed_eff(b5,4)
    e15=base.signed_eff(b15,4)
    e30=base.signed_eff(b30,4)
    a5=base.atr14(m5)

    pe,ps,pdir,li,si=structure.parent_series(m15,m30)
    phi,plo,pht,plt=structure.latest_fast_pivots(b15)

    profiles={}
    for pname,pivot_policy,rearm_policy in PROFILES:
        st,ss,se,c=engine.detect(
            t,mid,
            b5["end_ms"],b5["close"],e5,
            b15["end_ms"],b15["high"],b15["low"],b15["close"],e15,
            b30["end_ms"],e30,
            m5["end_ms"],a5,
            pe,ps,li,si,
            phi,plo,pht,plt,
            pivot_policy,rearm_policy,
        )
        x=base.execute_r9_lifecycle(t,ask,bid,st,ss)
        profiles[pname]=pack(st,ss,se,c,x)

    ctrl=profiles["POST_PULLBACK_SINGLE_ENTRY_CONTROL"]["actual"]
    if not (
        ctrl["signals"]==783
        and ctrl["trades"]==783
        and ctrl["raw_positive_wins"]==363
        and ctrl["pullback_episodes"]==1402
        and ctrl["exhaustion"]==940
        and ctrl["reclaim"]==790
        and ctrl["signal_sha256"]=="5c569c82ea7e94a9497220b28eb480761bf6c9ee5da1d0b03ac3e27c00bb259b"
    ):
        raise SystemExit("CONTROL_13B fingerprint mismatch: "+json.dumps(ctrl,sort_keys=True))

    order=sorted((p[0] for p in PROFILES),key=lambda z:profiles[z]["parity_score"])
    lead=order[0]
    q=profiles[lead]["actual"]
    exact=(
        q["trades"]==TARGET["trades"]
        and q["raw_positive_wins"]==TARGET["raw_positive_wins"]
        and all(abs(q[k]-TARGET[k])<0.011 for k in ("gross_profit","gross_loss","net_profit","max_balance_drawdown"))
    )

    base_trades=ctrl["trades"]
    deficit=max(1,TARGET["trades"]-base_trades)
    closure=(q["trades"]-base_trades)/deficit

    out={
        "schema":"delta-r037-dh03-s06-pullback-event-multiplicity-parity-13c-v1",
        "status":"COMPLETE_EXACT_PARITY" if exact else "COMPLETE_EVENT_MULTIPLICITY_QA_PARITY_NOT_YET",
        "unit":"R037_DH03_S06_PULLBACK_EVENT_MULTIPLICITY_AND_RESET_PARITY_RECONSTRUCTION",
        "source_sha256":sh,
        "stage_a_ticks":int(len(t)),
        "surface":"DUKAS_COINEXX_LIKE_P75",
        "vector_fingerprint":FP,
        "numeric_vector_retune":False,
        "august_accessed":False,
        "profiles":profiles,
        "ranking":order,
        "finding":{
            "leading_profile":lead,
            "control_13b_reproduced":True,
            "exact_historical_parity":exact,
            "target":TARGET,
            "activity_deficit_closed_fraction_vs_13b_control":float(closure),
            "next":ev["next_if_exact"] if exact else ev["next_if_material_nonexact"],
        },
        "mql5_authorized":False,
    }
    base.atomic_write_json(a.output,out)
    print(json.dumps(out["finding"],separators=(",",":")))

if __name__=="__main__":
    main()

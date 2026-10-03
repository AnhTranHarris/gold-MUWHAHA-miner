"""DELTA R037 DH03-S06 event identity / rearm-boundary parity — Checkpoint 13F.

Frozen 13C/13D/13E thresholds and execution mechanics. This bounded unit changes
only causal S15 reclaim-pivot ownership across the original pullback and its
rearmed attempts. No numeric tuning.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

import delta_r037_dh02_s08_cleanroom_parity as base
import delta_r037_dh03_s06_structure as structure
import delta_r037_dh03_s06_attempt_admission_parity as admission13d
import delta_r037_dh03_s06_pending_validity_parity as pending13e
import delta_r037_dh03_s06_event_identity_rearm_engine as engine

FP="a3a086b7344c"
EXPECTED_STRICT_SIGNALS=1586
EXPECTED_STRICT_SHA="261b6ad5a1cab4dd4378ec40af7fdde4e5178e82694089b3bf2a28bc6bebfdea"
TARGET={
    "trades":1563,
    "raw_positive_wins":690,
    "gross_profit":151.82,
    "gross_loss":-490.75,
    "net_profit":-338.93,
    "max_balance_drawdown":339.25,
}
PROFILES=(
    "POST_ORIGINAL_PULLBACK_CONTROL",
    "ANY_CAUSAL_DIAGNOSTIC",
    "INHERITED_FIRST_ATTEMPT_ONLY",
    "INHERITED_FIRST_THEN_POST_REARM",
    "START_LATCH_FIRST_ATTEMPT",
)

def score(actual):
    er={k:abs(actual[k]-TARGET[k]) for k in TARGET}
    sc=(100.0*er["trades"]+25.0*er["raw_positive_wins"]+
        er["gross_profit"]+er["gross_loss"]+er["net_profit"]+er["max_balance_drawdown"])
    return er,float(sc)

def pack_drop(x,signals,sigsha):
    a={
        "generator_signals":int(signals),"signal_sha256":sigsha,
        "trades":int(x[0]),"raw_positive_wins":int(x[1]),"official_wins":int(x[2]),
        "gross_profit":float(x[3]),"gross_loss":float(x[4]),"net_profit":float(x[5]),
        "max_balance_drawdown":float(x[6]),"immediate_admissions":int(x[7]),
        "rejected_while_occupied":int(x[8]),"unexecuted_generator_signals":int(signals-int(x[0])),
    }
    er,sc=score(a)
    return {"actual":a,"abs_error":er,"parity_score":sc}

def pack_pending(x,signals,sigsha):
    a={
        "generator_signals":int(signals),"signal_sha256":sigsha,
        "trades":int(x[0]),"raw_positive_wins":int(x[1]),"official_wins":int(x[2]),
        "gross_profit":float(x[3]),"gross_loss":float(x[4]),"net_profit":float(x[5]),
        "max_balance_drawdown":float(x[6]),"immediate_admissions":int(x[7]),
        "pending_created":int(x[8]),"pending_admitted_after_observation":int(x[9]),
        "pending_invalid_parent":int(x[10]),"pending_invalid_structure":int(x[11]),
        "pending_invalid_age":int(x[12]),"signal_events_while_occupied":int(x[13]),
    }
    a["pending_invalid_total"]=a["pending_invalid_parent"]+a["pending_invalid_structure"]+a["pending_invalid_age"]
    a["unexecuted_generator_signals"]=a["generator_signals"]-a["trades"]
    er,sc=score(a)
    return {"actual":a,"abs_error":er,"parity_score":sc}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--evidence",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()

    ev=json.loads(a.evidence.read_text(encoding="utf-8"))
    if ev.get("schema")!="delta-r037-dh03-s06-pending-event-identity-rearm-boundary-evidence-13f-v1":
        raise SystemExit("13F evidence schema mismatch")

    sh=base.sha256_file(a.source)
    if sh!=base.CANONICAL_JAN_SHA256:
        raise SystemExit("canonical January SHA mismatch")

    df=pd.read_csv(a.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
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
    for mode,pname in enumerate(PROFILES):
        st,ss,se,c,evstart,evend,evreason,evside=engine.detect(
            t,mid,b5["end_ms"],b5["close"],e5,
            b15["end_ms"],b15["high"],b15["low"],b15["close"],e15,
            b30["end_ms"],e30,m5["end_ms"],a5,
            pe,ps,li,si,phi,plo,pht,plt,mode,
        )
        sigsha=base.signal_sha(st,ss,se)
        xd=admission13d.admit_attempt_policy(t,ask,bid,st,ss,se,0)
        xp=pending13e.admit_with_validity(t,ask,bid,st,ss,se,evend,evreason,3)
        profiles[pname]={
            "signal_count":int(st.size),
            "signal_sha256":sigsha,
            "event_funnel":{
                "pullbacks":int(c[0]),"exhaustion":int(c[1]),"reclaim":int(c[2]),"signals":int(c[3]),
                "parent_invalid":int(c[4]),"structural_invalid":int(c[5]),"expired":int(c[6]),
                "rearms_after_signal":int(c[11]),"inherited_reclaims":int(c[12]),
                "post_original_reclaims":int(c[13]),"post_rearm_reclaims":int(c[14]),
                "start_latched_reclaims":int(c[15]),
            },
            "episode_end_reasons":{
                "parent_opposition":int(np.sum(evreason==1)),
                "structural_invalidation":int(np.sum(evreason==2)),
                "max_age_expiry":int(np.sum(evreason==3)),
                "active_at_stage_a_end":int(np.sum(evreason==0))-1,
            },
            "drop_occupied":pack_drop(xd,st.size,sigsha),
            "full_event_pending_secondary":pack_pending(xp,st.size,sigsha),
        }

    ctrl=profiles["POST_ORIGINAL_PULLBACK_CONTROL"]
    ca=ctrl["drop_occupied"]["actual"]
    if not (
        ctrl["signal_count"]==EXPECTED_STRICT_SIGNALS and ctrl["signal_sha256"]==EXPECTED_STRICT_SHA
        and ca["trades"]==1513 and ca["raw_positive_wins"]==674 and ca["official_wins"]==661
        and abs(ca["gross_profit"]-137.12)<1e-8 and abs(ca["gross_loss"]+476.26)<1e-8
        and abs(ca["net_profit"]+339.14)<1e-8
    ):
        raise SystemExit("13C strict control drift: "+json.dumps(ctrl,sort_keys=True))

    anyc=profiles["ANY_CAUSAL_DIAGNOSTIC"]
    aa=anyc["drop_occupied"]["actual"]
    if not (
        anyc["signal_count"]==1748 and aa["trades"]==1672 and aa["raw_positive_wins"]==749
        and abs(aa["gross_profit"]-151.25)<1e-8 and abs(aa["gross_loss"]+522.89)<1e-8
        and abs(aa["net_profit"]+371.64)<1e-8
    ):
        raise SystemExit("13C any-causal control drift: "+json.dumps(anyc,sort_keys=True))

    primary_order=sorted(PROFILES,key=lambda n:profiles[n]["drop_occupied"]["parity_score"])
    source_candidates=PROFILES[2:]
    candidate_order=sorted(source_candidates,key=lambda n:profiles[n]["drop_occupied"]["parity_score"])
    lead=candidate_order[0]
    q=profiles[lead]["drop_occupied"]["actual"]
    exact=(
        q["trades"]==TARGET["trades"] and q["raw_positive_wins"]==TARGET["raw_positive_wins"]
        and all(abs(q[k]-TARGET[k])<0.011 for k in ("gross_profit","gross_loss","net_profit","max_balance_drawdown"))
    )
    ctrl_gap=abs(ca["trades"]-TARGET["trades"])
    lead_gap=abs(q["trades"]-TARGET["trades"])
    material_nonexact=(lead_gap<ctrl_gap and profiles[lead]["drop_occupied"]["parity_score"]<ctrl["drop_occupied"]["parity_score"])

    out={
        "schema":"delta-r037-dh03-s06-event-identity-rearm-boundary-parity-13f-v1",
        "status":"COMPLETE_EXACT_PARITY" if exact else ("COMPLETE_MATERIAL_EVENT_IDENTITY_CLUE_FULL_PARITY_NOT_YET" if material_nonexact else "COMPLETE_EVENT_IDENTITY_QA_NO_MATERIAL_PARITY_GAIN"),
        "unit":"R037_DH03_S06_PENDING_EVENT_IDENTITY_AND_REARM_BOUNDARY_PARITY_RECONSTRUCTION",
        "source_sha256":sh,"stage_a_ticks":int(len(t)),"surface":"DUKAS_COINEXX_LIKE_P75",
        "vector_fingerprint":FP,"numeric_vector_retune":False,"generator_threshold_changed":False,"august_accessed":False,
        "profiles":profiles,"primary_drop_ranking":primary_order,"source_candidate_ranking":candidate_order,
        "finding":{
            "leading_source_candidate":lead,
            "leading_trade_gap":int(q["trades"]-TARGET["trades"]),
            "leading_raw_win_gap":int(q["raw_positive_wins"]-TARGET["raw_positive_wins"]),
            "strict_control_trade_gap":int(ca["trades"]-TARGET["trades"]),
            "exact_historical_parity":exact,
            "material_nonexact":material_nonexact,
            "target":TARGET,
            "next":ev["next_if_exact"] if exact else (ev["next_if_material_nonexact"] if material_nonexact else ev["next_if_negative"]),
        },
        "integrated_r037_replay_started":False,"mql5_authorized":False,
    }
    base.atomic_write_json(a.output,out)
    print(json.dumps(out["finding"],separators=(",",":")))

if __name__=="__main__":
    main()

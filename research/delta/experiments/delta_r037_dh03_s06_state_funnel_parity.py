"""DELTA R037 DH03-S06 state-funnel semantic parity — Checkpoint 13B.

Bounded diagnostic. 13A is reproduced as a hard control. The only tested change is
LOCAL_RECLAIM timing/level ownership under the frozen S06 vector:
- control: completed S15 close through S15 pivot (13A);
- candidates: completed S5 close through causally known S15 pivot.

No numeric threshold retuning, no August, no SORB, no MQL5.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd
import delta_r037_dh02_s08_cleanroom_parity as base
import delta_r037_dh03_s06_structure as structure
import delta_r037_dh03_s06_engine as engine13a
import delta_r037_dh03_s06_state_funnel_engine as engine13b

FP="a3a086b7344c"
TARGET={"trades":1563,"raw_positive_wins":690,"gross_profit":151.82,"gross_loss":-490.75,"net_profit":-338.93,"max_balance_drawdown":339.25}
PROFILES=(
    "CONTROL_13A_S15_CLOSE_RECLAIM",
    "S5_RECLAIM_POST_PULLBACK_PIVOT",
    "S5_RECLAIM_ANY_CAUSAL_PIVOT",
    "S5_RECLAIM_FROZEN_AT_EXHAUSTION",
)

def score(actual):
    er={q:abs(actual[q]-TARGET[q]) for q in TARGET}
    sc=100*er["trades"]+25*er["raw_positive_wins"]+er["gross_profit"]+er["gross_loss"]+er["net_profit"]+er["max_balance_drawdown"]
    return er,float(sc)

def pack(st,ss,se,c,x,extended=False):
    a={
        "signals":int(len(st)),
        "signal_sha256":base.signal_sha(st,ss,se),
        "pullbacks":int(c[0]),
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
        "trades":int(x[0]),
        "raw_positive_wins":int(x[1]),
        "official_wins":int(x[2]),
        "gross_profit":float(x[3]),
        "gross_loss":float(x[4]),
        "net_profit":float(x[5]),
        "max_balance_drawdown":float(x[6]),
    }
    if extended:
        a["frozen_pivot_available_at_exhaustion"]=int(c[11])
        a["frozen_pivot_unavailable_at_exhaustion"]=int(c[12])
    er,sc=score(a)
    return {"actual":a,"abs_error":er,"parity_score":sc}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--evidence",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    ev=json.loads(a.evidence.read_text())
    if ev.get("schema")!="delta-r037-dh03-s06-state-funnel-evidence-13b-v1" or ev["vector"]["fingerprint"]!=FP:
        raise SystemExit("13B evidence mismatch")
    sh=base.sha256_file(a.source)
    if sh!=base.CANONICAL_JAN_SHA256:
        raise SystemExit("canonical January SHA mismatch")
    df=pd.read_csv(a.source,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
    df=df[df.timestamp_ms_utc<base.STAGE_A_END_MS]
    t=df.timestamp_ms_utc.to_numpy(np.int64)
    if len(t)!=4205709:
        raise SystemExit("Stage-A tick mismatch")
    ask,bid=base.p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64))
    mid=ask+bid
    b5=base.bars(t,mid,5000);b15=base.bars(t,mid,15000);b30=base.bars(t,mid,30000)
    m5=base.bars(t,mid,300000);m15=base.bars(t,mid,900000);m30=base.bars(t,mid,1800000)
    e5=base.signed_eff(b5,4);e15=base.signed_eff(b15,4);e30=base.signed_eff(b30,4);a5=base.atr14(m5)
    pe,ps,pdir,li,si=structure.parent_series(m15,m30)
    phi,plo,pht,plt=structure.latest_fast_pivots(b15)

    profiles={}

    st,ss,se,c=engine13a.detect(
        t,mid,b5["end_ms"],b5["close"],e5,
        b15["end_ms"],b15["high"],b15["low"],b15["close"],e15,
        b30["end_ms"],e30,m5["end_ms"],a5,pe,ps,pdir,li,si,phi,plo,pht,plt,1
    )
    x=base.execute_r9_lifecycle(t,ask,bid,st,ss)
    profiles[PROFILES[0]]=pack(st,ss,se,c,x,False)
    ctrl=profiles[PROFILES[0]]["actual"]
    if not (
        ctrl["signals"]==709 and ctrl["trades"]==709 and ctrl["raw_positive_wins"]==302
        and ctrl["pullbacks"]==1369 and ctrl["exhaustion"]==906 and ctrl["reclaim"]==722
        and ctrl["signal_sha256"]=="67d456b871d3c6b31b59e8bb546fb42a72f3890ec61f5e343eae28109d878bf3"
    ):
        raise SystemExit("CONTROL_13A fingerprint mismatch: "+json.dumps(ctrl,sort_keys=True))

    for pi,pname in enumerate(PROFILES[1:]):
        st,ss,se,c=engine13b.detect(
            t,mid,b5["end_ms"],b5["close"],e5,
            b15["end_ms"],b15["high"],b15["low"],b15["close"],e15,
            b30["end_ms"],e30,m5["end_ms"],a5,pe,ps,li,si,phi,plo,pht,plt,pi
        )
        x=base.execute_r9_lifecycle(t,ask,bid,st,ss)
        profiles[pname]=pack(st,ss,se,c,x,True)

    order=sorted(PROFILES,key=lambda z:profiles[z]["parity_score"])
    lead=order[0]
    q=profiles[lead]["actual"]
    exact=q["trades"]==TARGET["trades"] and q["raw_positive_wins"]==TARGET["raw_positive_wins"] and all(abs(q[k]-TARGET[k])<.011 for k in ("gross_profit","gross_loss","net_profit","max_balance_drawdown"))

    control_trades=profiles[PROFILES[0]]["actual"]["trades"]
    deficit=max(1,TARGET["trades"]-control_trades)
    closure=(q["trades"]-control_trades)/deficit

    out={
        "schema":"delta-r037-dh03-s06-state-funnel-parity-13b-v1",
        "status":"COMPLETE_EXACT_PARITY" if exact else "COMPLETE_STATE_FUNNEL_QA_PARITY_NOT_YET",
        "unit":"R037_DH03_S06_STATE_FUNNEL_SEMANTICS_PARITY_RECONSTRUCTION",
        "source_sha256":sh,
        "stage_a_ticks":int(len(t)),
        "surface":"DUKAS_COINEXX_LIKE_P75",
        "vector_fingerprint":FP,
        "numeric_vector_retune":False,
        "august_accessed":False,
        "source_grounded_transition":"LOCAL_RECLAIM uses completed S5 close through causally known S15 pivot/reclaim level",
        "profiles":profiles,
        "ranking":order,
        "finding":{
            "leading_profile":lead,
            "control_reproduced":True,
            "exact_historical_parity":exact,
            "target":TARGET,
            "activity_deficit_closed_fraction_vs_13a":float(closure),
            "next":ev["next_if_exact"] if exact else ev["next_if_nonexact_localized"]
        },
        "mql5_authorized":False
    }
    base.atomic_write_json(a.output,out)
    print(json.dumps(out["finding"],separators=(",",":")))

if __name__=="__main__":
    main()

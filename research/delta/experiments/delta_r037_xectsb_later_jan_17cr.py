"""R037 XECTSB 17CR: unchanged M15 leader independent later-January validation."""
from __future__ import annotations
import argparse, hashlib, json, time
from pathlib import Path
import numpy as np
import pandas as pd
import delta_r037_xectsb_stage_a_17cp_17cq as base

PARENT_SHA256 = "c26dc710879a86b9447dfaf2e236c4f3621151a3ab2a62d35aef8f34f44ae03e"
PREREG_COMMIT = "11bb98ec46eaf2d30e1a8bed872b696c0abd1922"
WARMUP_START = 1768348800000
ECON_START = 1768737600000
HOLD_END = 1769904000000
TF = 900000
EXPECTED_CONTROL = {"trades":20,"distinct_days":10,"official_wins":11,"direct_net_usd":0.68}

def sha256_file(p: Path) -> str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda:f.read(1<<20), b""):
            h.update(block)
    return h.hexdigest()

def sigs_window(t,a,b,z,economic_start,end_exclusive):
    c,h,l,e=z["c"],z["h"],z["l"],z["e"]
    f=base.ema(c,9);s=base.ema(c,21)
    ix=[];sd=[]
    g={"crosses":0,"bull":0,"bear":0,"resets":0,"touches":0,"bots":0,
       "enters":0,"prewindow_entries":0,"spread_rejects":0}
    st=0;side=sw=th=tl=ck=tk=bk=0
    for k in range(21,len(c)):
        if e[k]>end_exclusive:
            break
        up=f[k-1]<=s[k-1] and f[k]>s[k]
        dn=f[k-1]>=s[k-1] and f[k]<s[k]
        if up or dn:
            if st in (1,2,3):
                g["resets"]+=1
            side=1 if up else -1
            sw=int(np.max(h[k-10:k]) if side>0 else np.min(l[k-10:k]))
            st=1;ck=k;g["crosses"]+=1
            g["bull" if side>0 else "bear"]+=1
            continue
        if st==1 and k>ck:
            if l[k]<=f[k]<=h[k]:
                th=int(h[k]);tl=int(l[k]);tk=k;st=2;g["touches"]+=1
            continue
        if st==2 and k>tk:
            if (side>0 and h[k]>th) or (side<0 and l[k]<tl):
                bk=k;st=3;g["bots"]+=1
            continue
        if st==3 and k>bk and ((side>0 and c[k]>sw) or (side<0 and c[k]<sw)):
            j=int(np.searchsorted(t,int(e[k]),side="left"))
            if j<len(t) and t[j]<end_exclusive:
                if t[j] < economic_start:
                    g["prewindow_entries"]+=1
                elif a[j]-b[j] <= base.MS:
                    ix.append(j);sd.append(side);g["enters"]+=1
                else:
                    g["spread_rejects"]+=1
            st=4
    return np.asarray(ix,np.int64),np.asarray(sd,np.int8),g

def control_replay(df):
    d=df[(df.timestamp_ms_utc>=base.START)&(df.timestamp_ms_utc<base.END)]
    t=d.timestamp_ms_utc.to_numpy(np.int64)
    if len(t)!=4205709 or np.any(t[1:]<t[:-1]):
        raise SystemExit("control chronology mismatch")
    a,b=base.p75(t,d.ask_raw.to_numpy(np.int64),d.bid_raw.to_numpy(np.int64))
    ix,sd,diag=base.sigs(t,a,b,base.bars(t,b,TF))
    metrics,_=base.pack(ix,sd,t,a,b)
    actual={k:metrics[k] for k in EXPECTED_CONTROL}
    if actual != EXPECTED_CONTROL:
        raise SystemExit("Stage-A control mismatch: "+json.dumps(actual,sort_keys=True))
    return metrics,diag,len(t)

def holdout_replay(df):
    d=df[(df.timestamp_ms_utc>=WARMUP_START)&(df.timestamp_ms_utc<HOLD_END)]
    t=d.timestamp_ms_utc.to_numpy(np.int64)
    if len(t)==0 or np.any(t[1:]<t[:-1]):
        raise SystemExit("holdout chronology mismatch")
    a,b=base.p75(t,d.ask_raw.to_numpy(np.int64),d.bid_raw.to_numpy(np.int64))
    ix,sd,diag=sigs_window(t,a,b,base.bars(t,b,TF),ECON_START,HOLD_END)
    metrics,_=base.pack(ix,sd,t,a,b)
    gate={
        "minimum_trades_10":metrics["trades"]>=10,
        "minimum_distinct_days_5":metrics["distinct_days"]>=5,
        "direct_net_positive":metrics["direct_net_usd"]>0
    }
    gate["validation_pass"]=all(gate.values())
    return metrics,diag,gate,len(t)

def main():
    st=time.monotonic()
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    parent_path=Path(base.__file__).resolve()
    parent_sha=sha256_file(parent_path)
    if parent_sha!=PARENT_SHA256:
        raise SystemExit(f"parent producer SHA mismatch: {parent_sha}")

    source_sha=sha256_file(args.source)
    if source_sha!=base.SHA:
        raise SystemExit(f"canonical January SHA mismatch: {source_sha}")

    df=pd.read_csv(args.source,compression="gzip",
                   usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)

    cm,cd,ct=control_replay(df)
    hm,hd,hg,ht=holdout_replay(df)

    out={
        "schema":"delta-r037-xectsb-later-jan-17cr-v1",
        "status":"COMPLETE_INDEPENDENT_LATER_JAN_VALIDATION",
        "unit":"R037_XECTSB_LEADER_INDEPENDENT_LATER_JAN_VALIDATION_CHECKPOINT_17CR",
        "family":"R037-XECTSB-v1",
        "candidate":"17CQ_M15_EMA9_21_TOUCH_SWING10",
        "parent_checkpoint":"R037_XAUUSD_EMA_CROSS_TOUCH_SWING_BREAK_STAGE_A_SCREEN_CHECKPOINT_17CP_17CQ",
        "prereg_commit":PREREG_COMMIT,
        "parent_producer_sha256":parent_sha,
        "source_sha256":source_sha,
        "stage_a_control":{"metrics":cm,"diagnostics":cd,"ticks":ct},
        "later_jan":{
            "warmup_start_ms":WARMUP_START,
            "economic_start_ms":ECON_START,
            "end_exclusive_ms":HOLD_END,
            "metrics":hm,
            "diagnostics":hd,
            "ticks":ht,
            "gate":hg
        },
        "finding":{
            "decision":"RETAIN_XECTSB_M15_INDEPENDENTLY_VALIDATED" if hg["validation_pass"] else "RETIRE_XECTSB_AFTER_LATER_JAN_FAIL",
            "next":"R037_XECTSB_REFINEMENT_COMPARISON_GATE" if hg["validation_pass"] else "R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST"
        },
        "numeric_retuning":False,
        "post_result_rescue":False,
        "august_accessed":False,
        "mql5_authorized":False,
        "runtime_seconds":round(time.monotonic()-st,3)
    }
    base.atomic(args.output,out)
    print(json.dumps({
        "control":{"trades":cm["trades"],"days":cm["distinct_days"],"wins":cm["official_wins"],"net":cm["direct_net_usd"]},
        "later_jan":{"trades":hm["trades"],"days":hm["distinct_days"],"wins":hm["official_wins"],"net":hm["direct_net_usd"],"pass":hg["validation_pass"],"diag":hd},
        "finding":out["finding"],
        "runtime_seconds":out["runtime_seconds"]
    },separators=(",",":")))

if __name__=="__main__":
    main()

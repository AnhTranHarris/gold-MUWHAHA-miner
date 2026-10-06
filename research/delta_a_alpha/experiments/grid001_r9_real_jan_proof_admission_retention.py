from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

from grid001_january_event_label_lab import load, materialize
from grid001_january_early_thesis_failure import m1_atr_gap

CAN_NET=-6651.62
CAN_GP=3785.28
CAN_GL=-10436.90
SPLIT_MS=1769418162219

@njit(cache=True)
def admission(t,a,b,idx,side,gaps,deadline_ms):
    n=len(idx)
    outcome=np.zeros(n,np.int8)
    decision_idx=np.full(n,-1,np.int64)
    latency=np.full(n,np.nan)
    for k in range(n):
        i=int(idx[k]); s=int(side[k]); g=int(gaps[i]); end=int(deadline_ms[k])
        entry=a[i] if s>0 else b[i]
        proof=max(1,int(round(.25*g)))
        fail=max(1,int(round(.50*g)))
        j=i+1; decided=False
        while j<t.size and t[j]<=end:
            px=b[j] if s>0 else a[j]
            if s>0:
                if px<=entry-fail:
                    outcome[k]=2; decision_idx[k]=j; decided=True; break
                if px>=entry+proof:
                    outcome[k]=1; decision_idx[k]=j; decided=True; break
            else:
                if px>=entry+fail:
                    outcome[k]=2; decision_idx[k]=j; decided=True; break
                if px<=entry-proof:
                    outcome[k]=1; decision_idx[k]=j; decided=True; break
            j+=1
        if not decided:
            outcome[k]=3
            decision_idx[k]=min(j-1,t.size-1)
        latency[k]=(t[decision_idx[k]]-t[i])/1000.0 if decision_idx[k]>=i else 0.0
    return outcome,decision_idx,latency

def nearest_indices(t,ms):
    j=np.searchsorted(t,ms); j=np.clip(j,0,len(t)-1)
    p=np.maximum(j-1,0)
    return np.where(np.abs(t[p]-ms)<=np.abs(t[j]-ms),p,j)

def econ(df,mask):
    x=df.loc[np.asarray(mask,bool)]
    deals=np.concatenate([x.entry_deal_cashflow.to_numpy(float),x.exit_deal_cashflow.to_numpy(float)]) if len(x) else np.array([],float)
    gp=float(deals[deals>0].sum()) if len(deals) else 0.0
    gl=float(deals[deals<0].sum()) if len(deals) else 0.0
    return {"trades":int(len(x)),"net":float(x.net_cashflow.sum()),"gross_profit":gp,"gross_loss":gl,
            "pf":gp/abs(gl) if gl<0 else None,
            "win_rate_pct":100*float(np.mean(x.net_cashflow.to_numpy(float)>0)) if len(x) else None}

def segment(df,mask,outcome,latency):
    mask=np.asarray(mask,bool)
    proof=mask&(outcome==1); fail=mask&(outcome==2); nd=mask&(outcome==3)
    base=econ(df,mask); retained=econ(df,proof); removed=econ(df,mask&~(outcome==1))
    gl_removed=abs(base["gross_loss"])-abs(retained["gross_loss"])
    gp_sac=base["gross_profit"]-retained["gross_profit"]
    netv=df.net_cashflow.to_numpy(float)
    pos=mask&(netv>0); neg=mask&(netv<0)
    return {
      "signals":int(mask.sum()),"proof":int(proof.sum()),"fail":int(fail.sum()),"no_decision":int(nd.sum()),
      "proof_pct":100*float(proof.sum()/max(1,mask.sum())),
      "median_proof_latency_s":float(np.median(latency[proof])) if proof.any() else None,
      "p75_proof_latency_s":float(np.quantile(latency[proof],.75)) if proof.any() else None,
      "baseline":base,"retained":retained,"removed":removed,
      "gross_loss_removed_usd":gl_removed,
      "gross_loss_removed_pct_of_segment":100*gl_removed/abs(base["gross_loss"]) if base["gross_loss"]<0 else None,
      "gross_profit_sacrificed_usd":gp_sac,
      "gross_profit_sacrificed_pct_of_segment":100*gp_sac/base["gross_profit"] if base["gross_profit"]>0 else None,
      "net_improvement_proxy":retained["net"]-base["net"],
      "positive_trade_retention_pct":100*float(np.sum(pos&(outcome==1))/max(1,pos.sum())),
      "negative_trade_retention_pct":100*float(np.sum(neg&(outcome==1))/max(1,neg.sum()))
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("context_rows",type=Path)
    ap.add_argument("ticks",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    df=pd.read_csv(args.context_rows).sort_values("entry_utc_ms").reset_index(drop=True)
    t,sa,sb=load(args.ticks)
    a,b,maxe=materialize(t,sa,sb)
    gaps=m1_atr_gap(t,b,1.5)

    ems=df.mapped_tick_utc_ms.to_numpy(np.int64) if "mapped_tick_utc_ms" in df.columns else df.entry_utc_ms.to_numpy(np.int64)
    idx=nearest_indices(t,ems)
    side=df.side.to_numpy(np.int8)
    life_ms=np.minimum(df.hold_seconds.to_numpy(float)*1000.0,300_000.0)
    life_ms=np.maximum(life_ms,0.0).astype(np.int64)
    deadline=np.minimum(t[idx]+life_ms,t[-1])
    outcome,decision_idx,latency=admission(t,a,b,idx,side,gaps,deadline)

    disc=df.entry_utc_ms.to_numpy(np.int64)<SPLIT_MS
    full=np.ones(len(df),bool)
    relation={}
    for code,name in ((1,"ALIGNED"),(-1,"OPPOSED"),(0,"NEUTRAL"),(2,"CONFLICT")):
        relation[name]=segment(df,df.owner_relation.to_numpy()==code,outcome,latency)

    active_days=len(np.unique(df.entry_utc_ms.to_numpy(np.int64)//86_400_000))
    out={
      "schema":"delta-a-alpha-r9-real-jan-proof-admission-retention-v1",
      "unit":"DAA_GRID_001_R9_REAL_JAN_PROOF_ADMISSION_RETENTION_001","status":"COMPLETE",
      "contract":{"lattice":"A15","proof_gap_fraction":.25,"failure_gap_fraction":.50,
                  "deadline":"min(original R9 hold time,300s)","accounting":"original R9 cashflow retention proxy only"},
      "full":segment(df,full,outcome,latency),"discovery":segment(df,disc,outcome,latency),
      "validation":segment(df,~disc,outcome,latency),"owner_relation":relation,
      "active_days":int(active_days),"retained_trades_per_active_day_proxy":int(np.sum(outcome==1))/active_days,
      "max_midpoint_quantization_error_price":float(maxe/(2*1000)),
      "breakthrough_targets":{"gross_loss_removed_usd":2087.38,"net_improvement_proxy_usd":1330.324}
    }
    args.output.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2))

if __name__=="__main__":
    main()

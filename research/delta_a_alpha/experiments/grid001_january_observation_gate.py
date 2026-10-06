#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
from numba import njit
from grid001_january_event_label_lab import load, materialize, events, DAY_MS, GAP_RAW, PRICE_SCALE

WAITS=(250,1000,3000)
THRESH=(0.0,0.10,0.25)

@njit(cache=True)
def evaluate(t,a,b,idx,side,horizon=300_000):
    n=idx.size; pnl=np.zeros(n,np.float64)
    for k in range(n):
        s=int(side[k])
        if s==0: continue
        i=int(idx[k]); end=t[i]+horizon; entry=a[i] if s>0 else b[i]
        tp=entry+GAP_RAW if s>0 else entry-GAP_RAW
        sl=entry-GAP_RAW if s>0 else entry+GAP_RAW
        ex=entry; last=i; j=i+1
        while j<t.size and t[j]<=end:
            last=j
            if s>0:
                if b[j]>=tp or b[j]<=sl: ex=b[j]; break
            else:
                if a[j]<=tp or a[j]>=sl: ex=a[j]; break
            j+=1
        else:
            ex=b[last] if s>0 else a[last]
        pnl[k]=((ex-entry) if s>0 else (entry-ex))/PRICE_SCALE-0.02
    return pnl

def stats(x):
    gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    return {"n":len(x),"net":float(x.sum()),"gp":gp,"gl":gl,
            "pf":gp/abs(gl) if gl<0 else None,"expected":float(x.mean()),
            "win_pct":100*float((x>0).mean())}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("source",type=Path); ap.add_argument("--output",type=Path,required=True)
    z=ap.parse_args()
    t,sa,sb=load(z.source); a,b,_=materialize(t,sa,sb); ei,ed,_,_,_=events(t,a,b)
    mid=(a.astype(np.int64)+b.astype(np.int64))//2; m0=mid[ei]; et=t[ei]
    split=2*len(t)//3; disc=ei<split; val=~disc; active_days=len(np.unique(et//DAY_MS))
    rows=[]
    for w in WAITS:
        iw=np.searchsorted(t,et+w,side="left").astype(np.int64); valid=iw<len(t)
        mw=np.where(valid,mid[np.minimum(iw,len(t)-1)],m0)
        probe=ed.astype(np.float64)*(mw-m0)/GAP_RAW
        for c in THRESH:
            side=np.zeros(len(ei),np.int8)
            if c==0:
                side[(probe>0)&valid]=ed[(probe>0)&valid]; side[(probe<0)&valid]=-ed[(probe<0)&valid]
            else:
                side[(probe>=c)&valid]=ed[(probe>=c)&valid]; side[(probe<=-c)&valid]=-ed[(probe<=-c)&valid]
            p=evaluate(t,a,b,iw,side); acc=side!=0
            rows.append({"wait_ms":w,"threshold_gap":c,"accept_pct":100*float(acc.mean()),
                         "events_per_day":float(acc.sum()/active_days),
                         "full":stats(p[acc]),"discovery":stats(p[acc&disc]),"validation":stats(p[acc&val])})
    z.output.write_text(json.dumps({"schema":"delta-a-alpha-grid001-observation-gate-v1","variants":rows},indent=2)+"\n")
if __name__=="__main__": main()

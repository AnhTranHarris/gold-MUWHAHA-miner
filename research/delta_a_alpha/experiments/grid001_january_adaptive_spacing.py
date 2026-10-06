#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
from numba import njit
from grid001_january_event_label_lab import load, materialize, DAY_MS, H1_MS, WINDOW, PRICE_SCALE

MULTS=(0.5,1.0,1.5)

def m1_atr_gap(t,bid,mult):
    bucket=t//60_000; starts=np.r_[0,np.flatnonzero(bucket[1:]!=bucket[:-1])+1]; ends=np.r_[starts[1:]-1,len(t)-1]
    hi=np.maximum.reduceat(bid,starts).astype(np.int64); lo=np.minimum.reduceat(bid,starts).astype(np.int64); cl=bid[ends].astype(np.int64)
    prev=np.r_[cl[0],cl[:-1]]; tr=np.maximum(hi-lo,np.maximum(np.abs(hi-prev),np.abs(lo-prev))).astype(float)
    cs=np.r_[0.0,np.cumsum(tr)]; atr=np.full(len(tr),1000.0)
    for k in range(14,len(tr)): atr[k]=(cs[k]-cs[k-14])/14.0
    g=np.clip(mult*atr,750,5000); g=np.rint(g/100)*100; g=np.clip(g,750,5000).astype(np.int32)
    return np.repeat(g,ends-starts+1)

@njit(cache=True)
def gen(t,a,b,gaps,max_events=500000,max_stack=20000):
    bs=np.empty(max_stack,"i4"); bg=np.empty(max_stack,"i4"); ss=np.empty(max_stack,"i4"); sg=np.empty(max_stack,"i4"); nb=ns=0
    hi=np.empty(WINDOW-1,"i4"); lo=np.empty(WINDOW-1,"i4"); cnt=p=0; hour=np.int64(-1); ch=cl=np.int32(0); ready=False; rh=rl=np.int32(0)
    ei=np.empty(max_events,"i8"); ed=np.empty(max_events,"i1"); eg=np.empty(max_events,"i4"); ne=0
    for i in range(t.size):
        ti=np.int64(t[i]); ai=np.int32(a[i]); bi=np.int32(b[i]); g=np.int32(gaps[i]); h=ti//H1_MS
        if h!=hour:
            if hour!=-1: hi[p]=ch; lo[p]=cl; p=(p+1)%(WINDOW-1); cnt=min(cnt+1,WINDOW-1)
            hour=h; ch=bi; cl=bi
            if cnt>=WINDOW-1:
                rh=bi; rl=bi
                for j in range(WINDOW-1): rh=max(rh,hi[j]); rl=min(rl,lo[j])
                ready=True
            else: ready=False
        else: ch=max(ch,bi); cl=min(cl,bi)
        while nb>0 and bi>=bs[nb-1]+bg[nb-1]: nb-=1
        while ns>0 and ai<=ss[ns-1]-sg[ns-1]: ns-=1
        if not ready: continue
        ba=bs[nb-1] if nb else rh
        if ai<ba-g: bs[nb]=ai; bg[nb]=g; nb+=1; ei[ne]=i; ed[ne]=-1; eg[ne]=g; ne+=1
        sa=ss[ns-1] if ns else rl
        if ai>sa+g: ss[ns]=bi; sg[ns]=g; ns+=1; ei[ne]=i; ed[ne]=1; eg[ne]=g; ne+=1
    return ei[:ne],ed[:ne],eg[:ne]

@njit(cache=True)
def shadows(t,a,b,ei,ed,eg,horizon=300000):
    n=ei.size; mr=np.empty(n); co=np.empty(n)
    for k in range(n):
        i=int(ei[k]); d=int(ed[k]); g=int(eg[k]); end=t[i]+horizon
        for q in range(2):
            s=(1 if d<0 else -1) if q==0 else (-1 if d<0 else 1)
            e=a[i] if s>0 else b[i]; tp=e+g if s>0 else e-g; sl=e-g if s>0 else e+g; ex=e; last=i; j=i+1
            while j<t.size and t[j]<=end:
                last=j
                if s>0:
                    if b[j]>=tp or b[j]<=sl: ex=b[j]; break
                else:
                    if a[j]<=tp or a[j]>=sl: ex=a[j]; break
                j+=1
            else: ex=b[last] if s>0 else a[last]
            p=((ex-e) if s>0 else (e-ex))/PRICE_SCALE-0.02
            if q==0: mr[k]=p
            else: co[k]=p
    return mr,co

def stats(x):
    gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    return {"n":len(x),"net":float(x.sum()),"gp":gp,"gl":gl,"pf":gp/abs(gl) if gl<0 else None,
            "expected":float(x.mean()),"win_pct":100*float((x>0).mean())}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("source",type=Path); ap.add_argument("--output",type=Path,required=True); z=ap.parse_args()
    t,sa,sb=load(z.source); a,b,_=materialize(t,sa,sb); split=2*len(t)//3; out={}
    for m in MULTS:
        g=m1_atr_gap(t,b,m); ei,ed,eg=gen(t,a,b,g); mr,co=shadows(t,a,b,ei,ed,eg); disc=ei<split; val=~disc; oracle=np.maximum(mr,co)
        days=len(np.unique(t[ei]//DAY_MS))
        out[str(m)]={"events":len(ei),"events_per_day":len(ei)/days,
                     "gap_q":np.quantile(eg/1000,[.1,.25,.5,.75,.9]).tolist(),
                     "mr":stats(mr),"cont":stats(co),"oracle":stats(oracle),
                     "both_negative_pct":100*float(np.mean((mr<0)&(co<0))),
                     "disc_cont":stats(co[disc]),"val_cont":stats(co[val]),"val_oracle":stats(oracle[val])}
    z.output.write_text(json.dumps({"schema":"delta-a-alpha-adaptive-spacing-v1","variants":out},indent=2)+"\n")
if __name__=="__main__": main()

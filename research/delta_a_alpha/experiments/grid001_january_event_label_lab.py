#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np, pandas as pd
from numba import njit

N=9_135_062; DAY_MS=86_400_000; H1_MS=3_600_000; PRICE_SCALE=1000
TICK_RAW=10; GAP_RAW=1000; WINDOW=48
P75=np.array([20,20,21,21],dtype=np.int64)
US_DST=np.int64(1772953200000); UK_DST=np.int64(1774746000000)

def sha256(p:Path):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(8<<20),b""):h.update(b)
    return h.hexdigest()

def load(p:Path):
    t=np.empty(N,"i8"); a=np.empty(N,"i4"); b=np.empty(N,"i4"); pos=0
    for df in pd.read_csv(p,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],
                          dtype={"timestamp_ms_utc":"i8","ask_raw":"i4","bid_raw":"i4"},chunksize=1_000_000):
        k=len(df); t[pos:pos+k]=df.timestamp_ms_utc; a[pos:pos+k]=df.ask_raw; b[pos:pos+k]=df.bid_raw; pos+=k
    if pos!=N: raise RuntimeError(f"rows {pos}!={N}")
    return t,a,b

@njit(cache=True)
def session(t):
    tod=t%DAY_MS
    ls=7*3_600_000 if t>=UK_DST else 8*3_600_000; le=ls+8*3_600_000+30*60_000
    ns=12*3_600_000 if t>=US_DST else 13*3_600_000; ne=ns+9*3_600_000
    il=ls<=tod<le; inn=ns<=tod<ne
    if il and inn:return 2
    if il:return 1
    if inn:return 3
    return 0

@njit(cache=True)
def materialize(t,sa,sb):
    n=t.size; a=np.empty(n,"i4"); b=np.empty(n,"i4"); maxe=0
    for i in range(n):
        spr=P75[session(np.int64(t[i]))]*TICK_RAW
        mid2=np.int64(sa[i])+np.int64(sb[i])
        bi=((mid2-spr+TICK_RAW)//(2*TICK_RAW))*TICK_RAW
        ai=bi+spr; a[i]=ai; b[i]=bi
        e=abs((2*bi+spr)-mid2); maxe=max(maxe,e)
    return a,b,maxe

@njit(cache=True)
def events(t,a,b,max_events=500_000,max_stack=20_000):
    bs=np.empty(max_stack,"i4"); ss=np.empty(max_stack,"i4"); nb=0; ns=0
    hi=np.empty(WINDOW-1,"i4"); lo=np.empty(WINDOW-1,"i4")
    cnt=0; p=0; hour=np.int64(-1); ch=np.int32(0); cl=np.int32(0); ready=False; rh=np.int32(0); rl=np.int32(0)
    ei=np.empty(max_events,"i8"); ed=np.empty(max_events,"i1"); eh=np.empty(max_events,"i4"); el=np.empty(max_events,"i4"); dep=np.empty(max_events,"i2"); ne=0
    for i in range(t.size):
        ti=np.int64(t[i]); ai=np.int32(a[i]); bi=np.int32(b[i]); h=ti//H1_MS
        if h!=hour:
            if hour!=-1:
                hi[p]=ch; lo[p]=cl; p=(p+1)%(WINDOW-1); cnt=min(cnt+1,WINDOW-1)
            hour=h; ch=bi; cl=bi
            if cnt>=WINDOW-1:
                rh=bi; rl=bi
                for j in range(WINDOW-1):
                    rh=max(rh,hi[j]); rl=min(rl,lo[j])
                ready=True
            else: ready=False
        else:
            ch=max(ch,bi); cl=min(cl,bi)
        while nb>0 and bi>=bs[nb-1]+GAP_RAW: nb-=1
        while ns>0 and ai<=ss[ns-1]-GAP_RAW: ns-=1
        if not ready: continue
        buy_anchor=bs[nb-1] if nb else rh
        if ai<buy_anchor-GAP_RAW:
            bs[nb]=ai; nb+=1
            ei[ne]=i; ed[ne]=-1; eh[ne]=rh; el[ne]=rl; dep[ne]=nb; ne+=1
        sell_anchor=ss[ns-1] if ns else rl
        if ai>sell_anchor+GAP_RAW:
            ss[ns]=bi; ns+=1
            ei[ne]=i; ed[ne]=1; eh[ne]=rh; el[ne]=rl; dep[ne]=ns; ne+=1
    return ei[:ne],ed[:ne],eh[:ne],el[:ne],dep[:ne]

@njit(cache=True)
def shadows(t,a,b,ei,ed,horizon=300_000):
    n=ei.size; mr=np.empty(n); co=np.empty(n)
    for k in range(n):
        i=int(ei[k]); d=int(ed[k]); end=t[i]+horizon
        sides=(1 if d<0 else -1, -1 if d<0 else 1)
        out0=0.0; out1=0.0
        for q in range(2):
            side=sides[q]; entry=a[i] if side>0 else b[i]
            tp=entry+GAP_RAW if side>0 else entry-GAP_RAW
            sl=entry-GAP_RAW if side>0 else entry+GAP_RAW
            ex=entry; last=i; done=False; j=i+1
            while j<t.size and t[j]<=end:
                last=j
                if side>0:
                    if b[j]>=tp or b[j]<=sl: ex=b[j]; done=True; break
                else:
                    if a[j]<=tp or a[j]>=sl: ex=a[j]; done=True; break
                j+=1
            if not done: ex=b[last] if side>0 else a[last]
            pnl=((ex-entry) if side>0 else (entry-ex))/PRICE_SCALE-0.02
            if q==0: out0=pnl
            else: out1=pnl
        mr[k]=out0; co[k]=out1
    return mr,co

def stats(x):
    gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    return {"n":len(x),"net":float(x.sum()),"gross_profit":gp,"gross_loss":gl,
            "pf":gp/abs(gl) if gl<0 else None,"expected":float(x.mean()),"win_pct":100*float((x>0).mean())}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("source",type=Path); ap.add_argument("--output",type=Path,required=True)
    z=ap.parse_args()
    t,sa,sb=load(z.source); a,b,maxe=materialize(t,sa,sb); ei,ed,eh,el,dep=events(t,a,b); mr,co=shadows(t,a,b,ei,ed)
    split=2*len(t)//3; disc=ei<split; val=~disc; oracle=np.maximum(mr,co)
    out={"schema":"delta-a-alpha-grid001-january-event-label-lab-v1","source_sha256":sha256(z.source),
         "ticks":len(t),"surface":"DUKAS_COINEXX_LIKE_P75","events":len(ei),
         "active_event_days":int(len(np.unique(t[ei]//DAY_MS))),
         "events_per_active_day":float(len(ei)/len(np.unique(t[ei]//DAY_MS))),
         "max_midpoint_quantization_error_price":maxe/(2*PRICE_SCALE),
         "full":{"mr":stats(mr),"cont":stats(co),"oracle":stats(oracle),
                 "both_negative_pct":100*float(np.mean((mr<0)&(co<0)))},
         "discovery":{"mr":stats(mr[disc]),"cont":stats(co[disc]),"oracle":stats(oracle[disc])},
         "validation":{"mr":stats(mr[val]),"cont":stats(co[val]),"oracle":stats(oracle[val])},
         "split_tick_index":int(split),"split_time_ms":int(t[split])}
    z.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
if __name__=="__main__": main()

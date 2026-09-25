#!/usr/bin/env python3
import argparse, glob, hashlib, json, os, tempfile, time
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

PEN=0.05
RECLAIM=0.01
ACCEPT=0.05
ACCEPT_SEC=2
EXPIRY_SEC=15
MODEL_SPREAD_HALF=0.10
STOP=5.0
ACT=0.01
TRAIL=0.01
MAXHOLD_MS=120000
SCALES=(1,3,5,10,20)

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):
            h.update(b)
    return h.hexdigest()

def atomic_json(path,obj):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=str(path.parent),prefix=path.name+".tmp.")
    with os.fdopen(fd,"w",encoding="utf-8") as f:
        json.dump(obj,f,indent=2,sort_keys=True,allow_nan=True)
        f.flush(); os.fsync(f.fileno())
    os.replace(tmp,path)

def load_ticks(path):
    d=pd.read_csv(path,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],
                  dtype={"timestamp_ms_utc":"int64","ask_raw":"int64","bid_raw":"int64"})
    t=d.timestamp_ms_utc.to_numpy(np.int64)
    ask=d.ask_raw.to_numpy(np.float64)/1000.0
    bid=d.bid_raw.to_numpy(np.float64)/1000.0
    mid=(ask+bid)*0.5
    return t,ask,bid,mid

def grouped_bars(keys,price):
    uniq,idx,cnt=np.unique(keys,return_index=True,return_counts=True)
    hi=np.maximum.reduceat(price,idx)
    lo=np.minimum.reduceat(price,idx)
    row=np.repeat(np.arange(len(uniq),dtype=np.int32),cnt)
    return uniq,hi,lo,row

@njit(cache=True)
def previous_window_extremes(hi,lo,window):
    n=len(hi)
    out_hi=np.empty(n,np.float64); out_lo=np.empty(n,np.float64)
    for i in range(n):
        out_hi[i]=np.nan; out_lo[i]=np.nan
    for i in range(window,n):
        h=-1e300; l=1e300
        for j in range(i-window,i):
            if hi[j]>h: h=hi[j]
            if lo[j]<l: l=lo[j]
        out_hi[i]=h; out_lo[i]=l
    return out_hi,out_lo

@njit(cache=True)
def detect_events_exact(t_ms,ask,bid,row,bhi,blo):
    cap=max(10000,len(t_ms)//4)
    et=np.empty(cap,np.int64)
    es=np.empty(cap,np.int8)
    typ=np.empty(cap,np.int8)
    bp=np.empty(cap,np.float64)
    n=0
    active=0
    side=0
    boundary=0.0
    started_sec=0
    for i in range(len(t_ms)):
        r=row[i]
        hi=bhi[r]; lo=blo[r]
        if not np.isfinite(hi) or not np.isfinite(lo):
            continue
        sec=t_ms[i]//1000
        if active!=0:
            dt=sec-started_sec
            if dt>EXPIRY_SEC:
                active=0
                side=0
                continue
            reclaim=False
            accept=False
            if side>0:
                reclaim=bid[i]<=boundary-RECLAIM
                accept=(dt>=ACCEPT_SEC and bid[i]>=boundary+ACCEPT)
            else:
                reclaim=ask[i]>=boundary+RECLAIM
                accept=(dt>=ACCEPT_SEC and ask[i]<=boundary-ACCEPT)
            if reclaim or accept:
                if n>=cap:
                    break
                et[n]=t_ms[i]
                es[n]=side
                typ[n]=(-1 if reclaim else 1)
                bp[n]=boundary
                n+=1
                active=0
                side=0
            continue
        if ask[i]>=hi+PEN:
            active=1; side=1; boundary=hi; started_sec=sec
        elif bid[i]<=lo-PEN:
            active=1; side=-1; boundary=lo; started_sec=sec
    return et[:n],es[:n],typ[:n],bp[:n]

@njit(cache=True)
def sim_actions(t_ms,mid,event_ms,event_side):
    n=len(event_ms)
    cp=np.empty(n,np.float64); ce=np.empty(n,np.int64); ch=np.empty(n,np.float64)
    fp=np.empty(n,np.float64); fe=np.empty(n,np.int64); fh=np.empty(n,np.float64)
    for k in range(n):
        for which in range(2):
            side=event_side[k] if which==0 else -event_side[k]
            i0=np.searchsorted(t_ms,event_ms[k])
            if i0>=len(t_ms):
                pnl=np.nan; exms=-1; hold=np.nan
            else:
                p=mid[i0]
                mbid=p-MODEL_SPREAD_HALF
                mask=p+MODEL_SPREAD_HALF
                entry=mask if side>0 else mbid
                stop=(mbid-STOP) if side>0 else (mask+STOP)
                ex=entry; ei=i0
                for i in range(i0+1,len(t_ms)):
                    p=mid[i]
                    mbid=p-MODEL_SPREAD_HALF
                    mask=p+MODEL_SPREAD_HALF
                    fav=(mbid-entry) if side>0 else (entry-mask)
                    exited=False
                    if (side>0 and mbid<=stop) or (side<0 and mask>=stop):
                        ex=mbid if side>0 else mask
                        ei=i; exited=True
                    elif t_ms[i]-event_ms[k]>=MAXHOLD_MS:
                        ex=mbid if side>0 else mask
                        ei=i; exited=True
                    else:
                        if fav>=ACT:
                            cand=(mbid-TRAIL) if side>0 else (mask+TRAIL)
                            if side>0:
                                if cand>stop+0.005: stop=cand
                            else:
                                if cand<stop-0.005: stop=cand
                    if exited:
                        break
                    ei=i
                if ei==i0 or (t_ms[ei]-event_ms[k]<MAXHOLD_MS and ex==entry):
                    p=mid[ei]
                    ex=(p-MODEL_SPREAD_HALF) if side>0 else (p+MODEL_SPREAD_HALF)
                pnl=(ex-entry)*side
                exms=t_ms[ei]
                hold=(exms-event_ms[k])/1000.0
            if which==0:
                cp[k]=pnl; ce[k]=exms; ch[k]=hold
            else:
                fp[k]=pnl; fe[k]=exms; fh[k]=hold
    return cp,ce,ch,fp,fe,fh

def metrics(x):
    x=np.asarray(x,float)
    x=x[np.isfinite(x)]
    gp=float(x[x>0].sum()) if len(x) else 0.0
    gl=float(x[x<0].sum()) if len(x) else 0.0
    return {
        "trades":int(len(x)),
        "net":float(x.sum()) if len(x) else 0.0,
        "gp":gp,
        "gl":gl,
        "pf":float(gp/-gl) if gl<0 else (999.0 if gp>0 else 0.0),
        "win":float((x>0).mean()) if len(x) else 0.0
    }

def main():
    ap=argparse.ArgumentParser(description="C27v2 bounded exact-source boundary-state scale unit.")
    ap.add_argument("--month",type=int,required=True)
    ap.add_argument("--scale",type=int,choices=[1,3,5,10,20],required=True)
    ap.add_argument("--data-dir",default=os.environ.get("R9_DATA_DIR","/mnt/data"))
    ap.add_argument("--out-dir",default=os.environ.get("R9_C27V2_OUT_DIR","/mnt/data/C27v2_boundary_scale"))
    a=ap.parse_args()
    m=a.month
    sc=a.scale
    out=Path(a.out_dir)
    out.mkdir(parents=True,exist_ok=True)
    candidates=sorted(glob.glob(str(Path(a.data_dir)/f"XAUUSD_DUKAS_2026_{m:02d}_ticks.csv.gz")))
    if not candidates:
        candidates=sorted(glob.glob(str(Path(a.data_dir)/f"XAUUSD_DUKAS_2026_{m:02d}_ticks.csv*.gz")))
    if not candidates:
        raise FileNotFoundError(f"missing month {m:02d}")
    raw=candidates[0]
    job=f"C27V2_M{m:02d}_S{sc:02d}"
    manifest=out/f"{job}.json"
    started=time.time()
    atomic_json(manifest,{"job_id":job,"status":"STARTED","month":m,"scale":sc,"source":Path(raw).name})

    t,ask,bid,mid=load_ticks(raw)

    if sc==1:
        secs=t//1000
        _,sec_hi,sec_lo,row=grouped_bars(secs,bid)
        bhi,blo=previous_window_extremes(sec_hi,sec_lo,60)
        boundary_kind="rolling_60_completed_1s_bid_bars"
    else:
        mins=t//60000
        _,min_hi,min_lo,row=grouped_bars(mins,bid)
        bhi,blo=previous_window_extremes(min_hi,min_lo,sc)
        boundary_kind=f"previous_{sc}_completed_M1_bid_bars"

    et,es,typ,bp=detect_events_exact(t,ask,bid,row,bhi,blo)
    cp,ce,ch,fp,fe,fh=sim_actions(t,mid,et,es)
    events=pd.DataFrame({
        "month":np.full(len(et),m,dtype=np.int8),
        "scale":np.full(len(et),sc,dtype=np.int8),
        "event_ms":et,
        "event_side":es.astype(np.int8),
        "event_type":np.where(typ>0,"ACCEPT","RECLAIM"),
        "cont_pnl":cp,
        "cont_exit_ms":ce,
        "fade_pnl":fp,
        "fade_exit_ms":fe
    }).sort_values("event_ms").reset_index(drop=True)

    summary=[]
    for side in (-1,1):
        for st in ("ACCEPT","RECLAIM"):
            q=events[(events.event_side==side)&(events.event_type==st)]
            for act,col in (("CONTINUE","cont_pnl"),("FADE","fade_pnl")):
                summary.append({"month":m,"scale":sc,"event_side":int(side),"event_type":st,
                                "action":act,"boundary_kind":boundary_kind,**metrics(q[col].to_numpy())})
    states=pd.DataFrame(summary)

    persist_events=events.copy()
    persist_events["event_type"]=np.where(persist_events["event_type"].to_numpy()=="ACCEPT",1,-1).astype(np.int8)
    evp=out/f"{job}.pkl.gz"
    tmp=Path(str(evp)+".tmp")
    persist_events.to_pickle(tmp,compression={"method":"gzip","compresslevel":1,"mtime":1})
    os.replace(tmp,evp)

    smp=out/f"{job}_states.csv"
    tmp=Path(str(smp)+".tmp")
    states.to_csv(tmp,index=False)
    os.replace(tmp,smp)

    final={
        "job_id":job,"status":"COMPLETED_LOCAL","month":m,"scale":sc,
        "ticks":int(len(t)),"events":int(len(events)),"state_rows":int(len(states)),
        "event_artifact_schema":["month","scale","event_ms","event_side","event_type_code","cont_pnl","cont_exit_ms","fade_pnl","fade_exit_ms"],
        "event_type_codes":{"ACCEPT":1,"RECLAIM":-1},
        "source":Path(raw).name,"source_sha256":sha256(raw),
        "events_sha256":sha256(evp),"states_sha256":sha256(smp),
        "elapsed_seconds":time.time()-started,
        "event_detection":{
            "quote_reference":"raw Dukascopy bid/ask",
            "boundary_kind":boundary_kind,
            "penetration":PEN,"reclaim":RECLAIM,"acceptance":ACCEPT,
            "acceptance_clock_seconds":ACCEPT_SEC,"expiry_clock_seconds":EXPIRY_SEC,
            "clock_semantics":"integer floor(timestamp_ms/1000), matching archived tick.time comparisons"
        },
        "outcome_execution":{
            "price_reference":"mid with fixed modeled +/-0.10 bid/ask",
            "spread_half":MODEL_SPREAD_HALF,"stop":STOP,"activation":ACT,
            "trail":TRAIL,"maxhold_ms":MAXHOLD_MS
        }
    }
    atomic_json(manifest,final)
    print(json.dumps(final,indent=2))

if __name__=="__main__":
    main()

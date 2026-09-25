#!/usr/bin/env python3
import argparse, glob, hashlib, json, os, tempfile, time
from pathlib import Path
import numpy as np, pandas as pd
from numba import njit

H=.10
BREAKOUT=6
VOLCAP=2.0
STOP_MULT=1.5
ACT_MULT=.25
TRAIL_MULT=1.0
MAXH=24*3600*1000

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def atomic_json(path,obj):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=str(path.parent),prefix=path.name+".tmp.")
    with os.fdopen(fd,"w",encoding="utf-8") as f:
        json.dump(obj,f,indent=2,sort_keys=True,allow_nan=True); f.flush(); os.fsync(f.fileno())
    os.replace(tmp,path)

def load_ticks(path,nrows=None):
    d=pd.read_csv(path,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],nrows=nrows,
                  dtype={"timestamp_ms_utc":"int64","ask_raw":"int64","bid_raw":"int64"})
    t=d.timestamp_ms_utc.to_numpy(np.int64)
    mid=(d.ask_raw.to_numpy(np.float64)+d.bid_raw.to_numpy(np.float64))/2000.0
    return t,mid

def wilder(z,n=14):
    h=z.high.to_numpy(float); l=z.low.to_numpy(float); c=z.close.to_numpy(float); pc=np.r_[np.nan,c[:-1]]
    tr=np.maximum(h-l,np.maximum(np.abs(h-pc),np.abs(l-pc))); a=np.full(len(z),np.nan)
    if len(z)>n:
        a[n]=np.nanmean(tr[1:n+1])
        for i in range(n+1,len(z)): a[i]=(a[i-1]*(n-1)+tr[i])/n
    return a

@njit(cache=True)
def sim(t,mid,sig,side,atr):
    i0=np.searchsorted(t,sig)
    if i0>=len(t): return np.nan,-1,np.nan,np.nan,np.nan
    p=mid[i0]; entry=p+H if side>0 else p-H; bid=p-H; ask=p+H
    stop=bid-atr*STOP_MULT if side>0 else ask+atr*STOP_MULT
    activation=atr*ACT_MULT; trail=atr*TRAIL_MULT; ot=t[i0]; mfe=0.; mae=0.; ei=i0
    for i in range(i0+1,len(t)):
        tt=t[i]; p=mid[i]; bid=p-H; ask=p+H
        fav=(bid-entry) if side>0 else (entry-ask); adv=(entry-bid) if side>0 else (ask-entry)
        if fav>mfe: mfe=fav
        if adv>mae: mae=adv
        if (side>0 and bid<=stop) or (side<0 and ask>=stop):
            return ((bid-entry) if side>0 else (entry-ask)),tt,(tt-ot)/1000.,mfe,mae
        if tt-ot>=MAXH:
            return ((bid-entry) if side>0 else (entry-ask)),tt,(tt-ot)/1000.,mfe,mae
        if fav>=activation:
            cand=bid-trail if side>0 else ask+trail
            if side>0:
                if cand>stop: stop=cand
            else:
                if cand<stop: stop=cand
        ei=i
    p=mid[ei]; bid=p-H; ask=p+H
    return ((bid-entry) if side>0 else (entry-ask)),t[ei],(t[ei]-ot)/1000.,mfe,mae

def main():
    ap=argparse.ArgumentParser(description="Fresh recertification of archived H4/6/vol<=2/HIST structural sleeve.")
    ap.add_argument("--month",type=int,choices=[5,6,7],required=True)
    ap.add_argument("--data-dir",default="/mnt/data")
    ap.add_argument("--bars-dir",default="/mnt/data/C25_P5_structural")
    ap.add_argument("--out-dir",default="/mnt/data/C26_H4_history_recert")
    args=ap.parse_args()
    m=args.month; data=Path(args.data_dir); bars=Path(args.bars_dir); out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    job=f"C26_H4_HIST_{m:02d}"; manifest=out/f"{job}.json"; started=time.time()
    atomic_json(manifest,{"job_id":job,"status":"STARTED","month":m,"rule":{"tf":"H4","breakout":BREAKOUT,"volcap":VOLCAP,"stop_mult":STOP_MULT,"act_mult":ACT_MULT,"trail_mult":TRAIL_MULT,"max_hold_hours":24}})

    current=sorted(glob.glob(str(data/f"XAUUSD_DUKAS_2026_{m:02d}_ticks.csv*.gz")))[0]
    t,mid=load_ticks(current)
    hist=pd.read_pickle(bars/"H4_bars_Jan04.pkl.gz",compression="gzip")
    for pm in range(5,m+1):
        p=bars/f"H4_bars_{pm:02d}.pkl.gz"
        if p.exists(): hist=pd.concat([hist,pd.read_pickle(p,compression="gzip")],ignore_index=True)
    z=hist.drop_duplicates("bucket").sort_values("bucket").reset_index(drop=True)
    z["atr"]=wilder(z); z["atrmean20"]=z.atr.shift(1).rolling(20,min_periods=20).mean(); z["volratio"]=z.atr/z.atrmean20

    first=int(t[0]); last=int(t[-1]); sigs=[]
    for i in range(max(21,BREAKOUT+1),len(z)):
        em=int(z.end_ms.iloc[i])
        if not(first<=em<=last+14400*1000): continue
        atr=float(z.atr.iloc[i]); vr=float(z.volratio.iloc[i])
        if not np.isfinite(atr) or not np.isfinite(vr) or vr>VOLCAP: continue
        ph=z.high.iloc[i-BREAKOUT:i].max(); pl=z.low.iloc[i-BREAKOUT:i].min(); cl=z.close.iloc[i]
        side=1 if cl>ph else (-1 if cl<pl else 0)
        if side: sigs.append((em,side,atr,vr))

    next_path=None
    if m<7:
        next_path=sorted(glob.glob(str(data/f"XAUUSD_DUKAS_2026_{m+1:02d}_ticks.csv*.gz")))[0]
        tn,mn=load_ticks(next_path,nrows=2000000); t=np.concatenate([t,tn]); mid=np.concatenate([mid,mn])

    rows=[]
    for sig,side,atr,vr in sigs:
        pnl,ex,hold,mfe,mae=sim(t,mid,sig,side,atr)
        rows.append((sig,side,atr,vr,pnl,ex,hold,mfe,mae))
    d=pd.DataFrame(rows,columns=["signal_ms","side","atr","volratio","pnl","exit_ms","hold","mfe","mae"]).sort_values("signal_ms")
    free=-1; chosen=[]
    for r in d.itertuples(index=False):
        if r.signal_ms<=free or not np.isfinite(r.pnl) or r.exit_ms<0: continue
        chosen.append(r); free=int(r.exit_ms)
    x=np.asarray([r.pnl for r in chosen],float); gp=float(x[x>0].sum()) if len(x) else 0.; gl=float(x[x<0].sum()) if len(x) else 0.
    res={"job_id":job,"status":"COMPLETED_LOCAL","month":m,"signals":len(sigs),"trades":int(len(x)),
         "net":float(x.sum()) if len(x) else 0.0,"gp":gp,"gl":gl,"pf":float(gp/-gl) if gl<0 else 1e9,
         "win":float((x>0).mean()) if len(x) else 0.0,"avg_hold":float(np.mean([r.hold for r in chosen])) if chosen else 0.0,
         "rule":{"tf":"H4","breakout":BREAKOUT,"volcap":VOLCAP,"stop_mult":STOP_MULT,"act_mult":ACT_MULT,"trail_mult":TRAIL_MULT,"max_hold_hours":24},
         "source":Path(current).name,"source_sha256":sha256(current),"next_source":Path(next_path).name if next_path else None,
         "next_source_sha256":sha256(next_path) if next_path else None,"elapsed_seconds":time.time()-started}
    pkl=out/f"{job}.pkl.gz"; d.to_pickle(pkl,compression="gzip"); res["output_sha256"]=sha256(pkl)
    atomic_json(manifest,res); print(json.dumps(res,indent=2,allow_nan=True))

if __name__=="__main__": raise SystemExit(main())

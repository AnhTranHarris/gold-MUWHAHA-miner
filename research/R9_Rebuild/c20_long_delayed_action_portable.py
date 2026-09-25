#!/usr/bin/env python3
import argparse, glob, hashlib, json, os, tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

HORIZONS=np.array([3000,5000,10000],dtype=np.int64)

def utcnow():
    return datetime.now(timezone.utc).isoformat()

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
        json.dump(obj,f,indent=2,allow_nan=True,sort_keys=True)
        f.flush(); os.fsync(f.fileno())
    os.replace(tmp,path)

def resolve_month_file(data_dir,month):
    pats=sorted(glob.glob(str(Path(data_dir)/f"XAUUSD_DUKAS_2026_{month:02d}_ticks.csv*.gz")))
    if not pats:
        raise FileNotFoundError(f"No Dukascopy month {month:02d} file under {data_dir}")
    return pats[0]

@njit(cache=True)
def sim_many(t,mid,decision_ms,side,stopd,targetd,maxhold):
    n=len(decision_ms)
    pnl=np.empty(n); exms=np.empty(n,np.int64); mfe=np.empty(n); mae=np.empty(n)
    for k in range(n):
        dt=decision_ms[k]
        i0=np.searchsorted(t,dt)
        if i0>=len(t):
            pnl[k]=np.nan; exms[k]=-1; mfe[k]=np.nan; mae[k]=np.nan
            continue
        s=side[k]
        p=mid[i0]
        entry=p+.10 if s>0 else p-.10
        best=0.; worst=0.; ex=entry; ei=i0
        for i in range(i0+1,len(t)):
            tt=t[i]; p=mid[i]; bid=p-.10; ask=p+.10
            fav=(bid-entry) if s>0 else (entry-ask)
            adv=(entry-bid) if s>0 else (ask-entry)
            if fav>best: best=fav
            if adv>worst: worst=adv
            if fav>=targetd or adv>=stopd or tt-dt>=maxhold:
                ex=bid if s>0 else ask
                ei=i
                break
            ei=i
        pnl[k]=(ex-entry)*s
        exms[k]=t[ei]
        mfe[k]=best
        mae[k]=worst
    return pnl,exms,mfe,mae

def seq(decision,pnl,ex):
    order=np.argsort(decision,kind="stable")
    free=-1; vals=[]
    for k in order:
        if not np.isfinite(pnl[k]) or decision[k]<=free:
            continue
        vals.append(pnl[k]); free=int(ex[k])
    x=np.asarray(vals,dtype=float)
    gp=float(x[x>0].sum()) if len(x) else 0.0
    gl=float(x[x<0].sum()) if len(x) else 0.0
    return {
        "trades":int(len(x)),
        "net":float(x.sum()) if len(x) else 0.0,
        "gp":gp,"gl":gl,
        "pf":float(gp/-gl) if gl<0 else 1e9,
        "win":float((x>0).mean()) if len(x) else 0.0
    }

def oracle_seq(decision,cp,ce,fp,fe):
    order=np.argsort(decision,kind="stable")
    free=-1; vals=[]; actions=[]
    for k in order:
        if decision[k]<=free:
            continue
        if fp[k]>cp[k]:
            vals.append(fp[k]); free=int(fe[k]); actions.append(-1)
        else:
            vals.append(cp[k]); free=int(ce[k]); actions.append(1)
    x=np.asarray(vals,dtype=float)
    gp=float(x[x>0].sum()) if len(x) else 0.0
    gl=float(x[x<0].sum()) if len(x) else 0.0
    return {
        "trades":int(len(x)),
        "net":float(x.sum()) if len(x) else 0.0,
        "gp":gp,"gl":gl,
        "pf":float(gp/-gl) if gl<0 else 1e9,
        "win":float((x>0).mean()) if len(x) else 0.0,
        "fade_share":float((np.asarray(actions)==-1).mean()) if actions else 0.0
    }

def main():
    ap=argparse.ArgumentParser(description="C20 portable 3/5/10s delayed CONTINUE/FADE outcome builder.")
    ap.add_argument("--month",type=int,required=True)
    ap.add_argument("--data-dir",default=os.environ.get("R9_DATA_DIR"))
    ap.add_argument("--snapshot-dir",default=os.environ.get("R9_SNAPSHOT_DIR"))
    ap.add_argument("--out-dir",default=os.environ.get("R9_ACTION_OUT_DIR"))
    args=ap.parse_args()
    month=args.month
    data_dir=Path(args.data_dir or (Path.home()/"XAUUSD-Tick-Research"))
    snapshot_dir=Path(args.snapshot_dir or (data_dir/"R9_Durable_Inputs"))
    out_dir=Path(args.out_dir or (data_dir/"R9_Durable_Results"/"pullback_action"))
    out_dir.mkdir(parents=True,exist_ok=True)

    job=f"C20_LONG_ACTION_{month:02d}"
    manifest=out_dir/f"{job}.json"
    atomic_json(manifest,{
        "job_id":job,"status":"STARTED","started_utc":utcnow(),
        "month":month,"horizons_ms":HORIZONS.tolist(),
        "data_dir":str(data_dir),"snapshot_dir":str(snapshot_dir),"out_dir":str(out_dir)
    })

    snap_path=snapshot_dir/f"pullback_lifecycle_snap_{month:02d}.pkl.gz"
    if not snap_path.exists():
        raise FileNotFoundError(f"Missing durable snapshot: {snap_path}")
    snap=pd.read_pickle(snap_path,compression="gzip").sort_values("entry_ms").reset_index(drop=True)
    src=resolve_month_file(data_dir,month)
    d=pd.read_csv(src,compression="gzip",usecols=["timestamp_ms_utc","ask_raw","bid_raw"],
                  dtype={"timestamp_ms_utc":"int64","ask_raw":"int64","bid_raw":"int64"})
    t=d.timestamp_ms_utc.to_numpy(np.int64)
    mid=(d.ask_raw.to_numpy(np.float64)+d.bid_raw.to_numpy(np.float64))/2000.0
    del d

    base_ent=snap.entry_ms.to_numpy(np.int64)
    side=snap.struct_side.to_numpy(np.int8)
    out=snap[["time_ms","entry_ms","struct_side"]].copy()
    caps={}

    for h in HORIZONS:
        decision=base_ent+h
        cp,ce,cm,ca=sim_many(t,mid,decision,side,.90,4.50,120000)
        fp,fe,fm,fa=sim_many(t,mid,decision,-side,.90,4.50,120000)
        tag=f"d{h}"
        out[tag+"_decision_ms"]=decision
        out[tag+"_cont_pnl"]=cp; out[tag+"_cont_exit_ms"]=ce
        out[tag+"_cont_mfe"]=cm; out[tag+"_cont_mae"]=ca
        out[tag+"_fade_pnl"]=fp; out[tag+"_fade_exit_ms"]=fe
        out[tag+"_fade_mfe"]=fm; out[tag+"_fade_mae"]=fa
        out[tag+"_diff"]=fp-cp
        caps[str(int(h))]={
            "continue":seq(decision,cp,ce),
            "fade":seq(decision,fp,fe),
            "oracle_capacity":oracle_seq(decision,cp,ce,fp,fe)
        }

    path=out_dir/f"{job}.pkl.gz"
    tmp=Path(str(path)+".tmp")
    out.to_pickle(tmp,compression="gzip")
    os.replace(tmp,path)

    final={
        "job_id":job,"status":"COMPLETED_LOCAL","completed_utc":utcnow(),
        "month":month,"source":Path(src).name,"source_sha256":sha256(src),
        "input_snapshot":snap_path.name,"input_snapshot_sha256":sha256(snap_path),
        "rows":int(len(out)),"horizons_ms":HORIZONS.tolist(),
        "capacity":caps,"output":path.name,"output_sha256":sha256(path),
        "lifecycle":".90 stop / 4.50 target / 120s; exact modeled bid/ask; decision/entry delayed after transformed event",
        "oracle_note":"future-informed capacity only; prohibited as execution input"
    }
    atomic_json(manifest,final)
    print(json.dumps(final,indent=2))

if __name__=="__main__":
    main()

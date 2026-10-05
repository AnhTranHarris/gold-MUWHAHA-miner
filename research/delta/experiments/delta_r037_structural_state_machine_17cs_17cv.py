"""R037 17CS-17CV structural state-machine harvest.

Two independent source-grounded families:
- classic 1-2-3 confirmed swing reversal -> neckline break;
- MSnR rolling Double Breakout staircase.

Research only. No post-result retuning. August sealed.
"""
from __future__ import annotations
import argparse, hashlib, json, os, tempfile, time
from pathlib import Path
import numpy as np
import pandas as pd
import delta_r037_xectsb_stage_a_17cp_17cq as base

PARENT_SHA256="c26dc710879a86b9447dfaf2e236c4f3621151a3ab2a62d35aef8f34f44ae03e"
CANONICAL_SHA256="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
PREREG_COMMIT="0f5e4299eab2e76ead38ad63a5a1376a62de8dc1"
PIVOT_W=3
MSNR_SCAN=120

LANES=(
    ("17CS_123NB_M1","123",60_000),
    ("17CT_123NB_M5","123",300_000),
    ("17CU_MSNR_DBO_M1","MSNR",60_000),
    ("17CV_MSNR_DBO_M5","MSNR",300_000),
)

def sha256_file(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""): h.update(block)
    return h.hexdigest()

def atomic(path:Path,obj:dict)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    tmpname=None
    try:
        with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="\n",
                                         prefix=f".{path.name}.",suffix=".tmp",
                                         dir=path.parent,delete=False) as tmp:
            tmpname=tmp.name
            json.dump(obj,tmp,indent=2)
            tmp.write("\n"); tmp.flush(); os.fsync(tmp.fileno())
        os.replace(tmpname,path); tmpname=None
    finally:
        if tmpname:
            try: os.unlink(tmpname)
            except FileNotFoundError: pass

def confirmed_pivots(z,w=PIVOT_W):
    h,l,e=z["h"],z["l"],z["e"]
    events=[]
    for k in range(w,len(h)-w):
        hi=int(h[k]); lo=int(l[k])
        ish=True; isl=True
        for j in range(1,w+1):
            if not (hi>h[k-j] and hi>h[k+j]): ish=False
            if not (lo<l[k-j] and lo<l[k+j]): isl=False
            if not ish and not isl: break
        if ish == isl:
            continue
        reveal=k+w
        events.append((reveal,1 if ish else -1,hi if ish else lo,k))
    return events

def signals_123(t,a,b,z):
    c,e=z["c"],z["e"]
    by_reveal={}
    for ev in confirmed_pivots(z):
        by_reveal.setdefault(ev[0],[]).append(ev)

    piv=[]
    pattern=None
    ix=[]; sd=[]
    diag={"pivots":0,"pattern_armed":0,"invalidated":0,"neckline_breaks":0,
          "ambiguous_reveals":0,"spread_rejects":0}

    for k in range(len(c)):
        evs=by_reveal.get(k,())
        if len(evs)>1:
            diag["ambiguous_reveals"]+=1
        for _,side,price,pidx in evs:
            diag["pivots"]+=1
            if piv and piv[-1][0]==side:
                if (side>0 and price>piv[-1][1]) or (side<0 and price<piv[-1][1]):
                    piv[-1]=[side,price,pidx,k]
                else:
                    continue
            else:
                piv.append([side,price,pidx,k])
                if len(piv)>8: piv=piv[-8:]

            if len(piv)>=3:
                p1,p2,p3=piv[-3],piv[-2],piv[-1]
                newpat=None
                if p1[0]==-1 and p2[0]==1 and p3[0]==-1 and p3[1]>p1[1]:
                    newpat={"side":1,"p1":p1[1],"neck":p2[1],"ready":k,
                            "ids":(p1[2],p2[2],p3[2])}
                elif p1[0]==1 and p2[0]==-1 and p3[0]==1 and p3[1]<p1[1]:
                    newpat={"side":-1,"p1":p1[1],"neck":p2[1],"ready":k,
                            "ids":(p1[2],p2[2],p3[2])}
                if newpat is not None:
                    pattern=newpat; diag["pattern_armed"]+=1

        if pattern is None or k<=pattern["ready"]:
            continue

        if (pattern["side"]>0 and c[k]<pattern["p1"]) or (pattern["side"]<0 and c[k]>pattern["p1"]):
            pattern=None; diag["invalidated"]+=1; continue

        hit=(pattern["side"]>0 and c[k]>pattern["neck"]) or (pattern["side"]<0 and c[k]<pattern["neck"])
        if not hit: continue

        j=int(np.searchsorted(t,int(e[k]),side="left"))
        if j<len(t):
            if a[j]-b[j] <= base.MS:
                ix.append(j); sd.append(pattern["side"]); diag["neckline_breaks"]+=1
            else:
                diag["spread_rejects"]+=1
        pattern=None

    return np.asarray(ix,np.int64),np.asarray(sd,np.int8),diag

def _expire(seed_origin, outer_origin, k):
    origin=outer_origin if outer_origin>=0 else seed_origin
    return origin>=0 and k-origin>MSNR_SCAN

def signals_msnr(t,a,b,z):
    o,c,e=z["o"],z["c"],z["e"]
    A=[None,-1,None,None,-1,-1]
    V=[None,-1,None,None,-1,-1]
    ix=[]; sd=[]
    diag={"a_levels":0,"v_levels":0,"a_breakouts":0,"v_breakouts":0,
          "a_slides":0,"v_slides":0,"a_restarts":0,"v_restarts":0,
          "expired":0,"spread_rejects":0}

    for k in range(1,len(c)):
        if _expire(A[1],A[4],k):
            A=[None,-1,None,None,-1,-1]; diag["expired"]+=1
        if _expire(V[1],V[4],k):
            V=[None,-1,None,None,-1,-1]; diag["expired"]+=1

        if A[2] is not None and c[k] > A[2]:
            j=int(np.searchsorted(t,int(e[k]),side="left"))
            if j<len(t):
                if a[j]-b[j] <= base.MS:
                    ix.append(j); sd.append(1); diag["a_breakouts"]+=1
                else: diag["spread_rejects"]+=1
            A=[None,-1,None,None,-1,-1]

        if V[2] is not None and c[k] < V[2]:
            j=int(np.searchsorted(t,int(e[k]),side="left"))
            if j<len(t):
                if a[j]-b[j] <= base.MS:
                    ix.append(j); sd.append(-1); diag["v_breakouts"]+=1
                else: diag["spread_rejects"]+=1
            V=[None,-1,None,None,-1,-1]

        prev_green=c[k-1]>o[k-1]; prev_red=c[k-1]<o[k-1]
        cur_green=c[k]>o[k]; cur_red=c[k]<o[k]

        if prev_green and cur_red:
            x=int(c[k-1]); origin=k-1; diag["a_levels"]+=1
            if A[0] is None:
                A=[x,origin,None,None,-1,-1]
            elif A[2] is None:
                if x < A[0]:
                    A=[None,-1,A[0],x,A[1],origin]
                else:
                    A=[x,origin,None,None,-1,-1]; diag["a_restarts"]+=1
            else:
                if x < A[3]:
                    A=[None,-1,A[3],x,A[5],origin]; diag["a_slides"]+=1
                else:
                    A=[x,origin,None,None,-1,-1]; diag["a_restarts"]+=1

        if prev_red and cur_green:
            x=int(c[k-1]); origin=k-1; diag["v_levels"]+=1
            if V[0] is None:
                V=[x,origin,None,None,-1,-1]
            elif V[2] is None:
                if x > V[0]:
                    V=[None,-1,V[0],x,V[1],origin]
                else:
                    V=[x,origin,None,None,-1,-1]; diag["v_restarts"]+=1
            else:
                if x > V[3]:
                    V=[None,-1,V[3],x,V[5],origin]; diag["v_slides"]+=1
                else:
                    V=[x,origin,None,None,-1,-1]; diag["v_restarts"]+=1

    if ix:
        order=np.argsort(np.asarray(ix,np.int64),kind="stable")
        return np.asarray(ix,np.int64)[order],np.asarray(sd,np.int8)[order],diag
    return np.empty(0,np.int64),np.empty(0,np.int8),diag

def main():
    st=time.monotonic()
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    parent_sha=sha256_file(Path(base.__file__).resolve())
    if parent_sha!=PARENT_SHA256:
        raise SystemExit(f"parent helper SHA mismatch: {parent_sha}")
    source_sha=sha256_file(args.source)
    if source_sha!=CANONICAL_SHA256:
        raise SystemExit(f"canonical January SHA mismatch: {source_sha}")

    df=pd.read_csv(args.source,compression="gzip",
                   usecols=["timestamp_ms_utc","ask_raw","bid_raw"],dtype=np.int64)
    df=df[(df.timestamp_ms_utc>=base.START)&(df.timestamp_ms_utc<base.END)]
    t=df.timestamp_ms_utc.to_numpy(np.int64)
    if len(t)!=4_205_709 or np.any(t[1:]<t[:-1]):
        raise SystemExit("Stage-A chronology/tick-count mismatch")
    a,b=base.p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64))

    results={}
    survivors=[]
    for name,fam,tf in LANES:
        z=base.bars(t,b,tf)
        if fam=="123":
            sx,ss,diag=signals_123(t,a,b,z)
        else:
            sx,ss,diag=signals_msnr(t,a,b,z)
        metrics,_=base.pack(sx,ss,t,a,b)
        gate={
            "minimum_trades_20":metrics["trades"]>=20,
            "minimum_distinct_days_5":metrics["distinct_days"]>=5,
            "direct_net_nonnegative":metrics["direct_net_usd"]>=0,
        }
        gate["screen_pass"]=all(gate.values())
        if gate["screen_pass"]: survivors.append(name)
        results[name]={"family":fam,"bar_ms":tf,"metrics":metrics,"diagnostics":diag,"gate":gate}

    leader=None
    if survivors:
        leader=max(survivors,key=lambda n:(results[n]["metrics"]["direct_net_usd"],
                                          results[n]["metrics"]["official_wins"],
                                          results[n]["metrics"]["trades"]))
    out={
        "schema":"delta-r037-structural-state-machine-harvest-17cs-17cv-v1",
        "status":"COMPLETE_FAST_CAUSAL_STAGE_A_SCREEN",
        "unit":"R037_HIGH_VALUE_STRUCTURAL_STATE_MACHINE_HARVEST_CHECKPOINT_17CS_17CV",
        "parent_checkpoint":"R037_XECTSB_LEADER_INDEPENDENT_LATER_JAN_VALIDATION_CHECKPOINT_17CR",
        "prereg_commit":PREREG_COMMIT,
        "parent_helper_sha256":parent_sha,
        "source_sha256":source_sha,
        "stage_a_ticks":int(len(t)),
        "surface":"DUKAS_COINEXX_LIKE_P75",
        "results":results,
        "finding":{
            "survivors":survivors,
            "leader":leader,
            "decision":"ADVANCE_SURVIVOR_TO_LATER_JAN" if survivors else "RETIRE_ALL_AND_RESUME_HIGH_VALUE_HARVEST",
            "next":"R037_STRUCTURAL_SURVIVOR_INDEPENDENT_LATER_JAN_VALIDATION" if survivors else "R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST"
        },
        "numeric_retuning":False,
        "post_result_rescue":False,
        "august_accessed":False,
        "mql5_authorized":False,
        "runtime_seconds":round(time.monotonic()-st,3)
    }
    atomic(args.output,out)
    brief={}
    for n,r in results.items():
        m=r["metrics"]
        brief[n]={"trades":m["trades"],"days":m["distinct_days"],"wins":m["official_wins"],
                  "net":m["direct_net_usd"],"pass":r["gate"]["screen_pass"]}
    print(json.dumps({"lanes":brief,"finding":out["finding"],"runtime_seconds":out["runtime_seconds"]},
                     separators=(",",":")))

if __name__=="__main__":
    main()

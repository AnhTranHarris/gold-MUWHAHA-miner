#!/usr/bin/env python3
import argparse, hashlib, json, os, tempfile, time
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def atomic_json(path,obj):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=str(path.parent),prefix=path.name+".tmp.")
    with os.fdopen(fd,"w",encoding="utf-8") as f:
        json.dump(obj,f,indent=2,sort_keys=True,allow_nan=True); f.flush(); os.fsync(f.fileno())
    os.replace(tmp,path)

def buildX(s,h):
    hs=[250,500,1000,2000]+([3000] if h>=3000 else [])+([5000] if h>=5000 else [])+([10000] if h>=10000 else [])
    arr=[]; names=[]
    for H in hs:
        cur=s[f"h{H}_cur"].to_numpy(float); mfe=s[f"h{H}_mfe"].to_numpy(float); mae=s[f"h{H}_mae"].to_numpy(float)
        gb=s[f"h{H}_giveback"].to_numpy(float); tu=s[f"h{H}_turns"].to_numpy(float); ti=s[f"h{H}_ticks"].to_numpy(float)
        rn=s[f"h{H}_renew05"].to_numpy(float)
        vals=[cur,mfe,mae,gb,tu,ti,rn,(mfe-mae)/(mfe+mae+.02),np.abs(cur)/(mfe+mae+.02),tu/(ti+1),rn/(ti+1)]
        nms=["cur","mfe","mae","giveback","turns","ticks","renew","dom","pathq","turnrate","renewrate"]
        for a,n in zip(vals,nms):
            arr.append(np.nan_to_num(a,nan=0,posinf=0,neginf=0)); names.append(f"{n}_{H}")
    for a,b in zip(hs[:-1],hs[1:]):
        dt=(b-a)/1000.0
        for v in ["cur","mfe","mae","giveback","turns","ticks","renew05"]:
            aa=s[f"h{a}_{v}"].to_numpy(float); bb=s[f"h{b}_{v}"].to_numpy(float)
            arr.append(np.nan_to_num((bb-aa)/dt)); names.append(f"d_{v}_{a}_{b}")
    if len(hs)>=3:
        a,b,c=hs[-3:]
        s1=(s[f"h{b}_cur"].to_numpy(float)-s[f"h{a}_cur"].to_numpy(float))/((b-a)/1000.0)
        s2=(s[f"h{c}_cur"].to_numpy(float)-s[f"h{b}_cur"].to_numpy(float))/((c-b)/1000.0)
        arr.append(np.nan_to_num(s2-s1)); names.append("cur_accel_last")
    return np.column_stack(arr),names

def load(month,h,snapshot_dir,c20_dir):
    sp=snapshot_dir/f"pullback_lifecycle_snap_{month:02d}.pkl.gz"
    op=c20_dir/f"C20_LONG_ACTION_{month:02d}.pkl.gz"
    s=pd.read_pickle(sp,compression="gzip").sort_values("time_ms").reset_index(drop=True)
    o=pd.read_pickle(op,compression="gzip").sort_values("time_ms").reset_index(drop=True)
    cols=["time_ms",f"d{h}_decision_ms",f"d{h}_cont_pnl",f"d{h}_cont_exit_ms",f"d{h}_fade_pnl",f"d{h}_fade_exit_ms"]
    z=s.merge(o[cols],on="time_ms",how="inner")
    z=z.rename(columns={f"d{h}_decision_ms":"decision_ms",f"d{h}_cont_pnl":"cont_pnl",f"d{h}_cont_exit_ms":"cont_exit_ms",
                        f"d{h}_fade_pnl":"fade_pnl",f"d{h}_fade_exit_ms":"fade_exit_ms"})
    X,names=buildX(z,h)
    return z,X,names,sp,op

def replay(z,act):
    dec=z.decision_ms.to_numpy(np.int64); order=np.argsort(dec,kind="stable")
    cp=z.cont_pnl.to_numpy(float); fp=z.fade_pnl.to_numpy(float)
    ce=z.cont_exit_ms.to_numpy(np.int64); fe=z.fade_exit_ms.to_numpy(np.int64)
    free=-1; xs=[]; aa=[]
    for k in order:
        if act[k]==0 or dec[k]<=free: continue
        p=cp[k] if act[k]>0 else fp[k]; ex=ce[k] if act[k]>0 else fe[k]
        if not np.isfinite(p) or ex<0: continue
        xs.append(p); aa.append(act[k]); free=int(ex)
    x=np.asarray(xs,float)
    gp=float(x[x>0].sum()) if len(x) else 0.0; gl=float(x[x<0].sum()) if len(x) else 0.0
    return {"trades":int(len(x)),"net":float(x.sum()) if len(x) else 0.0,
            "pf":float(gp/-gl) if gl<0 else 1e9,
            "fade":float((np.asarray(aa)==-1).mean()) if aa else 0.0}

def main():
    ap=argparse.ArgumentParser(description="Bounded C22 trajectory router unit.")
    ap.add_argument("--h",type=int,choices=[3000,5000,10000],required=True)
    ap.add_argument("--arch",choices=["PAIR","CLASS"],required=True)
    ap.add_argument("--snapshot-dir",default=os.environ.get("R9_SNAPSHOT_DIR","/mnt/data/r9_research_v2/pullback_lifecycle2"))
    ap.add_argument("--c20-dir",default=os.environ.get("R9_C20_DIR","/mnt/data/C20_long_action"))
    ap.add_argument("--out-dir",default=os.environ.get("R9_C22_OUT_DIR","/mnt/data/C22_traj_bounded"))
    args=ap.parse_args()
    h=args.h; arch=args.arch; months=[1,2,3]
    snapshot_dir=Path(args.snapshot_dir); c20_dir=Path(args.c20_dir); out_dir=Path(args.out_dir); out_dir.mkdir(parents=True,exist_ok=True)
    job=f"C22_TRAJ_h{h}_{arch}"; manifest=out_dir/f"{job}.json"
    started=time.time()
    atomic_json(manifest,{"job_id":job,"status":"STARTED","h":h,"arch":arch,"started_epoch":started})

    data={}; X={}; inputs=[]; names=None
    for m in months:
        data[m],X[m],names,sp,op=load(m,h,snapshot_dir,c20_dir)
        inputs += [{"path":str(sp),"sha256":sha256(sp)},{"path":str(op),"sha256":sha256(op)}]

    rows=[]
    for depth in [2,3,4]:
        for leaf in [500,800,1200]:
            pred={}
            for tm in months:
                trs=[m for m in months if m!=tm]
                XX=np.vstack([X[m] for m in trs])
                zz=pd.concat([data[m] for m in trs],ignore_index=True)
                yc=zz.cont_pnl.to_numpy(float); yf=zz.fade_pnl.to_numpy(float)
                ok=np.isfinite(yc)&np.isfinite(yf); XX=XX[ok]; yc=yc[ok]; yf=yf[ok]
                if arch=="PAIR":
                    mc=DecisionTreeRegressor(max_depth=depth,min_samples_leaf=leaf,random_state=41).fit(XX,yc)
                    mf=DecisionTreeRegressor(max_depth=depth,min_samples_leaf=leaf,random_state=41).fit(XX,yf)
                    pc=mc.predict(X[tm]); pf=mf.predict(X[tm]); pred[tm]=(np.maximum(pc,pf),pf-pc)
                else:
                    y=(yf>yc).astype(np.int8)
                    cl=DecisionTreeClassifier(max_depth=depth,min_samples_leaf=leaf,random_state=41).fit(XX,y)
                    pro=cl.predict_proba(X[tm]); classes=list(cl.classes_)
                    p1=pro[:,classes.index(1)] if 1 in classes else np.zeros(len(X[tm])); pred[tm]=p1
            thrs=[0,.05,.10,.15] if arch=="PAIR" else [.52,.55,.58,.60,.62]
            for thr in thrs:
                mets=[]
                for tm in months:
                    if arch=="PAIR":
                        best,diff=pred[tm]; act=np.where(best>=thr,np.where(diff>0,-1,1),0)
                    else:
                        p=pred[tm]; conf=np.maximum(p,1-p); act=np.where(conf>=thr,np.where(p>.5,-1,1),0)
                    mets.append(replay(data[tm],act))
                rows.append({"h":h,"arch":arch,"depth":depth,"leaf":leaf,"threshold":thr,
                             "all_positive":all(z["net"]>0 for z in mets),
                             "total_net":sum(z["net"] for z in mets),"min_month":min(z["net"] for z in mets),
                             "trades":sum(z["trades"] for z in mets),
                             "jan":mets[0]["net"],"feb":mets[1]["net"],"mar":mets[2]["net"],
                             "jan_pf":mets[0]["pf"],"feb_pf":mets[1]["pf"],"mar_pf":mets[2]["pf"],
                             "jan_fade":mets[0]["fade"],"feb_fade":mets[1]["fade"],"mar_fade":mets[2]["fade"]})
    out=pd.DataFrame(rows).sort_values(["all_positive","min_month","total_net"],ascending=[False,False,False])
    csv=out_dir/f"{job}.csv"; tmp=Path(str(csv)+".tmp"); out.to_csv(tmp,index=False); os.replace(tmp,csv)
    best=out.iloc[0].to_dict()
    final={"job_id":job,"status":"COMPLETED_LOCAL","h":h,"arch":arch,"rows":int(len(out)),
           "all_positive_count":int(out.all_positive.sum()),"best":best,"feature_count":int(len(names)),
           "elapsed_seconds":time.time()-started,"inputs":inputs,"output":str(csv),"output_sha256":sha256(csv)}
    atomic_json(manifest,final)
    print(json.dumps(final,indent=2,allow_nan=True))

if __name__=="__main__": raise SystemExit(main())

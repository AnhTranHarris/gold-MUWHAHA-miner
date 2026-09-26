#!/usr/bin/env python3
"""MM-C30-B0: original-R9 +2s survivor hazard discovery.
Jan-Mar cross-month OOF only. KEEP original R9 vs CLOSE at +2s.
No entry deletion, direction flip, or future/SYNTH input.
"""
from pathlib import Path
import argparse, hashlib, json, numpy as np, pandas as pd
from sklearn.tree import DecisionTreeRegressor

def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def maxdd(x):
    x=np.asarray(x,float)
    if not len(x): return 0.0
    c=np.cumsum(x); peak=np.maximum.accumulate(np.r_[0,c])[:-1]
    return float(np.max(peak-c))

def metrics(x):
    x=np.asarray(x,float); gp=float(x[x>0].sum()) if len(x) else 0.; gl=float(x[x<0].sum()) if len(x) else 0.
    return {"trades":int(len(x)),"net":float(x.sum()),"gp":gp,"gl":gl,
            "pf":float(gp/-gl) if gl<0 else 1e9,"win":float((x>0).mean()) if len(x) else 0.,"maxdd":maxdd(x)}

def load(root,m):
    ec=pd.read_pickle(root/f"event_clock_{m:02d}_fixed_outcomes.pkl.gz",compression="gzip")
    ev=pd.read_pickle(root/f"events_{m:02d}_v2_recovery.pkl.gz",compression="gzip")
    pre=["time_ms","base_hold","rearm","s1_disp_al","s1_eff","s1_range","s1_turns","s1_tickratio","atr_m5",
         "align_pos_count","align_strong_count","align_min","align_mean","align_max",
         "dc0p15_pol_al","dc0p15_age","dc0p15_overshoot","dc0p3_pol_al","dc0p3_age","dc0p3_overshoot"]
    z=ec.merge(ev[pre],on="time_ms",how="left")
    z=z[(z.base_hold>=2.0)&z.h2000_last.notna()].copy()
    z["close2_pnl"]=z.h2000_last.astype(float)-0.20
    z["keep_pnl"]=z.base_pnl.astype(float)
    X=pd.DataFrame(index=z.index); hs=[250,500,1000,2000]
    for h in hs:
        last=z[f"h{h}_last"].astype(float); mfe=z[f"h{h}_mfe"].astype(float); mae=z[f"h{h}_mae"].astype(float)
        travel=z[f"h{h}_travel"].astype(float); eff=z[f"h{h}_eff"].astype(float)
        turns=z[f"h{h}_turns"].astype(float); ticks=z[f"h{h}_ticks"].astype(float)
        rec=z[f"h{h}_recross"].astype(float); rf=z[f"h{h}_renew_f"].astype(float); ra=z[f"h{h}_renew_a"].astype(float)
        X[f"cur_{h}"]=last; X[f"mfe_{h}"]=mfe; X[f"mae_{h}"]=mae; X[f"giveback_{h}"]=mfe-last
        X[f"travel_{h}"]=travel; X[f"eff_{h}"]=eff; X[f"turnrate_{h}"]=turns/(ticks+1)
        X[f"recrossrate_{h}"]=rec/(ticks+1); X[f"renewf_rate_{h}"]=rf/(ticks+1); X[f"renewa_rate_{h}"]=ra/(ticks+1)
        X[f"dominance_{h}"]=(mfe-mae)/(mfe+mae+.02); X[f"pathq_{h}"]=np.abs(last)/(travel+.02)
    for a,b in zip(hs[:-1],hs[1:]):
        dt=(b-a)/1000.
        X[f"velocity_{a}_{b}"]=(z[f"h{b}_last"].astype(float)-z[f"h{a}_last"].astype(float))/dt
        X[f"mfe_growth_{a}_{b}"]=(z[f"h{b}_mfe"].astype(float)-z[f"h{a}_mfe"].astype(float))/dt
        X[f"mae_growth_{a}_{b}"]=(z[f"h{b}_mae"].astype(float)-z[f"h{a}_mae"].astype(float))/dt
        X[f"turn_growth_{a}_{b}"]=(z[f"h{b}_turns"].astype(float)-z[f"h{a}_turns"].astype(float))/dt
    for c in pre:
        if c not in ("time_ms","base_hold"): X["pre_"+c]=z[c].astype(float)
    return z.reset_index(drop=True),X.replace([np.inf,-np.inf],np.nan).fillna(0.).reset_index(drop=True)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--root",default="/mnt/data/mmc30b_preflight"); ap.add_argument("--out",default="/mnt/data/MM_C30_B_SURVIVOR_HAZARD")
    a=ap.parse_args(); root=Path(a.root); out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    D={};X={}
    for m in (1,2,3): D[m],X[m]=load(root,m)
    rows=[]
    for depth in (2,3,4):
      for leaf in (750,1000,1500):
        pred={}
        for tm in (1,2,3):
          tr=[m for m in (1,2,3) if m!=tm]; XX=pd.concat([X[m] for m in tr],ignore_index=True); zz=pd.concat([D[m] for m in tr],ignore_index=True)
          y=np.clip(zz.close2_pnl.to_numpy(float)-zz.keep_pnl.to_numpy(float),-3,3)
          pred[tm]=DecisionTreeRegressor(max_depth=depth,min_samples_leaf=leaf,random_state=73).fit(XX,y).predict(X[tm])
        for thr in (0,.03,.05,.08,.10,.15,.20):
          r={"depth":depth,"leaf":leaf,"threshold":thr}; ok=True; td=tg=0.; mn=1e9; gre=[]
          for tm in (1,2,3):
            z=D[tm]; h=pred[tm]>=thr; vals=np.where(h,z.close2_pnl,z.keep_pnl); b=metrics(z.keep_pnl); c=metrics(vals)
            dn=c["net"]-b["net"]; dg=c["gl"]-b["gl"]; gr=c["gp"]/b["gp"]; dd=c["maxdd"]-b["maxdd"]
            r.update({f"m{tm}_net":c["net"],f"m{tm}_delta":dn,f"m{tm}_gp":c["gp"],f"m{tm}_gl":c["gl"],f"m{tm}_gp_ret":gr,f"m{tm}_dd":c["maxdd"],f"m{tm}_base_dd":b["maxdd"],f"m{tm}_harvested":int(h.sum()),f"m{tm}_survivors":len(z)})
            ok &= dn>0 and dg>0 and gr>=.95 and dd<0; td+=dn; tg+=dg; mn=min(mn,dn); gre.append(gr)
          r.update(all_month_pass=bool(ok),total_delta=td,total_gl_improvement=tg,min_month_delta=mn,min_gp_ret=min(gre)); rows.append(r)
    G=pd.DataFrame(rows).sort_values(["all_month_pass","min_month_delta","total_delta"],ascending=[False,False,False])
    G.to_csv(out/"MM_C30_B_DISCOVERY_GRID.csv",index=False)
    best=G.iloc[0]
    result={"job_id":"MM-C30-B0-SURVIVOR-HAZARD-DISCOVERY","status":"COMPLETED_LOCAL","pass":bool(best.all_month_pass),
            "best":best.to_dict(),"scientific_scope":"Jan-Mar cross-month OOF discovery; original R9 +2s survivors; not exact Section73 promoted subset.",
            "inputs":{str(root/f"event_clock_{m:02d}_fixed_outcomes.pkl.gz"):sha256(root/f"event_clock_{m:02d}_fixed_outcomes.pkl.gz") for m in (1,2,3)}}
    with open(out/"MM_C30_B_DISCOVERY_RESULT_MIN.json","w") as f: json.dump(result,f,indent=2,default=lambda x:x.item() if hasattr(x,"item") else str(x))
    print(json.dumps(result,indent=2,default=lambda x:x.item() if hasattr(x,"item") else str(x)))
if __name__=="__main__": main()

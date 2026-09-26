import pandas as pd, numpy as np, json, pathlib, time, hashlib
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import roc_auc_score
ROOT=pathlib.Path('/mnt/data')
R120=ROOT/'MM_C30_B1_R120_CONTEXT'
PRE=ROOT/'mmc30b_preflight'
OUT=ROOT/'MM_C30_B1_LATE_FAILURE'
OUT.mkdir(exist_ok=True)
months=(1,2,3)
checkpoints=(3000,5000)

def maxdd(x):
    x=np.asarray(x,float)
    if not len(x): return 0.0
    c=np.cumsum(x); peak=np.maximum.accumulate(np.r_[0.,c])[:-1]
    return float(np.max(peak-c))

def metrics(x):
    x=np.asarray(x,float); gp=float(x[x>0].sum()) if len(x) else 0.; gl=float(x[x<0].sum()) if len(x) else 0.
    return dict(trades=int(len(x)),net=float(x.sum()) if len(x) else 0.,gp=gp,gl=gl,
                pf=float(gp/-gl) if gl<0 else 1e9,win=float((x>0).mean()) if len(x) else 0.,maxdd=maxdd(x))

def build_month(m,h):
    r=pd.read_pickle(R120/f'MM_C30_B1_R120_M{m:02d}.pkl.gz',compression='gzip')
    e=pd.read_pickle(PRE/f'event_clock_{m:02d}_fixed_outcomes.pkl.gz',compression='gzip')
    v=pd.read_pickle(PRE/f'events_{m:02d}_v2_recovery.pkl.gz',compression='gzip')[['time_ms','base_hold']]
    cols=['time_ms','base_pnl','h2000_last','h2000_mfe','h2000_mae','h2000_travel','h2000_eff','h2000_turns','h2000_ticks','h2000_recross','h2000_renew_f','h2000_renew_a',
          f'h{h}_last',f'h{h}_mfe',f'h{h}_mae',f'h{h}_travel',f'h{h}_eff',f'h{h}_turns',f'h{h}_ticks',f'h{h}_recross',f'h{h}_renew_f',f'h{h}_renew_a']
    z=r.merge(e[cols],on='time_ms',how='inner').merge(v,on='time_ms',how='left')
    sec=h/1000.0
    z=z[(z.base_hold>=sec)&z[f'h{h}_last'].notna()].sort_values('time_ms').reset_index(drop=True)
    z['keep_pnl']=z.base_pnl.astype(float)
    z['close_pnl']=z[f'h{h}_last'].astype(float)-0.20
    # Retain only prior +2s rolling tape features plus causal post-2s path evolution.
    rcols=[c for c in r.columns if c.startswith('r120_') or c.endswith('_share') or c.startswith('disp_')]
    X=z[rcols].astype(float).copy()
    for k in ['last','mfe','mae','travel','eff','turns','ticks','recross','renew_f','renew_a']:
        X[f'path_{k}_{h}']=z[f'h{h}_{k}'].astype(float)
    X[f'giveback_{h}']=z[f'h{h}_mfe'].astype(float)-z[f'h{h}_last'].astype(float)
    dt=(h-2000)/1000.0
    for k in ['last','mfe','mae','travel','turns','ticks','recross','renew_f','renew_a']:
        X[f'd_{k}_2s_to_{h}']=(z[f'h{h}_{k}'].astype(float)-z[f'h2000_{k}'].astype(float))/dt
    X[f'd_eff_2s_to_{h}']=(z[f'h{h}_eff'].astype(float)-z['h2000_eff'].astype(float))/dt
    X[f'giveback_growth_2s_to_{h}']=((z[f'h{h}_mfe']-z[f'h{h}_last'])-(z.h2000_mfe-z.h2000_last))/dt
    X=X.replace([np.inf,-np.inf],np.nan).fillna(0.)
    D=z[['time_ms','keep_pnl','close_pnl']].copy()
    return D,X

def evaluate(h):
    D={}; X={}
    for m in months: D[m],X[m]=build_month(m,h)
    rows=[]; pred_cache={}
    for depth in (2,3,4):
      for leaf in (750,1000,1500):
        preds={}
        for tm in months:
          tr=[m for m in months if m!=tm]
          XX=pd.concat([X[m] for m in tr],ignore_index=True)
          zz=pd.concat([D[m] for m in tr],ignore_index=True)
          y=np.clip(zz.close_pnl.to_numpy(float)-zz.keep_pnl.to_numpy(float),-3,3)
          mod=DecisionTreeRegressor(max_depth=depth,min_samples_leaf=leaf,random_state=735+h).fit(XX,y)
          preds[tm]=mod.predict(X[tm])
        for thr in (0,.03,.05,.08,.10,.15,.20):
          rec={'checkpoint_ms':h,'depth':depth,'leaf':leaf,'threshold':thr}; ok=True; total_delta=0.; total_gl=0.; minret=10.; closes=0
          for tm in months:
            z=D[tm]; flag=preds[tm]>=thr
            vals=np.where(flag,z.close_pnl.to_numpy(float),z.keep_pnl.to_numpy(float))
            b=metrics(z.keep_pnl); c=metrics(vals)
            dn=c['net']-b['net']; dgl=c['gl']-b['gl']; ret=c['gp']/b['gp'] if b['gp'] else 1.; ddd=c['maxdd']-b['maxdd']
            rec.update({f'm{tm}_net':c['net'],f'm{tm}_delta':dn,f'm{tm}_gl_improve':dgl,f'm{tm}_gp_ret':ret,f'm{tm}_dd_delta':ddd,f'm{tm}_close':int(flag.sum()),f'm{tm}_survivors':len(z)})
            ok &= (dn>0 and dgl>0 and ret>=.95 and ddd<0 and flag.sum()>0)
            total_delta+=dn; total_gl+=dgl; minret=min(minret,ret); closes+=int(flag.sum())
          rec.update(all_month_pass=bool(ok),total_delta=total_delta,total_gl_improvement=total_gl,min_gp_ret=minret,total_close=closes)
          rows.append(rec)
    grid=pd.DataFrame(rows).sort_values(['all_month_pass','total_delta','total_gl_improvement'],ascending=[False,False,False])
    # Diagnostic AUC using one frozen capacity model per holdout, not used to select OOS months.
    aucs={}; top={}
    for tm in months:
      tr=[m for m in months if m!=tm]
      XX=pd.concat([X[m] for m in tr],ignore_index=True); zz=pd.concat([D[m] for m in tr],ignore_index=True)
      y=np.clip(zz.close_pnl.to_numpy(float)-zz.keep_pnl.to_numpy(float),-3,3)
      mod=DecisionTreeRegressor(max_depth=3,min_samples_leaf=1000,random_state=735+h).fit(XX,y)
      p=mod.predict(X[tm]); yy=(D[tm].close_pnl.to_numpy()>D[tm].keep_pnl.to_numpy()).astype(int)
      aucs[str(tm)]=float(roc_auc_score(yy,p))
      imp=np.argsort(mod.feature_importances_)[::-1][:10]
      top[str(tm)]=[(X[tm].columns[i],float(mod.feature_importances_[i])) for i in imp if mod.feature_importances_[i]>0]
    return D,X,grid,aucs,top

t0=time.time(); results={}; grids=[]
for h in checkpoints:
    D,X,g,aucs,top=evaluate(h); grids.append(g)
    best=g.iloc[0].to_dict()
    results[str(h)]={'best':best,'pass':bool(best['all_month_pass']),'auc_close_better':aucs,'top_features':top,
                     'baseline':{str(m):metrics(D[m].keep_pnl) for m in months}}
allgrid=pd.concat(grids,ignore_index=True).sort_values(['all_month_pass','total_delta','total_gl_improvement'],ascending=[False,False,False])
allgrid.to_csv(OUT/'MM_C30_B1_LATE_FAILURE_GRID.csv',index=False)
best=allgrid.iloc[0].to_dict()
out={'job_id':'MM-C30-B1A-LATE-FAILURE-OBSERVABILITY','status':'COMPLETED_LOCAL','scope':'Jan-Mar original-R9 trades alive at checkpoint; +2s rolling120 context plus causal 2s->3s/5s path evolution; KEEP original R9 vs CLOSE at checkpoint','checkpoints_ms':list(checkpoints),'criteria':'each month net>baseline, GL improves, GP retention>=95%, DD improves, at least one close','results':results,'best_overall':best,'pass':bool(best['all_month_pass']),'elapsed_seconds':time.time()-t0}
with open(OUT/'MM_C30_B1_LATE_FAILURE_RESULT.json','w') as f: json.dump(out,f,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x))
print(json.dumps(out,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x)))
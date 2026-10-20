#!/usr/bin/env python3
"""F35: published source-feature phase-transition and HTF structural accelerations; actual original Jan/Feb/Jun/Jul cached tick engine.
Research only, read-only parent 76-vector; derivative features use strictly earlier event frames. Frozen Feb selector.
"""
from pathlib import Path
import sys,time,json,io,zipfile
import numpy as np
from lightgbm import LGBMClassifier
from joblib import dump
ROOT=Path('/mnt/data');P=ROOT/'R00_054_F35_CAUSAL_STRUCTURE_PHASE_20261020';P.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'R00_054_F30_ITERATIVE_CAUSAL_FILTER_20261020'))
import F27_PARENT_READONLY_SOURCE as src
# verified 43: 0:9 historical returns, 9:12 price-path efficiencies,12:14 quote rates,14 spread,
# 15:18 tick imbalance,18:21 path vol,21:37 completed bar M1/M5/M15/H1,37:43 clock.
COLS=np.r_[0:9,9:12,12:14,14:15,15:18,18:21,21:37,43:47,47:48]
DELAYS=(5000,15000,30000,60000,300000)

def build(b,m):
  c=src.load_one(b,m);t=c['t'];X=c['X'];n=len(t)
  feat=[];names=[]
  for lag in DELAYS:
    k=np.searchsorted(t,t-lag,side='right')-1
    valid=k>=0;k=k.clip(min=0)
    dx=np.nan_to_num(X[:,COLS]-X[k][:,COLS],nan=0,posinf=0,neginf=0)
    dx[~valid]=0
    feat.append(dx.astype(np.float32));names.extend([f'change_{lag}_{i}' for i in COLS])
    feat.append(np.where(valid,(t-t[k])/1000,100000).astype(np.float32)[:,None]);names.append(f'age_{lag}')
    for j in (0,1,2,3):
      feat.append(np.where(valid,(X[:,43+j]!=X[k,43+j]),False).astype(np.float32)[:,None]);names.append(f'expert_transition_{lag}_{j}')
    feat.append(np.where(valid,(c['side']!=c['side'][k]),False).astype(np.float32)[:,None]);names.append(f'side_transition_{lag}')
  add=np.hstack(feat)
  c['X']=np.column_stack((X,add)).astype(np.float32);c['transition_columns']=names
  return c

def score(c,prob,cut,refs):
  m=prob>=cut;y=c['y'];g=y==0;bad=~g;q=src.quota_stats(c,m,refs)
  return dict(n=len(y),correct_total=int(g.sum()),bad_total=int(bad.sum()),kept_correct=int((g&m).sum()),rejected_bad=int((bad&~m).sum()),correct_retention=float(m[g].mean()),bad_rejection=float((~m[bad]).mean()),interval_failures={k:len(q[k]) for k in ('newly_failed_hours','newly_failed_days','newly_failed_weeks','newly_failed_months')})

def run():
  spec={'phase':'F35 frozen before any JuneJul transfer','feature_origin':'43 native/source + 4 expert + matured 76 original; lag derivative of pre-existing known-at source columns, completed HTF bars; no same-month labels as decision features','lag_ms':list(DELAYS),'original_indices':COLS.tolist(),'JAN':'first80% both independent broker streams, purge40s, every fifth event','FEB':'last35% calibration, R9 quota across full February, min 71% correct retention','JUN_JUL':'historically exposed transfer without per-month threshold tuning','models':['structural_transitions_only','transitions_plus_original'],'target':{'correct':0.71,'bad':0.90,'R9_interval_new_failures':0},'models_mql5_compatibility':'source features, transitions and LightGBM exported tree ensembles; no compiled MQL5 yet'}
  (P/'F35_PREDECLARED_CONTRACT.json').write_text(json.dumps(spec,indent=2)+'\n')
  refs=src.r9_reference();jan={b:build(b,'01') for b in src.BROKERS};k0=jan['coinexx']['X'].shape[1]
  arr=[];label=[]
  for b,c in jan.items():
    ix=np.flatnonzero(c['t']<c['t'][int(len(c['y'])*.8)]-40000)[::5]
    arr.append(c['X'][ix]);label.append((c['y'][ix]==0).astype('int8'))
  X=np.concatenate(arr);y=np.concatenate(label);print('F35 fit sample',X.shape,flush=True)
  models={}
  for modelname,cols,params in [('structural_transitions_only',np.arange(76,k0),dict(num_leaves=43,n_estimators=150)),('transitions_plus_original',np.arange(k0),dict(num_leaves=63,n_estimators=180))]:
    classifier=LGBMClassifier(**params,learning_rate=.042,min_child_samples=125,reg_lambda=10,colsample_bytree=.80,n_jobs=3,random_state=54035,verbosity=-1)
    classifier.fit(X[:,cols],y)
    dump(dict(model=classifier,columns=cols),P/f'F35_MODEL_{modelname}.joblib',compress=3)
    models[modelname]=(classifier,cols)
  del jan,arr,label,X,y
  feb={b:build(b,'02') for b in src.BROKERS}
  scored={b:{name:model.predict_proba(c['X'][:,cols])[:,1] for name,(model,cols) in models.items()} for b,c in feb.items()}
  freeze={};grid=[]
  for name in models:
    val={b:np.arange(len(c['t']))>=int(len(c['t'])*.65) for b,c in feb.items()}
    dist=np.concatenate([scored[b][name][val[b]] for b in src.BROKERS]);choices=[]
    for quant in np.arange(0,.601,.04):
      thr=float(np.quantile(dist,quant));rows=[]
      for b,c in feb.items():
        base=score(c,scored[b][name],thr,refs)
        z=c['y'][val[b]]==0;mask=scored[b][name][val[b]]>=thr
        rows.append(dict(b=b,correct_retention_on_feb_last35=float(mask[z].mean()),incorrect_rejection_on_feb_last35=float((~mask[~z]).mean()),feb_full=base))
      valid=all(r['correct_retention_on_feb_last35']>=.71 and not any(r['feb_full']['interval_failures'].values()) for r in rows)
      rec=dict(name=name,quantile=round(float(quant),3),threshold=thr,valid=valid,brokers=rows)
      grid.append(rec)
      if valid:choices.append(rec)
    freeze[name]=max(choices,key=lambda x:min(y['incorrect_rejection_on_feb_last35'] for y in x['brokers'])) if choices else None
  (P/'F35_ALL_FEB_CANDIDATES.json').write_text(json.dumps(grid,indent=2)+'\n')
  (P/'F35_FEB_FROZEN_CHOICES.json').write_text(json.dumps(freeze,indent=2)+'\n')
  del feb,scored
  results=[];saved_scores={}
  for m in ('06','07'):
    for b in src.BROKERS:
      c=build(b,m)
      for name,(model,cols) in models.items():
        s=model.predict_proba(c['X'][:,cols])[:,1]
        # Store compressed for independent exhaustive oracle geometry, not training/promotion
        np.savez_compressed(P/f'F35_SCORES_{b}_{m}_{name}.npz',t=c['t'],side=c['side'],y=c['y'],p=s.astype(np.float32))
        if freeze[name]:
          result=score(c,s,freeze[name]['threshold'],refs)
          results.append(dict(month=m,broker=b,name=name,freeze_threshold=freeze[name]['threshold'],**result))
          print('F35',m,b,name,round(result['correct_retention'],4),round(result['bad_rejection'],4),sum(result['interval_failures'].values()),flush=True)
      del c
  aggregate=[]
  for name in models:
    rows=[r for r in results if r['name']==name]
    if len(rows)!=4:continue
    a=sum(r['kept_correct'] for r in rows);g=sum(r['correct_total'] for r in rows)
    rej=sum(r['rejected_bad'] for r in rows);bad=sum(r['bad_total'] for r in rows)
    agg=dict(name=name,correct_kept=a,correct_total=g,rejected_bad=rej,bad_total=bad,correct_retention=a/g,incorrect_rejection=rej/bad,interval_failures=sum(sum(r['interval_failures'].values()) for r in rows),passes_all=all(r['correct_retention']>=.71 and r['bad_rejection']>=.90 and not any(r['interval_failures'].values()) for r in rows))
    aggregate.append(agg)
  (P/'F35_EXPOSED_TRANSFER_DETAILS.json').write_text(json.dumps(results,indent=2)+'\n')
  (P/'F35_EXPOSED_TRANSFER_AGGREGATE.json').write_text(json.dumps(aggregate,indent=2)+'\n')
  print('F35 AGGREGATE',json.dumps(aggregate,indent=2),flush=True)
if __name__=='__main__':run()
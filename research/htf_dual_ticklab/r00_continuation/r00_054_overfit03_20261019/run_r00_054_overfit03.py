#!/usr/bin/env python3
"""Additive intentionally overfit discovery on R00-054 ORIGINAL preserved decisions.

NOT a trading filter or blind result. Original Jan/Feb/Jun/Jul, no EA/engine writes.
The June-July month labels are deliberately used to fit a model; tests on those
months are in-sample/temporally overlapping, NEVER promote. February is backward
historical diagnostic only. All features are decision-time causal. All original
raw decisions and outcome labels stay immutable. Quote change counts != volume.
"""
from __future__ import annotations
import io, zipfile, hashlib, csv, json, time, math, sys
from pathlib import Path
import numpy as np
import lightgbm as lgb
from joblib import dump
import pandas as pd

ROOT=Path('/mnt/data');OUT=ROOT/'R00_054_OVERFIT03_DISCOVERY';OUT.mkdir(exist_ok=True)
CORE=ROOT/'R00_054_055_NATIVE_RESEARCH_COMPLETE_CORE_20261018.zip'
R=ROOT/'R00_054_VALIDATION/continuation_results'
MONTHS=['06','07'];BRS=['coinexx','dukascopy'];Q=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
PLAN={
 'identity':'R00-054-OVERFIT03, intentionally exposed month label-fed diagnostic, NOT promotion',
 'election':'Immutable R00-054 native quote weighted-oracle, two brokers independently',
 'design':'High-capacity LightGBM meta-correctness detector on known June and July 2026 original events; month Feb reverse transfer',
 'fitting':'Use at most every seventh row from each June/July broker-month; rest same-month temporally overlapping; no blind claim',
 'features':'R00-054 43 causal previous tick/completed HTF, experts state, side-relative transformations, signed quote response, time/session, causal previous +32s outcomes',
 'filter':'Keep original BUY/SELL when meta model high probability. Never retime, reverse, or modify original labels.',
 'criteria':'Explore score quantiles and maximum 90% original R9 SYNTH correctly directed hourly supply without claiming trades; measure correct loss, wrong removed and false rejection',
 'target':'Seek >25% relative precision improvement and eventual 80%, but never assert unless actually measured; retention vs R9 floor',
 'governance':'Overfit used for hypothesis mining, February backwards check is NOT blind, June/July already historically exposed',
 'no_pnl':True,
 'seed':5403,
 'algorithm':dict(n_estimators=520,num_leaves=127,learning_rate=.13,min_child_samples=7,max_depth=-1, colsample_bytree=.95,reg_lambda=.08,max_bin=255,random_state=5403,n_jobs=4,verbosity=-1)
}
(OUT/'FROZEN_DISCOVERY_PLAN.json').write_text(json.dumps(PLAN,indent=2)+'\n')

def get(b,m):
 path=ROOT/f'R00_054_NATIVE_CACHE_{b}_{m}.zip'
 with zipfile.ZipFile(path) as z:
  if z.testzip() is not None:raise AssertionError('ARCHIVE CRC ERROR')
  n=[n for n in z.namelist() if n.endswith('.npz')];assert len(n)==1
  with np.load(io.BytesIO(z.read(n[0])),allow_pickle=False) as v:d={k:v[k].copy() for k in v.files}
 with np.load(R/f'FROZEN_R00_054_EVENTS_{b}_{m}.npz',allow_pickle=False) as v:orig={k:v[k].copy() for k in v.files}
 assert np.array_equal(d['t'],orig['t'])
 assert np.array_equal((np.isfinite(d['d30'])&(d['d30']*orig['side']>.10)).astype('int8'),orig['correct'])
 assert set(np.unique(orig['side'])) <= {-1,1}
 return d,orig

def matured(t,correct,side):
 # only original event outcomes whose +32s age has fully matured may be included
 idx=np.searchsorted(t,t-32_001,side='right')
 c=np.r_[0,np.cumsum(correct,dtype=np.int64)]
 n=len(t);out=[]
 for sec in [120,600,3600]:
  lo=np.searchsorted(t,t-sec*1000,side='left')
  cnt=idx-lo; win=c[idx]-c[lo]
  out.extend([np.where(cnt>=3,(win+2)/(cnt+4),.5), np.log1p(np.maximum(cnt,0))])
 prev=np.maximum(idx-1,0)
 out.extend([np.where(idx>0,side[prev]*side,0), np.log1p(np.clip(np.where(idx>0,(t-t[prev])/1000,3600),0,3600))])
 return np.column_stack(out).astype(np.float32)

def features(d,r):
 base=d['features'].astype(np.float32); base[~np.isfinite(base)]=-999
 side=r['side'].astype(np.float32)
 experts=d['experts'].T.astype(np.float32)
 signed=base[:,[0,1,2,3,4,5,6,7,8,15,16,17]]*side[:,None]
 stm=base[:,21:37];body=stm[:,[0,4,8,12]]*side[:,None];rg=stm[:,[1,5,9,13]]
 t=r['t'];hod=(t//3_600_000)%24;dow=(t//86_400_000+3)%7
 cyc=np.column_stack([np.sin(hod*(2*np.pi/24)),np.cos(hod*(2*np.pi/24)),np.sin(dow*(2*np.pi/7)),np.cos(dow*(2*np.pi/7)),(hod>=13)&(hod<=17),(hod>=22)|(hod<=1)]).astype(np.float32)
 inter=np.column_stack([side,experts*side[:,None], signed[:,3]-signed[:,6], signed[:,1]-signed[:,4],body[:,0]-body[:,2],body[:,1]-body[:,3],np.log1p(np.maximum(base[:,14],0)),np.log1p(np.maximum(base[:,18],0)),body/(rg+.1)]).astype(np.float32)
 hist=matured(t,r['correct'].astype(np.int8),r['side'])
 # Hierarchical groups for honest feature audit
 x=np.column_stack([base,signed,experts,cyc,inter,hist]).astype(np.float32)
 names=([f'original_past_feature_{i:02}' for i in range(43)]+[f'side_relative_return_{i:02}' for i in [0,1,2,3,4,5,6,7,8,15,16,17]]+[f'published_expert_state_{i}' for i in range(4)]+['hour_sin','hour_cos','dayweek_sin','dayweek_cos','ny_overlap_13_17','rollover_22_01']+['original_side']+[f'expert_side_agreement_{i}' for i in range(4)]+['momentum_fast_slow','momentum_short_medium','M1_M15_disagreement','M5_H1_disagreement','spread_log','quote_intensity_log']+[f'body_vs_range_{i}' for i in range(4)]+[f'matured_feedback_{i}' for i in range(8)])
 assert len(names)==x.shape[1],(len(names),x.shape)
 return x,names

def perf(p,y,idx=None):
 if idx is not None:p=p[idx];y=y[idx]
 return dict(n=int(len(y)),correct=int(y.sum()),accuracy=float(y.mean()), score_accuracy=float(np.mean((p>=.5)==y)),roc_auc=float(__import__('sklearn.metrics',fromlist=['roc_auc_score']).roc_auc_score(y,p)) if np.unique(y).size==2 else None)

def intervals(b,t,accept,cor):
 with pd.read_csv(R/'R00_054_CONTIGUOUS_UTC_HOURLY.csv.gz',compression='gzip',chunksize=8000) as it:
  ref=pd.concat([x[(x.broker==b)&x.eligible_reference] for x in it],ignore_index=True)
 hours=t//3600000;u,inv=np.unique(hours,return_inverse=True)
 a=np.bincount(inv,weights=accept.astype(np.int8),minlength=len(u))
 c=np.bincount(inv,weights=(accept&cor).astype(np.int8),minlength=len(u))
 lookup={int(k):(int(aa),int(cc)) for k,aa,cc in zip(u,a,c)}
 passed=0;fails=[]
 # evaluate ONLY benchmark hours corresponding to processed source months; no invented missing quotes
 covered_months=set(pd.to_datetime(t,unit='ms',utc=True).strftime('%Y-%m').unique())
 for row in ref.itertuples(index=False):
  dt=pd.Timestamp(int(row.hour_key)*3_600_000,unit='ms',tz='UTC')
  if dt.strftime('%Y-%m') not in covered_months:continue
  got=lookup.get(int(row.hour_key),(0,0));req=math.ceil(.9*row.r9_synth_completed_trades-1e-12)
  if got[0]>=req and got[1]>=req:passed+=1
  else:fails.append(dict(utc_hour=str(dt),required=req,emitted=got[0],correct=got[1]))
 return passed, len(fails), fails[:30]

def scorings(b,model,month,kind,thresholds, train_indices=None):
 d,r=get(b,month);X,names=features(d,r)
 p=model.predict_proba(X)[:,1].astype(np.float32);y=r['correct'].astype(bool)
 rows=[]
 for q,th in thresholds.items():
  keep=p>=th
  good=int((keep&y).sum()); rejectbad=int((~keep&~y).sum());lost=int((~keep&y).sum())
  rows.append(dict(broker=b,month=month,kind=kind,policy=f'TRAIN_BOTTOM_{q*100:.0f}pct',total=len(y),control_correct=int(y.sum()),kept=int(keep.sum()),correct=good,wrong_removed=rejectbad,correct_lost=lost,correct_retained_pct=100*good/max(1,y.sum()),accepted_accuracy_pct=100*good/max(1,keep.sum())))
 scored=perf(p,y,train_indices)
 aggregate=perf(p,y)
 del d,r,X,p
 return rows,scored,aggregate

def main():
 result=[];meta={};importances=[]
 for b in BRS:
  xs=[];ys=[];idxs=[];month_sizes=[];tick=time.time()
  for m in MONTHS:
   d,r=get(b,m);x,names=features(d,r);y=r['correct'].astype(np.int8)
   # deterministic sparse samples, known month data may overlap in time; overfit ON PURPOSE
   i=np.arange(0,len(y),7)
   xs.append(x[i]);ys.append(y[i]);month_sizes.append((m,len(y),len(i)))
   del d,r,x,y
  X=np.vstack(xs);Y=np.concatenate(ys)
  print('FIT',b,'sample',X.shape,'source_rows',month_sizes,'elapsed',round(time.time()-tick,1),flush=True)
  model=lgb.LGBMClassifier(**PLAN['algorithm']);model.fit(X,Y)
  dump(model,OUT/f'EXPOSED_OVERFIT03_{b}_MODEL.joblib',compress=3)
  train_p=model.predict_proba(X)[:,1].astype(np.float32)
  training=perf(train_p,Y)
  cuts={q:float(np.quantile(train_p,q)) for q in Q}
  feature_gain=model.booster_.feature_importance(importance_type='gain');
  feature_split=model.booster_.feature_importance(importance_type='split')
  order=np.argsort(feature_gain)[::-1]
  for rank,i in enumerate(order):
   importances.append(dict(broker=b,rank=int(rank+1),feature=names[i],gain=float(feature_gain[i]),split=int(feature_split[i])))
  broker_stat=dict(fitted_rows=len(Y),training=training,fit_time_sec=round(time.time()-tick,1),train_prob_quantiles={str(q):v for q,v in cuts.items()},feature_top20=[names[i] for i in order[:20]])
  for month,kind in [('06','EXPOSED_IN_SAMPLE_PERIOD'),('07','EXPOSED_IN_SAMPLE_PERIOD'),('02','BACKWARDS_TIME_TEST_NOT_BLIND')]:
   rows,_,agg=scorings(b,model,month,kind,cuts)
   result.extend(rows);broker_stat[month]=agg
   print('MONTH',b,month,'prediction_metrics',agg,'elapsed',round(time.time()-tick,1),flush=True)
  meta[b]=broker_stat
  (OUT/f'{b}_OVERFIT_TRAINING_AND_TEST.json').write_text(json.dumps(broker_stat,indent=2)+'\n')
 (OUT/'OVERFIT_FILTER_ALL_POLICIES.csv').write_text(pd.DataFrame(result).to_csv(index=False))
 pd.DataFrame(importances).to_csv(OUT/'FEATURE_IMPORTANCE_GAINS.csv',index=False)
 (OUT/'RESEARCH_METRICS.json').write_text(json.dumps(meta,indent=2)+'\n')
 print('DONE',json.dumps({b:meta[b]['training'] for b in meta}),flush=True)
if __name__=='__main__':main()

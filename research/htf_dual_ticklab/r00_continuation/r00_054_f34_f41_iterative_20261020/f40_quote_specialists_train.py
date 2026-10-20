#!/usr/bin/env python3
"""F40 source-native ordered quote meta-filter with separate causal quote and macro scoring plus error-class heads.
Uses only archived R00-054 Jan/Feb/Jun/Jul events and F39 new 30-column raw quote inputs.
Fit chronological January; select February; June/July exposed transfer; MQL5 port required.
"""
import sys,io,time,json,zipfile
from pathlib import Path
import numpy as np
from lightgbm import LGBMClassifier
from joblib import dump
ROOT=Path('/mnt/data');HERE=ROOT/'R00_054_F40_SOURCE_NATIVE_COOP_FILTER_20261020';HERE.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'R00_054_F30_ITERATIVE_CAUSAL_FILTER_20261020'))
import F27_PARENT_READONLY_SOURCE as src
F39=ROOT/'R00_054_F39_NATIVE_QUOTE_SEQUENCE_20261020'

def load(b,m):
 c=src.load_one(b,m)
 p=F39/f'F39_SOURCE_NATIVE_QUOTE_{b}_{m}.npz'
 with np.load(p) as z:
  if not np.array_equal(c['t'],z['t']) or not np.array_equal(c['side'],z['side']) or not np.array_equal(c['y'],z['truth']):raise ValueError('RAW_QUOTE_R00_054_EVENT_IDENTITY_FAIL')
  feats=z['features'].copy()
 c['X']=np.column_stack([c['X'],feats]).astype('float32')
 return c

def fast(c,mask):
 good=c['y']==0;bad=~good
 return dict(correct_kept=int(np.sum(mask&good)),correct_total=int(np.sum(good)),incorrect_rejected=int(np.sum((~mask)&bad)),incorrect_total=int(np.sum(bad)),correct_retention=float(np.mean(mask[good])),incorrect_rejection=float(np.mean((~mask)[bad])))

def all_scores(models,c):
 X=c['X'];ret={}
 for n,(m,cols) in models.items():ret[n]=m.predict_proba(X[:,cols])[:,1]
 ret['Q_coop_mean']=(ret['Q_native_quote_good']*.50+ret['QM_quote_macro_good']*.50)
 ret['Q_coop_min']=np.minimum(ret['Q_native_quote_good'],ret['QM_quote_macro_good'])
 ret['Q_opposite_neutral_veto']=1-np.maximum(ret['Q_opposite_hazard'],ret['Q_neutral_hazard'])
 ret['Q_adaptive_neutral']=.55*ret['QM_quote_macro_good']+.45*(1-ret['Q_neutral_hazard'])
 return ret

def main():
 spec={'stage':'frozen before JuneJuly scoring','experiment':'F40','source':'F39 new 30 causal ordered quote features from eight actual SHA pinned user-approved raw bid/ask feeds, plus original 76 known-at cached features; NOTE not original FILTER05 columns','train':'JAN first80% 40s purge every4 event, two brokers independent source then pooled supervised fit','freeze':'February last35%, 0..0.55 0.025 quantile, >=71% of correct per broker, zero new source quota misses on full Feb; highest bad rejection','transfer':'June and July immutable original broker/month events (previously historically exposed) tested after Feb freeze; no JunJul policy tuning','families':['Q_native_quote_good','QM_quote_macro_good','Q_opposite_hazard','Q_neutral_hazard','Q_coop_mean','Q_coop_min','Q_opposite_neutral_veto','Q_adaptive_neutral'],'gate':{'correct_retention':.71,'bad_rejected':.90,'new_R9_quota_failures':0},'python_to_mql5':'F39 30 native quote columns direct quote ring/array port; frozen LightGBM inference via validated MQL5 ONNX or tree serializer; not compiled'}
 (HERE/'F40_FROZEN_PRETRAIN_PLAN.json').write_text(json.dumps(spec,indent=2)+'\n')
 refs=src.r9_reference()
 jan={b:load(b,'01') for b in src.BROKERS}
 xx=[];yy=[]
 for b,c in jan.items():
  end=int(len(c['y'])*.8);ids=np.flatnonzero(c['t']<c['t'][end]-40000)[::4]
  xx.append(c['X'][ids]);yy.append(c['y'][ids])
 X=np.concatenate(xx);Y=np.concatenate(yy)
 print('F40 TRAIN',X.shape,len(Y),flush=True)
 colsquote=np.arange(76,106); colsmacro=np.arange(106)
 cols_err=np.r_[0:21,21:37,43:47,47:48,63:76,76:106]
 columns={
   'Q_native_quote_good':colsquote,
   'QM_quote_macro_good':colsmacro,
   'Q_opposite_hazard':cols_err,
   'Q_neutral_hazard':cols_err}
 target={
   'Q_native_quote_good':(Y==0),
   'QM_quote_macro_good':(Y==0),
   'Q_opposite_hazard':(Y==1),
   'Q_neutral_hazard':(Y==2)}
 models={}
 for n,cols in columns.items():
  param=dict(n_estimators=240,num_leaves=63,min_child_samples=140,reg_lambda=8.5,reg_alpha=.3,learning_rate=.048,n_jobs=3,verbosity=-1,random_state=54040,colsample_bytree=.85,subsample=.9,subsample_freq=1)
  model=LGBMClassifier(**param);model.fit(X[:,cols],target[n])
  models[n]=(model,cols)
  dump(dict(model=model,feature_ids=cols),HERE/f'F40_MODEL_{n}.joblib',compress=3)
  print('TRAINED',n,'feat',len(cols),flush=True)
 del X,Y,xx,yy,jan
 feb={b:load(b,'02') for b in src.BROKERS};fs={b:all_scores(models,c) for b,c in feb.items()}
 names=next(iter(fs.values())).keys();rules={};grid=[]
 for n in names:
  idx={b:np.arange(len(c['t']))>=int(len(c['t'])*.65) for b,c in feb.items()}
  pooled=np.concatenate([fs[b][n][idx[b]] for b in src.BROKERS]);choices=[]
  for q in np.arange(0,.551,.025):
   cut=float(np.quantile(pooled,q));rows=[];pass_=True
   for b,c in feb.items():
    mm=fs[b][n]>=cut
    dg=fast(c,mm)
    pg=c['y'][idx[b]]==0;pm=mm[idx[b]]
    ret=float(pm[pg].mean());rej=float((~pm[~pg]).mean())
    quotas=src.quota_stats(c,mm,refs)
    fail={k:len(quotas[k]) for k in ('newly_failed_hours','newly_failed_days','newly_failed_weeks','newly_failed_months')}
    rows.append(dict(broker=b,correct_retention_last35=ret,bad_rejected_last35=rej,full_feb_metrics=dg,quota_failures=fail))
    pass_=bool(pass_) and bool(ret>=.71 and not any(fail.values()))
   rec=dict(method=n,quantile=round(float(q),3),threshold=cut,eligible=bool(pass_),rows=rows)
   grid.append(rec)
   if pass_:choices.append(rec)
  rules[n]=max(choices,key=lambda z:min(r['bad_rejected_last35'] for r in z['rows'])) if choices else None
 (HERE/'F40_FEBRUARY_FULL_FROZEN_GRID.json').write_text(json.dumps(grid,indent=2)+'\n')
 (HERE/'F40_FEBRUARY_FROZEN_POLICY.json').write_text(json.dumps(rules,indent=2)+'\n')
 del feb,fs
 res=[]
 for mo in ('06','07'):
  for b in src.BROKERS:
   c=load(b,mo);s=all_scores(models,c)
   for n,rule in rules.items():
    if rule is None:continue
    mm=s[n]>=rule['threshold'];metrics=fast(c,mm);qs=src.quota_stats(c,mm,refs)
    fails={k:len(qs[k]) for k in ('newly_failed_hours','newly_failed_days','newly_failed_weeks','newly_failed_months')}
    row=dict(broker=b,month=mo,family=n,cutoff=rule['threshold'],**metrics,quota_failures=fails,pass_user_gate=bool(metrics['correct_retention']>=.71 and metrics['incorrect_rejection']>=.90 and not any(fails.values())))
    res.append(row)
    print('F40',mo,b,n,round(row['correct_retention'],4),round(row['incorrect_rejection'],4),sum(fails.values()),flush=True)
   # Only source-derived prediction scores for later geometric diagnostics; NEVER reorder source events.
   np.savez_compressed(HERE/f'F40_SCORES_{b}_{mo}.npz',t=c['t'],side=c['side'],truth=c['y'],**{n:v.astype('float32') for n,v in s.items()})
   del c,s
 (HERE/'F40_FULL_JUN_JUL_SCORES_AND_QUOTAS.json').write_text(json.dumps(res,indent=2)+'\n')
 aggregate=[]
 for n in rules:
  z=[x for x in res if x['family']==n]
  if len(z)!=4:continue
  cg=sum(x['correct_kept'] for x in z);ct=sum(x['correct_total'] for x in z);br=sum(x['incorrect_rejected'] for x in z);bt=sum(x['incorrect_total'] for x in z)
  aggregate.append(dict(family=n,correct_kept=cg,correct_total=ct,incorrect_removed=br,incorrect_total=bt,correct_retention=cg/ct,incorrect_rejection=br/bt,quota_failures=sum(sum(v for v in x['quota_failures'].values()) for x in z),meets_owner_gate=bool(all(x['pass_user_gate'] for x in z))))
 (HERE/'F40_AGGREGATE.json').write_text(json.dumps(aggregate,indent=2)+'\n')
 print('F40 COMPLETE',json.dumps(aggregate,indent=2),flush=True)
if __name__=='__main__':main()
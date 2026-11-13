"""Frozen R9 155-feature baseline vs quote-only pressure proxies.

Jan-Apr -> May, expanding to Jan-Aug -> September; retrospective/exposed-month
research. Identical old source entry ordinals, old 5s first-passage labels,
old 155 feature order and LightGBM config. No changed trigger, barrier or exit.
"""
from __future__ import annotations
import argparse,hashlib,io,json,os,sys,time,zipfile
from pathlib import Path
sys.path.insert(0,str(Path('/mnt/data/r9_m60_proxy_20261113/deps')))
import numpy as np,joblib
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score,average_precision_score
from signal_features import action_barrier_features
import train as former_hazard
from proxy_features import FEATURE_NAMES as PROXY_NAMES

ROOT=Path('/mnt/data/r9_m60_proxy_20261113')
DEPS=ROOT/'deps';MODELS=ROOT/'models';OUT=ROOT/'results'
ARCHIVE=Path('/mnt/data/R9_M60_JanSep_FullTraining_155Features_20261113.zip')
FROZEN={'05':{'auc':.719798 if False else 0},'06':{},'07':{},'08':{},'09':{}}
FAMILIES={
 'marked_hawkes':list(range(0,12)),
 'latent_pressure':list(range(12,19)),
 'spread_resilience':list(range(19,27)),
 'all_quote_proxies':list(range(27)),
}
PARAMS=dict(objective='binary',n_estimators=95,learning_rate=.05,num_leaves=19,
     min_child_samples=160,reg_alpha=2.,reg_lambda=22.,colsample_bytree=.85,
     subsample=.85,subsample_freq=1,random_state=20261113,n_jobs=2,
     verbosity=-1,max_bin=31,force_row_wise=True)

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(2*1024*1024),b''):h.update(b)
 return h.hexdigest()

def read_month(mm):
 with np.load(DEPS/f'full_month_2026_{mm}.npz',allow_pickle=False) as old, \
      np.load(DEPS/f'event_2026_{mm}.npz',allow_pickle=False) as ev, \
      np.load(DEPS/f'priority_2026_{mm}.npz',allow_pickle=False) as pri, \
      np.load(ROOT/'derived'/f'proxy_2026_{mm}.npz',allow_pickle=False) as new:
  assert np.array_equal(old['entry_times'],ev['entry']) and np.array_equal(ev['entry'],pri['entry'])
  assert np.array_equal(pri['entry'],new['entry'])
  assert np.array_equal(old['entry_ordinals'],ev['ordinal']) and np.array_equal(ev['ordinal'],new['ordinal'])
  assert np.array_equal(old['side'],ev['r9_side'])
  raw=np.hstack([old['features'],ev['features']]).astype(np.float32)
  cols=list(range(14))+former_hazard.OLD_HFT_IDX.tolist()+list(range(145,145+len(ev['feature_names'])))
  selected=raw[:,cols]
  side=np.tile(np.array([1.,-1.],np.float32),len(ev['entry']))
  r9side=np.repeat(ev['r9_side'].astype('f4'),2)
  trend_actions=np.repeat(ev['features'],2,axis=0)
  metadata=np.stack([side,(side==r9side).astype('f4'),np.repeat(ev['stop'].astype('f4'),2),
      np.repeat(ev['target'].astype('f4'),2),np.repeat(ev['spread'].astype('f4'),2)],axis=1)
  analytic=action_barrier_features(trend_actions,metadata[:,4],metadata[:,2],metadata[:,3],side)
  base=np.concatenate([np.repeat(selected,2,axis=0),np.repeat(pri['features'],2,axis=0),analytic,metadata],axis=1).astype(np.float32)
  assert base.shape[1]==155,(mm,base.shape)
  proxy=np.repeat(new['features'],2,axis=0).astype(np.float32)
  assert proxy.shape[1]==27
  kind=ev['cause'].reshape(-1).astype(np.int8)
  hit=ev['hit_ms'].reshape(-1).astype(np.int32)
  y=((kind==1)&(hit>=0)&(hit<=5000)).astype(np.int8)
  good=kind!=-1
  return dict(month=mm,base=base,proxy=proxy,y=y,good=good,
        n_entries=len(ev['entry']),r9_side=ev['r9_side'].astype(np.int8),
        entry_ms=ev['entry'].astype(np.int64))

def scoring(r,p):
 y=r['y'];good=r['good'];n=r['n_entries']
 r9ix=2*np.arange(n)+(r['r9_side']<0).astype(np.int64)
 original_valid=good[r9ix]
 if np.unique(y[good]).size!=2 or np.unique(y[r9ix][original_valid]).size!=2:raise RuntimeError('single class')
 # Selected side is only a counterfactual score; no actual trades and no future occupancy replay.
 buy=p[::2];sell=p[1::2];chosen=np.where(buy>=sell,0,1)
 ix=2*np.arange(n)+chosen
 return {
  'pooled_auc5':float(roc_auc_score(y[good],p[good])),
  'original_direction_auc5':float(roc_auc_score(y[r9ix][original_valid],p[r9ix][original_valid])),
  'pooled_average_precision5':float(average_precision_score(y[good],p[good])),
  'original_direction_average_precision5':float(average_precision_score(y[r9ix][original_valid],p[r9ix][original_valid])),
  'original_direction_positive_rate5':float(y[r9ix][original_valid].mean()),
  'chosen_side_positive_rate5':float(y[ix][good[ix]].mean()),
  'eligible_action_count':int(good.sum()),
  'all_action_count':int(len(p)),
  'original_decisions':int(n),
  'tested_decision_coverage':1.,
  'warning':'Ranking only; no execution-aware policy or future occupancy simulated',
 }

def benchmark_one_fold(idx):
 month=f'{idx+1:02d}';start=time.monotonic()
 rows=[read_month(f'{i:02d}') for i in range(1,idx+2)]
 tr=rows[:-1];te=rows[-1]
 if max(r['entry_ms'][-1] for r in tr)+60000>=te['entry_ms'][0]:raise RuntimeError('boundary leak')
 y_train=np.concatenate([r['y'][r['good']] for r in tr])
 base_train=np.concatenate([r['base'][r['good']] for r in tr])
 proxy_train=np.concatenate([r['proxy'][r['good']] for r in tr])
 if not np.isfinite(proxy_train).all():raise RuntimeError('nonfinite training proxy')
 result={'month':month,'train_months':[r['month'] for r in tr],
         'train_original_decisions':int(sum(r['n_entries'] for r in tr)),
         'test_original_decisions':int(te['n_entries']),
         'features_base':155,'proxy_features':27,
         'status':'EXPOSED_MONTH_RETROSPECTIVE_RESEARCH_NOT_FORWARD_CERTIFIED',
         'source':'frozen original nine months, same pre-decision entry ordinals and first-passage outcomes','families':{}}
 with zipfile.ZipFile(ARCHIVE) as z:
  file_name=f'models/direct_test_{month}_shadow.joblib'
  frozen=joblib.load(io.BytesIO(z.read(file_name)))
  if frozen['config']!=PARAMS:raise RuntimeError('trained configuration drift')
  frozen_pred=frozen['model'].predict_proba(te['base'])[:,1]
  frozen_metrics=scoring(te,frozen_pred)
  result['families']['frozen_155_baseline']=frozen_metrics
  result['frozen_model_file_sha256']=hashlib.sha256(z.read(file_name)).hexdigest()
  print('FOLD',month,'FROZEN',round(frozen_metrics['pooled_auc5'],5),round(frozen_metrics['original_direction_auc5'],5),flush=True)
 for name,sel in FAMILIES.items():
  tic=time.monotonic()
  X=np.concatenate([base_train,proxy_train[:,sel]],axis=1)
  Xt=np.concatenate([te['base'],te['proxy'][:,sel]],axis=1)
  model=LGBMClassifier(**PARAMS)
  model.fit(X,y_train)
  p=model.predict_proba(Xt)[:,1]
  met=scoring(te,p)
  met['delta_pooled_auc5_vs_frozen']=met['pooled_auc5']-frozen_metrics['pooled_auc5']
  met['delta_original_direction_auc5_vs_frozen']=met['original_direction_auc5']-frozen_metrics['original_direction_auc5']
  met['feature_count']=X.shape[1]
  outfile=MODELS/f'{name}_test_{month}_shadow.joblib'
  joblib.dump({'model':model,'config':PARAMS,'family':name,'evaluated_month':month,
        'status':'RETROSPECTIVE_SHADOW_NOT_DEPLOYABLE'},outfile,compress=3)
  met['model_sha256']=sha(outfile)
  met['seconds']=round(time.monotonic()-tic,2)
  result['families'][name]=met
  print('FOLD',month,name,'AUC',round(met['pooled_auc5'],5),'R9',round(met['original_direction_auc5'],5),'delta',round(met['delta_pooled_auc5_vs_frozen'],5),'sec',met['seconds'],flush=True)
 path=OUT/f'fold_{month}.json';path.write_text(json.dumps(result,indent=2)+'\n')
 print('FOLD_COMPLETE',month,'elapsed',round(time.monotonic()-start,1),flush=True)
 return result

def consolidate():
 xs=[json.loads((OUT/f'fold_{i:02}.json').read_text()) for i in range(5,10)]
 families=list(xs[0]['families'])
 result={'status':'RESEARCH_ONLY_NO_AUTOMATIC_PROMOTION', 'data':'XAUUSD Coinexx source ticks Jan-Sep 2026',
         'prior_exposure_warning':'May-Sep were previously examined repeatedly and are not pristine holdout data',
         'universe':{'original_decisions_nine_months':303934,
           'test_decisions_may_sep':int(sum(x['test_original_decisions'] for x in xs))},
         'target':'favorable-first within five seconds of frozen R9 decision, unchanged spread-aware barrier',
         'comparison':'same saved 155-feature direct classifier; identical feature order, labels, learning algorithm/config; added proxy features only',
         'folds':xs,'aggregates':{}}
 for name in families:
  data=[x['families'][name] for x in xs]
  result['aggregates'][name]={
   'pooled_auc_mean':float(np.mean([x['pooled_auc5'] for x in data])),
   'original_direction_auc_mean':float(np.mean([x['original_direction_auc5'] for x in data])),
   'pooled_precision_mean':float(np.mean([x['pooled_average_precision5'] for x in data])),
   'original_direction_precision_mean':float(np.mean([x['original_direction_average_precision5'] for x in data])),
   'above_075_pooled_months':[xs[i]['month'] for i,x in enumerate(data) if x['pooled_auc5']>=.75],
   'above_075_original_direction_months':[xs[i]['month'] for i,x in enumerate(data) if x['original_direction_auc5']>=.75]}
 if 'all_quote_proxies' in result['aggregates']:
  base=result['aggregates']['frozen_155_baseline'];new=result['aggregates']['all_quote_proxies'];
  result['change_all_vs_base']={'pooled_auc':new['pooled_auc_mean']-base['pooled_auc_mean'],
    'original_direction_auc':new['original_direction_auc_mean']-base['original_direction_auc_mean']}
 (OUT/'SUMMARY.json').write_text(json.dumps(result,indent=2)+'\n')
 print('SUMMARY',json.dumps(result['aggregates'],indent=2),flush=True)
 return result

def fit_all():
 rows=[read_month(f'{i:02d}') for i in range(1,10)]
 n=sum(r['n_entries'] for r in rows);assert n==303934
 x=np.concatenate([np.concatenate([r['base'][r['good']],r['proxy'][r['good']]],axis=1) for r in rows]);
 y=np.concatenate([r['y'][r['good']] for r in rows])
 assert x.shape[1]==182 and np.isfinite(x[:,155:]).all()
 model=LGBMClassifier(**PARAMS);start=time.monotonic();model.fit(x,y)
 output=MODELS/'all_182_features_JanSep_in_sample_only.joblib';joblib.dump({'model':model,'config':PARAMS,
 'feature_count':182,'train_months':'Jan-Sep 2026','status':'IN_SAMPLE_ONLY_REQUIRES_UNSEEN_OOS_TEST'},output,compress=3)
 receipt={'fit_decisions':n,'fit_actions_good':len(y),'feature_count':x.shape[1],
   'source_months':'2026-01..2026-09','model_sha256':sha(output),'model_file':output.name,
   'elapsed_s':round(time.monotonic()-start,2),'OOS_AUC':'NOT_AVAILABLE_AFTER_FITTING_ALL_NINE_MONTHS'}
 (OUT/'all_months_fit_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print('ALL_MONTHS_FINAL_IS_ONLY',json.dumps(receipt),flush=True)
 return receipt

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--fold',type=int,choices=[4,5,6,7,8]);ap.add_argument('--summarize',action='store_true');ap.add_argument('--full',action='store_true');x=ap.parse_args()
 if x.fold is not None:benchmark_one_fold(x.fold)
 elif x.summarize:consolidate()
 elif x.full:fit_all()
 else:raise SystemExit('pass --fold 4..8 or --summarize or --full')

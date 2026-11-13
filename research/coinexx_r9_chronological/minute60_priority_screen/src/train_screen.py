"""Prespecified Coinexx-only screening of three quant features against frozen hazard.

Full original R9 decision denominator and BUY/SELL counterfactuals are retained.
Jan-Apr -> May, ... Jan-Aug -> Sep. Held-out months previously exposed in
research; no prospective certification and no automatic deployment.
"""
from __future__ import annotations
import argparse,hashlib,json,os,sys,time
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score,average_precision_score
import joblib
sys.path.insert(0,'/mnt/data/r9_m60_competing/src')
import train as prior
from signal_features import action_barrier_features,FEATURE_NAMES,ACTION_NAMES

ROOT=Path('/mnt/data/r9_m60_priority_screen')
N_BASE=None
FAMILIES={
 'frozen_baseline':(),
 'cusum_only':('cusum',),
 'signed_intensity_only':('intensity',),
 'brownian_geometry_only':('brownian',),
 'all_three':('cusum','intensity','brownian')
}

def file_sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for x in iter(lambda:f.read(2**20),b''):h.update(x)
 return h.hexdigest()

def load_month(mm):
 r=prior.monthly(mm)
 old=prior.select_features(r['X'],'event_trend_flow').astype(np.float32)
 prior_length=old.shape[1]-5
 new=np.load(ROOT/'derived'/f'priority_2026_{mm}.npz',allow_pickle=False)
 src=np.load(Path('/mnt/data/r9_m60_competing/derived')/f'event_2026_{mm}.npz',allow_pickle=False)
 if not np.array_equal(new['ordinal'],src['ordinal']) or not np.array_equal(new['entry'],src['entry']):
  raise RuntimeError('priority input ordinal mismatch')
 # No positive/negative class-dependent construction; any original candidate is eligible.
 states=np.repeat(new['features'],2,axis=0)
 side=np.tile(np.array([1.,-1.],dtype=np.float32),len(src['entry']))
 event=np.repeat(src['features'],2,axis=0)
 analytic=action_barrier_features(event,np.repeat(src['spread'],2),np.repeat(src['stop'],2),np.repeat(src['target'],2),side)
 if not np.isfinite(analytic).all():raise RuntimeError('analytical feature not finite')
 X=np.concatenate([old[:,:-5],states,analytic,old[:,-5:]],axis=1).astype(np.float32)
 r['X']=X
 r['orig_width']=prior_length
 return r

def features(X,version,base_width):
 n=base_width
 cols=list(range(n))
 if 'cusum' in FAMILIES[version]:cols.extend(range(n,n+4))
 if 'intensity' in FAMILIES[version]:cols.extend(range(n+4,n+len(FEATURE_NAMES)))
 if 'brownian' in FAMILIES[version]:cols.extend(range(n+len(FEATURE_NAMES),n+len(FEATURE_NAMES)+len(ACTION_NAMES)))
 cols.extend(range(X.shape[1]-5,X.shape[1]))
 return X[:,cols]

def auc_for_month(m,r,X):
 pred=prior.cumulative_incidence(m,X)
 out={}
 n=r['n_orig'];mask=r['cause']!=-1
 ix_r9=(2*np.arange(n)) + np.where(r['r9_side'][::2]==1,0,1)
 for horizon in (5000,15000):
  p=pred[horizon];y=(r['cause']==1)&(r['hit']>=0)&(r['hit']<=horizon)
  good_r9=mask[ix_r9]
  prob=p['p_fav']; adv=p['p_adv'];alive=p['p_alive']
  util=prob*(r['target']-prior.FEE)-adv*(r['stop']+prior.FEE)-alive*prior.FEE
  bestix=2*np.arange(n)+np.where(util[0::2]>=util[1::2],0,1)
  utility_best=util[bestix]; valid=(mask[bestix])
  selected=bestix[(utility_best>0)&valid]
  out[str(horizon)]={
   'all_actions_auc':float(roc_auc_score(y[mask],prob[mask])),
   'r9_action_auc':float(roc_auc_score(y[ix_r9][good_r9],prob[ix_r9][good_r9])),
   'average_precision':float(average_precision_score(y[mask],prob[mask])),
   'n_original_decisions':int(n),
   'n_counterfactual_actions':int(len(y)),
   'positive_rate':float(np.mean(y[mask])),
   'strict_utility_positive_count':int(len(selected)),
   'strict_utility_positive_coverage':float(len(selected)/n),
   'mean_max_utility_cents':float(np.mean(utility_best[valid])),
   'note':'research probabilities; quote execution side but no realistic fills, occupancy, broker commission; 5sec EV not computed'
  }
 return out

def run_fold(ix):
 start=time.monotonic()
 rows=[load_month(f'{m:02}') for m in range(1,ix+2)]
 rtest=rows[-1];train=rows[:-1];w=rtest['orig_width']
 if max(z['time'].max() for z in train)+60000>=rtest['time'].min():
  raise ValueError('60sec chronological purge failed')
 result={'train_months':[z['month'] for z in train], 'test_month':rtest['month'],
  'status':'RETROSPECTIVE_DEVELOPMENT_ONLY_ALL_PREVIOUSLY_EXPOSED',
  'n_train_entry_opportunities':int(sum(x['n_orig'] for x in train)),
  'n_eval_entry_opportunities':int(rtest['n_orig']),
  'source':'frozen nine original Coinexx 2026 monthly quote files',
  'models':{}}
 for family in FAMILIES:
  t0=time.monotonic()
  X=np.concatenate([features(row['X'],family,w) for row in train])
  cause=np.concatenate([row['cause'] for row in train]);hit=np.concatenate([row['hit'] for row in train])
  xt,yt=prior.expanded_at_risk(X,cause,hit,max_per_bin=40000)
  model=prior.model();model.fit(xt,yt)
  del xt,yt,X,cause,hit
  pred=auc_for_month(model,rtest,features(rtest['X'],family,w))
  result['models'][family]=pred
  # Only *research artifacts* are serialized; no EA feature or training weights are promoted.
  folder=ROOT/'models';folder.mkdir(exist_ok=True)
  path=folder/f'{family}_test_{rtest["month"]}_FAILED_UNTIL_CERTIFIED.joblib'
  joblib.dump({'model':model,'family':family,'test_month':rtest['month'],'status':'NO_LIVE_DEPLOYMENT'},path,compress=3)
  result['models'][family]['model_sha256']=file_sha(path)
  print('FOLD',rtest['month'],family,'AUC5',round(pred['5000']['all_actions_auc'],5),
    'AUC_R9',round(pred['5000']['r9_action_auc'],5),'AUC15',round(pred['15000']['all_actions_auc'],5),
    'Utility+',pred['5000']['strict_utility_positive_count'],'time',round(time.monotonic()-t0,1),flush=True)
 dest=ROOT/'results'/f'fold_{rtest["month"]}.json'
 dest.write_text(json.dumps(result,indent=2)+'\n')
 print('FOLD DONE',rtest['month'],'total_elapsed',round(time.monotonic()-start,1),flush=True)
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--fold',type=int,required=True)
 a=p.parse_args()
 if a.fold not in range(4,9):raise ValueError('Allowed fold indices: 4 May through 8 Sep')
 run_fold(a.fold)

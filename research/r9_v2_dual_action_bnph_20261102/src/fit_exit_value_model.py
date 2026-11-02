"""Fit one side-specific realized R9 exit-value component on all 250 ms candidates."""
from __future__ import annotations
import argparse,hashlib,json,time
from pathlib import Path
import lightgbm as lgb
import numpy as np
from repaired_features import FEATURE_VERSION,REPAIRED_FEATURE_COUNT

def sha256(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()

def main(a):
 start=time.monotonic();Xs=[];ys=[]
 for di,day in enumerate(a.fit_days):
  base=f'coinexx_01_{day}';X=np.load(Path(a.root)/f'{base}_250ms_v5_X.npy',mmap_mode='r');d=np.load(Path(a.root)/f'{base}_250ms_universe.npz')
  j=0 if a.side=='buy' else 1;y=d['net'][:,j].astype(np.float32);mask=np.isfinite(y)
  if di==len(a.fit_days)-1:mask &= d['ts']<d['ts'][-1]-a.embargo_ms
  Xs.append(np.asarray(X[mask],np.float32));ys.append(y[mask])
 XX=np.concatenate(Xs);yy=np.concatenate(ys)
 common=dict(learning_rate=.04,seed=603+(0 if a.side=='buy' else 10)+(0 if a.target=='mean' else 1),feature_fraction=.85,num_threads=2,verbosity=-1,force_col_wise=True,num_leaves=31,min_data_in_leaf=1000,lambda_l2=40.,max_depth=6)
 params=dict(objective='huber',metric='l1',alpha=.9,**common) if a.target=='mean' else dict(objective='quantile',metric='quantile',alpha=.20,**common)
 mdl=lgb.train(params,lgb.Dataset(XX,label=yy,free_raw_data=True),num_boost_round=a.rounds)
 out=Path(a.out);out.mkdir(parents=True,exist_ok=True);p=out/f'coinexx_01_exit_value_v2_{a.side}_{a.target}.txt';mdl.save_model(str(p))
 r=dict(side=a.side,target=a.target,feature_version=FEATURE_VERSION,feature_count=REPAIRED_FEATURE_COUNT,fit_days=a.fit_days,fit_rows=len(yy),target_mean=float(np.mean(yy)),target_positive_rate=float(np.mean(yy>0)),rounds=a.rounds,model_sha256=sha256(p),status='EXIT_VALUE_COMPONENT_NOT_POLICY',elapsed_sec=round(time.monotonic()-start,2))
 (out/f'coinexx_01_exit_value_v2_{a.side}_{a.target}_fit.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--fit-days',nargs='+',required=True);p.add_argument('--side',choices=('buy','sell'),required=True);p.add_argument('--target',choices=('mean','q20'),required=True);p.add_argument('--out',required=True);p.add_argument('--rounds',type=int,default=64);p.add_argument('--embargo-ms',type=int,default=60000);main(p.parse_args())

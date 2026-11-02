"""Fit direct WAIT-improvement with frozen timing + fitted excitation features."""
from __future__ import annotations
import argparse,hashlib,json,time
from pathlib import Path
import lightgbm as lgb
import numpy as np
from timing_transition_features import wait_improves_target
def sha256(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()
def main(a):
 Xs=[];ys=[];start=time.monotonic()
 for di,day in enumerate(a.fit_days):
  X=np.load(Path(a.features)/f'coinexx_01_{day}_wait_transition_hawkes_X.npy',mmap_mode='r');d=np.load(Path(a.teacher)/f'coinexx_01_{day}_250ms_universe.npz');y,_=wait_improves_target(d,a.max_wait_ms);m=np.ones(len(y),bool)
  if di==len(a.fit_days)-1:m &= d['ts']<d['ts'][-1]-a.embargo_ms
  Xs.append(np.asarray(X[m],np.float32));ys.append(y[m])
 XX=np.concatenate(Xs);yy=np.concatenate(ys);pos=int(yy.sum());spw=(len(yy)-pos)/max(1,pos);params=dict(objective='binary',metric='binary_logloss',learning_rate=.04,seed=602,feature_fraction=.85,num_threads=2,verbosity=-1,force_col_wise=True,num_leaves=31,min_data_in_leaf=1000,lambda_l2=40.,max_depth=6,scale_pos_weight=spw)
 mdl=lgb.train(params,lgb.Dataset(XX,label=yy,free_raw_data=True),num_boost_round=64);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);p=out/'coinexx_01_wait_transition_hawkes_v1.txt';mdl.save_model(str(p));r=dict(identity='R9_V2_WAIT_TRANSITION_PLUS_FITTED_EXCITATION_V1',features=XX.shape[1],fit_rows=len(yy),positive=pos,positive_rate=float(yy.mean()),model_sha256=sha256(p),status='INCREMENTAL_RESEARCH_NOT_POLICY',elapsed_sec=round(time.monotonic()-start,2));(out/'fit.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--features',required=True);p.add_argument('--teacher',required=True);p.add_argument('--fit-days',nargs='+',required=True);p.add_argument('--out',required=True);p.add_argument('--embargo-ms',type=int,default=60000);p.add_argument('--max-wait-ms',type=int,default=1000);main(p.parse_args())

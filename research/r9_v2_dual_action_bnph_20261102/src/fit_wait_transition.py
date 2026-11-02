"""Fit direct all-candidate WAIT-improvement transition model for R9 v2 repair."""
from __future__ import annotations
import argparse,hashlib,json,time
from pathlib import Path
import lightgbm as lgb
import numpy as np
from timing_transition_features import TIMING_FEATURE_VERSION,TIMING_FEATURE_COUNT,wait_improves_target

def sha256(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()

def main(a):
 start=time.monotonic();Xs=[];ys=[]
 for di,day in enumerate(a.fit_days):
  X=np.load(Path(a.features)/f'coinexx_01_{day}_wait_transition_X.npy',mmap_mode='r')
  d=np.load(Path(a.teacher)/f'coinexx_01_{day}_250ms_universe.npz');y,_=wait_improves_target(d,a.max_wait_ms);mask=np.ones(len(y),bool)
  if di==len(a.fit_days)-1:mask &= d['ts']<d['ts'][-1]-a.embargo_ms
  Xs.append(np.asarray(X[mask],np.float32));ys.append(y[mask])
 XX=np.concatenate(Xs);yy=np.concatenate(ys);pos=int(yy.sum());neg=len(yy)-pos;spw=neg/max(1,pos)
 params=dict(objective='binary',metric='binary_logloss',learning_rate=.04,seed=602,feature_fraction=.85,num_threads=2,verbosity=-1,force_col_wise=True,
             num_leaves=31,min_data_in_leaf=1000,lambda_l2=40.,max_depth=6,scale_pos_weight=spw)
 mdl=lgb.train(params,lgb.Dataset(XX,label=yy,free_raw_data=True),num_boost_round=a.rounds)
 out=Path(a.out);out.mkdir(parents=True,exist_ok=True);p=out/'coinexx_01_wait_transition_v1.txt';mdl.save_model(str(p))
 r=dict(version=TIMING_FEATURE_VERSION,feature_count=TIMING_FEATURE_COUNT,fit_days=a.fit_days,fit_rows=len(yy),positive=pos,positive_rate=float(yy.mean()),scale_pos_weight=spw,
        rounds=a.rounds,model_sha256=sha256(p),embargo_ms=a.embargo_ms,max_wait_ms=a.max_wait_ms,status='TIMING_RESEARCH_NOT_POLICY',elapsed_sec=round(time.monotonic()-start,2))
 (out/'coinexx_01_wait_transition_v1_fit.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--features',required=True);p.add_argument('--teacher',required=True);p.add_argument('--fit-days',nargs='+',required=True);p.add_argument('--out',required=True);p.add_argument('--rounds',type=int,default=64);p.add_argument('--embargo-ms',type=int,default=60000);p.add_argument('--max-wait-ms',type=int,default=1000);main(p.parse_args())

"""Source/month-agnostic direct all-candidate WAIT-improvement fitter."""
from __future__ import annotations
import argparse,hashlib,json,time
from pathlib import Path
import lightgbm as lgb
import numpy as np
from timing_transition_features import wait_improves_target,TIMING_FEATURE_COUNT,TIMING_FEATURE_VERSION
from path_config import artifact_stem

def sha256(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()

def main(a):
 st=time.monotonic();root=Path(a.root);Xs=[];ys=[];source=a.source.lower();month=str(a.month).zfill(2)
 for di,day in enumerate(a.fit_days):
  stem=artifact_stem(source,month,day);X=np.load(root/f'{stem}_wait_transition_X.npy',mmap_mode='r');d=np.load(root/f'{stem}_250ms_universe.npz');y,_=wait_improves_target(d,a.max_wait_ms);m=np.ones(len(y),bool)
  if di==len(a.fit_days)-1:m &= d['ts']<d['ts'][-1]-a.embargo_ms
  Xs.append(np.asarray(X[m],np.float32));ys.append(y[m])
 XX=np.concatenate(Xs);yy=np.concatenate(ys);pos=int(yy.sum());spw=(len(yy)-pos)/max(1,pos);params=dict(objective='binary',metric='binary_logloss',learning_rate=.04,seed=602,feature_fraction=.85,num_threads=2,verbosity=-1,force_col_wise=True,num_leaves=31,min_data_in_leaf=1000,lambda_l2=40.,max_depth=6,scale_pos_weight=spw)
 mdl=lgb.train(params,lgb.Dataset(XX,label=yy,free_raw_data=True),num_boost_round=64);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);base=f'{source}_{month}_wait_transition_domain_v2';p=out/f'{base}.txt';mdl.save_model(str(p));r=dict(identity='R9_V2_DOMAIN_WAIT_TRANSITION_V2',source=source,month=month,feature_version=TIMING_FEATURE_VERSION,features=TIMING_FEATURE_COUNT,fit_days=a.fit_days,fit_rows=len(yy),positive=pos,positive_rate=float(yy.mean()),model_sha256=sha256(p),same_hyperparameters_as_coinexx_direct_wait=True,status='DOMAIN_RESEARCH_NOT_POLICY',elapsed_sec=round(time.monotonic()-st,2));(out/f'{base}_fit.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',choices=('coinexx','dukascopy'),required=True);p.add_argument('--month',required=True);p.add_argument('--root',required=True);p.add_argument('--fit-days',nargs='+',required=True);p.add_argument('--out',required=True);p.add_argument('--embargo-ms',type=int,default=60000);p.add_argument('--max-wait-ms',type=int,default=1000);main(p.parse_args())
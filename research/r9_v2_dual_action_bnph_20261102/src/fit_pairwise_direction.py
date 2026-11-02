"""Fit direct BUY-vs-SELL economic direction ranker on all 250 ms candidates."""
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
 start=time.monotonic();Xs=[];ys=[];ws=[];ties=0
 for di,day in enumerate(a.fit_days):
  base=f'coinexx_01_{day}';X=np.load(Path(a.root)/f'{base}_250ms_v5_X.npy',mmap_mode='r');d=np.load(Path(a.root)/f'{base}_250ms_universe.npz');diff=d['net'][:,0]-d['net'][:,1];mask=np.isfinite(diff)&(~np.isclose(diff,0,atol=1e-7))
  if di==len(a.fit_days)-1:mask &= d['ts']<d['ts'][-1]-a.embargo_ms
  ties+=int((np.isfinite(diff)&np.isclose(diff,0,atol=1e-7)).sum());v=diff[mask];Xs.append(np.asarray(X[mask],np.float32));ys.append((v>0).astype(np.uint8));ws.append(1.+np.minimum(4.,np.abs(v)/.30))
 XX=np.concatenate(Xs);yy=np.concatenate(ys);ww=np.concatenate(ws).astype(np.float32)
 params=dict(objective='binary',metric='binary_logloss',learning_rate=.04,seed=604,feature_fraction=.85,num_threads=2,verbosity=-1,force_col_wise=True,num_leaves=31,min_data_in_leaf=1000,lambda_l2=40.,max_depth=6)
 mdl=lgb.train(params,lgb.Dataset(XX,label=yy,weight=ww,free_raw_data=True),num_boost_round=a.rounds)
 out=Path(a.out);out.mkdir(parents=True,exist_ok=True);p=out/'coinexx_01_pairwise_direction_v2.txt';mdl.save_model(str(p))
 r=dict(identity='R9_V2_PAIRWISE_DIRECTION_V2',feature_version=FEATURE_VERSION,feature_count=REPAIRED_FEATURE_COUNT,fit_days=a.fit_days,fit_rows=len(yy),buy_better_rate=float(yy.mean()),excluded_ties=ties,weight='1+min(4,abs(net_buy-net_sell)/0.30)',rounds=a.rounds,model_sha256=sha256(p),status='DIRECTION_RESEARCH_NOT_POLICY',elapsed_sec=round(time.monotonic()-start,2))
 (out/'coinexx_01_pairwise_direction_v2_fit.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--fit-days',nargs='+',required=True);p.add_argument('--out',required=True);p.add_argument('--rounds',type=int,default=64);p.add_argument('--embargo-ms',type=int,default=60000);main(p.parse_args())

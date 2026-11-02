"""Fit one component of the chronological all-observed-250ms R9 v2 pilot."""
from __future__ import annotations
import argparse,hashlib,json,time
from pathlib import Path
import lightgbm as lgb
import numpy as np
from repaired_features import FEATURE_VERSION,REPAIRED_FEATURE_COUNT
from repaired_training_common import action_labels

def sha256(p:Path):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1<<20),b''):h.update(c)
    return h.hexdigest()

def paths(root,day):
    root=Path(root);base=f'coinexx_01_{day}'
    return root/f'{base}_250ms_v5_X.npy',root/f'{base}_250ms_universe.npz'

def load_day(root,day):
    xp,tp=paths(root,day);X=np.load(xp,mmap_mode='r');d=np.load(tp)
    if X.shape[1]!=REPAIRED_FEATURE_COUNT or len(X)!=len(d['ts']):raise ValueError('shard contract')
    return X,d,xp,tp

def main(a):
    start=time.monotonic();Xs=[];ys=[];used=0;source_files=[]
    fit_days=a.fit_days
    for di,day in enumerate(fit_days):
        X,d,xp,tp=load_day(a.root,day);ts=d['ts'];good=d['good'].astype(np.uint8);neutral=d['neutral'].astype(np.uint8)
        mask=np.ones(len(ts),bool)
        if di==len(fit_days)-1:mask &= ts < ts[-1]-a.embargo_ms
        if a.target=='opportunity':y=good.any(axis=1).astype(np.uint8)
        elif a.target in ('buy','sell'):y=action_labels(good,neutral)[:,0 if a.target=='buy' else 1]
        else:
            next_dt=d['next_dt_ms'];next_any=d['next_any_good'].astype(np.uint8);now_any=good.any(axis=1)
            mask &= (~now_any)&(next_dt>0)&(next_dt<=a.max_wait_ms);y=next_any
        Xs.append(np.asarray(X[mask],np.float32));ys.append(np.asarray(y[mask]));used+=int(mask.sum());source_files += [str(xp),str(tp)]
    XX=np.concatenate(Xs,axis=0);yy=np.concatenate(ys,axis=0);del Xs,ys
    common=dict(learning_rate=.05,seed=601,feature_fraction=.80,num_threads=2,verbosity=-1,force_col_wise=True,
                num_leaves=15,min_data_in_leaf=500,lambda_l2=25.,max_depth=5)
    if a.target in ('opportunity','wait'):
        params=dict(objective='binary',metric='binary_logloss',**common)
    else:params=dict(objective='multiclass',num_class=3,metric='multi_logloss',**common)
    mdl=lgb.train(params,lgb.Dataset(XX,label=yy,free_raw_data=True),num_boost_round=a.rounds)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True);path=out/f'coinexx_01_250ms_v5_pilot_{a.target}.txt';mdl.save_model(str(path))
    receipt=dict(target=a.target,feature_version=FEATURE_VERSION,feature_count=REPAIRED_FEATURE_COUNT,fit_days=fit_days,fit_rows=used,
                 positive_rate=float(np.mean(yy==1)) if a.target in ('opportunity','wait') else None,rounds=a.rounds,model_sha256=sha256(path),
                 embargo_ms=a.embargo_ms,max_wait_ms=(a.max_wait_ms if a.target=='wait' else None),source_files=source_files,
                 status='FROZEN_250MS_PILOT_COMPONENT_NOT_POLICY',elapsed_sec=round(time.monotonic()-start,2))
    (out/f'coinexx_01_250ms_v5_pilot_{a.target}_fit.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--target',choices=('opportunity','buy','sell','wait'),required=True);p.add_argument('--root',required=True)
    p.add_argument('--fit-days',nargs='+',required=True);p.add_argument('--out',required=True);p.add_argument('--rounds',type=int,default=32)
    p.add_argument('--embargo-ms',type=int,default=60000);p.add_argument('--max-wait-ms',type=int,default=1000);main(p.parse_args())

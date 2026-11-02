"""Fit one frozen component of the repaired R9 v2 entry engine."""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import lightgbm as lgb
import numpy as np
from repaired_features import FEATURE_VERSION,REPAIRED_FEATURE_COUNT
from repaired_training_common import masks,action_labels,sha256

def main(a):
    start=time.monotonic();X=np.load(a.features,mmap_mode='r');lab=np.load(a.labels)
    if X.shape[1]!=REPAIRED_FEATURE_COUNT:raise ValueError('feature contract')
    ts=lab['ts'];good=lab['good'].astype(np.uint8);neutral=lab['neutral'].astype(np.uint8);net=lab['net']
    valid=np.isfinite(net).all(axis=1);tr,_,_,_,split=masks(ts);tr&=valid
    common=dict(learning_rate=.05,seed=601,feature_fraction=.80,num_threads=2,verbosity=-1,force_col_wise=True,
                num_leaves=15,min_data_in_leaf=500,lambda_l2=25.,max_depth=5)
    if a.target=='opportunity':
        y=good.any(axis=1).astype(np.uint8);params=dict(objective='binary',metric='binary_logloss',**common)
    else:
        y=action_labels(good,neutral)[:,0 if a.target=='buy' else 1];params=dict(objective='multiclass',num_class=3,metric='multi_logloss',**common)
    mdl=lgb.train(params,lgb.Dataset(X[tr],label=y[tr],free_raw_data=True),num_boost_round=a.rounds)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True);path=out/f'{a.source}_{a.month}_repaired_{a.target}.txt';mdl.save_model(str(path))
    receipt=dict(source=a.source,month=a.month,target=a.target,feature_version=FEATURE_VERSION,feature_count=REPAIRED_FEATURE_COUNT,
                 rounds=a.rounds,fit_events=int(tr.sum()),split=split,model_sha256=sha256(path),elapsed_sec=round(time.monotonic()-start,2),
                 status='FROZEN_COMPONENT_NOT_POLICY')
    (out/f'{a.source}_{a.month}_repaired_{a.target}_fit.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--target',choices=('opportunity','buy','sell'),required=True);p.add_argument('--source',required=True);p.add_argument('--month',required=True)
    p.add_argument('--features',required=True);p.add_argument('--labels',required=True);p.add_argument('--out',required=True);p.add_argument('--rounds',type=int,default=32);main(p.parse_args())

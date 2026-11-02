#!/usr/bin/env python3
"""Predeclared leave-one-family-out OOS diagnostics, never a strategy release.
Every heldout eligible quote-action is evaluated; nothing randomly sampled.
"""
from pathlib import Path
import json,numpy as np
from sklearn.metrics import roc_auc_score
from src_wait_value_model import ywait
from src_three_class_student import K,B,MONS,load_label_chunks
R=Path('/mnt/data/next_action_timing')
GROUPS={
 'all':list(range(K)),
 'minus_spread':[j for j in range(K) if j not in (0,1,2,3)],
 'minus_fast_flow':[j for j in range(K) if j not in (4,5,6,7,8,13,14)],
 'minus_large_geometry':[j for j in range(K) if j not in (9,10,11,12)],
 'minus_session':[j for j in range(K) if j!=15],
 'quote_flow_only':[0,1,2,3,4,5,6,7,8,13,14,16],
 'session_and_spread_only':[0,15,16]
}

def score_variant(x,counts,cols):
    cc=counts.astype(np.float64);nclass=cc[0].sum(axis=1)
    prior=(nclass+1.)/(nclass.sum()+2.)
    z=np.tile(np.log(prior),(len(x),1))
    for j in cols:
        lp=np.log((cc[j]+3.)/(nclass[:,None]+3.*B))
        z+=.32*lp[:,x[:,j]].T
    z-=z.max(axis=1)[:,None]
    p=np.exp(z);p/=p.sum(axis=1)[:,None]
    return p[:,1]

def evaluate(src,mon):
    pos=MONS.index(mon);dir=R/'models'/f'{src}_{mon}'
    with np.load(dir/'DAILY_WAIT_COUNTS.npz') as d:days=d['days'];counts=d['counts']
    a=max(1,int(len(days)*.50));b=max(a+1,int(len(days)*.72))
    h=counts[:a].sum(axis=0)
    for prev in MONS[:pos]:
        with np.load(R/'models'/f'{src}_{prev}'/'DAILY_WAIT_COUNTS.npz') as d:h+=d['counts'].sum(axis=0)
    yt=[];probs={v:[] for v in GROUPS}
    for k,(_,_,_,_,_) in enumerate(load_label_chunks(src,mon,R)):
        with np.load(R/'results'/f'{src}_{mon}_full'/f'{src}_{mon}_action_events_{k:05d}.npz') as d:y=ywait(d['label'])
        with np.load(dir/f'asof_bins_{k:05d}.npz') as d:x=d['bin'];t=d['time']
        mask=t//86400000>=days[b]
        if not mask.any():continue
        xx=x[mask].reshape(-1,K);yy=y[mask].reshape(-1)
        yt.append(yy)
        for name,cols in GROUPS.items():probs[name].append(score_variant(xx,h,cols))
    labels=np.concatenate(yt)
    auc={name:round(float(roc_auc_score(labels,np.concatenate(v))),6) for name,v in probs.items()}
    out={'source':src,'month':mon,'heldout_side_actions':int(len(labels)),'heldout_delay_rescue_prior':float(labels.mean()),
         'auc_by_predeclared_family':auc,'valid_use':'DIAGNOSTIC_ONLY_NO_CHECK_THRESHOLD_TUNING'}
    (dir/'WAIT_FEATURE_ABLATION.json').write_text(json.dumps(out,indent=2))
    return out
if __name__=='__main__':
    res=[]
    for src in ('coinexx','dukascopy'):
        for m in MONS:
            path=R/'models'/f'{src}_{m}'/'WAIT_FEATURE_ABLATION.json'
            d=json.loads(path.read_text()) if path.exists() else evaluate(src,m)
            res.append(d)
            print(src,m,d['auc_by_predeclared_family'],flush=True)
    (R/'results'/'FULL_EIGHT_SOURCE_ABLATION.json').write_text(json.dumps(res,indent=2))

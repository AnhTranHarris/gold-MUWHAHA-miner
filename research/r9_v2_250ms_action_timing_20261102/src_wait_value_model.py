#!/usr/bin/env python3
"""Source-exact counterfactual WAIT/DELAY teacher, causal foresight student.

At the SAME side, loss/neutral NOW may become strict +0.10 favorable-first
within 250ms/1s/3s delayed entry. Teacher target is retrospective only.
Future quote/action information is NOT supplied to the causal Bayesian inputs.
Full event population; historical days train, middle days calibrate, later days
check; report feature ranking and genuine heldout AUC only (OFF POLICY).
"""
from pathlib import Path
from src_three_class_student import NAMES,K,B,load_label_chunks,sha
import argparse,json,numpy as np
from sklearn.metrics import roc_auc_score
MONS=['01','02','06','07']

def ywait(labs):
    """Same-side option to defer; NO selection of future best side."""
    return ((labs[:,0,:]!=1)&np.any(labs[:,1:,:]==1,axis=1)).astype(np.uint8)

def hist_binary(bins,labels):
    hist=np.zeros((K,2,B),np.int64)
    x=bins.reshape(-1,K)
    y=labels.reshape(-1)
    for j in range(K):
        hist[j]=np.bincount(y*B+x[:,j],minlength=2*B).reshape(2,B)
    return hist

def predict_binary(x,count):
    cc=count.astype(np.float64)
    totals=cc[0].sum(axis=1)
    prior=(totals+1)/(totals.sum()+2)
    conditional=np.log((cc+3)/(totals[None,:,None]+3*B))
    z=np.tile(np.log(prior),(len(x),1))
    for j in range(K):z+=.32*conditional[j][:,x[:,j]].T
    z-=np.max(z,axis=1)[:,None];p=np.exp(z);p/=p.sum(axis=1)[:,None]
    return p[:,1]

def create_daily_counts(source,month,root):
    droot=root/'models'/f'{source}_{month}'
    counts={};n=0
    for k,(_,t,_,_,all_y) in enumerate(load_label_chunks(source,month,root)):
        # load all 4-delay labels from original source and NOW causal feature bins.
        pp=root/'results'/f'{source}_{month}_full'/f'{source}_{month}_action_events_{k:05d}.npz'
        with np.load(pp) as d:y=ywait(d['label'])
        with np.load(droot/f'asof_bins_{k:05d}.npz') as d:x=d['bin'];tt=d['time']
        assert np.array_equal(tt,t) and x.shape[:2]==y.shape
        for day in np.unique(tt//86400000):
            mask=tt//86400000==day
            v=hist_binary(x[mask],y[mask])
            if int(day) not in counts:counts[int(day)]=v
            else:counts[int(day)]+=v
        n+=len(t)
    days=np.array(sorted(counts),np.int64)
    data=np.stack([counts[int(day)] for day in days])
    np.savez_compressed(droot/'DAILY_WAIT_COUNTS.npz',days=days,counts=data)
    return {'events':n,'days':len(days),'sha256':sha(droot/'DAILY_WAIT_COUNTS.npz')}

def fit(source,month,root):
    pos=MONS.index(month);droot=root/'models'/f'{source}_{month}'
    with np.load(droot/'DAILY_WAIT_COUNTS.npz') as d:days=d['days'];daily=d['counts']
    a=max(1,int(len(days)*.50));b=max(a+1,int(len(days)*.72))
    past=np.zeros((K,2,B),np.int64)
    for mon in MONS[:pos]:
        with np.load(root/'models'/f'{source}_{mon}'/'DAILY_WAIT_COUNTS.npz') as p:past+=p['counts'].sum(axis=0)
    past+=daily[:a].sum(axis=0)
    training_counts={'wait_rescues':int(past[0,1].sum()),'no_rescue':int(past[0,0].sum())}
    cal=[];check=[]
    for k,(_,_,_,_,_) in enumerate(load_label_chunks(source,month,root)):
        with np.load(root/'results'/f'{source}_{month}_full'/f'{source}_{month}_action_events_{k:05d}.npz') as d:y=ywait(d['label'])
        with np.load(droot/f'asof_bins_{k:05d}.npz') as d:x=d['bin'];t=d['time']
        day=t//86400000
        for mask,store in (( (day>=days[a])&(day<days[b]),cal),(day>=days[b],check)):
            if np.any(mask):
                prob=predict_binary(x[mask].reshape(-1,K),past)
                store.append((prob,y[mask].reshape(-1),np.repeat(t[mask],2)))
    pc,yc,tc=[np.concatenate([x[i] for x in cal]) for i in range(3)]
    pt,yt,tt=[np.concatenate([x[i] for x in check]) for i in range(3)]
    thresholds=[]
    for alpha in [.5,.75,.90,.95,.99]:
        th=float(np.quantile(pc[yc==0],alpha))
        chosen=pc>th;n=int(chosen.sum());hit=int(yc[chosen].sum())
        thresholds.append({'bad_rejection_quantile':alpha,'threshold':th,'calibration_precision':hit/n if n else None,'count':n,'meets80':bool(n and hit/n>=.8)})
    good=[x for x in thresholds if x['meets80']]
    sel=max(good,key=lambda v:v['count']) if good else None
    diagnostic=thresholds[2]
    th=(sel or diagnostic)['threshold'];chosen=pt>th;n=int(chosen.sum())
    precision=float(yt[chosen].mean()) if n else None
    byday={}
    for d in np.unique(tt//86400000):
        mask=chosen & (tt//86400000==d)
        byday[str(int(d))]={'selected':int(mask.sum()),'correct_wait_rescue':int(yt[mask].sum())}
    out={'source':source,'month':month,'target':'wait_side_specific_same_quote_no_now_good_and_delayed_good_teacher_only',
      'train_action_count':sum(training_counts.values()),'train_class_counts':training_counts,
      'calibration_action_count':len(pc),'check_action_count':len(pt),
      'heldout_wait_rescue_base_rate':float(yt.mean()),'heldout_auc':float(roc_auc_score(yt,pt)),
      'calibration_thresholds':thresholds,'valid_threshold':sel is not None,
      'heldout_diagnostic_selected':n,'heldout_diagnostic_precision':precision,
      'heldout_selected_days':byday,'heldout_80pct_daily_passes':int(sum(v['selected']>0 and v['correct_wait_rescue']/v['selected']>=.8 for v in byday.values())),
      'model_release':'SHADOW_ONLY_NEEDS_REAL_ONLINE_WAIT_REEVALUATION' if sel else 'REJECTED',
      'scientific_boundaries':'Selected actions overlap and future delay action availability is oracle known; not actual on-policy trading. AUC measures ranking only.'}
    (droot/'WAIT_VALUE_FOLD_RESULT.json').write_text(json.dumps(out,indent=2));return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--month',required=True)
    p.add_argument('--root',type=Path,default=Path('/mnt/data/next_action_timing'));p.add_argument('--stage',choices=['counts','fit'],required=True);a=p.parse_args()
    z=create_daily_counts(a.source,a.month,a.root) if a.stage=='counts' else fit(a.source,a.month,a.root)
    print(json.dumps({k:v for k,v in z.items() if k not in ('calibration_thresholds','heldout_selected_days')},indent=2))

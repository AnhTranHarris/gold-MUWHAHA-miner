#!/usr/bin/env python3
"""Streaming, full-coverage 3-class Bayesian action teacher/student.

As-of tick features only; separate CORRECT / INCORRECT / NEUTRAL labels.
All three are distinct. Hindsight future labels NEVER appear in input features.
Month chronology: previous source months, current first 50% of active days
for fit, next 22% calibration, remaining days locked check. 30sec purge.
No ex-post volume quota selection, no hidden negative subsampling, zero trades
on a failed calibration. Diagnostic rates refer to off-policy event opportunities,
NOT completed nonoverlapping EA positions. No model is approved by these data.
"""
from __future__ import annotations
import argparse,json,hashlib,time,math,zipfile
from pathlib import Path
import numpy as np
from numba import njit
from src_action_timing import load_ticks, sha
MONS=('01','02','06','07');SRC=('coinexx','dukascopy')
H=np.array([250,1000,5000,15000,45000,300000,900000,3600000,14400000],np.int64)
NAMES=['spread','bid_ask_change','spread_delta_1s','spread_delta_5s','impulse_250ms','impulse_1s','impulse_5s','impulse_15s','impulse_45s','impulse_5m','impulse_15m','impulse_1h','impulse_4h','rate_1s','rate_5s','session_utc','side']
K=len(NAMES);B=16
# neutral bins are not merged into incorrect classes. Fixed bins predeclared.
SP=np.array([.03,.08,.12,.16,.2,.25,.33,.45,.65,.85,1.2,1.6,2.,2.8,4.],np.float64)
DELTA=np.array([-1.,-.6,-.3,-.15,-.08,-.04,-.02,0.,.02,.04,.08,.15,.3,.6,1.],np.float64)
IMP=np.array([-5.,-3.,-2.,-1.3,-.8,-.4,-.15,0.,.15,.4,.8,1.3,2.,3.,5.],np.float64)
RATES=np.array([0.,1.,2.,3.,4.,6.,8.,12.,16.,24.,32.,48.,64.,96.,128.],np.float64)

def category_features(t,b,a,idx):
    """Vectorized as-of-only features for every eligible event; no future quote.
    Causal window uses the first quote after t-horizon but never after t.
    Long horizons explicitly missing=bin0; never invent 4h history.
    """
    m=len(idx);q=t[idx];mid=(b+a)*.5
    out=np.zeros((m,2,K),np.uint8)
    spr=a[idx]-b[idx]
    out[:,:,0]=np.searchsorted(SP,spr)[:,None]
    up1=np.maximum(0,idx-1)
    lastbid=b[idx]-b[up1];lastask=a[idx]-a[up1]
    sidepressure=lastbid-lastask
    out[:,:,1]=np.searchsorted(DELTA,sidepressure)[:,None]
    ix=[]
    for h in H:
        prior=np.searchsorted(t,q-h,side='left')
        prior=np.minimum(prior,idx)
        ix.append(prior)
    n1,n5=ix[1],ix[2]
    out[:,:,2]=np.searchsorted(DELTA,spr-(a[n1]-b[n1]))[:,None]
    out[:,:,3]=np.searchsorted(DELTA,spr-(a[n5]-b[n5]))[:,None]
    # Normalize by strictly earlier 5-minute displacement scale (abs), not future ATR.
    volproxy=np.maximum(.08, np.abs(mid[idx]-mid[ix[5]])+.20)
    for j,p in enumerate(ix):
        signed=((mid[idx]-mid[p])/volproxy).astype(np.float64)
        vbuy=np.searchsorted(IMP,signed)
        vsell=np.searchsorted(IMP,-signed)
        warm=(q-t[0])>=H[j]
        out[:,0,4+j]=np.where(warm,vbuy,0)
        out[:,1,4+j]=np.where(warm,vsell,0)
    rate1=(idx-n1);rate5=(idx-n5)/5.
    out[:,:,13]=np.searchsorted(RATES,rate1)[:,None]
    out[:,:,14]=np.searchsorted(RATES,rate5)[:,None]
    # Static 2-hour UTC buckets, not a hard session ban.
    out[:,:,15]=((q//3600000)%24//2).astype(np.uint8)[:,None]
    out[:,0,16]=1;out[:,1,16]=2
    assert np.all(out<B)
    return out

def prefix_stats(out,lab,day):
    days=np.unique(day)
    # side-oriented categorical class conditional statistics, no downsampling.
    counts=np.zeros((len(days),K,3,B),np.int64)
    for d_i,d in enumerate(days):
        mask=day==d
        x=out[mask].reshape(-1,K)
        y=lab[mask,:,].reshape(-1)
        y=np.where(y==1,2,np.where(y==-1,0,1)).astype(np.int64)
        for j in range(K):
            code=(y*B+x[:,j]).astype(np.int64)
            counts[d_i,j]=np.bincount(code,minlength=3*B).reshape(3,B)
    return days,counts

def score(x,counts):
    # Shrunk categorical naïve Bayes. Correlated scales downweighted to avoid
    # probability-overconfidence; these are rankings, NOT calibrated beliefs.
    counts=counts.astype(np.float64)
    nclass=counts[0].sum(axis=1)
    prior=(nclass+1.)/(nclass.sum()+3.)
    total=np.log(prior)
    cat=np.log((counts+3.)/(nclass[None,:,None]+3.*B))
    # no score fusing future outcomes, label classes and net are absent here.
    z=np.tile(total,(len(x),1))
    for j in range(K):
        z+=.32*cat[j][:,x[:,j]].T
    z-=np.max(z,axis=1)[:,None]
    p=np.exp(z);p/=p.sum(axis=1)[:,None]
    return p

def load_label_chunks(source,month,root):
    directory=root/'results'/f'{source}_{month}_full'
    prog=json.loads((directory/'PROGRESS_FULL.json').read_text())
    assert prog['status']=='COMPLETE' and prog['eligible_decisions']==prog['completed_decisions']
    for part in prog['parts']:
        path=directory/part['file'];assert sha(path)==part['sha256']
        with np.load(path) as d:
            yield (d['decision_tick'].copy(),d['decision_time'].copy(),d['label'][:,0,:].copy(),
                d['net'][:,0,:].copy(),d['label'][:,1:,:].copy())

def build_full_bins(source,month,root):
    t,b,a,raw=load_ticks(source,month)
    output=root/'models'/f'{source}_{month}';output.mkdir(parents=True,exist_ok=True)
    daily_counts={};receipts=[]
    for k,(idx,ts,label,net,delaylab) in enumerate(load_label_chunks(source,month,root)):
        f=output/f'asof_bins_{k:05d}.npz'
        if f.exists():
            # Source-exact continuation of verified committed chunk, no overwrite.
            with np.load(f) as d:
                assert len(d['time'])==len(ts) and np.array_equal(d['time'],ts)
                assert np.array_equal(d['label'],label)
                bins=d['bin']
        else:
            bins=category_features(t,b,a,idx)
            np.savez_compressed(f,bin=bins,time=ts,label=label,net=net,delay_correct=(delaylab==1).astype(np.uint8))
        day=(ts//86400000).astype(np.int64)
        days,counts=prefix_stats(bins,label,day)
        for d,cc in zip(days,counts):
            if int(d) not in daily_counts:daily_counts[int(d)]=cc.copy()
            else:daily_counts[int(d)]+=cc
        receipts.append({'name':f.name,'sha256':sha(f),'n':len(ts)})
        (output/'FULL_FEATURE_PROGRESS.json').write_text(json.dumps({
          'source':source,'month':month,'completed_events':int(sum(x['n'] for x in receipts)),
          'parts':receipts,'status':'IN_PROGRESS'},indent=2))
    daily=np.array(sorted(daily_counts),np.int64)
    vals=np.stack([daily_counts[int(d)] for d in daily])
    np.savez_compressed(output/'DAILY_CLASS_COUNTS.npz',days=daily,counts=vals)
    rc={'source':source,'month':month,'source_sha256':sha(raw),'full_eligible_events':int(sum(x['n'] for x in receipts)),
        'full_bin_sources':receipts,'daily_class_counts_sha256':sha(output/'DAILY_CLASS_COUNTS.npz'),
        'feature_names':NAMES,'bins':B,'classification':'incorrect=0,neutral=1,correct=2',
        'scientific_boundary':'all events, trained teacher labels from future; no runtime feature uses future'}
    (output/'FULL_FEATURE_RECEIPT.json').write_text(json.dumps(rc,indent=2));return rc

def complete_fit(source,month,root):
    """Historical training ONLY. No thresholds selected using check outcomes."""
    pos=MONS.index(month)
    target=root/'models'/f'{source}_{month}'
    with np.load(target/'DAILY_CLASS_COUNTS.npz') as d:
        days=d['days'];count=d['counts']
    # days counted in UTC, including source-specific positions.
    a=max(1,int(len(days)*.50));b=max(a+1,int(len(days)*.72))
    if b>=len(days):raise RuntimeError('Not enough chronological days')
    cutoff_train=days[a]*86400000;cutoff_cal=days[b]*86400000
    # Day-disjoint folds imply >30second embargo at boundaries.
    past=np.zeros((K,3,B),np.int64)
    for prev in MONS[:pos]:
        with np.load(root/'models'/f'{source}_{prev}'/'DAILY_CLASS_COUNTS.npz') as d:
            past+=d['counts'].sum(axis=0)
    past+=count[:a].sum(axis=0)
    goodprior=int(past[0,2].sum())
    # Fit strict NP only on calibration days (NOT check). Full input stream.
    cal_scores=[];cal_l=[];cal_net=[];check_stats=[]
    for part in sorted(target.glob('asof_bins_*.npz')):
        with np.load(part) as d:
            ts=d['time'];x=d['bin'];y=d['label'];net=d['net']
        mask=(ts>=cutoff_train)&(ts<cutoff_cal)
        if np.any(mask):
            z=x[mask].reshape(-1,K);p=score(z,past).reshape(-1,2,3)
            q=p[:,:,2]-.65*p[:,:,0]-.20*p[:,:,1]
            choice=np.argmax(q,axis=1)
            cal_scores.append(q[np.arange(len(q)),choice]);cal_l.append(y[mask][np.arange(len(q)),choice]);
            cal_net.append(net[mask][np.arange(len(q)),choice])
    s=np.concatenate(cal_scores);lab=np.concatenate(cal_l);nn=np.concatenate(cal_net)
    variants=[]
    # Rank thresholds fixed BEFORE check. False-class rejection is NP-style
    # development calibration, not a distribution-free live guarantee.
    for q in [.5,.75,.9,.95,.975,.99,.9975]:
        bad=s[lab!=1];th=float(np.quantile(bad,q)) if len(bad) else 1.0
        mask=s>th;n=int(mask.sum());k=int(np.sum(lab[mask]==1));val=float(nn[mask].sum(dtype=np.float64))
        variants.append({'q':q,'threshold':th,'n_cal':n,'correct_cal':k/n if n else None,
          'net_cal':round(val,2),'valid':bool(n and k/n>=.8 and val>0)})
    valid=[v for v in variants if v['valid']]
    selected=max(valid,key=lambda v:v['n_cal']) if valid else None
    # Failed calibrated policies do not authorize entry: still produce frozen
    # diagnostic on CHECK with predeclared .90 threshold, not a deployed policy.
    th=selected['threshold'] if selected is not None else variants[2]['threshold']
    checks={'n':0,'correct':0,'incorrect':0,'neutral':0,'net':0.,'days':{}}
    for part in sorted(target.glob('asof_bins_*.npz')):
        with np.load(part) as d:
            ts=d['time'];x=d['bin'];y=d['label'];net=d['net']
        mask=ts>=cutoff_cal
        if not np.any(mask):continue
        xt=x[mask];yt=y[mask];nt=net[mask];tt=ts[mask]
        p=score(xt.reshape(-1,K),past).reshape(-1,2,3)
        q=p[:,:,2]-.65*p[:,:,0]-.20*p[:,:,1]
        choice=np.argmax(q,axis=1)
        take=q[np.arange(len(choice)),choice]>th
        result=yt[np.arange(len(choice)),choice];money=nt[np.arange(len(choice)),choice]
        checks['n']+=int(take.sum());checks['correct']+=int(np.sum(take&(result==1)))
        checks['incorrect']+=int(np.sum(take&(result==-1)))
        checks['neutral']+=int(np.sum(take&(result==0)))
        checks['net']+=float(np.nansum(money[take]))
        for d in np.unique(tt//86400000):
            mm=take & (tt//86400000==d)
            checks['days'][str(int(d))]={'n':int(mm.sum()),'correct':int(np.sum(mm&(result==1)))}
    checks['survival_correct_rate']=checks['correct']/checks['n'] if checks['n'] else None
    checks['net']=round(checks['net'],2)
    checks['passes_daily_80']=sum(v['n']>0 and v['correct']/v['n']>=.8 for v in checks['days'].values())
    checks['active_days']=len(checks['days'])
    report={'source':source,'month':month,'algorithm':'MULTINOMIAL_BAYES_ASOF_NOW_SEPARATE_NEUTRAL',
        'historical_events_trained':int(past[0].sum()),'prior_correct_actions':goodprior,
        'calibration_decisions':len(s),'calibration_variants':variants,'approved_calibration':selected is not None,
        'frozen_threshold':float(th),'check_diagnostic_OFF_POLICY':checks,
        'true_on_policy_85pct_volume':'NOT_EVALUATED_UNLESS_APPROVED_POLICY_AND_REPLAY',
        'release':'REJECTED' if selected is None else 'SHADOW_REQUIRES_ON_POLICY_REPLAY',
        'scientific_boundary':'decision events overlap; do not count as executed trades. full-month source used; check is last chronological suffix.'}
    (target/'THREE_CLASS_FOLD_RESULT.json').write_text(json.dumps(report,indent=2));return report

if __name__=='__main__':
    pa=argparse.ArgumentParser();pa.add_argument('--source',required=True);pa.add_argument('--month',required=True)
    pa.add_argument('--root',type=Path,default=Path('/mnt/data/next_action_timing'))
    pa.add_argument('--stage',choices=['features','fit'],required=True);r=pa.parse_args()
    result=build_full_bins(r.source,r.month,r.root) if r.stage=='features' else complete_fit(r.source,r.month,r.root)
    print(json.dumps({k:v for k,v in result.items() if k not in ('full_bin_sources','calibration_variants')},indent=2))

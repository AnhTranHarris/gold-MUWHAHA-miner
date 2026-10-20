#!/usr/bin/env python3
"""R00-054 F27: SOURCE-LOCKED, OVERFIT-GUIDED CAUSAL REJECTION RESEARCH.

The original FILTER08 remains a hindsight-contaminated teacher for feature discovery,
never an inference-time input. Original 43 native quote features and 4 expert states
are read from immutable archives. Does NOT reconstruct missing FILTER05 15 quote columns.

Model input has ZERO access to the label of the current or an immature event;
labels are loaded separately only for supervised fit and retrospective evaluation.
"""
from __future__ import annotations
import argparse, csv, gzip, hashlib, io, json, math, os, zipfile
from pathlib import Path
import numpy as np

ROOT=Path('/mnt/data')
HERE=Path(__file__).resolve().parent
SEVEN=ROOT/'XAUUSD_R00_054_SEVEN_MONTH_PORTABLE_RESEARCH_20261019.zip'
BROKERS=('coinexx','dukascopy')
MONTHS=('01','02','06','07')
SOURCE_MANIFEST=ROOT/'R00_054_F25_OVERFIT_MECHANISM_LAB_20261020/SOURCE_ORIGINAL_EVENT_HASHES.json'
EPS=1e-10


def sha256(blob:bytes)->str:
    return hashlib.sha256(blob).hexdigest()


def strict_label(t:np.ndarray, side:np.ndarray, d30:np.ndarray)->np.ndarray:
    """0 correct, 1 opposite, 2 neutral/missing. Never available at decision time."""
    return np.where(np.isfinite(d30)&(side*d30>.10),0,
                    np.where(np.isfinite(d30)&(side*d30<-.10),1,2)).astype(np.int8)


def matured_past_stats(t:np.ndarray, y:np.ndarray, *, ms:int=33000)->np.ndarray:
    """Historical outcome features, published only after t_event + >=33 seconds."""
    if not (np.all(np.diff(t)>=0) and len(t)==len(y)):raise ValueError('UNSORTED_OR_UNMATCHED')
    elig=np.searchsorted(t,t-ms,side='right')
    # prior correctness statistics only, denominator includes neutral/opposite
    good=(y==0).astype(np.int32)
    cum=np.r_[0,np.cumsum(good,dtype=np.int64)]
    stats=[]
    for w in (120000,600000,3600000):
        lo=np.searchsorted(t,t-w,side='left')
        num=elig-lo
        wins=cum[elig]-cum[lo]
        stats.extend((np.where(num>=3,(wins+2.)/(num+4.),.5),np.log1p(np.maximum(num,0))))
    return np.column_stack(stats).astype(np.float32)


def native_features(t:np.ndarray,side:np.ndarray,native:np.ndarray,experts:np.ndarray,y:np.ndarray):
    """Feature family indices stable; do not append actual current outcome to X."""
    assert native.shape==(len(t),43) and experts.shape==(4,len(t))
    x=np.nan_to_num(native.astype(np.float32),nan=-999.,posinf=999.,neginf=-999.)
    states=experts.T.astype(np.float32)
    s=side.astype(np.float32).reshape(-1,1)
    side_indexes=[0,1,2,3,4,5,6,7,8,15,16,17]
    h=(t//3600000)%24
    dow=(t//86400000+3)%7
    cyc=np.column_stack((np.sin(h*np.pi/12),np.cos(h*np.pi/12),np.sin(dow*2*np.pi/7),np.cos(dow*2*np.pi/7),
                         (h>=12)&(h<17),(h>=22)|(h<2))).astype(np.float32)
    shadow=matured_past_stats(t,y)
    xall=np.column_stack((x,states,s,s*x[:,side_indexes],s*states,cyc,shadow)).astype(np.float32)
    names=[f'original_{i:02d}' for i in range(43)]+[f'expert_{i}' for i in range(4)]+['original_side']+[f'side_original_{i:02d}' for i in side_indexes]+[f'side_expert_{i}' for i in range(4)]+['hour_sin','hour_cos','day_sin','day_cos','session_overlap','session_rollover']+[f'matured_{i}' for i in range(6)]
    assert len(names)==xall.shape[1]==76
    return xall,names


def load_one(broker,month,verify=True):
    """Load exact original R00-054 event members from registered source archives.

    Noncausal outcome d30 is *not* included in the model features.
    """
    if broker not in BROKERS or month not in MONTHS:raise ValueError('UNAUTHORIZED_BROKER_MONTH')
    nativepath=ROOT/f'R00_054_NATIVE_CACHE_{broker}_{month}.zip'
    with zipfile.ZipFile(nativepath) as z:
        assert z.testzip() is None
        with np.load(io.BytesIO(z.read(f'cache/native_{broker}_{month}.npz')),allow_pickle=False) as c:
            t=c['t'].copy(); features=c['features'].copy();experts=c['experts'].copy()
    with zipfile.ZipFile(SEVEN) as z:
        data=z.read(f'evidence/FROZEN_R00_054_EVENTS_{broker}_{month}.npz')
    manifest=json.loads(SOURCE_MANIFEST.read_text()) if SOURCE_MANIFEST.exists() else {}
    if verify and manifest:
        expected=manifest[f'{broker}_{month}']['event_member_sha256']
        if sha256(data)!=expected:raise ValueError('SOURCE_EVENT_SHA_MISMATCH')
    with np.load(io.BytesIO(data),allow_pickle=False) as e:
        et=e['t'].copy();side=e['side'].copy();raw=e['d30'].copy();saved=e['correct'].copy()
    if not np.array_equal(t,et):raise ValueError('EVENT_TIMESTAMP_ID_DRIFT')
    if not np.all(np.diff(t)>=0):raise ValueError('EVENT_ORDER')
    if not set(np.unique(side)).issubset({-1,1}):raise ValueError('INVALID_SIDE')
    y=strict_label(t,side,raw)
    if not np.array_equal((y==0).astype(np.int8),saved):raise ValueError('ORIGINAL_OUTCOME_MISMATCH')
    if verify and manifest:
        m=manifest[f'{broker}_{month}']
        if len(t)!=m['n'] or int(sum(y==0))!=m['good']:raise ValueError('ORIGINAL_EVENT_COUNT_DRIFT')
    X,names=native_features(t,side,features,experts,y)
    return dict(broker=broker,month=month,t=t,side=side,y=y,X=X,names=names,sha=sha256(data))


def r9_reference():
    result={}
    with zipfile.ZipFile(SEVEN) as z:
        b=z.read('evidence/R00_054_CONTIGUOUS_UTC_HOURLY.csv.gz')
    with gzip.open(io.BytesIO(b),'rt',newline='') as f:
        for row in csv.DictReader(f):
            result[(row['broker'],int(row['hour_key']))]=int(row['r9_synth_completed_trades'])
    return result


def quota_stats(c,mask,refs):
    """Fast source-matched UTC R9 floor ledger across hour/day/week/month."""
    mask=np.asarray(mask,dtype=bool)
    if len(mask)!=len(c['t']):raise ValueError('MASK_MISMATCH')
    k=c.get('_quota_cache')
    if k is None:
        # Membership, canonical R9 source counts and baseline eligibility never change
        hour=c['t']//3600000
        u,ix=np.unique(hour,return_inverse=True)
        n=np.bincount(ix,minlength=len(u))
        good0=np.bincount(ix,weights=(c['y']==0).astype(np.int8),minlength=len(u)).astype(np.int64)
        r=np.array([refs.get((c['broker'],int(h)),0) for h in u],dtype=np.int64)
        available=r>0
        thr=(9*r+9)//10
        basepass=(good0>=thr)&(n>=thr)&available
        from datetime import date,timedelta
        dates=[date(1970,1,1)+timedelta(days=int(h//24)) for h in u]
        groupkeys={
           'day':np.array([d.toordinal() for d in dates],dtype=np.int64),
           'week':np.array([d.isocalendar().year*100+d.isocalendar().week for d in dates],dtype=np.int64),
           'month':np.array([d.year*100+d.month for d in dates],dtype=np.int64)}
        memberships={}
        for group,key in groupkeys.items():
            unique,inv=np.unique(key,return_inverse=True)
            ref=np.bincount(inv,weights=r*available,minlength=len(unique)).astype(np.int64)
            base=np.bincount(inv,weights=good0*available,minlength=len(unique)).astype(np.int64)
            orig_em=np.bincount(inv,weights=n*available,minlength=len(unique)).astype(np.int64)
            req=(9*ref+9)//10
            memberships[group]=(inv,ref,req,(base>=req)&(orig_em>=req)&(ref>0),unique)
        k={'ix':ix,'u':u,'r':r,'thr':thr,'basepass':basepass,'available':available,'groups':memberships}
        c['_quota_cache']=k
    got=np.bincount(k['ix'],weights=((c['y']==0)&mask).astype(np.int8),minlength=len(k['u'])).astype(np.int64)
    emitted=np.bincount(k['ix'],weights=mask.astype(np.int8),minlength=len(k['u'])).astype(np.int64)
    failed=k['basepass']&((got<k['thr'])|(emitted<k['thr']))
    newfails={'hour':[int(h) for h in k['u'][failed]]}
    for group,(ix,ref,thr,origpass,unique) in k['groups'].items():
        g=np.bincount(ix,weights=got*k['available'],minlength=len(unique)).astype(np.int64)
        em=np.bincount(ix,weights=emitted*k['available'],minlength=len(unique)).astype(np.int64)
        newfails[group]=[int(v) for v in unique[origpass&((g<thr)|(em<thr))]]
    return dict(hours_evaluated=int(sum(k['available'])),
                original_source_hours_uncovered=[int(v) for v in k['u'][k['available']&~k['basepass']]],
                newly_failed_hours=newfails['hour'],newly_failed_days=newfails['day'],
                newly_failed_weeks=newfails['week'],newly_failed_months=newfails['month'],
                eligible_days=int(sum(k['groups']['day'][3])))


def metrics(c,mask,refs):
    y=c['y'];mask=np.asarray(mask,dtype=bool)
    correct=(y==0);bad=~correct
    kept=int(sum(mask));cg=int(sum(mask&correct));bad_rej=int(sum(~mask&bad));good_lost=int(sum(~mask&correct))
    q=quota_stats(c,mask,refs)
    return dict(broker=c['broker'],month=c['month'],signals=len(y),retained=kept,
                correct_total=int(sum(correct)),incorrect_total=int(sum(bad)),correct_kept=cg,correct_lost=good_lost,
                incorrect_rejected=bad_rej,correct_retention=cg/max(1,int(sum(correct))),
                incorrect_rejection=bad_rej/max(1,int(sum(bad))),
                retained_precision=cg/max(1,kept),**q)


def invariant_decision(t,side,decision,*,n_original):
    """Filter may veto, but cannot change original timestamp or BUY/SELL."""
    if len(t)!=n_original or len(side)!=n_original or len(decision)!=n_original:raise ValueError('EVENT_COUNT_CHANGED')
    if not set(np.unique(side)).issubset({-1,1}):raise ValueError('SIDE_MUTATION')
    if not np.isin(decision,[0,1]).all():raise ValueError('INVALID_MASK')


def probabilities(models,X):
    # independent competing classifiers, not direct overfit-teacher probabilities
    pc=models['correct'].predict_proba(X)[:,1]
    pn=models['neutral'].predict_proba(X)[:,1]
    po=models['opposite'].predict_proba(X)[:,1]
    return {'p_correct':pc,'p_opposite_and_neutral':1-.5*(pn+po),
            'p_nonneutral_correct':(1-pn)*(1-po),
            'ensemble_skeptic':np.minimum(pc,(1-pn)*(1-po)),
            'risk_max':1-np.maximum(pn,po)}


def criteria_good(scores,refs,cutoffs,perbroker_c):
    """Evaluate February policy on BOTH distinct brokers; never June/July."""
    out=[]
    for name,cut in cutoffs.items():
        rows=[metrics(c,scores[b][name]>=cut,refs) for b,c in perbroker_c.items()]
        mingood=min(r['correct_retention'] for r in rows)
        nbad=sum(r['incorrect_rejected'] for r in rows);denom=sum(r['incorrect_total'] for r in rows)
        if mingood>=.71 and all(not r['newly_failed_hours'] and not r['newly_failed_days'] and not r['newly_failed_weeks'] and not r['newly_failed_months'] for r in rows):
            out.append((min(r['incorrect_rejection'] for r in rows),nbad/denom,name,cut,rows))
    return out


def select_policy(model, feb,refs,quantiles):
    scores={b:probabilities(model,c['X']) for b,c in feb.items()}
    ranked=[];allrows=[]
    for fam in next(iter(scores.values())):
        ps=np.concatenate([scores[b][fam] for b in BROKERS])
        for q in quantiles:
            cut=float(np.quantile(ps,q))
            rows=[metrics(feb[b],scores[b][fam]>=cut,refs) for b in BROKERS]
            valid=(min(r['correct_retention'] for r in rows)>=.71 and all(not r['newly_failed_hours'] and not r['newly_failed_days'] and not r['newly_failed_weeks'] and not r['newly_failed_months'] for r in rows))
            a=dict(family=fam,quantile=q,cutoff=cut,eligible=bool(valid),min_bad_rejection=min(r['incorrect_rejection'] for r in rows), min_good_retention=min(r['correct_retention'] for r in rows),sum_bad_rejected=sum(r['incorrect_rejected'] for r in rows),rows=rows)
            allrows.append(a)
            if valid: ranked.append(a)
    best=max(ranked,key=lambda x:(x['min_bad_rejection'],x['sum_bad_rejected'])) if ranked else {'family':'KEEP_ALL','quantile':None,'cutoff':None}
    return best,allrows


def train(*,sample=3):
    import lightgbm as lgb
    refs=r9_reference()
    jan=[load_one(b,'01') for b in BROKERS]
    models={}
    cutoff_index=[int(len(c['y'])*.80) for c in jan]
    idx=[np.flatnonzero(c['t']<c['t'][cutoff_index[i]]-40000)[::sample] for i,c in enumerate(jan)]
    X=np.concatenate([c['X'][idx[i]] for i,c in enumerate(jan)])
    y=np.concatenate([c['y'][idx[i]] for i,c in enumerate(jan)])
    params=dict(n_estimators=135,num_leaves=48,max_depth=9,learning_rate=.05,min_child_samples=100,
                colsample_bytree=.82,subsample=.85,subsample_freq=1,reg_lambda=6.,reg_alpha=.25,max_bin=127,
                n_jobs=4,random_state=540027,verbosity=-1)
    for kind,truth in [('correct',y==0),('opposite',y==1),('neutral',y==2)]:
        m=lgb.LGBMClassifier(**params)
        m.fit(X,truth.astype(np.int8));models[kind]=m
        print('FIT',kind,int(sum(truth)),len(y),flush=True)
    from joblib import dump
    for k,m in models.items():dump(m,HERE/f'JAN_POOLED_{k}.joblib',compress=3)
    del X,y,jan
    feb={b:load_one(b,'02') for b in BROKERS}
    frozen=json.loads((HERE/'FROZEN_EXPERIMENT_CONTRACT.json').read_text())
    best,grid=select_policy(models,feb,refs,frozen['frozen_cut_quantiles'])
    (HERE/'ALL_FEBRUARY_POLICY_FAMILIES.json').write_text(json.dumps(grid,indent=2)+'\n')
    chosen=dict(status='HISTORICALLY_SELECTED_FEBRUARY',policy=best, parent_manifest_sha256=sha256(SOURCE_MANIFEST.read_bytes()))
    (HERE/'FROZEN_FEBRUARY_POLICY.json').write_text(json.dumps(chosen,indent=2)+'\n')
    print('FROZEN_FEB',best['family'],best['cutoff'],flush=True)
    del feb
    transfer=[]
    for b in BROKERS:
        for mo in ('06','07'):
            c=load_one(b,mo)
            if best['family']=='KEEP_ALL':mask=np.ones(len(c['y']),bool)
            else: mask=probabilities(models,c['X'])[best['family']]>=best['cutoff']
            invariant_decision(c['t'],c['side'],mask.astype(np.int8),n_original=len(c['y']))
            m=metrics(c,mask,refs)
            m['passes_user_gates']=(m['correct_retention']>=.71 and m['incorrect_rejection']>=.90 and not m['newly_failed_hours'] and not m['newly_failed_days'] and not m['newly_failed_weeks'] and not m['newly_failed_months'])
            print('TRANSFER',b,mo,'good',round(m['correct_retention'],5),'wrong',round(m['incorrect_rejection'],5),'pass',m['passes_user_gates'],flush=True)
            transfer.append(m)
            np.savez_compressed(HERE/f'UNALTERED_EVENT_DECISIONS_{b}_{mo}.npz',t=c['t'],side=c['side'],mask=mask.astype(np.int8),truth=c['y'])
    receipt={'status':'RESEARCH_DIAGNOSTIC_HISTORICALLY_EXPOSED_NOT_BLIND','f27_frozen_contract_sha256':sha256((HERE/'FROZEN_EXPERIMENT_CONTRACT.json').read_bytes()),
             'per_broker_month':transfer,'ALL_USER_GATES_PASS':all(m['passes_user_gates'] for m in transfer),
             'observations':['No FILTER05 last64 ordered quote arrays: 15 features absent relative to original FILTER08','January parent R00-054 itself is Jan-fitted, not end-to-end OOF','June/July historically exposed in prior project, not blind','R9 quotas are candidate direction count floors, not P&L']}
    (HERE/'F27_TRANSFER_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt


def transfer_one(broker,month):
    """Freeze-only replay: uses existing January model bytes and February policy.

    Cannot train or change thresholds. Separate broker/month process controls memory.
    """
    from joblib import load
    from datetime import datetime, timezone
    policy=json.loads((HERE/'FROZEN_FEBRUARY_POLICY.json').read_text())
    models={kind:load(HERE/f'JAN_POOLED_{kind}.joblib') for kind in ('correct','opposite','neutral')}
    c=load_one(broker,month)
    refs=r9_reference()
    chosen=policy['policy']
    if chosen['family']=='KEEP_ALL':mask=np.ones(len(c['y']),bool)
    else:mask=probabilities(models,c['X'])[chosen['family']]>=chosen['cutoff']
    invariant_decision(c['t'],c['side'],mask.astype(np.int8),n_original=len(c['y']))
    m=metrics(c,mask,refs)
    m['passes_user_gates']=(m['correct_retention']>=.71 and m['incorrect_rejection']>=.90 and not any(m[x] for x in ('newly_failed_hours','newly_failed_days','newly_failed_weeks','newly_failed_months')))
    m['frozen_policy_sha256']=sha256((HERE/'FROZEN_FEBRUARY_POLICY.json').read_bytes())
    m['source_event_sha256']=c['sha']
    m['model_sha256']={key:sha256((HERE/f'JAN_POOLED_{key}.joblib').read_bytes()) for key in models}
    m['scored_at_utc']=datetime.now(timezone.utc).isoformat()
    name=f'F27_TRANSFER_{broker}_{month}'
    (HERE/f'{name}.json').write_text(json.dumps(m,indent=2)+'\n')
    np.savez_compressed(HERE/f'UNALTERED_EVENT_DECISIONS_{broker}_{month}.npz',t=c['t'],side=c['side'],mask=mask.astype(np.int8),truth=c['y'])
    print('TRANSFER_FROZEN',broker,month,'correct_retention',round(m['correct_retention'],8),'incorrect_rejection',round(m['incorrect_rejection'],8),'user_gates_pass',m['passes_user_gates'],flush=True)
    return m


def main():
    p=argparse.ArgumentParser();p.add_argument('--train-score',action='store_true');p.add_argument('--self-check',action='store_true')
    p.add_argument('--transfer-only',action='store_true')
    p.add_argument('--broker',choices=BROKERS)
    p.add_argument('--month',choices=MONTHS)
    a=p.parse_args()
    if a.transfer_only:
        if not a.broker or not a.month: p.error('--transfer-only needs --broker and --month')
        transfer_one(a.broker,a.month)
    if a.self_check:
        for b in BROKERS:
            for mo in MONTHS:
                c=load_one(b,mo)
                print('SOURCE_PASS',b,mo,len(c['t']),c['X'].shape[1],c['sha'],flush=True)
    if a.train_score:train()

if __name__=='__main__':main()
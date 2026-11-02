"""Paired, chronology-frozen cross-feed WAIT transfer on the SAME target quotes.

Both source-trained models are evaluated on each held-out target domain. Model
calibration is always done on the target domain's earlier day (A), a separate
B segment fixes the empirical false-action NP cutoff, and no information from
holdout features/labels is used to choose calibrators or policy thresholds.

All rows are overlapping offline teacher events, not executable filled trades.
No policy is promoted by this script; trade-entry validity remains a separate
original tick-exact one-position replay with positive net and volume constraints.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import lightgbm as lgb
from sklearn.metrics import roc_auc_score, brier_score_loss, log_loss
from repaired_training_common import fit_iso, apply_iso
from timing_transition_features import wait_improves_target, TIMING_FEATURE_COUNT, TIMING_FEATURE_VERSION
from decision import calibrate_binary_np
from path_config import artifact_stem

FEEDS=('coinexx','dukascopy')

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1<<20),b''):h.update(block)
    return h.hexdigest()

def partition_calibration(ts,embargo_ms=60000):
    ts=np.asarray(ts,np.int64)
    if len(ts)<1000 or np.any(ts[1:]<ts[:-1]):raise ValueError('calibration quote stream invalid')
    mid=int(ts[len(ts)//2]);a=(ts>=ts[0]+embargo_ms)&(ts<mid-embargo_ms)
    b=(ts>=mid+embargo_ms)&(ts<ts[-1]-embargo_ms)
    if not a.any() or not b.any():raise ValueError('calibration embargo exhausted')
    if ts[a].max()+embargo_ms>=ts[b].min():raise ValueError('calibration overlap')
    return a,b

def stats(y,p,cut):
    y=np.asarray(y,dtype=np.uint8);p=np.asarray(p,np.float64)
    if len(y)!=len(p) or len(p)==0 or np.any(~np.isfinite(p)):
        raise ValueError('invalid target predictions')
    sel=(p>=.80)&(p>cut)
    return dict(rows=len(y),prevalence=float(y.mean()),auc=float(roc_auc_score(y,p)) if y.min()!=y.max() else None,
                brier=float(brier_score_loss(y,p)),logloss=float(log_loss(y,p,labels=[0,1])),
                calibrated_pmax=float(p.max()),strict_p80_selected=int(sel.sum()),
                strict_p80_precision=float(y[sel].mean()) if sel.any() else None)

def calibration_admission(y,p,cut,min_n=150,min_precision=.80):
    """No action gate may rely on a tiny or failing calibration-B selected set."""
    y=np.asarray(y,dtype=np.uint8);p=np.asarray(p,np.float64)
    selected=(p>=.80)&(p>cut)
    n=int(selected.sum());precision=float(y[selected].mean()) if n else None
    approved=bool(n>=min_n and precision is not None and precision>=min_precision)
    return dict(approved=approved,calibration_selected=n,
                calibration_precision=precision,required_n=min_n,
                required_precision=min_precision,
                reason='QUALIFIED_CALIBRATION_ONLY' if approved else 'FAIL_CLOSED_CALIBRATION')

def paired_block_auc(y,p_same,p_cross,ts,seed=20261102,reps=100,block_ms=300000):
    """Resample chronological 5-minute blocks, preserving paired target rows."""
    y=np.asarray(y,np.uint8);p_same=np.asarray(p_same,float);p_cross=np.asarray(p_cross,float)
    block=np.asarray(ts,dtype=np.int64)//int(block_ms)
    _,inv=np.unique(block,return_inverse=True)
    order=np.argsort(inv,kind='stable');lengths=np.bincount(inv);starts=np.cumsum(lengths)-lengths
    rng=np.random.default_rng(seed);values=[]
    for _ in range(reps):
        picks=rng.integers(0,len(lengths),len(lengths))
        ix=np.concatenate([order[starts[j]:starts[j]+lengths[j]] for j in picks])
        if y[ix].min()==y[ix].max():continue
        values.append(float(roc_auc_score(y[ix],p_same[ix])-roc_auc_score(y[ix],p_cross[ix])))
    if not values:raise ValueError('no valid bootstrap replicates')
    vals=np.asarray(values)
    return dict(block_ms=block_ms,blocks=len(lengths),replicates=len(values),
                delta_same_minus_cross_mean=float(vals.mean()),
                ci95_same_minus_cross=[float(v) for v in np.quantile(vals,[.025,.975])],
                fraction_same_better=float((vals>0).mean()))

def load_target(root,source,month,day,max_wait_ms,verify_hash=True):
    stem=artifact_stem(source,month,day);root=Path(root)
    path=root/f'{stem}_wait_transition_X.npy'
    teacher_path=root/f'{stem}_250ms_universe.npz'
    receipt_path=root/f'{stem}_domain_shard_receipt.json'
    if not all(p.exists() for p in (path,teacher_path,receipt_path)):
        raise FileNotFoundError(f'incomplete frozen target shard: {stem}')
    receipt=json.loads(receipt_path.read_text())
    if receipt['source']!=source or receipt['month']!=month or receipt['day']!=day:
        raise ValueError('target receipt identity mismatch')
    if receipt['timing_feature_version']!=TIMING_FEATURE_VERSION or receipt['timing_features']!=TIMING_FEATURE_COUNT:
        raise ValueError('timing feature contract mismatch')
    if verify_hash and (sha256(path)!=receipt['timing_sha256'] or sha256(teacher_path)!=receipt['teacher_sha256']):
        raise ValueError('target teacher/feature SHA mismatch')
    X=np.load(path,mmap_mode='r');d=np.load(teacher_path,allow_pickle=False)
    if X.ndim!=2 or X.shape[1]!=TIMING_FEATURE_COUNT or len(X)!=len(d['ts']):
        raise ValueError('target feature/teacher row mismatch')
    y,_=wait_improves_target(d,max_wait_ms)
    return X,np.asarray(d['ts'],np.int64),np.asarray(y,np.uint8),receipt

def load_models(root,month,expected_fit_days):
    models={};receipts={}
    for source in FEEDS:
        base=f'{source}_{month}_wait_transition_domain_v1';path=Path(root)/f'{base}.txt';rp=Path(root)/f'{base}_fit.json'
        if not path.is_file() or not rp.is_file():raise FileNotFoundError(f'missing fitted domain model {base}')
        receipt=json.loads(rp.read_text())
        if (receipt['source']!=source or receipt['month']!=month or
            receipt['feature_version']!=TIMING_FEATURE_VERSION or receipt['features']!=TIMING_FEATURE_COUNT or
            receipt['fit_days']!=list(expected_fit_days)):
            raise ValueError('model fit receipt mismatch '+base)
        if receipt['model_sha256']!=sha256(path):raise ValueError('model SHA mismatch '+base)
        mdl=lgb.Booster(model_file=str(path))
        if mdl.num_feature()!=TIMING_FEATURE_COUNT:raise ValueError('model features mismatch '+base)
        models[source]=mdl;receipts[source]=receipt
    return models,receipts

def evaluate_target(target,models,root,month,cal_day,holdout_day,embargo_ms,max_wait_ms,bootstrap_reps):
    Xc,tc,yc,creceipt=load_target(root,target,month,cal_day,max_wait_ms)
    Xh,th,yh,hreceipt=load_target(root,target,month,holdout_day,max_wait_ms)
    # Calibration is target-domain local, even when the model was fitted in another feed.
    ca,cb=partition_calibration(tc,embargo_ms)
    hm=th>=th[0]+embargo_ms
    if not hm.any() or tc[-1]+embargo_ms>=th[hm].min():raise ValueError('holdout not after calibration')
    outputs={};preds={}
    for origin in FEEDS:
        m=models[origin]
        pa=m.predict(np.asarray(Xc[ca],np.float32),num_threads=2)
        iso=fit_iso(pa,yc[ca]);pb=apply_iso(iso,m.predict(np.asarray(Xc[cb],np.float32),num_threads=2))
        cutoff,info=calibrate_binary_np(pb,yc[cb].astype(bool),alpha=.10,min_bad=150)
        ph=apply_iso(iso,m.predict(np.asarray(Xh[hm],np.float32),num_threads=2))
        gate=calibration_admission(yc[cb],pb,cutoff)
        outputs[origin]=dict(origin_feed=origin,target_feed=target,
            calibration_B=stats(yc[cb],pb,cutoff),holdout=stats(yh[hm],ph,cutoff),
            calibration_admission=gate,holdout_admissible_p80_selected=(int(((ph>=.80)&(ph>cutoff)).sum()) if gate['approved'] else 0),
            calibration_np_cutoff=float(cutoff),calibration_np_info=info)
        preds[origin]=ph
    boot=paired_block_auc(yh[hm],preds[target],preds[next(s for s in FEEDS if s!=target)],th[hm],reps=bootstrap_reps)
    return dict(target=target,calibration_receipt_sha=creceipt['timing_sha256'],
                holdout_receipt_sha=hreceipt['timing_sha256'],cal_A_rows=int(ca.sum()),cal_B_rows=int(cb.sum()),
                holdout_rows=int(hm.sum()),same_feed=outputs[target],
                cross_feed=outputs[next(s for s in FEEDS if s!=target)],bootstrap=boot,
                qualified_policy=False)

def run(root,model_root,month,fit_days,cal_day,holdout_day,out,embargo_ms=60000,max_wait_ms=1000,bootstrap_reps=100,targets=FEEDS):
    month=str(month).zfill(2);models,receipts=load_models(model_root,month,fit_days)
    results={s:evaluate_target(s,models,root,month,cal_day,holdout_day,embargo_ms,max_wait_ms,bootstrap_reps) for s in targets}
    report=dict(identity='R9_V2_PAIRED_CROSS_FEED_WAIT_TRANSFER_20261102',model_source_sha={s:receipts[s]['model_sha256'] for s in FEEDS},
        fit_days=fit_days,calibration_day=cal_day,untouched_holdout_day=holdout_day,months=[month],
        embargo_ms=embargo_ms,wait_horizon_ms=max_wait_ms,feature_version=TIMING_FEATURE_VERSION,
        feed_local_isotonic_on_calibration_A=True,feed_local_np_on_calibration_B=True,
        holdout_used_for_selection=False,teacher_opportunities_are_overlapping_not_fills=True,
        results=results,policy_promoted=False,status='SOURCE_EXACT_CROSS_FEED_RESEARCH_ONLY')
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2))
    return report

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--models',required=True);p.add_argument('--month',default='01')
    p.add_argument('--fit-days',nargs='+',default=['2026-01-06','2026-01-07'])
    p.add_argument('--cal-day',default='2026-01-08');p.add_argument('--holdout-day',default='2026-01-21')
    p.add_argument('--out',required=True);p.add_argument('--target',choices=FEEDS);p.add_argument('--embargo-ms',type=int,default=60000)
    p.add_argument('--max-wait-ms',type=int,default=1000);p.add_argument('--bootstrap-reps',type=int,default=100)
    a=p.parse_args();r=run(a.root,a.models,a.month,a.fit_days,a.cal_day,a.holdout_day,a.out,a.embargo_ms,a.max_wait_ms,a.bootstrap_reps,(a.target,) if a.target else FEEDS)
    print(json.dumps(r,indent=2))
if __name__=='__main__': main()

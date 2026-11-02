#!/usr/bin/env python3
"""Chronological 60s teacher-guided v2 3-class + WAIT student.

Original 19 causal features exclusively. Hindsight first-passage path under +/-
60sec *only* as training targets. Train/cal/check strictly time ordered by source;
60s embargo between fit/cal/check. Predeclared small capacity sweep calibrated only
on calibration, rejected if 80% strict correct, net and trade volume conflict.
Models are OFF-POLICY on historical confirmed-sequential entries; approval
requires separate all-event ON-POLICY replay after freeze.
"""
from __future__ import annotations
import argparse,json,hashlib,math,os
from pathlib import Path
import numpy as np,lightgbm as lgb
from sklearn.metrics import log_loss,roc_auc_score,brier_score_loss
from teacher_60s import hash_file
MONS=['01','02','06','07']
# PREDECLARED three complexity settings, no adaptive search on the held-out set.
CONFIGS=[{'num_leaves':7,'min_data_in_leaf':150,'lambda_l2':10.0},
         {'num_leaves':15,'min_data_in_leaf':300,'lambda_l2':25.0},
         {'num_leaves':31,'min_data_in_leaf':600,'lambda_l2':50.0}]
SYNTH={'01':27980,'02':33523,'06':31801,'07':24382}


def load(source,month,root):
    path=Path(root)/'teacher'/f'{source}_{month}'/'teacher_60s.npz'
    receipt=path.with_name('receipt.json')
    r=json.loads(receipt.read_text())
    assert r['status']=='COMPLETE_VERIFIED' and r['teacher_file_sha256']==hash_file(path)
    with np.load(path) as v:
        result={k:v[k] for k in ('X','entry_utc_ms','side','observed_class','realized_net','delay_class')}
        lab=result['delay_class']
        # Actual online pending life is <=3000ms; later 5/15/30s oracle
        # observations are scientifically useful but NOT reachable WAIT labels.
        result['wait_rescue']=((lab[:,0]!=1)&np.any(lab[:,1:4]==1,axis=1)).astype(np.uint8)
        result['teacher_60s_later_rescue']=((lab[:,0]!=1)&np.any(lab[:,4:]==1,axis=1)).astype(np.uint8)
        return result

def chronological_partition(t):
    days=np.unique(t//86400000)
    a=max(1,int(len(days)*.50));b=max(a+1,int(len(days)*.72))
    # Both calibration / check must contain at least one active day.
    assert len(days)>4 and b<len(days)
    fit=t < days[a]*86400000-60000
    cal=(t>=days[a]*86400000+60000)&(t<days[b]*86400000-60000)
    chk=t>=days[b]*86400000+60000
    return fit,cal,chk,{'fit_until_day':int(days[a]),'cal_until_day':int(days[b]),'days':len(days)}

def training_arrays(source,month,root):
    ix=MONS.index(month)
    current=load(source,month,root)
    fit,cal,chk,dates=chronological_partition(current['entry_utc_ms'])
    prev=[]
    for m in MONS[:ix]:prev.append(load(source,m,root))
    d=list(prev)+[{k:v[fit] for k,v in current.items()}]
    X=np.concatenate([v['X'] for v in d])
    y=np.concatenate([np.where(v['observed_class']==1,2,np.where(v['observed_class']==0,1,0)).astype(np.uint8) for v in d])
    w=np.concatenate([v['wait_rescue'] for v in d]);n=np.concatenate([v['realized_net'] for v in d])
    return {'X':X,'y':y,'w':w,'net':n,'cal':{k:v[cal] for k,v in current.items()},'check':{k:v[chk] for k,v in current.items()},'dates':dates,
            'train_rows':len(X),'no_future_features':True,'source':source,'month':month}

def fit_models(X,y,w,conf):
    # Categorical bins 0..11 with explicit missing/HTF readiness encoding.
    par={'objective':'multiclass','num_class':3,'learning_rate':.055,'max_depth':-1,
        'feature_fraction':.93,'verbosity':-1,'num_threads':2,'seed':61,**conf}
    three=lgb.train(par,lgb.Dataset(X,label=y,free_raw_data=True),num_boost_round=90)
    p2={'objective':'binary','learning_rate':.055,'verbosity':-1,'num_threads':2,'seed':71,**conf}
    wait=lgb.train(p2,lgb.Dataset(X,label=w,free_raw_data=True),num_boost_round=75)
    return three,wait

def safeauc(y,p):
    return float(roc_auc_score(y,p)) if 0<y.sum()<len(y) else None

def evaluate_calibration(ytrue,net,p,wscore,source,month):
    # NO quota selection based on future sorted scores; only earlier calibration.
    # Worst class=incorrect is more costly than neutral; penalized action score.
    scores=p[:,2]-1.2*p[:,0]-.45*p[:,1]-.2*wscore
    results=[]
    for q in (.50,.75,.85,.90,.95,.98,.99):
        threshold=float(np.quantile(scores,q))
        chosen=scores>threshold
        n=int(chosen.sum());good=int(np.sum(ytrue[chosen]==1))
        res={'quantile':q,'threshold':threshold,'selected':n,'strict_correct':good,
             'precision':good/n if n else 0.,'net':float(np.nansum(net[chosen])),
             'profit_factor':float(np.nansum(np.maximum(0,net[chosen]))/(-np.nansum(np.minimum(0,net[chosen]))+1e-12)) if n else 0.}
        # Feasibility: do not approve merely by shrinking to zero trades
        res['passes_calibration']=bool(n and res['precision']>=.80 and res['net']>0)
        results.append(res)
    valid=[x for x in results if x['passes_calibration']]
    # Most-active feasible threshold, no check-set optimization.
    best=max(valid,key=lambda x:x['selected']) if valid else None
    return results,best

def fold(source,month,root):
    root=Path(root);out=root/'models_reachable_3s'/f'{source}_{month}';out.mkdir(parents=True,exist_ok=True)
    receipt_file=out/'FOLD_RECEIPT.json'
    if receipt_file.exists():
        old=json.loads(receipt_file.read_text());print(json.dumps({'reused_checkpoint':True,'source':source,'month':month}));return old
    a=training_arrays(source,month,root);X=a['X'];y=a['y'];w=a['w'];cal=a['cal'];chk=a['check']
    yc=(cal['observed_class']==1).astype(np.uint8);nc=cal['realized_net'].astype(np.float64)
    names=['spread response','bid response','ask response','cross-side response','mid response','wait elapsed',
           'spread','5s displacement','45s displacement','5m geometry','5m efficiency',
           '5m volatility','1s Hawkes direction','5s Hawkes direction','1s Hawkes spread',
           '15m context','1h context','4h context','session']
    trials=[]
    for i,conf in enumerate(CONFIGS):
        three,wait=fit_models(X,y,w,conf)
        p=three.predict(cal['X']);pw=wait.predict(cal['X'])
        sweep,best=evaluate_calibration(yc,nc,p,pw,source,month)
        valid=bool(best)
        # optimize A/B/C only using earlier calibration; prevent check peeking.
        ll=float(log_loss(np.where(cal['observed_class']==1,2,np.where(cal['observed_class']==0,1,0)),p,labels=[0,1,2]))
        trial={'id':i,'config':conf,'cal_log_loss':ll,'sweep':sweep,'valid':valid,
               'best':best,'cal_wait_auc':safeauc(cal['wait_rescue'],pw)}
        trials.append(trial)
        three.save_model(str(out/f'three_{i}.txt'));wait.save_model(str(out/f'wait_{i}.txt'))
    feasible=[x for x in trials if x['valid']]
    best_trial=min(feasible,key=lambda x:x['cal_log_loss']) if feasible else min(trials,key=lambda x:x['cal_log_loss'])
    frozen_id=best_trial['id'];th=best_trial['best']['threshold'] if best_trial['valid'] else None
    three=lgb.Booster(model_file=str(out/f'three_{frozen_id}.txt'))
    wait=lgb.Booster(model_file=str(out/f'wait_{frozen_id}.txt'))
    pc=three.predict(chk['X']);wc=wait.predict(chk['X']);scores=pc[:,2]-1.2*pc[:,0]-.45*pc[:,1]-.2*wc
    selected=(scores>th) if th is not None else np.zeros(len(scores),bool)
    success=(chk['observed_class']==1)
    # Record OFF-POLICY diagnostic only, selected baseline entries cannot simply
    # be reused to calculate new dynamic-position trade volume.
    held={'rows':len(scores),'correct_base_rate':float(success.mean()),
          'auc_correct':safeauc(success.astype(np.uint8),pc[:,2]),
          'auc_wait_rescue':safeauc(chk['wait_rescue'],wc),
          'threshold':th,'selected':int(selected.sum()),
          'correct_selected':int(np.sum(success&selected)),
          'selected_precision':float(success[selected].mean()) if selected.any() else None,
          'selected_net':float(chk['realized_net'][selected].sum()),
          'policy_approved':False,'off_policy':True}
    receipt={'source':source,'month':month,'train_rows':a['train_rows'],'feature_count':19,'features':names,
      'cal_rows':len(yc),'check_rows':len(scores),'time_splits':a['dates'],'trials':trials,
      'frozen_research_model':frozen_id,'calibrated_threshold':th,
      'heldout':held,'status':'REJECTED_REQUIRES_ON_POLICY_80PCT_ALL_DAYS_AND_MONTHLY_85PCT',
      'hindsight_runtime_used':False,'teacher_60s_is_training_labels_only':True,
      'primary_WAIT_target':'same_side_correct_at_250_1000_3000ms_not_5_15_30s',
      'source_models_sha256':{p.name:hash_file(p) for p in out.glob('*.txt')}}
    receipt_file.write_text(json.dumps(receipt,indent=2))
    print(json.dumps({'source':source,'month':month,'train_rows':len(X),'calibration_valid':bool(feasible),
      'chosen_model':frozen_id,'heldout':held}))
    return receipt

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True,choices=['coinexx','dukascopy']);ap.add_argument('--month',required=True,choices=MONS);ap.add_argument('--root',default='/mnt/data/v2_new_research/sixty');q=ap.parse_args();fold(q.source,q.month,q.root)

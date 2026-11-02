"""Chronological dual action: BUY vs SELL vs WAIT, 3-class and payoff models.

Research trained on ORIGINAL baseline entry timestamps. Input source is complete,
never a small sampled excerpt. A valid future deployable EA requires parity-checked
live tick features, complete 250ms opportunity universe, and new on-policy replay.
"""
from __future__ import annotations
import argparse,json,hashlib,sys,time
from pathlib import Path
import lightgbm as lgb
import numpy as np
from sklearn.metrics import roc_auc_score
from source_exact import load,two_views,labels,canonical,chronological_masks
from decision import calibrate_np,Limits,select_dual

CONFIGS=(dict(num_leaves=15,min_data_in_leaf=500,lambda_l2=25.,max_depth=5),)
ROOT=Path(__file__).resolve().parents[1]

def train(source,month,previous_months=(),rounds=32,experiment=""):
    start=time.monotonic();now=load(source,month)
    tr,cal,check,split=chronological_masks(now['t'])
    tr &= now['valid'];cal &= now['valid'];check &= now['valid']
    past=[load(source,m) for m in previous_months]
    train_events=int(tr.sum())+sum(int(d['valid'].sum()) for d in past)
    fitX=[two_views(d['X'][d['valid']],d['side'][d['valid']]) for d in past]
    fity=[labels({'good':d['good'][d['valid']],'neutral':d['neutral'][d['valid']],'side':d['side'][d['valid']]}) for d in past]
    fitX.append(two_views(now['X'][tr],now['side'][tr]))
    fity.append(labels({k:v[tr] if isinstance(v,np.ndarray) and len(v)==len(now['t']) else v for k,v in now.items()}))
    X=np.concatenate(fitX);Y=np.concatenate(fity)
    assert X.shape[1]==103 and len(X)==len(Y)
    params=dict(objective='multiclass',num_class=3,learning_rate=.05,metric='multi_logloss',
        seed=601,feature_fraction=.95,num_threads=2,verbosity=-1,force_col_wise=True,**CONFIGS[0])
    mdl=lgb.train(params,lgb.Dataset(X,label=Y,free_raw_data=True),num_boost_round=rounds)
    del X,Y,fitX,fity,past
    def pred(mask):
        x=two_views(now['X'][mask],now['side'][mask]);q=mdl.predict(x,num_threads=2).reshape(-1,2,3)
        return q
    cp=pred(cal)
    cy=labels({'good':now['good'][cal],'neutral':now['neutral'][cal],'side':now['side'][cal]}).reshape(-1,2)
    # Cutoffs predeclared separately per side based on wrong+neutral sample.
    cut=[];infos=[]
    for j in range(2):
        th,info=calibrate_np(cp[:,j,2],cy[:,j],alpha=.10)
        cut.append(th);infos.append(info)
    # empirical calibration-only payoff proxy, bucketed by each side's probability.
    # Do not fit an ex-post threshold based on check outcomes.
    pscore=cp[:,:,2]; ncal=canonical(now['net'][cal],now['side'][cal])
    net_est=np.zeros((2,20),np.float32)
    for j in range(2):
        for k in range(20):
            mask=(np.minimum(19,(pscore[:,j]*20).astype(np.int32))==k)
            net_est[j,k]=float(np.nanmean(ncal[mask,j])) if mask.sum()>=100 and np.isfinite(ncal[mask,j]).sum()>=100 else -1.
    def expected(p):
        idx=np.minimum(19,(p[:,:,2]*20).astype(np.int32))
        return np.column_stack((net_est[0,idx[:,0]],net_est[1,idx[:,1]]))
    limits=Limits(min_correct=.8,min_margin=.08)
    act_cal=select_dual(cp,expected(cp),np.asarray(cut),limits)
    pcheck=pred(check)
    act=select_dual(pcheck,expected(pcheck),np.asarray(cut),limits)
    good=canonical(now['good'][check],now['side'][check]);net=canonical(now['net'][check],now['side'][check]);neutral=canonical(now['neutral'][check],now['side'][check])
    actionside=np.where(act==1,0,1);chosen=act!=0;rc=np.arange(len(act))
    match_one=(good.sum(axis=1)==1);truth_side=np.where(good[:,0]==1,1,-1)
    def direction(y,mask):
        return dict(n=int(mask.sum()),matched=int(np.sum(y[mask]==truth_side[mask])),
                    accuracy=float(np.mean(y[mask]==truth_side[mask])) if mask.sum() else None)
    dir_base=np.where(now['side'][check]==1,1,-1)
    baseline_unique=direction(dir_base,match_one)
    ranked_side=np.where(pcheck[:,0,2]>=pcheck[:,1,2],1,-1)
    ranked_unique=direction(ranked_side,match_one)
    selected=(chosen & match_one)
    accepted_unique=direction(act,selected)
    n=int(chosen.sum());g=int(np.sum(good[rc[chosen],actionside[chosen]]))
    actualnet=float(np.nansum(net[rc[chosen],actionside[chosen]]))
    # off-policy: rejected old trade timestamps would expose other online events.
    cal_n=int((act_cal!=0).sum());cal_good=int(np.sum(canonical(now['good'][cal],now['side'][cal])[np.arange(len(cp))[act_cal!=0], np.where(act_cal[act_cal!=0]==1,0,1)])) if cal_n else 0
    roc=[]
    for j in (0,1):
        y=good[:,j]
        roc.append(float(roc_auc_score(y,pcheck[:,j,2])) if 0<y.sum()<len(y) else None)
    out=dict(source=source,month=month,scope='COMPLETE_SOURCE_PAIR_EVENT_OFF_POLICY',
        version='dual_action_3class_BNP_research_v1',source_archive=now['archive'],source_sha256=now['archive_sha256'],
        original_events=len(now['t']),excluded_censored=int((~now['valid']).sum()),historical_previous_months=list(previous_months),
        chronological_split=split,train_action_rows=int(train_events*2),
        calibration_event_count=int(cal.sum()),check_event_count=int(check.sum()),
        class_prob_side_auc=roc,baseline_unique_direction=baseline_unique,
        learned_rank_unique_direction=ranked_unique,selected_unique_direction=accepted_unique,
        side_np_cutoffs=cut,side_np_info=infos,
        calibration_selected=cal_n,calibration_selected_strict_correct=cal_good,
        calibration_selected_rate=(cal_good/cal_n if cal_n else None),
        check_selected=n,check_strict_correct=g,
        check_strict_correct_rate=(g/n if n else None),check_selected_net=actualnet,
        check_total_unique=int(match_one.sum()),
        check_volume_pass='NOT_EVALUATED: requires full on-policy full-month single-position replay',
        qualified_policy=False,model_status='RESEARCH_ONLY_NO_PROMOTION',
        original_feature_count=102,models_use_future_in_inputs=False,
        time_s=round(time.monotonic()-start,2))
    mdlpath=ROOT/'models'/f'{source}_{month}{experiment}_triple_action.txt';mdl.save_model(str(mdlpath))
    out['model_sha256']=hashlib.sha256(mdlpath.read_bytes()).hexdigest()
    (ROOT/'results'/f'{source}_{month}{experiment}_dual_evaluation.json').write_text(json.dumps(out,indent=2))
    # Persist calibration payoff buckets and NP cutoffs (never check-derived)
    np.savez_compressed(ROOT/'models'/f'{source}_{month}{experiment}_policy_data.npz',cutoffs=np.asarray(cut),payoff_bins=net_est)
    print(json.dumps(out,indent=2),flush=True)
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',choices=['coinexx','dukascopy'],required=True)
    p.add_argument('--month',choices=['01','02','06','07'],required=True)
    p.add_argument('--prev',nargs='*',default=[]);p.add_argument('--rounds',type=int,default=32);p.add_argument('--experiment',default='')
    a=p.parse_args();train(a.source,a.month,a.prev,a.rounds,a.experiment)

"""Chronological Jan-06..09 all-observed-250ms pilot evaluation for R9 v2 repair.

This evaluates overlapping teacher candidates only. It is NOT a filled-trade or
on-policy backtest. One-position exact-tick replay is a separate mandatory stage.
"""
from __future__ import annotations
import argparse,hashlib,json,time
from pathlib import Path
import lightgbm as lgb
import numpy as np
from sklearn.metrics import roc_auc_score
from repaired_features import FEATURE_VERSION,REPAIRED_FEATURE_COUNT,REPAIRED_FEATURE_NAMES
from repaired_training_common import (action_labels,fit_iso,apply_iso,choose_prior_weight,calibrate_action_probs,
    apply_action_calibration,raw_action_predict,payoff_lcb_bins,expected_from_bins,runtime_entry_mask)
from decision import Limits,calibrate_np,calibrate_binary_np,select_dual

def sha256(p:Path):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1<<20),b''):h.update(c)
    return h.hexdigest()

def load_component(models_dir,target):
    model_path=Path(models_dir)/f'coinexx_01_250ms_v5_pilot_{target}.txt'
    receipt_path=Path(models_dir)/f'coinexx_01_250ms_v5_pilot_{target}_fit.json'
    if not receipt_path.exists():raise FileNotFoundError(f'missing v5 pilot fit receipt: {receipt_path}')
    receipt=json.loads(receipt_path.read_text())
    if receipt.get('feature_version')!=FEATURE_VERSION or int(receipt.get('feature_count',-1))!=REPAIRED_FEATURE_COUNT:
        raise ValueError(f'stale/incompatible {target} pilot receipt')
    if receipt.get('model_sha256')!=sha256(model_path):raise ValueError(f'{target} pilot model hash mismatch')
    model=lgb.Booster(model_file=str(model_path))
    if model.num_feature()!=REPAIRED_FEATURE_COUNT:raise ValueError(f'{target} pilot feature contract')
    return model,model_path

def load_day(root,day):
    root=Path(root);base=f'coinexx_01_{day}'
    X=np.load(root/f'{base}_250ms_v5_X.npy',mmap_mode='r');d=np.load(root/f'{base}_250ms_universe.npz')
    if X.shape[1]!=REPAIRED_FEATURE_COUNT or len(X)!=len(d['ts']):raise ValueError('shard contract')
    return X,d

def wait_mask(d,max_wait_ms):
    good=d['good'].astype(np.uint8);dt=d['next_dt_ms']
    return (~good.any(axis=1))&(dt>0)&(dt<=max_wait_ms)

def side_priors(root,fit_days,embargo_ms):
    counts=np.zeros((2,3),np.float64)
    for i,day in enumerate(fit_days):
        _,d=load_day(root,day);ts=d['ts'];mask=np.ones(len(ts),bool)
        if i==len(fit_days)-1:mask &= ts < ts[-1]-embargo_ms
        y=action_labels(d['good'].astype(np.uint8),d['neutral'].astype(np.uint8))[mask]
        for j in (0,1):counts[j]=[(y[:,j]==k).sum() for k in range(3)]
    return (counts+1.)/(counts.sum(axis=1,keepdims=True)+3.),counts

def apply_wait(wait_model,iso,X):return apply_iso(iso,wait_model.predict(X,num_threads=2))

def evaluate_segment(name,X,d,mask,opp,opp_iso,models,priors,w,isos,opp_cut,side_cut,paybins,wait_model,wait_iso,wait_cut,limits,max_wait_ms):
    rows=np.where(mask)[0];xx=np.asarray(X[rows],np.float32);good=d['good'][rows].astype(np.uint8);net=d['net'][rows].astype(np.float32)
    yopp=good.any(axis=1);pop=apply_iso(opp_iso,opp.predict(xx,num_threads=2));q=apply_action_calibration(raw_action_predict(models,xx),priors,w,isos)
    est=expected_from_bins(q,paybins);side=select_dual(q,est,side_cut,limits);opp_ok=runtime_entry_mask(pop,opp_cut,xx,limits);act=np.where(opp_ok,side,0).astype(np.int8)
    chosen=act!=0;rr=np.arange(len(rows));sidecol=np.where(act==1,0,1);one=good.sum(axis=1)==1;truth=np.where(good[:,0]==1,1,-1);ranked=np.where(q[:,0,2]>=q[:,1,2],1,-1)
    n=int(chosen.sum());strict=int(good[rr[chosen],sidecol[chosen]].sum()) if n else 0;teacher_net=float(np.nansum(net[rr[chosen],sidecol[chosen]])) if n else 0.
    wm=(~yopp)&(d['next_dt_ms'][rows]>0)&(d['next_dt_ms'][rows]<=max_wait_ms);wr=np.where(wm)[0]
    if len(wr):
        wy=d['next_any_good'][rows][wr].astype(bool);wp=apply_wait(wait_model,wait_iso,xx[wr]);wsel=(wp>=limits.min_opportunity)&(wp>wait_cut)
        wait_auc=float(roc_auc_score(wy,wp)) if wy.any() and (~wy).any() else None
        wait_selected=int(wsel.sum());wait_correct=int(wy[wsel].sum()) if wait_selected else 0
        wait_precision=(wait_correct/wait_selected if wait_selected else None);wait_capture=(wait_correct/wy.sum() if wy.sum() else None)
    else:wait_auc=None;wait_selected=wait_correct=0;wait_precision=wait_capture=None
    return dict(segment=name,events=len(rows),opportunity_auc=float(roc_auc_score(yopp,pop)) if yopp.any() and (~yopp).any() else None,
        learned_rank_unique_accuracy=float(np.mean(ranked[one]==truth[one])) if one.any() else None,
        selected_teacher_actions=n,selected_teacher_strict_good=strict,selected_teacher_strict_good_rate=(strict/n if n else None),selected_teacher_net=teacher_net,
        any_good_events=int(yopp.sum()),neither_good_events=int((~yopp).sum()),both_good_events=int((good.sum(axis=1)==2).sum()),
        wait_evaluable_events=int(len(wr)),wait_auc=wait_auc,wait_selected=wait_selected,wait_selected_next_good=wait_correct,
        wait_selected_precision=wait_precision,wait_next_good_capture_rate=wait_capture)

def main(a):
    start=time.monotonic();root=Path(a.root);models_dir=Path(a.models);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    opp,opp_path=load_component(models_dir,'opportunity');buy,buy_path=load_component(models_dir,'buy');sell,sell_path=load_component(models_dir,'sell');wait,wait_path=load_component(models_dir,'wait')
    priors,prior_counts=side_priors(root,a.fit_days,a.embargo_ms);models=(buy,sell)
    Xc,dc=load_day(root,a.cal_day);ts=dc['ts'];mid=int(ts[len(ts)//2]);cala=(ts>=ts[0]+a.embargo_ms)&(ts<mid-a.embargo_ms);calb=(ts>=mid+a.embargo_ms)&(ts<ts[-1]-a.embargo_ms)
    if not(cala.any() and calb.any()):raise ValueError('calibration split')
    yact=action_labels(dc['good'].astype(np.uint8),dc['neutral'].astype(np.uint8));yopp=dc['good'].any(axis=1).astype(np.uint8)
    qa=raw_action_predict(models,np.asarray(Xc[cala],np.float32));w,prior_loss=choose_prior_weight(qa,yact[cala],priors);_,isos=calibrate_action_probs(qa,yact[cala],priors,w)
    opp_iso=fit_iso(opp.predict(np.asarray(Xc[cala],np.float32),num_threads=2),yopp[cala])
    wma=wait_mask(dc,a.max_wait_ms)&cala
    wait_iso=fit_iso(wait.predict(np.asarray(Xc[wma],np.float32),num_threads=2),dc['next_any_good'][wma].astype(np.uint8))
    qb=apply_action_calibration(raw_action_predict(models,np.asarray(Xc[calb],np.float32)),priors,w,isos)
    cut=[];side_info=[]
    for j in (0,1):
        th,info=calibrate_np(qb[:,j,2],yact[calb,j],alpha=a.alpha,min_bad=150);cut.append(th);side_info.append(info)
    pb=apply_iso(opp_iso,opp.predict(np.asarray(Xc[calb],np.float32),num_threads=2));opp_cut,opp_info=calibrate_binary_np(pb,yopp[calb].astype(bool),alpha=a.alpha,min_bad=150)
    wmb=wait_mask(dc,a.max_wait_ms)&calb;wpb=apply_wait(wait,wait_iso,np.asarray(Xc[wmb],np.float32));wait_cut,wait_info=calibrate_binary_np(wpb,dc['next_any_good'][wmb].astype(bool),alpha=a.alpha,min_bad=150)
    paybins,paycounts=payoff_lcb_bins(qb[:,:,2],dc['net'][calb].astype(np.float32),bins=a.payoff_bins,min_n=150,z=1.64)
    limits=Limits(min_correct=.80,max_wrong=.20,min_margin=.08,min_expected_net=0.,min_opportunity=.80)
    cal_eval=evaluate_segment('calibration_B',Xc,dc,calb,opp,opp_iso,models,priors,w,isos,opp_cut,np.asarray(cut),paybins,wait,wait_iso,wait_cut,limits,a.max_wait_ms)
    Xh,dh=load_day(root,a.check_day);check=dh['ts']>=dh['ts'][0]+a.embargo_ms
    check_eval=evaluate_segment('check',Xh,dh,check,opp,opp_iso,models,priors,w,isos,opp_cut,np.asarray(cut),paybins,wait,wait_iso,wait_cut,limits,a.max_wait_ms)
    top={}
    for name,m in (('OPPORTUNITY',opp),('BUY',buy),('SELL',sell),('WAIT',wait)):
        gain=m.feature_importance(importance_type='gain');ii=np.argsort(gain)[::-1][:25];top[name]=[dict(name=REPAIRED_FEATURE_NAMES[int(i)],gain=float(gain[i])) for i in ii]
    result=dict(identity='R9_V2_250MS_DIRECTION_NEUTRAL_CHRONOLOGICAL_PILOT',feature_version=FEATURE_VERSION,feature_count=REPAIRED_FEATURE_COUNT,
        fit_days=a.fit_days,calibration_day=a.cal_day,check_day=a.check_day,embargo_ms=a.embargo_ms,max_wait_ms=a.max_wait_ms,
        fit_prior_counts=prior_counts.astype(int).tolist(),selected_prior_weight=w,prior_selection_multiclass_logloss=prior_loss,
        calibration_A_rows=int(cala.sum()),calibration_B_rows=int(calb.sum()),opportunity_np_cutoff=float(opp_cut),opportunity_np_info=opp_info,
        side_np_cutoffs=[float(x) for x in cut],side_np_info=side_info,wait_np_cutoff=float(wait_cut),wait_np_info=wait_info,
        payoff_positive_bin_count=[int(np.sum(paybins[j]>0)) for j in (0,1)],payoff_nonempty_bin_count=[int(np.sum(paycounts[j]>=150)) for j in (0,1)],
        calibration_B=cal_eval,check=check_eval,top_features=top,
        component_model_sha256={'opportunity':sha256(opp_path),'buy':sha256(buy_path),'sell':sha256(sell_path),'wait':sha256(wait_path)},
        teacher_candidate_semantics='OVERLAPPING_OFFLINE_OBSERVATIONS_NOT_FILLED_TRADES',historical_250ms_sell_bug_teacher_used=False,
        qualified_policy=False,model_status='PILOT_ONLY_REQUIRES_ONE_POSITION_ON_POLICY_REPLAY_AND_BROADER_CHRONOLOGY',elapsed_sec=round(time.monotonic()-start,2))
    p=out/'coinexx_01_250ms_v5_pilot_evaluation.json';p.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--models',required=True);p.add_argument('--out',required=True);p.add_argument('--fit-days',nargs='+',required=True);p.add_argument('--cal-day',required=True);p.add_argument('--check-day',required=True);p.add_argument('--alpha',type=float,default=.10);p.add_argument('--payoff-bins',type=int,default=30);p.add_argument('--embargo-ms',type=int,default=60000);p.add_argument('--max-wait-ms',type=int,default=1000);main(p.parse_args())

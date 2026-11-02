"""Freeze calibration and evaluate repaired R9 v2 components on untouched chronology."""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import lightgbm as lgb
import numpy as np
from repaired_features import FEATURE_VERSION,REPAIRED_FEATURE_COUNT,REPAIRED_FEATURE_NAMES
from decision import Limits,calibrate_np,calibrate_binary_np
from repaired_training_common import (masks,action_labels,raw_action_predict,choose_prior_weight,calibrate_action_probs,
    apply_action_calibration,fit_iso,apply_iso,payoff_lcb_bins,eval_policy,iso_pack,sha256)

def _load_component(out,source,month,target):
    model_path=out/f'{source}_{month}_repaired_v5_{target}.txt'
    receipt_path=out/f'{source}_{month}_repaired_v5_{target}_fit.json'
    if not receipt_path.exists():raise FileNotFoundError(f'missing v5 fit receipt: {receipt_path}')
    receipt=json.loads(receipt_path.read_text())
    if receipt.get('feature_version')!=FEATURE_VERSION or int(receipt.get('feature_count',-1))!=REPAIRED_FEATURE_COUNT:
        raise ValueError(f'stale/incompatible {target} fit receipt')
    if receipt.get('model_sha256')!=sha256(model_path):raise ValueError(f'{target} model hash mismatch')
    mdl=lgb.Booster(model_file=str(model_path))
    if mdl.num_feature()!=REPAIRED_FEATURE_COUNT:raise ValueError(f'{target} model feature contract mismatch')
    return mdl,model_path

def main(a):
    start=time.monotonic();out=Path(a.out);X=np.load(a.features,mmap_mode='r');lab=np.load(a.labels)
    ts=lab['ts'];good=lab['good'].astype(np.uint8);neutral=lab['neutral'].astype(np.uint8);net=lab['net'].astype(np.float32);baseline=np.where(lab['side']>0,1,-1)
    valid=np.isfinite(net).all(axis=1);tr,cala,calb,chk,split=masks(ts);tr&=valid;cala&=valid;calb&=valid;chk&=valid
    opp,opp_path=_load_component(out,a.source,a.month,'opportunity')
    buy,buy_path=_load_component(out,a.source,a.month,'buy');sell,sell_path=_load_component(out,a.source,a.month,'sell');models=(buy,sell)
    yact=action_labels(good,neutral);yopp=good.any(axis=1).astype(np.uint8)
    counts=np.stack([(yact[tr,j,None]==np.arange(3)).sum(axis=0) for j in (0,1)]).astype(np.float64)
    priors=(counts+1.)/(counts.sum(axis=1,keepdims=True)+3.)
    qa=raw_action_predict(models,X[cala]);w,prior_loss=choose_prior_weight(qa,yact[cala],priors)
    _,isos=calibrate_action_probs(qa,yact[cala],priors,w)
    opp_iso=fit_iso(opp.predict(X[cala],num_threads=2),yopp[cala])
    print('calibration_A frozen',round(time.monotonic()-start,2),'prior_weight',w,flush=True)
    qb=apply_action_calibration(raw_action_predict(models,X[calb]),priors,w,isos)
    cut=[];npinfo=[]
    for j in (0,1):
        th,info=calibrate_np(qb[:,j,2],yact[calb,j],alpha=a.alpha,min_bad=150);cut.append(th);npinfo.append(info)
    pb=apply_iso(opp_iso,opp.predict(X[calb],num_threads=2));opp_cut,opp_info=calibrate_binary_np(pb,yopp[calb].astype(bool),alpha=a.alpha,min_bad=150)
    paybins,paycounts=payoff_lcb_bins(qb[:,:,2],net[calb],bins=a.payoff_bins,min_n=150,z=1.64)
    limits=Limits(min_correct=.80,max_wrong=.20,min_margin=.08,min_expected_net=0.,min_opportunity=.80)
    cal_eval=eval_policy('calibration_B',calb,X,good,net,opp,opp_iso,models,priors,w,isos,opp_cut,np.asarray(cut),paybins,limits,baseline)
    check_eval=eval_policy('check',chk,X,good,net,opp,opp_iso,models,priors,w,isos,opp_cut,np.asarray(cut),paybins,limits,baseline)
    top={}
    for name,mdl in (('BUY',buy),('SELL',sell),('OPPORTUNITY',opp)):
        gain=mdl.feature_importance(importance_type='gain');idx=np.argsort(gain)[::-1][:30]
        top[name]=[dict(name=REPAIRED_FEATURE_NAMES[int(i)],gain=float(gain[i])) for i in idx]
    policy=out/f'{a.source}_{a.month}_repaired_v5_policy.npz';pack=dict(feature_version=np.asarray([FEATURE_VERSION]),feature_count=np.asarray([REPAIRED_FEATURE_COUNT]),
        prior_counts=counts,prior_weight=np.asarray([w]),opportunity_cutoff=np.asarray([opp_cut]),side_cutoffs=np.asarray(cut),payoff_lcb_bins=paybins,payoff_bin_counts=paycounts,
        component_model_sha256=np.asarray([sha256(opp_path),sha256(buy_path),sha256(sell_path)]),
        component_model_role=np.asarray(['opportunity','buy','sell']))
    ox,oy=iso_pack(opp_iso);pack['opp_iso_x']=ox;pack['opp_iso_y']=oy
    for j in (0,1):
        for kind in ('correct','wrong'):
            x,y=iso_pack(isos[(j,kind)]);pack[f'side{j}_{kind}_iso_x']=x;pack[f'side{j}_{kind}_iso_y']=y
    np.savez(policy,**pack)
    result=dict(source=a.source,month=a.month,feature_version=FEATURE_VERSION,feature_count=REPAIRED_FEATURE_COUNT,
        architecture='INDEPENDENT_OPPORTUNITY_BUY_SELL_MODELS',scope='SOURCE_EXACT_BASELINE_ENTRY_POPULATION_OFF_POLICY',split=split,
        fit_events=int(tr.sum()),calibration_A_events=int(cala.sum()),calibration_B_events=int(calb.sum()),check_events=int(chk.sum()),
        bayesian_prior_counts=counts.astype(int).tolist(),selected_prior_weight=w,prior_selection_multiclass_logloss=prior_loss,
        opportunity_np_cutoff=float(opp_cut),opportunity_np_info=opp_info,side_np_cutoffs=[float(x) for x in cut],side_np_info=npinfo,
        payoff_positive_bin_count=[int(np.sum(paybins[j]>0)) for j in (0,1)],payoff_nonempty_bin_count=[int(np.sum(paycounts[j]>=150)) for j in (0,1)],
        calibration_B=cal_eval,check=check_eval,top_features=top,
        component_model_sha256={'opportunity':sha256(opp_path),'buy':sha256(buy_path),'sell':sha256(sell_path)},policy_sha256=sha256(policy),
        qualified_policy=False,model_status='RESEARCH_ONLY_NO_PROMOTION_REQUIRES_FULL_250MS_ON_POLICY_AND_CROSS_MONTH',elapsed_sec=round(time.monotonic()-start,2))
    p=out/f'{a.source}_{a.month}_repaired_v5_evaluation.json';p.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--month',required=True);p.add_argument('--features',required=True);p.add_argument('--labels',required=True);p.add_argument('--out',required=True);p.add_argument('--alpha',type=float,default=.10);p.add_argument('--payoff-bins',type=int,default=30);main(p.parse_args())

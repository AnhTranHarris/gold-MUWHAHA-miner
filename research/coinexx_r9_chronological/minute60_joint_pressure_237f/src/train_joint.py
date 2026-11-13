"""R9 M60 SOURCE-FROZEN quote pressure joint interaction research.

Retains complete original 155-feature extraction and 27 quote-only proxies.
Adds predeclared causal cross-group interactions; never touches R9 trading EA,
entry timestamps, targets, barriers, or source quote logs.
Retrospective chronological checks Jan-Apr -> May ... Jan-Aug -> September.
ALL nine-month final models are IN-SAMPLE ONLY. No model promotion.
"""
from __future__ import annotations
import sys,json,hashlib,zipfile,io,time,gc
from pathlib import Path
import numpy as np
import joblib
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss

ROOT=Path('/mnt/data/r9_m60_joint_20261113')
UP=Path('/mnt/data/r9_m60_proxy_20261113')
sys.path.insert(0,str(UP/'src'))
sys.path.insert(0,str(UP/'deps'))
from train_proxy import read_month as read_source
from event_engine import FEATURE_NAMES as EVENT_NAMES
from proxy_features import FEATURE_NAMES as PROXY_NAMES
from signal_features import FEATURE_NAMES as PRIORITY_NAMES, ACTION_NAMES

# Original base selected features: 14 R9, 25 old HFT, 77 event, 23 priority,
# 11 side-specific analytical, and 5 action metadata = 155; 27 proxies = 182.
NAME_TO_COL={n:39+i for i,n in enumerate(EVENT_NAMES)}
NAME_TO_COL.update({n:116+i for i,n in enumerate(PRIORITY_NAMES)})
NAME_TO_COL.update({n:139+i for i,n in enumerate(ACTION_NAMES)})
NAME_TO_COL.update({n:155+i for i,n in enumerate(PROXY_NAMES)})
NAME_TO_COL.update({'action_side':150,'stop_cents':152,'target_cents':153,'spread_cents':154})
SEED=20261113
CONFIG=dict(objective='binary',n_estimators=160,learning_rate=.04,
 num_leaves=23,min_child_samples=220,reg_alpha=3.,reg_lambda=24.,
 colsample_bytree=.85,subsample=.85,subsample_freq=1,
 random_state=SEED,n_jobs=3,verbosity=-1,max_bin=63,force_col_wise=True)


def _bound(z,scale=1.):
    return np.tanh(z/scale).astype('f4')


def cross_features(x):
    """Input only frozen as-of features (action-conditional side/barriers OK).
    Predeclared physical/causal interactions; no labels, future outcomes or
    evaluation statistics. Saturation prevents extreme quote-gap explosions.
    """
    if x.shape[1]!=182:raise ValueError(f'expected frozen 182 columns; got {x.shape[1]}')
    # Missing 60-second histories remain NaN in the ORIGINAL features; for
    # explicit products, neutralize undefined operands and append availability.
    xc=np.nan_to_num(x.copy(),nan=0.0,posinf=0.0,neginf=0.0)
    c=lambda name:xc[:,NAME_TO_COL[name]]
    missing_60=(~np.isfinite(x[:,NAME_TO_COL['net_mid_u_60000ms']])).astype('f4')
    side=c('action_side')
    sp=np.maximum(1.,c('spread_cents'))
    v1=_bound(side*c('net_mid_u_1000ms')/(sp+1.),1.)
    v5=_bound(side*c('net_mid_u_5000ms')/(sp+1.),1.)
    v60=_bound(side*c('net_mid_u_60000ms')/(sp+1.),2.)
    eff1=np.clip(c('path_eff_1000ms'),0.,1.)
    eff5=np.clip(c('path_eff_5000ms'),0.,1.)
    hawkes1=_bound(side*c('hex_net_200ms'),.6)
    hawkes5=_bound(side*c('hex_net_5000ms'),.6)
    lpfast=_bound(side*c('latent_pressure_fast'),1.4)
    lpslow=_bound(side*c('latent_pressure_slow'),1.4)
    lpdis=_bound(side*c('latent_pressure_disagreement'),1.4)
    qrb1=_bound(side*c('quote_signed_fraction_1000ms'),.6)
    qrb5=_bound(side*c('quote_signed_fraction_5000ms'),.6)
    qaf5=_bound(side*c('qaf_completed_5s'),.6)
    qaf15=_bound(side*c('qaf_completed_15s'),.6)
    cusum=_bound(side*c('cusum_imbalance'),1.4)
    qint1=_bound(side*c('qint_signed_1000ms'),1.4)
    qint5=_bound(side*c('qint_signed_5000ms'),1.4)
    quote_count=np.maximum(0.,c('quotes_per_s_1000ms'))
    quote_density=_bound(np.log1p(quote_count),2.)
    active_spread=_bound(c('res_spread_rel_ew')-1.,.30)
    spread_shock=_bound(c('res_active_shock_excess')/sp,.5)
    spread_recover=np.clip(c('res_recovery_fraction'),0.,1.)
    spread_reversion=_bound(c('res_spread_reversion_rate'),.3)
    unc=np.maximum(0.,c('latent_uncertainty'))
    stable=1./(1.+np.sqrt(unc))
    slow_var=np.maximum(0.,c('realized_vol_u_5000ms'))
    vol_ratio=_bound(slow_var/(sp+1.),4.)
    brownian=np.clip(c('brownian_upper_before_lower'),0.,1.)
    brownian_center=2.*brownian-1.
    brown_hit=np.clip(c('brownian_hit_upper_5s'),0.,1.)
    stop_to_spread=np.clip(c('stop_cents')/sp,0.,20.)
    gates=[v1,v5,v60,eff1,eff5,hawkes1,hawkes5,lpfast,lpslow,
           lpdis,qrb1,qrb5,qaf5,qaf15,cusum,qint1,qint5,
           quote_density,active_spread,spread_shock,spread_recover,
           spread_reversion,stable,vol_ratio,brownian_center,brown_hit,stop_to_spread]
    # Avoid explosion of ALL pairwise products; these are specifically selected
    # mechanisms linking statistical features across independent families.
    term=[
      ('trend1_hawkes_fast',v1*hawkes1),('trend5_hawkes_slow',v5*hawkes5),
      ('trend1_latent',v1*lpfast),('trend5_latent',v5*lpslow),
      ('trend5_cusum',v5*cusum),('trend1_quote_intensity',v1*qint1),
      ('trend5_quote_intensity',v5*qint5),
      ('trend1_qrb',v1*qrb1),('trend5_qrb',v5*qrb5),
      ('trend1_qaf',v1*qaf5),('trend5_qaf',v5*qaf15),
      ('qrb_hawkes',qrb1*hawkes1),('qaf_hawkes',qaf5*hawkes5),
      ('qrb_latent',qrb1*lpfast),('qaf_latent',qaf5*lpslow),
      ('qrb_cusum',qrb5*cusum),('hawkes_latent',hawkes1*lpfast),
      ('hawkes_cusum',hawkes5*cusum),('hawkes_quote_intensity',hawkes1*qint1),
      ('cusum_latent',cusum*lpfast),('cusum_qint',cusum*qint5),
      ('latent_qint',lpfast*qint1),('latent_disagreement_hawkes',lpdis*hawkes1),
      ('latent_uncertainty_flow',stable*qaf5),
      ('spread_shock_hawkes',spread_shock*hawkes1),
      ('spread_shock_latent',spread_shock*lpfast),
      ('spread_recover_qrb',spread_recover*qrb5),
      ('spread_recover_latent',spread_recover*lpslow),
      ('spread_reversion_hawkes',spread_reversion*hawkes1),
      ('spread_reversion_qint',spread_reversion*qint1),
      ('spread_reversion_qaf',spread_reversion*qaf5),
      ('quote_density_hawkes',quote_density*hawkes1),
      ('quote_density_latent',quote_density*lpfast),
      ('quote_density_qrb',quote_density*qrb1),
      ('brownian_latent',brownian_center*lpfast),
      ('brownian_hawkes',brownian_center*hawkes1),
      ('brownian_qrb',brownian_center*qrb5),
      ('brownian_qaf',brownian_center*qaf5),
      ('brownian_recovery',brownian_center*spread_recover),
      ('brownian_shock',brownian_center*spread_shock),
      ('brownian_hit_latent',brown_hit*lpfast),
      ('brownian_hit_hawkes',brown_hit*hawkes5),
      ('brownian_hit_qrb',brown_hit*qrb5),
      ('volatility_hawkes',vol_ratio*hawkes1),
      ('volatility_latent',vol_ratio*lpfast),
      ('volatility_recovery',vol_ratio*spread_recover),
      ('barrier_pressure',stop_to_spread*(hawkes1+lpfast)*.5),
      ('efficient_trend_latent',eff1*v1*lpfast),
      ('efficient_trend_quote',eff5*v5*qrb5),
      ('efficient_trend_hawkes',eff1*v1*hawkes1),
      ('pressure_consensus',np.mean(np.stack([v1,v5,hawkes1,hawkes5,lpfast,lpslow,qrb1,qrb5,cusum,qint1],axis=1),axis=1)),
      ('pressure_conflict',np.std(np.stack([v1,v5,hawkes1,hawkes5,lpfast,lpslow,qrb1,qrb5,cusum,qint1],axis=1),axis=1)),
      ('pressure_vote',np.mean(np.sign(np.stack([v1,v5,hawkes1,hawkes5,lpfast,lpslow,qrb1,qrb5,cusum,qint1],axis=1)),axis=1)),
      ('pressure_alignment_brownian',brownian_center*np.mean(np.stack([v1,hawkes1,lpfast,qrb1,cusum],axis=1),axis=1)),
      ('missing_60s_quote_history',missing_60),
    ]
    names=[name for name,_ in term]
    assert len(names)==len(set(names))
    arr=np.column_stack([v for _,v in term]).astype('f4')
    if not np.isfinite(arr).all():raise ValueError('nonfinite interaction feature')
    return arr,names


def read_month(mm):
    r=read_source(mm)
    x=np.hstack([r['base'],r['proxy']]).astype('f4')
    extra,names=cross_features(x)
    r['X182']=x
    r['X_joint']=np.hstack([x,extra]).astype('f4')
    r['joint_names']=names
    return r


def metrics(r,p):
    y=r['y'];g=r['good'];n=r['n_entries'];sideidx=2*np.arange(n)+(r['r9_side']<0)
    gg=g[sideidx]
    vals={
      'pooled_auc':float(roc_auc_score(y[g],p[g])),
      'r9_direction_auc':float(roc_auc_score(y[sideidx][gg],p[sideidx][gg])),
      'pooled_ap':float(average_precision_score(y[g],p[g])),
      'r9_direction_ap':float(average_precision_score(y[sideidx][gg],p[sideidx][gg])),
      'pooled_brier':float(brier_score_loss(y[g],p[g])),
      'r9_direction_brier':float(brier_score_loss(y[sideidx][gg],p[sideidx][gg])),
      'full_opportunities_scored':int(n),
      'r9_original_y_rate':float(y[sideidx][gg].mean()),
      'original_direction_positive_75cov':None,
      'original_direction_positive_50cov':None,
      'original_direction_counts_75cov':int(np.ceil(.75*n)),
      'original_direction_counts_50cov':int(np.ceil(.5*n)),
      'decision_rule_warning':'top-coverage metrics are DIAGNOSTICS not trade fills or a deployable policy'
    }
    # Selection thresholds anchored exclusively to fitted model scores on train
    # would be required for on-policy trade counts; top-k uses all eval scores,
    # and is explicitly nondeployable ranking diagnostic.
    r9scores=p[sideidx][gg];r9truth=y[sideidx][gg]
    for frac in (.75,.50):
      count=max(1,int(np.ceil(frac*len(r9scores))))
      chosen=np.argpartition(r9scores,-count)[-count:]
      vals[f'original_direction_positive_{int(frac*100)}cov']=float(r9truth[chosen].mean())
    return vals


def sha(f):
    h=hashlib.sha256()
    with open(f,'rb') as fd:
      for b in iter(lambda:fd.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def get_train(train,typ,selected_side=False):
    # Folds are chronological; same-month simultaneous buy/sell duplicates are
    # retained for pooled model, not independent observations for significance.
    key='X_joint' if typ=='joint' else 'X182'
    if selected_side:
      x=[];y=[]
      for r in train:
        idx=2*np.arange(r['n_entries'])+(r['r9_side']<0)
        valid=r['good'][idx]
        x.append(r[key][idx][valid]);y.append(r['y'][idx][valid])
      return np.vstack(x),np.concatenate(y)
    return np.vstack([r[key][r['good']] for r in train]),np.concatenate([r['y'][r['good']] for r in train])


def summarize():
    folds=[json.loads((ROOT/'results'/f'fold_{i:02}.json').read_text()) for i in range(5,10)]
    families=list(folds[0]['models'])
    agg={}
    for name in families:
      group=[f['models'][name] for f in folds]
      agg[name]={
       'mean_pooled_auc':float(np.mean([g['pooled_auc'] for g in group])),
       'mean_original_direction_auc':float(np.mean([g['r9_direction_auc'] for g in group])),
       'mean_original_direction_ap':float(np.mean([g['r9_direction_ap'] for g in group])),
       'pooled_months_ge_075':[folds[i]['evaluation_month'] for i,g in enumerate(group) if g['pooled_auc']>=.75],
       'original_direction_months_ge_075':[folds[i]['evaluation_month'] for i,g in enumerate(group) if g['r9_direction_auc']>=.75],
       'original_direction_positive_75cov':float(np.mean([g['original_direction_positive_75cov'] for g in group])),
       'original_direction_positive_50cov':float(np.mean([g['original_direction_positive_50cov'] for g in group])),
      }
    receipt={'status':'EXPOSED_MONTH_RETROSPECTIVE_RESEARCH_ONLY','data':'Coinexx XAUUSD frozen as-of 2026-01..09 72,129,347 ticks',
      'original_r9_opportunities':303934,'score_target':'5s favorable-first same spread-aware fixed barrier',
      'new_feature_group':'27 previously preserved quote proxies plus '+str(len(cross_features(np.zeros((1,182),dtype=np.float32))[1]))+' predeclared interactions',
      'hyperparam_search':False,'results':folds,'aggregates':agg}
    (ROOT/'results'/'SUMMARY.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('AGGREGATES',json.dumps(agg,indent=2),flush=True)
    return receipt


if __name__=='__main__':
    import argparse
    cli=argparse.ArgumentParser(description='Summarize frozen single-process R9 joint-training receipts; fit with fit_isolated.py and fit_full_isolated.py')
    cli.add_argument('--summary',action='store_true',required=True)
    cli.parse_args()
    summarize()

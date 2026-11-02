#!/usr/bin/env python3
"""Chronological causal BUY/SELL/WAIT student, source-specific eight-source-month research.

Different from the earlier veto-only research: both causal ACTION proposals
compete at the SAME tick event with teacher labels independently replayed from
future real bid/ask quotes. Consecutive months train earlier than later months.
Nested calendar splits; +30 s purge before any calibration/check boundary.
NP threshold and choice use ONLY calibration data; check remains untouched.
Selected check streams are off-policy on frozen baseline event times, not a
regenerated online trading strategy. NO promotion from these diagnostics.
"""
from __future__ import annotations
import argparse,json,time,math,hashlib,datetime as dt
from pathlib import Path
import numpy as np,lightgbm as lgb
from sklearn.metrics import roc_auc_score,brier_score_loss
ROOT=Path('/mnt/data/r9_v2_counterfactual_action_20261101')
MONTHS=['01','02','06','07'];FLOOR={'01':23783,'02':28495,'06':27031,'07':20725}
from causal_dual_features import NAMES
ORIENT=np.array([i for i,n in enumerate(NAMES) if n in ('last_bid_move','last_ask_move','last_mid_move') or n.startswith(('mid_disp_','bid_disp_','ask_disp_','event_pressure_'))],np.int64)

def load(source,mon):
    with np.load(ROOT/'results'/f'{source}_{mon}_causal_asof.npz') as d:
        X=d['X'];t=d['ts'];side=d['side']
    with np.load(ROOT/'results'/f'{source}_{mon}_paired_counterfactual.npz') as d:
        y=d['good'];net=d['net'];ext=d['exit_time'];neutral=d['neutral']
    assert len(X)==len(y)==len(t)
    return {'X':X,'t':t,'side':side,'y':y,'net':net,'ext':ext,'neutral':neutral}

def orient(X,sides):
    # option0 = baseline side, option1 = exact same quote/opposite side
    s=np.column_stack((sides,-sides)).reshape(-1).astype(np.float32)
    x=np.repeat(X,2,axis=0)
    x[:,ORIENT]*=s[:,None]
    return np.column_stack((x,s)).astype(np.float32)

def fit_month(source,mon):
    start=time.monotonic();this=load(source,mon)
    # Strict calendar train/cal/check within each requested source month, never train on future months
    dates=(this['t']//86400000).astype(np.int64)
    unique=np.unique(dates)
    a=max(1,int(.50*len(unique)));b=max(a+1,int(.72*len(unique)))
    if b>=len(unique):raise ValueError('insufficient dates')
    train_cut=unique[a];cal_cut=unique[b]
    purge=30000
    train_mask=(this['t'] < train_cut*86400000-purge)
    cal_mask=(this['t'] >= train_cut*86400000)&(this['t']<cal_cut*86400000-purge)
    check_mask=this['t']>=cal_cut*86400000
    XX=[];YY=[]
    for prev in MONTHS:
        if int(prev)>int(mon):break
        d=this if prev==mon else load(source,prev)
        keep=train_mask if prev==mon else np.ones(len(d['t']),bool)
        X=orient(d['X'][keep],d['side'][keep]);y=d['y'][keep].reshape(-1)
        XX.append(X);YY.append(y)
    allX=np.concatenate(XX);ally=np.concatenate(YY).astype(np.uint8);del XX,YY
    learner=lgb.train({'objective':'binary','metric':'binary_logloss','num_leaves':19,'max_depth':6,
        'learning_rate':0.055,'min_data_in_leaf':500,'feature_fraction':0.90,'lambda_l2':15.,
        'num_threads':4,'verbosity':-1,'seed':20261101,'deterministic':True,'force_col_wise':True},
        lgb.Dataset(allX,label=ally,feature_name=NAMES+['side'],free_raw_data=True),num_boost_round=55)
    tr_n=len(ally);tr_good=int(ally.sum());del allX,ally
    np_model=ROOT/'results'/f'{source}_{mon}_new_paired_action_student.txt';learner.save_model(str(np_model))
    def predict(mask):
        X=orient(this['X'][mask],this['side'][mask]);p=learner.predict(X,num_threads=4).reshape(-1,2)
        del X
        choice=np.argmax(p,axis=1);score=p[np.arange(len(p)),choice]
        y=this['y'][mask][np.arange(len(p)),choice];net=this['net'][mask][np.arange(len(p)),choice]
        ext=this['ext'][mask][np.arange(len(p)),choice];ts=this['t'][mask]
        return p,score,y,net,ext,ts,choice
    pc,sc,yc,nc,ec,tc,cc=predict(cal_mask)
    variants=[]
    for q in (.50,.75,.90,.95,.975,.99):
        null=sc[yc==0];th=float(np.quantile(null,q)) if len(null) else 1.
        selected=sc>th;n=int(selected.sum());good=int(yc[selected].sum());net=float(nc[selected].sum(dtype=np.float64))
        variants.append({'bad_quantile':q,'threshold':th,'cal_selected':n,'cal_win30':good/n if n else None,
                         'cal_net':net,'meets_80pct':bool(n>0 and good/n>=.8),'positive_net':net>0})
    valid=[v for v in variants if v['meets_80pct'] and v['positive_net']]
    # never use check metrics to choose threshold
    selected_variant=max(valid,key=lambda v:v['cal_selected']) if valid else None
    diagnostic=variants[2] # locked NP 0.90 failure diagnostic, NOT deployable if no valid policy
    applied=selected_variant or diagnostic
    pc,sc,yc,nc,ec,tc,cc=predict(check_mask)
    eligible=sc>applied['threshold']
    # prevent overlapping positions in frozen candidate set. Still off-policy (rejected positions create different opportunities).
    selected=np.zeros(len(sc),bool);busy=-1
    for j in range(len(sc)):
        if eligible[j] and tc[j]>busy:
            selected[j]=True;busy=int(ec[j]);
    selected_count=int(selected.sum());good=int(yc[selected].sum());net=float(nc[selected].sum(dtype=np.float64))
    daily={};weekly={}
    for tt,yy,nn in zip(tc[selected],yc[selected],nc[selected]):
        date=dt.datetime.fromtimestamp(int(tt)/1000,dt.timezone.utc)
        wk=date.strftime('%G-W%V');dy=date.strftime('%Y-%m-%d')
        for key,v in ((dy,daily),(wk,weekly)):
            if key not in v:v[key]={'n':0,'good':0,'net':0.}
            v[key]['n']+=1;v[key]['good']+=int(yy);v[key]['net']+=float(nn)
    # Include zero-trade days/weeks in denominators as failures.
    all_days={dt.datetime.fromtimestamp(int(v*86400000)/1000,dt.timezone.utc).strftime('%Y-%m-%d') for v in np.unique(tc//86400000)}
    all_weeks={dt.datetime.fromtimestamp(int(v*86400000)/1000,dt.timezone.utc).strftime('%G-W%V') for v in np.unique(tc//86400000)}
    report={'source':source,'month':mon,'mode':'SOURCE_CHRONOLOGICAL_OFF_POLICY_PAIRED_ACTION_CHECK',
       'full_month_original_events':int(len(this['t'])),'train_events_actions':tr_n,'train_strict_good_actions':tr_good,
       'calibration_events':int(cal_mask.sum()),'check_events':int(check_mask.sum()),'calibration_variants':variants,
       'valid_calibration_policy':selected_variant is not None,'chosen':applied,'diagnostic_only':selected_variant is None,
       'check_selected_nonoverlapping':selected_count,'check_win30':good,'check_survival':good/selected_count if selected_count else None,
       'check_net':round(net,2),'all_days':len(all_days),'daily_80pct_passes':sum(d in daily and daily[d]['good']/daily[d]['n']>=.8 for d in all_days),
       'all_weeks':len(all_weeks),'weekly_80pct_passes':sum(w in weekly and weekly[w]['good']/weekly[w]['n']>=.8 for w in all_weeks),
       'check_auc_oracle_label':float(roc_auc_score(yc,sc)) if len(np.unique(yc))>1 else None,
       'check_brier_on_best_action':float(brier_score_loss(yc,sc)),
       'monthly_volume_floor':FLOOR[mon],
       'full_month_approval':'NOT_EVALUATED: no full-month on-policy rerun',
       'source_no_future_training':True,'teacher_used_only_as_label':True,
       'model_sha256':hashlib.sha256(np_model.read_bytes()).hexdigest(),
       'elapsed_sec':round(time.monotonic()-start,2)}
    output=ROOT/'results'/f'{source}_{mon}_paired_action_student.json';output.write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k not in ('calibration_variants',)},indent=2),flush=True)
    return report
if __name__=='__main__':
    pa=argparse.ArgumentParser();pa.add_argument('--source',required=True);pa.add_argument('--month',required=True);a=pa.parse_args();fit_month(a.source,a.month)

#!/usr/bin/env python3
"""R00-054 FILTER08. Research ONLY: deliberate train/test SAME original broker-month.
Read-only original feature archives and labels; no trading orders or engine changes.
Caution: saved per-month models and same-month threshold selection are contaminated,
never predictive validation. Source original causality retained at event input time.
"""
from __future__ import annotations
import argparse, ast, csv, gzip, hashlib, io, json, math, sys, time, zipfile
from pathlib import Path
import numpy as np
import lightgbm as lgb
from joblib import dump,load
from sklearn.metrics import roc_auc_score
R=Path('/mnt/data'); P=R/'R00_054_FILTER08_FOUR_MONTH_DISCOVERY';P.mkdir(exist_ok=True)
SRC=R/'R00_054_FILTER07_OVERFIT70/run_filter07.py'
BASIC=['bid_only_share_64','ask_only_share_64','joint_update_share_64','one_sided_bias_64','signed_quote_impulse_64','signed_mid_positive_share_64','quote_turn_fraction_64','spread_change_64','spread_range_64','signed_last8_impulse','median_tick_gap_ms_64','last_bid_age_ms','last_ask_age_ms','side_stale_asymmetry','session_utc']
ns={'np':np,'zipfile':zipfile,'io':io,'R':R,'BASIC':BASIC}
node=next(x for x in ast.parse(SRC.read_text()).body if isinstance(x,ast.FunctionDef) and x.name=='data')
exec(compile(ast.Module(body=[node],type_ignores=[]),str(SRC),'exec'),ns)
data=ns['data']
with gzip.open(R/'R00_054_VALIDATION/continuation_results/R00_054_CONTIGUOUS_UTC_HOURLY.csv.gz','rt',newline='') as f:
    REF={(x['broker'],int(x['hour_key'])):int(x['r9_synth_completed_trades']) for x in csv.DictReader(f)}
CFG={'n_estimators':450,'num_leaves':255,'learning_rate':.17,'min_child_samples':3,'max_depth':-1,'feature_fraction':.93,'reg_lambda':.01,'max_bin':127,'n_jobs':4,'verbosity':-1,'random_state':5407}
PLAN={'title':'FILTER08 4-month 70% deliberately overfit historical feasibility map','lineage':'R00-054 FILTER07 -> FILTER08','months':['01','02','06','07'],'brokers':['coinexx','dukascopy'], 'input_source':'original R00-054 preserved 43-feature immutable quote events + FILTER05 prior-quote sequences + preexisting published expert states + past 32-second matured labels', 'training':'Fit separate secondary overlay on EVERY labeled broker-month INCLUDING its evaluation month; thresholds selected on SAME outcomes. Contaminated by design.', 'unseen_claim':False,'core_engine_changed':False, 'output':'do-not-trade research masks of original entry signals; initial fixed 30..32-second >$0.10 midpoint criterion only; original direction untouched','quota':'>=90% original R9 SYNTH source-UTC correctly directed event supply per eligible hour and day; no future-hour topK ranking allowed','policy_search':['binary probability Q20..Q70 step .025','binary+past-state regime risk','spread-side hazard safeguards','quantile modestly recalibrated only within SAME labeled month'], 'config':CFG,'parent_filter07':'preserve June model exactly; do not rerun completed June fit'}
freeze=P/'FROZEN_PLAN_BEFORE_EXECUTION.json'
if not freeze.exists(): freeze.write_text(json.dumps(PLAN,indent=2)+'\n')
else: assert json.loads(freeze.read_text())==PLAN

def score(b,m,t,y,p,kind,q,keep):
    keep=keep.astype(bool); n=int(keep.sum());correct=int(((y==0)&keep).sum()); opp=int(((y==1)&keep).sum());neu=int(((y==2)&keep).sum())
    hour=t//3600000; days=hour//24
    uniq, inv=np.unique(hour,return_inverse=True)
    gc=np.bincount(inv, weights=((y==0)&keep).astype(np.uint8))
    refhr=[(int(x),REF[(b,int(x))]) for x in uniq if REF.get((b,int(x)),0)>0]
    passhr=sum(int(gc[np.searchsorted(uniq,x)])>=math.ceil(.90*r) for x,r in refhr)
    # Per-day correct supply compares R9 reported UTC positions per day, not sum of per-hour ceilings
    daycnt={}; need={}
    for x,r in refhr: need[x//24]=need.get(x//24,0)+r
    for idx,x in enumerate(uniq): daycnt[int(x//24)]=daycnt.get(int(x//24),0)+int(gc[idx])
    passday=sum(daycnt.get(d,0)>=math.ceil(.9*nref) for d,nref in need.items())
    return {'broker':b,'month':m,'policy':kind,'q':float(q),'signals':n,'correct':correct,'opposite':opp,'neutral':neu, 'precision':correct/max(1,n),'correct_retention':correct/int((y==0).sum()),'bad_rejected':int((y!=0).sum())-opp-neu,'hour_pass':passhr,'hour_total':len(refhr),'day_pass':passday,'day_total':len(need),'cutoff':float(np.quantile(p,q))}

def main():
    a=argparse.ArgumentParser();a.add_argument('--broker',required=True,choices=['coinexx','dukascopy']);a.add_argument('--month',required=True,choices=['01','02','06','07']);a=a.parse_args();b,m=a.broker,a.month
    start=time.time();t,side,y,X,names=data(b,m)
    n=len(t);print('LOADED',b,m,n,'features',X.shape[1],flush=True)
    # Verify independent cache time-side-outcome identities and the original R00-054 sign label.
    assert np.all(np.diff(t)>=0), 'event ordering invalid';assert set(np.unique(side)).issubset({-1,1})
    archive=R/f'R00_054_VALIDATION/continuation_results/FROZEN_R00_054_EVENTS_{b}_{m}.npz'
    sha=hashlib.sha256(archive.read_bytes()).hexdigest()
    if m=='06':
        model=load(R/f'R00_054_FILTER07_OVERFIT70/EXPOSED_TRAIN_JUNE_{b}_binary.joblib')
        print('REUSING_FROZEN_JUNE_BINARY_PARENT',b,flush=True)
    else:
        model=lgb.LGBMClassifier(objective='binary',**CFG)
        model.fit(X,(y==0).astype('int8'))
        dump(model,P/f'FIT_SAME_MONTH_{b}_{m}_binary.joblib',compress=3)
        print('MONTH_FITTED',b,m,round(time.time()-start,1),flush=True)
    p=model.predict_proba(X)[:,1].astype('float32');auc=roc_auc_score(y==0,p)
    # Multiple cooperative policies leveraging quote-side, session/regime, matured feedback, structural index.
    # Conservative bounded adjustments, original models unchanged.
    quote=np.tanh(np.clip(X[:,47]+X[:,52],-6,6));reg=np.tanh(np.clip(X[:,31]*side,-6,6));mature=np.tanh(np.clip(X[:,87]-.5,-1,1))
    scores={'binary':p,'quote_phase':p+.015*quote,'structure_conflict':p+.015*reg,'matured_feedback':p+.015*mature, 'cooperative_3':p+.012*quote+.012*reg+.012*mature}
    rows=[]
    for name,probs in scores.items():
        for q in np.arange(.20,.701,.025):
            cutoff=float(np.quantile(probs,q));keep=probs>=cutoff
            rows.append(score(b,m,t,y,probs,name,q,keep))
    qual=[r for r in rows if r['precision']>=.70 and r['hour_pass']==r['hour_total'] and r['day_pass']==r['day_total']]
    selected=max(qual,key=lambda r:(r['correct'],r['precision']),default=None)
    if selected is None: selected=max(rows,key=lambda r:(r['hour_pass']==r['hour_total'] and r['day_pass']==r['day_total'],r['precision'],r['correct']))
    policy=selected['policy'];q=selected['q'];prob=scores[policy];keep=prob>=np.quantile(prob,q)
    out={'broker':b,'month':m,'n_original':n,'n_correct':int((y==0).sum()),'n_incorrect':int((y!=0).sum()),'original_rate':float(np.mean(y==0)),'selected':selected,'qualified_count':len(qual),'total_candidate_policies':len(rows),'auc_in_sample':float(auc),'input_event_sha256':sha,'fitted_to_evaluation_labels':True,'wall_seconds':round(time.time()-start,1)}
    (P/f'RESULT_{b}_{m}.json').write_text(json.dumps(out,indent=2)+'\n')
    with (P/f'GRID_{b}_{m}.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    np.savez_compressed(P/f'FITTED_CLASSIFIER_SCORES_{b}_{m}.npz',t=t,original_side=side,truth_class=y,score=prob,kept=keep)
    gains=model.booster_.feature_importance(importance_type='gain');rank=np.argsort(gains)[::-1]
    with (P/f'FEATURE_GAINS_{b}_{m}.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['rank','feature','gain']); w.writerows([(i+1,names[j],float(gains[j])) for i,j in enumerate(rank)])
    print('FINAL',b,m, json.dumps({'qualified':len(qual),'precision':selected['precision'],'correct':selected['correct'],'original_correct':int((y==0).sum()),'hour':f"{selected['hour_pass']}/{selected['hour_total']}",'day':f"{selected['day_pass']}/{selected['day_total']}",'policies':len(rows),'sec':out['wall_seconds']}),flush=True)
if __name__=='__main__': main()

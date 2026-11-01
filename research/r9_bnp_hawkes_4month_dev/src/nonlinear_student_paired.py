#!/usr/bin/env python3
"""Nonlinear survival/expected-payoff student for causal BNP-Hawkes entries.
Real labels dominate, SYNTH only training weights; blocked days for fit/NP/dev.
No EX5, no MT5 compile, no future or teacher fields in inference matrix.
All output remains research-only; NEVER automatically promotes a policy.
"""
from __future__ import annotations
import collections,glob,json,math,sys
from pathlib import Path
import numpy as np
from scipy.stats import binom
from lightgbm import LGBMClassifier,LGBMRegressor
sys.path.insert(0,str(Path(__file__).resolve().parent))
from four_month_train import read_outcomes
FEAT_NAMES=['impulse','efficiency','hawkes_direction','hawkes_pressure','atr_acceleration',
            'rsi','bollinger','qwap_dislocation','fib_location','clock_agreement','spread_score','raw_spread']

def fetch(out):
    records=[]
    for file in sorted(Path(out).glob('*_candidate_outcomes.csv.gz')):
        for r in read_outcomes(file):records.append(r)
    x=np.asarray([json.loads(r['features'])+[r['spread']] if isinstance(r['features'],str)
                  else r['features']+[r['spread']] for r in records],dtype=np.float32)
    roles=np.asarray([r['role'] for r in records]);y=np.asarray([r['survived'] for r in records]);teacher=np.asarray([r['teacher'] for r in records]);pay=np.asarray([r['net'] for r in records]);return records,x,roles,y,teacher,pay

def np_threshold(scores_neg,alpha,delta=.05):
    scores=np.sort(np.asarray(scores_neg,dtype=np.float64));n=len(scores)
    if n<200:return None
    lo,hi=1,n+1
    while lo<hi:
        k=(lo+hi)//2
        if binom.sf(k-1,n,1-alpha)<=delta:hi=k
        else:lo=k+1
    return float(scores[lo-1]) if lo<=n else None

def replay(records,scores,threshold,spread_limit):
    days=collections.defaultdict(list)
    for i,r in enumerate(records):
        if r['role']!='development_check' or r['spread']>spread_limit:continue
        days[(r['source'],r['date'])].append((i,r))
    taken=[]
    for key,rr in sorted(days.items()):
        rr.sort(key=lambda x:x[1]['utc_ms']);exit_ms=-1
        # At one timestamp, BUY and SELL are competing actions: select the
        # higher-scoring side, not the first CSV row, then enforce nonoverlap.
        proposals=collections.defaultdict(list)
        for ix,r in rr:
            if scores[ix]>threshold:proposals[r['utc_ms']].append((float(scores[ix]),r))
        for when in sorted(proposals):
            if when<=exit_ms:continue
            _,r=max(proposals[when],key=lambda z:(z[0],z[1]['side']))
            taken.append(r);exit_ms=r['exit_utc_ms']
    res={'trades':len(taken),'net':round(sum(r['net'] for r in taken),2),'by_source':{},'by_month':{}}
    for key in ('source','month'):
        for v in sorted({r[key] for r in taken}):
            a=[r for r in taken if r[key]==v]
            res['by_'+key][v]={'n':len(a),'net':round(sum(r['net'] for r in a),2),
                                'mean':round(sum(r['net'] for r in a)/len(a),4),
                                'win':round(sum(r['net']>0 for r in a)/len(a),4)}
    return res

def main(out):
    out=Path(out);records,x,roles,y,t,pay=fetch(out)
    fit=roles=='fit';cal=roles=='np_calibration';dev=roles=='development_check'
    info={'n':len(records),'fit':int(fit.sum()),'np_cal':int(cal.sum()),'dev':int(dev.sum()),
          'input_features':FEAT_NAMES,'includes_synth_teacher_at_inference':False,
          'unseen_months_touched':False,'status':'RESEARCH_ONLY'}
    trials=[];passing=[]
    for leaves in (7,15):
      for teacher_w in (0.,.20):
        weights=np.where((y[fit]==1)&(t[fit]==1),1+teacher_w,1.).astype('float64')
        cfg={'num_leaves':leaves,'n_estimators':100,'max_depth':-1,'learning_rate':.035,
             'min_child_samples':170,'colsample_bytree':.9,'subsample':.9,'subsample_freq':1,
             'reg_lambda':8.,'random_state':731,'n_jobs':2,'verbosity':-1}
        # Payoff prediction better reflects asymmetric loss than classification alone.
        clf=LGBMClassifier(**cfg)
        reg=LGBMRegressor(**cfg)
        clf.fit(x[fit],y[fit],sample_weight=weights)
        reg.fit(x[fit],pay[fit],sample_weight=weights)
        # Uncalibrated combination is a ranking score, not a probability.
        scores=(.6*reg.predict(x)+.4*(clf.predict_proba(x)[:,1]-.5)).astype('float64')
        for alpha in (.05,.15,.30):
          for sp in (.35,.85,1.50):
            neg=scores[cal&(y==0)&(x[:,-1]<=sp)]
            threshold=np_threshold(neg,alpha)
            if threshold is None:continue
            e=replay(records,scores,threshold,sp)
            trial={'leaves':leaves,'teacher_weight':teacher_w,'np_alpha':alpha,'spread_cap':sp,
                   'threshold':threshold,'negative_cal':int(len(neg)),**e}
            trials.append(trial)
            both=e['by_source'];
            if all(both.get(s,{}).get('n',0)>=20 and both[s]['net']>0 for s in ('coinexx','dukascopy')):
                passing.append(trial)
    score=lambda row:min(row['by_source'][s]['mean'] for s in ('coinexx','dukascopy'))
    passing.sort(key=lambda row:score(row),reverse=True)
    info['trials']=len(trials);info['passing']=len(passing)
    info['chosen_development_candidate']=passing[0] if passing else None
    info['best_combined_diagnostic']=max(trials,key=lambda row:row['net']) if trials else None
    info['label_model']='unchanged R9 stop/trail/30s with raw bid/ask; no slippage/margin/stop level; commission=0.02'
    info['qualifications']='Scores uncalibrated; NP risk bound not guaranteed under dependent quotes; 4 development days per month only.'
    (out/'nonlinear_trials.json').write_text(json.dumps(trials,indent=2))
    (out/'nonlinear_summary.json').write_text(json.dumps(info,indent=2))
    print(json.dumps({k:v for k,v in info.items() if k not in ('best_combined_diagnostic','chosen_development_candidate')},indent=2))
    print('CHOSEN',json.dumps(info['chosen_development_candidate']))
    print('BEST',json.dumps(info['best_combined_diagnostic']))
    return info
if __name__=='__main__':main(sys.argv[1])

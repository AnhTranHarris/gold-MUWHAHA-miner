#!/usr/bin/env python3
"""F34 new frozen causal matured-error state: adds 33-second delayed signed outcomes to validated 76 source features.
NOT live/EA; no F34 success until scored per frozen Feb and Jun/Jul with exact member reconciliation.
"""
from __future__ import annotations
import json,io,sys,time,os,hashlib,zipfile,math,warnings
from pathlib import Path
import numpy as np
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score
import joblib
ROOT=Path('/mnt/data');P=ROOT/'R00_054_F34_MATURED_OUTCOME_EPISODE_20261020';P.mkdir(exist_ok=True)
FO=ROOT/'R00_054_F30_ITERATIVE_CAUSAL_FILTER_20261020';sys.path.insert(0,str(FO))
import F27_PARENT_READONLY_SOURCE as src
PINS={'source_master_governor':'https://docs.google.com/document/d/1cYkw43LC5Ot-V686onwQS5cDZRKPyw1T1T6MvbFVSCA/edit','parent':'F33 frozen partial features only','allowed_events':'XAUUSD_R00_054_SEVEN_MONTH_PORTABLE_RESEARCH_20261019.zip','month_clock':'Coinexx -120min Jan/Feb; -180min June/July; Dukascopy native UTC'}

def matured(t,side,d30):
    """All future data below accessed only after timestamp maturation; no t_i d30 accessed in its own row."""
    n=len(t); elig=np.searchsorted(t,t-33000,side='right')
    last=elig-1
    valid=last>=0;ix=last.clip(min=0)
    finite=np.isfinite(d30)
    d=np.where(finite,np.clip(d30,-8,8),0.)
    dside=d*side # historical outcome signed relative historical predicted side
    y=np.where(finite&(dside>.1),0,np.where(finite&(dside<-.1),1,2))
    recent=np.full((n,9),0.,dtype=np.float32)
    for off in range(9):
        j=last-off;v=j>=0;j=j.clip(min=0)
        recent[:,off]=np.where(v, side* d[j],0.) # signed relative TODAY side; causal mature price displacement
    # avoid confusion between stale and real zeros: separate ages and availability
    age=np.where(valid,np.maximum(0,t-t[ix]),999999999).astype('float32')
    features=[(age/1000).clip(0,1000),valid.astype('float32'),
              np.where(valid,side*side[ix],0.),
              np.where(valid,(y[ix]==0).astype(float),.5),
              np.where(valid,(y[ix]==1).astype(float),.5),
              np.where(valid,(y[ix]==2).astype(float),.5)]
    for i in range(9): features.append(recent[:,i]);features.append((last>=i).astype('float32'))
    for w in [60000,180000,600000]:
        lo=np.searchsorted(t,t-w,side='left');den=np.maximum(elig-lo,1)
        idx=np.arange(n)
        # restrict to prior outcomes observable at current event time, never current outcome
        for a in [d,dside,(y==0).astype(float),(y==1).astype(float),(y==2).astype(float),(dside>0).astype(float)]:
            pref=np.r_[0,np.cumsum(a,dtype='float64')];stat=(pref[elig]-pref[lo])/den
            features.append(stat.astype('float32'))
        features.append(np.log1p(np.maximum(elig-lo,0)).astype('float32'))
    # all features depend on t_i and prior mature raw outcomes; no raw current future accessed
    return np.column_stack(features).astype('float32')

def loader(b,m):
    c=src.load_one(b,m)
    with zipfile.ZipFile(src.SEVEN) as z: blob=z.read(f'evidence/FROZEN_R00_054_EVENTS_{b}_{m}.npz')
    with np.load(io.BytesIO(blob)) as f: d=f['d30'].copy()
    x=matured(c['t'],c['side'],d)
    c['X']=np.column_stack((c['X'],x)).astype('float32')
    assert c['X'].shape==(len(c['t']),76+x.shape[1])
    return c

def evaluate(c,score,threshold,refs,fullquota=True):
    mask=(score>=threshold)
    y=c['y']; good=y==0; bad=~good
    ret=mask[good].mean();rej=(~mask[bad]).mean();q=src.quota_stats(c,mask,refs) if fullquota else None
    fail={k:len(q[k]) for k in ('newly_failed_hours','newly_failed_days','newly_failed_weeks','newly_failed_months')} if q else {}
    return dict(correct_kept=int((mask&good).sum()),bad_rejected=int((~mask&bad).sum()),n=int(len(y)),correct_total=int(good.sum()),bad_total=int(bad.sum()),correct_retention=float(ret),incorrect_rejection=float(rej),retained_precision=float(good[mask].mean()) if mask.any() else 0.,quota_failures=fail)

def run():
    plan={'status':'FROZEN_PRE_TRAIN','version':'F34','model_families':['MATURED_LAST9','MATURED_MACRO','ALL_COMBINED'], 'feature_def':'current event side * most recent 9 already matured 30s source midpoint displacements; lagged class and multiwindow time since prior outcome','maturity_ms':33000,'model_train':'Jan first 80%, 40s purge, thinning 1:4, both brokers, no June/July','feb_selection':'last35% Feb, threshold grid 0..0.55 by 0.05 on candidate score, per-broker correct preservation 71% and all Feb R9 interval quota','transfer':'frozen threshold, independent June+July broker-months; no retrospective selection','labels':'+30..32 sec original midpoint, $0.10, missing neutral/incorrect','targets':{'correct_retention':.71,'incorrect_rejection':.90,'extra_intervals':0},'no_original_source_mutation':True,'pinned':PINS}
    (P/'FROZEN_F34_PRE_TRAIN.json').write_text(json.dumps(plan,indent=2)+'\n')
    t0=time.time();refs=src.r9_reference()
    jan={b:loader(b,'01') for b in src.BROKERS}
    Xa=[];ya=[]
    for b,c in jan.items():
        k=int(len(c['t'])*.8);sel=np.flatnonzero(c['t']<c['t'][k]-40000)[::4]
        Xa.append(c['X'][sel]);ya.append((c['y'][sel]==0).astype('int8'))
    X=np.concatenate(Xa);y=np.concatenate(ya)
    from hashlib import sha256
    def mod(name,cols):
        model=LGBMClassifier(n_estimators=150,num_leaves=35,learning_rate=.045,min_child_samples=140,reg_lambda=12,n_jobs=3,verbosity=-1,random_state=54034)
        model.fit(X[:,cols],y)
        joblib.dump({'model':model,'cols':cols},P/f'MODEL_{name}.joblib',compress=3)
        return (model,cols)
    cm=np.r_[0:9,14:21,21:37,43:76]
    ml=np.r_[76:len(X[0])]
    families={'MATURED_LAST9':ml,'MATURED_MACRO':np.r_[cm,ml], 'ALL_COMBINED':np.arange(len(X[0]))}
    models={n:mod(n,cols) for n,cols in families.items()}
    del Xa,ya,X,y,jan
    feb={b:loader(b,'02') for b in src.BROKERS}
    fscore={b:{name:model.predict_proba(c['X'][:,cols])[:,1] for name,(model,cols) in models.items()} for b,c in feb.items()}
    rules={};grid=[]
    for name in families:
        ix={b:np.arange(len(c['y']))>=int(len(c['y'])*.65) for b,c in feb.items()}
        sample=np.concatenate([fscore[b][name][ix[b]] for b in src.BROKERS])
        for quant in np.arange(0,.551,.05):
            cut=float(np.quantile(sample,quant)); rows=[];valid=True
            for b,c in feb.items():
                met=evaluate(c,fscore[b][name],cut,refs)
                gm=c['y'][ix[b]]==0
                sub=(fscore[b][name][ix[b]]>=cut)
                febret=float(np.mean(sub[gm])); febrej=float(np.mean(~sub[~gm]))
                passed=febret>=.71 and not any(met['quota_failures'].values())
                rows.append({'broker':b,'last35_good_retention':febret,'last35_bad_rejection':febrej,'quota_failures':met['quota_failures']})
                valid &= passed
            grid.append(dict(family=name,quantile=round(float(quant),3),threshold=cut,valid=valid,rows=rows))
        choices=[r for r in grid if r['family']==name and r['valid']]
        rules[name]=max(choices,key=lambda r:min(v['last35_bad_rejection'] for v in r['rows'])) if choices else None
    (P/'F34_FEBRUARY_POLICY_GRID.json').write_text(json.dumps(grid,indent=2)+'\n')
    (P/'F34_FEBRUARY_FROZEN_SELECTION.json').write_text(json.dumps(rules,indent=2)+'\n')
    del feb,fscore
    outcome=[]
    for month in ('06','07'):
      for b in src.BROKERS:
        c=loader(b,month)
        for name,(model,cols) in models.items():
          rule=rules[name]
          if rule is None:continue
          score=model.predict_proba(c['X'][:,cols])[:,1]
          res=evaluate(c,score,rule['threshold'],refs)
          outcome.append(dict(family=name,broker=b,month=month,threshold=rule['threshold'],**res))
          print('F34',month,b,name,round(res['correct_retention'],4),round(res['incorrect_rejection'],4),sum(res['quota_failures'].values()),flush=True)
        del c
    aggregate=[]
    for name in models:
        r=[z for z in outcome if z['family']==name]
        if len(r)<4:continue
        g=sum(z['correct_total'] for z in r);bad=sum(z['bad_total'] for z in r);k=sum(z['correct_kept'] for z in r);rem=sum(z['bad_rejected'] for z in r)
        aggregate.append(dict(family=name,correct_total=g,bad_total=bad,correct_kept=k,bad_removed=rem,correct_retention=k/g,bad_rejection=rem/bad,quota_failures=sum(sum(z['quota_failures'].values()) for z in r),all_pass=all(z['correct_retention']>=.71 and z['incorrect_rejection']>=.90 and not any(z['quota_failures'].values()) for z in r)))
    (P/'F34_ALL_TRANSFER_RESULTS.json').write_text(json.dumps(outcome,indent=2)+'\n')
    (P/'F34_AGGREGATE.json').write_text(json.dumps(aggregate,indent=2)+'\n')
    print('F34 RESULTS',json.dumps(aggregate,indent=2), 'seconds',round(time.time()-t0,2),flush=True)
if __name__=='__main__':run()
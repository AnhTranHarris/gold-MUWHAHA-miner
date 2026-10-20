#!/usr/bin/env python3
"""R00-054 FILTER09: month-independent neutral/opposite veto specialists.
Read-only original R00-054 sources/caches/models; Jan fit -> Feb freeze -> Jun/Jul exposed.
Classification diagnostic ONLY; no trade orders or execution; do not claim blind validation.
"""
from __future__ import annotations
import ast,csv,gzip,hashlib,io,json,math,os,sys,time,zipfile
from pathlib import Path
import numpy as np
import lightgbm as lgb
from joblib import dump,load
from numba import njit
ROOT=Path('/mnt/data');OUT=ROOT/'R00_054_FILTER09_MONTH_INDEPENDENT';OUT.mkdir(exist_ok=True)
PARENT=ROOT/'R00_054_FILTER07_OVERFIT70/run_filter07.py'
BASIC=['bid_only_share_64','ask_only_share_64','joint_update_share_64','one_sided_bias_64','signed_quote_impulse_64','signed_mid_positive_share_64','quote_turn_fraction_64','spread_change_64','spread_range_64','signed_last8_impulse','median_tick_gap_ms_64','last_bid_age_ms','last_ask_age_ms','side_stale_asymmetry','session_utc']
npns={'np':np,'zipfile':zipfile,'io':io,'R':ROOT,'BASIC':BASIC}
node=next(v for v in ast.parse(PARENT.read_text()).body if isinstance(v,ast.FunctionDef) and v.name=='data')
exec(compile(ast.Module(body=[node],type_ignores=[]),str(PARENT),'exec'),npns)
data=npns['data']
REF={}
with gzip.open(ROOT/'R00_054_VALIDATION/continuation_results/R00_054_CONTIGUOUS_UTC_HOURLY.csv.gz','rt',newline='') as f:
 for row in csv.DictReader(f): REF[(row['broker'],int(row['hour_key']))]=int(row['r9_synth_completed_trades'])
PLAN={
 'name':'R00-054 FILTER09: two-stage independent neutral/opposite hazard + N/O/S/R/M state lifecycles',
 'parent_sha':'f05028d3b50a93c77847206d32a0518af56bc574',
 'months':{'01':'JAN_fit','02':'FEB_policy_freeze','06':'EXPOSED_transfer','07':'EXPOSED_transfer'},
 'brokers':['coinexx','dukascopy'], 'baseline':'R00-054 original 5-sec event, immutable BUY/SELL and original +30..32 second signed midpoint labels, neutrals incorrect',
 'inputs':'unaltered original 43 R00-054 features, 15 ordered-quote, 4 independently published expert states, 6 matured prior labels, 12 side-relative features, timestamp context; source-native prior tick only',
 'fitting':'broker-independent N and O risk estimators trained only using first 75pct JAN chronologically; 40sec purge to Jan last25pct diagnostic; February per-broker numerically frozen thresholds; never use Jun/Jul outcomes for selection',
 'episodes':'N quote availability; O side-opposition; S completed HTF expert structure; R regime and session; M matured prior shadow. Each independently ARMs, confirms after next past-known event, expires on contradiction/age, cooldown, rearms. At decision only past/current tick-visible state.',
 'mechanisms':['neutral-risk','opposite-risk-conditioned-nonneutral','joint-survival','cooperative-two-or-more','cooperative-three-or-more','neutral-specialist-veto','opposite-specialist-veto','structure-regime-veto'],
 'selection':'on February, rank candidates by uplift in correctly directed count retained at <=0 incremental R9 eligible-hour/day failures; ties select higher accuracy then fewer vetoes. Report all failures; never select Jun/Jul score.',
 'units':'no fills, no PnL; R9 reference is synthetic completed-position count, not live executable orders',
 'params':{'estimators':100,'leaves':19,'min_leaf':130,'lr':0.045,'max_bin':63,'seed':9054,'early_purge_ms':40000},
 'no_overlay_of_same_month_overfit':True}
pl=OUT/'FROZEN_PLAN_PRE_SCORING.json'
if pl.exists(): assert json.loads(pl.read_text())==PLAN
else: pl.write_text(json.dumps(PLAN,indent=2)+'\n')

@njit(cache=True)
def episodic(t,trigger,expire_ms,cooldown_ms):
    """State 0 idle, 1 ARM, 2 CONFIRM, 3 cooldown; output 1 only after separate event confirmation.
    Current trigger is at current event, output is observable at decision timestamp.
    """
    n=len(t);on=np.zeros(n,np.int8);phase=np.zeros(n,np.int8);age=np.zeros(n,np.float32);count=np.zeros(n,np.int32)
    stage=0;armed=0;confirmed=0;cool=0;positive=0;episode=0;off_count=0
    for i in range(n):
        now=t[i]
        if i>0 and (now<t[i-1] or now-t[i-1]>7200000):
            stage=0;off_count=0
        if stage==3 and now>=cool: stage=0
        if stage==2:
            if now-confirmed>expire_ms or now-armed>expire_ms*2:
                stage=3;cool=now+cooldown_ms
            elif not trigger[i]:
                off_count+=1
                if off_count>=2:
                    stage=3;cool=now+cooldown_ms
            else: off_count=0
        if stage==1:
            if now-armed>expire_ms or not trigger[i]:
                stage=3;cool=now+cooldown_ms
            elif now>armed:
                stage=2;confirmed=now;episode+=1;off_count=0
        if stage==0 and trigger[i]:
            stage=1;armed=now
        phase[i]=stage;count[i]=episode
        if stage==2:
            on[i]=1;age[i]=(now-confirmed)/1000.
    return on,phase,age,count

def make_lifecycles(t,X,thresholds):
    # All five triggers at a decision event derived from causal features or earlier matured labels.
    triggers=[
      (X[:,53]>thresholds['gap_hi']) | ((X[:,14]>thresholds['spread_hi']) & (X[:,13]<thresholds['tick_low'])),
      (X[:,75]<thresholds['quote_impulse_low']) & ((X[:,63]<thresholds['side_return_low']) | (X[:,76]<thresholds['last8_low'])),
      (X[:,70]<thresholds['htf_low']) & ((X[:,58:62]<0).sum(axis=1)>=1),
      (X[:,20]>thresholds['vol_hi']) | (X[:,20]<thresholds['vol_lo']) | (X[:,86]>.5),
      (X[:,87]<thresholds['mature_low']) & (X[:,89]<thresholds['mature_low_long'])]
    settings=[(45000,20000),(30000,15000),(120000,30000),(240000,30000),(300000,25000)]
    out=[];flags=[]
    for tr,(ttl,cool) in zip(triggers,settings):
        act,phase,age,ep=episodic(t,tr.astype(np.bool_),ttl,cool)
        flags.append(act)
        out.extend([act.astype('float32'),phase.astype('float32'),np.log1p(age)])
    return np.column_stack(out).astype('float32'),np.column_stack(flags).astype('int8')

def calc_thresholds(X):
    q=lambda i,p:float(np.quantile(X[:,i],p))
    return {'gap_hi':q(53,.8),'spread_hi':q(14,.75),'tick_low':q(13,.3),
      'quote_impulse_low':q(75,.32),'side_return_low':q(63,.35),'last8_low':q(76,.32),
      'htf_low':q(70,.33),'vol_hi':q(20,.85),'vol_lo':q(20,.15),
      'mature_low':q(87,.35),'mature_low_long':q(89,.35)}

# Chosen before reading any Feb labels. Model N has neutral-focused quotes + market context;
# O has direction-conditioned structure, quote response, expert states and matured shadows.
N_IDX=np.r_[np.arange(9,43),np.arange(43,62),np.arange(81,93),np.arange(93,108)]
O_IDX=np.r_[np.arange(0,12),np.arange(14,43),np.arange(43,62),np.arange(62,81),np.arange(81,93),np.arange(93,108)]

def score(b,t,y,mask):
    mask=mask.astype(bool)
    totals={'signals':int(mask.sum()),'correct':int(((y==0)&mask).sum()),'opposite':int(((y==1)&mask).sum()),'neutral':int(((y==2)&mask).sum()),'correct_retention':float(((y==0)&mask).sum()/max(1,(y==0).sum()))}
    totals['accuracy']=totals['correct']/max(1,totals['signals']);totals['bad_removed']=int(((y!=0)&~mask).sum())
    hour=t//3600000;u,inv=np.unique(hour,return_inverse=True)
    gc=np.bincount(inv,weights=((y==0)&mask).astype(np.int8),minlength=len(u))
    base=np.bincount(inv,weights=(y==0).astype(np.int8),minlength=len(u))
    allowed={};origpass=0;passhour=0;newbad=0
    for i,h in enumerate(u):
        n=REF.get((b,int(h)),0)
        if n>0:
            need=math.ceil(.9*n);ok=base[i]>=need;origpass+=int(ok);p=gc[i]>=need;passhour+=int(p)
            if ok and not p:newbad+=1
            allowed[int(h//24)]=allowed.get(int(h//24),[0,0,0])
            allowed[int(h//24)][0]+=n;allowed[int(h//24)][1]+=gc[i];allowed[int(h//24)][2]+=base[i]
    newday=0;passday=0;origday=0
    for n,g,v in allowed.values():
        need=math.ceil(.9*n);newday+=int(v>=need and g<need);passday+=int(g>=need);origday+=int(v>=need)
    totals.update({'r9_hours_pass':passhour,'r9_hours_baseline_pass':origpass,'r9_hours_with_reference':sum(REF.get((b,int(h)),0)>0 for h in u),'new_r9_hour_fails':newbad,'r9_days_pass':passday,'r9_days_baseline_pass':origday,'r9_days_with_reference':len(allowed),'new_r9_day_fails':newday})
    return totals

def candidates(pn,po,flags):
    # Each candidate is evaluated as-of-event and has numerical thresholds frozen in FEB.
    pc=(1-pn)*(1-po)
    risk=pn+(1-pn)*po
    nv,ov,sv,rv,mv=[flags[:,i].astype(bool) for i in range(5)]
    confirmations=flags.sum(axis=1)
    risk_sets={'joint':risk,'neutral':pn,'opposite':po,'max':np.maximum(pn,po),'conditional_product':1-pc}
    for k,rr in risk_sets.items():
        for q in (.40,.50,.60,.70,.80):
            thr=float(np.quantile(rr,q))
            yield f'{k}_Q{q:.2f}',rr,thr,None,None
    for minvotes in (2,3):
        for gate in ('all','N_or_O','S_and_R','N_and_O','M_or_S'):
            support={'all':np.ones(len(pn),bool),'N_or_O':nv|ov,'S_and_R':sv&rv,'N_and_O':nv&ov,'M_or_S':mv|sv}[gate]
            agree=support & (confirmations>=minvotes)
            for q in (.50,.65,.80):
                thresh=float(np.quantile(risk,q))
                yield f'cooperative_{minvotes}_{gate}_Q{q:.2f}',risk,thresh,agree,gate

def process_broker(b):
    t0=time.time(); t,s,y,X,names=data(b,'01');assert X.shape[1]==93
    th=calc_thresholds(X);(OUT/f'JAN_ONLY_EPISODE_THRESHOLDS_{b}.json').write_text(json.dumps(th,indent=2))
    life,flags=make_lifecycles(t,X,th); Z=np.column_stack((X,life)).astype('float32')
    k=int(.75*len(t));limit=t[k]-40000;trainidx=np.flatnonzero(t<limit)[::2]
    cfg=dict(n_estimators=PLAN['params']['estimators'],num_leaves=PLAN['params']['leaves'],learning_rate=PLAN['params']['lr'],min_child_samples=PLAN['params']['min_leaf'],max_bin=PLAN['params']['max_bin'],n_jobs=4,verbosity=-1,random_state=9054)
    print('TRAIN',b,'JAN',len(trainidx),'sampled from',len(t),'N',int((y[trainidx]==2).sum()),'O',int((y[trainidx]==1).sum()),flush=True)
    neutral=lgb.LGBMClassifier(objective='binary',**cfg)
    neutral.fit(Z[trainidx][:,N_IDX],(y[trainidx]==2).astype('int8'))
    dump(neutral,OUT/f'JAN_NEUTRAL_SPECIALIST_{b}.joblib',compress=3)
    nonneutral=trainidx[y[trainidx]!=2]
    opposite=lgb.LGBMClassifier(objective='binary',**cfg)
    opposite.fit(Z[nonneutral][:,O_IDX],(y[nonneutral]==1).astype('int8'))
    dump(opposite,OUT/f'JAN_OPPOSITE_SPECIALIST_{b}.joblib',compress=3)
    npred=neutral.predict_proba(Z[k:][:,N_IDX])[:,1]; opred=opposite.predict_proba(Z[k:][:,O_IDX])[:,1]
    jan_train_score=score(b,t[k:],y[k:],np.ones(len(y)-k,bool))
    jan_hold_score=score(b,t[k:],y[k:],(npred+(1-npred)*opred)<np.quantile(npred+(1-npred)*opred,.6))
    print('JAN_CHRONO_AUDIT',b,'baseline',jan_train_score['accuracy'],'masked',jan_hold_score['accuracy'],'sec',round(time.time()-t0,1),flush=True)
    del X,Z,life,flags,t,s,y
    t,s,y,X,names=data(b,'02');life,flags=make_lifecycles(t,X,th);Z=np.column_stack((X,life)).astype('float32');
    pn=neutral.predict_proba(Z[:,N_IDX])[:,1];po=opposite.predict_proba(Z[:,O_IDX])[:,1];
    baseline=score(b,t,y,np.ones(len(y),bool));rows=[];book={}
    for name,risk,thr,gate,gname in candidates(pn,po,flags):
        veto=risk>thr
        if gate is not None:veto &= gate
        result=score(b,t,y,~veto); result.update({'policy':name,'threshold':thr,'risk_type':name.split('_Q')[0].split('_')[0],'gate':gname,'vetoes':int(veto.sum())});rows.append(result);book[name]=(name,thr)
    # objective: pass all previously passed R9 hours and days; improve correct/incorrect selectivity.
    good=[r for r in rows if r['new_r9_hour_fails']==0 and r['new_r9_day_fails']==0 and r['accuracy']>baseline['accuracy']]
    # never zero baseline: if no candidate qualifies, KEEP_ALL is a valid pre-registered answer.
    best=max(good,key=lambda r:(r['accuracy'],r['correct'],r['signals']),default=None)
    if best is None:
        best={**baseline,'policy':'KEEP_ALL','threshold':None,'gate':None,'vetoes':0}
    freeze={'broker':b,'selection_month':'02','selected':best,'feb_baseline':baseline,'jan_last25pct_baseline':jan_train_score,'jan_last25pct_trial':jan_hold_score,'tested_candidates':len(rows),'models':['JAN_NEUTRAL_SPECIALIST_'+b+'.joblib','JAN_OPPOSITE_SPECIALIST_'+b+'.joblib']}
    (OUT/f'FEB_FROZEN_POLICY_{b}.json').write_text(json.dumps(freeze,indent=2))
    with (OUT/f'FEB_ALL_{b}.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print('FEB_FROZEN',b,best['policy'],'precision',round(best['accuracy'],6),'vs baseline',round(baseline['accuracy'],6),'NEW_HOUR_FAILS',best['new_r9_hour_fails'],flush=True)
    del t,s,y,X,life,flags,Z,pn,po
    for m in ('06','07'):
        t,s,y,X,names=data(b,m);life,flags=make_lifecycles(t,X,th);Z=np.column_stack((X,life)).astype('float32')
        pn=neutral.predict_proba(Z[:,N_IDX])[:,1];po=opposite.predict_proba(Z[:,O_IDX])[:,1]
        name=best['policy'];base=score(b,t,y,np.ones(len(y),bool))
        if name=='KEEP_ALL':keep=np.ones(len(y),bool);risk=np.zeros(len(y),np.float32)
        else:
            risks={'joint':pn+(1-pn)*po,'neutral':pn,'opposite':po,'max':np.maximum(pn,po),'conditional_product':pn+(1-pn)*po}
            risk=risks['joint'] if name.startswith('cooperative_') else risks[name.split('_Q')[0]]
            veto=risk>best['threshold']
            if name.startswith('cooperative_'):
                parts=name.split('_');minvotes=int(parts[1]);gate=best['gate'];nv,ov,sv,rv,mv=[flags[:,i].astype(bool) for i in range(5)]
                support={'all':np.ones(len(y),bool),'N_or_O':nv|ov,'S_and_R':sv&rv,'N_and_O':nv&ov,'M_or_S':mv|sv}[gate]
                veto &= support & (flags.sum(axis=1)>=minvotes)
            keep=~veto
        output=score(b,t,y,keep);output.update({'broker':b,'month':m,'policy':name,'baseline':base,'original_event_count':len(y),'original_correct':int((y==0).sum()),'validation_type':'HISTORICALLY_EXPOSED_JUNE_JULY_NOT_BLIND'})
        (OUT/f'TRANSFER_{b}_{m}.json').write_text(json.dumps(output,indent=2))
        # Minimal event-level record only, derivative of original immutable complete ledgers
        np.savez_compressed(OUT/f'FROZEN_DECISIONS_{b}_{m}.npz',t=t,side=s,label=y,keep=keep.astype('int8'),risk=np.asarray(risk,dtype='float32'),N_state=flags[:,0],O_state=flags[:,1],S_state=flags[:,2],R_state=flags[:,3],M_state=flags[:,4])
        print('TRANSFER',b,m,name,'correct',output['correct'],'/',base['correct'],'accuracy',round(output['accuracy'],5),'base',round(base['accuracy'],5),'newhourmiss',output['new_r9_hour_fails'],'newdaymiss',output['new_r9_day_fails'],flush=True)
        del t,s,y,X,life,flags,Z,pn,po
    print('FINISHED',b,'sec',round(time.time()-t0,1),flush=True)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--broker',required=True,choices=['coinexx','dukascopy']);b=p.parse_args().broker
    print('FROZEN_RESEARCH_PLAN_SHA256',hashlib.sha256(pl.read_bytes()).hexdigest(),flush=True)
    process_broker(b)

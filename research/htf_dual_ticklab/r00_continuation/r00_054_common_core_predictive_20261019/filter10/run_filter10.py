#!/usr/bin/env python3
"""Additive FILTER10: discover common four-month overfit-model consensus vs out-of-month robustness.
Original R00-054 source/models unchanged. No trades, no execution. Diagnostic only.
The four month-fit teachers used on their *own* fit month contaminate the proposed policy.
Out-of-month other teachers may have future calendars (LOMO != forward). Jan-only forward
scores on February / June / July are the chronological reference.
"""
from __future__ import annotations
import ast,zipfile,io,csv,gzip,json,hashlib,os,sys,time,math,warnings
from pathlib import Path
import numpy as np,pandas as pd,joblib
warnings.filterwarnings('ignore',message='X does not have valid feature names')
R=Path('/mnt/data'); OUT=R/'R00_054_FILTER10_CROSS_MONTH_COMMON_CORE';OUT.mkdir(exist_ok=True)
months=['01','02','06','07'];brokers=['coinexx','dukascopy']
BASIC=['bid_only_share_64','ask_only_share_64','joint_update_share_64','one_sided_bias_64','signed_quote_impulse_64','signed_mid_positive_share_64','quote_turn_fraction_64','spread_change_64','spread_range_64','signed_last8_impulse','median_tick_gap_ms_64','last_bid_age_ms','last_ask_age_ms','side_stale_asymmetry','session_utc']
SRC=R/'R00_054_FILTER07_OVERFIT70/run_filter07.py';ns={'np':np,'zipfile':zipfile,'io':io,'R':R,'BASIC':BASIC}
node=next(x for x in ast.parse(SRC.read_text()).body if isinstance(x,ast.FunctionDef) and x.name=='data')
exec(compile(ast.Module(body=[node],type_ignores=[]),str(SRC),'exec'),ns)
data=ns['data']
with gzip.open(R/'R00_054_VALIDATION/continuation_results/R00_054_CONTIGUOUS_UTC_HOURLY.csv.gz','rt',newline='') as f:
    REF={(r['broker'],int(r['hour_key'])):int(r['r9_synth_completed_trades']) for r in csv.DictReader(f)}
FREEZE={'experiment':'FILTER10 month-independent teacher-consensus mechanism transfer diagnostic',
 'sources':'January/February/June/July original R00-054 source quote events, unchanged 93 past-only feature inputs, independent Coinexx/Dukascopy',
 'goal':'identify common mechanism beyond 8 month-specific 70pct apparent fits',
 'orig_model_paths':'FILTER08_FOUR_MONTH_DISCOVERY / per-broker-month .joblib',
 'tested_versions': ['original_base', 'own_fit_teacher', 'other_month_mean','other_month_median','other_month_min','all4_mean','all4_median','all4_min','self80_other20','self50_other50','self20_other80','all4_unanimous'],
 'cutoffs':[0.45,0.50,0.55,0.60,0.65,0.70,0.75,0.80],
 'in_sample_warning':'all4 and self-weighted policies incorporate a same-month label-fitted teacher; only Jan-trained model at Feb/Jun/Jul is chronological as-of-model fit',
 'quota':'>=90pct independent source matched original R9 SYNTH correct-count per UTC hour/day, reject no baseline-passing windows',
 'not_an_EA':True,'not_blind':True,'no_holds_exits_pnl':True}
fp=OUT/'FROZEN_PLAN_BEFORE_ANY_EVALUATION.json'
if not fp.exists():fp.write_text(json.dumps(FREEZE,indent=2)+'\n')
else:assert json.loads(fp.read_text())==FREEZE

CTX=None

def precompute(b,t,y):
    hour=t//3600000;u,inv=np.unique(hour,return_inverse=True)
    ref=np.array([REF.get((b,int(h)),0) for h in u],dtype=np.int64)
    need=np.ceil(ref*.90).astype(np.int64);valid=ref>0
    orig=np.bincount(inv,weights=(y==0).astype(np.int8),minlength=len(u))
    day,di=np.unique(u//24,return_inverse=True)
    dayref=np.bincount(di,weights=ref,minlength=len(day));dayneed=np.ceil(dayref*.90).astype(np.int64);dayvalid=dayref>0
    dayorig=np.bincount(di,weights=orig,minlength=len(day))
    return {'inv':inv,'need':need,'valid':valid,'orig':orig,'di':di,'dayneed':dayneed,'dayvalid':dayvalid,'dayorig':dayorig}

def interval_mask(b,t,y,mask):
    ctx=CTX;good=mask&(y==0)
    found=np.bincount(ctx['inv'],weights=good.astype(np.int8),minlength=len(ctx['need']))
    valid=ctx['valid'];need=ctx['need'];orig=ctx['orig']
    hm=int(np.sum(valid & (orig>=need)&(found<need)));hp=int(np.sum(valid & (found>=need)));total=int(np.sum(valid))
    got=np.bincount(ctx['di'],weights=found,minlength=len(ctx['dayneed']))
    dayvalid=ctx['dayvalid']; dn=ctx['dayneed']; dor=ctx['dayorig']
    dm=int(np.sum(dayvalid & (dor>=dn) & (got<dn)));dp=int(np.sum(dayvalid & (got>=dn)))
    return hm,dm,hp,total,dp,int(dayvalid.sum())

def met(b,m,t,y,name,c,mode):
    keep=np.ones(len(t),bool) if c is None else c
    good=(y==0);v=interval_mask(b,t,y,keep)
    return {'broker':b,'month':m,'mode':mode,'policy':name,'signals':int(keep.sum()),'correct':int((good&keep).sum()),'opposite':int(((y==1)&keep).sum()),'neutral':int(((y==2)&keep).sum()),'accuracy':float((good&keep).sum()/max(1,keep.sum())), 'correct_retained_fraction':float((good&keep).sum()/good.sum()),'incorrect_rejected':int(((y!=0)&~keep).sum()),'extra_r9_hour_misses':v[0],'extra_r9_day_misses':v[1], 'hours_pass':v[2],'hours_total':v[3],'days_pass':v[4],'days_total':v[5]}

rows=[];specific=[]
for b in brokers:
    print('BROKER',b,flush=True)
    mods={}
    for m in months:
        path=R/'R00_054_FILTER08_FOUR_MONTH_DISCOVERY'/f'FIT_SAME_MONTH_{b}_{m}_binary.joblib'
        if m=='06':path=R/'R00_054_FILTER07_OVERFIT70'/f'EXPOSED_TRAIN_JUNE_{b}_binary.joblib'
        mods[m]=joblib.load(path)
    for m in months:
        start=time.time();t,side,y,X,names=data(b,m);assert X.shape[1]==93
        CTX=precompute(b,t,y)
        p=np.column_stack([mods[x].predict_proba(X)[:,1] for x in months]).astype('float32');selfidx=months.index(m)
        others=np.delete(p,selfidx,axis=1)
        scores={
          'own_fit_teacher':p[:,selfidx],
          'other_month_mean':others.mean(axis=1),
          'other_month_median':np.median(others,axis=1),
          'other_month_min':others.min(axis=1),
          'all4_mean':p.mean(axis=1),
          'all4_median':np.median(p,axis=1),
          'all4_min':p.min(axis=1),
          'self80_other20':.80*p[:,selfidx]+.20*others.mean(axis=1),
          'self50_other50':.50*p[:,selfidx]+.50*others.mean(axis=1),
          'self20_other80':.20*p[:,selfidx]+.80*others.mean(axis=1),
          'all4_unanimous':p.min(axis=1)}
        rows.append(met(b,m,t,y,'KEEP_ALL','' if False else None,'baseline'))
        for teacher in months:
            # model diagnostics at universal probability threshold: one teacher per source month, no refitting
            keep=p[:,months.index(teacher)]>=.5
            specific.append(met(b,m,t,y,'model_fit_'+teacher+'_score>=0.50',keep,'per_teacher'))
        for key,prob in scores.items():
            for cut in FREEZE['cutoffs']:
                keep=(prob>=cut)
                rows.append(met(b,m,t,y,key+'_P'+str(cut),keep,'same_month_contaminated' if ('own_fit' in key or 'all4' in key or 'self' in key) else 'other_month_models_historical'))
        np.savez_compressed(OUT/f'ALL_MONTH_TEACHER_SCORES_{b}_{m}.npz',t=t,side=side,truth_class=y,teacher_score=p.astype('float32'),trained_model_months=np.array(months))
        print('EVAL',b,m,len(y),'source right',int((y==0).sum()),'elapsed',round(time.time()-start,1),flush=True)
        pd.DataFrame([x for x in rows if x['broker']==b and x['month']==m]).to_csv(OUT/f'GRID_{b}_{m}.csv',index=False)
        del X,p,t,side,y
pd.DataFrame(rows).to_csv(OUT/'ALL_FOUR_MONTH_ENSEMBLE_RULES.csv',index=False)
pd.DataFrame(specific).to_csv(OUT/'ALL_32_TEACHER_CROSS_MONTH_VALIDATIONS.csv',index=False)
rr=pd.DataFrame(rows);rr['formula']=rr.policy.str.split('_P').str[0]
results=[]
for (formula,cut),g in rr[(rr['mode']!='baseline')].groupby(['formula',rr.policy.str.rsplit('_P',n=1).str[-1]]):
    # one COMMON rule across all 8 source months, common fixed numerical cutoff
    results.append({'formula':formula,'common_cutoff':float(cut),'min_month_accuracy':float(g.accuracy.min()),'total_correct':int(g.correct.sum()),'total_signals':int(g.signals.sum()),'combined_precision':float(g.correct.sum()/max(1,g.signals.sum())),'total_incorrect_rejected':int(g.incorrect_rejected.sum()),'hours_lost':int(g.extra_r9_hour_misses.sum()),'days_lost':int(g.extra_r9_day_misses.sum()),'all_months_70':bool((g.accuracy>=.70).all()),'all_hours_days_pass':bool((g.extra_r9_hour_misses==0).all() and (g.extra_r9_day_misses==0).all())})
res=pd.DataFrame(results).sort_values(['all_months_70','all_hours_days_pass','min_month_accuracy','total_correct'],ascending=[False,False,False,False]);res.to_csv(OUT/'COMMON_RULES_GLOBAL_NO_MONTH_TUNING.csv',index=False)
# Feature stability is an exact 8-way intersection, not merely averaged ranking.
f=pd.read_csv(R/'R00_054_FILTER08_FOUR_MONTH_DISCOVERY/FINE_GRAINED_FEATURE_FACETS_PER_MODEL.csv')
g=f.groupby(['feature','group']).agg(mean_gain_fraction=('model_fit_gain_fraction','mean'),minimum_gain_fraction=('model_fit_gain_fraction','min'),max_rank=('original_in_sample_rank','max'),all_top20=('original_in_sample_rank',lambda z:bool((z<=20).all())),eight_models=('original_in_sample_rank','size')).reset_index();g.sort_values(['all_top20','minimum_gain_fraction'],ascending=False).to_csv(OUT/'STABLE_FEATURE_INTERSECTION.csv',index=False)
# fixed summary excludes side-affecting contaminated rules from predictive claims
for name,col in [('GLOBAL_TOP',res.head(10)),('FORWARD_JAN_TEACHER',pd.DataFrame(specific).query("policy=='model_fit_01_score>=0.50'"))]:
    (OUT/(name+'.json')).write_text(col.to_json(orient='records',indent=2))
print('GLOBAL_TOP_10',res.head(10).to_json(orient='records'),flush=True)
print('COMPLETE',time.time(),flush=True)

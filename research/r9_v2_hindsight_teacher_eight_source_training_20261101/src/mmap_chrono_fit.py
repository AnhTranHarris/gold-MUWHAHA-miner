#!/usr/bin/env python3
"""Memory-bounded, source-specific chronological NP/Hawkes student.
No future labels/teacher marks enter runtime X; teacher weighting only in fit.
Evaluations use frozen input rows and are candidate-filter studies, NOT
regenerated filtered trade opportunity streams.
"""
from __future__ import annotations
import argparse,json,time,math,hashlib,os
from pathlib import Path
import numpy as np,lightgbm as lgb
ROOT=Path('/mnt/data/r9_v2_eight_source_training_20261101')
MON=('01','02','06','07');DATES={'01':(20260112,20260119),'02':(20260211,20260218),'06':(20260610,20260617),'07':(20260710,20260717)}
SYNTH={'01':27980,'02':33523,'06':31801,'07':24382}

def load(src,mon,k):return np.load(ROOT/'checkpoints'/f'{src}_{mon}_{k}.npy',mmap_mode='r')

def metric(arr,nmask,source,mon,phase):
    y=arr['win'];net=arr['net'];dates=arr['date'];weeks=arr['week']
    sel=np.asarray(nmask,dtype=bool);ct=int(sel.sum());wins=int(y[sel].sum());pn=float(np.sum(net[sel],dtype=np.float64))
    all_d=np.unique(dates);all_w=np.unique(weeks)
    daily={};weekly={}
    for name,uni,key,storage in [('daily',all_d,dates,daily),('weekly',all_w,weeks,weekly)]:
        for val in uni:
            ix=sel&(key==val);n=int(ix.sum());positive=int(y[ix].sum())
            storage[str(int(val))]={'trades':n,'good30':positive,'survival30_rate':round(positive/n,5) if n else None,'pass':bool(n>0 and positive/n>=.8),'net':round(float(np.sum(net[ix],dtype=np.float64)),2)}
    return {'source':source,'month':mon,'phase':phase,'candidate_count':len(y),'selected':ct,'win30':wins,
       'win30_rate':round(wins/ct,5) if ct else None,'net':round(pn,2),'monthly_survival_pass':bool(ct>0 and wins/ct>=.8),
       'daily_pass_count':sum(v['pass'] for v in daily.values()),'daily_total':len(daily),
       'weekly_pass_count':sum(v['pass'] for v in weekly.values()),'weekly_total':len(weekly),
       'monthly_volume_floor':int(math.ceil(.85*SYNTH[mon])),
       'full_month_volume_pass':bool(phase=='full_month' and ct>=math.ceil(.85*SYNTH[mon])),
       'byday':daily,'byweek':weekly}

def assemble(src,mon):
    trainX=[];trainY=[];trainW=[]
    for m in MON:
        if int(m)>int(mon):break
        dat=load(src,m,'date');allowed=dat<=DATES[m][0] if m==mon else np.full(len(dat),True)
        # Purge 30s overlap before fit cutoff (never train outcome crossing calibration).
        if m==mon:
            ts=load(src,m,'ts');boundary=int(str(DATES[m][0])) # eod cut preserved by day
            # Purge near next UTC midnight: >=23:59:30 of fit cutoff
            import datetime as dt
            limit=int(dt.datetime.strptime(str(boundary),'%Y%m%d').replace(tzinfo=dt.timezone.utc).timestamp()*1000)+86370000
            allowed &= (ts<limit)
        if not allowed.any():continue
        X=load(src,m,'X');Y=load(src,m,'win');T=load(src,m,'teacher')
        trainX.append(np.asarray(X[allowed],dtype=np.float32));trainY.append(np.asarray(Y[allowed],dtype=np.uint8))
        weights=np.ones(len(trainY[-1]),np.float32);weights[(trainY[-1]>0)&(T[allowed]>0)]=1.05
        trainW.append(weights)
    return np.concatenate(trainX,axis=0),np.concatenate(trainY),np.concatenate(trainW)

def study(src,mon):
    start=time.monotonic();out=ROOT/'results';out.mkdir(exist_ok=True)
    X,Y,W=assemble(src,mon)
    model=lgb.train({'objective':'binary','metric':'binary_logloss','num_leaves':27,'max_depth':7,'learning_rate':.055,
       'min_data_in_leaf':180,'feature_fraction':.82,'lambda_l2':10.,'num_threads':4,
       'verbosity':-1,'seed':20261101,'deterministic':True,'force_col_wise':True},
       lgb.Dataset(X,label=Y,weight=W,free_raw_data=True),num_boost_round=105)
    del X,Y,W
    meta=json.loads((ROOT/'checkpoints'/f'{src}_{mon}_mmap.json').read_text())
    names=meta['features'];model.save_model(str(ROOT/'checkpoints'/f'{src}_{mon}_chrono_fitted.txt'))
    X=load(src,mon,'X');d=load(src,mon,'date');y=load(src,mon,'win');net=load(src,mon,'net');week=load(src,mon,'week')
    ca,cb=DATES[mon]
    cal=(d>ca)&(d<=cb);check=(d>cb)
    # Thresholds optimize only on calibration days, never on future check days.
    pcal=model.predict(np.asarray(X[cal],np.float32),num_threads=4)
    bad=pcal[np.asarray(y[cal]==0)]
    variants=[]
    for q in (.50,.70,.80,.90,.95,.975,.99,.995,.999):
        th=float(np.quantile(bad,q))
        ix=(pcal>th);sel_y=np.asarray(y[cal])[ix];sel_net=np.asarray(net[cal])[ix]
        n=len(sel_y);w=int(sel_y.sum());win=w/n if n else 0.;pnl=float(np.sum(sel_net,dtype=np.float64))
        variants.append({'np_bad_rejection_q':q,'threshold':th,'n':n,'win30':win,'net':round(pnl,2),
        'meets80':bool(n>0 and win>=.8),'positive_expectancy':bool(n>0 and pnl>0)})
    eligible=[v for v in variants if v['meets80'] and v['positive_expectancy']]
    if eligible:chosen=max(eligible,key=lambda x:x['n'])
    else: chosen=max(variants,key=lambda x:(x['net'],x['win30']))
    print(src,mon,'fit',len(model.feature_importance()),'cal_n',sum(cal),'choice',chosen,flush=True)
    p=model.predict(np.asarray(X[check],np.float32),num_threads=4)
    selected=(p>chosen['threshold'])
    a={k:np.asarray(load(src,mon,k)[check]) for k in ('win','net','date','week')}
    eval_result=metric(a,selected,src,mon,'chronological_check')
    res={'model':'LightGBM bidask-asof event posterior + NP quantile + weak synthetic teacher weight','source':src,'month':mon,
      'train_rows':sum(load(src,m,'date').shape[0] for m in MON if int(m)<int(mon))+int((d<=ca).sum()),
      'test_days':sorted(np.unique(d[check]).tolist()),'source_month_universe':len(d),
      'feature_names':names,'num_features':len(names),'teacher_runtime_feature':False,'teacher_weight':.05,
      'NP_variants':variants,'chosen_on_cal_only':chosen,'evaluation':eval_result,
      'elapsed_sec':round(time.monotonic()-start,2),
      'warning':'Selected baseline-entry subset only; rejected baseline positions do not create new tick decisions.'}
    (out/f'{src}_{mon}_chronological.json').write_text(json.dumps(res,indent=2))
    print('RESULT',src,mon,'selected',eval_result['selected'],'survival',eval_result['win30_rate'],'pnl',eval_result['net'],'days',eval_result['daily_pass_count'],'/',eval_result['daily_total'],flush=True)
    return res
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--month',required=True);a=p.parse_args();study(a.source,a.month)

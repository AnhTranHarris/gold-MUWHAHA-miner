#!/usr/bin/env python3
"""R00-054 A01: source-event, causal F44-score meta-specialist.

Research only. F44 frozen Jan-trained predictions are inputs; never use the
FILTER08 same-month fitted teacher score or current/future truth at decision.
No original tick engine rebuilt, no production order veto, no blind claim.
"""
from __future__ import annotations
import argparse, hashlib, io, json, pickle, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

HEADS=('OOF_good','OOF_opp_guard','OOF_neutral_guard')
BROKERS=('coinexx','dukascopy')
QMS=33001  # Original t0+30..32s label cannot mature before this bound.

def sha_bytes(data: bytes)->str:return hashlib.sha256(data).hexdigest()

def read_npz(z:zipfile.ZipFile, broker:str, month:str):
    raw=z.read(f'F44/F44_PREDICTIONS_{broker}_{month}.npz')
    with np.load(io.BytesIO(raw)) as n:
        a={k:n[k].copy() for k in n.files}
    assert np.all(np.diff(a['t'])>=0), 'source event clock unsorted'
    assert set(np.unique(a['truth'])) <= {0,1,2}
    assert set(np.unique(a['side'])) <= {-1,1}
    return a,sha_bytes(raw)

def _past_mean(t:np.ndarray, x:np.ndarray, window_ms:int):
    # For event i, only j < i can affect rolling state.
    idx=np.searchsorted(t,t,side='left')  # Exclude all same-ms events: native ordinal not in F44 cache.
    start=np.searchsorted(t,t-window_ms,side='left')
    cs=np.vstack((np.zeros((1,x.shape[1]),dtype=np.float64),np.cumsum(x,dtype=np.float64,axis=0)))
    counts=idx-start
    means=(cs[idx]-cs[start])/np.maximum(1,counts)[:,None]
    return means,counts

def _matured_rates(t:np.ndarray,side:np.ndarray,truth:np.ndarray,window_ms:int):
    # Prior truth is available ONLY if its entire original label window has matured.
    rates=np.full((len(t),3),1/3,dtype=np.float64)
    counts=np.zeros(len(t),dtype=np.float64)
    for s in (-1,1):
        pos=np.flatnonzero(side==s)
        ts=t[pos]
        label=truth[pos]
        hi=np.searchsorted(ts,ts-QMS,side='right')
        lo=np.searchsorted(ts,ts-QMS-window_ms,side='left')
        count=hi-lo
        counts[pos]=count
        for c in range(3):
            cum=np.r_[0,np.cumsum(label==c,dtype=np.int64)]
            rates[pos,c]=(cum[hi]-cum[lo]+3)/(count+9)
    return rates,counts

def features(a:dict):
    t=a['t'].astype(np.int64)
    side=a['side'].astype(np.int8)
    truth=a['truth'].astype(np.int8)
    x=np.column_stack([a[k] for k in HEADS]).astype(np.float64)
    short,nshort=_past_mean(t,x,120_000)
    long,nlong=_past_mean(t,x,1_800_000)
    prior10,c10=_matured_rates(t,side,truth,600_000)
    prior60,c60=_matured_rates(t,side,truth,3_600_000)
    dt=pd.to_datetime(t,unit='ms',utc=True)
    hour=np.asarray(dt.hour)+np.asarray(dt.minute)/60
    session=np.floor(hour/8).astype(np.int8)
    sessions=np.eye(3,dtype=np.float64)[session]
    s=side.astype(np.float64)[:,None]
    # 3 independent Jan-trained class heads; causal past-score changes and
    # previous fully matured outcomes, with broker-specific fitted coefficients.
    f=[x,s,np.sin(2*np.pi*hour/24)[:,None],np.cos(2*np.pi*hour/24)[:,None],
       sessions,x*s,x[:, :, None].__mul__(sessions[:,None,:]).reshape(len(t),-1),
       short,long,x-short,short-long,np.abs(short-long),
       np.log1p(nshort)[:,None],np.log1p(nlong)[:,None],
       prior10,prior60,prior10-prior60,
       np.log1p(c10)[:,None],np.log1p(c60)[:,None],
       (1-x[:,1:2])*prior10[:,1:2],(1-x[:,2:3])*prior10[:,2:3]]
    out=np.column_stack(f).astype(np.float32)
    assert np.isfinite(out).all()
    return out

def split(n:int):
    # Feb first60 FIT, next20 CAL, final20 VALIDATION.
    return np.arange(n)<int(.6*n), (np.arange(n)>=int(.6*n))&(np.arange(n)<int(.8*n)),np.arange(n)>=int(.8*n)

def count(a,keep):
    y=a['truth'];g=y==0;b=y!=0
    return dict(n=len(y),correct_total=int(g.sum()),incorrect_total=int(b.sum()),
       correct_kept=int((g&keep).sum()),incorrect_rejected=int((b&~keep).sum()),
       opposite_rejected=int(((y==1)&~keep).sum()),neutral_rejected=int(((y==2)&~keep).sum()),
       correct_retention=float(keep[g].mean()),incorrect_rejection=float((~keep[b]).mean()),
       precision=float(g[keep].mean()) if keep.any() else None)

def quota_check(a,keep,broker,month,quota,levels=('hour','day','month')):
    # Compare all source-reference rows, including eligible uncovered hours.
    t=pd.to_datetime(a['t'],unit='ms',utc=True)
    y=a['truth']; good=keep&(y==0)
    periods={'hour':t.strftime('%Y-%m-%dT%H:00:00+00:00'),
             'day':t.strftime('%Y-%m-%d'),
             'month':t.strftime('%Y-%m')}
    report={}
    for level in levels:
        ref=quota[(quota.broker==broker)&(quota.level==level)&(quota.utc_key.str.startswith(f'2026-{month}'))]
        got=pd.Series(good.astype(np.int8)).groupby(periods[level]).sum()
        measured=ref.utc_key.map(got).fillna(0).astype(int).to_numpy()
        fail=(measured<ref.required_correct_90pct.to_numpy())&(ref.r9_reference.to_numpy()>0)
        report[level]={'reference_rows':int(len(ref)), 'eligible_rows':int((ref.r9_reference>0).sum()),
                       'failed_rows':int(fail.sum()),'min_correct_surplus':int((measured-ref.required_correct_90pct.to_numpy()).min()) if len(ref) else None,
                       'first_failures':ref.loc[fail,['utc_key','r9_reference','required_correct_90pct']].head(5).to_dict('records')}
    return report

def load_quota(z):
    return pd.read_csv(io.BytesIO(z.read('FILTER08/FOUR_MONTH_HOUR_DAY_WEEK_MONTH_R9_QUOTAS.csv')),
                       dtype={'utc_key':str})

def train(f44,original,out):
    with zipfile.ZipFile(f44) as z,zipfile.ZipFile(original) as rz:
        q=load_quota(rz)
        records={};models={};freeze={}
        for b in BROKERS:
            a,h=read_npz(z,b,'02');X=features(a);fit,cal,val=split(len(a['t']))
            sc=StandardScaler();Z=sc.fit_transform(X[fit]);
            mdl=LogisticRegression(C=0.10,max_iter=150,solver='lbfgs',random_state=5401)
            mdl.fit(Z,a['truth'][fit]);
            p=mdl.predict_proba(sc.transform(X))[:,int(np.where(mdl.classes_==0)[0][0])]
            # One predeclared q=0.22 of Feb middle20 correct-class CAL scores.
            cut=float(np.quantile(p[cal&(a['truth']==0)],0.22))
            freeze[b]=dict(threshold=cut,cal_quantile_correct=0.22,fit_n=int(fit.sum()),cal_n=int(cal.sum()),val_n=int(val.sum()),
                model='multinomial L2 C=.10',train_window='February first60%',cal_window='February middle20%',
                frozen_before='February last20% and all June/July',input_head_source='F44 Jan-fitted OOF score archive',
                score_archive_sha256=h,feature_dimension=int(X.shape[1]))
            models[b]=(sc,mdl)
            base_cut=json.loads(z.read('F44/F44_FEB_FROZEN_POLICIES.json'))['OOF_min_err']['threshold']
            report={}
            for k,mask in [('FIT',fit),('CAL',cal),('VAL',val),('FULL_FEB',np.ones(len(a['t']),dtype=bool))]:
                aa={key:value[mask] for key,value in a.items()}
                keep=p[mask]>=cut
                base=a['OOF_min_err'][mask]>=base_cut
                report[k]={'candidate':count(aa,keep),'f44_original_frozen_min_err':count(aa,base)}
            report['FULL_FEB']['candidate_quota']=quota_check(a,p>=cut,b,'02',q)
            report['FULL_FEB']['baseline_quota']=quota_check(a,a['OOF_min_err']>=base_cut,b,'02',q)
            records[b]=report
        with (out/'frozen_models.pkl').open('wb') as f:pickle.dump(models,f,protocol=4)
        (out/'frozen_thresholds.json').write_text(json.dumps(freeze,indent=2)+'\n')
        (out/'feb_chronological_controls.json').write_text(json.dumps(records,indent=2)+'\n')
        print('FIT_FREEZE',json.dumps({b:records[b]['VAL']['candidate'] for b in BROKERS}))

def transfer(f44,original,out):
    with (out/'frozen_models.pkl').open('rb') as f:models=pickle.load(f)
    freeze=json.loads((out/'frozen_thresholds.json').read_text())
    with zipfile.ZipFile(f44) as z,zipfile.ZipFile(original) as rz:
        q=load_quota(rz)
        base_cut=json.loads(z.read('F44/F44_FEB_FROZEN_POLICIES.json'))['OOF_min_err']['threshold']
        reports={};data={}
        for b in BROKERS:
            sc,mdl=models[b];cut=freeze[b]['threshold']
            for m in ('06','07'):
                a,h=read_npz(z,b,m);X=features(a)
                p=mdl.predict_proba(sc.transform(X))[:,int(np.where(mdl.classes_==0)[0][0])]
                keep=p>=cut;base=a['OOF_min_err']>=base_cut
                key=f'{b}_{m}'
                reports[key]={'candidate':count(a,keep),'baseline_f44':count(a,base),
                              'candidate_quota':quota_check(a,keep,b,m,q),
                              'baseline_quota':quota_check(a,base,b,m,q),
                              'f44_source_npz_sha256':h,
                              'mask_sha256':sha_bytes(np.packbits(keep.astype(np.uint8),bitorder='little').tobytes()),
                              'event_time_sha256':sha_bytes(a['t'].tobytes()),
                              'event_side_sha256':sha_bytes(a['side'].tobytes())}
                data[key]=(a,keep)
                np.savez_compressed(out/f'frozen_mask_{key}.npz',t=a['t'],side=a['side'],keep=keep,truth=a['truth'])
        # June/July ISO week quotas computed over BOTH months (not partial month).
        for b in BROKERS:
            aa=[data[f'{b}_{m}'][0] for m in ('06','07')]
            kk=[data[f'{b}_{m}'][1] for m in ('06','07')]
            t=np.concatenate([x['t'] for x in aa]);y=np.concatenate([x['truth'] for x in aa]);keep=np.concatenate(kk)
            iso=pd.to_datetime(t,unit='ms',utc=True).strftime('%G-W%V')
            got=pd.Series(((y==0)&keep).astype(np.int8)).groupby(iso).sum()
            refs=q[(q.broker==b)&(q.level=='iso_week')&(q.utc_key.isin(np.unique(iso)))]
            actual=refs.utc_key.map(got).fillna(0).astype(int).to_numpy()
            fails=(actual<refs.required_correct_90pct.to_numpy())&(refs.r9_reference.to_numpy()>0)
            reports[f'{b}_06_07_ISO_WEEK']={'eligible_rows':int((refs.r9_reference>0).sum()),'failed_rows':int(fails.sum()),'reference_rows':int(len(refs))}
        (out/'june_july_frozen_transfer.json').write_text(json.dumps(reports,indent=2)+'\n')
        print('TRANSFER',json.dumps({k:v['candidate'] for k,v in reports.items() if k.endswith('_06') or k.endswith('_07')}))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['fit','transfer']);ap.add_argument('--f44',required=True,type=Path);ap.add_argument('--original',required=True,type=Path);ap.add_argument('--out',required=True,type=Path)
    x=ap.parse_args();x.out.mkdir(parents=True,exist_ok=True)
    (train if x.phase=='fit' else transfer)(x.f44,x.original,x.out)
if __name__=='__main__':main()

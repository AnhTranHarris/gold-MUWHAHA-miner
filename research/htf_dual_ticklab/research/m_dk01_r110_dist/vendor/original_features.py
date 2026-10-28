"""R00-ENTRY-054 native price-tape event features, source-pinned and strictly causal.
Derived from original approved raw XAUUSD bid/ask CSV.GZ, never a synthetic broker tape.
January/February: first quote in populated 5s epoch; June/July: archived R00-040
candidate timestamps where exact raw source quote identity is verified.
No alternative market-data source. Labels are for post-event scoring ONLY.
"""
import argparse, gc, gzip, hashlib, json, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit
ROOT=Path(__file__).resolve().parent
DATA=ROOT.parent
ARCH=DATA/'r00_resume'/'R00_ENTRY_050_PHASE_CLOCK'
PINS={
('dukascopy','01'):'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
('dukascopy','02'):'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d',
('dukascopy','06'):'34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2',
('dukascopy','07'):'e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7',
('coinexx','01'):'1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8',
('coinexx','02'):'5de772aab4d15ebf18aa48850e847c98e2bcb639064790bbed9d87a598c3bf05',
('coinexx','06'):'3033ccb257d067aecc123f3791d9dddc5c95841b9bba167ff1ca0cf1589dc2b4',
('coinexx','07'):'d9d47d40abb33935414edfb5c11f0c518d8c9cc27221da182dab0bc49b0b708d'
}
@njit(cache=True)
def firstpass(t,bid,ask,ev_idx,target,stop,horizon_ms):
    n=len(ev_idx);out=np.zeros((n,2),dtype=np.int8);age=np.full((n,2),-1,dtype=np.int32)
    for j in range(n):
        i=ev_idx[j];lastt=t[i]+horizon_ms
        el=ask[i];es=bid[i];hitL=0;hitS=0
        k=i+1
        while k<len(t) and t[k]<=lastt and (hitL==0 or hitS==0):
            if hitL==0:
                if bid[k]>=el+target:hitL=1;age[j,0]=int(t[k]-t[i])
                elif bid[k]<=bid[i]-stop:hitL=-1;age[j,0]=int(t[k]-t[i])
            if hitS==0:
                if ask[k]<=es-target:hitS=1;age[j,1]=int(t[k]-t[i])
                elif ask[k]>=ask[i]+stop:hitS=-1;age[j,1]=int(t[k]-t[i])
            k+=1
        out[j,0]=hitL;out[j,1]=hitS
    return out,age

@njit(cache=True)
def independent_experts(tt,features):
    # index features: [r1,r3,r5,r10,r30,r60,r300,r900,r3600,eff5,eff10,eff30,rate5,rate10,...]
    n=len(tt);e=np.zeros((4,n),np.int8)
    pending=np.zeros(4,np.int8);start=np.full(4,-1,np.int64);cool=np.full(4,-100000,np.int64)
    for i in range(n):
        t=tt[i];r1,r3,r5,r10,r30=features[i,0],features[i,1],features[i,2],features[i,3],features[i,4]
        m5body=features[i,31];m15body=features[i,34];h1body=features[i,37]
        eff5=features[i,9];eff10=features[i,10];spr=features[i,14]
        mk=np.zeros(4,np.int8)
        if abs(r10)>.12 and abs(r3)>.028 and r10*r3>0 and eff10>.22:
            mk[0]=1 if r10>0 else -1
        if abs(r10)>.12 and abs(r3)>.028 and r10*r3<0 and eff5>.16:
            mk[1]=1 if r3>0 else -1
        if abs(r30)>.2 and abs(r3)>.04 and r30*r3<0 and abs(m15body)>.15:
            mk[2]=1 if r3>0 else -1
        if abs(m15body)>.25 and abs(h1body)>.6 and m15body*h1body>0 and r10*m15body<0 and abs(r3)>.02:
            mk[3]=1 if m15body>0 else -1
        for k in range(4):
            if pending[k]!=0:
                age=t-start[k]
                if age>15000:pending[k]=0;cool[k]=t
                elif age>=5000:
                    s=pending[k]
                    
                    if k==0: match=(r3*s>.005)
                    elif k==1: match=(r3*s>.005 and r10*s<.15)
                    elif k==2: match=(r3*s>.005 and abs(r30)>.05)
                    else: match=(r3*s>.0 and m15body*s>0)
                    if match:
                        e[k,i]=s;pending[k]=0;cool[k]=t
            if pending[k]==0 and e[k,i]==0 and mk[k]!=0 and t-cool[k]>5000 and spr<1.5:
                pending[k]=mk[k];start[k]=t
    return e

def price_bars(tm, mid, width, event_t):
    bucket=tm//width
    starts=np.r_[0,np.flatnonzero(bucket[1:]!=bucket[:-1])+1]
    ends=np.r_[starts[1:],len(tm)]
    keys=bucket[starts]
    highs=np.maximum.reduceat(mid,starts);lows=np.minimum.reduceat(mid,starts)
    op=mid[starts];cl=mid[ends-1]
    # completed bar index exactly previous bucket (not previous observed if missing)
    idx=np.searchsorted(keys,event_t//width-1)
    good=(idx<len(keys))
    matched=np.zeros(len(idx),bool);matched[good]=keys[idx[good]]==event_t[good]//width-1
    safe=np.clip(idx,0,len(keys)-1)
    features=np.column_stack((cl[safe]-op[safe], highs[safe]-lows[safe], cl[safe]-lows[safe], highs[safe]-cl[safe])).astype('float32')
    features[~matched]=np.nan
    return features

def raw_features(tm,mid,bid,ask,event_idx):
    te=tm[event_idx];p=mid[event_idx]
    cols=[];names=[]
    for sec in [1,3,5,10,30,60,300,900,3600]:
        prev=np.searchsorted(tm,te-sec*1000,side='right')-1
        age=np.where(prev>=0,te-sec*1000 - tm[np.maximum(prev,0)],999999)
        r=np.full(len(te),np.nan,'float32')
        valid=(prev>=0)&(age<=max(2000, min(sec*1000//3, 60000)))
        r[valid]=(p[valid]-mid[prev[valid]]).astype('float32')
        cols.append(r);names.append(f'ret_{sec}s')
    dif=np.diff(mid).astype('float32')
    path=np.r_[0,np.cumsum(np.abs(dif),dtype=np.float64)]
    ups=np.r_[0,np.cumsum(dif>0,dtype=np.int64)]
    dns=np.r_[0,np.cumsum(dif<0,dtype=np.int64)]
    for sec in (5,10,30):
        prev=np.searchsorted(tm,te-sec*1000,side='right')-1
        prev=np.maximum(prev,0)
        den=path[event_idx]-path[prev]
        net=np.abs(p-mid[prev])
        eff=(net/np.maximum(den,.0001)).astype('float32')
        cols.append(eff);names.append(f'eff_{sec}s')
    for sec in (5,10):
        prev=np.searchsorted(tm,te-sec*1000,side='right')-1;prev=np.maximum(prev,0)
        rate=((event_idx-prev)/sec).astype('float32')
        cols.append(rate);names.append(f'quote_rate_{sec}s')
    spread=(ask[event_idx]-bid[event_idx]).astype('float32')
    cols.append(spread);names.append('spread')
    for sec in (1,10,30):
        prev=np.searchsorted(tm,te-sec*1000,side='right')-1;prev=np.maximum(prev,0)
        bu=(ups[event_idx]-ups[prev]);be=(dns[event_idx]-dns[prev]);
        imbalance=((bu-be)/np.maximum(bu+be,1)).astype('float32')
        cols.append(imbalance);names.append(f'tick_sign_imbalance_{sec}s')
    for sec in (5,10,30):
        prev=np.searchsorted(tm,te-sec*1000,side='right')-1;prev=np.maximum(prev,0)
        var=((path[event_idx]-path[prev])/sec).astype('float32')
        cols.append(var);names.append(f'path_volatility_{sec}s')
    # four completed time frames; index 23,27,31,35. Raw expert indices below aligned by constants.
    for width,name in [(60000,'M1'),(300000,'M5'),(900000,'M15'),(3600000,'H1')]:
        data=price_bars(tm,mid,width,te)
        for i,n in enumerate(('body','range','close_low','high_close')):
            cols.append(data[:,i]);names.append(name+'_'+n)
    # periodic clock features are known at actual tick time
    day=(te//86400000)%7;hour=(te//3600000)%24;secs=(te//1000)%60
    for arr,name in [(np.sin(hour*2*np.pi/24),'sin_hour'),(np.cos(hour*2*np.pi/24),'cos_hour'),(np.sin(secs*2*np.pi/60),'sin_sec'),(np.cos(secs*2*np.pi/60),'cos_sec'),(day,'weekday'),(np.log1p(np.maximum(cols[12],0)),'log_quote_rate')]:
        cols.append(np.asarray(arr,dtype=np.float32));names.append(name)
    X=np.column_stack(cols).astype('float32')
    return X,names

def run(br,mo):
    stem=f'XAUUSD_DUKAS_2026_{mo}_ticks.csv.gz' if br=='dukascopy' else f'XAUUSD_MT5_BROKER_2026_{mo}_ticks_ALL.csv.gz'
    file=DATA/stem;start=time.time()
    got=hashlib.file_digest(open(file,'rb'),'sha256').hexdigest()
    assert got==PINS[(br,mo)],f'UNAUTHORIZED_SOURCE sha mismatch {stem}'
    if br=='dukascopy':
        frame=pd.read_csv(file,compression='gzip',dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'},usecols=['timestamp_ms_utc','ask_raw','bid_raw'])
        ts=frame['timestamp_ms_utc'].to_numpy();ask=frame['ask_raw'].to_numpy().astype(np.float64)/1000.;bid=frame['bid_raw'].to_numpy().astype(np.float64)/1000.
    else:
        frame=pd.read_csv(file,compression='gzip',dtype={'time_msc':'int64','bid':'float64','ask':'float64'},usecols=['time_msc','bid','ask'])
        ts=frame['time_msc'].to_numpy()- (120 if mo in ('01','02') else 180)*60000
        bid=frame['bid'].to_numpy();ask=frame['ask'].to_numpy()
    del frame;gc.collect()
    assert (np.diff(ts)>=0).all() and (ask>=bid).all() and (bid>0).all()
    mid=(bid+ask)/2
    if mo in ('06','07'):
        orig=np.load(ARCH/f'ORIGINAL_CONFIRMATIONS_{br}_{mo}.npz')
        te=orig['t'];idx=np.searchsorted(ts,te,side='left')
        assert idx.max()<len(ts) and np.array_equal(ts[idx],te),'Original archived event timestamp did not resolve to ORIGINAL raw tick'
        # Archived event x/y stay intact; verify labels with raw re-derivation below.
        archived={k:orig[k] for k in orig.files}
    else:
        keys=ts//5000;idx=np.r_[0,np.flatnonzero(keys[1:]!=keys[:-1])+1]
        archived={}
    te=ts[idx];X,names=raw_features(ts,mid,bid,ask,idx)
    # caution previous-month close unavailable; nulls explicit; no imputation using future sample.
    delp=te+30000;j=np.searchsorted(ts,delp,side='left')
    has=j<len(ts);js=np.clip(j,0,len(ts)-1);valid=has & ((ts[js]-delp)<2000)
    d30=np.full(len(idx),np.nan,'float64');d30[valid]=mid[js[valid]]-mid[idx[valid]]
    d10=np.full(len(idx),np.nan,'float64');t10=te+10000;k=np.searchsorted(ts,t10,side='left');good=k<len(ts);ks=np.clip(k,0,len(ts)-1);v=good & ((ts[ks]-t10)<2000);d10[v]=mid[ks[v]]-mid[idx[v]]
    if archived:
        a=archived['d30'];match=np.isfinite(a)&np.isfinite(d30)
        delta=np.abs(d30[match]-a[match])
        print('ARCHIVE_D30_CHECK',br,mo,'match',match.sum(),'exact_close',int((delta<0.0002).sum()),'max_delta',float(delta.max()) if len(delta) else -1,flush=True)
        assert len(a)==len(idx) and (delta<.0003).mean()>.999,'Archived fixed 30sec score inconsistent with source native ticks'
    fp,ages=firstpass(ts,bid,ask,idx,.30,.45,30000)
    # independent lifecycle experts: explicit time-pending/expiry, no future data in decisions
    # correct index mapping expected: 0-8 ret; 9-11 eff; 12-13 rate; 14 spread; 15-17 imbalance; 18-20 path; 21-24 M1;25-28 M5;29-32 M15;33-36 H1.
    # fix numeric indexing via names dynamically; expert side uses specific compact reordered view
    sub=np.zeros((len(idx),38),'float32');sub[:,:min(19,X.shape[1])]=np.nan_to_num(X[:,:min(19,X.shape[1])])
    sub[:,31]=np.nan_to_num(X[:,names.index('M5_body')]);sub[:,34]=np.nan_to_num(X[:,names.index('M15_body')]);sub[:,37]=np.nan_to_num(X[:,names.index('H1_body')]);
    experts=independent_experts(te,sub)
    meta={'broker':br,'month':mo,'source':stem,'source_sha256':got,'input_raw_ticks':len(ts),'event_ticks':len(te),'event_t_first':int(te[0]),'event_t_last':int(te[-1]),'missing_d30':int((~np.isfinite(d30)).sum()),'features':names,'archive_verified':bool(archived),'archive_score_consistency':'MATCHED' if archived else 'not_applicable','elapsed_sec':round(time.time()-start,2)}
    p=ROOT/'cache'/f'native_{br}_{mo}.npz'
    kw=dict(t=te,features=X,d30=d30,d10=d10,firstpass=fp,firstpass_age=ages,experts=experts)
    if archived:kw.update(archived_control=archived['control_side'],archived_050=archived['side'],archived_experts=archived['specialists'])
    np.savez_compressed(p,**kw)
    (ROOT/'results'/f'native_{br}_{mo}_receipt.json').write_text(json.dumps(meta,indent=2))
    print('BUILT',br,mo,'raw_ticks',len(ts),'5s_events',len(te),'cache_MB',round(p.stat().st_size/1e6,2),'sec',meta['elapsed_sec'],flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('broker',choices=['coinexx','dukascopy']);ap.add_argument('month',choices=['01','02','06','07']);ar=ap.parse_args();run(ar.broker,ar.month)

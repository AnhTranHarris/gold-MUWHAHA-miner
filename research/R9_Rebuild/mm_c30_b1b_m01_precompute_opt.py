import json, time, hashlib
from pathlib import Path
import numpy as np
import pandas as pd

RAW=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
OUT=Path('/mnt/data/MM_C30_B1B_M01_PRECOMPUTE_OPT'); OUT.mkdir(exist_ok=True)
CACHE=OUT/'MM_C30_B1B_M01_CAUSAL_CACHE.npz'
RESULT=OUT/'MM_C30_B1B_M01_PRECOMPUTE_RESULT.json'


def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20), b''): h.update(b)
    return h.hexdigest()


def active_seconds(t, mid):
    sec=t//1000
    change=np.empty(len(sec), dtype=np.bool_)
    change[0]=True; change[1:]=sec[1:]!=sec[:-1]
    idx=np.flatnonzero(change)
    ids=sec[idx]
    last=np.r_[idx[1:]-1, len(sec)-1]
    cnt=(last-idx+1).astype(np.int32)
    o=mid[idx]; c=mid[last]
    h=np.maximum.reduceat(mid, idx)
    l=np.minimum.reduceat(mid, idx)
    return ids.astype(np.int64), o, h, l, c, cnt


def s1_features(h,l,c):
    N=len(c)
    disp=np.full(N,np.nan,np.float64)
    eff=np.full(N,np.nan,np.float64)
    rng=np.full(N,np.nan,np.float64)
    turns=np.full(N,99.0,np.float64)
    if N<10: return disp,eff,rng,turns
    dc=np.diff(c)
    absdc=np.abs(dc)
    cs=np.r_[0.0,np.cumsum(absdc)]
    i=np.arange(9,N)
    # window c[i-9:i+1] has 9 diffs: dc[i-9:i]
    travel=cs[i]-cs[i-9]
    disp[i]=c[i]-c[i-9]
    eff[i]=np.abs(disp[i])/(travel+1e-12)
    hs=pd.Series(h).rolling(10,min_periods=10).max().to_numpy()
    ls=pd.Series(l).rolling(10,min_periods=10).min().to_numpy()
    rng[i]=hs[i]-ls[i]
    s=np.sign(dc).astype(np.int8)
    # original loop removes zero moves before counting sign changes; zeros are rare but preserve semantics exactly via tiny rolling loop on active seconds only.
    for k in i:
        z=s[k-9:k]; z=z[z!=0]
        turns[k]=np.sum(z[1:]!=z[:-1]) if len(z)>1 else 0.0
    return disp,eff,rng,turns


def aggregate_from_seconds(sec_ids,h,l,c,tf):
    bucket=sec_ids//tf
    change=np.empty(len(bucket),dtype=np.bool_); change[0]=True; change[1:]=bucket[1:]!=bucket[:-1]
    idx=np.flatnonzero(change)
    last=np.r_[idx[1:]-1,len(bucket)-1]
    ids=bucket[idx]
    cc=c[last]
    hh=np.maximum.reduceat(h,idx)
    ll=np.minimum.reduceat(l,idx)
    end=(ids+1)*tf
    prev=np.r_[np.nan,cc[:-1]]
    tr=np.maximum(hh-ll,np.maximum(np.abs(hh-prev),np.abs(ll-prev)))
    atr=np.full(len(tr),np.nan,np.float64)
    e=np.nan
    for j,x in enumerate(tr):
        if not np.isfinite(x): continue
        e=x if not np.isfinite(e) else (13.0/14.0)*e+(1.0/14.0)*x
        if j>=13: atr[j]=e
    ret=np.r_[np.nan,np.diff(cc)]
    return end.astype(np.int64), ret, atr


def map_completed(sec_ids,end,values):
    j=np.searchsorted(end,sec_ids,side='right')-1
    out=np.full(len(sec_ids),np.nan,np.float64)
    ok=j>=0; out[ok]=values[j[ok]]
    return out


def main():
    t0=time.time()
    d=pd.read_csv(RAW,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],
                  dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
    t=d.timestamp_ms_utc.to_numpy(np.int64,copy=False)
    ask=d.ask_raw.to_numpy(np.float64)/1000.0
    bid=d.bid_raw.to_numpy(np.float64)/1000.0
    mid=(ask+bid)*0.5
    load_s=time.time()-t0

    t1=time.time(); sec_ids,o,h,l,c,n=active_seconds(t,mid); active_s=time.time()-t1
    t2=time.time(); sd,se,sr,st=s1_features(h,l,c); s1_s=time.time()-t2

    t3=time.time()
    end5,ret5,atr5=aggregate_from_seconds(sec_ids,h,l,c,300)
    m5atr=map_completed(sec_ids,end5,atr5)
    along=np.zeros(len(sec_ids),np.int8); ashort=np.zeros(len(sec_ids),np.int8)
    tf_meta={}
    for tf in (60,180,300,600,1200):
        end,ret,atr=aggregate_from_seconds(sec_ids,h,l,c,tf)
        rr=map_completed(sec_ids,end,ret); aa=map_completed(sec_ids,end,atr)
        valid=np.isfinite(aa)
        along += ((rr>0)&valid).astype(np.int8)
        ashort += ((rr<0)&valid).astype(np.int8)
        tf_meta[str(tf)]={'bars':int(len(end)),'first_end':int(end[0]),'last_end':int(end[-1])}
    tf_s=time.time()-t3

    t4=time.time()
    np.savez(CACHE,
             sec_ids=sec_ids,o=o,h=h,l=l,c=c,tick_count=n,
             s1_disp=sd,s1_eff=se,s1_range=sr,s1_turns=st,
             m5_atr=m5atr,align_long=along,align_short=ashort)
    save_s=time.time()-t4
    # Deterministic invariants needed by following replay unit.
    result={
      'job_id':'MM-C30-B1B-M01-PRECOMPUTE-OPT',
      'status':'COMPLETED_LOCAL',
      'month':'2026-01',
      'scope':'engineering precompute only; no strategy economics; no May-Jul access',
      'raw_rows':int(len(t)),
      'active_seconds':int(len(sec_ids)),
      'raw_first_ms':int(t[0]),'raw_last_ms':int(t[-1]),
      'active_first_sec':int(sec_ids[0]),'active_last_sec':int(sec_ids[-1]),
      's1_ready_seconds':int(np.isfinite(sd).sum()),
      'm5_atr_ready_seconds':int(np.isfinite(m5atr).sum()),
      'align_hist_long':{str(i):int(np.sum(along==i)) for i in range(6)},
      'align_hist_short':{str(i):int(np.sum(ashort==i)) for i in range(6)},
      'tf_meta':tf_meta,
      'timing_seconds':{'csv_load':load_s,'active_seconds':active_s,'s1_features':s1_s,'tf_features':tf_s,'save':save_s,'total':time.time()-t0},
      'raw_sha256':sha256(RAW),
      'cache_sha256':sha256(CACHE),
      'cache_bytes':CACHE.stat().st_size,
      'frozen_next_checksum':{'rule10_january_net_delta':63.60,'rule':'>=3/5 completed 1m/3m/5m/10m/20m returns aligned at entry; alive +2s; >=6 post-entry ticks','extension':'60s max hold; +$0.20 activation; $0.08 trail'},
      'promotion':'NONE_PRECOMPUTE_ONLY'
    }
    with open(RESULT,'w') as f: json.dump(result,f,indent=2,sort_keys=True)
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__': main()
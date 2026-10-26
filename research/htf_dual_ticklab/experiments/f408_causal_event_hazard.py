"""F408: original t0 event-arrival and previously matured 3-class hazards.

Research only. No source quote-tape price, no true quote intensity/OFI,
no fitted FILTER08 teacher and no current event outcome at decision time.
Existing replay engine and original event index/timestamp/side remain immutable.
"""
from __future__ import annotations
import io, json, zipfile, hashlib, pathlib
import numpy as np

GRACE_MS=33_002
WINDOWS_S=(20,60,180,600,1800,3600)

def features(t,side,truth):
    t=np.asarray(t,dtype=np.int64);side=np.asarray(side,dtype=np.int8);truth=np.asarray(truth,dtype=np.int8)
    assert len(t)==len(side)==len(truth) and np.all(np.diff(t)>=0)
    assert np.all(np.isin(side,(-1,1))) and np.all(np.isin(truth,(0,1,2)))
    n=len(t);i=np.arange(n,dtype=np.int64)
    matured_end=np.searchsorted(t,t-GRACE_MS,side='right')
    assert np.all(matured_end<=i)
    prev=np.maximum(i-1,0)
    feats=[];names=[]
    def add(name,v):
        a=np.asarray(v,dtype=np.float32)
        assert a.shape==(n,) and np.isfinite(a).all(),name
        feats.append(a);names.append(name)
    add('side_original',side)
    add('event_gap_s',np.where(i>0,np.minimum((t-t[prev])/1000,600),600))
    for k in (2,8,32,128):
        ix=np.maximum(i-k,0)
        add(f'last{k}_event_span_s',np.where(i>=k,np.minimum((t-t[ix])/1000,3600),3600))
        add(f'last{k}_event_side_switch_rate',
            (np.cumsum(np.r_[0,(side[1:]!=side[:-1]).astype(np.int32)])[i]
             -np.cumsum(np.r_[0,(side[1:]!=side[:-1]).astype(np.int32)])[ix])/np.maximum(i-ix,1))
    secs=t/1000
    utc_hour=((t//3600000)%24).astype(np.float64)
    utc_week=((t//86400000+3)%7).astype(np.float64)
    for nm,period,v in [('utc_hour',24,utc_hour),('utc_week',7,utc_week)]:
        add(nm+'_sin',np.sin(2*np.pi*v/period));add(nm+'_cos',np.cos(2*np.pi*v/period))
    # Prefix class counts for matured history, not same-event labels.
    # Cumulative sums computed on full archive but only prefix indices < event time are accessed.
    cats=np.column_stack([(truth==c)&(side==s) for s in (-1,1) for c in (0,1,2)]).astype(np.int32)
    prefix=np.vstack((np.zeros((1,6),dtype=np.int32),np.cumsum(cats,axis=0,dtype=np.int32)))
    windows={}
    for h in WINDOWS_S:
        lo=np.searchsorted(t,t-GRACE_MS-h*1000,side='left')
        w=(prefix[matured_end]-prefix[lo]).astype(np.float32)
        windows[h]=w
        nside=np.where(side>0,w[:,3:].sum(axis=1),w[:,:3].sum(axis=1))
        same_good=np.where(side>0,w[:,3],w[:,0]);same_opp=np.where(side>0,w[:,4],w[:,1]);same_neu=np.where(side>0,w[:,5],w[:,2])
        other_good=np.where(side>0,w[:,0],w[:,3]);other_opp=np.where(side>0,w[:,1],w[:,4])
        add(f'matured_{h}s_same_count_log',np.log1p(nside))
        add(f'matured_{h}s_same_opp_p',(same_opp+1)/(nside+3))
        add(f'matured_{h}s_same_neu_p',(same_neu+1)/(nside+3))
        add(f'matured_{h}s_same_good_p',(same_good+1)/(nside+3))
        add(f'matured_{h}s_cross_direction',(same_good-same_opp-other_good+other_opp)/(w.sum(axis=1)+6))
        # Strictly pre-event original R00 signal arrival counts; NOT quote tick intensity.
        e_lo=np.searchsorted(t,t-h*1000,side='left')
        add(f'event_arrival_{h}s_log',np.log1p(i-e_lo))
        sb=np.r_[0,np.cumsum((side==1).astype(np.int32))]
        buys=sb[i]-sb[e_lo]
        add(f'event_side_imbalance_{h}s',(2*buys-(i-e_lo))/(i-e_lo+4))
    for short,long in ((20,180),(60,600),(180,1800),(600,3600)):
        w0=windows[short];w1=windows[long]
        def rate(w,c):return (w[:,c]+w[:,c+3]+1)/(w.sum(axis=1)+3)
        add(f'opposite_regime_jump_{short}_{long}',rate(w0,1)-rate(w1,1))
        add(f'neutral_regime_jump_{short}_{long}',rate(w0,2)-rate(w1,2))
        add(f'correct_regime_jump_{short}_{long}',rate(w0,0)-rate(w1,0))
    # Last matured event class and side, never current-event outcome.
    for k in (1,3,8):
        valid=matured_end>=k
        old=np.maximum(matured_end-k,0)
        add(f'last_matured_{k}_class',np.where(valid,truth[old]+1,0))
        add(f'last_matured_{k}_side',np.where(valid,side[old],0))
        add(f'last_matured_{k}_age_s',np.where(valid,np.minimum((t-t[old])/1000,3600),3600))
    return np.column_stack(feats).astype(np.float32),names,matured_end

def load_original(z,broker,month):
    name=f'F395_S14_{broker}_{month}_FROZEN_ORIGINAL_EVENT_MASK.npz'
    raw=z.read(name)
    with np.load(io.BytesIO(raw)) as a:
        d={k:a[k].copy() for k in ('t','side','truth','original_index','final_source_shadow_veto')}
    assert np.array_equal(d['original_index'],np.arange(len(d['t'])))
    return d,hashlib.sha256(raw).hexdigest()

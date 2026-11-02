"""Causal rolling-five-minute structural state for R9 v2 entry repair.

The feature view preserves the ordered quote path across the entire trailing 300 s
without collapsing it to one OHLC or endpoint statistic. Candidate ``now`` uses the
exact raw source index, so later source rows sharing the same millisecond are never
visible. Historical samples use the last observed quote at-or-before each 5 s lag;
missing quote intervals are not forward-synthesized and their coverage is explicit.
"""
from __future__ import annotations
import numpy as np

STRUCTURAL_5M_VERSION='r9_v2_full_5m_structural_state_v1'
LAGS_MS=np.arange(0,300001,5000,dtype=np.int64)  # now, 5s, ... 300s
N5=60

RET5_NAMES=tuple(f'path_ret5s_{i:02d}' for i in range(1,61))
RET15_NAMES=tuple(f'path_bid_ret15s_{i:02d}' for i in range(1,21))+tuple(f'path_ask_ret15s_{i:02d}' for i in range(1,21))
RET30_NAMES=tuple(f'path_mid_ret30s_{i:02d}' for i in range(1,11))
RET60_NAMES=tuple(f'path_mid_ret60s_{i:02d}' for i in range(1,6))
SPREAD15_NAMES=tuple(f'path_spread_z15s_{i:02d}' for i in range(0,21))
DERIVED_NAMES=(
 'path_scale_5s','path_coverage_mean','path_coverage_max','path_coverage_stale_fraction',
 'path_eff_60s','path_eff_180s','path_eff_300s','path_terminal_pos_60s','path_terminal_pos_180s','path_terminal_pos_300s',
 'path_extreme_order_300s','path_high_age_frac_300s','path_low_age_frac_300s','path_range_norm_300s',
 'path_max_favorable_norm_300s','path_max_adverse_norm_300s','path_retracement_ratio_300s','path_dominant_side_300s',
 'path_turn_rate_5s','path_threshold_pivots_5s','path_terminal_run_frac_5s','path_sign_persistence_5s','path_autocorr1_5s','path_autocorr3_5s',
 'path_recent_ret15_norm','path_recent_ret30_norm','path_recent_ret60_norm','path_prev60_ret_norm','path_old180_ret_norm',
 'path_accel_15_vs_60','path_accel_60_vs_prev60','path_continuation_score','path_pullback_score',
 'path_reject_high_norm','path_reject_low_norm','path_spread_current_vs_5m','path_spread_recent_vs_old',
 'path_bid_ask_lead_recent','path_bid_ask_lead_5m','path_bid_ask_disagree_15s','path_bid_ask_persistence_gap_15s',
)
STRUCTURAL_5M_NAMES=RET5_NAMES+RET15_NAMES+RET30_NAMES+RET60_NAMES+SPREAD15_NAMES+DERIVED_NAMES
STRUCTURAL_5M_COUNT=len(STRUCTURAL_5M_NAMES)
assert STRUCTURAL_5M_COUNT==177
assert len(STRUCTURAL_5M_NAMES)==len(set(STRUCTURAL_5M_NAMES))

def _sample_indices(t, candidate_ts, candidate_idx):
    """Return raw indices for [now,5s,...,300s] with exact-index current safety."""
    t=np.asarray(t,np.int64);ts=np.asarray(candidate_ts,np.int64);idx=np.asarray(candidate_idx,np.int64)
    if len(ts)!=len(idx):raise ValueError('candidate row mismatch')
    if np.any(idx<0)|np.any(idx>=len(t)):raise ValueError('candidate raw index out of range')
    if not np.array_equal(t[idx],ts):raise ValueError('candidate timestamp/raw-index mismatch')
    out=np.empty((len(ts),len(LAGS_MS)),np.int64);out[:,0]=idx
    for q,lag in enumerate(LAGS_MS[1:],1):
        j=np.searchsorted(t,ts-lag,side='right')-1
        out[:,q]=np.maximum(j,0)
    return out

def _eff(x):
    d=np.diff(x,axis=1);return np.abs(x[:,-1]-x[:,0])/(np.sum(np.abs(d),axis=1)+1e-9)

def _terminal_pos(x):
    lo=np.min(x,axis=1);hi=np.max(x,axis=1);return (2*(x[:,-1]-lo)/(hi-lo+1e-9)-1).astype(np.float32)

def _autocorr(d,k):
    if d.shape[1]<=k:return np.zeros(len(d),np.float32)
    a=d[:,:-k];b=d[:,k:];am=a-a.mean(axis=1,keepdims=True);bm=b-b.mean(axis=1,keepdims=True)
    return (np.sum(am*bm,axis=1)/(np.sqrt(np.sum(am*am,axis=1)*np.sum(bm*bm,axis=1))+1e-9)).astype(np.float32)

def build_structural_5m_features(t,bid,ask,candidate_idx,chunk_rows=25000):
    """Build source-exact five-minute structural features at candidate raw indices."""
    t=np.asarray(t,np.int64);bid=np.asarray(bid,np.float64);ask=np.asarray(ask,np.float64);idx=np.asarray(candidate_idx,np.int64)
    if not(len(t)==len(bid)==len(ask)):raise ValueError('raw length mismatch')
    if len(t) and np.any(t[1:]<t[:-1]):raise ValueError('nonchronological raw source')
    if np.any(ask<bid):raise ValueError('crossed raw quote')
    out=np.empty((len(idx),STRUCTURAL_5M_COUNT),np.float32);chunk=max(1000,int(chunk_rows))
    for lo in range(0,len(idx),chunk):
        hi=min(len(idx),lo+chunk);ii=idx[lo:hi];ts=t[ii];sidx=_sample_indices(t,ts,ii)
        sb=bid[sidx];sa=ask[sidx];sm=.5*(sb+sa);ss=sa-sb
        # sampled matrix is now->old; reverse to old->now for path calculations.
        bm=sb[:,::-1];am=sa[:,::-1];mm=sm[:,::-1];sp=ss[:,::-1]
        ages=(ts[:,None]-t[sidx])[:,::-1].astype(np.float64)
        d5=np.diff(mm,axis=1)
        scale=np.maximum(.01,np.sqrt(np.mean(d5*d5,axis=1)))
        c=0
        z5=(d5/scale[:,None]).astype(np.float32);out[lo:hi,c:c+60]=z5;c+=60
        # 15s endpoint path has 21 points, hence 20 ordered bid/ask returns.
        b15=bm[:,::3];a15=am[:,::3];m15=mm[:,::3];s15=sp[:,::3]
        db15=np.diff(b15,axis=1)/scale[:,None];da15=np.diff(a15,axis=1)/scale[:,None]
        out[lo:hi,c:c+20]=db15;c+=20;out[lo:hi,c:c+20]=da15;c+=20
        m30=mm[:,::6];dm30=np.diff(m30,axis=1)/scale[:,None];out[lo:hi,c:c+10]=dm30;c+=10
        m60=mm[:,::12];dm60=np.diff(m60,axis=1)/scale[:,None];out[lo:hi,c:c+5]=dm60;c+=5
        spr_med=np.median(sp,axis=1);spr_den=np.maximum(.01,spr_med)
        out[lo:hi,c:c+21]=((s15-spr_med[:,None])/spr_den[:,None]).astype(np.float32);c+=21

        n=len(ii);derived=np.empty((n,len(DERIVED_NAMES)),np.float32);k=0
        expected=np.arange(300000,-1,-5000,dtype=np.float64)[None,:]
        coverage=np.abs(ages-expected)/5000.0
        derived[:,k]=scale;k+=1
        derived[:,k]=np.mean(coverage,axis=1);k+=1
        derived[:,k]=np.max(coverage,axis=1);k+=1
        derived[:,k]=np.mean(coverage>.5,axis=1);k+=1
        for qn in (13,37,61):derived[:,k]=_eff(mm[:,-qn:]);k+=1
        for qn in (13,37,61):derived[:,k]=_terminal_pos(mm[:,-qn:]);k+=1
        hi_ix=np.argmax(mm,axis=1);lo_ix=np.argmin(mm,axis=1);rng=np.max(mm,axis=1)-np.min(mm,axis=1)
        derived[:,k]=(hi_ix-lo_ix)/60.;k+=1
        derived[:,k]=(60-hi_ix)/60.;k+=1;derived[:,k]=(60-lo_ix)/60.;k+=1
        derived[:,k]=rng/scale;k+=1
        disp=mm[:,-1]-mm[:,0];dom=np.where(disp>=0,1.,-1.);start=mm[:,0];curr=mm[:,-1]
        fav=np.max((mm-start[:,None])*dom[:,None],axis=1);adv=np.min((mm-start[:,None])*dom[:,None],axis=1)
        derived[:,k]=fav/scale;k+=1;derived[:,k]=adv/scale;k+=1
        extreme=np.where(dom>0,np.max(mm,axis=1),np.min(mm,axis=1));span=np.maximum(scale,np.abs(extreme-start));retr=(extreme-curr)*dom/span
        derived[:,k]=retr;k+=1;derived[:,k]=dom;k+=1
        signs=np.sign(d5);nz=(signs!=0);turn=(signs[:,1:]*signs[:,:-1]<0)
        derived[:,k]=np.sum(turn,axis=1)/np.maximum(1,np.sum(nz,axis=1)-1);k+=1
        threshold=.35*scale[:,None];sd=np.where(np.abs(d5)>=threshold,np.sign(d5),0.)
        derived[:,k]=np.sum(sd[:,1:]*sd[:,:-1]<0,axis=1);k+=1
        run=np.ones(n,np.float32);last=np.sign(d5[:,-1])
        for q in range(2,61):run+=((last!=0)&(np.sign(d5[:,-q])==last)&(run==(q-1))).astype(np.float32)
        derived[:,k]=run/60.;k+=1
        pos=np.mean(signs>0,axis=1);neg=np.mean(signs<0,axis=1);derived[:,k]=np.maximum(pos,neg);k+=1
        derived[:,k]=_autocorr(d5,1);k+=1;derived[:,k]=_autocorr(d5,3);k+=1
        ret15=mm[:,-1]-mm[:,-4];ret30=mm[:,-1]-mm[:,-7];ret60=mm[:,-1]-mm[:,-13]
        prev60=mm[:,-13]-mm[:,-25];old180=mm[:,-25]-mm[:,0]
        for v in (ret15,ret30,ret60,prev60,old180):derived[:,k]=v/scale;k+=1
        derived[:,k]=(ret15/3.-ret60/12.)/scale;k+=1
        derived[:,k]=(ret60-prev60)/scale;k+=1
        derived[:,k]=dom*(ret15/scale);k+=1
        derived[:,k]=-dom*(ret15/scale);k+=1
        derived[:,k]=(curr-np.max(mm,axis=1))/scale;k+=1
        derived[:,k]=(curr-np.min(mm,axis=1))/scale;k+=1
        derived[:,k]=(sp[:,-1]-spr_med)/spr_den;k+=1
        derived[:,k]=(np.mean(sp[:,-4:],axis=1)-np.mean(sp[:,:37],axis=1))/spr_den;k+=1
        lead=db15-da15
        derived[:,k]=np.mean(lead[:,-4:],axis=1);k+=1
        derived[:,k]=np.mean(lead,axis=1);k+=1
        derived[:,k]=np.mean((np.sign(db15)*np.sign(da15))<0,axis=1);k+=1
        derived[:,k]=np.mean(np.sign(db15)-np.sign(da15),axis=1);k+=1
        if k!=len(DERIVED_NAMES):raise AssertionError((k,len(DERIVED_NAMES)))
        out[lo:hi,c:c+k]=derived;c+=k
        if c!=STRUCTURAL_5M_COUNT:raise AssertionError((c,STRUCTURAL_5M_COUNT))
    if not np.isfinite(out).all():raise ValueError('nonfinite structural state')
    return out
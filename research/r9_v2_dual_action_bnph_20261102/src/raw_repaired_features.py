"""Source-exact raw quote kernels for repaired R9 v2 features.

These functions build the v4 repaired feature contract directly from chronological
Bid/Ask ticks at arbitrary decision indices. No legacy specialist nomination or
future outcome enters the feature matrix. The same kernels are used for old-lane
parity and the new direction-neutral 250 ms opportunity universe.
"""
from __future__ import annotations
import math
import numpy as np
from numba import njit
from repaired_features import (
    GRID_LAGS_MS, SEGMENTS_MS, GEOMETRY_WINDOWS_MS, EXCITATION_TAUS_MS,
    GRID_NAMES, EXCITATION_NAMES, CONTEXT_NAMES, REPAIRED_FEATURE_COUNT,
)

GRID_LAGS=np.asarray(GRID_LAGS_MS,np.int64)
SEG_SHORT=np.asarray([GRID_LAGS_MS.index(a) for a,b in SEGMENTS_MS],np.int64)
SEG_LONG=np.asarray([GRID_LAGS_MS.index(b) for a,b in SEGMENTS_MS],np.int64)
WIN_COUNTS=np.asarray([sum(x<=h for x in GRID_LAGS_MS) for h in GEOMETRY_WINDOWS_MS],np.int64)
WINDOWS=np.asarray(GEOMETRY_WINDOWS_MS,np.int64)
TAUS=np.asarray(EXCITATION_TAUS_MS,np.float64)
GRID_COUNT=len(GRID_NAMES);EXC_COUNT=len(EXCITATION_NAMES);CONTEXT_COUNT=len(CONTEXT_NAMES)
HTF=np.asarray((900000,3600000,14400000),np.int64)

A=np.zeros((6,6),np.float64)
for i in range(6):A[i,i]=.035
for x,y in ((0,2),(2,0),(1,3),(3,1),(4,5),(5,4)):A[x,y]=.025
BASELINE=.02

def candidate_indices_250ms(t,bid,ask,warmup_ms=300000,max_spread=1.50):
    """First raw quote of each observed 250 ms slot after direction-neutral warmup.

    These are teacher/research candidates, not filled trades. Candidate timestamps
    can overlap in their future labels. On-policy execution must be replayed later
    with one active position at a time.
    """
    t=np.asarray(t,np.int64);bid=np.asarray(bid,float);ask=np.asarray(ask,float)
    if not (len(t)==len(bid)==len(ask)):raise ValueError('raw length mismatch')
    if len(t)==0:return np.empty(0,np.int64)
    if np.any(t[1:]<t[:-1]):raise ValueError('nonchronological')
    slot=t//250
    first=np.empty(len(t),bool);first[0]=True;first[1:]=slot[1:]!=slot[:-1]
    valid=first&(t>=t[0]+int(warmup_ms))&((ask-bid)<=float(max_spread))&(bid>0)&(ask>=bid)
    return np.flatnonzero(valid).astype(np.int64)

def _prefixes(bid,ask):
    n=len(bid);bu=np.zeros(n+1,np.int64);bd=np.zeros(n+1,np.int64);au=np.zeros(n+1,np.int64);ad=np.zeros(n+1,np.int64)
    sw=np.zeros(n+1,np.int64);sn=np.zeros(n+1,np.int64);ss=np.zeros(n+1,np.float64);path=np.zeros(n+1,np.float64);rv=np.zeros(n+1,np.float64)
    spread=ask-bid;ss[1:]=np.cumsum(spread,dtype=np.float64)
    if n>1:
        db=np.diff(bid);da=np.diff(ask);ds=np.diff(spread);dm=(db+da)*.5
        bu[2:]=np.cumsum(db>1e-10);bd[2:]=np.cumsum(db<-1e-10);au[2:]=np.cumsum(da>1e-10);ad[2:]=np.cumsum(da<-1e-10)
        sw[2:]=np.cumsum(ds>1e-10);sn[2:]=np.cumsum(ds<-1e-10);path[2:]=np.cumsum(np.abs(dm));rv[2:]=np.cumsum(dm*dm)
    return bu,bd,au,ad,sw,sn,ss,path,rv

def build_context_features(t,bid,ask,idx):
    """Exact 28-column v4 non-specialist context from raw quotes."""
    t=np.asarray(t,np.int64);bid=np.asarray(bid,np.float64);ask=np.asarray(ask,np.float64);idx=np.asarray(idx,np.int64)
    if np.any(idx<0) or np.any(idx>=len(t)):raise ValueError('candidate index out of range')
    out=np.zeros((len(idx),CONTEXT_COUNT),np.float32)
    spread=ask-bid;mid=.5*(bid+ask);j0=np.maximum(0,idx-1);db=bid[idx]-bid[j0];da=ask[idx]-ask[j0]
    hour=(t[idx]//3600000)%24;dow=((t[idx]//86400000)+3)%7
    out[:,0]=spread[idx];out[:,1]=db;out[:,2]=da;out[:,3]=db-da;out[:,4]=(db+da)*.5
    out[:,5]=(db-da)/(np.abs(db)+np.abs(da)+.001)
    out[:,6]=np.sin(2*np.pi*hour/24);out[:,7]=np.cos(2*np.pi*hour/24)
    out[:,8]=np.sin(2*np.pi*dow/7);out[:,9]=np.cos(2*np.pi*dow/7)
    bu,bd,au,ad,sw,sn,ss,path,rv=_prefixes(bid,ask)
    c=10
    for h in HTF:
        j=np.searchsorted(t,t[idx]-h,side='left');count=idx-j+1;delta=mid[idx]-mid[j]
        up=(bu[idx+1]-bu[j])+(au[idx+1]-au[j]);down=(bd[idx+1]-bd[j])+(ad[idx+1]-ad[j]);total=up+down
        out[:,c]=delta;out[:,c+1]=(ss[idx+1]-ss[j])/count;out[:,c+2]=(up-down)/(total+1)
        out[:,c+3]=np.sqrt(np.maximum(0.,rv[idx+1]-rv[j]));out[:,c+4]=count/(h/1000.)
        out[:,c+5]=np.abs(delta)/(np.maximum(0.,path[idx+1]-path[j])+.0001);c+=6
    return out

@njit(cache=True)
def _geometry_from_samples(sm,sage,current,win_counts,windows):
    m=sm.shape[0];out=np.zeros((m,len(windows)*5),np.float32)
    for r in range(m):
        col=0
        for w in range(len(windows)):
            qn=win_counts[w];old=qn-1;prev=sm[r,old];hi=prev;lo=prev;age_hi=sage[r,old];age_lo=sage[r,old]
            path=0.;turns=0;nsign=0;last_sign=0
            for q in range(old-1,-1,-1):
                v=sm[r,q];d=v-prev;path+=abs(d);sign=1 if d>1e-12 else (-1 if d<-1e-12 else 0)
                if sign:
                    if last_sign and sign!=last_sign:turns+=1
                    last_sign=sign;nsign+=1
                if v>hi:hi=v;age_hi=sage[r,q]
                if v<lo:lo=v;age_lo=sage[r,q]
                prev=v
            v=current[r];d=v-prev;path+=abs(d);sign=1 if d>1e-12 else (-1 if d<-1e-12 else 0)
            if sign:
                if last_sign and sign!=last_sign:turns+=1
                nsign+=1
            if v>hi:hi=v;age_hi=0
            if v<lo:lo=v;age_lo=0
            rng=hi-lo;disp=v-sm[r,old]
            out[r,col]=disp/(path+1e-9);out[r,col+1]=(2*(v-lo)/(rng+1e-9)-1) if rng>1e-12 else 0.
            out[r,col+2]=(age_lo-age_hi)/max(1.,float(windows[w]));out[r,col+3]=turns/max(1,nsign-1);out[r,col+4]=rng;col+=5
    return out

def build_grid_features(t,bid,ask,idx):
    idx=np.asarray(idx,np.int64);m=len(idx);L=len(GRID_LAGS);now=t[idx];cb=bid[idx];ca=ask[idx];cm=.5*(cb+ca);cs=ca-cb
    sb=np.empty((m,L),np.float32);sa=np.empty((m,L),np.float32);sage=np.empty((m,L),np.int64)
    for q,lag in enumerate(GRID_LAGS):
        j=np.searchsorted(t,now-lag,side='right')-1;j=np.maximum(j,0);sb[:,q]=bid[j];sa[:,q]=ask[j];sage[:,q]=now-t[j]
    sm=.5*(sb+sa);ss=sa-sb;out=np.empty((m,GRID_COUNT),np.float32);col=0
    for q,lag in enumerate(GRID_LAGS):
        out[:,col]=cb-sb[:,q];out[:,col+1]=ca-sa[:,q];out[:,col+2]=cs-ss[:,q];out[:,col+3]=np.minimum(1.5,sage[:,q]/float(lag));col+=4
    for x,y in zip(SEG_SHORT,SEG_LONG):
        out[:,col]=sb[:,x]-sb[:,y];out[:,col+1]=sa[:,x]-sa[:,y];out[:,col+2]=ss[:,x]-ss[:,y];col+=3
    g=_geometry_from_samples(sm,sage,cm,WIN_COUNTS,WINDOWS);out[:,col:col+g.shape[1]]=g;col+=g.shape[1]
    if col!=GRID_COUNT:raise AssertionError((col,GRID_COUNT))
    return out

def decay_table(max_ms=60000):
    dt=np.arange(max_ms+1,dtype=np.float64);return np.exp(-dt[None,:]/TAUS[:,None])

@njit(cache=True)
def build_excitation_features(t,bid,ask,idx,decays,taus,A_,baseline):
    m=len(idx);out=np.zeros((m,EXC_COUNT),np.float32);state=np.zeros((len(taus),6),np.float64);maxdt=decays.shape[1]-1;row=0
    for k in range(len(t)):
        if k>0:
            dt=t[k]-t[k-1]
            for z in range(len(taus)):
                decay=decays[z,dt] if 0<=dt<=maxdt else math.exp(-dt/taus[z])
                for e in range(6):state[z,e]*=decay
            db=bid[k]-bid[k-1];da=ask[k]-ask[k-1];ds=(ask[k]-bid[k])-(ask[k-1]-bid[k-1]);vals=(db,-db,da,-da,ds,-ds)
            for e in range(6):
                if vals[e]>1e-10:
                    for z in range(len(taus)):state[z,e]+=1.
        while row<m and idx[row]==k:
            col=0
            for z in range(len(taus)):
                bu,bd,au,ad,sw,sn=state[z]
                out[row,col]=(bu-bd)/(bu+bd+1e-9);out[row,col+1]=(au-ad)/(au+ad+1e-9)
                out[row,col+2]=(bu+au-bd-ad)/(bu+au+bd+ad+1e-9);out[row,col+3]=(sn-sw)/(sn+sw+1e-9)
                total=bu+bd+au+ad+sw+sn;out[row,col+4]=math.log1p(total if total>0 else 0.);col+=5
            weighted=np.zeros(6,np.float64)
            for e in range(6):
                for z in range(len(taus)):weighted[e]+=state[z,e]
                weighted[e]/=len(taus)
            lam=np.empty(6,np.float64)
            for i in range(6):
                v=baseline
                for j in range(6):v+=A_[i,j]*weighted[j]
                lam[i]=v
            if ask[k]-bid[k]<=.01:lam[5]=0.
            up=lam[0]+lam[2];down=lam[1]+lam[3]
            out[row,col]=(up-down)/(up+down+1e-12);out[row,col+1]=(lam[5]-lam[4])/(lam[5]+lam[4]+1e-12)
            total_l=0.
            for e in range(6):total_l+=lam[e]
            ent=0.
            for e in range(6):
                p=lam[e]/(total_l+1e-12)
                if p>0:ent-=p*math.log(p+1e-12)
            out[row,col+2]=ent;row+=1
    return out,row

def build_repaired_raw_features(t,bid,ask,idx,chunk_rows=25000):
    """Return the complete v4 feature matrix at arbitrary raw tick indices."""
    idx=np.asarray(idx,np.int64);X=np.empty((len(idx),REPAIRED_FEATURE_COUNT),np.float32);c=0
    ctx=build_context_features(t,bid,ask,idx);X[:,c:c+ctx.shape[1]]=ctx;c+=ctx.shape[1]
    chunk=max(1000,int(chunk_rows))
    for lo in range(0,len(idx),chunk):
        hi=min(len(idx),lo+chunk);g=build_grid_features(t,bid,ask,idx[lo:hi]);X[lo:hi,c:c+g.shape[1]]=g
    c+=GRID_COUNT
    exc,hit=build_excitation_features(np.asarray(t,np.int64),np.asarray(bid,np.float64),np.asarray(ask,np.float64),idx,decay_table(),TAUS,A,BASELINE)
    if hit!=len(idx):raise ValueError(f'excitation matched {hit}/{len(idx)}')
    X[:,c:c+EXC_COUNT]=exc;c+=EXC_COUNT
    if c!=REPAIRED_FEATURE_COUNT or not np.isfinite(X).all():raise ValueError('raw repaired feature contract failure')
    return X

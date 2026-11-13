"""Auditable 60-second causal XAUUSD features on previously observed 500-ms grid.

Input shape (N,5,120): side-aligned standardized mid-return, relative spread,
log(1+quote events), side-aligned normalized mid-level, absolute return.
The source extractor explicitly as-of clamps the final sample to the decision
ordinal. All derived features use only X at or prior to that ordinal.
"""
from __future__ import annotations
import numpy as np
from numba import njit

WINDOWS=(2,6,10,20,30,60,120)

@njit(cache=True)
def _one_features(X):
    n=X.shape[0]
    # 7 lookbacks x 14 features + 5 global spread/event patterns
    out=np.zeros((n,103),dtype=np.float32)
    for i in range(n):
        k=0
        for w in WINDOWS:
            start=120-w
            path=0.0;net=0.0;pos=0.0;neg=0.0;rv=0.0;bp=0.0
            reversals=0;prev=0;ct=0.0;count_high_spread=0
            max_abs=0.0;quote_events=0.0;last_r=0.0;recent=0.0
            for j in range(start,120):
                r=float(X[i,0,j]);ar=abs(r)
                path+=ar;net+=r;rv+=r*r
                if r>0:pos+=r
                if r<0:neg-=r
                if j>start:bp+=ar*abs(last_r)
                last_r=r
                s=1 if r>0 else (-1 if r<0 else 0)
                if s and prev and s!=prev:reversals+=1
                if s:prev=s
                ct+=X[i,2,j]
                quote_events+=np.expm1(min(13.0,X[i,2,j]))
                if X[i,1,j]>0.25:count_high_spread+=1
                if ar>max_abs:max_abs=ar
                recent+=X[i,4,j]
            eff=abs(net)/(path+1e-5)
            values=(net,path,eff,rv/max(1,w),bp/max(1,w-1),
                max(0.,rv-(np.pi/2)*bp)/max(1,w),
                (pos-neg)/(pos+neg+1e-5),pos/(pos+neg+1e-5),
                reversals/max(1,w),ct/w,quote_events/max(1,w),
                count_high_spread/max(1,w),max_abs,
                net/(np.sqrt(rv)+1e-5))
            for value in values:
                out[i,k]=value;k+=1
        out[i,k]=X[i,1,119];k+=1
        out[i,k]=X[i,2,119];k+=1
        out[i,k]=X[i,3,119];k+=1
        out[i,k]=X[i,4,119];k+=1
        out[i,k]=X[i,0,119]
    return out

def hft_features(X:np.ndarray)->np.ndarray:
    X=np.asarray(X,np.float32)
    if X.ndim!=3 or X.shape[1:]!=(5,120):
        raise ValueError('Expected (n,5,120) past-only sequences')
    if not np.isfinite(X).all():raise ValueError('non-finite source features')
    return _one_features(X)

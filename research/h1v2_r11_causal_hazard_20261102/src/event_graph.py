"""R11 event-time Bid/Ask microstructure graph with 300s causal memory.

Research-only additive feature family. Never mutates original H1V2 teacher or
uses future outcomes in X. It captures the two mixed-sign quote revisions lost
by R4 and a temporal multi-scale rolling path with exact extrema order.
Best Bid/Ask quote changes are NOT exchange order flow or L2 market orders.
"""
from __future__ import annotations
import numpy as np
from numba import njit

WINDOWS_MS = (250, 1000, 3000, 15000, 30000, 60000, 300000)
MARKS = (
    'UNCHANGED', 'BID_UP_ONLY', 'BID_DOWN_ONLY', 'ASK_UP_ONLY',
    'ASK_DOWN_ONLY', 'BOTH_UP', 'BOTH_DOWN', 'BID_UP_ASK_DOWN',
    'BID_DOWN_ASK_UP',
)
BASE = ('quote_count', 'elapsed_ms', 'mid_delta', 'signed_path_efficiency',
        'mid_range', 'high_age_ms', 'low_age_ms', 'extrema_order',
        'terminal_range_location', 'abs_mid_path', 'mean_spread',
        'mixed_compress_fraction', 'mixed_widen_fraction',
        'bid_leads_ask_count', 'ask_leads_bid_count')
FIELDS = BASE + tuple('mark_'+m for m in MARKS)
NAMES = tuple(f'{s}_{int(w)}ms' for w in WINDOWS_MS for s in FIELDS)

@njit(cache=True)
def classify_marks(b, a):
    n=len(b);m=np.zeros(n,np.uint8)
    for j in range(1,n):
        db=b[j]-b[j-1];da=a[j]-a[j-1]
        if db>1e-10:
            m[j]=5 if da>1e-10 else (7 if da<-1e-10 else 1)
        elif db<-1e-10:
            m[j]=8 if da>1e-10 else (6 if da<-1e-10 else 2)
        else:
            m[j]=3 if da>1e-10 else (4 if da<-1e-10 else 0)
    return m

@njit(cache=True)
def _graph(t, mid, spread, marks, ix, windows, cap):
    n=len(t);K=len(windows);f=len(FIELDS)
    result=np.zeros((len(ix),K*f),np.float32)
    maxq=np.zeros((K,cap),np.int64);minq=np.zeros((K,cap),np.int64)
    mh=np.zeros(K,np.int64);ms=np.zeros(K,np.int64)
    nh=np.zeros(K,np.int64);ns=np.zeros(K,np.int64)
    left=np.zeros(K,np.int64)
    markcounts=np.zeros((K,9),np.int64);leadcounts=np.zeros((K,2),np.int64)
    spreadsums=np.zeros(K,np.float64)
    path=np.zeros(n,np.float64)
    leads=np.zeros((n,2),np.uint8)
    for j in range(1,n):
        path[j]=path[j-1]+abs(mid[j]-mid[j-1])
        pm=marks[j-1];cm=marks[j]
        if (pm==1 and cm==3) or (pm==2 and cm==4):leads[j,0]=1
        if (pm==3 and cm==1) or (pm==4 and cm==2):leads[j,1]=1
    r=0
    for j in range(n):
        now=t[j]
        for k in range(K):
            cutoff=now-windows[k]
            while left[k] < j and t[left[k]] < cutoff:
                z=left[k]
                markcounts[k,marks[z]]-=1
                leadcounts[k,0]-=leads[z,0];leadcounts[k,1]-=leads[z,1]
                spreadsums[k]-=spread[z]
                left[k]+=1
            while ms[k] and maxq[k,(mh[k]+ms[k]-1)%cap]!=-1 and mid[maxq[k,(mh[k]+ms[k]-1)%cap]]<=mid[j]:
                ms[k]-=1
            maxq[k,(mh[k]+ms[k])%cap]=j;ms[k]+=1
            while ns[k] and minq[k,(nh[k]+ns[k]-1)%cap]!=-1 and mid[minq[k,(nh[k]+ns[k]-1)%cap]]>=mid[j]:
                ns[k]-=1
            minq[k,(nh[k]+ns[k])%cap]=j;ns[k]+=1
            while ms[k] and maxq[k,mh[k]]<left[k]:
                mh[k]=(mh[k]+1)%cap;ms[k]-=1
            while ns[k] and minq[k,nh[k]]<left[k]:
                nh[k]=(nh[k]+1)%cap;ns[k]-=1
            markcounts[k,marks[j]]+=1
            leadcounts[k,0]+=leads[j,0];leadcounts[k,1]+=leads[j,1]
            spreadsums[k]+=spread[j]
            if r>=len(ix) or j!=ix[r]:continue
            lo=left[k];cnt=j-lo+1;elapsed=now-t[lo]
            hi_ix=maxq[k,mh[k]];lo_ix=minq[k,nh[k]]
            high=mid[hi_ix];low=mid[lo_ix];rng=high-low
            walk=path[j]-path[lo];delta=mid[j]-mid[lo]
            off=k*f
            result[r,off+0]=cnt
            result[r,off+1]=elapsed
            result[r,off+2]=delta
            result[r,off+3]=delta/(walk+1e-10)
            result[r,off+4]=rng
            result[r,off+5]=now-t[hi_ix]
            result[r,off+6]=now-t[lo_ix]
            result[r,off+7]=1. if lo_ix>hi_ix else (-1. if lo_ix<hi_ix else 0.)
            result[r,off+8]=(mid[j]-low)/(rng+1e-10)
            result[r,off+9]=walk
            result[r,off+10]=spreadsums[k]/cnt
            result[r,off+11]=markcounts[k,7]/cnt
            result[r,off+12]=markcounts[k,8]/cnt
            result[r,off+13]=leadcounts[k,0]
            result[r,off+14]=leadcounts[k,1]
            for m in range(9):result[r,off+15+m]=markcounts[k,m]
        if r<len(ix) and j==ix[r]:r+=1
    return result

def extract(t,bid,ask,idx,windows=WINDOWS_MS):
    t=np.asarray(t,dtype=np.int64);b=np.asarray(bid,np.float64);a=np.asarray(ask,np.float64)
    ix=np.asarray(idx,dtype=np.int64);w=np.asarray(windows,dtype=np.int64)
    if not (len(t)==len(b)==len(a)) or np.any(np.diff(t)<0) or (not np.isfinite(b).all()) or (not np.isfinite(a).all()) or np.any(a<b):
        raise ValueError('invalid quote stream')
    if np.any(np.diff(ix)<=0) or (len(ix) and (ix[0]<0 or ix[-1]>=len(t))):
        raise ValueError('invalid input ordinals')
    if np.any(w<=0) or np.any(np.diff(w)<=0):
        raise ValueError('windows must be positive increasing')
    if not len(t):return np.empty((0,len(w)*len(FIELDS)),np.float32)
    first=np.searchsorted(t,t-int(w[-1]),side='left')
    cap=int(np.max(np.arange(len(t),dtype=np.int64)-first+1))+2
    z=_graph(t,(b+a)*.5,a-b,classify_marks(b,a),ix,w,cap)
    if not np.isfinite(z).all() or z.shape!=(len(ix),len(w)*len(FIELDS)):
        raise ValueError('invalid generated causal graph')
    return z

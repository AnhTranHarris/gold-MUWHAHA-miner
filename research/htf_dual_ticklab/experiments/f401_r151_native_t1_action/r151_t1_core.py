"""Source-native T1 action-time contract, F401-R151. Research only.

No original t0 order is modified. All T1 proposals are counterfactual and
never submitted. L1 bid/ask touches are not certified broker fills.
"""
import numpy as np
from numba import njit

def action_t1_index(quote_ms_utc, original_t0_ms_utc):
    """First native quote in [t0+15_000,t0+16_000); -1 if absent."""
    t=np.asarray(quote_ms_utc,dtype=np.int64)
    t0=np.asarray(original_t0_ms_utc,dtype=np.int64)
    if len(t)==0:
        return np.full(len(t0),-1,dtype=np.int64)
    if np.any(np.diff(t)<0) or np.any(np.diff(t0)<0):
        raise ValueError('UNSORTED_SOURCE_CLOCK')
    idx=np.searchsorted(t,t0+15000,side='left')
    safe=np.minimum(idx,len(t)-1)
    valid=(idx<len(t))&(t[safe]<t0+16000)
    return np.where(valid,idx,-1).astype(np.int64)

@njit(cache=True)
def first_touch(t,bid,ask,idx,side,target_raw=2000,stop_raw=1500,horizon_ms=30000):
    """First favorable/adverse native quote touch after hypothetical T1.

    Outcome 1=favorable first, -1=adverse first, 0=time mark,
    -9=no executable observation. BUY enters ASK/exits BID; SELL enters
    BID/exits ASK. Excludes current and same-millisecond source quotes.
    """
    n=len(idx)
    out=np.full(n,-9,dtype=np.int8)
    gross=np.zeros(n,dtype=np.int32)
    elapsed=np.full(n,-1,dtype=np.int32)
    exit_idx=np.full(n,-1,dtype=np.int32)
    for j in range(n):
        k=idx[j]
        if k<0 or k>=len(t):
            continue
        s=side[j]
        entry=ask[k] if s>0 else bid[k]
        deadline=t[k]+horizon_ms
        last=k
        for p in range(k+1,len(t)):
            if t[p]>deadline:
                break
            if t[p]<=t[k]:
                continue
            last=p
            px=bid[p] if s>0 else ask[p]
            pnl=s*(px-entry)
            if pnl>=target_raw:
                out[j]=1
                gross[j]=pnl
                elapsed[j]=t[p]-t[k]
                exit_idx[j]=p
                break
            if pnl<=-stop_raw:
                out[j]=-1
                gross[j]=pnl
                elapsed[j]=t[p]-t[k]
                exit_idx[j]=p
                break
        if out[j]==-9 and last>k:
            out[j]=0
            px=bid[last] if s>0 else ask[last]
            gross[j]=s*(px-entry)
            elapsed[j]=t[last]-t[k]
            exit_idx[j]=last
    return out,gross,elapsed,exit_idx

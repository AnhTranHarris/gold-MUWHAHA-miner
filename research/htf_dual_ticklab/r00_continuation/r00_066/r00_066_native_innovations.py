"""Causal quote-side innovation prototype for R00-066 DESIGN-ONLY research.

Input times must already be normalized by the unchanged, approved broker reader.
These are quote updates, not exchange trade prints or confirmed order flow.
No labels, future outcomes or changes to source-clock logic are here.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class NativeInnovations:
    tick_time_ms: np.ndarray
    max_observed_feature_time_ms: np.ndarray
    bid_change: np.ndarray
    ask_change: np.ndarray
    update_kind: np.ndarray  # 0 unchanged, 1 bid-only, 2 ask-only, 3 both
    prior_quote_age_ms: np.ndarray
    trailing_bid_update_count_1s: np.ndarray
    trailing_ask_update_count_1s: np.ndarray
    opposite_quote_age_ms: np.ndarray  # -1 when unavailable or not one-sided


def extract_quote_innovations(t_ms: np.ndarray, bid: np.ndarray, ask: np.ndarray) -> NativeInnovations:
    """Only current and preceding observed ticks; prefix invariant."""
    t=np.asarray(t_ms,dtype=np.int64)
    b=np.asarray(bid,dtype=np.float64)
    a=np.asarray(ask,dtype=np.float64)
    if len(t)==0 or len(t)!=len(b) or len(t)!=len(a):
        raise ValueError('nonempty equally sized quote arrays required')
    if np.any(np.diff(t)<0) or np.any(b<=0) or np.any(a<b) or not np.all(np.isfinite(b+a)):
        raise ValueError('invalid chronology or bid/ask quotes')
    db=np.zeros(len(t)); da=np.zeros(len(t))
    db[1:]=np.diff(b); da[1:]=np.diff(a)
    bc=np.abs(db)>1e-9; ac=np.abs(da)>1e-9
    kind=bc.astype(np.uint8)+2*ac.astype(np.uint8)
    age=np.zeros(len(t),np.int64);age[1:]=np.diff(t)
    start=np.searchsorted(t,t-1000,side='left')
    cb=np.cumsum(bc,dtype=np.int64); ca=np.cumsum(ac,dtype=np.int64)
    nb=cb-np.where(start>0,cb[np.maximum(start-1,0)],0)
    na=ca-np.where(start>0,ca[np.maximum(start-1,0)],0)
    other_age=np.full(len(t),-1,dtype=np.int64)
    last_bid=None;last_ask=None
    for i in range(len(t)):
        if bc[i] and not ac[i] and last_ask is not None:
            other_age[i]=int(t[i]-last_ask)
        elif ac[i] and not bc[i] and last_bid is not None:
            other_age[i]=int(t[i]-last_bid)
        if bc[i]:last_bid=int(t[i])
        if ac[i]:last_ask=int(t[i])
    return NativeInnovations(t.copy(),t.copy(),db,da,kind,age,nb,na,other_age)

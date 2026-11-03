"""R11 lossless quote-mark and gap-epoch audit, source ordinal and prefix causal.

Extends R4's mark set 0..6 with 7 mixed bid-up/ask-down and 8 mixed
bid-down/ask-up. Mark 9 reserved for unhandled patterns (fail in strict mode).
Epoch starts on >15000ms observed quote gaps, avoiding a fabricated
cross-gap impulse. This is NOT a trained trading signal nor order-book flow.
"""
from __future__ import annotations
import numpy as np

MARK_NAMES=(
    "UNCHANGED", "BID_UP_ONLY", "BID_DOWN_ONLY",
    "ASK_UP_ONLY", "ASK_DOWN_ONLY", "BOTH_UP", "BOTH_DOWN",
    "BID_UP_ASK_DOWN", "BID_DOWN_ASK_UP", "UNCLASSIFIED",
)
def classify_delta(db:float,da:float,atol:float=1e-9)->int:
    bu=db>atol;bd=db< -atol;au=da>atol;ad=da< -atol
    if not (bu or bd or au or ad):return 0
    if bu and ad:return 7
    if bd and au:return 8
    if bu and au:return 5
    if bd and ad:return 6
    if bu and not (au or ad):return 1
    if bd and not (au or ad):return 2
    if au and not (bu or bd):return 3
    if ad and not (bu or bd):return 4
    return 9

def quote_marks(t,bid,ask,gap_reset_ms:int=15_000,atol:float=1e-9):
    t=np.asarray(t,np.int64);b=np.asarray(bid,np.float64);a=np.asarray(ask,np.float64)
    if not (t.ndim==b.ndim==a.ndim==1 and len(t)==len(b)==len(a)):
        raise ValueError("quote vectors must be 1-d aligned")
    if np.any(t[1:]<t[:-1]) or np.any(a<b) or not(np.isfinite(a).all() and np.isfinite(b).all()):
        raise ValueError("invalid raw source quote data")
    if gap_reset_ms<=0 or atol<0:raise ValueError("invalid thresholds")
    marks=np.zeros(len(t),dtype=np.uint8);epoch=np.zeros(len(t),dtype=np.bool_)
    if len(t):epoch[0]=True
    for i in range(1,len(t)):
        if t[i]-t[i-1]>gap_reset_ms:
            epoch[i]=True
            marks[i]=0  # cross-gap price difference is not in-epoch momentum
        else:
            marks[i]=classify_delta(float(b[i]-b[i-1]),float(a[i]-a[i-1]),atol=atol)
            if marks[i]==9:raise AssertionError("unclassified observed bid/ask change")
    return marks,epoch

def observed_prefix_state(t,bid,ask,entry_ordinals,lookback_ms=(250,1000,5000,30000,300000)):
    """Reference implementation for audit samples; O(window ticks) and NOT fast full-month inference.

    Five physical clocks, 9 nonzero mark categories, bid/ask response
    order and spread transition. Must replace with validated streaming
    implementation before high-frequency use. No post-entry indices read.
    """
    t=np.asarray(t,np.int64);b=np.asarray(bid,np.float64);a=np.asarray(ask,np.float64)
    idx=np.asarray(entry_ordinals,np.int64)
    if len(idx) and (idx.min()<0 or idx.max()>=len(t) or np.any(idx[1:]<=idx[:-1])):
        raise ValueError("unsorted/invalid source quote ordinals")
    marks,epoch=quote_marks(t,b,a)
    windows=tuple(int(z) for z in lookback_ms)
    if any(h<=0 for h in windows):raise ValueError("invalid horizon")
    # Per horizon: nine mark counts, true observed age, spread change,
    # first-to-last signed mid displacement, changes of mixed mark sides.
    features=np.zeros((len(idx),len(windows)*13),dtype=np.float64)
    for row,i in enumerate(idx):
        for k,h in enumerate(windows):
            lo=int(np.searchsorted(t,t[i]-h,side="left"))
            epoch_start=int(np.flatnonzero(epoch[:i+1])[-1])
            lo=max(lo,epoch_start)
            segment=marks[lo:i+1]
            c=np.bincount(segment,minlength=10)
            off=k*13
            features[row,off:off+9]=c[1:10]
            features[row,off+9]=int(t[i]-t[lo])
            features[row,off+10]=(a[i]-b[i])-(a[lo]-b[lo])
            features[row,off+11]=.5*(a[i]+b[i]-a[lo]-b[lo])
            conflict=segment[(segment==7)|(segment==8)]
            features[row,off+12]=float((conflict[1:]!=conflict[:-1]).sum()) if len(conflict)>1 else 0.
    return features

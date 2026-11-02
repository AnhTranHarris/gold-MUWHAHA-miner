"""H1V2 R4: full quote-ordinal causal marked-event state, NOT order-book flow.

Mark classes: 0 none/ambiguous; 1 bid rise; 2 bid fall; 3 ask rise;
4 ask fall; 5 bid+ask rise; 6 bid+ask fall. No midpoint executions.
Only rows j <= candidate quote index are observed; equal ms preserved by ordinal.
Exp-decay signals are *Hawkes-style regressors*, NOT a fitted Hawkes process.
"""
from __future__ import annotations
import numpy as np
from numba import njit

WINDOWS=np.array([250,1000,5000,15000,30000],dtype=np.int64)
TAU=np.array([250.,1000.,5000.],dtype=np.float64)
NAMES=(tuple(f'event_count_{k}_{h}ms' for h in WINDOWS for k in range(1,7))+
       tuple(f'decayed_{k}_{int(t)}ms' for t in TAU for k in range(1,7))+
       tuple(f'transition_{i}_{j}_last5s' for i in range(1,7) for j in range(1,7))+
       ('last_mark','second_last_mark','third_last_mark','last_gap_ms','signed_mark_run','bid_ask_push_asymmetry_1s','turn_count_5s','quote_count_5s'))

def mark_quotes(bid,ask,atol=1e-8):
    b=np.diff(bid,prepend=bid[0]);a=np.diff(ask,prepend=ask[0]);out=np.zeros(len(bid),np.uint8)
    bu=b>atol;bd=b<-atol;au=a>atol;ad=a<-atol
    out[bu&~au&~ad]=1;out[bd&~au&~ad]=2
    out[au&~bu&~bd]=3;out[ad&~bu&~bd]=4
    out[bu&au]=5;out[bd&ad]=6
    out[0]=0
    return out

@njit(cache=True)
def _features(t,marks,ix):
    n=len(ix);o=np.zeros((n,92),np.float32)
    for r in range(n):
        end=ix[r];now=t[end]
        start=np.searchsorted(t,now-30000,side='left')
        decay=np.zeros((3,6),np.float64)
        counts=np.zeros((5,6),np.float64)
        transit=np.zeros((6,6),np.float64)
        last=0; second=0; third=0;last_tm=-1;last_run=0;turns=0;events=0
        prev5=0;first_up_down=0
        for j in range(start,end+1):
            k=int(marks[j]);dt=now-t[j]
            if k==0:continue
            events+=1
            for h in range(5):
                if dt<=WINDOWS[h]:counts[h,k-1]+=1.
            for h in range(3):decay[h,k-1]+=np.exp(-dt/TAU[h])
            if dt<=5000 and prev5>0:transit[prev5-1,k-1]+=1.
            if dt<=5000:
                if prev5>0 and ((prev5%2)!=(k%2)):turns+=1
                prev5=k
            # Preserve the ordered latest three actual quote marks.
            third=second;second=last;last=k;last_tm=t[j]
            sign=1 if k in (1,3,5) else -1
            if first_up_down==sign:last_run+=sign
            else:last_run=sign
            first_up_down=sign
        o[r,:30]=counts.ravel()
        o[r,30:48]=decay.ravel()
        o[r,48:84]=transit.ravel()
        o[r,84]=last;o[r,85]=second;o[r,86]=third
        o[r,87]=now-last_tm if last_tm>=0 else 30000
        o[r,88]=last_run
        o[r,89]=counts[1,0]+counts[1,2]-counts[1,1]-counts[1,3]
        o[r,90]=turns
        o[r,91]=events
    return o

def extract(t,b,a,ix,marks=None):
    if marks is None:marks=mark_quotes(b,a)
    ix=np.asarray(ix,np.int64)
    assert np.all(np.diff(t)>=0) and np.all((ix>=0)&(ix<len(t)))
    out=_features(t,marks,ix)
    assert out.shape==(len(ix),len(NAMES)) and np.all(np.isfinite(out))
    return out

def shuffled_marks_within_second(t,marks,seed=20261102):
    """Adversarial control: preserve per-second mark histogram, destroy event order.

    This is an intentionally unrealizable counterfactual, NEVER an input feed.
    """
    rng=np.random.default_rng(seed);out=marks.copy();secs=t//1000
    bounds=np.r_[0,np.flatnonzero(secs[1:]!=secs[:-1])+1,len(t)]
    for lo,hi in zip(bounds[:-1],bounds[1:]):
        if hi-lo>1:out[lo:hi]=out[lo:hi][rng.permutation(hi-lo)]
    return out

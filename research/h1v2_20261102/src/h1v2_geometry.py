"""Raw-tick causal H1V2 99-dimensional ordered Bid/Ask geometry.

Parity target is original repaired OrderedQuoteGeometry.snapshot(), 2026-11-02.
Read only ticks with source row ordinal <= event ordinal, including equal ms.
No future maxima, outcomes, execution direction, hindsight delay or synthetic M1.
"""
from __future__ import annotations
import numpy as np
from numba import njit
WINDOWS=np.asarray((250,500,1000,5000,15000,30000,45000,60000,300000),dtype=np.int64)
FIELDS=('range','first_extreme','extreme_age_ms','terminal_location',
        'max_favorable_up','max_favorable_down','bid_only','ask_only',
        'bid_leads_ask','ask_leads_bid','path_efficiency')
NAMES=tuple(f'{name}_{int(h)}ms' for h in WINDOWS for name in FIELDS)

@njit(cache=True)
def _geom(t,b,a,ix,win):
    n=len(ix);out=np.empty((n,len(win)*11),np.float32)
    for row in range(n):
        i=ix[row];now=t[i]
        for h_i in range(len(win)):
            cutoff=now-win[h_i]
            lo=np.searchsorted(t,cutoff,side='left')
            if lo>i:lo=i
            start=(b[lo]+a[lo])*.5;end=(b[i]+a[i])*.5
            mx=start;mn=start;max_i=lo;min_i=lo
            path=0.;bid_only=0;ask_only=0;bid_lead=0;ask_lead=0
            pending_bid=0;pending_ask=0
            mid_prev=start
            for j in range(lo+1,i+1):
                mid=(b[j]+a[j])*.5
                if mid>mx:mx=mid;max_i=j
                if mid<mn:mn=mid;min_i=j
                path+=abs(mid-mid_prev);mid_prev=mid
                db=b[j]-b[j-1];da=a[j]-a[j-1]
                bc=abs(db)>1e-10;ac=abs(da)>1e-10
                if bc and not ac:
                    bid_only+=1;pending_bid+=1
                    if pending_ask:ask_lead+=1;pending_ask-=1
                elif ac and not bc:
                    ask_only+=1;pending_ask+=1
                    if pending_bid:bid_lead+=1;pending_bid-=1
                elif bc and ac:
                    pending_bid=0;pending_ask=0
            rng=mx-mn;offset=h_i*11
            out[row,offset+0]=rng
            out[row,offset+1]=1. if min_i>max_i else (-1. if min_i<max_i else 0.)
            out[row,offset+2]=now-t[max(max_i,min_i)]
            out[row,offset+3]=(end-mn)/(rng+1e-10)
            out[row,offset+4]=mx-start
            out[row,offset+5]=start-mn
            out[row,offset+6]=bid_only;out[row,offset+7]=ask_only
            out[row,offset+8]=bid_lead;out[row,offset+9]=ask_lead
            out[row,offset+10]=abs(end-start)/(path+1e-10)
    return out

def extract_raw_geometry(t,b,a,idx):
    i=np.asarray(idx,dtype=np.int64)
    if np.any(i<0) or np.any(i>=len(t)):raise IndexError('candidate ordinal')
    return _geom(np.asarray(t,np.int64),np.asarray(b,np.float64),np.asarray(a,np.float64),i,WINDOWS)


def parity_with_repaired_quote_geometry(t,b,a,idx,Geometry):
    """Full repaired original geometry as cross-check on arbitrary selected rows."""
    from types import SimpleNamespace
    ret=extract_raw_geometry(t,b,a,np.asarray(idx,dtype=np.int64))
    for k,i in enumerate(idx):
        g=Geometry();lo=np.searchsorted(t,t[i]-int(WINDOWS[-1]),side='left')
        # Original append consumes all source events up to this exact ordinal.
        for j in range(lo,i+1):g.append(int(t[j]),float(b[j]),float(a[j]))
        expected=g.snapshot()
        np.testing.assert_allclose(ret[k],expected,atol=1e-4,rtol=1e-4)
    return len(idx)

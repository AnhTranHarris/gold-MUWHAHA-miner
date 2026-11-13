"""R9 2026 event-time, exact-ordinal, quote-only competing-risk research.

Bid/Ask quote revisions are NOT market orders, real volume, L2 or executable fills.
All X derives from source ordinals <= entry ordinal. Both counterfactual BUY and
SELL Y derive from future executable quote sides and are never input to features.
"""
from __future__ import annotations
import numpy as np
from numba import njit

WINDOWS_MS = (100,500,1000,3000,5000,15000,60000)
TREND_NAMES = tuple(f'{metric}_{w}ms' for w in WINDOWS_MS for metric in ('net_mid_u','gross_path_u','path_eff','realized_vol_u','reversal_frac','quotes_per_s'))+('micro_macro_agreement','fast_slow_residual','trend_nesting_1s_5s','trend_nesting_5s_60s')
FLOW_NAMES = tuple(f'{metric}_{w}ms' for w in WINDOWS_MS for metric in ('quote_revisions_balance','quote_signed_fraction','quote_spread_pressure','quote_activity_log'))+('qaf_completed_5s','qaf_completed_15s','qaf_completed_60s')
FEATURE_NAMES = TREND_NAMES + FLOW_NAMES
TREND_N = len(TREND_NAMES)

@njit(cache=True)
def first_passage_actions(t, bid, ask, entries, stop, target, horizon_ms=15000):
    """0=none,1=favorable,2=adverse,-1=censored; 2 counterfactual sides.
    Stop/target in integer 0.01-XAU quote units, frozen before future iteration.
    Includes immediately-marked adverse spread at entry; no free mid execution.
    """
    n=len(entries)
    kind=np.zeros((n,2),dtype=np.int8)
    hit=np.full((n,2),-1,dtype=np.int32)
    ret=np.zeros((n,2),dtype=np.int32)
    for j in range(n):
        ix=entries[j]; tm=t[ix]; buy_entry=ask[ix]; sell_entry=bid[ix]
        done_buy=False;done_sell=False
        last_ix=ix
        for k in range(ix,len(t)):
            if t[k]-tm>horizon_ms:break
            if k>ix and t[k]-t[k-1]>10000:
                if not done_buy:kind[j,0]=-1
                if not done_sell:kind[j,1]=-1
                break
            dt=t[k]-tm
            if not done_buy:
                r=bid[k]-buy_entry
                if r>=target[j]:kind[j,0]=1;hit[j,0]=dt;ret[j,0]=r;done_buy=True
                elif r<=-stop[j]:kind[j,0]=2;hit[j,0]=dt;ret[j,0]=r;done_buy=True
            if not done_sell:
                r=sell_entry-ask[k]
                if r>=target[j]:kind[j,1]=1;hit[j,1]=dt;ret[j,1]=r;done_sell=True
                elif r<=-stop[j]:kind[j,1]=2;hit[j,1]=dt;ret[j,1]=r;done_sell=True
            last_ix=k
            if done_buy and done_sell:break
        if not done_buy:
            if kind[j,0]!=-1:
                if t[last_ix]-tm < horizon_ms and (last_ix==len(t)-1 or t[last_ix+1]-t[last_ix]>10000):kind[j,0]=-1
                ret[j,0]=bid[last_ix]-buy_entry
        if not done_sell:
            if kind[j,1]!=-1:
                if t[last_ix]-tm < horizon_ms and (last_ix==len(t)-1 or t[last_ix+1]-t[last_ix]>10000):kind[j,1]=-1
                ret[j,1]=sell_entry-ask[last_ix]
    return kind,hit,ret

def prefix_views(t, bid, ask):
    """Revisions as a location/arrival proxy, never false actual traded volume."""
    mid2=bid.astype(np.int32)+ask.astype(np.int32)
    delta=np.diff(mid2,prepend=mid2[0]).astype(np.int32)
    positive=(delta>0).astype(np.int8);negative=(delta<0).astype(np.int8)
    spread=ask-bid
    sp_delta=np.diff(spread,prepend=spread[0])
    signed=np.sign(delta).astype(np.int8)
    # Flip ignores zero-change quotes, to avoid false reversion counting.
    prev_nonzero=np.empty(len(signed),dtype=np.int8)
    current=0
    # vectorized propagation of last nonzero sign before each tick
    last_pos=np.maximum.accumulate(np.where(signed!=0,np.arange(len(signed),dtype=np.int32),-1))
    prev_pos=np.roll(last_pos,1);prev_pos[0]=-1
    prev_nonzero[:]=0
    mask=prev_pos>=0
    prev_nonzero[mask]=signed[prev_pos[mask]]
    flip=((signed*prev_nonzero)<0).astype(np.int8)
    arrays={
      'abs':np.abs(delta).astype(np.int32),
      'rv':np.square(delta.astype(np.float64)),
      'up':positive,
      'down':negative,
      'flip':flip,
      'widen':(sp_delta>0).astype(np.int8),
      'tighten':(sp_delta<0).astype(np.int8),
    }
    prefixes={k:np.cumsum(v,dtype=np.float64) for k,v in arrays.items()}
    return mid2,spread,prefixes

def completed_second_qaf(t, mid2, entry_times):
    """CMF-like close-location weighted by number of quote events. No trade volume.
    Only *completed seconds* strictly before each entry second are eligible.
    """
    secs=t//1000
    unique,first,counts=np.unique(secs,return_index=True,return_counts=True)
    highs=np.maximum.reduceat(mid2,first);lows=np.minimum.reduceat(mid2,first)
    close=mid2[first+counts-1]
    location=np.zeros(len(unique),dtype=np.float64)
    moved=highs>lows
    location[moved]=(2*close[moved]-highs[moved]-lows[moved])/(highs[moved]-lows[moved])
    weight=counts.astype(float)
    flow=np.cumsum(location*weight,dtype=float);activity=np.cumsum(weight,dtype=float)
    end_second=entry_times//1000
    result=np.full((len(entry_times),3),np.nan,dtype=np.float32)
    right=np.searchsorted(unique,end_second,side='left')-1 # only full earlier seconds
    for j,w in enumerate((5,15,60)):
        low=np.searchsorted(unique,end_second-w,side='left')-1
        has=(right>=0)&(right>low)
        v=np.zeros(len(right),dtype=float);d=np.ones(len(right),dtype=float)
        ri=right[has];li=low[has]
        # prefix values with -1 sentinel handled without indexing end as -1
        v[has]=flow[ri]-np.where(li>=0,flow[np.maximum(li,0)],0)
        d[has]=activity[ri]-np.where(li>=0,activity[np.maximum(li,0)],0)
        result[has,j]=(v[has]/np.maximum(d[has],1.)).astype('f')
    return result

def build_features(t,bid,ask,entry_ix):
    """Vectorized 7 exact event-time windows. At most entry_ix (even same-ms)."""
    et=t[entry_ix]
    n=len(entry_ix);out=np.zeros((n,len(FEATURE_NAMES)),dtype=np.float32)
    mid2,spread,pref=prefix_views(t,bid,ask)
    mids=np.zeros((n,len(WINDOWS_MS)),dtype=np.float32)
    abs5=None
    rv1=np.zeros(n,dtype=np.float32)
    for j,w in enumerate(WINDOWS_MS):
        lo=np.searchsorted(t,et-w,side='left'); lo=np.minimum(lo,entry_ix)
        valid=et-t[lo]>=min(w,2500) # history length availability; not feature mask
        count=(entry_ix-lo).astype(np.float64)
        net=(mid2[entry_ix]-mid2[lo]).astype(np.float64)/2.0
        sums={k:(v[entry_ix]-v[lo]) for k,v in pref.items()}
        gross=sums['abs']/2.0
        rv=np.sqrt(np.maximum(sums['rv'],0))/2.0
        signs=sums['up']+sums['down']
        tspan=np.maximum(et-t[lo],1)
        vals=[net,gross,np.abs(net)/(gross+1.e-6),rv,sums['flip']/(signs+1.0),count*1000.0/tspan]
        for k,z in enumerate(vals):out[:,j*6+k]=np.nan_to_num(z,nan=0.0,posinf=0.0).astype('f')
        flow=[sums['up']-sums['down'],(sums['up']-sums['down'])/(signs+1.0),
              (sums['widen']-sums['tighten'])/(count+1.0),np.log1p(count*1000./tspan)]
        for k,z in enumerate(flow):out[:,TREND_N+j*4+k]=z.astype('f')
        mids[:,j]=net.astype('f')
        if w==1000:rv1=rv.astype('f')
    # Multiscale trend-within-trend, must use observed history only.
    out[:,42]=np.sign(mids[:,1])*np.sign(mids[:,6])
    out[:,43]=mids[:,2]-mids[:,6]*(1000./60000.)
    out[:,44]=np.sign(mids[:,2])*np.sign(mids[:,4])
    out[:,45]=np.sign(mids[:,4])*np.sign(mids[:,6])
    out[:,TREND_N+28:TREND_N+31]=completed_second_qaf(t,mid2,et)
    # No 60-second history condition is deliberately not imputed to zero.
    no_60=(et-t[0]<60000)
    out[no_60,6*6:7*6]=np.nan
    out[no_60,TREND_N+6*4:TREND_N+7*4]=np.nan
    out[no_60,TREND_N+30]=np.nan
    return out,rv1,spread[entry_ix].astype('i')

def barriers(spread,rv1):
    """Predeclared spread/volatility adaptive counterfactual barriers, in cents.
    r=0 immediately if adverse spread consumed stop. G >= L for reward geometry.
    """
    spread=np.asarray(spread,dtype=float)
    rv1=np.asarray(rv1,dtype=float)
    stop=np.maximum.reduce([np.full_like(spread,30.),2.0*spread,1.5*rv1]).astype(np.int32)
    target=np.maximum(np.full(len(stop),50,dtype=np.int32),np.ceil(1.6*stop).astype(np.int32))
    return stop,target

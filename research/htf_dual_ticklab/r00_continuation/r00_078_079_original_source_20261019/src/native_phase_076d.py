"""R00-076D1 additive ORIGINAL-tick quote-duration and four lifecycle evidence.

ONLY observes broker quotes with original normalized UTC <= event time. Reuses the
UNMODIFIED R00-070 confirmed-pivot registry: a pivot is activated when its right
confirmation bar is COMPLETED, never when the pivot itself occurs.

This is a feature extractor for preexisting R00 events, NEVER an event generator.
Bid/ask quote changes are retail-dealer quotes, NOT executed order-flow volume.
"""
from __future__ import annotations
from pathlib import Path
from importlib.machinery import SourceFileLoader
from zipfile import ZipFile
import hashlib
import numpy as np
from numba import njit

DEP=Path(__file__).resolve().parent.parent/'original_dependencies'/'causal_pivot_registry.py'
PIV=SourceFileLoader('original_R00_070_confirmed_registry_076d',str(DEP)).load_module()

FIELDS = [
 'dt_last_ms','ewma_dt_fast_ms','ewma_dt_slow_ms','dt_fast_over_slow',
 'bid_count_1000ms','ask_count_1000ms','bid_count_5000ms','ask_count_5000ms',
 'bid_ask_signed_1000ms','bid_ask_signed_5000ms',
 'last_bid_response_ms','last_ask_response_ms','last_opposite_response_ms',
 'quote_burst_acceleration','spread_change_1000ms','mid_change_3000ms',
 'imp_side','imp_stage','imp_age_ms','imp_displacement',
 'ex_side','ex_stage','ex_age_ms','ex_reversal_displacement',
 'm15_sweep_high_phase','m15_sweep_low_phase','m15_latest_sweep_age_ms','m15_reclaim_age_ms',
 'h1_sweep_high_phase','h1_sweep_low_phase','h1_latest_sweep_age_ms','h1_reclaim_age_ms',
 'm15_pullback_side','m15_pullback_phase','m15_pullback_age_ms',
 'h1_pullback_side','h1_pullback_phase','h1_pullback_age_ms',
 'm15_published_topology','h1_published_topology',
 'm15_known_pivot_age_ms','h1_known_pivot_age_ms',
]

def published_pivots(t, bid, ask):
    """Call exact R00-070 pivot-confirmation logic on observed completed bars.

    No synthetic missing bars and no future publication is available to _stream.
    """
    mid=(bid+ask)*.5
    events=[]
    for tf,period in [(0,900000),(1,3600000)]:
        gid=t//period
        first=np.r_[0,np.flatnonzero(np.diff(gid)!=0)+1]
        last=np.r_[first[1:],len(t)]
        high=np.maximum.reduceat(mid,first)
        low=np.minimum.reduceat(mid,first)
        close=mid[last-1]
        bars=[PIV.CompleteBar(int(gid[first[k]]*period),int((gid[first[k]]+1)*period),float(high[k]),float(low[k]),float(close[k])) for k in range(len(first))]
        piv=PIV.confirm_pivots(bars,left=2,right=2)
        for p in piv:
            events.append((int(p.publicly_known_utc_ms),tf,1 if p.kind=='HIGH' else -1,float(p.level)))
    events.sort(key=lambda x:(x[0],x[1],x[2]))
    if not events:
        return np.empty(0,np.int64),np.empty(0,np.int8),np.empty(0,np.int8),np.empty(0,np.float64)
    a=np.array(events,dtype=[('t','i8'),('tf','i1'),('kind','i1'),('level','f8')])
    return a['t'].copy(),a['tf'].copy(),a['kind'].copy(),a['level'].copy()

@njit(cache=True)
def _stream(t,bid,ask,j,pub_t,pub_tf,pub_kind,pub_lvl):
    n=len(t);ne=len(j)
    out=np.empty((ne,42),dtype=np.float32)
    cb=np.zeros(n,dtype=np.int32);ca=np.zeros(n,dtype=np.int32)
    sb=np.zeros(n,dtype=np.int32);sa=np.zeros(n,dtype=np.int32)
    qev=0;p1=0;p5=0;p3=0;pk=0
    fast=1000.;slow=1000.;lastb=-1;lasta=-1;lastop=-1
    imp_side=0;imp_stage=0;imp_t=0;imp_price=0.
    ex_side=0;ex_stage=0;ex_t=0;ex_price=0.
    high=np.empty(2,dtype=np.float64);low=np.empty(2,dtype=np.float64)
    prevh=np.empty(2,dtype=np.float64);prevl=np.empty(2,dtype=np.float64)
    high[:]=np.nan;low[:]=np.nan;prevh[:]=np.nan;prevl[:]=np.nan
    pubage=np.zeros(2,dtype=np.int64)
    high_phase=np.zeros(2,dtype=np.int8);low_phase=np.zeros(2,dtype=np.int8)
    high_sweep_t=np.zeros(2,dtype=np.int64);low_sweep_t=np.zeros(2,dtype=np.int64)
    high_reclaim_t=np.zeros(2,dtype=np.int64);low_reclaim_t=np.zeros(2,dtype=np.int64)
    pb_side=np.zeros(2,dtype=np.int8);pb_phase=np.zeros(2,dtype=np.int8)
    pb_t=np.zeros(2,dtype=np.int64);pb_price=np.zeros(2,dtype=np.float64)
    topology=np.zeros(2,dtype=np.int8)
    for i in range(n):
        now=t[i];mid=(bid[i]+ask[i])*.5
        dt=0
        if i:
            dt=max(0,now-t[i-1]);d_b=bid[i]-bid[i-1];d_a=ask[i]-ask[i-1]
            fast=.87*fast+.13*min(dt,20000)
            slow=.995*slow+.005*min(dt,20000)
            bc=abs(d_b)>.0007;ac=abs(d_a)>.0007
            cb[i]=cb[i-1]+(1 if bc else 0)
            ca[i]=ca[i-1]+(1 if ac else 0)
            sb[i]=sb[i-1]+(1 if d_b>.0007 else (-1 if d_b<-.0007 else 0))
            sa[i]=sa[i-1]+(1 if d_a>.0007 else (-1 if d_a<-.0007 else 0))
            if bc:
                if lasta>=0:lastop=now-lasta
                lastb=now
            if ac:
                if lastb>=0:lastop=now-lastb
                lasta=now
        else:
            cb[i]=0;ca[i]=0;sb[i]=0;sa[i]=0
        while p1<i and t[p1]<now-1000:p1+=1
        while p5<i and t[p5]<now-5000:p5+=1
        while p3<i and t[p3]<now-3000:p3+=1
        # Public pivots only activated at/after completed right-side bar publication.
        while pk<len(pub_t) and pub_t[pk]<=now:
            tf=pub_tf[pk];v=pub_lvl[pk]
            pubage[tf]=now
            if pub_kind[pk]>0:
                prevh[tf]=high[tf];high[tf]=v;high_phase[tf]=0
            else:
                prevl[tf]=low[tf];low[tf]=v;low_phase[tf]=0
            if np.isfinite(prevh[tf]) and np.isfinite(prevl[tf]):
                if high[tf]>prevh[tf] and low[tf]>prevl[tf]:topology[tf]=1
                elif high[tf]<prevh[tf] and low[tf]<prevl[tf]:topology[tf]=-1
                else:topology[tf]=0
            pk+=1
        # Independent IMPULSE finite-state stage, at every tick.
        n1=i-p1
        d1=mid-(bid[p1]+ask[p1])*.5
        if imp_side and (now-imp_t>6000 or (mid-imp_price)*imp_side<-.15):
            imp_side=0;imp_stage=0
        if imp_side==0 and n1>=5 and abs(d1)>.22:
            imp_side=1 if d1>0 else -1;imp_t=now;imp_price=mid;imp_stage=1
        elif imp_side and imp_stage==1 and now>imp_t and (mid-imp_price)*imp_side>.11:
            imp_stage=2
        # Independent EXHAUSTION: only a witnessed earlier impulse can arm it.
        if ex_side and (now-ex_t>20000 or (mid-ex_price)*ex_side<-.12):
            ex_side=0;ex_stage=0
        if ex_side==0 and imp_stage==2 and (mid-imp_price)*imp_side<-.07:
            ex_side=-imp_side;ex_stage=1;ex_t=now;ex_price=mid
        elif ex_side and ex_stage==1 and (mid-ex_price)*ex_side>.06:
            ex_stage=2
        # Per-tick HTF sweep -> reclaim -> retest phase, independent timeframes.
        for tf in range(2):
            if high_phase[tf] and now-high_sweep_t[tf]>60000:high_phase[tf]=0
            if low_phase[tf] and now-low_sweep_t[tf]>60000:low_phase[tf]=0
            if np.isfinite(high[tf]):
                if high_phase[tf]==0 and mid>high[tf]+.03:
                    high_phase[tf]=1;high_sweep_t[tf]=now
                elif high_phase[tf]==1 and mid<high[tf]-.02:
                    high_phase[tf]=2;high_reclaim_t[tf]=now
                elif high_phase[tf]==2 and now>high_reclaim_t[tf] and mid>=high[tf]-.02 and mid<=high[tf]+.05:
                    high_phase[tf]=3
            if np.isfinite(low[tf]):
                if low_phase[tf]==0 and mid<low[tf]-.03:
                    low_phase[tf]=1;low_sweep_t[tf]=now
                elif low_phase[tf]==1 and mid>low[tf]+.02:
                    low_phase[tf]=2;low_reclaim_t[tf]=now
                elif low_phase[tf]==2 and now>low_reclaim_t[tf] and mid<=low[tf]+.02 and mid>=low[tf]-.05:
                    low_phase[tf]=3
            # Independent structural PULLBACK retracement -> re-impulse.
            if pb_side[tf] and (now-pb_t[tf]>90000 or topology[tf]!=pb_side[tf]):
                pb_side[tf]=0;pb_phase[tf]=0
            if pb_side[tf]==0 and topology[tf]!=0 and n1>0 and d1*topology[tf]<-.18:
                pb_side[tf]=topology[tf];pb_t[tf]=now;pb_price[tf]=mid;pb_phase[tf]=1
            elif pb_side[tf] and pb_phase[tf]==1 and (mid-pb_price[tf])*pb_side[tf]>.12:
                pb_phase[tf]=2
        while qev<ne and j[qev]==i:
            z=out[qev]
            z[0]=dt;z[1]=fast;z[2]=slow;z[3]=fast/max(slow,1.)
            z[4]=cb[i]-(cb[p1-1] if p1>0 else 0)
            z[5]=ca[i]-(ca[p1-1] if p1>0 else 0)
            z[6]=cb[i]-(cb[p5-1] if p5>0 else 0)
            z[7]=ca[i]-(ca[p5-1] if p5>0 else 0)
            z[8]=(sb[i]-(sb[p1-1] if p1>0 else 0))-(sa[i]-(sa[p1-1] if p1>0 else 0))
            z[9]=(sb[i]-(sb[p5-1] if p5>0 else 0))-(sa[i]-(sa[p5-1] if p5>0 else 0))
            z[10]=min(60000,now-lastb) if lastb>=0 else -1
            z[11]=min(60000,now-lasta) if lasta>=0 else -1
            z[12]=lastop if lastop>=0 else -1
            z[13]=z[6]/5.-z[4]
            z[14]=(ask[i]-bid[i])-(ask[p1]-bid[p1])
            z[15]=mid-(bid[p3]+ask[p3])*.5
            z[16]=imp_side;z[17]=imp_stage;z[18]=min(120000,now-imp_t) if imp_side else -1
            z[19]=(mid-imp_price)*imp_side if imp_side else 0
            z[20]=ex_side;z[21]=ex_stage;z[22]=min(120000,now-ex_t) if ex_side else -1
            z[23]=(mid-ex_price)*ex_side if ex_side else 0
            for tf in range(2):
                k=24+4*tf
                z[k]=high_phase[tf];z[k+1]=low_phase[tf]
                z[k+2]=min(60000,now-max(high_sweep_t[tf],low_sweep_t[tf])) if high_phase[tf] or low_phase[tf] else -1
                ret=max(high_reclaim_t[tf] if high_phase[tf]>=2 else 0,low_reclaim_t[tf] if low_phase[tf]>=2 else 0)
                z[k+3]=min(60000,now-ret) if ret else -1
                k=32+3*tf
                z[k]=pb_side[tf];z[k+1]=pb_phase[tf]
                z[k+2]=min(90000,now-pb_t[tf]) if pb_side[tf] else -1
                z[38+tf]=topology[tf]
                z[40+tf]=min(86400000,now-pubage[tf]) if pubage[tf] else -1
            qev+=1
    if qev!=ne:raise ValueError('missing protected original quote-index in current source stream')
    return out


def extract(t,bid,ask,j):
    t=np.asarray(t,dtype=np.int64);bid=np.asarray(bid,dtype=np.float64);ask=np.asarray(ask,dtype=np.float64)
    j=np.asarray(j,dtype=np.int64)
    if not len(t) or len(j)==0 or len(bid)!=len(t) or len(ask)!=len(t) or np.any(np.diff(t)<0) or np.any(np.diff(j)<0):
        raise ValueError('invalid original quote/event schema or chronology')
    if np.any(j<0) or np.any(j>=len(t)) or np.any(ask<bid):
        raise ValueError('invalid original quote index or negative spread')
    pub=published_pivots(t,bid,ask)
    out=_stream(t,bid,ask,j,*pub)
    assert out.shape==(len(j),len(FIELDS)) and np.isfinite(out).all()
    return out,pub

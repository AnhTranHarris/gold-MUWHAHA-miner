"""R6 source-ordinal as-of XAUUSD quote-arrival surprise and ordinal burst survival.

Input is raw source t,bid,ask and original candidate row ix. No post-decision
samples, quote-window last-tick knowledge, future first-hit or teacher net in X.
The time-gap and price variation features are *observed quote* statistics, not
actual order-flow, queue position or filled order events.
"""
from __future__ import annotations
import numpy as np
from numba import njit

DEPTHS=(8,32,128,512)
SINGLES=('last_gap_ms','gap_ratio_last8_to32','gap_ratio_last32_to128','bid_ask_spread','spread_jump_last8','last_mid_change','last_mid_change_per_gap','has_same_ms_prior')
BLOCK=('n_observed','elapsed_ms','quote_rate_per_s','mean_gap_ms','gap_cv','net_mid_trend','path_abs','path_efficiency','price_range','up_revisions','down_revisions','synchronous_revisions','asynchronous_revisions','bid_lead_pressure','mean_spread','spread_instability','swing_terminal_position','run_direction')
NAMES=tuple(SINGLES)+tuple(f'd{d}_{k}' for d in DEPTHS for k in BLOCK)

@njit(cache=True)
def _compute(t,b,a,ix):
    out=np.empty((len(ix),len(NAMES)),np.float32)
    for q in range(len(ix)):
        i=ix[q]; now=t[i]; m=(b[i]+a[i])*.5
        lastgap=max(0,t[i]-t[i-1]) if i else 0.
        g8=max(float(t[i]-t[max(0,i-8)]),1.)
        g32=max(float(t[i]-t[max(0,i-32)]),1.)
        g128=max(float(t[i]-t[max(0,i-128)]),1.)
        out[q,0]=lastgap
        out[q,1]=g8/g32
        out[q,2]=g32/g128
        out[q,3]=a[i]-b[i]
        out[q,4]=(a[i]-b[i])-(a[max(i-8,0)]-b[max(i-8,0)])
        prevm=(b[i-1]+a[i-1])*.5 if i else m
        out[q,5]=m-prevm
        out[q,6]=(m-prevm)/(1.+lastgap)
        out[q,7]=1. if i and t[i]==t[i-1] else 0.
        for z in range(len(DEPTHS)):
            d=DEPTHS[z];start=max(0,i-d);n=i-start
            age=max(float(t[i]-t[start]),1.)
            start_mid=(b[start]+a[start])*.5
            vabs=0.;high=start_mid;low=start_mid;pos=0.;neg=0.
            synchronous=0.;asynchronous=0.;bidlead=0.
            midprev=start_mid;spread_total=0.;spread_abs=0.;gap_sum=0.;gap_sq=0.
            lastsign=0.;run=0.
            for j in range(start+1,i+1):
                cur=(b[j]+a[j])*.5
                if cur>high:high=cur
                if cur<low:low=cur
                inc=cur-midprev;vabs+=abs(inc);midprev=cur
                if inc>1e-9:pos+=1
                elif inc<-1e-9:neg+=1
                sign=1. if inc>1e-9 else (-1. if inc<-1e-9 else 0.)
                if sign and sign==lastsign:run+=sign
                elif sign:run=sign
                if sign:lastsign=sign
                db=b[j]-b[j-1];da=a[j]-a[j-1]
                cb=abs(db)>1e-9;ca=abs(da)>1e-9
                if cb and ca:synchronous+=1.
                elif cb or ca:asynchronous+=1.
                if cb and not ca:bidlead+=1.
                elif ca and not cb:bidlead-=1.
                spread=a[j]-b[j];oldspread=a[j-1]-b[j-1]
                spread_total+=spread;spread_abs+=abs(spread-oldspread)
                gap=float(t[j]-t[j-1]);gap_sum+=gap;gap_sq+=gap*gap
            mean_gap=gap_sum/max(n,1);variance=max(0.,gap_sq/max(n,1)-mean_gap*mean_gap)
            off=len(SINGLES)+z*len(BLOCK)
            out[q,off+0]=n
            out[q,off+1]=age
            out[q,off+2]=1000.*n/age
            out[q,off+3]=mean_gap
            out[q,off+4]=(variance**.5)/max(1.,mean_gap)
            out[q,off+5]=m-start_mid
            out[q,off+6]=vabs
            out[q,off+7]=abs(m-start_mid)/(vabs+1e-9)
            out[q,off+8]=high-low
            out[q,off+9]=pos
            out[q,off+10]=neg
            out[q,off+11]=synchronous
            out[q,off+12]=asynchronous
            out[q,off+13]=bidlead
            out[q,off+14]=spread_total/max(n,1)
            out[q,off+15]=spread_abs/max(n,1)
            out[q,off+16]=(m-low)/(high-low+1e-9)
            out[q,off+17]=run
    return out

def extract(t,b,a,ix):
    t=np.asarray(t,np.int64);b=np.asarray(b,np.float64);a=np.asarray(a,np.float64);ix=np.asarray(ix,np.int64)
    if not(np.all(t[1:]>=t[:-1]) and np.all((ix>=0)&(ix<len(t))) and np.all(a>=b)):raise ValueError('bad raw quote/ordinal input')
    z=_compute(t,b,a,ix)
    if not(np.all(np.isfinite(z)) and z.shape==(len(ix),len(NAMES))):raise ValueError('nonfinite as-of survival features')
    return z

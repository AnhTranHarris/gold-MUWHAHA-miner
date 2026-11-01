"""Strictly prior-to-T1 native quote-mark evidence; no label, teacher, or parent model."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

MARK_NAMES=("signed_net","signed_last_1s","signed_last_5s","signed_last_15s",
  "path_efficiency","quote_tortuosity","return_variance","quote_count_log",
  "updates_per_dollar","spread_mean","spread_now","spread_growth",
  "bid_ask_divergence","spread_widen_rate","up_down_entropy",
  "same_direction_run","revision_reversal_rate","arrival_cv",
  "arrival_median_ms","quote_age_ms","activity_1s","activity_5s",
  "activity_15s","activity_1s_vs_5s","directional_energy_per_quote",
  "signed_early_vs_late","max_favorable","max_adverse","terminal_giveback",
  "positive_revision_fraction","stale_fraction","side_broker_independent")

@dataclass(frozen=True)
class NativePrefix:
    t0_ms:int
    t1_ms:int
    side:int
    quote_count:int
    features:np.ndarray
    last_quote_ms:int


def build_prefix(t_ms:np.ndarray,bid:np.ndarray,ask:np.ndarray,
                 *,t0_ms:int,t1_ms:int,side:int)->NativePrefix:
    """Only uses actual native quotes with timestamp < t1; decision quote excluded.
    The caller must independently certify original event and true T1 from the source.
    """
    if side not in (-1,1) or not t0_ms+15000<=t1_ms<t0_ms+16000:
        raise ValueError('T1/side invalid')
    t=np.asarray(t_ms,dtype=np.int64);b=np.asarray(bid,dtype=np.int64);a=np.asarray(ask,dtype=np.int64)
    if not(t.ndim==b.ndim==a.ndim==1 and 2<=len(t)==len(b)==len(a)):
        raise ValueError('native quote vectors invalid')
    if np.any(np.diff(t)<0) or np.any(b<=0) or np.any(a<=b):
        raise ValueError('unsorted or invalid quote values')
    lo=np.searchsorted(t,t0_ms,side='left');hi=np.searchsorted(t,t1_ms,side='left')
    if hi-lo<3:raise ValueError('insufficient predecision genuine quotes')
    # recent prefix [t0,t1), quote at t1 deliberately unobservable to scorer.
    t=t[lo:hi];b=b[lo:hi].astype(np.float64);a=a[lo:hi].astype(np.float64)
    if t[-1]>=t1_ms:raise ValueError('lookahead quote')
    mid=(b+a)/2000.;spread=(a-b)/1000.; ret=np.diff(mid);abs_ret=np.abs(ret)
    signed=(mid-mid[0])*side;dx=ret*side
    positive=np.sum(dx>0);negative=np.sum(dx<0);zero=np.sum(dx==0)
    d=np.diff(t).astype(float);dt=np.maximum(d,0.)
    seconds=max((t[-1]-t[0])/1000.,1.e-3)
    count=len(t)
    def last_ms(w):
        j=np.searchsorted(t,t1_ms-w,side='left')
        return float((mid[-1]-mid[min(j,len(t)-1)])*side)
    def activity(w):return float((t>=t1_ms-w).sum())
    path=float(abs_ret.sum());net=float(signed[-1]);mid_range=float(np.ptp(mid))
    sg=np.sign(dx);nonzero=sg[sg!=0]
    reversals=int(np.count_nonzero(np.diff(nonzero)!=0)) if len(nonzero)>1 else 0
    p=(np.array([positive,negative,zero])+0.5)/(len(dx)+1.5)
    entropy=float(-np.dot(p,np.log(p))/np.log(3))
    same_run=1
    if len(nonzero):
        for q in nonzero[-2::-1]:
            if q==nonzero[-1]:same_run+=1
            else:break
    widen=np.diff(spread)>0
    bd=np.diff(b);ad=np.diff(a)
    early=np.searchsorted(t,t0_ms+7500,side='left')
    early_ret=(mid[min(early,len(t)-1)]-mid[0])*side
    late_ret=net-early_ret
    energy=path/(len(dx)+1e-9)
    fresh=dt[np.isfinite(dt)]
    data=np.array([
     net,last_ms(1000),last_ms(5000),last_ms(15000),abs(net)/(path+1e-9),path/(abs(net)+.01),
     np.var(ret),np.log1p(count),len(dx)/(path+0.10),np.mean(spread),spread[-1],spread[-1]-spread[0],
     float(np.mean((bd*ad)<0)),float(np.mean(widen)),entropy,float(same_run)/len(dx),
     reversals/max(1,len(nonzero)-1),float(np.std(fresh)/(np.mean(fresh)+1)) if len(fresh) else 0.,
     float(np.median(fresh)) if len(fresh) else 0.,float(t1_ms-t[-1]),
     activity(1000),activity(5000),activity(15000),activity(1000)/(activity(5000)+1),
     net/(len(dx)+1),float(early_ret-late_ret),float(np.max(signed)),float(np.min(signed)),
     float(np.max(signed)-net),positive/(len(dx)+1),
     float(np.mean(dt>1000)) if len(dt) else 0.,float(side)
    ],dtype=np.float32)
    assert len(data)==len(MARK_NAMES)==32 and np.isfinite(data).all()
    data.setflags(write=False)
    return NativePrefix(int(t0_ms),int(t1_ms),int(side),count,data,int(t[-1]))

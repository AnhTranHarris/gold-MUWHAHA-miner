"""R150B frozen-source prefix-only marked-quote state.

New unsubmitted-intent decision = first native quote in [t0+15000,t0+16000).
Only source quotes with timestamps STRICTLY LESS than this exact quote are read.
Source data and original event ordinals remain immutable. No class, fitted
teacher or current t+30..32 outcome is accepted by event-time builder.
"""
from __future__ import annotations
import numpy as np

FEATURES=(
 'p32_side_mid_displacement_spreadz','p32_quote_efficiency','p32_signed_revision_imbalance',
 'p32_bid_only_rate','p32_ask_only_rate','p32_both_rate','p32_spread_open_rate',
 'p32_spread_close_rate','p32_spread_mean_log','p32_spread_std_log',
 'p32_interarrival_logmean','p32_interarrival_logstd','p32_interarrival_burstiness',
 'p32_mid_reversal_rate','p32_side_run_signed','p32_signed_bidflow_spread',
 'p32_signed_askflow_spread','p32_spread_delta_norm','p32_signed_flow_recent_vs_prior',
 'p32_interval_recent_vs_prior','p32_exp_excitation_bid','p32_exp_excitation_ask',
 'p32_exp_excitation_spread_open','p32_shannon_mark_entropy',
 'p32_leadlag_spread_mid','p32_leadlag_bid_ask','p32_path_turn_area',
 'p32_net_vs_gross_spread','p32_time_coverage_log','p32_signed_firsthalf_vs_secondhalf',
 'p32_spread_wide_tail','p32_mid_zero_fraction',
)

def causal_marks(t:np.ndarray,bid:np.ndarray,ask:np.ndarray,decision:np.ndarray,
                 side:np.ndarray,events:int=32)->tuple[np.ndarray,np.ndarray]:
 """Source quotes are sorted and the first same-ms event is also excluded.

 No orders/truth/teacher predictions enter this function. Time array is UTC ms,
 integer bid/ask source-native 0.001 units.
 """
 assert events==32
 n=len(decision); out=np.zeros((n,len(FEATURES)),np.float32)
 if n==0:return out,np.empty(0,bool)
 # searchsorted left excludes ALL same-timestamp quotes, even if an earlier ordinal
 prior=np.searchsorted(t,decision,side='left')
 valid=(prior>=events+1)&(np.asarray(side)!=0)
 good=np.flatnonzero(valid)
 for start in range(0,len(good),12000):
  k=good[start:start+12000]; ix=prior[k,None]-np.arange(events,0,-1,dtype=np.int64)[None,:]
  tt=t[ix].astype(np.float64); bb=bid[ix].astype(np.float64);aa=ask[ix].astype(np.float64)
  spr=np.maximum(aa-bb,1); mid=(bb+aa)/2
  db=np.diff(bb,axis=1); da=np.diff(aa,axis=1); dm=np.diff(mid,axis=1); ds=np.diff(spr,axis=1)
  dt=np.maximum(np.diff(tt,axis=1),1.); ss=side[k,None].astype(np.float64)
  absflow=np.sum(np.abs(dm),axis=1)+1e-5;midmove=(mid[:,-1]-mid[:,0])*side[k]
  avgspread=np.maximum(np.mean(spr,axis=1),1.)
  sign=np.sign(dm); changes=(sign[:,1:]*sign[:,:-1]<0).mean(axis=1)
  bidonly=(db!=0)&(da==0);askonly=(da!=0)&(db==0);both=(da!=0)&(db!=0)
  widen=ds>0;close=ds<0
  sflow=ss*dm
  rsign=np.sign(sflow)
  # Exact contiguous signed-revision run ending at the latest update.
  # Stop at the first prior sign mismatch; do NOT count older disjoint runs.
  runs=np.cumprod((rsign[:,::-1]==rsign[:,-1,None]),axis=1).sum(axis=1)
  nmarks=np.column_stack([bidonly.sum(axis=1),askonly.sum(axis=1),both.sum(axis=1),((db==0)&(da==0)).sum(axis=1)]).astype(float)
  q=nmarks/np.maximum(nmarks.sum(axis=1,keepdims=True),1)
  entropy=-np.sum(np.where(q>0,q*np.log(q+1e-9),0),axis=1)
  # Finite causal exponentially decayed intensity (a mark-count Hawkes-inspired
  # state, NOT a fitted Hawkes stochastic intensity).
  elapsed=(tt[:,-1,None]-tt[:,1:])/1000.
  expweight=np.exp(-np.clip(elapsed,0.,60.)/2.5)
  bidexc=np.sum((db!=0)*expweight,axis=1);askexc=np.sum((da!=0)*expweight,axis=1)
  spexc=np.sum(widen*expweight,axis=1)
  lead1=np.sum((ds[:,:-1]/avgspread[:,None])* (sflow[:,1:]/avgspread[:,None]),axis=1)/30
  lead2=np.sum((db[:,:-1]/avgspread[:,None])*(da[:,1:]/avgspread[:,None])-(da[:,:-1]/avgspread[:,None])*(db[:,1:]/avgspread[:,None]),axis=1)/30
  area=np.sum(((mid[:,1:-1]-mid[:,:-2])/avgspread[:,None])*(ds[:,1:]/avgspread[:,None])-((mid[:,2:]-mid[:,1:-1])/avgspread[:,None])*(ds[:,:-1]/avgspread[:,None]),axis=1)/30
  first=np.mean(sflow[:,:15],axis=1);second=np.mean(sflow[:,16:],axis=1)
  mean_dt=dt.mean(axis=1);std_dt=dt.std(axis=1)
  x=np.column_stack([
   midmove/avgspread,midmove/absflow,np.sum(sflow,axis=1)/absflow,
   bidonly.mean(axis=1),askonly.mean(axis=1),both.mean(axis=1),
   widen.mean(axis=1),close.mean(axis=1),np.log1p(avgspread),
   np.log1p(spr.std(axis=1)),np.log1p(mean_dt),np.log1p(std_dt),std_dt/(mean_dt+1e-3),
   changes,rsign[:,-1]*runs/31.,np.sum(ss*db,axis=1)/avgspread,
   np.sum(ss*da,axis=1)/avgspread,(spr[:,-1]-spr[:,0])/avgspread,
   (np.mean(sflow[:,16:],axis=1)-np.mean(sflow[:,:15],axis=1))/avgspread,
   np.log1p(np.mean(dt[:,16:],axis=1))-np.log1p(np.mean(dt[:,:15],axis=1)),
   bidexc,askexc,spexc,entropy,lead1,lead2,area,
   np.sum(np.abs(ds),axis=1)/np.maximum(np.abs(spr[:,-1]-spr[:,0]),1.),
   np.log1p((tt[:,-1]-tt[:,0])/1000.),(second-first)/avgspread,
   (spr[:,-1]>np.quantile(spr,.75,axis=1)).astype(float),
   (dm==0).mean(axis=1)
  ])
  out[k]=np.nan_to_num(np.clip(x,-1e4,1e4),nan=0.0,posinf=0.,neginf=0.).astype(np.float32)
 return out,valid


def get_native_decision(t:np.ndarray,event_t:np.ndarray)->tuple[np.ndarray,np.ndarray]:
 first=np.searchsorted(t,event_t+15000,side='left');safe=np.minimum(first,len(t)-1)
 tm=t[safe];good=(first<len(t))&(tm>=event_t+15000)&(tm<event_t+16000)
 return np.where(good,tm,event_t+15000),good

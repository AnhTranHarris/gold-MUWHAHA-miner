#!/usr/bin/env python3
"""Strictly published M1/M5/M15/H1 OHLC/grid-trend bridge for R120 geometry.

Using source-native UTC milliseconds, every event aligns to completed bar only:
`np.searchsorted(observed_bucket, t0 // width, 'left') - 1`.
HTF bars are source-time derived, never synthetic fill-forward; no future tick
can enter the event feature.  Volume metrics are quoted size only, NOT trades.
"""
import pathlib,json,sys,gc,argparse
import numpy as np
import pandas as pd
from r120_multiclock_geometry import PIN,ROOT,FEATURES,load_source,sha256
HTF_WIDTH={'M1':60000,'M5':300000,'M15':900000,'H1':3600000}
FIELDS=['trend4','trend8','acceleration','efficiency','support_rank','grid_quartile_distance','range_log','quote_count_log','closed_bar_age']

def _finite(a):
 a=np.asarray(a,dtype=np.float32)
 return np.nan_to_num(a,copy=False,nan=0.0,posinf=0.0,neginf=0.0)

def make_macro_native(t,bid,ask,original_t,side):
 assert np.all(t[:-1]<=t[1:]) and np.all(original_t[:-1]<=original_t[1:])
 mid=(bid.astype(np.float64)+ask.astype(np.float64))*.5
 bars_all=[];by_w={};names=[]
 for lab,width in HTF_WIDTH.items():
  bucket=t//width
  ix=np.flatnonzero(np.r_[True, bucket[1:]!=bucket[:-1]])
  starts=bucket[ix]
  ends=np.r_[ix[1:],len(bucket)]-1
  open_=mid[ix];close=mid[ends]
  # Dynamic high-low / quote activity from every tick in each completed timeframe bar.
  high=np.maximum.reduceat(mid,ix)
  low=np.minimum.reduceat(mid,ix)
  count=ends-ix+1
  # At event t0, bucket floor(t0/w) is NOT complete.  Choose only prior bucket.
  qid=original_t//width
  pos=np.searchsorted(starts,qid,side='left')-1
  have=pos>=0
  safe=np.maximum(pos,0)
  n=len(original_t);x=np.zeros((n,len(FIELDS)),dtype=np.float32)
  p4=np.maximum(safe-4,0);p8=np.maximum(safe-8,0)
  # Backward-only rolling of source-published HIGH/LOW and absolute close variation.
  upper=pd.Series(high).rolling(16,min_periods=1).max().to_numpy()
  lower=pd.Series(low).rolling(16,min_periods=1).min().to_numpy()
  # Crucially: rolling ranges at each bar use no *later* published bar.
  rng=np.maximum(upper[safe]-lower[safe],1.0)
  p0=close[safe];c4=close[p4];c8=close[p8]
  sgn=side.astype(np.float64)
  x[:,0]=_finite(sgn*(p0-c4)/rng)
  x[:,1]=_finite(sgn*(p0-c8)/rng)
  x[:,2]=_finite(sgn*(p0-2*c4+c8)/rng)
  # A ratio of net displacement to cumulative absolute completed bar-close movement.
  step_abs=np.r_[0,np.abs(np.diff(close))];cum_abs=np.cumsum(step_abs)
  route=cum_abs[safe]-cum_abs[p8]
  x[:,3]=_finite(np.abs(p0-c8)/(route+1.))
  rank=np.where(side>0,(p0-lower[safe])/rng,(upper[safe]-p0)/rng)
  x[:,4]=_finite(rank)
  x[:,5]=_finite(np.abs(4*rank-np.round(4*rank)))
  x[:,6]=_finite(np.log1p(rng))
  x[:,7]=_finite(np.log1p(count[safe]))
  x[:,8]=_finite(np.minimum((original_t-(starts[safe]+1)*width)/width,1e6))
  # Current partial HTF is not exposed; completed bars only.
  x[~have]=0
  by_w[lab]={'ticks':len(t),'bars':len(starts),'with_completed':int(have.sum()),'interval_ms':width}
  bars_all.append(x);names.extend([lab+'_'+f for f in FIELDS])
 return np.concatenate(bars_all,axis=1),names,by_w

def main():
 pa=argparse.ArgumentParser();pa.add_argument('--months',nargs='+',default=['01']);args=pa.parse_args()
 for m in args.months:
  src,orig=load_source(m)
  Xt,cols,meta=make_macro_native(src[0],src[1],src[2],orig['t'],orig['side'])
  assert len(Xt)==len(orig['t']) and np.isfinite(Xt).all()
  dest=ROOT/f'R120_{m}_COMPLETED_HTF_BRIDGE.npy';np.save(dest,Xt)
  meta={'month':m,'n_original':len(orig['t']),'features':cols,'bar_meta':meta,'sha256':sha256(dest),
  'contract':'All HTF buckets strictly < floor(t0 / width) and only raw quote ticks inside source-published bucket. No DST exchange calendar; no interpolation/synthetic bars.'}
  (ROOT/f'R120_{m}_HTF_RECEIPT.json').write_text(json.dumps(meta,indent=2))
  print('HTF',m, Xt.shape, 'SHA',meta['sha256'],flush=True)
  del src,orig,Xt;gc.collect()
if __name__=='__main__':main()
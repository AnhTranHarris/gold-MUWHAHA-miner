#!/usr/bin/env python3
"""F39 NEW causal ordered bid/ask last-64 ORIGINAL raw tick feature cache.
NOT a byte-identical reconstruction of missing FILTER05; separate 30-column design.
Coinexx clock -2h JanFeb / -3h JunJul; Dukascopy native UTC; first raw source quote at event ms;
all current+prior quotes only. No trading P&L or inference-time future-label input.
"""
from __future__ import annotations
import hashlib,io,json,time,zipfile,sys
from pathlib import Path
import numpy as np,pandas as pd
from numba import njit
ROOT=Path('/mnt/data');HERE=ROOT/'R00_054_F39_NATIVE_QUOTE_SEQUENCE_20261020';HERE.mkdir(exist_ok=True)
SOURCE=ROOT/'XAUUSD_R00_054_SEVEN_MONTH_PORTABLE_RESEARCH_20261019.zip'
KEYS={'coinexx':lambda m:f'XAUUSD_MT5_BROKER_2026_{m}_ticks_ALL.csv.gz','dukascopy':lambda m:f'XAUUSD_DUKAS_2026_{m}_ticks.csv.gz'}
FEATURE_NAMES=('bid_only_share_64','ask_only_share_64','joint_share_64','bid_stale_age_s','ask_stale_age_s',
 'side_mid_impulse_64','side_bid_impulse_64','side_ask_impulse_64','side_mid_impulse_8',
 'side_bid_impulse_8','side_ask_impulse_8','side_tick_imbalance_64','side_tick_imbalance_8',
 'quote_rate_64','interquote_mean_gap_ms_64','interquote_max_gap_ms_64','spread_at_event',
 'spread_mean_64','spread_range_64','spread_change_64','spread_change_8','mid_turn_share_64',
 'mid_turn_share_8','path_efficiency_64','path_efficiency_8','bid_ask_direction_disagreement_8',
 'unchanged_quote_share_64','one_sided_skew_64','side_spread_change_64','previous_quote_gap_ms')
@njit(cache=True)
def build(t,bid,ask,idx,side):
 n=len(idx);X=np.zeros((n,30),dtype=np.float32);tiny=1.e-7
 for j in range(n):
  k=idx[j]
  if k==0:
   # First source quote has no prior tick; do not borrow a future observation.
   X[j,3]=1000.;X[j,4]=1000.;X[j,16]=ask[0]-bid[0]
   X[j,17]=X[j,16];X[j,29]=1000000.
   continue
  start=max(1,k-63);start8=max(1,k-7)
  mid_now=(bid[k]+ask[k])*.5
  mid_prev=(bid[max(0,start-1)]+ask[max(0,start-1)])*.5
  sidej=side[j]
  bon=0;aon=0;joint=0;un=0;turns=0;turns8=0;prev_sign=0;prev8_sign=0
  imb=0;imb8=0;vol=0.;vol8=0.;spread_sum=0.;spmax=-1e9;spmin=1e9
  spread_init=ask[start-1]-bid[start-1]
  intermax=0.;intertot=0.;bidlast=-1;asklast=-1;tick8_b=0.;tick8_a=0.
  start_sp8=ask[start8-1]-bid[start8-1]
  for q in range(start,k+1):
   db=bid[q]-bid[q-1];da=ask[q]-ask[q-1]
   ub=abs(db)>tiny;ua=abs(da)>tiny
   if ub and ua:joint+=1
   elif ub:bon+=1
   elif ua:aon+=1
   else:un+=1
   if ub:bidlast=q
   if ua:asklast=q
   dm=(db+da)*.5
   sgn=1 if dm>tiny else (-1 if dm<-tiny else 0)
   if sgn!=0:
    imb+=sgn
    if prev_sign!=0 and prev_sign!=sgn:turns+=1
    prev_sign=sgn
   vol+=abs(dm)
   if q>=start8:
    tick8_b+=db;tick8_a+=da;vol8+=abs(dm);imb8+=sgn
    if sgn!=0:
     if prev8_sign!=0 and prev8_sign!=sgn: turns8+=1
     prev8_sign=sgn
   spr=ask[q]-bid[q]
   spread_sum+=spr
   if spr>spmax:spmax=spr
   if spr<spmin:spmin=spr
   gap=float(t[q]-t[q-1]);intertot+=gap
   if gap>intermax:intermax=gap
  N=float(k-start+1); N8=float(k-start8+1)
  sprnow=ask[k]-bid[k]
  mid8before=(bid[start8-1]+ask[start8-1])*.5
  X[j,0]=bon/N;X[j,1]=aon/N;X[j,2]=joint/N
  X[j,3]=(t[k]-t[bidlast])/1000 if bidlast>=0 else 1000.
  X[j,4]=(t[k]-t[asklast])/1000 if asklast>=0 else 1000.
  X[j,5]=sidej*(mid_now-mid_prev);X[j,6]=sidej*(bid[k]-bid[start-1]);X[j,7]=sidej*(ask[k]-ask[start-1])
  X[j,8]=sidej*(mid_now-mid8before);X[j,9]=sidej*tick8_b;X[j,10]=sidej*tick8_a
  X[j,11]=sidej*imb/N;X[j,12]=sidej*imb8/N8
  X[j,13]=(N-1)/max(float(t[k]-t[start-1])/1000.,.001)
  X[j,14]=intertot/N;X[j,15]=intermax;X[j,16]=sprnow;X[j,17]=spread_sum/N
  X[j,18]=spmax-spmin;X[j,19]=sprnow-spread_init;X[j,20]=sprnow-start_sp8
  X[j,21]=turns/N;X[j,22]=turns8/N8
  X[j,23]=abs(mid_now-mid_prev)/max(vol,tiny);X[j,24]=abs(mid_now-mid8before)/max(vol8,tiny)
  X[j,25]=(1. if tick8_b*tick8_a<0 else 0.)
  X[j,26]=un/N;X[j,27]=(bon-aon)/N
  X[j,28]=sidej*(sprnow-spread_init)
  X[j,29]=(t[k]-t[k-1]) if k>0 else 1000000.
 return X

def one(br,mo):
 start=time.time();fn=ROOT/KEYS[br](mo)
 with zipfile.ZipFile(SOURCE) as z:
  evt=z.read(f'evidence/FROZEN_R00_054_EVENTS_{br}_{mo}.npz')
 with np.load(io.BytesIO(evt)) as v:
  event_t=v['t'].copy();side=v['side'].copy();d30=v['d30'].copy();correct=v['correct'].copy()
 # CSV reading unmodified raw evidence from approved pinned gzip.
 if br=='coinexx':
  df=pd.read_csv(fn,compression='gzip',usecols=['time_msc','bid','ask'],dtype={'time_msc':'int64','bid':'float64','ask':'float64'})
  t=df['time_msc'].to_numpy(copy=True)-(120 if mo in ('01','02') else 180)*60000
  bid=df['bid'].to_numpy(copy=True);ask=df['ask'].to_numpy(copy=True)
 else:
  df=pd.read_csv(fn,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
  t=df['timestamp_ms_utc'].to_numpy(copy=True)
  bid=df['bid_raw'].to_numpy(dtype=np.float64)/1000.;ask=df['ask_raw'].to_numpy(dtype=np.float64)/1000.
 del df
 if np.any(np.diff(t)<0):raise AssertionError('raw ticks unsorted')
 if not np.all((bid>0)&(ask>=bid)):raise AssertionError('bad quote prices')
 idx=np.searchsorted(t,event_t,side='left')
 if idx.max()>=len(t) or not np.array_equal(t[idx],event_t):raise AssertionError('ORIGINAL_EVENT_TIMESTAMP_NOT_EXACT_RAW_FIRST_QUOTE')
 x=build(t,bid,ask,idx,side)
 if x.shape!=(len(event_t),30) or not np.isfinite(x).all():raise AssertionError('FEATURE_BAD_SHAPE_OR_NONFINITE')
 y=np.where(np.isfinite(d30)&(side*d30>.1),0,np.where(np.isfinite(d30)&(side*d30<-.1),1,2))
 if not np.array_equal((y==0).astype(np.int8),correct):raise AssertionError('ORIGINAL_LABEL_MISMATCH')
 dst=HERE/f'F39_SOURCE_NATIVE_QUOTE_{br}_{mo}.npz'
 np.savez_compressed(dst,t=event_t,side=side,raw_first_quote_index=idx,features=x,truth=y.astype('int8'),names=np.array(FEATURE_NAMES))
 receipt=dict(broker=br,month=mo,file=fn.name,tick_rows=len(t),events=len(event_t),features=x.shape[1],original_label_correct=int(correct.sum()),orig_event_sha256=hashlib.sha256(evt).hexdigest(),output_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),source_file_sha256=json.loads((HERE/'F39_8_APPROVED_SOURCE_GZIP_SHA_PINS.json').read_text())[f'{br}{mo}']['sha256'],source_clock_correction_minutes=(120 if mo in ('01','02') else 180) if br=='coinexx' else 0,causal_quote_input_cutoff_rule='first native raw quote of original event ms, all earlier tick indices only; no later same millisecond tick',elapsed_seconds=round(time.time()-start,2))
 (HERE/f'F39_RECEIPT_{br}_{mo}.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print('F39 BUILT',br,mo,len(t),len(event_t),'source_quote_index',idx[:2],'sec',receipt['elapsed_seconds'],flush=True)

if __name__=='__main__':
 spec={'source':'Original eight SHA-pinned raw Dukascopy/Coinexx tick csv.gz; source hashes were independently rechecked 8/8','new_research_not_original_filter05':True,'event_timestamp_fixed':True,'output_cols':list(FEATURE_NAMES),'safe_quote_index':'np.searchsorted(raw_t,source_event_t,side=left) FIRST raw source quote; last64 prior inclusive','broker_data_independent':True,'reconstructible_MQL5':True,'status':'source_native_original_tick derived causal feature hypothesis; no trained filter'}
 (HERE/'F39_FROZEN_EXTRACTION_PLAN.json').write_text(json.dumps(spec,indent=2)+'\n')
 for mo in ('01','02','06','07'):
  for br in ('coinexx','dukascopy'): one(br,mo)
 print('COMPLETE F39 RAW EXTRACTION',flush=True)
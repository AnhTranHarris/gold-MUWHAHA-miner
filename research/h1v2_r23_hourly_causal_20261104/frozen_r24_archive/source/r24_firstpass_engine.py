"""R24 additive dual-broker source-exact, as-of features / competing path labels.

This file does NOT import R23 future-selected positions to generate actions.
The ONLY use of future bid/ask is to construct supervised TARGET/STOP/TIMEOUT/
CENSORED labels after frozen as-of signal ordinals. Results are NONDEPLOYABLE.
BTC/MT5 cash P&L and broker dealer fills are not modeled.
"""
from __future__ import annotations
import csv, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
from numba import njit

BASE=Path('/mnt/data'); R24=BASE/'h1v2_r24_asof'
R23=BASE/'h1v2_r23_dualbroker/R23_ALL_96_COMPLETE_EIGHT_SOURCE_MONTH_SCENARIOS.csv'
HORIZONS=(15000,30000,60000)
FEE_RAW=20; NET_TP_RAW=100; LIQ_STOP_RAW=100; MAX_QUOTE_GAP=15000
CLASS_NAMES=('STOP','TARGET','TIMEOUT','CENSORED','UNFILLED')
SOURCE_NAMES=('DUKASCOPY_RAW','MT5_BROKER_EXPORT')
FEATURE_NAMES=(
 'broker_mt5','spread_raw','spread_relative_3s','spread_relative_60s','spread_relative_300s',
 'bid_move_3s','ask_move_3s','bid_move_15s','ask_move_15s','bid_move_60s','ask_move_60s',
 'bid_move_300s','ask_move_300s','bidask_dislocation_3s','bidask_leadership_mark',
 'abs_bid_rv_3s','abs_bid_rv_15s','abs_bid_rv_60s','abs_bid_rv_300s',
 'quotes_3s','quotes_15s','quotes_60s','quotes_300s','spread_ema15s','spread_ema300s',
 'epoch_age_s','lagged_quote_age_ms','minute_in_hour','hour_sin','hour_cos',
 'day_of_week','date_of_month','tokyo_session','london_session','ny_session','sydney_session',
 'syd_lon_overlap','london_ny_overlap','mtf_15m_closed_slope','mtf_h1_closed_slope',
 'mtf_h4_closed_slope','mtf_15m_valid','mtf_h1_valid','mtf_h4_valid',
 'news_verified_available','operations_permission_verified','broker_spread_strain_60s'
)

@njit(cache=False)
def build_tree(b,a):
 n=len(b); size=1
 while size<n: size*=2
 ibmax=np.full(size*2,np.int32(-2147483647),np.int32)
 ibmin=np.full(size*2,np.int32(2147483647),np.int32)
 iamin=np.full(size*2,np.int32(2147483647),np.int32)
 iamax=np.full(size*2,np.int32(-2147483647),np.int32)
 ibmax[size:size+n]=b;ibmin[size:size+n]=b
 iamin[size:size+n]=a;iamax[size:size+n]=a
 for i in range(size-1,0,-1):
  ibmax[i]=max(ibmax[2*i],ibmax[2*i+1]);ibmin[i]=min(ibmin[2*i],ibmin[2*i+1])
  iamin[i]=min(iamin[2*i],iamin[2*i+1]);iamax[i]=max(iamax[2*i],iamax[2*i+1])
 return size,ibmax,ibmin,iamax,iamin

@njit(cache=False)
def first_crossing(tree_max,tree_min,size,left,right,hi,lo):
 """Return earliest observed raw ordinal in [left,right) crossing either level.
 Iterative dyadic interval decomposition, O(log n), same-ms ordinals retained.
 """
 if right<=left: return -1,-1
 l=left+size;r=right+size
 p=np.empty(64,np.int64);q=np.empty(64,np.int64);np_=0;nq=0
 while l<r:
  if l&1:p[np_]=l;np_+=1;l+=1
  if r&1:r-=1;q[nq]=r;nq+=1
  l//=2;r//=2
 for j in range(np_+nq):
  node=p[j] if j<np_ else q[nq-1-(j-np_)]
  if tree_max[node]<hi and tree_min[node]>lo:continue
  while node<size:
   lc=node*2
   if tree_max[lc]>=hi or tree_min[lc]<=lo:node=lc
   else:node=lc+1
  idx=node-size
  if tree_max[node]>=hi:return idx,1
  if tree_min[node]<=lo:return idx,0
 return -1,-1

@njit(cache=False)
def label_path(t,b,a,signal,fill,right60,gapidx,hend15,hend30,hend60,size,bmax,bmin,amax,amin):
 n=len(signal)
 code=np.full((n,2,3),np.int8(3),np.int8)
 event_ix=np.full((n,2),-1,np.int32)
 fillvalid=np.zeros(n,np.bool_)
 for k in range(n):
  f=fill[k]
  if f<0 or f>=len(t):
   for side in range(2):
    for h in range(3):code[k,side,h]=4
   continue
  fillvalid[k]=True
  far=right60[k]
  cap=gapidx[k]
  if cap<far:far=cap
  for side in range(2):
   if side==0:
    hit,cause=first_crossing(bmax,bmin,size,f+1,far,int(a[f])+FEE_RAW+NET_TP_RAW,int(b[f])-LIQ_STOP_RAW)
   else:
    # first crossing high (STOP) or low (TARGET) for ask series
    hit,rawcause=first_crossing(amax,amin,size,f+1,far,int(a[f])+LIQ_STOP_RAW,int(b[f])-FEE_RAW-NET_TP_RAW)
    cause=0 if rawcause==1 else (1 if rawcause==0 else -1)
   event_ix[k,side]=hit
   for h in range(3):
    horizon_end=hend15[k] if h==0 else hend30[k] if h==1 else hend60[k]
    th=t[f]+(15000 if h==0 else 30000 if h==1 else 60000)
    if hit>=0 and t[hit]<=th:
     code[k,side,h]=cause
    else:
     # Gap first: never fabricate a path or change it to a loss/zero win.
     if gapidx[k]<len(t) and gapidx[k]<=horizon_end:
      code[k,side,h]=3
     elif horizon_end>=len(t) or t[horizon_end]-th>MAX_QUOTE_GAP:
      code[k,side,h]=3
     else:
      code[k,side,h]=2
 return code,event_ix,fillvalid


def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as file:
  for chunk in iter(lambda:file.read(1<<20),b''):h.update(chunk)
 return h.hexdigest()


def source_pin(source,mon):
 d=pd.read_csv(R23,usecols=['source','month','source_quote_SHA'],dtype={'month':'int32'})
 row=d[(d.source==source)&(d.month==int(mon))]
 if row.empty:return None
 h=row.source_quote_SHA.unique()
 if len(h)!=1:raise ValueError('ORIGINAL_R23_SOURCE_HASH_INCONSISTENCY')
 return str(h[0])


def source_file(source,mon):
 if source=='DUKASCOPY_RAW':return BASE/f'XAUUSD_DUKAS_2026_{mon}_ticks.csv.gz'
 if source=='MT5_BROKER_EXPORT':return BASE/f'XAUUSD_MT5_BROKER_2026_{mon}_ticks_ALL.csv.gz'
 raise ValueError(source)


def raw_month(source,mon,verify=True):
 p=source_file(source,mon)
 if verify:
  h=hashlib.file_digest(open(p,'rb'),'sha256').hexdigest()
  if h!=source_pin(source,mon):raise ValueError('SOURCE_SHA256_DRIFT '+source+' '+mon)
 if source=='DUKASCOPY_RAW':
  f=pd.read_csv(p,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
  t=f.timestamp_ms_utc.to_numpy(copy=True);b=f.bid_raw.to_numpy(copy=True);a=f.ask_raw.to_numpy(copy=True)
 else:
  f=pd.read_csv(p,compression='gzip',usecols=['time_msc','bid','ask'],dtype={'time_msc':'int64','bid':'float64','ask':'float64'})
  # Original R18/R23 historical-source offset convention; verify separately.
  offset_hours=2 if mon in ('01','02') else 3
  t=f.time_msc.to_numpy(copy=True)-offset_hours*3_600_000
  b=np.rint(f.bid.to_numpy()*1000).astype(np.int32)
  a=np.rint(f.ask.to_numpy()*1000).astype(np.int32)
 del f
 if source=='MT5_BROKER_EXPORT' and mon=='06':
  # R18 source-exact June UTC calendar tail: original file ends June 30 20:59
  # UTC, July server-month file contains last 2 UTC hours, with real observed
  # broker quote gap intact. Never fabricate quotes or join with time interp.
  jpath=source_file('MT5_BROKER_EXPORT','07')
  jhash=hashlib.file_digest(open(jpath,'rb'),'sha256').hexdigest()
  if jhash!=source_pin('MT5_BROKER_EXPORT','07'):raise ValueError('JULY_HALO_SOURCE_SHA_DRIFT')
  tail=pd.read_csv(jpath,compression='gzip',usecols=['time_msc','bid','ask'],dtype={'time_msc':'int64','bid':'float64','ask':'float64'})
  tj=tail.time_msc.to_numpy(np.int64)-3*3_600_000
  end=int(datetime(2026,7,1,tzinfo=timezone.utc).timestamp()*1000)
  mask=(tj>t[-1])&(tj<=end+60000)
  if not mask.any() or tj[mask][0]-t[-1]<=15000:raise ValueError('JUNE_TAIL_HALO_GAP_CONTRACT')
  t=np.r_[t,tj[mask]]
  b=np.r_[b,np.rint(tail.bid.to_numpy()[mask]*1000).astype(np.int32)]
  a=np.r_[a,np.rint(tail.ask.to_numpy()[mask]*1000).astype(np.int32)]
  del tail,tj
 if not len(t) or np.any(np.diff(t)<0) or np.any(a<b):raise ValueError('SOURCE_INVALID_BID_ASK_OR_ORDER')
 return t,b,a


def candidates(t,b,a,decision_ms=1000,cap=4000):
 if decision_ms<1:raise ValueError('positive observation clock required')
 ix=np.flatnonzero(np.r_[True,np.diff(t//decision_ms)!=0]).astype(np.int32)
 gapstart=np.flatnonzero(np.r_[True,np.diff(t)>MAX_QUOTE_GAP]).astype(np.int32)
 pos=np.searchsorted(gapstart,ix,side='right')-1
 age=t[ix]-t[gapstart[pos]]
 sp=a[ix].astype(np.int64)-b[ix].astype(np.int64)
 good=(age>=300000)&(sp>=0)&(sp<=cap)
 return ix[good],gapstart


def fill_after(t,b,a,signal,lag=100,fillcap=4000,stale=1000):
 f=np.searchsorted(t,t[signal]+lag,side='left').astype(np.int32)
 valid=(f<len(t));fi=np.minimum(f,len(t)-1)
 valid&=(t[fi]-(t[signal]+lag)<=stale)&((a[fi]-b[fi])<=fillcap)&(a[fi]>=b[fi])
 return np.where(valid,fi,-1).astype(np.int32)


def generate_labels(t,b,a,signal,fill):
 size,bmax,bmin,amax,amin=build_tree(b,a)
 ts=t[np.maximum(fill,0)]
 m=len(t)
 bounds=[np.searchsorted(t,ts+h,side='left').astype(np.int32) for h in HORIZONS]
 right60=np.searchsorted(t,ts+60000,side='right').astype(np.int32)
 gap=np.flatnonzero(np.diff(t)>MAX_QUOTE_GAP).astype(np.int32)+1
 nextgap=gap[np.minimum(np.searchsorted(gap,np.maximum(fill,0)+1),max(len(gap)-1,0))] if len(gap) else np.full(len(fill),m,np.int32)
 if len(gap):nextgap[np.searchsorted(gap,np.maximum(fill,0)+1)==len(gap)]=m
 labels,events,valid=label_path(t,b,a,signal,fill,right60,nextgap,*bounds,size,bmax,bmin,amax,amin)
 del bmax,bmin,amax,amin
 return labels,events,valid


def clock_by_hour(t_ms):
 hkeys,inv=np.unique(t_ms//3_600_000,return_inverse=True)
 out=np.zeros((len(hkeys),12),np.float32)
 for i,h in enumerate(hkeys):
  z=datetime.fromtimestamp(int(h*3600),tz=timezone.utc)
  zones={n:z.astimezone(ZoneInfo(s)) for n,s in [('T','Asia/Tokyo'),('L','Europe/London'),('N','America/New_York'),('S','Australia/Sydney')]}
  ts=9<=zones['T'].hour<18;ls=8<=zones['L'].hour<17;ns=8<=zones['N'].hour<17;ss=9<=zones['S'].hour<17
  out[i]=[z.hour,z.weekday(),z.day,int(ts),int(ls),int(ns),int(ss),int(ss and ls),int(ls and ns),float(np.sin(2*np.pi*z.hour/24)),float(np.cos(2*np.pi*z.hour/24)),z.minute]
 return out[inv]


def extract_features(t,b,a,signal,gapstarts,source):
 """No future quote ordinal or future-selected side in feature computation."""
 n=len(signal)
 if not n:return np.zeros((0,len(FEATURE_NAMES)),np.float32)
 s=signal;t0=t[s];bs=b[s].astype(np.int64); aa=a[s].astype(np.int64)
 spread=(aa-bs).astype(np.float32)
 f=np.zeros((n,len(FEATURE_NAMES)),np.float32)
 ind={k:i for i,k in enumerate(FEATURE_NAMES)}
 def setf(name,val):f[:,ind[name]]=val
 setf('broker_mt5',int(source=='MT5_BROKER_EXPORT'))
 setf('spread_raw',spread)
 price_abs=np.abs(np.diff(b.astype(np.int64),prepend=int(b[0])))
 abs_pref=np.r_[0,np.cumsum(price_abs,dtype=np.int64)]
 sraw=(a.astype(np.int64)-b.astype(np.int64))
 sp_pref=np.r_[0,np.cumsum(sraw,dtype=np.int64)]
 for win,suf in ((3000,'3s'),(15000,'15s'),(60000,'60s'),(300000,'300s')):
  j=np.searchsorted(t,t0-win,side='left')
  setf('bid_move_'+suf,bs-b[j]);setf('ask_move_'+suf,aa-a[j]);setf('quotes_'+suf,s-j)
  setf('abs_bid_rv_'+suf,(abs_pref[s+1]-abs_pref[j+1])/np.maximum(s-j,1)) if win in (3000,15000,60000,300000) else None
  if win==3000:
   setf('bidask_dislocation_3s',(bs-b[j])-(aa-a[j]))
   current_diff_bid=np.sign(bs-b[np.maximum(s-1,0)])
   current_diff_ask=np.sign(aa-a[np.maximum(s-1,0)])
   setf('bidask_leadership_mark',3*(current_diff_bid+1)+(current_diff_ask+1))
  if win==15000 or win==300000:
   mean=(sp_pref[s+1]-sp_pref[j])/np.maximum(s-j+1,1)
   setf('spread_ema15s' if win==15000 else 'spread_ema300s',mean)
  if win==3000 or win==60000 or win==300000:
   initial_spread=(a[j].astype(np.int64)-b[j].astype(np.int64))
   setf('spread_relative_'+suf,spread/(1.0+initial_spread))
 setf('broker_spread_strain_60s',spread/(100.0+np.abs(f[:,ind['bid_move_60s']])+np.abs(f[:,ind['ask_move_60s']])))
 e=gapstarts[np.searchsorted(gapstarts,s,side='right')-1]
 setf('epoch_age_s',(t0-t[e])/1000.0)
 setf('lagged_quote_age_ms',t0-t[np.maximum(s-1,0)])
 setf('minute_in_hour',(t0//60000)%60)
 clock=clock_by_hour(t0)
 for name,col in [('hour_sin',9),('hour_cos',10),('day_of_week',1),('date_of_month',2),('tokyo_session',3),('london_session',4),('ny_session',5),('sydney_session',6),('syd_lon_overlap',7),('london_ny_overlap',8)]:setf(name,clock[:,col])
 for period,name in ((900000,'15m'),(3_600_000,'h1'),(14_400_000,'h4')):
  start=(t0//period)*period
  prev=np.searchsorted(t,start,side='left')-1
  prev2=np.searchsorted(t,start-period,side='left')-1
  valid=(prev>=0)&(prev2>=0)
  p1=np.maximum(prev,0);p2=np.maximum(prev2,0)
  # last actual quote before each completed boundary, no synthesized bars
  valid&=(start-t[p1]<=period+15000)&(start-period-t[p2]<=period+15000)
  slope=((b[p1].astype(np.int64)+a[p1])-(b[p2].astype(np.int64)+a[p2]))/2
  setf('mtf_'+name+'_closed_slope',np.where(valid,slope,0))
  setf('mtf_'+name+'_valid',valid.astype(np.float32))
 # News, permission intentionally UNKNOWN until independent MT5 export and source historical permissions verified.
 setf('news_verified_available',0)
 setf('operations_permission_verified',0)
 return np.clip(f,-1.e7,1.e7)


def calendar_reference(mon):
 """Source-exact R9 benchmark calendar recovered from R23 ZIP; no division by 4."""
 import zipfile
 z=zipfile.ZipFile(BASE/'h1v2_r23_dualbroker/R23_DUKASCOPY_RAW_COMPLETE_FOUR_MONTH_ALL_SCENARIOS_QUARTER_HOUR_DAY_BIDASK_ORDINALS_20261103.zip')
 stem=f'results/R23_DUKASCOPY_RAW_{mon}_COMPLETE_QUARTERS.csv'
 with z.open(stem) as f:d=pd.read_csv(f,dtype={'month':str})
 d=d[d.scenario=='A1_TP050_STOP100_H60_CAP4000_Q8'].copy()
 if len(d)!= {'01':2976,'02':2688,'06':2880,'07':2976}[mon]:raise ValueError('BROKEN_REFERENCE_QUARTER_COUNT')
 times=pd.to_datetime(d.utc_quarter,utc=True).astype('int64').to_numpy()//1000000
 qr=d.original_R9_SYNTH_reference.to_numpy(np.int32)
 source_map={'01':27980,'02':33523,'06':31758,'07':24324}
 if qr.sum()!=source_map[mon]:raise ValueError('ORIGINAL_R9_SYNTH_SOURCE_REFERENCE_DRIFT')
 return times,qr

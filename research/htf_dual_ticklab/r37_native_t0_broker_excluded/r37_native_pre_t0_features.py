"""R37: source-native PRE-t0 specialist. New feature adapter, NOT a replay-engine replacement.

Consumes SHA-authorized raw source ticks, and pre-existing frozen R00 event timestamps,
BUY/SELL sign, and label diagnostic. Every market feature uses ONLY ticks with
normalized timestamp STRICTLY BEFORE t0. Equal-millisecond ordinal ambiguity is
excluded conservatively instead of silently selecting a later tick.
"""
from __future__ import annotations
import gzip, hashlib, io
from pathlib import Path
import numpy as np
import pandas as pd

WINDOWS=(1000,5000,15000,30000,60000,180000,900000,3600000)
BARS=(60000,300000,900000,3600000)
PINS={
 'coinexx':{
 '01':'1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8',
 '02':'5de772aab4d15ebf18aa48850e847c98e2bcb639064790bbed9d87a598c3bf05',
 '06':'3033ccb257d067aecc123f3791d9dddc5c95841b9bba167ff1ca0cf1589dc2b4',
 '07':'d9d47d40abb33935414edfb5c11f0c518d8c9cc27221da182dab0bc49b0b708d'},
 'dukascopy':{
 '01':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
 '02':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d',
 '06':'34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2',
 '07':'e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7'}}

def digest(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
 return h.hexdigest()

def read_native_ticks(p,broker,month):
 p=Path(p)
 if p.name != (f'XAUUSD_MT5_BROKER_2026_{month}_ticks_ALL.csv.gz' if broker=='coinexx' else f'XAUUSD_DUKAS_2026_{month}_ticks.csv.gz'):
  raise ValueError('registered filename mismatch')
 sha=digest(p)
 if sha!=PINS[broker][month]:raise ValueError('REGISTERED SOURCE SHA256 MISMATCH')
 if broker=='coinexx':
  raw=pd.read_csv(p,usecols=['time_msc','bid','ask'],dtype={'time_msc':'int64','bid':'float64','ask':'float64'})
  t=raw['time_msc'].to_numpy()- (120 if month in ('01','02') else 180)*60000
  bid=raw['bid'].to_numpy();ask=raw['ask'].to_numpy()
 else:
  raw=pd.read_csv(p,usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int64','ask_raw':'int64'})
  t=raw['timestamp_ms_utc'].to_numpy();bid=raw['bid_raw'].to_numpy(dtype=np.float64)/1000;ask=raw['ask_raw'].to_numpy(dtype=np.float64)/1000
 del raw
 if not (np.all(t[1:]>=t[:-1]) and np.all(np.isfinite(bid)) and np.all(np.isfinite(ask)) and np.all(ask>=bid) and np.all(bid>0)):
  raise ValueError('native tick ordering/price contract')
 return t,bid,ask,sha

def feature_matrix(t,bid,ask,event_t,side):
 """Causal as-of quote/bid/ask/HTF-completion feature matrix.
 All index lookups end STRICTLY BEFORE the event timestamp. No labels passed.
 """
 t=np.asarray(t,dtype=np.int64);event_t=np.asarray(event_t,dtype=np.int64);side=np.asarray(side)
 if not (len(t)==len(bid)==len(ask) and np.all(t[1:]>=t[:-1]) and np.all(event_t[1:]>event_t[:-1]) and np.all(np.isin(side,(-1,1)))):
  raise ValueError('chronology or source shape')
 idx=np.searchsorted(t,event_t,side='left')-1
 safe=np.maximum(idx,0)
 mid=(bid+ask)*.5
 sp=ask-bid
 n=len(t)
 changed_bid=np.r_[False,bid[1:]!=bid[:-1]]
 changed_ask=np.r_[False,ask[1:]!=ask[:-1]]
 abs_delta=np.r_[0,np.abs(np.diff(mid))]
 cols=[];names=[]
 def put(name,arr):
  cols.append(np.asarray(arr,dtype=np.float32));names.append(name)
 put('native_spread',sp[safe]);put('prior_quote_age_ms',(event_t-t[safe]).clip(0,120000))
 put('quote_count_prior64',np.minimum(safe+1,64))
 put('quote_rate_64',64000 / np.maximum(1,t[safe]-t[np.maximum(0,safe-64)]))
 b_only=(changed_bid & ~changed_ask).astype(np.int32)
 a_only=(changed_ask & ~changed_bid).astype(np.int32)
 both=(changed_ask & changed_bid).astype(np.int32)
 # Prefix counts for strict event as-of ending with quote idx.
 for label,v in (('bid_only',b_only),('ask_only',a_only),('joint',both),('mid_positive',(abs_delta>0).astype(np.int32))):
  cs=np.pad(np.cumsum(v,dtype=np.int64),(1,0))
  for q in (8,32,64):
   start=np.maximum(0,safe+1-q)
   put(f'{label}_share_last{q}',(cs[safe+1]-cs[start])/np.maximum(1,safe+1-start))
 cs_abs=np.pad(np.cumsum(abs_delta),(1,0))
 for q in (8,32,64):
  older=np.maximum(0,safe-q)
  put(f'side_mid_impulse_last{q}',side*(mid[safe]-mid[older]))
  put(f'side_bid_impulse_last{q}',side*(bid[safe]-bid[older]))
  put(f'side_ask_impulse_last{q}',side*(ask[safe]-ask[older]))
  put(f'spread_delta_last{q}',sp[safe]-sp[older])
  put(f'elapsed_quote_last{q}',t[safe]-t[older])
  # Average absolute path length in last q updates; prefix excludes future quotes.
  path=cs_abs[safe+1]-cs_abs[np.maximum(0,safe+1-q)]
  put(f'efficiency_last{q}',side*(mid[safe]-mid[older])/(.0001+path))
 for ms in WINDOWS:
  j=np.searchsorted(t,event_t-ms,side='left')-1
  j=np.minimum(safe,np.maximum(j,0))
  put(f'side_mid_change_{ms}ms',side*(mid[safe]-mid[j]))
  put(f'quote_count_{ms}ms',safe-j)
  put(f'spread_delta_{ms}ms',sp[safe]-sp[j])
 for ms in BARS:
  published=(event_t//ms)*ms
  end=np.searchsorted(t,published,side='left')-1
  start=np.searchsorted(t,published-ms,side='left')-1
  end=np.maximum(end,0);start=np.maximum(start,0)
  put(f'completed_{ms}ms_side_close_change',side*(mid[end]-mid[start]))
  put(f'completed_{ms}ms_quote_count',end-start)
 # Broker-agnostic UTC cyclic features; no month/original t0 absolute ID, nor price level.
 hour=(event_t%86400000)/3600000.0
 put('utc_hour_sin',np.sin(2*np.pi*hour/24));put('utc_hour_cos',np.cos(2*np.pi*hour/24))
 put('utc_weekday_sin',np.sin(2*np.pi*((event_t//86400000+3)%7)/7))
 put('side',side)
 valid=(idx>=65)&((event_t-t[safe])<=60000)&np.isfinite(sp[safe])
 X=np.column_stack(cols).astype(np.float32)
 if not np.all(np.isfinite(X)):raise ValueError('nonfinite feature')
 return X,names,valid

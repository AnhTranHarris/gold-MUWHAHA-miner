"""R13 source-exact broker-conditional H1V2 entry geometry (EXPERIMENTAL).

This additive research uses prefix-only candidate/feature state, followed by
separate future-privileged labels and future-informed one-position schedules.
Do not use results as a predictive entry strategy. Original R9/R11/R12 receipts,
source bytes, exit logic and spread $1.50 gate are immutable controls.

Three data domains: MT5 Strategy Tester REAL-tick mode, MT5 Strategy Tester
synthetic mode (both source Coinexx tester contexts), Dukascopy raw vendor feed.
Neither MT5 tester data is a certified record of live Coinexx fills.

Every successful label buys ASK/sells BID or sells BID/covers ASK, plus .02 USD
quoted-price proxy cost. Favorable >=+.10 NET by observed quote within the
specified 5/15/30s, with NO -0.10 opening-liquidation adverse anywhere over
FULL 30s, complete source quote coverage, and strictly later observed quotes.
Dynamic horizon alternatives are distinct labels, NOT original S1 success.

Candidate lanes (not predicted actions):
  BASE_250_1500: original max $1.50, first observed 250ms quote
  DENSE_1500: as-observed distinct ms when spread <= $1.50
  WIDE_REQUOTE_4000: diagnostic permitted up to $4.00 source spread,
    ONLY on observed 250ms boundary OR first within-bin squeeze >=$.02;
    actual ASK/BID future target still pays entire spread
  BROKER_CONTRACTION: first250/intrabin squeeze in raw spread<=4.00,
    raw current spread 20% below PREVIOUSLY observed 300s EMA
  DIRECTIONAL_MICROPATH: first250/within-bin squeeze, spread<=4.00,
    source 3s BID and ASK motion same signed direction and sufficient to
    have covered ACTUAL cost + fee + target in that past interval;
    this is historical past motion, NOT a future guarantee.
All lanes require 300s fresh quotes after any >15s quote gap.
"""
from __future__ import annotations
import argparse, csv, datetime as dt, hashlib, importlib.util, json, sys, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

SRC=Path('/mnt/data')
BASE=SRC/'h1v2_r13_broker_adaptive'
OUT=BASE/'results'
FEE=20; NET_TARGET=100; BAD=100; WARMUP=300_000; RESET_GAP=15_000
HORIZONS=(5000,15000,30000)
T0=int(dt.datetime(2026,2,2,6,tzinfo=dt.timezone.utc).timestamp()*1000)
T1=T0+3_600_000
HALO_START=T0-360_000; HALO_END=T1+45_000
EXPECTED={
 'R9_REAL_MT5_TESTER':('R9_REAL_2026-02-02_ticks.csv.gz','24e4b31935ead7b0eb039fe84dc8972c59500b362cac21721739f1b0c050b3d7'),
 'R9_SYNTH_MT5_TESTER':('R9_SYNTH_2026-02-02_ticks.csv.gz','dcedb28f7453c80d2dec5ffe5d386dad1661134ba61765337155fbbaeb6213a2'),
 'DUKASCOPY_RAW':('XAUUSD_DUKAS_2026_02_ticks.csv.gz','ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d')}
PINNED_HELPER='c52de41072911ad53dedadfb3dba1899ea112e41a9e58e48ea29a7903e3ec475'


def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
 return h.hexdigest()


def load_source(source):
 path=SRC/EXPECTED[source][0]; expected=EXPECTED[source][1]
 if sha(path)!=expected:raise RuntimeError('SOURCE_SHA_MISMATCH '+source)
 if source=='DUKASCOPY_RAW':
  frame=pd.read_csv(path,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],
                    dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
  t=frame.timestamp_ms_utc.to_numpy(np.int64); b=frame.bid_raw.to_numpy(np.int32);a=frame.ask_raw.to_numpy(np.int32)
 else:
  frame=pd.read_csv(path,compression='gzip',usecols=['time_msc','bid','ask'],
                    dtype={'time_msc':'int64','bid':'float64','ask':'float64'})
  t=frame.time_msc.to_numpy(np.int64)-2*3_600_000
  b=np.rint(frame.bid.to_numpy()*1000).astype(np.int32)
  a=np.rint(frame.ask.to_numpy()*1000).astype(np.int32)
 if np.any(t[1:]<t[:-1]) or np.any(a<b):raise ValueError('QUOTE_SOURCE_INVALID')
 lo=np.searchsorted(t,HALO_START,'left');hi=np.searchsorted(t,HALO_END,'right')
 t=t[lo:hi].copy();b=b[lo:hi].copy();a=a[lo:hi].copy()
 if not len(t) or t[0]>T0-WARMUP or t[-1]<T1+30000:raise ValueError('SOURCE_HALO_INCOMPLETE')
 return t,b,a,expected


@njit(cache=True)
def prefix_candidates(t,b,a):
 """Only observed prefix prices, 3s ordered motion and past-time spread EMA.

 flags: bit1 first observed 250ms, bit2 first spread squeeze >=$.02 in
 occupied 250ms after its first quote; all later same-ms ordinals ignored.
 Spread up to $4.00 for explicit WIDE counterfactual, not original baseline.
 """
 n=len(t); ix=np.empty(n,np.int64);fl=np.empty(n,np.int8)
 ema300=np.empty(n,np.float64);ema15=np.empty(n,np.float64)
 moveb3=np.empty(n,np.int32);movea3=np.empty(n,np.int32)
 epoch=t[0];s300=float(a[0]-b[0]);s15=s300
 last250=-9223372036854775807;firstspread=0;firstsqueeze=False;j3=0;count=0
 for i in range(n):
  if i and t[i]-t[i-1]>RESET_GAP:
   epoch=t[i];s300=float(a[i]-b[i]);s15=s300;j3=i
  s=a[i]-b[i]
  if i:
   dtms=max(0,t[i]-t[i-1]);
   s300=s300+(1-np.exp(-dtms/300000.0))*(float(s)-s300)
   s15=s15+(1-np.exp(-dtms/15000.0))*(float(s)-s15)
  ema300[i]=s300;ema15[i]=s15
  while j3+1<=i and t[j3+1]<=t[i]-3000:j3+=1
  moveb3[i]=b[i]-b[j3];movea3[i]=a[i]-a[j3]
  k=t[i]//250;new250=k!=last250
  if new250:firstspread=s;firstsqueeze=False
  last250=k
  if i and t[i]==t[i-1]:continue
  if t[i]-epoch<WARMUP or s<0 or s>4000:continue
  bits=1 if new250 else 0
  if not new250 and not firstsqueeze and s<=firstspread-20:
   bits|=2;firstsqueeze=True
  ix[count]=i;fl[count]=bits;count+=1
 return ix[:count],fl[:count],ema300,ema15,moveb3,movea3


def lane_membership(ix,flags,b,a,ema300,ema15,moveb3,movea3):
 s=(a[ix].astype(np.int64)-b[ix].astype(np.int64))
 f=flags.astype(np.int32);start=(f&1)!=0;anyclock=(f&3)!=0
 long=ema300[ix];short=ema15[ix]
 moved=np.minimum(np.abs(moveb3[ix]),np.abs(movea3[ix]))
 coherent=np.sign(moveb3[ix])==np.sign(movea3[ix])
 motion_threshold=s+FEE+NET_TARGET
 return {
  'BASE_250_1500':start&(s<=1500),
  'DENSE_1500':s<=1500,
  'WIDE_REQUOTE_4000':anyclock&(s<=4000),
  'BROKER_CONTRACTION':anyclock&(s<=4000)&(s<=.80*long)&(short<=long),
  'DIRECTIONAL_MICROPATH':anyclock&(s<=4000)&coherent&(moved>=motion_threshold),
 }


def frozen_extrema(t,b,a,ix,h):
 """Import original independently SHA-pinned R11S1 algorithm, not a remake."""
 source=SRC/'h1v2_r12/upstream/entry_survivability.py'
 if sha(source)!=PINNED_HELPER:raise RuntimeError('S1_HELPER_SHA_MISMATCH')
 sys.path.insert(0,str(source.parent))
 try:
  import entry_survivability
  return entry_survivability._rolling_extrema(t,b,a,ix,h)
 finally:sys.path.pop(0)


@njit(cache=True)
def first_tp(t,b,a,ix,side,horizon_ms):
 m=len(ix);ends=np.full(m,-1,np.int64);times=np.full(m,-1,np.int64)
 for k in range(m):
  i=ix[k];end=t[i]+horizon_ms;j=i+1
  if side[k]==1:
   threshold=a[i]+FEE+NET_TARGET
   while j<len(t) and t[j]<=end:
    if t[j]>t[i] and b[j]>=threshold:
     ends[k]=j;times[k]=t[j];break
    j+=1
  else:
   threshold=b[i]-FEE-NET_TARGET
   while j<len(t) and t[j]<=end:
    if t[j]>t[i] and a[j]<=threshold:
     ends[k]=j;times[k]=t[j];break
    j+=1
 return ends,times


def exact_interval_schedule(starts,ends):
 """FUTURE-known earliest finish exact unweighted interval cardinality.

 Strict start>prior exit, ties deterministically by entry timestamp then ordinal.
 """
 if len(starts)!=len(ends) or np.any(ends<=starts):raise ValueError('INVALID_INTERVALS')
 order=np.lexsort((np.arange(len(starts)),starts,ends))
 chosen=np.empty(len(order),np.int64);last=-2**62;n=0
 for i in order:
  if starts[i]>last:
   chosen[n]=i;n+=1;last=ends[i]
 return chosen[:n]


def experiment_source(name):
 t,b,a,pin=load_source(name)
 ix,flags,e300,e15,mb3,ma3=prefix_candidates(t,b,a)
 mask=(t[ix]>=T0)&(t[ix]<T1);ix=ix[mask];flags=flags[mask]
 if not len(ix):raise RuntimeError('EMPTY_CANDIDATE_SOURCE '+name)
 lanes=lane_membership(ix,flags,b,a,e300,e15,mb3,ma3)
 min30,max30,mina30,maxa30,_,_,cov30=frozen_extrema(t,b,a,ix,30000)
 future15={};safeB=(min30.astype(np.int64)>b[ix].astype(np.int64)-BAD)&cov30
 safeS=(maxa30.astype(np.int64)<a[ix].astype(np.int64)+BAD)&cov30
 for h in HORIZONS:
  mb,xb,ma,xa,_,_,cov=frozen_extrema(t,b,a,ix,h)
  future15[h]=((xb.astype(np.int64)>=a[ix].astype(np.int64)+120)&cov&safeB,
               (ma.astype(np.int64)<=b[ix].astype(np.int64)-120)&cov&safeS)
 originalB,originalS=future15[15000]
 if np.any(originalB&originalS):raise RuntimeError('ORIGINAL_BOTH_SIDES_QUALIFIED')
 hourly=[];qrows=[];counter={};trace_rows=[];signal_suites={}
 hours=(dt.datetime.fromtimestamp(T0/1000,dt.timezone.utc).strftime('%Y-%m-%dT%H:00:00Z'))
 quarter_starts=[T0+i*900_000 for i in range(4)]
 for lane,valid in lanes.items():
  for horizon in HORIZONS:
   gb,gs=future15[horizon]
   qualified=valid&(gb|gs)
   ids=np.flatnonzero(qualified)
   side=np.where(gb[ids],1,-1).astype(np.int8)
   j,exitt=first_tp(t,b,a,ix[ids],side,horizon)
   if np.any(j<0):raise AssertionError('QUALIFIED_FAV_WITHOUT_TP')
   gross=np.where(side==1,b[j]-a[ix[ids]],b[ix[ids]]-a[j])-FEE
   if np.any(gross<NET_TARGET):raise AssertionError('NONEXECUTABLE_TP')
   sel=exact_interval_schedule(t[ix[ids]],exitt)
   got=t[ix[ids[sel]]];ended=exitt[sel]
   if horizon==15000:signal_suites[lane]=(ix[ids[sel]].copy(),side[sel].copy())
   for kk in sel:
    i=int(ix[ids[kk]]);jj=int(j[kk]);
    trace_rows.append({'source':name,'lane':lane,'favorable_horizon_ms':horizon,
      'entry_raw_tick_ordinal':i,'exit_raw_tick_ordinal':jj,
      'entry_ms_UTC':int(t[i]),'exit_ms_UTC':int(t[jj]),
      'side_BUY_1_SELL_minus1':int(side[kk]),'entry_bid_raw':int(b[i]),'entry_ask_raw':int(a[i]),
      'exit_bid_raw':int(b[jj]),'exit_ask_raw':int(a[jj]),'net_proxy_price_raw_0p001':int(gross[kk]),
      'entry_spread_raw_0p001':int(a[i]-b[i]),'past_spread_300s_EMA_raw':float(e300[i]),
      'past_spread_15s_EMA_raw':float(e15[i]),
      'past_bid_3s_move_raw':int(mb3[i]),'past_ask_3s_move_raw':int(ma3[i]),
      'original_strict_S1_15s':bool(horizon==15000),
      'future_informed_schedule':True})
   if len(got)>1 and np.any(got[1:]<=ended[:-1]):raise AssertionError('OVERLAPPING_POSITIONS')
   if horizon==15000:
    if np.any(~(originalB[ids[sel]]|originalS[ids[sel]])):raise AssertionError('STRICT15_DRIFT')
   rec={'source':name,'lane':lane,'first_favorable_horizon_ms':horizon,
    'future_good_source_candidate_count':len(ids),'future_selected_nonoverlap_firstTP':len(sel),
    'all_selected_tp_executable_net_ge_0p10':True,'source_hash':pin,
    'full_30s_zero_0p10_adverse_required':True,
    'original_S1_strict_only_if_horizon_15000':horizon==15000,
    'selection_future_privileged':True}
   counter[(lane,horizon)]=rec
   for q,qs in enumerate(quarter_starts):
    count=int(np.count_nonzero((got>=qs)&(got<qs+900_000)))
    # Optimistic stand-alone upper for this quarter, ignores incoming occupancy
    local=(t[ix[ids]]>=qs)&(t[ix[ids]]<qs+900_000)
    upper=len(exact_interval_schedule(t[ix[ids[local]]],exitt[local]))
    qrows.append({'source':name,'lane':lane,'horizon_ms':horizon,
      'quarter_UTC':dt.datetime.fromtimestamp(qs/1000,dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:00Z'),
      'source_R9_SYNTH_original_quarter_ref':[28,27,25,24][q], # Check against R12C pinned acute quarter receipt below
      'future_selected_nonoverlap_count':count,'isolated_optimistic_upper':upper,
      'future_good_candidate_count':int(local.sum()),'capacity_met':int(count>=[28,27,25,24][q]),
      'not_deployable':True})
   hourly.append({**rec,'hour_original_R9_SYNTH_entry_reference':104,
                  'meets_hour_count':int(len(sel)>=104)})
 # Preserve complete as-of candidates, every future offline label and exact
 # winning source ordinal. A long-form source trace prevents reliance on totals.
 np.savez_compressed(OUT/f'R13_{name}_ALL_ASOF_CANDIDATES_AND_SEPARATE_HORIZON_LABELS.npz',
   source_quote_ordinal=ix,entry_utc_ms=t[ix],entry_bid_raw=b[ix],entry_ask_raw=a[ix],
   asof_clock_bits=flags,past_15s_spread_ema_raw=e15[ix],
   past_300s_spread_ema_raw=e300[ix],past_bid_move_3s_raw=mb3[ix],
   past_ask_move_3s_raw=ma3[ix],source_covered30=cov30,
   **{('lane_'+k):v for k,v in lanes.items()},
   **{f'h{h}_future_good_BUY':future15[h][0] for h in HORIZONS},
   **{f'h{h}_future_good_SELL':future15[h][1] for h in HORIZONS})
 p=OUT/f'R13_{name}_ALL_FUTURE_SELECTED_TRADE_SOURCE_ORDINALS.csv'
 write_csv(p,trace_rows)
 return hourly,qrows,{'source':name,'sha256':pin,'halo_quotes':len(t),'asof_candidates_up_to_4_USD':len(ix),
      'candidate_first250_admitted_lte1p50':int(lanes['BASE_250_1500'].sum()),
      'raw_source_hour_median_spread_USD':round(float(np.median(a[(t>=T0)&(t<T1)]-b[(t>=T0)&(t<T1)]))/1000,5)}


def write_csv(path,rows):
 with path.open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def run():
 OUT.mkdir(parents=True,exist_ok=True)
 hr=[];qr=[];source=[]
 for name in EXPECTED:
  h,q,r=experiment_source(name);hr.extend(h);qr.extend(q);source.append(r)
  print(json.dumps({'source':name,'status':'COMPLETED','hour_lanes':len(h),'source_median_spread':r['raw_source_hour_median_spread_USD']}),flush=True)
 assert len(hr)==3*5*3 and len(qr)==len(hr)*4
 a=OUT/'R13_ALL_45_SOURCE_LANE_HORIZON_RESULTS.csv';b=OUT/'R13_ALL_180_SOURCE_QUARTER_LANE_HORIZON_RESULTS.csv';
 write_csv(a,hr);write_csv(b,qr)
 receipt={'scientific_status':'FUTURE_KNOWN_HINDSIGHT_ONLY_NO_CAUSAL_PREDICTOR_NO_BROKER_FILL',
  'source':source,'legacy_original_GATE_USD':1.50,'new_MAX_4_USD_gate':'DIAGNOSTIC_NOT_PERMITTED_FOR_LIVE',
  'quote_horizon_5000_30000': 'DISTINCT_LABELS_DO_NOT_REPLACE_ORIGINAL_15S',
  'past_only_features':'all source candidate and 3s/15s/300s prefix state',
  'original_dollars_price_not_account_cash':'fee_proxy_0p02_USD_per_1oz_price_path',
  'hour_rows':len(hr),'quarter_rows':len(qr)}
 (OUT/'R13_EXPERIMENT_RECEIPT.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
 pins={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='R13_OUTPUT_SHA_MANIFEST.json'}
 (OUT/'R13_OUTPUT_SHA_MANIFEST.json').write_text(json.dumps(pins,indent=2)+'\n')
 return receipt

if __name__=='__main__':print(json.dumps(run(),indent=2))

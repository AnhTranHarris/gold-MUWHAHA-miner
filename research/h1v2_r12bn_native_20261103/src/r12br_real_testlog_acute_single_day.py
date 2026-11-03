#!/usr/bin/env python3
"""R12BR: cross-source acute single-day counterfactual on archived R9 REAL tester ticks.

This is NOT live Coinexx, and uses future-known outcomes to select trades.
Each input comes from exactly one original source. Output is isolated and never
replaces R12BN synthetic, R12DQ Dukascopy, R11S4, or deployed R9 v2 code.
"""
from __future__ import annotations
import csv,datetime as dt,hashlib,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path[:0]=['/mnt/data/h1v2_r12/source','/mnt/data/h1v2_r12/upstream']
from r12_dense_requote import asof_quote_clocks,_rolling_extrema
from r12_tp_oracle import quote_tp_first,earliest_finish_schedule
RAW=Path('/mnt/data/R9_REAL_2026-02-02_ticks.csv.gz')
SYN=Path('/mnt/data/R9_SYNTH_2026-02-02_ticks.csv.gz')
DUK=Path('/mnt/data/XAUUSD_DUKAS_2026_02_ticks.csv.gz')
OUT=Path('/mnt/data/h1v2_r12_realprobe')
TARGET=int(dt.datetime(2026,2,2,6,tzinfo=dt.timezone.utc).timestamp()*1000)
REF=104

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def run_source(path,label):
 if label=='DUKASCOPY_RAW':
  df=pd.read_csv(path,usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':np.int64,'bid_raw':np.int32,'ask_raw':np.int32})
  t=df.timestamp_ms_utc.to_numpy(copy=True);bid=df.bid_raw.to_numpy(copy=True);ask=df.ask_raw.to_numpy(copy=True)
 else:
  df=pd.read_csv(path,usecols=['time_msc','bid','ask'],dtype={'time_msc':np.int64,'bid':np.float64,'ask':np.float64})
  t=df.time_msc.to_numpy(copy=True)-7200000
  bid=np.rint(df.bid.to_numpy()*1000).astype(np.int32);ask=np.rint(df.ask.to_numpy()*1000).astype(np.int32)
 assert len(t)>0 and np.all(t[1:]>=t[:-1]) and np.all(ask>=bid)
 masks=(t>=TARGET)&(t<TARGET+3600000)
 spreads=(ask[masks].astype(np.int64)-bid[masks].astype(np.int64))/1000
 # As-of entries require 5min warmup, so source all chronological quotes input.
 ix,flags=asof_quote_clocks(t,bid,ask)
 cand_mask=(t[ix]>=TARGET)&(t[ix]<TARGET+3600000)
 ci=ix[cand_mask];ff=flags[cand_mask]
 mn15,mx15,ma15,xa15,nn15,age15,cov15=_rolling_extrema(t,bid,ask,ci,15000)
 mn30,mx30,ma30,xa30,nn30,age30,cov30=_rolling_extrema(t,bid,ask,ci,30000)
 eb=bid[ci].astype(np.int64);ea=ask[ci].astype(np.int64)
 goodb=(mx15.astype(np.int64)>=ea+120)&(mn30.astype(np.int64)>eb-100)&cov15&cov30
 goods=(ma15.astype(np.int64)<=eb-120)&(xa30.astype(np.int64)<ea+100)&cov15&cov30
 assert not np.any(goodb&goods)
 valid=goodb|goods;choices=ci[valid];sides=np.where(goodb[valid],1,-1).astype(np.int8)
 first=(ff[valid]&1)!=0
 x,xt=quote_tp_first(t,bid,ask,choices,ask[choices],bid[choices],sides)
 assert np.all(x>=0) and np.all(xt>t[choices]) and np.all(xt<=t[choices]+15000)
 liq=np.where(sides>0,bid[x],ask[x]);entry=np.where(sides>0,ask[choices],bid[choices]);pnl=(liq.astype(np.int64)-entry.astype(np.int64))*sides-20
 assert np.all(pnl>=100)
 sel={}
 for name,sub in [('FIRST250',np.flatnonzero(first)),('DISTINCT_MS',np.arange(len(choices)))]:
  chosen=sub[earliest_finish_schedule(t[choices[sub]],xt[sub])] if len(sub) else np.empty(0,np.int64)
  assert len(chosen)<=1 or np.all(t[choices[chosen[1:]]]>xt[chosen[:-1]])
  sel[name]={'strict_event_count':int(len(sub)),'isolated_UTC_06_hour_optimistic_firstTP_count':int(len(chosen)),
   'quota_104_possible_isolated':bool(len(chosen)>=REF),'selected_quote_ordinals_first_10':choices[chosen][:10].astype(int).tolist(),
   'TP_selected_nominal_net_p50':(float(np.median(pnl[chosen]))/1000 if len(chosen) else None)}
 return {'data_contract':label,'archive':path.name,'source_sha256':sha(path),'source_quote_rows_full_file':len(t),'UTC_target_hour':'2026-02-02T06:00:00Z',
         'UTC_target_quote_count':int(masks.sum()),'hour_spread_usd_p0_p50_p90_p99_p100':np.quantile(spreads,[0,.5,.9,.99,1]).round(4).tolist(),
         'fraction_hour_quotes_spread_gt_usd_1p5':float(np.mean(spreads>1.5)),
         'admitted_250ms_exact_count':int(np.count_nonzero((ff&1)!=0)), 'admitted_distinct_ms_asof_count':len(ci),
         'strict_full30_safe_first15_good_event_count_distinct':int(len(choices)), 'source_eligibility_past_only':True,
         'source_15_and_30_outcomes_and_TP_selections_future_informed':True, 'variants':sel}

def main():
 results=[run_source(p,n) for p,n in ((RAW,'R9_REAL_MT5_TESTER'),(SYN,'R9_SYNTH_MT5_TESTER'),(DUK,'DUKASCOPY_RAW'))]
 ret={'experiment':'R12BR_INDEPENDENT_ACUTE_SINGLE_HOUR_THREE_SOURCE_TESTER_AND_RAW_DUKAS_COMPARE',
  'source_historical_original_R9_SYNTH_hourly_ref':REF,'three_separately_scored_quote_histories':results,
  'utc_conversion_for_R9_MT5_source_hour':'server UTC -2 hours, as pinned in R11S3/R12 original source',
  'limitations':['R9 REAL tester quote history is not a live Coinexx fill or guarantee of historical broker execution',
  'Dukascopy independent raw spread not equivalent to Coinexx spreads','source-isolated hourly greedy capacity ignores earlier/later hour boundary inventory and is an optimistic bound',
  'future-known selection proves nothing about causal model accuracy','nominal $0.02 fee excludes latency, slippage and rejection',
  'one date/hour does not establish full-month or cross-feed generalization']}
 out=OUT/'R12BR_FEB02_06UTC_REAL_SYNTH_DUKAS_FIRSTTP_SEPARATE_SOURCE_WITNESS.json'
 out.write_text(json.dumps(ret,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
 print(json.dumps(ret,indent=2,ensure_ascii=False))
 print('RESULT_SHA256',sha(out),'SOURCE_CODE_SHA256',sha(Path(__file__)))
if __name__=='__main__':main()

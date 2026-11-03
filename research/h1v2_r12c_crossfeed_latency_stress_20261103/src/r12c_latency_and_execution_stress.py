#!/usr/bin/env python3
"""R12C: immutable-source, frozen hindsight-signal, execution-latency stress.

Purpose: test whether R12BN/R12D first-250ms full30-safe + first15
future-good signals remain economically and temporally defensible after
first later observed Bid/Ask quote and extra entry/exit friction. This does
NOT predict entries, model actual broker fills or calculate realized account
P&L. No original baseline source, cached label, or trace is overwritten.

Offline future-known baseline signals are selected ONCE under zero delay;
never reoptimized using outcomes of a stress scenario. Failed filled trades
occupy a conservative 30s window (NOT the original R9 dynamic stop). No
post-failure position P&L is claimed. Success still requires favorable
>=+$0.10 after fee and friction within 15s and zero initial-liquidation
adverse barrier crossing for all 30s after the ACTUAL delayed quote.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, sys
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

FEE_RAW=20
FAVORABLE_RAW=100
ADVERSE_RAW=100
H15=15000
H30=30000
OFFSET_HOURS=-2   # historical R9 MT5 Feb 2026 source server timestamp -> UTC
TARGET_START=int(dt.datetime(2026,2,2,6,tzinfo=dt.timezone.utc).timestamp()*1000)
TARGET_END=TARGET_START+3600000
# 6-min warm-up source halo, plus post-end 45s for full horizon.
SOURCE_START=TARGET_START-360000
SOURCE_END=TARGET_END+45000
EXPECTED_SOURCE_SHA={
 'R9_REAL_MT5_TESTER':'24e4b31935ead7b0eb039fe84dc8972c59500b362cac21721739f1b0c050b3d7',
 'R9_SYNTH_MT5_TESTER':'dcedb28f7453c80d2dec5ffe5d386dad1661134ba61765337155fbbaeb6213a2',
 'DUKASCOPY_RAW':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d',
}


def sha256(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1<<20),b''): h.update(block)
 return h.hexdigest()


def load_source(path:Path, source:str):
 actual=sha256(path)
 if actual!=EXPECTED_SOURCE_SHA[source]: raise ValueError(f'SOURCE_SHA_MISMATCH {source}: {actual}')
 if source=='DUKASCOPY_RAW':
  f=pd.read_csv(path,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],
                dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
  t=f.timestamp_ms_utc.to_numpy(np.int64)
  b=f.bid_raw.to_numpy(np.int32);a=f.ask_raw.to_numpy(np.int32)
 else:
  f=pd.read_csv(path,compression='gzip',usecols=['time_msc','bid','ask'],
                dtype={'time_msc':'int64','bid':'float64','ask':'float64'})
  t=f.time_msc.to_numpy(np.int64)+OFFSET_HOURS*3600000
  b=np.rint(f.bid.to_numpy()*1000).astype(np.int32)
  a=np.rint(f.ask.to_numpy()*1000).astype(np.int32)
 if not len(t) or np.any(np.diff(t)<0) or np.any(a<b): raise ValueError('INVALID_SOURCE_QUOTE_ORDER')
 lo=np.searchsorted(t,SOURCE_START,side='left');hi=np.searchsorted(t,SOURCE_END,side='right')
 t,b,a=t[lo:hi].copy(),b[lo:hi].copy(),a[lo:hi].copy()
 if len(t)<100 or t[0]>TARGET_START-300000 or t[-1]<TARGET_END+30000:
  raise ValueError('INSUFFICIENT_PREFIX_OR_FUTURE_SOURCE_COVERAGE')
 return t,b,a,actual


@njit(cache=True)
def freeze_delayed_signal_replay(t,b,a, signal_ix,side,latency_ms,slip_raw,
                                 max_fill_staleness_ms=1000):
 """One-position ON SIGNAL-TIMELINE replay, no future oracle rescheduling.

 outcome 1=GOOD,0=FAILED_ASSIGNED_30S,-1=QUOTE_REJECTED,-2=BUSY_SKIP,
 -3=SOURCE_CENSORED; return no earnings for failed or rejected.
 Original 30s full future safety intentionally observed even after TP.
 """
 n=len(t);m=len(signal_ix)
 out=np.empty(m,np.int8);fill_ix=np.full(m,-1,np.int64)
 exit_ix=np.full(m,-1,np.int64);net=np.full(m,-2147483647,np.int32)
 last_exit_ms=-9223372036854775807
 for k in range(m):
  i=signal_ix[k]; now=t[i]
  if now<=last_exit_ms:
   out[k]=-2;continue
  f=i
  if latency_ms>0:
   target=now+latency_ms
   lo=i+1;hi=n
   while lo<hi:
    mid=(lo+hi)//2
    if t[mid]<target:lo=mid+1
    else:hi=mid
   f=lo
  if f>=n or t[f]<now+latency_ms or (latency_ms>0 and t[f]==now):
   out[k]=-1;continue
  if t[f]-(now+latency_ms)>max_fill_staleness_ms or a[f]<b[f] or a[f]-b[f]>1500:
   out[k]=-1;continue
  if t[f]>=TARGET_END:
   out[k]=-1;continue
  fill_ix[k]=f
  side_k=side[k]
  entry=(a[f]+slip_raw) if side_k==1 else (b[f]-slip_raw)
  liquidation0=b[f] if side_k==1 else a[f]
  tp_j=-1; min_liq=9223372036854775807;max_liq=-9223372036854775807
  stale=False;end_cov=False;seen=False;prev_ms=t[f];last_in_window=t[f]
  for j in range(f+1,n):
   if t[j]==t[f]:continue
   if t[j]>t[f]+H30:
    # Match frozen S1: complete raw source beyond horizon, no unobserved
    # >15s boundary gap after last quote that was INSIDE horizon.
    end_cov=(t[j]-last_in_window<=15000 or last_in_window==t[f]+H30)
    break
   if t[j]-prev_ms>15000:stale=True
   prev_ms=t[j];last_in_window=t[j]
   seen=True
   liquidation=b[j] if side_k==1 else a[j]
   if liquidation<min_liq:min_liq=liquidation
   if liquidation>max_liq:max_liq=liquidation
   if tp_j<0 and t[j]<=t[f]+H15:
    close=(b[j]-slip_raw) if side_k==1 else (a[j]+slip_raw)
    v=(close-entry)*side_k-FEE_RAW
    if v>=FAVORABLE_RAW:tp_j=j;net[k]=v
  # Complete when the last source quote lies exactly on the horizon,
  # even without a following quote; otherwise first quote after end
  # provides honest observation of a straddling interquote gap.
  if last_in_window>=t[f]+H30: end_cov=True
  if not end_cov or not seen or stale:
   out[k]=-3;last_exit_ms=t[f]+H30;continue
  safe=(min_liq>liquidation0-ADVERSE_RAW) if side_k==1 else (max_liq<liquidation0+ADVERSE_RAW)
  if tp_j>=0 and safe:
   out[k]=1;exit_ix[k]=tp_j;last_exit_ms=t[tp_j]
  else:
   out[k]=0;last_exit_ms=t[f]+H30
 return out,fill_ix,exit_ix,net


def core_experiment(source_paths:dict,engine_dir:Path,output:Path):
 sys.path.insert(0,str(engine_dir))
 from r12_dense_requote import asof_quote_clocks,_rolling_extrema
 from r12_tp_oracle import quote_tp_first,earliest_finish_schedule
 output.mkdir(parents=True,exist_ok=True)
 all_records=[];source_receipts=[]
 for source,path in source_paths.items():
  t,b,a,source_hash=load_source(path,source)
  ix,flags=asof_quote_clocks(t,b,a)
  q=(t[ix]>=TARGET_START)&(t[ix]<TARGET_END)&((flags&1)!=0)
  ix=ix[q]
  m15,x15,a15,y15,_,_,cov15=_rolling_extrema(t,b,a,ix,H15)
  m30,x30,a30,y30,_,_,cov30=_rolling_extrema(t,b,a,ix,H30)
  gb=(x15.astype(np.int64)>=a[ix].astype(np.int64)+120)&(m30.astype(np.int64)>b[ix].astype(np.int64)-100)&cov15&cov30
  gs=(a15.astype(np.int64)<=b[ix].astype(np.int64)-120)&(y30.astype(np.int64)<a[ix].astype(np.int64)+100)&cov15&cov30
  if np.any(gb&gs):raise AssertionError('TWO_STRICT_SIDES_SAME_EVENT')
  qual=gb|gs;good_ix=ix[qual]; side=np.where(gb[qual],1,-1).astype(np.int8)
  exitix,exitt=quote_tp_first(t,b,a,good_ix,a[good_ix],b[good_ix],side)
  if not len(good_ix) or np.any(exitix<0):raise AssertionError('NO_QUALIFIED_FROZEN_SOURCE')
  selected=earliest_finish_schedule(t[good_ix],exitt)
  sig=good_ix[selected];directions=side[selected]
  if len(sig)>1 and np.any(t[sig[1:]]<=exitt[selected[:-1]]):raise AssertionError('BASE_POSITION_OVERLAP')
  source_receipts.append({'source':source,'source_file':path.name,'source_sha256':source_hash,
   'source_quote_rows_halo':len(t),'qualified_first250_future_known':len(good_ix),
   'baseline_frozen_firstTP_signals':len(sig),
   'source_median_spread_usd':float(np.median(a[(t>=TARGET_START)&(t<TARGET_END)]-b[(t>=TARGET_START)&(t<TARGET_END)]))/1000})
  for lag in (0,50,100,250,500,1000):
   for slip in (0,20,50):
    out,fills,exits,nets=freeze_delayed_signal_replay(t,b,a,sig,directions,lag,slip)
    good=(out==1);accepted=(out==1)|(out==0)|(out==-3)
    # This is a frozen hindsight-signal robustness test, not economic expectancy.
    records={'source':source,'latency_nominal_ms':lag,'entry_and_exit_each_slip_raw_usd_0p001':slip,
     'extra_roundtrip_slippage_usd':2*slip/1000,'baseline_future_selected_signals':len(sig),
     'good_first15_and_safe_full30_at_delayed_quote':int(good.sum()),
     'failed_after_fill':int((out==0).sum()),'source_censored_after_fill':int((out==-3).sum()),
     'quote_reject':int((out==-1).sum()),'busy_after_other_stressed_fill':int((out==-2).sum()),
     'entered_quote':int(accepted.sum()),
     'strict_accuracy_completed_fills_only':float(good.sum()/((out==1)|(out==0)).sum()) if np.any((out==1)|(out==0)) else None,
     'source_R9_SYNTH_06UTC_REFERENCE':104,
     'quota_met_by_strict_correct_delayed_fills':bool(good.sum()>=104),
     'model_future_informed_original_signal':True,'execution_latency_counterfactual_only':True,
     'not_live_broker_fill_or_profit':True}
    all_records.append(records)
    # Every source signal retained for exact forensic reconstruction, not only aggregates.
    if lag in (0,100,500,1000) and slip in (0,50):
     stem=f'{source}_lag{lag}_slip{slip}'
     np.savez_compressed(output/f'{stem}_FROZEN_ORACLE_SIGNAL_STRESS.npz',
       signal_quote_ix=sig,signal_utc_ms=t[sig],source_side=directions,
       delayed_fill_quote_ix=fills,delayed_exit_quote_ix=exits,
       outcome_code=out,modeled_good_exit_net_raw_only=nets)
    if lag==0 and slip==0:
     if int(good.sum())!=len(sig) or int(np.count_nonzero(out!=1)):
      raise AssertionError(f'PARITY_BASELINE_FIRSTTP_{source}_{len(sig)}_{int(good.sum())}')
 with (output/'R12C_ALL_54_SOURCE_LATENCY_SLIPPAGE_SCENARIOS.csv').open('w',newline='') as f:
  import csv
  w=csv.DictWriter(f,fieldnames=list(all_records[0]));w.writeheader();w.writerows(all_records)
 receipt={'research_class':'R12C_FROZEN_HINDSIGHT_SIGNAL_CROSS_SOURCE_EXECUTION_STRESS_NONDEPLOYABLE',
   'baseline_script':'R12BN / R12D-Q original strict full30 future-label / observed first250 future-TP one-position teacher',
   'raw_source_sha_verified':source_receipts,'stress_grid_count':len(all_records),
   'source_hour':'2026-02-02T06:00:00Z','original_reference':104,
   'scenario_rows_sha256':sha256(output/'R12C_ALL_54_SOURCE_LATENCY_SLIPPAGE_SCENARIOS.csv'),
   'no_in_sample_classification_accuracy_claim':True,'no_prospective_entry_policy':True,
   'no_broker_fill_execution_guarantee':True,
   'cannot_claim_account_economic_pnl_on_failed_trade':True,
   'original_research_source_readonly':True,'lossless_signal_traces':'individually source SHA manifest in followup'}
 (output/'R12C_SOURCE_AND_RESULT_RECEIPT.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
 manifest={p.name:{'sha256':sha256(p),'bytes':p.stat().st_size} for p in output.iterdir() if p.is_file() and p.name!='R12C_SHA_MANIFEST.json'}
 (output/'R12C_SHA_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
 return receipt,all_records


def main():
 pa=argparse.ArgumentParser()
 pa.add_argument('--real',type=Path,required=True);pa.add_argument('--synth',type=Path,required=True)
 pa.add_argument('--dukas',type=Path,required=True);pa.add_argument('--engine-dir',type=Path,required=True)
 pa.add_argument('--out',type=Path,required=True)
 a=pa.parse_args()
 rec,rows=core_experiment({'R9_REAL_MT5_TESTER':a.real,'R9_SYNTH_MT5_TESTER':a.synth,'DUKASCOPY_RAW':a.dukas},a.engine_dir,a.out)
 print(json.dumps({'source':rec['raw_source_sha_verified'],'scenarios':len(rows),
                   'first':rows[0], 'last':rows[-1]},indent=2))

if __name__=='__main__':main()

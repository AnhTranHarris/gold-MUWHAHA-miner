"""R22-v2 add-only dual-broker H1V2 source research: nine Dukascopy residual quarters.

READ FIRST: R9 SYNTH is ONLY the contemporaneous activity reference, NOT a
tradable benchmark. Earlier R19/R21 selected times and sides using future quote
paths. R22 also uses future BUY/SELL FIRST-PASSAGE outcomes ONLY for OFFLINE
capacity and NEVER presents those outcomes as an as-of trained entry policy.
Original R9 v5 300s readiness and original R11 strict 15s/SAFE30 stay immutable.
Changed 0/10/15s post-gap and 90/120s first TP are experimental ONLY.
"""
from __future__ import annotations
import csv, json, sys, hashlib
from dataclasses import dataclass
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/data'); LAB=ROOT/'h1v2_r22_nine_residual'
sys.path[:0]=[str(ROOT/'h1v2_r21_dualbroker/src'),str(ROOT/'h1v2_r20_last46/src')]
import r21_quota_aware_interval_exchange as x
import r21_cold_epoch_broker_state as cold
p=x.p
Q=900_000
SOURCES=('DUKASCOPY_RAW','MT5_BROKER_EXPORT')
MONTHS=('01','02','06','07')
BASE_CASE='EVENT30_8_QUOTES_CAP4000'
# No new case is approved for original v5. Every case retains first ACTUAL later
# quote +100ms, max staleness <=1000ms, fee 20 raw, TP +100, adverse 100 raw.
# Horizon changes are after-entry first TP observation, not a future entry signal.
CASES=(
 ('C00_FROZEN_R21_RETEST_30S_8Q_H60',30000,8,60000,4000,100,0),
 ('C01_POSTGAP_15S_8Q_H60',15000,8,60000,4000,100,0),
 ('C02_POSTGAP_10S_8Q_H60',10000,8,60000,4000,100,0),
 ('C03_POSTGAP_0S_8Q_H60',0,8,60000,4000,100,0),
 ('C04_POSTGAP_30S_8Q_H90',30000,8,90000,4000,100,0),
 ('C05_POSTGAP_30S_8Q_H120',30000,8,120000,4000,100,0),
 ('C06_POSTGAP_15S_8Q_H90',15000,8,90000,4000,100,0),
 ('C07_POSTGAP_0S_8Q_H90',0,8,90000,4000,100,0),
 ('C08_POSTGAP_0S_8Q_H120',0,8,120000,4000,100,0),
 ('C09_POSTGAP_0S_1Q_H90_DIAGNOSTIC',0,1,90000,4000,100,0),
 ('C10_POSTGAP_0S_8Q_H90_WIDE8_DIAGNOSTIC',0,8,90000,8000,100,0),
 # Delayed signal 500ms and two-leg 20 raw adverse friction; comparator to C07.
 ('C11_POSTGAP_0S_8Q_H90_LAG500_SLIP20',0,8,90000,4000,500,20),
)


def sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for v in iter(lambda:f.read(1<<20),b''):h.update(v)
 return h.hexdigest()


def before_quote_metrics(t:np.ndarray, ix:np.ndarray):
 """Only ordinals <= observed decision quote i, even with same-ms source duplicates."""
 if not len(ix):return np.empty(0,np.int32),np.empty(0,np.int64)
 # An as-of 30s count must not use any quote from before a >15s raw
 # quote drought. This matters ONLY when testing faster than 30s readiness.
 gap_ix=np.flatnonzero(np.diff(t)>15000).astype(np.int32)+1
 pos=np.searchsorted(gap_ix,ix,side='right')-1
 anchor=np.where(pos>=0,gap_ix[np.maximum(pos,0)],0)
 trailing_start=np.searchsorted(t,t[ix]-30000,side='left')
 start=np.maximum(trailing_start,anchor)
 obs=(ix-start+1).astype(np.int32)
 age=(t[ix]-t[anchor]).astype(np.int64)
 return obs,age


def delay_fill(t,b,a,signal:np.ndarray,lag:int,cap:int):
 """No mid-quote interpolation. Reject stale/unavailable actual future fills."""
 if len(signal)==0:return np.empty(0,np.int32),np.empty(0,np.int32)
 requested=t[signal].astype(np.int64)+lag
 fill=np.searchsorted(t,requested,side='left').astype(np.int64)
 capped=np.minimum(fill,len(t)-1)
 spread=a[capped].astype(np.int64)-b[capped].astype(np.int64)
 ok=(fill<len(t))&(capped>signal)&(t[capped]>t[signal])
 ok&=(t[capped]>=requested)&(t[capped]-requested<=1000)
 ok&=(spread>=0)&(spread<=cap)
 return signal[ok],capped[ok].astype(np.int32)


def trial_from_residual(t,b,a,qkeys,missing,shortest_age=0,atleast=1,cap=4000,lag=100):
 """Source quote admission independent of future outcomes; quote complete order."""
 pieces=[];n_raw=0
 for qi in missing:
  q0=qkeys[int(qi)]*Q
  lo=int(np.searchsorted(t,q0-1000,side='left'))
  hi=int(np.searchsorted(t,q0+Q,side='left'))
  n_raw+=hi-lo
  if hi>lo:pieces.append(np.arange(lo,hi,dtype=np.int32))
 if not pieces:return None,dict(raw=n_raw,distinct=0,eligible=0,filled=0)
 signal=np.unique(np.concatenate(pieces))
 signal=signal[(signal==0)|(t[signal]!=t[np.maximum(signal-1,0)])]
 distinct=len(signal)
 count,age=before_quote_metrics(t,signal)
 spread=a[signal].astype(np.int64)-b[signal].astype(np.int64)
 admitted=(count>=atleast)&(age>=shortest_age)&(spread>=0)&(spread<=cap)
 signal=signal[admitted]
 sig,fill=delay_fill(t,b,a,signal,lag,cap)
 if len(fill):
  qi=t[fill]//Q-qkeys[0]
  inmonth=(qi>=0)&(qi<len(qkeys))
  inmissing=np.isin(qi,missing)
  sig=sig[inmonth&inmissing];fill=fill[inmonth&inmissing]
 if len(fill):
  # A later observed quote cannot be relabeled as multiple independent fills.
  u,first=np.unique(fill,return_index=True)
  signal=sig[first];fill=u.astype(np.int32)
 else:signal=np.empty(0,np.int32)
 return (signal,fill),dict(raw=int(n_raw),distinct=int(distinct),eligible=int(admitted.sum()),filled=int(len(fill)))


def winner_intervals(t,b,a,fills,horizon,slip):
 """Full both-sided STOP/TP/TIMEOUT/CENSORED source paths, future-only teacher."""
 if not len(fills):
  z=np.empty(0,np.int32)
  return z,z.copy(),np.empty(0,np.int8),z.copy(),np.empty((0,2),np.int8),np.empty((0,2),np.int32),np.empty((0,2),np.int32)
 codes,exits,nets=p.independent_both_sides(t,b,a,fills.astype(np.int32),slip,horizon)
 wins=np.argwhere(codes==1)
 wf=fills[wins[:,0]].astype(np.int32)
 we=exits[wins[:,0],wins[:,1]].astype(np.int32)
 sides=np.where(wins[:,1]==0,1,-1).astype(np.int8)
 vals=nets[wins[:,0],wins[:,1]].astype(np.int32)
 if len(wf) and (np.any(t[we]<=t[wf]) or np.any(vals<100)):
  raise AssertionError('CONTRADICTORY_FUTURE_WIN_OR_PRICE')
 return wf,we,sides,vals,codes,exits,nets


def read_baseline(source,mon):
 """Read and compare R21 E immutable full-calendar baseline before doing surgery."""
 t,b,a,_,_,_,proof=p.get_frozen(source,mon)
 refs=p.r18.refs_for_month(mon,ROOT)
 f=ROOT/'h1v2_r21_dualbroker/results'/f'R21E_{source}_{mon}_ALL_BIDASK_SIDE_SOURCE_ORDINALS_WIN_STOP_TIMEOUT_CENSOR.npz'
 with np.load(f,allow_pickle=False) as z:
  oldf=z[BASE_CASE+'__exchanged_global_full_schedule_fill'].astype(np.int32)
  olde=z[BASE_CASE+'__exchanged_global_full_schedule_exit'].astype(np.int32)
 if len(oldf)>1 and np.any(t[oldf[1:]]<=t[olde[:-1]]):raise AssertionError('BASELINE_POSITION_COLLISION')
 qref=refs['qref'];href=refs['href'];qkeys=refs['qkeys']
 counts=np.bincount(t[oldf]//Q-qkeys[0],minlength=len(qref))
 miss=np.flatnonzero((qref>0)&(counts<qref))
 csvname=ROOT/'h1v2_r21_dualbroker/results'/f'R21E_{source}_{mon}_SCENARIOS.csv'
 with csvname.open(newline='') as ff:
  row=next(z for z in csv.DictReader(ff) if z['case']==BASE_CASE)
 if len(oldf)!=int(row['future_selected_monthly_trade_count']):raise AssertionError('R21_E_COUNT_DRIFT')
 if np.count_nonzero((qref>0)&(counts>=qref))!=int(row['quarter_quota_met_after']):raise AssertionError('R21_E_QUARTER_DRIFT')
 hc=counts.reshape(-1,4).sum(axis=1)
 if np.count_nonzero((href>0)&(hc>=href))!=int(row['hour_quota_met_after']):raise AssertionError('R21_E_HOUR_DRIFT')
 return t,b,a,refs,oldf,olde,counts,miss,proof


def run_month(source:str,mon:str,only_duk_rescue=True):
 if source not in SOURCES or mon not in MONTHS:raise ValueError('UNSUPPORTED_SOURCE_OR_MONTH')
 t,b,a,refs,oldf,olde,orig,miss,proof=read_baseline(source,mon)
 qref=refs['qref'];href=refs['href'];qkeys=refs['qkeys'];n=len(qref)
 out=LAB/'results_v2';out.mkdir(parents=True,exist_ok=True)
 records=[];quarters=[];hours=[];days=[];npz={}
 if source=='MT5_BROKER_EXPORT' and only_duk_rescue and len(miss)!=0:raise AssertionError('SOURCE_MT5_NOT_FULL_COVERAGE')
 for name,age_min,min_count,horizon,cap,lag,slip in CASES:
  trial,pre=trial_from_residual(t,b,a,qkeys,miss,age_min,min_count,cap,lag)
  if trial is None:signal=fill=np.empty(0,np.int32)
  else:signal,fill=trial
  wfi,wei,sides,wnets,codes,exits,nets=winner_intervals(t,b,a,fill,horizon,slip)
  newf,newe,diag,before,after,changed=x.local_capacity(t,oldf,olde,qkeys,qref,miss,wfi,wei)
  oldhours=before.reshape(-1,4).sum(axis=1);newhours=after.reshape(-1,4).sum(axis=1)
  if not np.array_equal(before,orig):raise AssertionError('SOURCE_BASELINE_CHANGED')
  if np.any(after<before):raise AssertionError('QUARTER_REGRESSION')
  if len(newf)>1 and np.any(t[newf[1:]]<=t[newe[:-1]]):raise AssertionError('NEW_OVERLAP')
  met=(qref>0)&(after>=qref);hourmet=(href>0)&(newhours>=href)
  rec={'source':source,'month':mon,'scenario':name,'cold_epoch_readiness_ms':age_min,
   'min_observed_quotes_past_30s':min_count,'first_positive_net_horizon_ms':horizon,
   'signal_and_fill_spread_cap_raw':cap,'actual_fill_nominal_latency_ms':lag,
   'slippage_raw_each_leg':slip,'new_trial_quote_ordinal_signals':int(pre['eligible']),
   'new_actual_fill_unique_quote_ordinals':int(len(fill)),
   'future_GOOD_two_sided':int((codes==1).sum()),'observed_STOP_two_sided':int((codes==0).sum()),
   'observed_TIMEOUT_two_sided':int((codes==2).sum()),'source_CENSORED_two_sided':int((codes==-3).sum()),
   'new_hindsight_winner_intervals':int(len(wfi)), 'new_exchanges_applied':len(changed),
   'original_monthly_reference_R9_SYNTH':int(qref.sum()),
   'future_known_monthly_selection':int(len(newf)),
   'active_quarters':int(np.count_nonzero(qref)), 'active_quarter_quota_met':int(met.sum()),
   'active_hours':int(np.count_nonzero(href)), 'active_hour_quota_met':int(hourmet.sum()),
   'remaining_quarter_deficit_slots':int(np.maximum(qref-after,0).sum()),
   'no_COINEXX_live_fill_or_account_PNL':True,'hindsight_side_policy_NOT_CAUSAL':True,
   'original_300s_v5_and_15F30S_UNMODIFIED':True,
   'changed_contract_requires_separate_approval':True}
  records.append(rec)
  for qi,row in enumerate(refs['rows']):
   quarters.append({'source':source,'month':mon,'scenario':name,'utc_quarter':row['utc_quarter'],
     'R9_SYNTH_reference':int(qref[qi]),'original_R21_count':int(before[qi]),
     'R22_hindsight_selected_count':int(after[qi]),
     'deficit':max(0,int(qref[qi]-after[qi])),
     'R22_QUARTER_PASS':int(met[qi]) if qref[qi] else '',
     'future_oracle_not_tradable':True})
  for h in range(len(href)):
   hours.append({'source':source,'month':mon,'scenario':name,'utc_hour':refs['rows'][4*h]['utc_hour'],
       'R9_SYNTH_hour_reference':int(href[h]),'R22_hour_count':int(newhours[h]),
       'R22_HOUR_PASS':int(hourmet[h]) if href[h] else ''})
  for d in range(n//96):
   sl=slice(96*d,96*d+96);r=int(qref[sl].sum());v=int(after[sl].sum())
   days.append({'source':source,'month':mon,'scenario':name,
       'utc_day':refs['rows'][96*d]['utc_quarter'][:10],
       'R9_SYNTH_day_reference':r,'R22_day_count':v,
       'R22_DAY_PASS':int(v>=r) if r else ''})
  # Lossless trial source ordinals, all future loser classes, full intervals.
  for key,value in {'signal':signal,'fill':fill,'code_2side':codes,'exit_2side':exits,
     'net_2side':nets,'future_good_fill':wfi,'future_good_exit':wei,
     'future_good_side':sides,'future_good_net':wnets,
     'source_exact_hindsight_final_fill':newf,'source_exact_hindsight_final_exit':newe}.items():
   npz[name+'__'+key]=value
  print(source,mon,name,'new good',len(wfi),'Q',rec['active_quarter_quota_met'],'/',rec['active_quarters'],
        'H',rec['active_hour_quota_met'],'/',rec['active_hours'], 'missed slots',rec['remaining_quarter_deficit_slots'],flush=True)
 base=f'R22V2_{source}_{mon}'
 paths=[]
 for suffix,data in [('ALL_SCENARIOS',records),('ALL_UTC_QUARTERS',quarters),('ALL_UTC_HOURS',hours),('ALL_UTC_DAYS',days)]:
  fp=out/f'{base}_{suffix}.csv'
  with fp.open('w',newline='',encoding='utf8') as f:
   w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
  paths.append(fp)
 npzf=out/f'{base}_ALL_12_CASES_FULL_QUOTE_ORDINAL_POSITIVE_NEGATIVE_AND_CENSORED.npz'
 np.savez_compressed(npzf,**npz)
 paths.append(npzf)
 rec={'source':source,'month':mon,'orig_hash':p.r18.PINS[source][mon],
     'reference_hash':refs['sha256'],'quotes':len(t),'source_proof':proof,
     'R21_original_historical_selected':int(len(oldf)),
     'R21_original_residual_quarters':int(len(miss)),
     'remaining_quarters':int(len(miss)),'scenarios':records,
     'outputs':{f.name:{'bytes':f.stat().st_size,'sha256':sha(f)} for f in paths},
     'original_R9_v5_unchanged':True,'not_instrument_USD_account_PNL':True,
     'future_hindsight_admission_NOT_CAUSAL':True}
 outfile=out/f'{base}_SOURCE_EXACT_EXECUTION_RECEIPT.json'
 outfile.write_text(json.dumps(rec,indent=2,allow_nan=False)+'\n')
 return rec


def main():
 import argparse
 ar=argparse.ArgumentParser()
 ar.add_argument('--source',choices=SOURCES,required=True)
 ar.add_argument('--month',choices=MONTHS,required=True)
 a=ar.parse_args()
 run_month(a.source,a.month)

if __name__=='__main__': main()

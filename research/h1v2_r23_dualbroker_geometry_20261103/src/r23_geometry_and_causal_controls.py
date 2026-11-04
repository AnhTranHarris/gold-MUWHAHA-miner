"""R23 isolated dual-broker source-ordinal geometry experiments.

ALL prospective admissions/rules use prefix-only observed quotes. R23 expands
hindsight source first-passage target/stop choices; OFFLINE winning-side selection
and quarter interval exchange are still future-privileged and NONDEPLOYABLE.
Old R9, H1V2 R11-R22 data/code/models/outputs are immutable.
"""
from __future__ import annotations
import csv, hashlib, json, sys
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple
import numpy as np
from numba import njit

ROOT=Path('/mnt/data')
LAB=ROOT/'h1v2_r23_dualbroker'; OUT=LAB/'results'
sys.path[:0]=[str(ROOT/'h1v2_r22_nine_residual'),str(ROOT/'h1v2_r21_dualbroker/src'),str(ROOT/'h1v2_r20_last46/src')]
import r22_source_exact_rescue_v2 as r22
Q=900_000
# source, fill cap, readiness count, TP raw quote units, stop raw, horizon ms,
# entry nominal latency ms, per-leg slippage raw. ORIGINAL research fee=20 raw.
# Changed TARGET or STOP creates a NEW experiment, not R9/S1 equivalence.
CASES=(
 ('A1_TP050_STOP100_H60_CAP4000_Q8',4000,8,50,100,60000,100,0),
 ('A2_TP050_STOP100_H90_CAP4000_Q8',4000,8,50,100,90000,100,0),
 ('A3_TP075_STOP100_H90_CAP4000_Q8',4000,8,75,100,90000,100,0),
 ('A4_TP050_STOP100_H90_CAP8000_Q8',8000,8,50,100,90000,100,0),
 ('A5_TP025_STOP100_H90_CAP4000_Q8',4000,8,25,100,90000,100,0),
 ('A6_TP100_STOP150_H90_CAP4000_Q8',4000,8,100,150,90000,100,0),
 ('A7_TP200_STOP100_H90_CAP4000_Q8',4000,8,200,100,90000,100,0),
 ('A8_TP050_STOP100_H90_CAP4000_Q1',4000,1,50,100,90000,100,0),
 ('A9_TP050_STOP100_H90_CAP8000_Q1',8000,1,50,100,90000,100,0),
 ('A10_TP025_STOP100_H120_CAP4000_Q1',4000,1,25,100,120000,100,0),
 ('A11_TP050_STOP100_H90_CAP4000_Q1_LAG500_SLIP20',4000,1,50,100,90000,500,20),
 ('A12_TP100_STOP100_H60_CAP4000_Q8_NEGCTRL',4000,8,100,100,60000,100,0),
)
BASE='C10_POSTGAP_0S_8Q_H90_WIDE8_DIAGNOSTIC'


def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for part in iter(lambda:f.read(1<<20),b''):h.update(part)
 return h.hexdigest()


def sink(path,records):
 if not records:raise ValueError('NO_DATA')
 with Path(path).open('w',newline='',encoding='utf8') as f:
  writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)


@njit(cache=False)
def quote_first_passages(t,b,a,fills,profit_net_raw,stop_liq_raw,horizon,slip_raw):
 """Two-sided executable price path; no missing observations fabricated.

 Return codes 1=TP,0=initial liquidation STOP,2=TIMEOUT,-3=GAP/CENSOR.
 STOP is relative to opening liquidation quote, as in R20, not entry.
 STOP loss includes spread+fee and both-leg slippage. TIMEOUT evaluated at
 first actual quote at/after horizon (if no >15s coverage gap).
 """
 n=len(fills); code=np.full((n,2),-3,np.int8)
 ends=np.full((n,2),-1,np.int32)
 net=np.full((n,2),-2147483647,np.int32)
 for k in range(n):
  f=fills[k];firstms=t[f]
  for si in range(2):
   buy=(si==0)
   entry=a[f]+slip_raw if buy else b[f]-slip_raw
   openliq=b[f] if buy else a[f]
   last=firstms
   for j in range(f+1,len(t)):
    if t[j]==firstms:continue
    if t[j]-last>15000:break
    last=t[j]
    liquidation=b[j] if buy else a[j]
    realized=(liquidation-entry-20-slip_raw) if buy else (entry-liquidation-20-slip_raw)
    if t[j]>firstms+horizon:
     if t[j]-(firstms+horizon)<=15000:
      code[k,si]=2;ends[k,si]=j;net[k,si]=realized
     break
    is_stop=(liquidation<=openliq-stop_liq_raw) if buy else (liquidation>=openliq+stop_liq_raw)
    if is_stop:
     code[k,si]=0;ends[k,si]=j;net[k,si]=realized;break
    if realized>=profit_net_raw:
     code[k,si]=1;ends[k,si]=j;net[k,si]=realized;break
 return code,ends,net


def causal_prefix_features(t,b,a,signal):
 """As-of signal-ordinal-only; never incorporate delayed fill or future event."""
 if len(signal)==0:return {s:np.array([]) for s in ('flow3','flow15','flow60','spread','ema15','ema300','mag3')}
 sp=a.astype(np.int64)-b.astype(np.int64)
 prefix=np.r_[0,np.cumsum(sp,dtype=np.int64)]
 d={}
 for win,label in [(3000,'flow3'),(15000,'flow15'),(60000,'flow60')]:
  j=np.searchsorted(t,t[signal]-win,side='right')-1
  j=np.maximum(0,np.minimum(j,signal))
  valid=t[signal]-t[j]>=win
  # Bid and Ask must agree on sign; otherwise WAIT.
  db=b[signal].astype(np.int64)-b[j].astype(np.int64)
  da=a[signal].astype(np.int64)-a[j].astype(np.int64)
  d[label]=np.where(valid & (db>0)&(da>0),1,np.where(valid&(db<0)&(da<0),-1,0)).astype(np.int8)
  if win==3000:d['mag3']=np.minimum(np.abs(db),np.abs(da)).astype(np.int32)
 for win,label in [(15000,'ema15'),(300000,'ema300')]:
  start=np.searchsorted(t,t[signal]-win,side='left')
  d[label]=(prefix[signal+1]-prefix[start])/np.maximum(signal+1-start,1)
 d['spread']=sp[signal]
 return d


def source_rec(source,mon):
 """Original source SHA/order and source R9 quotas verified by old loader."""
 t,b,a,_,_,_,proof=r22.p.get_frozen(source,mon)
 refs=r22.p.r18.refs_for_month(mon,ROOT)
 k=ROOT/'h1v2_r22_nine_residual/results_v2'/f'R22V2_{source}_{mon}_ALL_12_CASES_FULL_QUOTE_ORDINAL_POSITIVE_NEGATIVE_AND_CENSORED.npz'
 with np.load(k,allow_pickle=False) as z:
  oldf=z[BASE+'__source_exact_hindsight_final_fill'].astype(np.int32)
  olde=z[BASE+'__source_exact_hindsight_final_exit'].astype(np.int32)
 if len(oldf)>1 and np.any(t[oldf[1:]]<=t[olde[:-1]]):raise AssertionError('R22_BASELINE_OVERLAP')
 qref=refs['qref'];href=refs['href'];qkeys=refs['qkeys']
 counts=np.bincount(t[oldf]//Q-qkeys[0],minlength=len(qref))
 miss=np.flatnonzero((qref>0)&(counts<qref))
 return t,b,a,refs,oldf,olde,counts,miss,proof


def quarter_description(t,b,a,qkeys,qref,baseline_count,missing,source,mon):
 report=[]
 for qi in missing:
  q0=qkeys[qi]*Q;q1=q0+Q
  left=int(np.searchsorted(t,q0,side='left'));right=int(np.searchsorted(t,q1,side='left'))
  gap=(np.diff(t[left:right]) if right-left>1 else np.array([],dtype=np.int64))
  sp=a[left:right].astype(np.int64)-b[left:right].astype(np.int64)
  s='NO_QUOTE' if not len(sp) else 'ACTIVE_QUOTE'
  report.append({'source':source,'month':mon,'utc_quarter':__import__('datetime').datetime.fromtimestamp(q0/1000,__import__('datetime').timezone.utc).strftime('%Y-%m-%dT%H:%M:00Z'),
    'r9_SYNTH_exact_reference':int(qref[qi]),'frozen_R22_C10_selected':int(baseline_count[qi]),
    'missing':int(max(0,qref[qi]-baseline_count[qi])),'source_raw_quotes_in_quarter':right-left,
    'first_quote_ms_after_quarter_start':int(t[left]-q0) if right>left else '',
    'last_quote_ms_before_quarter_end':int(q1-t[right-1]) if right>left else '',
    'median_spread_quoteUSD':round(float(np.median(sp))/1000,6) if len(sp) else '',
    'p90_spread_quoteUSD':round(float(np.quantile(sp,0.9))/1000,6) if len(sp) else '',
    'fraction_raw_spread_gt4':round(float(np.mean(sp>4000)),7) if len(sp) else '',
    'fraction_raw_spread_gt8':round(float(np.mean(sp>8000)),7) if len(sp) else '',
    'raw_interquote_gap_gt15s':int((gap>15000).sum()),'raw_quote_state':s})
 return report


def test_case(t,b,a,refs,oldf,olde,basecount,missing,source,mon,case,cache):
 name,cap,minquotes,tp,stop,horizon,lag,slip=case
 qkeys=refs['qkeys'];qref=refs['qref'];href=refs['href']
 cachekey=(cap,minquotes,lag)
 if cachekey not in cache:
  qdata,pre=r22.trial_from_residual(t,b,a,qkeys,missing,shortest_age=0,atleast=minquotes,cap=cap,lag=lag)
  if qdata is None:signal=fill=np.array([],dtype=np.int32)
  else:signal,fill=qdata
  cache[cachekey]=(signal,fill,pre)
 signal,fill,pre=cache[cachekey]
 codes,ends,nets=quote_first_passages(t,b,a,fill,tp,stop,horizon,slip)
 success=np.argwhere(codes==1)
 trialf=fill[success[:,0]].astype(np.int32)
 triale=ends[success[:,0],success[:,1]].astype(np.int32)
 trialsides=np.where(success[:,1]==0,1,-1).astype(np.int8)
 trialnets=nets[success[:,0],success[:,1]].astype(np.int32)
 if len(trialf)>0 and (np.any(t[triale]<=t[trialf]) or np.any(trialnets<tp)):
  raise AssertionError('WIN_EXECUTABLE_PATH_FAILURE')
 fullf,fulle,diags,before,after,changed=r22.x.local_capacity(t,oldf,olde,qkeys,qref,missing,trialf,triale)
 if not np.array_equal(before,basecount):raise AssertionError('R22_BASE_COUNT_DRIFT')
 if len(fullf)>1 and np.any(t[fullf[1:]]<=t[fulle[:-1]]):raise AssertionError('ONE_POSITION_VIOLATION')
 if np.any(after<before):raise AssertionError('QUARTER_REGRESSION')
 oldhour=basecount.reshape(-1,4).sum(axis=1);newhour=after.reshape(-1,4).sum(axis=1)
 feats=causal_prefix_features(t,b,a,signal)
 # actually selected signal side from PAST 3s or 15s flow, never future-known teacher.
 # We do not force a trade if flow is flat/mixed; this is a localized shadow
 # diagnostic on the missing-quarter candidate set, not whole-month policy.
 sigside=feats['flow3']
 eligible=(sigside!=0)
 # mapping filled unique -> corresponding source signal is deterministic R22.
 code3=np.where(sigside==1,codes[:,0],np.where(sigside==-1,codes[:,1],-4))
 net3=np.where(sigside==1,nets[:,0],np.where(sigside==-1,nets[:,1],-2147483647))
 # Signal-derived as-of spread relief and agreed flow must be observed at signal.
 relief=feats['spread']<=(.8*feats['ema300'])
 flow_quality=eligible&relief&(feats['mag3']>=np.maximum(25,0.2*feats['spread']))
 def flow_diag(mask):
  x=code3[mask];nn=net3[mask]
  completed=(x==1)|(x==0)|(x==2)
  viable=np.flatnonzero(mask&((code3==1)|(code3==0)|(code3==2)))
  valid=nn[completed]
  return {'admitted':int(mask.sum()),'good':int((x==1).sum()),'stopped':int((x==0).sum()),'timedout':int((x==2).sum()),
    'censored':int((x==-3).sum()),'conditional_GOOD_fraction_completed':(float((x==1).sum()/completed.sum()) if completed.any() else None),
    'mean_quoted_price_net_per_completed':(float(valid.mean()/1000) if len(valid) else None),
    'sum_quoted_price_net_completed':(float(valid.sum()/1000) if len(valid) else None)}
 shadow={'PAST3S_SIGNED_BIDASK':flow_diag(eligible),'PAST3S_SIGNED_AND_SPREAD_RELIEF':flow_diag(flow_quality)}
 winning_spreads=(a[trialf].astype(np.int64)-b[trialf].astype(np.int64)) if len(trialf) else np.array([],np.int64)
 source_spread=(a[fill].astype(np.int64)-b[fill].astype(np.int64)) if len(fill) else np.array([],np.int64)
 action={'source':source,'month':mon,'scenario':name,'source_quote_SHA':r22.p.r18.PINS[source][mon],
  'r9_ref_month':int(qref.sum()),'r22_C10_before_volume':int(len(oldf)),
  'new_quoted_target_net_raw':tp,'new_open_liq_stop_raw':stop,
  'new_exit_horizon_ms':horizon,'signal_fill_spread_cap_raw':cap,
  'observed_quote_min_past30s_since_lastgap':minquotes,'fill_delay_ms':lag,'slip_each_leg_raw':slip,
  'new_source_candidates_before_spread':int(pre['distinct']),'new_quote_eligible':int(pre['eligible']),
  'new_unique_actual_filled_quote_ordinals':int(len(fill)),
  'raw_two_sided_GOOD':int((codes==1).sum()),'raw_two_sided_STOP':int((codes==0).sum()),
  'raw_two_sided_TIMEOUT':int((codes==2).sum()),'raw_two_sided_CENSORED':int((codes==-3).sum()),
  'future_good_interval_offline_count':len(trialf),'historical_future_selected_after_exchange':len(fullf),
  'historical_new_exchanges':len(changed),
  'active_quarters':int((qref>0).sum()),'active_quarter_count_met':int(((qref>0)&(after>=qref)).sum()),
  'active_hours':int((href>0).sum()),'active_hour_count_met':int(((href>0)&(newhour>=href)).sum()),
  'quarter_deficit_slots':int(np.maximum(qref-after,0).sum()),
  'filled_spread_median_quoteUSD':(float(np.median(source_spread))/1000 if len(source_spread) else None),
  'winning_candidate_spread_median_quoteUSD':(float(np.median(winning_spreads))/1000 if len(winning_spreads) else None),
  'shadow_PAST3S_sign_correct_completed':shadow['PAST3S_SIGNED_BIDASK']['conditional_GOOD_fraction_completed'],
  'shadow_PAST3S_mean_net_quoteUSD':shadow['PAST3S_SIGNED_BIDASK']['mean_quoted_price_net_per_completed'],
  'shadow_PAST3S_RELIEF_sign_correct_completed':shadow['PAST3S_SIGNED_AND_SPREAD_RELIEF']['conditional_GOOD_fraction_completed'],
  'shadow_PAST3S_RELIEF_mean_net_quoteUSD':shadow['PAST3S_SIGNED_AND_SPREAD_RELIEF']['mean_quoted_price_net_per_completed'],
  'no_causal_policy_from_future_side':True,'not_real_broker_fill':True,'no_original_R9_modified':True}
 qr=[];hr=[];dr=[]
 for qi,original in enumerate(refs['rows']):
  qr.append({'source':source,'month':mon,'scenario':name,'utc_quarter':original['utc_quarter'],
   'original_R9_SYNTH_reference':int(qref[qi]),'R22_C10_before':int(basecount[qi]),
   'R23_after':int(after[qi]),'R23_quarter_pass':int(after[qi]>=qref[qi]) if qref[qi] else '',
   'R23_quarter_deficit':int(max(0,int(qref[qi])-int(after[qi]))),
   'source_future_selected_not_causal':True})
 for h in range(len(href)):
  hr.append({'source':source,'month':mon,'scenario':name,'utc_hour':refs['rows'][4*h]['utc_hour'],
   'R9_SYNTH_hour_reference':int(href[h]),'R22_C10_before':int(oldhour[h]),
   'R23_hindsight_after':int(newhour[h]),'hour_pass':int(newhour[h]>=href[h]) if href[h] else ''})
 for d in range(len(qref)//96):
  sl=slice(d*96,(d+1)*96);base=int(basecount[sl].sum());value=int(after[sl].sum());ref=int(qref[sl].sum())
  dr.append({'source':source,'month':mon,'scenario':name,'utc_day':refs['rows'][96*d]['utc_quarter'][:10],
    'R9_SYNTH_day_reference':ref,'R22_C10_day_before':base,'R23_hindsight_day_after':value,
    'day_pass':int(value>=ref) if ref else ''})
 oracle={'signal_source_quote_ordinal':signal,'actual_fill_quote_ordinal':fill,
  'both_side_stop_target_timeout_censor_code':codes,'both_side_actual_observed_exit_quote_ordinal':ends,
  'both_side_quoted_price_net_after_entry_exit_slip_and_fee':nets,
  'prefix_sign_3s_at_signal':sigside,'prefix_flow_quality_at_signal':flow_quality,
  'OFFLINE_future_win_fill_ordinal':trialf,'OFFLINE_future_win_exit_ordinal':triale,
  'OFFLINE_future_win_side':trialsides,'OFFLINE_future_win_net_quote_price_raw':trialnets,
  'OFFLINE_full_month_final_fill_ordinal':fullf,'OFFLINE_full_month_final_exit_ordinal':fulle}
 return action,qr,hr,dr,diags,shadow,oracle


def run_month(source,mon):
 OUT.mkdir(parents=True,exist_ok=True)
 t,b,a,refs,oldf,olde,base,missing,proof=source_rec(source,mon)
 qref=refs['qref'];qkeys=refs['qkeys']
 forensic=quarter_description(t,b,a,qkeys,qref,base,missing,source,mon)
 allactions=[];allq=[];allh=[];alld=[];allshadow=[];interval=[];npz={};cache={}
 for case in CASES:
  action,qr,hr,dr,diag,shadow,oracle=test_case(t,b,a,refs,oldf,olde,base,missing,source,mon,case,cache)
  allactions.append(action);allq.extend(qr);allh.extend(hr);alld.extend(dr)
  allshadow.append({'source':source,'month':mon,'scenario':case[0],**shadow})
  for row in diag:interval.append({'source':source,'month':mon,'scenario':case[0],**row})
  for name,values in oracle.items():
   # For full-quarter-complete broker controls these two arrays are identical
   # across all counterfactuals (no experiment is triggered). Persist one
   # hashable copy rather than 24 redundant half-million-row copies.
   if not len(missing) and name in ('OFFLINE_full_month_final_fill_ordinal','OFFLINE_full_month_final_exit_ordinal'):
    npz['FROZEN_R22_C10__'+name]=values
   else:
    npz[case[0]+'__'+name]=values
  print('R23',source,mon,case[0],'eligible',action['new_quote_eligible'], 'winners',action['future_good_interval_offline_count'],
   'Q',action['active_quarter_count_met'],'/',action['active_quarters'],'remaining',action['quarter_deficit_slots'],flush=True)
 stem=f'R23_{source}_{mon}'
 paths=[]
 for suffix,rows in [('CASES',allactions),('COMPLETE_QUARTERS',allq),('COMPLETE_HOURS',allh),('COMPLETE_DAYS',alld),('SOURCE_ORIGINAL_MISSING_QUARTER_FORENSICS',forensic),('EXACT_INDEPENDENT_INTERVAL_SOURCE_UPPERS',interval)]:
  if rows:
   file=OUT/f'{stem}_{suffix}.csv';sink(file,rows);paths.append(file)
 file=OUT/f'{stem}_ALL_12_CASES_SOURCE_ORDINAL_OUTCOMES_BOTH_SIDES_POSITIVE_NEGATIVE_CENSORED.npz'
 np.savez_compressed(file,**npz);paths.append(file)
 shadowpath=OUT/f'{stem}_PREENTRY_CAUSAL_SHADOW_DIAGNOSTICS.json'
 shadowpath.write_text(json.dumps(allshadow,indent=2,allow_nan=False)+'\n');paths.append(shadowpath)
 receipt={'source':source,'month':mon,'exact_quote_rows':len(t),'verified_source_SHA':r22.p.r18.PINS[source][mon],
  'actual_quote_source_contract':proof,'reference_source_sha':refs['sha256'],
  'r22_C10_original_hindsight_count':len(oldf),'r22_C10_deficient_quarters':int(len(missing)),
  'completed_scenarios':len(allactions),'complete_month_quarters_per_scenario':len(qref),
  'complete_month_hours_per_scenario':len(refs['href']),
  'causal_shadow': 'PAST-only deterministic signals, local missing-quarter diagnostic; NO full-calendar trading policy',
  'all_source_scenario_rows':allactions,
  'source_results':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths},
  'original_R22_R21_R9_unchanged':True,'historical_future_oracle_not_deployable':True}
 outfile=OUT/f'{stem}_FULL_SOURCE_EXACT_SHA_AND_SCIENCE_RECEIPT.json'
 outfile.write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
 return receipt


if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--source',choices=r22.SOURCES,required=True);ap.add_argument('--month',choices=r22.MONTHS,required=True)
 a=ap.parse_args();run_month(a.source,a.month)

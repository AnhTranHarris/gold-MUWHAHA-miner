"""R12-DENSE: new AS-OBSERVED quote-ordinal candidate universes, exact S1 labels.

This is a NEW hypothetical HINDSIGHT oracle with observable intrabin entry
quotes, source quote histories >15s reset and >=300s warmup, spread <=$1.50.
Everything after the decision remains OFFLINE future-only labels/TP exits.
R9 v2 250ms live runtime remains unchanged, no claim of 50ms real deployment.

Three distinct causal candidate clocks inside R12 experiment:
 A. first actually OBSERVED quote of each source 50ms interval
 B. original first 250ms plus first subsequent >=$0.02 spread-narrowed quote
 C. all actually OBSERVED distinct millisecond source quote states
The three are separately scored future-informed and never summed.

Exact source original S1 _rolling_extrema is imported from independently
hashed immutable full S1 source bytes, never copied from memory.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,os,sys,time,zipfile
from pathlib import Path
import numpy as np
from numba import njit
from r12_tp_oracle import (load_labels,read_raw,quote_tp_first,earliest_finish_schedule,
                          write_csv,sha,quarter_key,hour_key,FAV_RAW,FEE_RAW)

ROOT=Path('/mnt/data');OUT=ROOT/'h1v2_r12/results';UPSTREAM=ROOT/'h1v2_r12/upstream'
UPSTREAM_SHA={'entry_survivability.py':'c52de41072911ad53dedadfb3dba1899ea112e41a9e58e48ea29a7903e3ec475',
              'entry_contract.py':'b720a609eb13bc025a706b8fe1601e4fa8d1df9fa9908eb808222f5ac96d34cb'}
for name,expected in UPSTREAM_SHA.items():
 if sha(UPSTREAM/name)!=expected:raise RuntimeError('UPSTREAM_ORIGINAL_SOURCE_DRIFT '+name)
sys.path.insert(0,str(UPSTREAM))
from entry_survivability import _rolling_extrema

@njit(cache=True)
def asof_quote_clocks(t,b,a):
 """Past-only clock generation. flags bit1 original first250, 2 first50,
 bit4 first250+first observed later 250ms bin narrow by >=$0.02.
 Each decision only occurs AFTER the quote at that ordinal is observed.
 """
 n=len(t);ix=np.empty(n,np.int64);flags=np.empty(n,np.int8);count=0
 if not n:return ix[:0],flags[:0]
 epoch=t[0];last250=-9223372036854775807;last50=-9223372036854775807
 firstspread=0;firstnarrow=False
 for i in range(n):
  if i and t[i]-t[i-1]>15000:epoch=t[i]
  curr250=t[i]//250;curr50=t[i]//50
  changed250=(curr250!=last250);changed50=(curr50!=last50)
  if changed250:firstspread=a[i]-b[i];firstnarrow=False
  last250=curr250;last50=curr50
  if i and t[i]==t[i-1]:continue  # explicit no same-ms fill convention
  if t[i]-epoch<300000:continue
  spread=a[i]-b[i]
  if spread<0 or spread>1500:continue
  bit=0
  if changed250:bit|=1;bit|=4
  if changed50:bit|=2
  if (not changed250) and not firstnarrow and spread<=firstspread-20:
   bit|=4;firstnarrow=True
  ix[count]=i;flags[count]=bit;count+=1
 return ix[:count],flags[:count]

def load_original_s1_labels(mon):
 path=next(ROOT.glob(f'R11S_{mon}_FULLMONTH_FIXED15_30_SURVIVAL_FULLPOP_LABELS_CALENDARS_SOURCE_20261103.zip'))
 with zipfile.ZipFile(path) as z:
  name=next(s for s in z.namelist() if s.endswith('_ALL_V5_CANDIDATE_H15_H30_EXACT_SURVIVAL_LABELS.npz'))
  blob=z.read(name)
 with np.load(io.BytesIO(blob),allow_pickle=False) as a:
  v={k:a[k].copy() for k in ('source_tick_ordinal','h15_BUY_survives_and_favorable','h15_SELL_survives_and_favorable',
    'h30_BUY_survives_no_adverse','h30_SELL_survives_no_adverse','h30_coverage')}
 return v,hashlib.sha256(blob).hexdigest()

def run(mon):
 start=time.time();OUT.mkdir(parents=True,exist_ok=True)
 frozen=load_labels(mon);t,b,a=read_raw(mon)
 all_ix,flags=asof_quote_clocks(t,b,a)
 assert len(all_ix)>len(frozen['ix']) and np.all(all_ix[1:]>all_ix[:-1])
 orig,orig_sha=load_original_s1_labels(mon)
 assert orig_sha==frozen['labels_sha256']
 base_ix=orig['source_tick_ordinal'];pos=np.searchsorted(all_ix,base_ix)
 assert np.array_equal(all_ix[pos],base_ix),('original first250 missing',mon)
 assert np.array_equal(all_ix[(flags&1)!=0],base_ix),('first250 ASOF parity failure',mon)
 # Original S1 monotonic raw-ordinal extrema used unmodified; new observed
 # candidate population means 15/30 labels MUST be independently recomputed.
 mn15,mx15,na15,xa15,n15,age15,cov15=_rolling_extrema(t,b,a,all_ix,15000)
 mn30,mx30,na30,xa30,n30,age30,cov30=_rolling_extrema(t,b,a,all_ix,30000)
 ib=b[all_ix].astype(np.int64);ia=a[all_ix].astype(np.int64)
 gB=(mx15.astype(np.int64)>=ia+120)&(mn30.astype(np.int64)>ib-100)&cov15&cov30
 gS=(na15.astype(np.int64)<=ib-120)&(xa30.astype(np.int64)<ia+100)&cov15&cov30
 assert not np.any(gB&gS),('both directions strict good',mon)
 oldB=orig['h15_BUY_survives_and_favorable']&orig['h30_BUY_survives_no_adverse']&orig['h30_coverage']
 oldS=orig['h15_SELL_survives_and_favorable']&orig['h30_SELL_survives_no_adverse']&orig['h30_coverage']
 assert np.array_equal(gB[pos],oldB) and np.array_equal(gS[pos],oldS),('ORIGINAL S1 LABEL CONTRACT PARITY FAILED',mon)
 # Compute exits for ALL strict-good new eligible as-of candidate ordinals.
 valid=gB|gS;goodix=all_ix[valid];goodflag=flags[valid];gs=np.where(gB[valid],1,-1).astype(np.int8)
 goodtime=t[goodix];eb=b[goodix];ea=a[goodix]
 exits,exit_t=quote_tp_first(t,b,a,goodix,ea,eb,gs)
 assert np.all(exits>=0) and np.all(exit_t>goodtime) and np.all(exit_t<=goodtime+15000)
 liq=np.where(gs>0,b[exits],a[exits]).astype(np.int64)
 net=(liq-np.where(gs>0,ea,eb))*gs-20
 assert np.all(net>=100)
 old_base_mask=(goodflag&1)!=0
 assert int(np.count_nonzero(old_base_mask))==len(frozen['t'])
 variants={'FIRST250_REFERENCE':1,'FIRST50_OBSERVED':2,'INTRABIN_SPREAD_NARROW':4,'ALL_DISTINCT_MS_OBSERVED':0}
 refs=list(csv.DictReader(open(OUT/f'R12_{mon}_ALL_UTC_QUARTERS_WITH_R9_SYNTH_VERIFIED.csv',newline='',encoding='utf8')))
 for _,r in enumerate(refs):assert r['R9_SYNTH_exact_15min_reference']!='UNVERIFIED_PENDING_TICK_SOURCE'
 allrows=[];variant_meta={};partial=[]
 for variant,bit in variants.items():
  mask=np.ones(len(goodix),bool) if bit==0 else ((goodflag&bit)!=0)
  ii=np.flatnonzero(mask);local_time=goodtime[ii];local_exit=exit_t[ii]
  sel=ii[earliest_finish_schedule(local_time,local_exit)]
  if len(sel)>1:assert np.all(goodtime[sel[1:]]>exit_t[sel[:-1]])
  if variant=='FIRST250_REFERENCE':
   assert len(sel)=={'01':88233,'02':82027,'06':101889,'07':75928}[mon],('frozen R12 first250 maxcount regression',mon)
   expected=[int(r['entry_tick_ordinal']) for r in csv.DictReader(open(OUT/f'R12_{mon}_ALL_EXECUTABLE_FIRSTTP_SELECTED_SOURCE_QUOTE_TRACES.csv'))]
   assert np.array_equal(goodix[sel],np.asarray(expected,np.int64)),('first250 original selected ordinals not reproduced',mon)
  selected_n=len(sel)
  quarterselected={}
  for k in sel:
   key=quarter_key(goodtime[k]);quarterselected[key]=quarterselected.get(key,0)+1
  qarr=goodtime[ii]//900000
  breakpoints=np.r_[0,np.flatnonzero(np.diff(qarr))+1,len(qarr)]
  upper={};validqt={};
  for s,e in zip(breakpoints[:-1],breakpoints[1:]):
   bb=int(qarr[s]);validqt[bb]=e-s
   upper[bb]=len(earliest_finish_schedule(local_time[s:e],local_exit[s:e]))
  qmet=0;qbad=0;missed=0
  for row in refs:
   key=row['utc_quarter'];ref=int(row['R9_SYNTH_exact_15min_reference']);
   bucket=int(__import__('datetime').datetime.strptime(key,'%Y-%m-%dT%H:%M:00Z').replace(tzinfo=__import__('datetime').timezone.utc).timestamp())//900
   chosen=quarterselected.get(key,0);cap=upper.get(bucket,0)
   covered=int(chosen>=ref) if ref else ''
   impossible=int(cap<ref) if ref else ''
   qmet+=int(covered) if covered!='' else 0
   qbad+=int(impossible) if impossible!='' else 0
   missed+=int(ref>cap or ref>chosen) if ref else 0
   if variant!='FIRST250_REFERENCE':
    allrows.append({'month':'2026-'+mon,'utc_quarter':key,'utc_hour':row['utc_hour'],'variant':variant,
       'r9_SYNTH_original_entry_ref':ref,'s1_ORIGINAL_SAFE30_FAV15_QUOTE_EVENT_CANDIDATE_COUNT':int(validqt.get(bucket,0)),
       'hindsight_firstTP_selected':chosen,'quarter_isolated_optimistic_upper':cap,
       'reaches_original_quarter_reference':covered,'source_isolated_quarter_impossible':impossible,
       'not_a_causal_student':True})
  # Preserve every individual new selected entry source ordinal; no sample.
  if variant!='FIRST250_REFERENCE':
   trace=[]
   for k in sel:
    trace.append({'month':'2026-'+mon,'variant':variant,'entry_utc_ms':int(goodtime[k]),
      'entry_tick_ordinal':int(goodix[k]),'exit_utc_ms':int(exit_t[k]),'exit_tick_ordinal':int(exits[k]),
      'entry_UTC_quarter':quarter_key(goodtime[k]),'entry_UTC_hour':hour_key(goodtime[k]),
      'side':int(gs[k]),'entry_bid_raw':int(eb[k]),'entry_ask_raw':int(ea[k]),
      'exit_liquidation_raw':int(liq[k]),'source_nominal_net_after_fee_raw':int(net[k]),
      'hold_ms':int(exit_t[k]-goodtime[k]),'ASOF_event_clock_bit_flags':int(goodflag[k]),
      'S1_good15_safe30_verified_from_complete_source_quotes':True,'future_selected_not_causal':True})
   tracep=OUT/f'R12D_{mon}_{variant}_FULL_SELECTED_QUOTE_TRACES.csv';write_csv(tracep,trace,list(trace[0]));partial.append(tracep)
  variant_meta[variant]={'observed_event_strict_good_count':int(mask.sum()),'selected_one_position_firstTP_count':selected_n,
       'r9_active_quarter_reference_count':sum(int(r['R9_SYNTH_exact_15min_reference'])>0 for r in refs),
       'quotas_reached_in_source_active_quarters':qmet,'isolated_source_impossible_quarters':qbad,
       'quota_misses_all_reasons':missed}
  print(mon,variant,variant_meta[variant],flush=True)
 qpath=OUT/f'R12D_{mon}_FULL_DENSE_THREE_ASOF_CLOCK_15MIN_MATRIX.csv';write_csv(qpath,allrows,list(allrows[0]));partial.append(qpath)
 # Full source quote ordinal label arrays must survive restarts and be hash-pinned.
 orig_rows=np.flatnonzero(valid)
 npz=OUT/f'R12D_{mon}_ALL_OBSERVED_INTRA250MS_EXACT_H15_H30_LABELS.npz'
 np.savez_compressed(npz,raw_candidate_tick_ordinal=all_ix,
       asof_candidate_clocks_flag=flags,entry_UTC_ms=t[all_ix],
       strict_good15_safe30_BUY=gB,strict_good15_safe30_SELL=gS,
       quote_covered15=cov15,quote_covered30=cov30,
       strict_good_row_index_in_all_candidates=orig_rows,
       strict_good_firstTP_exit_tick_ordinal=exits,
       strict_good_firstTP_exit_utc_ms=exit_t)
 partial.append(npz)
 result={'month':mon,'raw_source_SHA256':{'01':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
  '02':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d',
  '06':'34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2',
  '07':'e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7'}[mon],
  'original_S1_frozen_NPZ_SHA256':orig_sha,'observed_distinct_ms_eligible_candidate_events':len(all_ix),
  'original_first250_candidate_count':len(base_ix),
  'original_first250_exact_source_ordinal_AND_both_sides_S1_label_parity':True,
  'all_observed_good15_safe30_count':len(goodix),
  'original_strict_first250_good15_safe30_count':int(old_base_mask.sum()),
  'new_distinct_ms_good15_safe30_candidate_count':int(len(goodix)-old_base_mask.sum()),
  'variants':variant_meta,'source_quote_bid_ask_tp_all_positive_net_confirmed':True,
  'original_R9_15min_quarter_source_verified_all_hours':True,
  'trade_fill_latency_spread_slippage':'NOT_VERIFIED',
  'fitted_asof_student':'NOT_TRAINED',
  'full_source_member_sha256':{v.name:sha(v) for v in partial},
  'elapsed_seconds':round(time.time()-start,2)}
 p=OUT/f'R12D_{mon}_FULL_COMPLETE_DENSE_REQUOTE_ORACLE_RECEIPT.json';p.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2),flush=True)
 return result

if __name__=='__main__':
 x=argparse.ArgumentParser();x.add_argument('--month',choices=['01','02','06','07'],required=True);a=x.parse_args();run(a.month)

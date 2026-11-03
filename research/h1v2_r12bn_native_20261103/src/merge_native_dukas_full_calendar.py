#!/usr/bin/env python3
"""Lossless full 11,520-quarter / 2,880-hour source-domain cross-evaluation.
Never imply two feed-origin hindsight schedules can be combined into executable fills.
"""
import csv,json,hashlib
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path('/mnt/data');OUT=ROOT/'h1v2_r12_native/reports'

def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def read(p):return list(csv.DictReader(open(p,newline='',encoding='utf-8')))
def write(p,rows):
 with open(p,'w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),extrasaction='raise');w.writeheader();w.writerows(rows)

def main():
 orig=read(ROOT/'R12DQ_COMPLETE_ALL_11520_SOURCE_QUARTERS_S4_R12_R12DQ.csv')
 assert len(orig)==11520
 native=[]
 for m in ('01','02','06','07'):
  a=read(OUT/f'R12BN_{m}_COMPLETE_ORIGINAL_R9_QUARTERS_SYNTH_NATIVE.csv')
  assert len(a) in (2688,2880,2976)
  native+=a
 assert len(native)==len(orig)
 arr=[];h=defaultdict(list);mm=defaultdict(Counter)
 for o,n in zip(orig,native):
  assert o['utc_quarter']==n['utc_quarter'] and o['month']==n['month']
  assert int(o['original_R9_SYNTH_15min_reference'])==int(n['r9_SYNTH_EXACT_15M_reference'])
  ref=int(o['original_R9_SYNTH_15min_reference']);duk=int(o['R12DQ_dense_firstTP_selected']);nat=int(n['r12b_NATIVE_testlog_ALL_DISTINCT_SELECTED']);first=int(n['r12b_NATIVE_testlog_FIRST250_selected'])
  dukmet=(duk>=ref) if ref else None;natmet=(nat>=ref) if ref else None
  res={'month':o['month'],'utc_quarter':o['utc_quarter'],'utc_hour':o['utc_hour'],
      'source_verified_original_R9_SYNTH_15min_reference':ref,
      'S4_Dukascopy_original_fixed30_future_selected':int(o['S4_fixed30_selected']),
      'R12_Dukascopy_original_first250_FIRSTTP_future_selected':int(o['R12_original_firstTP_250ms_selected']),
      'R12DQ_Dukascopy_all_distinctms_FIRSTTP_future_selected':duk,
      'R12BN_native_testlog_FIRST250_FIRSTTP_future_selected':first,
      'R12BN_native_testlog_all_distinctms_FIRSTTP_future_selected':nat,
      'R12DQ_Dukascopy_quota_met':int(dukmet) if dukmet is not None else '',
      'R12BN_SynthNative_quota_met':int(natmet) if natmet is not None else '',
      'BOTH_sources_meet_same_quarter_independently':int(dukmet and natmet) if ref else '',
      'AT_LEAST_ONE_independent_source_has_capacity_NOT_EXECUTABLE_UNION':int(dukmet or natmet) if ref else '',
      'neither_source_hindsight_quota_met':int(not dukmet and not natmet) if ref else '',
      'source_domain_restriction':'separate standalone future-selected source paths; NEVER blend quotes or fills',
      'synthetic_testlog_not_real_MT5_broker_ticks':True,'no_causal_forecast_or_actual_PnL_proof':True}
  arr.append(res);h[o['utc_hour']].append(res)
  if ref:
   k=mm[o['month']];k['active_quarters']+=1;k['R9_source_ref']+=ref
   k['Dukas']+=int(dukmet);k['Native']+=int(natmet);k['Neither']+=int(not dukmet and not natmet);k['Both']+=int(dukmet and natmet)
 hour=[]
 for t,rs in sorted(h.items()):
  ref=sum(x['source_verified_original_R9_SYNTH_15min_reference'] for x in rs);d=sum(x['R12DQ_Dukascopy_all_distinctms_FIRSTTP_future_selected'] for x in rs);n=sum(x['R12BN_native_testlog_all_distinctms_FIRSTTP_future_selected'] for x in rs);f=sum(x['R12BN_native_testlog_FIRST250_FIRSTTP_future_selected'] for x in rs)
  assert len(rs)==4
  hour.append({'month':rs[0]['month'],'utc_hour':t,'reference_R9_SYNTH':ref,'Dukascopy_R12DQ_future_selected':d,
               'SynthNative_R12BN_future_selected':n,'SynthNative_R12BN_FIRST250_future_selected':f,
               'Dukascopy_hour_met':int(d>=ref) if ref else '', 'Native_hour_met':int(n>=ref) if ref else '',
               'Dukas_quarters_met':sum(x['R12DQ_Dukascopy_quota_met']==1 for x in rs),
               'Native_quarters_met':sum(x['R12BN_SynthNative_quota_met']==1 for x in rs),
               'source_domain_status':'two independent and incompatible source domains; hindsight only'})
 assert len(hour)==2880
 for x in hour:
  if x['reference_R9_SYNTH']:mm[x['month']]['active_hours']+=1;mm[x['month']]['Dukas_hour']+=x['Dukascopy_hour_met'];mm[x['month']]['Native_hour']+=x['Native_hour_met']
 write(OUT/'R12BN_DUKAS_COMPLETE_ALL_11520_QUARTERS_INDEPENDENT_SOURCE_DOMAIN_EVIDENCE.csv',arr)
 write(OUT/'R12BN_DUKAS_COMPLETE_ALL_2880_HOURS_INDEPENDENT_SOURCE_DOMAIN_EVIDENCE.csv',hour)
 fail=[x for x in arr if x['neither_source_hindsight_quota_met']==1];orig_fail=[x for x in arr if x['R12DQ_Dukascopy_quota_met']==0]
 native_fail=[x for x in arr if x['R12BN_SynthNative_quota_met']==0]
 assert len(orig_fail)==208 and len(native_fail)==1
 assert not fail
 assert sum(v['active_quarters'] for v in mm.values())==7521
 assert sum(v['R9_source_ref'] for v in mm.values())==117585
 outputs={p.name:{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(OUT.glob('*SOURCE_DOMAIN_EVIDENCE.csv'))}
 res={'experiment':'R12BN_FOUR_MONTH_R9_SYNTH_NATIVE_QUOTE_HISTORY_CROSS_DOMAIN_HINDSIGHT',
      'classification':'RESEARCH_HINDSIGHT_ONLY','R9_SYNTH_reference_exact_15min_all_quarters':117585,
      'whole_UTC_quarters':11520,'whole_UTC_hours':2880,'source_R9_active_15min_quarters':7521,
      'per_month_complete':{m:dict(v) for m,v in sorted(mm.items())},
      'DUKAS_R12DQ_source_15min_quota_met':sum(v['Dukas'] for v in mm.values()),
      'SYNTH_NATIVE_R12BN_source_15min_quota_met':sum(v['Native'] for v in mm.values()),
      'SYNTH_NATIVE_SOURCE_historical_only_shortfall_quarter':native_fail,
      'NEITHER_source_has_hindsight_capacity_active_quarters':len(fail),
      'BOTH_source_independent_15min_quota_achieved':sum(v['Both'] for v in mm.values()),
      'DUKAS_R12DQ_source_hour_quota_met':sum(v['Dukas_hour'] for v in mm.values()),
      'SYNTH_NATIVE_R12BN_source_hour_quota_met':sum(v['Native_hour'] for v in mm.values()),
      'critical_nonclaim':'A hypothetical union across two incompatible quote sources is NOT an executable portfolio and proves ZERO joint live capability.',
      'synthetic_mt5_strategy_tester':True,'not_broker_real_ticks':True,'no_actual_latency_slippage_margin_equity':True,
      'original_H1V2_R11_R12_R12DQ_untouched':True,
      'full_source_daily_trace_NPZ_preserved':True,'manifest_outputs':outputs}
 path=OUT/'R12BN_ALL_FOUR_SOURCES_COMPLETE_DIAGNOSTIC_RECEIPT.json';path.write_text(json.dumps(res,indent=2,allow_nan=False)+'\n');print(json.dumps({k:v for k,v in res.items() if k not in ['SYNTH_NATIVE_SOURCE_historical_only_shortfall_quarter','manifest_outputs']},indent=2))
if __name__=='__main__':main()

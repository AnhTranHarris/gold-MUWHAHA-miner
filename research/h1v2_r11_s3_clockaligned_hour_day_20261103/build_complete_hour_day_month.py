#!/usr/bin/env python3
"""Reconcile all four frozen H1V2-R11S UTC-clock-corrected source-hour budgets
and all 36 true same-month fitted R11S2 policy traces. NO future labels in
policy selection. Original hindsight schedules ARE future-informed; keep separate.
This program does NOT train a new fitted classifier, optimize R9 exits, or certify
live/OOS behavior. It is an exact aggregation, independent parity check and a
new source-exact hour-granular student-versus-oracle deficit matrix.
"""
from __future__ import annotations
import csv,hashlib,json,os,zipfile,datetime as dt
from pathlib import Path
import numpy as np

DATA = Path(os.getenv('R11_SOURCE_ROOT','/mnt/data'))
OUT = Path(os.getenv('R11S3_OUT','/mnt/data/h1v2_r11_s3_hourly_20261103'))
MONTHS=('01','02','06','07')
SOURCE_ROOT = DATA/'h1v2_r11_s2_full_month/replay'
UTC=dt.timezone.utc

def sha_bytes(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def sha_file(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(2**20),b''):h.update(block)
 return h.hexdigest()
def dumpjson(p,obj):p.write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
def writecsv(p,rows,cols):
 with p.open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=cols,extrasaction='raise');w.writeheader();w.writerows(rows)
def unixtohour(ms:int)->str:
 return dt.datetime.fromtimestamp(ms/1000,tz=UTC).strftime('%Y-%m-%dT%H:00:00Z')
def checked_json(z,name):return json.loads(z.read(name))
def _safe_pct(n,d):return None if d==0 else n/d

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 hourly=[];daily=[];month_records=[];model_hour=[];model_day=[];model_month=[]
 inputs=[]; failure_hours=[]; exact_checks=[]
 for month in MONTHS:
  archive=next(iter(sorted(DATA.glob(f'R11S_{month}_COMPLETE_CLOCK_CORRECTED_SOURCE_EXACT*20261103.zip'))),None)
  if archive is None:raise FileNotFoundError(f'missing source archive {month}')
  with zipfile.ZipFile(archive) as z:
   assert z.testzip() is None, f'ZIP CRC {archive}'
   meta=checked_json(z,'CLOCK_CORRECTED_SOURCE_EXACT_IMMUTABLE_SHA256_MANIFEST.json')
   assert meta['month_2026']==month
   assert int(meta['source_clock_correction_shift_hour'])==(-2 if month in ('01','02') else -3)
   memberpins=meta['source_complete_CSV_JSON_NPZ_PY_file_sha256']
   for name,pin in memberpins.items():
    b=z.read(name)
    assert len(b)==pin['bytes'] and sha_bytes(b)==pin['sha256'],(month,name)
   cmp=checked_json(z,f'full_results/R11S_{month}_UTC_DAY_HOUR_SOURCE_EXACT_R9_SYNTH_COMPARISON.json')
   capacity=checked_json(z,f'full_results/R11S_{month}_HOUR_QUOTA_CAPACITY_COMPLETE_V2.json')
   risk=checked_json(z,f'full_results/R11S_{month}_SIX_ADVERSE_RISK_BUDGET_SURVIVAL_FULL_UTC_HOUR_DAY_PARETO.json')
   occupancy=checked_json(z,f'full_results/R11S_{month}_FOUR_RESERVATION_FULL_HOURLY_DAY_FRONTIER.json')
   unsafe=checked_json(z,f'full_results/R11S_{month}_NO_ADVERSE_VETO_ABSOLUTE_HOURLY_QUOTA_BOUND.json')
   assert len(cmp['every_UTC_hour_in_month_including_no_trade'])==len(capacity['all_calendar_hours'])
   c_hours=cmp['every_UTC_hour_in_month_including_no_trade']
   cap_hours=capacity['all_calendar_hours'];calendar_n=len(c_hours)
   n=calendar_n
   assert n in (672,720,744)
   risk_hour={key:{h['utc_hour_start']:h for h in v['all_calendar_hours']} for key,v in risk['all_variants'].items()}
   occ_hour={key:{h['utc_hour_start']:h for h in v['calendar_hourly']} for key,v in occupancy['variants'].items()}
   uns_hours={h['utc_hour_start']:h for h in unsafe['full_calendar_hours']}
   assert all(len(x)==n for x in [*risk_hour.values(),*occ_hour.values(),uns_hours])
   cmpday={d['utc_day']:d for d in cmp['every_UTC_day_in_month_including_no_trade']}
   assert len(cmpday)==len(cmp['every_UTC_day_in_month_including_no_trade'])
   for ch,ca in zip(c_hours,cap_hours):
    t=ch['utc_hour_start'];assert t==ca['utc_hour_start']
    ref=int(ch['r9_synth_entry_count'])
    assert ref==int(ca['r9_synth_reference_entries'])
    lower=int(ca['r11_hour_interior_optimal_capacity']);upper=int(ca['r11_independent_hour_upper_bound_with_boundary_crossing'])
    glob=int(ca['r11_global_max_count_scheduler_entries'])
    assert lower<=upper,(month,t,lower,upper)
    assert bool(ca['strict_hourly_impossible_even_with_crossing'])==(ref>upper), (month,t,ref,upper)
    row={'month':'2026-'+month,'utc_hour_start':t,'utc_day':ch['utc_day'],'hour_utc':ch['UTC_hour'],
         'clock_shift_server_to_UTC_hours':meta['source_clock_correction_shift_hour'],
         'R9_SYNTH_reference':ref,'R9_SYNTH_reference_active':int(ref>0),
         'R11_strict_15fav_30surv_original_global_hindsight_selected':glob,
         'R11_strict_30s_hour_interior_constructive_MAX':lower,
         'R11_strict_30s_hour_crossing_optimistic_UPPER':upper,
         'R11_global_scheduler_meets_exact_hour_reference':int(glob>=ref) if ref else '',
         'R11_interior_constructive_meets_exact_hour_reference':int(lower>=ref) if ref else '',
         'R11_impossible_even_independent_hour_crossing':int(ref>upper),
         'R11_interior_entry_deficit_if_reference_active':max(0,ref-lower) if ref else '',
         'R11_interior_entry_surplus_if_reference_active':max(0,lower-ref) if ref else '',
         'R11_independent_hour_upper_bound_deficit':max(0,ref-upper) if ref else '',
         'R11_legacy_15sec_reserve15_oracle_global':ch['r11_SURVIVE15_FAV15_RESERVE15'],
         'R11_legacy_30sec_reserve30_oracle_global':ch['r11_SURVIVE30_FAV30_RESERVE30'],
         'R11_strict_30sec_reserve30_oracle_global':ch['r11_SURVIVE30_FAV15_RESERVE30']}
    for k,record in risk_hour.items():
     v=record[t];assert v['r9_synth_entries']==ref
     row[k+'_interior_max']=v['hour_interior_nonoverlap_count']
     row[k+'_cross_upper']=v['independent_hour_crossing_upper_count']
     row[k+'_impossible']=int(ref>int(v['independent_hour_crossing_upper_count']))
    for k,record in occ_hour.items():
     v=record[t];assert v['r9_synth_entries']==ref
     row[k+'_interior_max']=v['r11_guaranteed_no_cross_hour_entries']
     row[k+'_cross_upper']=v['r11_hourly_upper_bound_if_crossing_allowed']
    u=uns_hours[t];assert u['r9_synth_entries']==ref
    row['UNSAFE_NO_ADVERSE_VETO_interior_max']=u['hindsight_fav15_30s_full_obs_no_adverse_veto_interior_count']
    row['UNSAFE_NO_ADVERSE_VETO_cross_upper']=u['independent_hour_upper_count']
    hourly.append(row)
    if ref>upper:failure_hours.append({'month':month,'utc_hour_start':t,'reference':ref,'max_possible_with_original_strict_horizon':upper,'unavoidable_deficit':ref-upper})
   for day,x in cmpday.items():
    row={'month':'2026-'+month,'utc_day':day,'clock_shift_hours':meta['source_clock_correction_shift_hour'],
         'R9_SYNTH_reference':x['r9_synth_entry_count'],
         'reference_active':int(x['r9_synth_entry_count']>0),
         'strict_15fav30surv_global_hindsight':x['r11_SURVIVE30_FAV15_RESERVE30'],
         'global_meets_reference':int(x['r11_SURVIVE30_FAV15_RESERVE30']>=x['r9_synth_entry_count']) if x['r9_synth_entry_count'] else ''}
    for k,v in risk['all_variants'].items():
     d=next(a for a in v['all_calendar_days'] if a['utc_day']==day)
     row[k+'_interior']=d['hour_interior_nonoverlap_count']
    for k,v in occupancy['variants'].items():
     d=next(a for a in v['calendar_daily'] if a['utc_day']==day)
     row[k+'_interior']=d['r11_hour_allocated_entries']
    daily.append(row)
   assert sum(int(x['R9_SYNTH_reference']) for x in hourly if x['month']=='2026-'+month)==meta['corrected_UTC_month_synth_count']
   assert sum(int(x['R11_strict_15fav_30surv_original_global_hindsight_selected']) for x in hourly if x['month']=='2026-'+month)==meta['R11S_original_30s_reserve_hindsight_count']
   houractive=sum(x['R9_SYNTH_reference_active'] for x in hourly if x['month']=='2026-'+month)
   hrsfail=sum(x['R11_impossible_even_independent_hour_crossing'] for x in hourly if x['month']=='2026-'+month)
   assert houractive==capacity['metrics']['synth_active_utc_hours'] and hrsfail==capacity['metrics']['hours_proven_impossible_30s_reservation_even_allow_cross_hour']
   # Reconstruct exact fitted-policy hour/day table directly from the original
   # source-index ordinal selection traces. No model re-fit, no revised labels.
   receipt_path=SOURCE_ROOT/f'R11S2_{month}_FULLSOURCE_IN_SAMPLE_15S30S_RANKING_RECEIPT.json'
   receipt=json.loads(receipt_path.read_text())
   ref_hour={r['utc_hour_start']:r['R9_SYNTH_reference'] for r in hourly if r['month']=='2026-'+month}
   for fraction,p in receipt['policies'].items():
    slug=fraction.replace('.', 'p')
    trace_path=SOURCE_ROOT/f'R11S2_{month}_FITMONTH_FRACTION{slug}_30SEC_TRACE.npz'
    if not trace_path.exists():raise FileNotFoundError(trace_path)
    with np.load(trace_path,allow_pickle=False) as trace:
     t=trace['entry_utc_ms'].copy(); good=trace['hindsight_class'].copy(); cens=trace['source_censor'].copy();side=trace['BUY_side'].copy()
    assert len(t)==p['selected_nonoverlap_30s']
    assert np.all(np.diff(t)>30000),('single-position 30s reservation mismatch',month,fraction)
    assert int((good==2).sum())==p['survive30_and_favorable15']
    assert int((good==1).sum())==p['survive30_without_favorable15']
    assert int(((good==0)&(~cens)).sum())==p['adverse30']
    assert int(cens.sum())==p['censored_unscored']
    counts={};goodcount={};badcount={};neucount={};censcount={};buycount={}
    for i,ts in enumerate(t):
     h=unixtohour(int(ts)); counts[h]=counts.get(h,0)+1
     if good[i]==2:goodcount[h]=goodcount.get(h,0)+1
     elif good[i]==1:neucount[h]=neucount.get(h,0)+1
     elif not cens[i]:badcount[h]=badcount.get(h,0)+1
     if cens[i]:censcount[h]=censcount.get(h,0)+1
     if side[i]:buycount[h]=buycount.get(h,0)+1
    for h,ref in ref_hour.items():
     ncount=counts.get(h,0);ngood=goodcount.get(h,0);nbad=badcount.get(h,0);nneu=neucount.get(h,0);ncens=censcount.get(h,0)
     den=ncount-ncens
     model_hour.append({'month':'2026-'+month,'utc_hour_start':h,'model_fit_scope':'SAME_MONTH_400K_PER_SIDE_SYSTEMATIC_SAMPLE','fraction':fraction,
       'R9_SYNTH_reference':ref,'R11S2_model_trades_30s_nooverlap':ncount,'R11S2_model_STRICT_15fav30surv':ngood,
       'R11S2_model_ADVERSE30':nbad,'R11S2_model_NEUTRAL':nneu,'R11S2_model_CENSORED':ncens,'R11S2_model_BUY':buycount.get(h,0),
       'survival_precision_on_completed':_safe_pct(ngood,den),
       'meets_hour_reference':int(ncount>=ref) if ref else '', 'meets_strict80pct':int(ngood/den>=.8) if den else '',
       'joint_hour_reference_and_strict80':int(ncount>=ref and den>0 and ngood/den>=.8) if ref else ''})
    for d in sorted(set(h[:10] for h in ref_hour)):
     drows=[x for x in model_hour if x['month']=='2026-'+month and x['fraction']==fraction and x['utc_hour_start'].startswith(d)]
     assert len(drows)==24
     n=sum(x['R11S2_model_trades_30s_nooverlap'] for x in drows)
     g=sum(x['R11S2_model_STRICT_15fav30surv'] for x in drows)
     bad=sum(x['R11S2_model_ADVERSE30'] for x in drows)
     neu=sum(x['R11S2_model_NEUTRAL'] for x in drows);cen=sum(x['R11S2_model_CENSORED'] for x in drows)
     ref=sum(x['R9_SYNTH_reference'] for x in drows)
     model_day.append({'month':'2026-'+month,'utc_day':d,'fraction':fraction,'R9_SYNTH_reference':ref,'R11S2_model_trades':n,'strict_15fav30surv':g,'adverse30':bad,'neutral30':neu,'censored':cen,
                      'survival_precision_on_completed':_safe_pct(g,n-cen),
                      'joint_day_ref_and_strict80':int(ref>0 and n>=ref and n>cen and g/(n-cen)>=.8)})
    model_month.append({'month':'2026-'+month,'fraction':fraction,'original_fit_receipt':p,
                        'raw_model_trace_file':trace_path.name,'trace_sha256':sha_file(trace_path)})
   month_records.append({'month':'2026-'+month,'source_original_clock_corrected_archive':archive.name,'source_zip_sha256':sha_file(archive),
    'source_clock_shift_hours':meta['source_clock_correction_shift_hour'],'original_label_source_sha256':meta['original_label_source_sha256'],
    'source_R9_SYNTH_direct_id_index':meta['source_R9_SYNTH_direct_id_index'],
    'full_original_manifest':meta,'original_R11S2_models_and_9_policy_results':receipt})
   exact_checks.append({'month':month,'zip_crc':True,'all_manifest_member_sha256':len(memberpins),'utc_hour_rows':calendar_n,
                        'strict_cap_impossible_hours':hrsfail,'source_active_syn_hours':houractive,
                        'model_policies':len(receipt['policies']),'all_model_traces_rechecked':True})
  inputs.append({'month':month,'original_zip_file':str(archive),'sha256':sha_file(archive)})
 assert len(hourly)==2880 and len(daily)==120 and len(model_hour)==2880*9 and len(model_day)==120*9 and len(model_month)==36,(len(hourly),len(daily),len(model_hour),len(model_day))
 assert sum(x['R11_impossible_even_independent_hour_crossing'] for x in hourly)==sum(x['strict_cap_impossible_hours'] for x in exact_checks)
 writecsv(OUT/'ALL_2880_UTC_HOURLY_CAUSAL_STUDENT_ORACLE_QUOTA_AND_RISK.csv',hourly,list(hourly[0]))
 writecsv(OUT/'ALL_120_UTC_DAILY_CAUSAL_STUDENT_ORACLE_QUOTA_AND_RISK.csv',daily,list(daily[0]))
 writecsv(OUT/'ALL_25920_UTC_HOURLY_STUDENT_REPLAY_36_POLICIES.csv',model_hour,list(model_hour[0]))
 writecsv(OUT/'ALL_1080_UTC_DAILY_STUDENT_REPLAY_36_POLICIES.csv',model_day,list(model_day[0]))
 dumpjson(OUT/'ALL_36_MONTHLY_FITTED_POLICY_FULL_SOURCE_RECEIPTS.json',model_month)
 dumpjson(OUT/'ALL_FOUR_COMPLETE_ORIGINAL_MANIFESTS_AND_FIT_RESULTS.json',month_records)
 dumpjson(OUT/'ALL_SOURCE_EXACT_EXECUTION_PARITY_CHECKS.json',exact_checks)
 dumpjson(OUT/'ALL_PROVEN_30SEC_HOURLY_IMPOSSIBILITY_WITNESSES.json',failure_hours)
 complete={'research_classification':'R11S3_COMPLETE_CLOCK_ALIGNED_HOURLY_DAILY_MONTHLY_ORACLE_AND_FITTED_STUDENT_PARITY_FULL_DATA_NOT_FRESH_FIT',
           'month_source_count':4,'calendar_hours':len(hourly),'calendar_days':len(daily),'student_policy_hour_rows':len(model_hour),
           'student_policy_day_rows':len(model_day),'student_policies':len(model_month),
           'exact_30second_single_position_reservation':True,'hindsight_original_future_oracle_is_not_a_classifier':True,
           'synth_broker_server_clock_corrected_to_UTC':True,
           'source_archives':inputs,
           'monthly':[{**x,'month_R9_SYNTH_corrected':sum(int(r['R9_SYNTH_reference']) for r in hourly if r['month']=='2026-'+x['month']),
                       'hourly_safe_oracle_30s_impossible':x['strict_cap_impossible_hours']} for x in exact_checks],
           'limits':['historical hindsight future labels are intentionally privileged, not an executable entry rule',
                     'prior student is trained on 400k systematic rows per month and side, scores 100% month, not full 4M rows fit',
                     'monthly source native R9 SYNTH reference may differ from UTC-clock aligned same calendar month due boundary shifts',
                     'greater tolerance >0.10 original stop permits larger excursions and does NOT satisfy original survivability criterion',
                     '15/20/25s reservation may overlap another 30s tracked window: counterfactual only',
                     'no holding/exit optimization or portfolio profitability here']}
 dumpjson(OUT/'EXECUTION_VERIFICATION_INDEX.json',complete)
 # SHA manifest of all produced files including code; excludes self to avoid recursion.
 outputs=[p for p in OUT.iterdir() if p.is_file() and p.name not in ('NEW_R11S3_ALL_FILE_SHA256_MANIFEST.json','RUN_STDOUT.json','RUN_STDERR.log')]
 pins={p.name:{'size':p.stat().st_size,'sha256':sha_file(p)} for p in sorted(outputs)}
 dumpjson(OUT/'NEW_R11S3_ALL_FILE_SHA256_MANIFEST.json',{'source_months':list(MONTHS),'member_sha256':pins,'source_archives':inputs,'test_result':'ALL_EXACT_PARITY_ASSERTIONS_PASS','read_only_source':True})
 print(json.dumps({'completed':True,'hours':len(hourly),'days':len(daily),'student_hourly':len(model_hour),'student_daily':len(model_day),'impossible_hour_witnesses':len(failure_hours),'source_verification':exact_checks,'files':pins},indent=2))
if __name__=='__main__':main()

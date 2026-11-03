"""Lossless source-exact R11S4 vs R12 first-TP 11,520 quarter-hour merge.
R9 SYNTH 15-min original entry counts are rebuilt from each daily source gzip,
not interpolated. Append-only derived artifacts; no previous source mutation.
"""
from __future__ import annotations
import csv,datetime as dt,hashlib,io,json,zipfile
from collections import Counter
from pathlib import Path
from r12_tp_oracle import write_csv,sha
ROOT=Path('/mnt/data');OUT=ROOT/'h1v2_r12/results'
MONTHS=('01','02','06','07')
S4_SHA='fba5a62a4d77d09450a9ac00522cff2532664a5e4d466573cb2a5694bec711fc'

def merge():
 s4_path=ROOT/'R11S4_ALL_FOUR_COMPLETE_HOUR_DAY_MONTH_STRICT_15FAV_30SURV_HINDSIGHT_20261103.zip'
 assert sha(s4_path)==S4_SHA
 out=[];full_hour=[];bad=[];month=[];evidence=[]
 with zipfile.ZipFile(s4_path) as archive:
  assert archive.testzip() is None
  for m in MONTHS:
   orig=Counter();n_s4=0
   with io.StringIO(archive.read(f'month_{m}/R11S4_{m}_FULL_SELECTED_SOURCE_TRACE.csv').decode()) as f:
    for r in csv.DictReader(f):
     assert int(r['strict15fav30surv'])==1
     k=int(r['entry_utc_ms'])//900000;orig[k]+=1;n_s4+=1
   receipt=json.loads((OUT/f'R12_{m}_FULL_RESEARCH_RECEIPT.json').read_text())
   assert n_s4==receipt['old_S4_global_30s_selected']
   source=json.loads((OUT/f'R12_{m}_SYNTH_QUARTER_FULL_SOURCE_RECEIPT_FAST.json').read_text())
   assert source['exact_source_hourly_parity_all_hours']
   qrows=list(csv.DictReader(open(OUT/f'R12_{m}_ALL_UTC_QUARTERS_WITH_R9_SYNTH_VERIFIED.csv',encoding='utf-8',newline='')))
   hr=list(csv.DictReader(open(OUT/f'R12_{m}_ALL_UTC_HOURS.csv',encoding='utf-8',newline='')))
   assert len(qrows)==len(hr)*4
   n_ref=0;n_s4_ref=0;n_r12=0;n_strict_impossible=0;n_quarter_met=0;n_active=0
   hour_aggregate={h['utc_hour']:{'reference':0,'original_s4':0,'r12':0} for h in hr}
   for q in qrows:
    time_q=dt.datetime.strptime(q['utc_quarter'],'%Y-%m-%dT%H:%M:00Z').replace(tzinfo=dt.timezone.utc)
    bucket=int(time_q.timestamp()*1000)//900000
    src=int(q['R9_SYNTH_exact_15min_reference']); r12=int(q['R12_first_TP_global_maxcount_quarter_selected']);old=int(orig.get(bucket,0))
    cap=int(q['R12_first_TP_isolated_quarter_upper']);n_ref+=src;n_s4_ref+=old;n_r12+=r12;n_active+=int(src>0)
    iso_bad=int(src>cap) if src else 0;got=int(r12>=src) if src else None
    if iso_bad:n_strict_impossible+=1
    if got:n_quarter_met+=1
    line={'month':'2026-'+m,'utc_quarter':q['utc_quarter'],'utc_hour':q['utc_hour'],'quarter_ordinal':q['quarter_ordinal_in_hour'],
     'ORIGINAL_R9_SYNTH_UTC_ENTRY_REFERENCE':src,'ORIGINAL_R11S4_30SEC_FIXED_SELECTED':old,
     'R12_FIRSTTP_GLOBAL_GREEDY_SELECTED':r12,'R12_FIRSTTP_ISOLATED_QUARTER_UPPER':cap,
     'R12_FIRSTTP_SOURCE_STRICT_CANDIDATES':q['R12_first_TP_candidate_count_in_quarter'],
     'R9_active_quarter':int(src>0),'ORIGINAL_S4_MEETS_R9_QUARTER':int(old>=src) if src else '',
     'R12_MEETS_R9_QUARTER':got if src else '',
     'R12_QUARTER_PROVEN_CAPACITY_INFEASIBLE':iso_bad,'R12_QUARTER_MISSED_BUT_ISOLATED_FEASIBLE':int(not iso_bad and r12<src) if src else '',
     'R12_QUARTER_REFERENCE_DEFICIT':max(0,src-r12),
     'PERSISTENCE':'FUTURE_PRIVILEGED_HINDSIGHT_ONLY_30S_STRICT_S1_ENTRY_FIRST_TP_OCCUPANCY'}
    out.append(line)
    if src>r12:bad.append(line.copy())
    h=hour_aggregate[q['utc_hour']];h['reference']+=src;h['original_s4']+=old;h['r12']+=r12
   for h in hr:
    agg=hour_aggregate[h['utc_hour']]
    assert agg['reference']==int(h['r9_synth_hour_reference'])
    assert agg['r12']==int(h['R12_first_TP_global_maxcount_hourly_selected'])
    assert agg['original_s4']==int(h['R11S4_original_30s_selected'])
    full_hour.append({**h,**{'source_rebuilt_original_R9_15min_sum':agg['reference'],
                                'source_rebuilt_original_S4_15min_sum':agg['original_s4'],
                                'source_rebuilt_R12_15min_sum':agg['r12']}})
   assert n_ref==receipt['total_R9_SYNTH_UTC_hour_reference']
   assert n_s4_ref==n_s4 and n_r12==receipt['selected_first_TP_maxcount_global']
   assert n_strict_impossible==source['R12_quarters_source_infeasible_first_TP']
   assert n_quarter_met==source['R12_quarters_meeting_100pct_R9_SYNTH']
   month.append({'month':'2026-'+m,'source_all_UTC_quarters':len(qrows),'R9_active_UTC_quarters':n_active,
                 'R9_SYNTH_original_source_entries':n_ref,'R11S4_original_fixed30_selected':n_s4,
                 'R12_firstTP_selected':n_r12,'R12_quarters_meet_quota':n_quarter_met,
                 'R12_quarters_cap_infeasible':n_strict_impossible,
                 'S4_quarters_meet_quota':sum(int(x['ORIGINAL_S4_MEETS_R9_QUARTER']) for x in out if x['month']=='2026-'+m and x['ORIGINAL_S4_MEETS_R9_QUARTER']!='')})
   evidence.append({'month':m,'S4_archive_SHA':S4_SHA,'S4_original_selected_trace_sha256':hashlib.sha256(archive.read(f'month_{m}/R11S4_{m}_FULL_SELECTED_SOURCE_TRACE.csv')).hexdigest(),
     'R12_quarter_SOURCE_SHA':sha(OUT/f'R12_{m}_ALL_UTC_QUARTERS_WITH_R9_SYNTH_VERIFIED.csv'),
     'R9_original_entry_trace_SHA':sha(OUT/f'R12_{m}_ORIGINAL_R9_SYNTH_ALL_ENTRY_EVENTS_CLOCKALIGNED_UTC.csv'),
     'R12_firstTP_selected_trace_SHA':sha(OUT/f'R12_{m}_ALL_EXECUTABLE_FIRSTTP_SELECTED_SOURCE_QUOTE_TRACES.csv')})
 assert len(out)==11520 and len(full_hour)==2880 and len(bad)==240
 assert sum(int(x['R12_QUARTER_PROVEN_CAPACITY_INFEASIBLE']) for x in bad)==239
 assert sum(int(x['R12_QUARTER_MISSED_BUT_ISOLATED_FEASIBLE']) for x in bad)==1
 assert sum(x['R9_SYNTH_original_source_entries'] for x in month)==117585
 assert sum(x['R12_firstTP_selected'] for x in month)==348077
 p=OUT/'R12_ALL_11520_EXACT_UTC_QUARTERS_R9_S4_TP_FULL_MATRIX.csv';write_csv(p,out,list(out[0]))
 q=OUT/'R12_ALL_240_QUARTERHOURLY_FAILURE_WITNESSES.csv';write_csv(q,bad,list(bad[0]))
 x=OUT/'R12_ALL_2880_VERIFIED_UTC_HOURS_WITH_15MIN_PARITY.csv';write_csv(x,full_hour,list(full_hour[0]))
 y=OUT/'R12_ALL_FOUR_MONTH_QUARTER_SOURCE_AUDIT.csv';write_csv(y,month,list(month[0]))
 result={'original_R9_SYNTH_full_month_entry_totals':117585,'S4_original_fixed30_selected':145401,'R12_full_source_firstTP_selected':348077,
         'all_four_month_clock_corrected_hour_rows':2880,'all_four_month_exact_quarter_rows':11520,
         'all_four_R9_active_quarter_source_count':sum(x['R9_active_UTC_quarters'] for x in month),
         'all_four_R12_quarter_exact_met':sum(x['R12_quarters_meet_quota'] for x in month),
         'all_four_original_S4_quarter_met':sum(x['S4_quarters_meet_quota'] for x in month),
         'all_four_R12_source_proven_impossible_quarters':239,
         'all_four_R12_missed_feasible_under_isolated_quarter_bound':1,
         'original_source_months':month,'original_file_sha256_evidence':evidence,
         'source_SHA256_outputs':{v.name:sha(v) for v in (p,q,x,y)},
         'statistical_interpretation':'HINDSIGHT_SELECTION_CAN_EXPLOIT_FUTURE_AND_IS_NOT_A_LEARNED_ACTION_POLICY',
         'source_domain':'Dukascopy quote vs Coinexx SYNTH reference; quote feeds DIFFER'}
 r=OUT/'R12_COMPLETE_FOUR_MONTH_11520_QUARTER_EXECUTION_RECEIPT.json';r.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ('original_file_sha256_evidence','source_SHA256_outputs')},indent=2))
 print('FILES', {a.name:sha(a) for a in (p,q,x,y,r)},flush=True)
 return result

if __name__=='__main__':merge()

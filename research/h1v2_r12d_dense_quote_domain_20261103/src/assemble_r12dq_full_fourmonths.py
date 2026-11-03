"""R12D-Q: immutable 11,520-quarter and 2,880-hour full-source reconciliation.

Requires four completed raw quote-verified R12D-Q receipts and source quarter
matrix; never infers a quarter quota by dividing the hour count. Outputs all
calendar quarters including 0-entry periods, full missing certificate rows,
monthly source-clock exactness and cryptographic hashes. Research only.
"""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
from collections import defaultdict
ROOT=Path('/mnt/data/h1v2_r12/results')
MONTHS=('01','02','06','07')
ORIG_R9={'01':27980,'02':33523,'06':31758,'07':24324}
FULL_QUARTERS={'01':2976,'02':2688,'06':2880,'07':2976}


def digest(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def readcsv(path):
 with open(path,newline='',encoding='utf8') as f:return list(csv.DictReader(f))

def writecsv(path,rows):
 assert rows
 with open(path,'w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),extrasaction='raise');w.writeheader();w.writerows(rows)

def run():
 base=readcsv(ROOT/'R12_ALL_11520_EXACT_UTC_QUARTERS_R9_S4_TP_FULL_MATRIX.csv')
 assert len(base)==11520
 baseline={(r['month'],r['utc_quarter']):r for r in base}
 assert len(baseline)==len(base)
 quarters=[];hourmap=defaultdict(lambda:{'orig_R9':0,'S4_fixed30':0,'R12_firstTP':0,'R12DQ_dense_firstTP':0,'quarters_R9_active':0,
                                  'quarters_S4_meet':0,'quarters_R12_meet':0,'quarters_R12DQ_meet':0,'quarters_R12DQ_impossible':0})
 receipts=[];impossible=[]
 for mon in MONTHS:
  receiptp=ROOT/f'R12DQ_{mon}_ALL_DISTINCT_MS_OBSERVED_COMPLETE_SCIENTIFIC_RECEIPT.json'
  receipt=json.loads(receiptp.read_text()); assert receipt['month']==mon and receipt['feasible_quarters_still_unmet']==0
  source=ROOT/f'R12DQ_{mon}_ALL_DISTINCT_MS_OBSERVED_ALL_SOURCE_15MIN_QUOTAS.csv'
  rows=readcsv(source)
  assert len(rows)==FULL_QUARTERS[mon]
  assert digest(source)==receipt['sha256_outputs'][source.name]
  assert sum(int(x['r9_SYNTH_original_entry_ref']) for x in rows)==ORIG_R9[mon]
  prev=None
  for i,r in enumerate(rows):
   k=(r['month'],r['utc_quarter']); v=baseline[k]
   assert r['utc_hour']==v['utc_hour']
   assert int(r['r9_SYNTH_original_entry_ref'])==int(v['ORIGINAL_R9_SYNTH_UTC_ENTRY_REFERENCE'])
   assert r['R12DQ_FEASIBLE_BUT_UNMET'] in ('0','') and int(r['R12DQ_QUOTA_PRIORITY_SELECTED'])>=0
   entry={'month':r['month'],'utc_quarter':r['utc_quarter'],'utc_hour':r['utc_hour'],
          'original_R9_SYNTH_15min_reference':int(r['r9_SYNTH_original_entry_ref']),
          'S4_fixed30_selected':int(v['ORIGINAL_R11S4_30SEC_FIXED_SELECTED']),
          'R12_original_firstTP_250ms_selected':int(v['R12_FIRSTTP_GLOBAL_GREEDY_SELECTED']),
          'R12DQ_dense_firstTP_selected':int(r['R12DQ_QUOTA_PRIORITY_SELECTED']),
          'R12DQ_source_isolated_optimistic_quarter_capacity':int(r['quarter_isolated_optimistic_upper']),
          'R12DQ_SOURCE_STRICT_ORACLE_CANDIDATE_EVENTS':int(r['s1_ORIGINAL_SAFE30_FAV15_QUOTE_EVENT_CANDIDATE_COUNT']),
          'source_broker_R9_quarter_active':int(int(r['r9_SYNTH_original_entry_ref'])>0),
          'S4_fixed30_reaches_original_quarter':int(int(v['ORIGINAL_R11S4_30SEC_FIXED_SELECTED'])>=int(r['r9_SYNTH_original_entry_ref'])) if int(r['r9_SYNTH_original_entry_ref']) else '',
          'R12_firstTP_250ms_reaches_original_quarter':int(int(v['R12_FIRSTTP_GLOBAL_GREEDY_SELECTED'])>=int(r['r9_SYNTH_original_entry_ref'])) if int(r['r9_SYNTH_original_entry_ref']) else '',
          'R12DQ_dense_firstTP_reaches_original_quarter':int(r['R12DQ_QUARTER_REFERENCE_MET']) if r['R12DQ_QUARTER_REFERENCE_MET']!='' else '',
          'R12DQ_proven_isolated_source_infeasible':int(r['R12DQ_PROVEN_ISOLATED_IMPOSSIBLE']) if r['R12DQ_PROVEN_ISOLATED_IMPOSSIBLE']!='' else '',
          'R12DQ_unavoidable_isolated_source_deficit':max(0,int(r['r9_SYNTH_original_entry_ref'])-int(r['quarter_isolated_optimistic_upper'])),
          'future_privileged_oracle_not_deployable':True}
   quarters.append(entry)
   if entry['original_R9_SYNTH_15min_reference']>0 and entry['R12DQ_dense_firstTP_reaches_original_quarter']==0:
    assert entry['R12DQ_proven_isolated_source_infeasible']==1;impossible.append(entry)
   h=(r['month'],r['utc_hour']); agg=hourmap[h]
   agg['orig_R9']+=entry['original_R9_SYNTH_15min_reference']
   agg['S4_fixed30']+=entry['S4_fixed30_selected']
   agg['R12_firstTP']+=entry['R12_original_firstTP_250ms_selected']
   agg['R12DQ_dense_firstTP']+=entry['R12DQ_dense_firstTP_selected']
   if entry['source_broker_R9_quarter_active']:
    agg['quarters_R9_active']+=1
    agg['quarters_S4_meet']+=int(entry['S4_fixed30_reaches_original_quarter'])
    agg['quarters_R12_meet']+=int(entry['R12_firstTP_250ms_reaches_original_quarter'])
    agg['quarters_R12DQ_meet']+=int(entry['R12DQ_dense_firstTP_reaches_original_quarter'])
    agg['quarters_R12DQ_impossible']+=int(entry['R12DQ_proven_isolated_source_infeasible'])
  assert sum(int(x['R12DQ_QUOTA_PRIORITY_SELECTED']) for x in rows)==receipt['repaired_month_trade_count']
  achieved=sum(int(r['R12DQ_QUARTER_REFERENCE_MET']) for r in rows if r['R12DQ_QUARTER_REFERENCE_MET']!='')
  bad=sum(int(r['R12DQ_PROVEN_ISOLATED_IMPOSSIBLE']) for r in rows if r['R12DQ_PROVEN_ISOLATED_IMPOSSIBLE']!='')
  assert achieved==receipt['repaired_quarters_achieved'] and bad==receipt['strict_source_proven_isolated_impossible_remaining']
  receipts.append({'month':mon,'source_R12DQ_receipt':str(receiptp),'source_quarter_csv':str(source),'source_quarter_sha':digest(source),
     'original_R9_SYNTH_UTC_verified_entry_reference':ORIG_R9[mon], 'selected_source_quote_count':receipt['repaired_month_trade_count'],
     'quarters_achieved':achieved,'quarters_impossible':bad,'feasible_quotas_unpaid':0})
 assert len(quarters)==11520 and len(hourmap)==2880
 out_hour=[]
 for mon,h in sorted(hourmap):
  row=hourmap[(mon,h)];r9=row['orig_R9']
  out_hour.append({'month':mon,'utc_hour':h,**row,'R9_active':int(r9>0),
   'S4_reaches_hour_reference':int(row['S4_fixed30']>=r9) if r9 else '',
   'R12_reaches_hour_reference':int(row['R12_firstTP']>=r9) if r9 else '',
   'R12DQ_reaches_hour_reference':int(row['R12DQ_dense_firstTP']>=r9) if r9 else '',
   'S4_deficit':max(0,r9-row['S4_fixed30']),'R12_deficit':max(0,r9-row['R12_firstTP']),
   'R12DQ_deficit':max(0,r9-row['R12DQ_dense_firstTP'])})
 out1=ROOT/'R12DQ_COMPLETE_ALL_11520_SOURCE_QUARTERS_S4_R12_R12DQ.csv'
 out2=ROOT/'R12DQ_COMPLETE_ALL_2880_SOURCE_HOURS_S4_R12_R12DQ.csv'
 out3=ROOT/'R12DQ_COMPLETE_ALL_208_PROVEN_INFEASIBLE_SOURCE_QUARTERS.csv'
 writecsv(out1,quarters);writecsv(out2,out_hour);writecsv(out3,impossible)
 active=sum(r['source_broker_R9_quarter_active'] for r in quarters)
 total={'research_classification':'FULL_SOURCE_EXACT_FUTURE_PRIVILEGED_ORACLE_ONLY_NOT_TRAINED_NOT_BROKER_FILL',
       'R9_source_quarter_reference_proof':'ORIGINAL_PER_TICK_ENTRY_SOURCE_R9_SYNTH_WITH_UTC_OFFSET_VERIFIED_ALL_2880_HOURS',
       'source_calendar_quarters':len(quarters),'source_calendar_hours':len(out_hour),'active_15min_R9_reference_quarters':active,
       'original_R9_SYNTH_entry_reference_total':sum(r['original_R9_SYNTH_15min_reference'] for r in quarters),
       'S4_strict_fixed30_selected':sum(r['S4_fixed30_selected'] for r in quarters),
       'R12_first250_firstTP_selected':sum(r['R12_original_firstTP_250ms_selected'] for r in quarters),
       'R12DQ_all_distinct_ms_firstTP_selected':sum(r['R12DQ_dense_firstTP_selected'] for r in quarters),
       'S4_active_quarters_exact_reference_met':sum(int(r['S4_fixed30_reaches_original_quarter']) for r in quarters if r['source_broker_R9_quarter_active']),
       'R12_active_quarters_exact_reference_met':sum(int(r['R12_firstTP_250ms_reaches_original_quarter']) for r in quarters if r['source_broker_R9_quarter_active']),
       'R12DQ_active_quarters_exact_reference_met':sum(int(r['R12DQ_dense_firstTP_reaches_original_quarter']) for r in quarters if r['source_broker_R9_quarter_active']),
       'R12DQ_isolated_source_infeasible_quarters':len(impossible),
       'R12DQ_source_feasible_unpaid_quarter_targets':0,
       'original_S4_active_hours_quota_met':sum(int(r['S4_reaches_hour_reference']) for r in out_hour if r['R9_active']),
       'R12_active_hours_quota_met':sum(int(r['R12_reaches_hour_reference']) for r in out_hour if r['R9_active']),
       'R12DQ_active_hours_quota_met':sum(int(r['R12DQ_reaches_hour_reference']) for r in out_hour if r['R9_active']),
       'month_receipts':receipts,
       'outputs_sha256':{str(p.name):digest(p) for p in (out1,out2,out3)},
       'frozen_original_results_not_modified':True,
       'no_validation_real_world_or_fitted_student':True}
 assert total['original_R9_SYNTH_entry_reference_total']==117585
 assert total['R12DQ_active_quarters_exact_reference_met']+len(impossible)==active
 assert total['R12DQ_all_distinct_ms_firstTP_selected']==379291
 p=ROOT/'R12DQ_ALL_FOUR_MONTH_COMPLETE_EVIDENCE_AND_EXECUTION_RECEIPT.json'
 p.write_text(json.dumps(total,indent=2)+'\n',encoding='utf8')
 print(json.dumps(total,indent=2))
 return total

if __name__=='__main__':run()

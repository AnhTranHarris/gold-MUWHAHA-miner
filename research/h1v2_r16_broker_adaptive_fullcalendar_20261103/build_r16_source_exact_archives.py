"""Reproducible source-exact all-month R16 manifest and lossless ZIP transport."""
from __future__ import annotations
import csv,hashlib,json,zipfile,datetime
from pathlib import Path
import numpy as np
P=Path('/mnt/data/h1v2_r16_broker_adaptive');RESULTS=P/'results';FINAL=P/'final'
FINAL.mkdir(parents=True,exist_ok=True)
MONS=('01','02','06','07')

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def exact_csv_concat(name,pattern,expected_rows):
 target=FINAL/name
 with target.open('w',encoding='utf8',newline='') as f:
  writer=None;total=0
  for m in MONS:
   with (RESULTS/pattern.format(m)).open(newline='',encoding='utf8') as fh:
    rdr=csv.DictReader(fh)
    if writer is None:writer=csv.DictWriter(f,fieldnames=rdr.fieldnames);writer.writeheader()
    else:assert rdr.fieldnames==writer.fieldnames
    for row in rdr:writer.writerow(row);total+=1
 assert total==expected_rows,(name,total,expected_rows)
 return target,sha(target),total

def rows_file(name,items):
 p=FINAL/name
 with p.open('w',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)
 return p

def zip_files(destination,files):
 manifest={'member':{str(arc):{'bytes':f.stat().st_size,'sha256':sha(f)} for f,arc in files},
  'sciences':'SOURCE_EXACT_R16_HINDSIGHT_NOT_CAUSAL_NOT_REAL_EXECUTION',
  'no_old_research_overwritten':True}
 with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=5,allowZip64=True) as z:
  for f,name in files:z.write(f,str(name))
  z.writestr('MANIFEST_SHA256_ALL_ORIGINAL_MEMBERS.json',json.dumps(manifest,indent=2,allow_nan=False)+'\n')
 with zipfile.ZipFile(destination) as z:
  assert z.testzip() is None
  inside=json.loads(z.read('MANIFEST_SHA256_ALL_ORIGINAL_MEMBERS.json'))['member']
  for name,rec in inside.items():
   assert len(z.read(name))==rec['bytes']
   assert hashlib.sha256(z.read(name)).hexdigest()==rec['sha256']
 return {'name':destination.name,'bytes':destination.stat().st_size,'sha256':sha(destination),
         'full_crc_and_per_member_sha_verified':True,'payload_members':len(files)}

recs=[];stressrecs=[]
for mon in MONS:
 j=json.loads((RESULTS/f'R16_{mon}_EXACT_COMPLETE_EXECUTION.json').read_text())
 s=json.loads((RESULTS/f'R16_{mon}_FULL_DELAY_EXECUTION_RECEIPT.json').read_text())
 assert j['month']==s['month']==mon and len(s['results_all_35_scenarios'])==35
 for x in j['fully_evaluated_variants'].values():recs.append(x)
 stressrecs.extend(s['results_all_35_scenarios'])
 assert j['verified_original_raw_SHA256']==s['original_raw_source_SHA']
assert len(recs)==36 and len(stressrecs)==140
out1=rows_file('ALL_36_FULL_FOUR_MONTH_SOURCE_HINDSIGHT_LANE_OUTCOMES.csv',recs)
out2=rows_file('ALL_140_FULL_FOUR_MONTH_FROZEN_EXECUTION_LATENCY_FRICTION.csv',stressrecs)
exact_csv_concat('ALL_103680_FOUR_MONTHS_ALL_SOURCE_QUARTERS_NINE_ENTRY_LANES.csv','R16_{}_ALL_15MIN_LANE_CALENDAR.csv',9*11520)
exact_csv_concat('ALL_25920_FOUR_MONTHS_ALL_HOURS_NINE_ENTRY_LANES.csv','R16_{}_ALL_HOURLY_LANE_CALENDAR.csv',9*2880)
exact_csv_concat('ALL_403200_FOUR_MONTHS_ALL_QUARTERS_140_EXECUTION_SCENARIOS.csv','R16_{}_ALL_15MIN_DELAYS_STRESS_CALENDAR.csv',35*11520)

mats=['BASE_250_1500','DENSE_1500','WIDE_REQUOTE_4000','BROKER_CONTRACTION','DIRECTIONAL_MICROPATH','WATCH60_COOL_1500','WATCH60_COOL_2500','BUDGETED_MULTI_REGIME','FULL_WIDE_DENSE_DIAGNOSTIC']
met={}
for name in mats:
 v=[r for r in recs if r['lane']==name]
 met[name]={
  'months':['2026-'+m for m in MONS],
  'total_source_future_selected_one_position':sum(r['selected_one_position_firsttp'] for r in v),
  'total_source_R9_active_quarters':sum(r['R9_active_15m_quarters'] for r in v),
  'strict_future_selected_15minute_quotas_met':sum(r['15m_quotas_met'] for r in v),
  'independent_quarter_source_isolated_infeasible':sum(r['15m_source_isolated_impossible'] for r in v),
  'source_active_hour_quotas_met':sum(r['active_hour_quotas_met'] for r in v),
  'source_active_hour_count':sum(r['active_hour_original_R9_quotas'] for r in v),
 }

fullreport=FINAL/'R16_COMPLETE_UNABRIDGED_FOUR_MONTH_BROKER_GEOMETRY_HINDSIGHT_RESEARCH_20261103.md'
pre=(P/'README.md').read_text(encoding='utf8')
original=(Path('/mnt/data/H1V2_COMPLETE_DEEP_HOURLY_AUDIT_20261103.md').read_text(encoding='utf8'))
oldr15=(Path('/mnt/data/R15_COMPLETE_UNABRIDGED_HINDSIGHT_WATCH60_CROSSFEED_REPORT_20261103.md').read_text(encoding='utf8'))
with fullreport.open('w',encoding='utf8') as f:
 f.write('# H1V2 R16 — COMPLETE, UNSHORTENED FOUR-MONTH NINE-LANE BROKER ENTRY ADMISSION RESEARCH\n\n')
 f.write('No original source, H1V2 teacher, R9 EA, earlier R11/12/13/14/15 outcome or branch altered. Complete machine-readable 103,680 source quarter rows, 25,920 source hour rows, 403,200 stressed quarter rows, 36 month-lane outcome rows, 140 month-scenario rows, all saved source quote ordinals, 140 complete frozen-signal trace NPZ and four candidate-good source NPZ are preserved separately with SHA256 in month archive source manifests. These files, not an abbreviated text, are the primary proof.\n\n')
 f.write('## Full R16 executable source and scientific contract\n\n'+pre+'\n\n')
 f.write('## Source complete 36 lane-month report rows, verbatim\n\n```csv\n'+out1.read_text()+'```\n\n')
 f.write('## Source complete 140 delayed execution month-scenario report rows, verbatim\n\n```csv\n'+out2.read_text()+'```\n\n')
 f.write('## Source quotas, no proxy or source-calendar omission\n\n'+json.dumps(met,indent=2)+'\n\n')
 f.write('## Complete independent verification\n\n'+(FINAL/'R16_INDEPENDENT_FULL_SOURCE_VERIFICATION.json').read_text()+'\n\n')
 f.write('## All upstream R15 source audit and complete three-feed primary comparison (unaltered content)\n\n'+oldr15+'\n\n')
 f.write('## Original 85KB H1V2 forensic audit, unaltered verbatim source copy\n\n'+original+'\n')

source_files=[P/'README.md',P/'src/r16_fullcalendar_broker_adaptive.py',P/'src/r16_source_delayed_fills.py',P/'tests/test_r16_contracts.py',P/'tests/test_r16_stress.py',P/'verify_r16_source_exact.py',P/'build_r16_source_exact_archives.py',fullreport,
  FINAL/'R16_INDEPENDENT_FULL_SOURCE_VERIFICATION.json',out1,out2,
  FINAL/'ALL_103680_FOUR_MONTHS_ALL_SOURCE_QUARTERS_NINE_ENTRY_LANES.csv',
  FINAL/'ALL_25920_FOUR_MONTHS_ALL_HOURS_NINE_ENTRY_LANES.csv',
  FINAL/'ALL_403200_FOUR_MONTHS_ALL_QUARTERS_140_EXECUTION_SCENARIOS.csv',
  P/'logs/independent_verify.log']
for src in ['H1V2 R11 APPEND-ONLY R&D EXECUTION AND RECOVERY LEDGER — 20261102.txt',
            'H1V2 COMPLETE FORENSIC AUDIT — R0–R10 — ORIGINAL FULL TECHNICAL RECORD — 20261102.txt']:
 p=Path('/mnt/data')/src
 if p.exists():source_files.append(p)

monthly=[]
for mon in MONS:
 files=[p for p in RESULTS.iterdir() if p.is_file() and p.name.startswith(f'R16_{mon}_')]
 assert len(files)==43,(mon,len(files)) # 4 principal + 2 calendars + 1 receipt + 35 stress +1 stress receipt?
 dest=FINAL/f'H1V2_R16_MONTH_{mon}_ALL_SOURCE_QUOTE_ORDINALS_AND_FROZEN_STRESS_20261103.zip'
 monthly.append(zip_files(dest,[(p,'month_'+mon+'/'+p.name) for p in sorted(files)]))
master=FINAL/'H1V2_R16_COMPLETE_FOUR_MONTH_RESEARCH_AND_RECOVERY_CORE_20261103.zip'
core=zip_files(master,[(p,'core/'+p.name) for p in source_files])
reg={'record_classification':'R16_FULL_FOURMONTH_DIRECT_SOURCE_REPRODUCIBILITY_HINDSIGHT_ONLY',
     'original_teacher_sha':'edce573d9c53b743dc5de1b0d741c81370af52c1',
     'original_r9_v2_sha':'ded3d0dff9d9112be52d9ddb29fbc7c6b9e2a1c0',
     'parent_r15_sha':'1da637cc3def47fd586f598fa98dbe6881c6c048',
     'RAW_DUKAS_SOURCE_GZIP_SHA256':{
       '01':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
       '02':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d',
       '06':'34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2',
       '07':'e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7'},
     'per_month_archives':monthly,'core':core,'full_data_quotas':{'total_utc_hours':2880,'total_utc_quarters':11520,'original_R9_active_quarters':7521,'original_R9_active_hours':1917},
     'source_results':met,'source_verified_all_months':True,
     'frozen_future_known_side_and_good_not_runtime_prediction':True,
     'negative_latency_100ms':'DEMONSTRATED_NEGATIVE_ACROSS_FOUR_MONTHS','note':'Do not promote; 100ms delay achieved <80% strict accuracy on all broad lanes across all four months' }
# json manifest source no incorrect dict literal
reg['negative_latency_100ms'] = 'DEMONSTRATED_NEGATIVE_ACROSS_FOUR_MONTHS'
regp=FINAL/'R16_ALL_ARCHIVES_AND_EXACT_SOURCE_MANIFEST.json';regp.write_text(json.dumps(reg,indent=2,allow_nan=False)+'\n',encoding='utf8')
print(json.dumps({'complete':True,'archives':monthly,'core':core,'registered':regp.name},indent=2))

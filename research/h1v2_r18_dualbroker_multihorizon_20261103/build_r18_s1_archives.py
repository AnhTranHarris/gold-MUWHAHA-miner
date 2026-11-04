"""Archive R18-S1 exact all source-month latency scenarios with SHA/CRC receipts."""
from pathlib import Path
import hashlib, json, zipfile, csv
ROOT=Path('/mnt/data/h1v2_r18_dualbroker')
OUT=ROOT/'results_r18_FROZEN_DELAY'
DEST=ROOT/'archives_r18_s1';DEST.mkdir(exist_ok=True)
SOURCES=('DUKASCOPY_RAW','MT5_BROKER_EXPORT');MONTHS=('01','02','06','07')
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(4<<20),b''):h.update(x)
 return h.hexdigest()

def build(files,out):
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=4) as z:
  for f in files:z.write(f,arcname=f.name)
 with zipfile.ZipFile(out) as z:
  assert z.testzip() is None
  names={x.filename for x in z.infolist()}
  assert names=={f.name for f in files}
 return {'file':out.name,'size':out.stat().st_size,'sha256':digest(out),
         'members':{f.name:{'size':f.stat().st_size,'sha256':digest(f)} for f in files}}
archive_entries=[]
for src in SOURCES:
 for mon in MONTHS:
  tag=f'R18_LATENCY_{src}_{mon}'
  files=[OUT/(tag+x) for x in ('_9_SCENARIO_RESULTS.csv','_ALL_UTC_QUARTERS.csv','_ALL_UTC_HOURS.csv',
        '_ALL_FROZEN_SOURCE_ORDINAL_OUTCOME_TRACES.npz','_SOURCE_SHA_AND_RESULT_RECEIPT.json')]
  files.append(OUT/f'R18_S1_VERIFIED_{src}_{mon}_ATOMIC_SOURCE_RECEIPT.json')
  assert all(f.exists() for f in files)
  out=DEST/f'R18_S1_{src}_{mon}_COMPLETE_9_SCENARIO_15MIN_HOURS_AND_QUOTE_ORDINALS_20261103.zip'
  entry=build(files,out);archive_entries.append(entry)
  print('ARCHIVED',src,mon,entry['size'],entry['sha256'],flush=True)
extras=[ROOT/'src/r18_frozen_latency_economic_stress.py',ROOT/'verify_r18_latency_fullpopulation.py',
 ROOT/'tests/test_r18_frozen_latency_contracts.py',ROOT/'results_r18_FROZEN_DELAY/R18_EIGHT_SOURCE_LATENCY_PROGRESS_APPEND_ONLY.log',
 ROOT/'results_r18_FROZEN_DELAY/R18_S1_INDEPENDENT_VERIFIER_EXECUTION.log',
 ROOT/'results_r18_FROZEN_DELAY/R18_LATENCY_MT5_BROKER_EXPORT_06_RETRY.log']
assert all(f.exists() for f in extras)
core=build(extras,DEST/'R18_S1_SOURCE_TESTS_FULL_72_CASE_INDEX_AND_FAILURE_LOGS_20261103.zip')
manifest={'classification':'R18_ZERO_DELAY_TEACHER_FUTURE_SELECTED_NOT_CAUSAL','year':2026,
 'sources':'Dukascopy historical raw quotes and Coinexx-connected MT5 broker export quotes; original provider fills not proven',
 'months':MONTHS,'nominal_quote_price_fee_units_raw':20,'quote_price_unit_raw_usd_per_oz':0.001,
 'real_account_cash_pnl_known':False,'source_month_archives':archive_entries,'core':core,
 'original_R18_source_study_not_modified':True,'underlying_raw_8_files_not_copied':True}
p=DEST/'R18_S1_8_FULL_MONTH_SHA256_AND_MEMBER_MANIFEST.json';p.write_text(json.dumps(manifest,indent=2)+'\n')
print('ALL_ARCHIVED',len(archive_entries),'RESULT',p,flush=True)

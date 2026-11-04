"""Lossless, immutable R24S5 July evidence archiver. Source artifacts unchanged.

Four 15-policy complete bundles keep every selected entry quote ordinal, cause,
exact source 15m/hour/day rows and receipts. No sampling or row reduction.
"""
from __future__ import annotations
import json, hashlib, csv, zipfile, os, shutil
from pathlib import Path
from datetime import datetime,timezone
BASE=Path('/mnt/data/h1v2_r24s5')
SOURCE=BASE/'results/DUKASCOPY_RAW/07'
S4=Path('/mnt/data/h1v2_r24s4_entry_specialists/results/DUKASCOPY_RAW/07')
OUT=BASE/'archives';OUT.mkdir(parents=True,exist_ok=True)
SRC='R24S5_DUKASCOPY_RAW_07_'

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(4<<20),b''):h.update(b)
 return h.hexdigest()

def add_zip(name, items):
 out=OUT/name
 if out.exists():
  raise FileExistsError('PRESERVATION_REQUIRES_NEW_NAME '+str(out))
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for arc,p in items:
   if not p.is_file():raise FileNotFoundError(str(p))
   z.write(p,arcname=arc)
 with zipfile.ZipFile(out,'r') as z:
  if z.testzip() is not None:raise AssertionError('ZIP_CRC_FAILURE '+name)
  if len(z.namelist())!=len(items):raise AssertionError('ZIP_COUNT_FAILURE '+name)
 return out

case_receipts=sorted(SOURCE.glob(f'{SRC}P*_ATOMIC_RECEIPT.json'))
assert len(case_receipts)==60,len(case_receipts)
manifest={'purpose':'R24S5_JULY_DUKASCOPY_60_ALL_IN_SAMPLE_CAUSAL_SURVIVABILITY_RESEARCH_FULL_SOURCE','source':'DUKASCOPY_RAW','month':'2026-06','created_utc':datetime.now(timezone.utc).isoformat(),'source_raw_sha256':'e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7','files':{},'archives':{},'casenames':[],'no_profitability_claim':True,'not_blind_out_of_sample':True,'no_hist_mt5_ff_news_claim':True}

paths={}
for item in case_receipts:
 case=item.name[len(SRC):-len('_ATOMIC_RECEIPT.json')]
 assert case.startswith('P') and case not in paths
 paths[case]=[]
 for ending in ('_ALL_SELECTED_SOURCE_ORDINALS_GOOD_BAD_TIMEOUT_CENSORED.npz','_ATOMIC_RECEIPT.json','_COMPLETE_QUARTERS.csv','_COMPLETE_HOURS.csv','_COMPLETE_DAYS.csv'):
  p=SOURCE/f'{SRC}{case}{ending}'
  assert p.exists(),p
  paths[case].append(p)
 manifest['casenames'].append(case)
for j in range(0,60,15):
 cases=manifest['casenames'][j:j+15]
 items=[(f'cases/{c}/{p.name}',p) for c in cases for p in paths[c]]
 out=add_zip(f'R24S5_DUKASCOPY_2026_07_LOSSLESS_SELECTED_TRADES_UTC_QUARTERS_HOURS_DAYS_CASES_{j:02}_{j+14:02}.zip',items)
 manifest['archives'][out.name]={'bytes':out.stat().st_size,'sha256':sha(out),'case_count':len(cases),'file_count':len(items),'case_ids':cases}
 print('ARCHIVE',out.name,out.stat().st_size,flush=True)

agg_files=[SOURCE/f'{SRC}ALL_60_CASES_COMPLETE_{suffix}.csv' for suffix in ('MONTH_CASES','QUARTERS','HOURS','DAYS')]
for x in agg_files:assert x.exists(),x
extras=[BASE/'R24S5_JULY_60CASE_INDEPENDENT_FULL_SOURCE_VERIFICATION.json',SOURCE/f'{SRC}ALL60_FINAL_SOURCE_AND_CALENDAR_RECEIPT.json',BASE/'R24S5_APPEND_ONLY_CHECKPOINTS_20261104.txt']
for x in extras:assert x.exists(),x
items=[('all_case_full_utc_calendar/'+p.name,p) for p in agg_files]+[('verification/'+x.name,x) for x in extras]
out=add_zip('R24S5_DUKASCOPY_2026_07_ALL60_COMPLETE_MONTH_DAY_HOUR_15MIN_AND_INDEPENDENT_1680_CHECKS.zip',items)
manifest['archives'][out.name]={'bytes':out.stat().st_size,'sha256':sha(out),'file_count':len(items)}
print('ARCHIVE',out.name,out.stat().st_size,flush=True)

modelnames=(f'R24S4_DUKASCOPY_RAW_07_{s}' for s in ('BROKER_ONLY_MULTISCALE_CROSS_PRODUCT_5_CAUSE_LGBM.txt','BROKER_ONLY_WAIT10_HAZARD.txt','TRAINING_ROW_INDICES.npy','R24S5_DUKASCOPY_RAW_07_RESUMABLE_INFERENCE_ATOMIC_FINAL_RECEIPT.json'))
modelitems=[]
for name in modelnames:
 p=S4/name
 if not p.exists():
  # terminal final receipt is R24S5_* no R24S4 prefix
  if 'RESUMABLE_INFERENCE_ATOMIC_FINAL_RECEIPT.json' in name:
   p=S4/'R24S5_DUKASCOPY_RAW_07_RESUMABLE_INFERENCE_ATOMIC_FINAL_RECEIPT.json'
  if not p.exists():raise FileNotFoundError(str(p))
 modelitems.append(('frozen_models_and_sha_receipts/'+p.name,p))
modelitems += [ ('frozen_models_and_sha_receipts/'+p.name,p) for p in [S4/'R24S5_DUKASCOPY_RAW_07_ATOMIC_CHUNK_INFERENCE_PROGRESS.json']]
modelitems += [('source_and_tests/'+p.name,p) for p in [BASE/'r24s5_recover_trained_s4_atomic_inference.py',BASE/'r24s5_replay_per_policy_atomic.py',BASE/'verify_r24s5_full_june_exact.py',BASE/'build_r24s5_july_full_archives.py']]
out=add_zip('R24S5_DUKASCOPY_2026_07_FROZEN_5CAUSE_WAIT10_MODELS_48_BLOCKS_AND_REPRODUCIBLE_SOURCE.zip',modelitems)
manifest['archives'][out.name]={'bytes':out.stat().st_size,'sha256':sha(out),'file_count':len(modelitems)}
print('ARCHIVE',out.name,out.stat().st_size,flush=True)

for p in list(SOURCE.iterdir())+extras+[s for _,s in modelitems]:
 if p.is_file():
  manifest['files'][p.name]={'bytes':p.stat().st_size,'sha256':sha(p)}
jsonpath=OUT/'R24S5_JULY_COMPLETE_LOSSLESS_ARCHIVE_MANIFEST_SHA256.json'
jsonpath.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
print('FINISHED',len(manifest['archives']),'archives',len(manifest['files']),'member sources',jsonpath.stat().st_size,flush=True)

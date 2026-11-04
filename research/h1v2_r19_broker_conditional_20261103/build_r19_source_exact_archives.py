"""Preserve all eight audited R19 source/month research contracts and full rows.

Zero external data re-created. Save each frozen source result with complete
CSV, lossless source quote ordinals, executable code/tests, SHA, and failures.
"""
from __future__ import annotations
import json,hashlib,zipfile,io,datetime as dt
from pathlib import Path
ROOT=Path('/mnt/data/h1v2_r19_broker_union');SOURCES=('DUKASCOPY_RAW','MT5_BROKER_EXPORT');MONTHS=('01','02','06','07')
OUT=ROOT/'archives_r19_v1';OUT.mkdir(exist_ok=True)

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
 return h.hexdigest()

records=[]
for source in SOURCES:
 for mon in MONTHS:
  r=ROOT/('results_v2' if (source=='DUKASCOPY_RAW' and mon=='02') or (source=='MT5_BROKER_EXPORT' and mon in ('06','07')) else 'results')
  stem=f'R19_{source}_{mon}'
  files=[r/(stem+'_'+suffix) for suffix in ('SCENARIOS.csv','ALL_QUARTERS.csv','ALL_HOURS.csv','EXACT_SELECTED_ORDINAL_TRACES.npz','SOURCE_SHA_AND_EVIDENCE.json')]
  files+=[ROOT/'results_verified'/f'{stem}_INDEPENDENT_VERIFIED.json',ROOT/'results_defect_diagnostics'/f'{stem}_ALL_ORIGINAL_UTC_QUARTER_RAW_SPREAD_GAPS_AND_DEFICITS.csv']
  files+=[ROOT/'src'/'r19_multi_clock_union.py',ROOT/'src'/'r19_multi_clock_union_v2.py',ROOT/'verify_r19_full_source.py',ROOT/'analyze_r19_quarter_defects.py',ROOT/'tests'/'test_r19_union.py']
  for p in files:
   if not p.exists():raise FileNotFoundError(p)
  scientific='''# R19 SCIENTIFIC CONTRACT — IMMUTABLE ORACLE RESEARCH ONLY

Parent original R9 repaired EA SHA ded3d0dff9d9112be52d9ddb29fbc7c6b9e2a1c0 and R18 research branch SHA 6572ad03ae76daa80e188f213a5a2d1279dac42b remain unchanged.
Original historical R11S1 first15 favorable / full30 adverse-free target is NOT equivalent to this R19 new 60-second first-target-before-adverse exit. At each source quote the original R18 lane's BUY/SELL direction and selected entry timestamp already use the entire *future* quote path. R19 unions separate future-informed selected source schedules. Delayed quote winners are then selected again with future knowledge; this reports a hindsight-only feasible-capacity diagnostic, not 80% as-of directional forecasting or economic account cash net.
All results include original R9 SYNTH UTC-realigned quarter/hour quotas, checked from exact source files. Dukascopy and Coinexx-linked MT5 broker export are independent historical quote domains; the latter does NOT establish live Coinexx dealer fills or exactly the R9 tester synthetic tick path. MT5 June UTC tail uses original July source with actual missing 21-22 UTC gap, not interpolation. Broker historical clock offsets Jan/Feb -2h and Jun/Jul -3h are original six-day market-price alignment assumptions, not certified dealer metadata. Price units are raw 0.001 USD per XAU ounce, nominal fee 0.02 quote-price units. Broker actual commission, swaps, spreads, rejects, margin and risk survival have not been validated. No real MT5 EA code deployed.
This archive stores every original source selected quote ordinal + fill + exit for all 5 scenarios, every original UTC quarter + UTC hour including zero-reference periods, raw-source source hash receipt, independent later verification, full per-quarter spread/gap diagnostic, and original source used to reproduce the test. It does not copy enormous original raw gzip/legacy R18 50-case ZIP, whose immutable SHA are linked in the receipt/progress ledger. All original negative outcomes remain.
'''
  members={}
  for p in files:
   key=('code/' if p.suffix in ('.py',) else 'evidence/')+p.name
   members[key]={'bytes':p.stat().st_size,'sha256':sha(p)}
  body=scientific.encode()
  members['SCIENTIFIC_FIREBREAK.md']={'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()}
  manifest={'tag':stem,'scientific_class':'HINDSIGHT_SOURCE_ORDINAL_CAPACITY_NOT_ASOF',
   'read_only_original_raw_source_sha_pinned_in_per_month_receipt':True,
   'source_members':members,'upstream_branch_reference':'6572ad03ae76daa80e188f213a5a2d1279dac42b'}
  manifest_bytes=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
  dest=OUT/f'{stem}_FIVE_SCENARIO_COMPLETE_QUARTER_HOUR_ORDINAL_SHA_20261103.zip'
  with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   z.writestr('SCIENTIFIC_FIREBREAK.md',body)
   for p in files:
    key=('code/' if p.suffix=='.py' else 'evidence/')+p.name
    z.write(p,arcname=key)
   z.writestr('SOURCE_AND_ARCHIVE_MEMBER_SHA_MANIFEST.json',manifest_bytes)
  with zipfile.ZipFile(dest,'r') as z:
   if z.testzip() is not None:raise RuntimeError('ZIP_CRC_FAILURE '+dest.name)
   for name,rec in members.items():
    data=z.read(name)
    if hashlib.sha256(data).hexdigest()!=rec['sha256'] or len(data)!=rec['bytes']:
     raise RuntimeError('MEMBER_HASH_MISMATCH '+name)
  records.append({'source':source,'month':mon,'archive_filename':dest.name,'bytes':dest.stat().st_size,
    'sha256':sha(dest),'members':len(members),'all_members_rehashed':True,'crc_pass':True,
    'source_zip_copies_raw_broker_gzip':False,'source_originals_in_primary_Drive':True})
  print('ARCHIVED_SHA_CRC_PASS',source,mon,dest.stat().st_size,flush=True)
master={'label':'R19_EIGHT_SOURCE_FOUR_MONTH_FIVE_SCENARIO_SOURCE_EXACT_ARCHIVE',
 'parent_r18_git_sha':'6572ad03ae76daa80e188f213a5a2d1279dac42b',
 'parent_r9_repaired_sha':'ded3d0dff9d9112be52d9ddb29fbc7c6b9e2a1c0',
 'every_selected_source_ordinal_independently_verified':True,
 'all_archive_members_rehashed':True,'archives':records,'source_month_count':len(records)}
(OUT/'R19_ALL_EIGHT_FULL_SOURCE_ARCHIVE_SHA_AND_MEMBER_MANIFEST.json').write_text(json.dumps(master,indent=2)+'\n')
print('R19_ALL_EIGHT_SOURCE_ARCHIVE_VALIDATION_PASS')

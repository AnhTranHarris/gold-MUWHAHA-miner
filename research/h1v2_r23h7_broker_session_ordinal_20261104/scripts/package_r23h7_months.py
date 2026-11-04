"""R23H7 0007 lossless per-month archival publication; do not rebuild raw ticks.
No compression loss of original binary; archive entry SHA256+CRC32+uncompressed byte size.
"""
from __future__ import annotations
import hashlib,json,os,sys,zipfile
from pathlib import Path
WORK=Path('/mnt/data/r23h7_work')
DATA=Path('/mnt/data/r23h24_workspace')
RELEASE=WORK/'release'
MONTHS=('01','02','06','07')
SOURCES=('DUKASCOPY_RAW','MT5_BROKER_EXPORT')
EXCLUDES={'.pyc','.DS_Store'}

def digest(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()

def add_if_exists(arr:list[tuple[str,Path]],name:str,p:Path):
 if p.is_file():arr.append((name,p))

def under(arr:list[tuple[str,Path]],prefix:str,path:Path):
 if path.exists():
  for p in sorted(path.rglob('*')):
   if p.is_file() and p.suffix not in EXCLUDES:arr.append((prefix+'/'+p.relative_to(path).as_posix(),p))

def pack(month:str):
 arr=[]
 for source in SOURCES:
  under(arr, f'broker_month/{source}/models',DATA/'r23h7_models'/source/month)
  under(arr, f'broker_month/{source}/day_scores',DATA/'r23h7_scores'/source/month)
  under(arr, f'broker_month/{source}/clock_day_hour_quarter',WORK/'results'/'clock_audit'/source/month)
  under(arr, f'broker_month/{source}/future_hindsight_capacity',WORK/'results'/'capacity_witness'/source/month)
  if month=='01':under(arr,f'broker_month/{source}/jan_week1_six_policy_replay',WORK/'results'/'jan_week1_replay'/source)
 under(arr,'source_and_contract',WORK/'src')
 under(arr,'tests',WORK/'tests')
 for n in ('README_R23H7_0007_SOURCE_EXACT.md','run_8_month_source_probes.sh','run_jan_week1_shards.sh','R23H_0007_001_ATOMIC_OPENING_ENTRY_20261104.txt'):
  add_if_exists(arr,'source_and_contract/'+n,WORK/n)
 for n in ('R23H7_0007_FINAL_EXECUTED_SHA_VERIFIER.json','R23H7_PROBE_EXECUTION_REGISTER.tsv','R23H7_JAN_WEEK1_DAY_SHARD_REGISTER.tsv','R23H7_BATCH_STDOUT.log','R23H7_JAN_WEEK1_BATCH_STDOUT.log','WEEK_REPLAY_DUKASCOPY_RAW.log','WEEK_REPLAY_MT5_BROKER_EXPORT.log'):
  add_if_exists(arr,'research_receipts/'+n,WORK/'results'/n)
 under(arr,'research_receipts/clock_sha_manifest',WORK/'results'/'clock_audit') if False else None
 add_if_exists(arr,'research_receipts/R23H7_ALL_EIGHT_SOURCE_MONTHS_24_OUTPUT_SHA_MANIFEST.json',WORK/'results'/'clock_audit'/'R23H7_ALL_EIGHT_SOURCE_MONTHS_24_OUTPUT_SHA_MANIFEST.json')
 add_if_exists(arr,'research_receipts/R23H7_ALL_96_FUTURE_CAPACITY_WITNESS_HASHES.json',WORK/'results'/'capacity_witness'/'R23H7_ALL_96_FUTURE_CAPACITY_WITNESS_HASHES.json')
 seen=set();arr2=[]
 for name,p in arr:
  if name not in seen:seen.add(name);arr2.append((name,p))
 arr=arr2
 entry={name:{'bytes':p.stat().st_size,'sha256':digest(p)} for name,p in arr}
 doc={'classification':'HISTORICAL_IN_SAMPLE_SOURCE_EXACT_NOT_DEPLOYABLE','month':f'2026-{month}','source_roots':['DUKASCOPY_RAW','MT5_BROKER_EXPORT'],'original_quote_gzip_excluded':True,'original_quote_sha_in_fit_receipts':True,'source_branch':'carson/h1v2-r23h7-broker-session-ordinal-hazards-20261104','original_R23H24_parent':'b97c70208c943e5fc9224b552d1cb5c9659b3bba','full_2026_01_02_06_07_R23H24_original_complete':'refer_to_frozen_parent_not_rebuilt_here','R23H7_new_replay_scope':'JANUARY_UTC_DAYS_1_TO_7_ONLY' if month=='01' else 'FIRST_DAY_ONLY_FROZEN_MODEL_SCORE','news_status':'UNKNOWN_NO_HISTORIC_VENDOR_VINTAGE','prop_session_permission':'UNKNOWN_NO_AUTHORIZED_RULES','file_count':len(arr),'entry_manifest':entry}
 manifest=json.dumps(doc,indent=2,sort_keys=True).encode('utf-8')
 zpath=RELEASE/f'R23H7_0007_{month}_DUKAS_MT5_FULL_FROZEN_IN_SAMPLE_EVIDENCE_20261104.zip'
 with zipfile.ZipFile(zpath,'w',allowZip64=True) as z:
  z.writestr('R23H7_0007_LOSSLESS_MEMBER_SHA256_MANIFEST.json',manifest,compress_type=zipfile.ZIP_DEFLATED)
  for name,p in arr:
   compress=zipfile.ZIP_STORED if p.suffix in ('.npz','.gz','.zip') else zipfile.ZIP_DEFLATED
   z.write(p,name,compress_type=compress,compresslevel=6 if compress==zipfile.ZIP_DEFLATED else None)
 with zipfile.ZipFile(zpath,'r') as z:
  bad=z.testzip()
  assert bad is None,bad
  m=json.loads(z.read('R23H7_0007_LOSSLESS_MEMBER_SHA256_MANIFEST.json'))
  assert len(m['entry_manifest'])==len(arr)
  for name,src in arr:
   assert z.getinfo(name).file_size==entry[name]['bytes']
   assert digest(src)==entry[name]['sha256']
 package_receipt={'zip_path':str(zpath),'bytes':zpath.stat().st_size,'sha256':digest(zpath),'archive_crc_test':'PASS','members':len(arr),'manifest_sha256':hashlib.sha256(manifest).hexdigest(),'month':month}
 (RELEASE/f'R23H7_0007_{month}_ZIP_ATOMIC_SHA_RECEIPT.json').write_text(json.dumps(package_receipt,indent=2)+'\n')
 print(json.dumps(package_receipt),flush=True)
 return package_receipt

if __name__=='__main__':
 RELEASE.mkdir(exist_ok=True,parents=True)
 result=[pack(m) for m in MONTHS]
 (RELEASE/'R23H7_0007_FOUR_MONTH_PACKAGE_SOURCE_SHA_INDEX.json').write_text(json.dumps(result,indent=2)+'\n')
 print('ALL_FOUR_MONTHS_CRC_SHA_PASS',flush=True)

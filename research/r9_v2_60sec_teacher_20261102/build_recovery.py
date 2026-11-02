#!/usr/bin/env python3
"""Reproducible source-exact per-broker-month archival, no overwrite.
Zips contain all 60s teacher labels, complete closed-trade ledger, TWO original
fitted student families (rejected) including corrected reachable 3s target,
original v2/observed-WAIT full code/test and append-only logs. Raw tick files
are pinned by SHA256 and original Drive provenance, not duplicated.
"""
from pathlib import Path
import json,hashlib,zipfile,sys
root=Path('/mnt/data/v2_new_research/sixty')
prior=Path('/mnt/data/v2_new_research/restore')
observed=Path('/mnt/data/v2_new_research/sequential')
out=Path('/mnt/data')
months=('01','02','06','07')
sources=('coinexx','dukascopy')

def digest(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for block in iter(lambda:f.read(1<<20),b''):h.update(block)
 return h.hexdigest()

def package(source,month):
 name=f'R9_V2_60SEC_{source.upper()}_2026_{month}_EXACT_RECOVERY.zip'
 dest=out/name
 if dest.exists():raise FileExistsError(f'Immutable checkpoint exists: {dest}')
 names=[]
 for base,label in [
  (root/'src','latest_60sec/src'),(root/'tests','latest_60sec/tests'),(root/'docs','latest_60sec/docs'),
  (prior/'original_v2','complete_original_v2'),(prior/'repair','original_full_volume_runner'),
  (observed/'src','previous_19feature_observed_WAIT/src'),
  (observed/'tests','previous_19feature_observed_WAIT/tests'),
  (observed/'docs','previous_19feature_observed_WAIT/docs'),
  (root/'results'/f'{source}_{month}_full','full_month_observed_WAIT_trades'),
  (root/'teacher'/f'{source}_{month}','complete_60sec_teacher'),
  (root/'models'/f'{source}_{month}','first_fit_preserved_rejected'),
  (root/'models_reachable_3s'/f'{source}_{month}','corrected_reachable_fit'),
  (root/'models_60s_aux'/f'{source}_{month}','one_minute_hindsight_aux_fit')]:
  if not base.exists():raise FileNotFoundError(base)
  for p in base.rglob('*'):
   if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':
    names.append((p,f'{label}/{p.relative_to(base).as_posix()}'))
 expected=(root/'teacher'/f'{source}_{month}'/'receipt.json')
 teacher=json.loads(expected.read_text());assert teacher['class_mismatch']==0 and teacher['net_mismatch']==0
 receipt=json.loads((root/'models_reachable_3s'/f'{source}_{month}'/'FOLD_RECEIPT.json').read_text())
 assert receipt['hindsight_runtime_used'] is False
 manifest={'source':source,'month':month,'verification':'ZIP_CRC_ALL_FILE_SHA256_AND_R9_CLASS_NET_RECONCILIATION',
   'input_raw_sha256':teacher['source_sha256'],'input_raw_filename':f'XAUUSD_{"MT5_BROKER" if source=="coinexx" else "DUKAS"}_2026_{month}_ticks{"_ALL" if source=="coinexx" else ""}.csv.gz',
   'source_truth_not_in_this_archive':True,'original_entry_exit':'R9 exact unchanged 30s',
   'future_60s_labels':'OFFLINE ONLY','new_fit':'REJECTED_BEFORE_ON_POLICY_PROMOTION',
   'model_reachable_WAIT_window_ms':3000,
   'artifacts':{arc:{'sha256':digest(p),'bytes':p.stat().st_size} for p,arc in names}}
 with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as zipf:
  for path,arc in names:zipf.write(path,arc)
  zipf.writestr('SOURCE_EXACT_MANIFEST.json',json.dumps(manifest,indent=2))
 with zipfile.ZipFile(dest) as zipf:
  assert zipf.testzip() is None
  for arc,expected in manifest['artifacts'].items():assert hashlib.sha256(zipf.read(arc)).hexdigest()==expected['sha256']
 return {'name':name,'source':source,'month':month,'zip_sha256':digest(dest),
         'zip_bytes':dest.stat().st_size,'file_count':len(names)+1,
         'raw_sha256':teacher['source_sha256'],'trades':teacher['trades'],
         'all_class_and_net_reconcile':True,'approved_policy':False,'zip_integrity':'PASS'}

if __name__=='__main__':
 index=[]
 for month in months:
  for source in sources:
   x=package(source,month);index.append(x);print(x['name'],x['zip_bytes'],flush=True)
 (out/'R9_V2_60SEC_EIGHT_EXACT_RECOVERY_INDEX_20261102.json').write_text(json.dumps({'entries':index,'all_inputs_real_ticks':True,'no_models_approved':True},indent=2))
 print('COMPLETE',len(index))

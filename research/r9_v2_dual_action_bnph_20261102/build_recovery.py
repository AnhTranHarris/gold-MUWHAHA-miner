from pathlib import Path
import json,hashlib,zipfile,os
ROOT=Path(__file__).resolve().parent
SRC=Path('/mnt/data/v2_new_research/restore')
BASE=Path('/mnt/data/v2_direction_audit')
OUT=Path('/mnt/data/R9_V2_DUAL_ACTION_BNP_HAWKES_SOURCE_EXACT_20261102.zip')
def hashf(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
files=[]
for p in ROOT.rglob('*'):
 if p.is_file() and p.name not in ('SOURCE_EXACT_SHA256_MANIFEST.json','RECOVERY_RECEIPT.json') and p.suffix in ('.py','.json','.md','.txt','.log','.npz') and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts:
  files.append((p,'new_research/'+p.relative_to(ROOT).as_posix()))
for sub in ('repair/src','repair/tests','original_v2/src','original_v2/tests','original_v2/docs'):
 for p in (SRC/sub).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts:
   files.append((p,'pinned_original/'+sub+'/'+p.relative_to(SRC/sub).as_posix()))
with zipfile.ZipFile(BASE/'R9_V2_PAIRED_ACTION_COINEXX_2026_01_FULL_CHECKPOINT.zip') as z:
 original=['source/src/causal_dual_features.py','source/src/paired_action_labels.py',
           'source/src/train_paired_action.py','source/tests/test_paired_action.py']
 for n in original:
  dest=ROOT/'original_pair_source'/n
  dest.parent.mkdir(parents=True,exist_ok=True)
  dest.write_bytes(z.read(n))
  files.append((dest,'pinned_original/paired_action/'+n))
manifest={
 'identity':'R9 v2 true dual-action Bayesian/Neyman-Pearson/Hawkes research',
 'status':'NOT_APPROVED_UNDER_80PCT_85PCT_CONTRACT',
 'input_event_scope':'ORIGINAL_COMPLETE_SAVED_BASELINE_ENTRY_EVENTS_NOT_ALL_ELIGIBLE_MARKET_EVENTS',
 'self_contained_code':True,
 'input_archives_not_duplicated':True,
 'inputs':{},
 'files':{}
}
for source in ('coinexx','dukascopy'):
 for m in ('01','02','06','07'):
  p=BASE/f'R9_V2_PAIRED_ACTION_{source.upper()}_2026_{m}_FULL_CHECKPOINT.zip'
  assert p.exists()
  manifest['inputs'][f'{source}_{m}']={'name':p.name,'bytes':p.stat().st_size,'sha256':hashf(p)}
for p,n in files:
 manifest['files'][n]={'bytes':p.stat().st_size,'sha256':hashf(p)}
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p,n in files:z.write(p,n)
 z.writestr('SOURCE_EXACT_SHA256_MANIFEST.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(OUT) as z:
 assert z.testzip() is None
 for n,item in manifest['files'].items():
  assert hashlib.sha256(z.read(n)).hexdigest()==item['sha256'],n
receipt=dict(archive=OUT.name,bytes=OUT.stat().st_size,sha256=hashf(OUT),
             items=len(files)+1,zip_crc='PASS',all_manifest_member_hashes='PASS',
             archived_inputs='REFERENCED_BY_FULL_SHA256_AND_STORED_SEPARATELY',
             approved=False)
(ROOT/'RECOVERY_RECEIPT.json').write_text(json.dumps(receipt,indent=2))
(ROOT/'SOURCE_EXACT_SHA256_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(receipt,indent=2))

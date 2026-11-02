#!/usr/bin/env python3
"""Byte-exact compact release; month-specific full arrays live in eight ZIPs."""
from pathlib import Path
import hashlib,zipfile,json,datetime
base=Path('/mnt/data/v2_30s_teacher_training');out=Path('/mnt/data/R9_V2_30S_DUAL_BROKER_HINDSIGHT_TEACHER_RESEARCH_20261101.zip')
paths=[]
for p in base.glob('*.py'):
 if p.name in ('audit_ledger.py','score_micro.py'):continue  # superseded / incompatible partial helpers
 paths.append((p,'src/'+p.name))
for p in (base/'tests').rglob('*.py'):
 paths.append((p,'tests/'+p.name))
for p in (base/'docs').rglob('*'):
 if p.is_file():paths.append((p,'docs/'+p.name))
for p in (base/'source').rglob('*'):
 if p.is_file():paths.append((p,'frozen_original/'+p.relative_to(base/'source').as_posix()))
R=base/'results'
for p in R.rglob('*'):
 if not p.is_file():continue
 if p.suffix in ('.pkl','.pyc'):continue
 if p.name.endswith('.csv.gz') or p.name.endswith('.json') or p.name.endswith('.txt') or p.name.endswith('.csv') or p.name=='analysis.stdout':
  paths.append((p,'results/'+p.relative_to(R).as_posix()))
for p in (base/'checkpoints').glob('*_RECEIPT.json'):
 paths.append((p,'checkpoints/'+p.name))
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
manifest={'name':'R9 V2 30s hindsight/foresight source-exact train and optimize research',
 'trade_coverage':'all eight complete original source-month datasets',
 'status':'UNAPPROVED: 80% daily/weekly/monthly and 85% synthetic volume not jointly achieved',
 'original_frozen_r9_v2_commit':'35056fa38c11a7b2e9b9d6bab984af3368e905be',
 'scientific_caveat':'R9 style early-exit 30s quality proxy is NOT exact 30s mark-to-market first-passage classification',
 'full_feature_arrays_preserved_in':'8 separate *_FULL_FEATURE_CHECKPOINT.zip files, each with its own SHA256 manifest',
 'files':{a:{'bytes':p.stat().st_size,'sha256':sha(p)} for p,a in paths}}
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=4) as z:
 for p,a in paths:z.write(p,a)
 z.writestr('SOURCE_EXACT_MANIFEST.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 for a,m in manifest['files'].items():assert hashlib.sha256(z.read(a)).hexdigest()==m['sha256']
receipt={'file':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'archived_files':len(paths)+1,'crc':'PASS','file_sha256':'PASS'}
(base/'docs/MAIN_RECOVERY_RECEIPT.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt,indent=2))

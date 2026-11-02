"""Create hash-verified independent recovery packages, no summary substitution."""
import zipfile,hashlib,json,os,glob
from pathlib import Path
R=Path('/mnt/data/r9_v2_eight_source_training_20261101');OUT=Path('/mnt/data');M=('01','02','06','07')
def hashfile(f):
 h=hashlib.sha256()
 with open(f,'rb') as inp:
  for chunk in iter(lambda:inp.read(2**20),b''):h.update(chunk)
 return h.hexdigest()
def make(name,files):
 path=OUT/name
 manifest={'archive':name,'release_status':'TRAINED_RESEARCH_ONLY; NO ACCEPTED POLICY','files':{}}
 with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
  for source,entry in files:
   z.write(source,entry)
   manifest['files'][entry]={'sha256':hashfile(source),'bytes':source.stat().st_size}
  z.writestr('REPRODUCIBLE_SHA256_MANIFEST.json',json.dumps(manifest,indent=2))
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None
  for k,v in manifest['files'].items():
   assert hashlib.sha256(z.read(k)).hexdigest()==v['sha256']
 return {'name':name,'bytes':path.stat().st_size,'sha256':hashfile(path),'verified_files':len(files),'crc_pass':True,'sha_pass':True}
allfiles=[]
for sub in ('src','tests','docs','results'):
 for p in (R/sub).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts:allfiles.append((p,'training/'+p.relative_to(R).as_posix()))
for p in (R/'checkpoints').glob('*.txt'):allfiles.append((p,'training/checkpoints/'+p.name))
for p in (R/'checkpoints').glob('*receipt.json'):allfiles.append((p,'training/checkpoints/'+p.name))
for p in (R/'checkpoints').glob('*mmap.json'):allfiles.append((p,'training/checkpoints/'+p.name))
for p in (R/'checkpoints').glob('*feature_names.json'):allfiles.append((p,'training/checkpoints/'+p.name))
for p in (R/'original/code').rglob('*'):
 if p.is_file(): allfiles.append((p,'original_v2_code/'+p.relative_to(R/'original/code').as_posix()))
base=OUT/'R9_V2_EIGHT_SOURCE_HINDSIGHT_TEACHER_TRAINING_SOURCE_MODELS_20261101.zip'
main=make(base.name,allfiles)
check=[]
for s in ('coinexx','dukascopy'):
 for m in M:
  p=R/'checkpoints'/f'{s}_{m}_tick_asof.pkl.gz'
  receipt=R/'checkpoints'/f'{s}_{m}_feature_receipt.json'
  mm=R/'checkpoints'/f'{s}_{m}_mmap.json'
  name=f'R9_V2_TEACHER_TRAINING_EXACT_QUOTE_FEATURES_{s.upper()}_{m}_20261101.zip'
  check.append(make(name,[(p,f'features/{p.name}'),(receipt,f'features/{receipt.name}'),(mm,f'features/{mm.name}')]))
(R/'results'/'RECOVERY_PACKAGE_INDEX.json').write_text(json.dumps({'primary':main,'checkpoints':check},indent=2))
print(json.dumps({'primary':main,'checkpoints':check},indent=2))

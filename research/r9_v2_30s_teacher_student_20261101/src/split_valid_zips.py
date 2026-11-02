from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib,json,sys,shutil
root=Path('/mnt/data/v2_30s_teacher_training/checkpoints')
month=sys.argv[1];src='COINEXX'
original=root/f'R9_V2_30S_TEACHER_{src}_2026_{month}_FULL_FEATURE_CHECKPOINT.zip'
with ZipFile(original) as z:
 names=z.namelist();feat=f'coinexx_{month}_features.pkl'
 for group in ('A','B'):
  wanted=[feat] if group=='A' else [n for n in names if n!=feat]
  name=f'R9_V2_30S_COINEXX_2026_{month}_VALID_PART_{group}.zip'
  out=Path('/mnt/data')/name
  with ZipFile(out,'w',ZIP_DEFLATED,compresslevel=1) as w:
   for n in wanted:
    with z.open(n) as f, w.open(n,'w') as o:
     shutil.copyfileobj(f,o,1024*1024)
   w.writestr('PART_ORIGIN.json',json.dumps({'original_zip':original.name,'original_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),
    'part':group,'included_original_members':wanted,'reconstruction':'Extract both PART_A and PART_B archives to the same destination; verify MONTH_MANIFEST.json for original file hashes.'},indent=2))
  with ZipFile(out) as v:assert v.testzip() is None
  print(name,out.stat().st_size,hashlib.sha256(out.read_bytes()).hexdigest())

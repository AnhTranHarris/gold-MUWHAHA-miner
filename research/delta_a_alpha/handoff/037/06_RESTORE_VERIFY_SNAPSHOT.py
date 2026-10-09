#!/usr/bin/env python3
"""Verify preserved V1 snapshot parts; concatenate optionally; NEVER touches sealed August inputs."""
import argparse,csv,hashlib,json,shutil,subprocess,sys
from pathlib import Path
BLOCK=1024*1024

def digest(f):
 h=hashlib.sha256()
 with f.open('rb') as inp:
  for chunk in iter(lambda:inp.read(BLOCK),b''):h.update(chunk)
 return h.hexdigest()

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--folder',type=Path,default=Path(__file__).resolve().parent)
 ap.add_argument('--join',action='store_true',help='Recreate COMPLETE_WORKSPACE.tar.zst, requires ample disk')
 ap.add_argument('--extract-to',type=Path,help='Only after full hashes pass; will extract all source files')
 a=ap.parse_args()
 p=a.folder
 j=json.loads((p/'05_BACKUP_VOLUME_AND_EXTERNAL_SOURCE_MAP.json').read_text())
 records=j['volumes'];full=hashlib.sha256(); count=0
 for r in records:
  f=p/r['name']
  assert f.is_file(),f'MISSING {f}'
  assert f.stat().st_size==r['size_bytes'],f'WRONG SIZE {f}'
  h=hashlib.sha256()
  with f.open('rb') as inp:
   for block in iter(lambda:inp.read(BLOCK),b''):
    h.update(block);full.update(block)
  assert h.hexdigest()==r['sha256'],f'CHUNK SHA MISMATCH {f}'
  count+=1
 assert full.hexdigest()==j['compressed_archive_sha256'],'FULL ARCHIVE SHA MISMATCH'
 print(f'VERIFIED {count} ordered chunks, joined archive SHA256={full.hexdigest()}')
 if a.join or a.extract_to:
  dest=p/'COMPLETE_WORKSPACE.tar.zst'
  with dest.open('wb') as dst:
   for r in records:
    with (p/r['name']).open('rb') as inp:shutil.copyfileobj(inp,dst,length=BLOCK)
  assert digest(dest)==j['compressed_archive_sha256']
  print('JOINED_OK',dest)
  subprocess.run(['zstd','-q','-t',str(dest)],check=True)
  print('COMPRESSED_TAR_STREAM_OK')
  if a.extract_to:
   a.extract_to.mkdir(parents=True,exist_ok=True)
   subprocess.run(['tar','--use-compress-program=zstd','-xf',str(dest),'-C',str(a.extract_to)],check=True)
   print('EXTRACTED',a.extract_to)
   manifest=p/'03_ALL_LOCAL_FILES_MANIFEST.csv'
   with manifest.open() as f:
    rows=list(csv.DictReader(f))
   bad=[]
   for row in rows:
    file=a.extract_to/row['path']
    if row['kind']=='symlink':
     if not file.is_symlink():bad.append([row['path'],'SYMLINK_MISSING'])
     continue
    if not file.is_file() or digest(file)!=row['sha256']:bad.append([row['path'],'HASH_MISMATCH'])
   assert not bad,f'{len(bad)} source files fail: {bad[:5]}'
   print('RESTORED_SHA256_VERIFIED',len(rows),'files_and_symlinks')
 print('August SEALED, deliberately absent; no original strategy performance certified by this integrity check.')
if __name__=='__main__':main()
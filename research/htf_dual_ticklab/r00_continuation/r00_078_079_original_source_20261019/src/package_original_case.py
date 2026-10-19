"""Complete byte-preserving research case ZIP + 10-part transport + SHA/CRC verification."""
from pathlib import Path
import zipfile,hashlib,json,math
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/'XAUUSD_R00_078A_B_R00_079_ORIGINAL_RESEARCH_20261019.zip'
manifest=json.loads((ROOT/'SHA256_ALL_FILES_MANIFEST.json').read_text())
with zipfile.ZipFile(OUT,'w',allowZip64=True) as z:
 for item in manifest['files']:
  z.write(ROOT/item['path'],arcname=item['path'],compress_type=zipfile.ZIP_STORED if (item['path'].endswith(('.npz','.zip','.joblib','.gz'))) else zipfile.ZIP_DEFLATED,compresslevel=3)
 z.write(ROOT/'SHA256_ALL_FILES_MANIFEST.json',arcname='SHA256_ALL_FILES_MANIFEST.json',compress_type=zipfile.ZIP_DEFLATED,compresslevel=3)
with zipfile.ZipFile(OUT) as z:
 assert z.testzip() is None,'bad CRC'
 assert len(z.namelist())==len(manifest['files'])+1
 for item in manifest['files']:
  with z.open(item['path']) as f:
   h=hashlib.sha256()
   for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
   assert h.hexdigest()==item['sha256'],item['path']
 print('ZIP PASS',len(z.namelist()),'members')
with OUT.open('rb') as f:zip_sha=hashlib.file_digest(f,'sha256').hexdigest()
PARTS=ROOT.parent/'R00_078_079_ARCHIVE_10_PARTS';PARTS.mkdir(exist_ok=True)
size=OUT.stat().st_size;part_size=math.ceil(size/10)
records=[]
with OUT.open('rb') as f:
 for i in range(10):
  p=PARTS/f'{OUT.name}.part{i+1:02d}-of-10'
  with p.open('wb') as g:
   remaining=min(part_size,size-part_size*i);h=hashlib.sha256()
   while remaining:
    block=f.read(min(8*1024*1024,remaining));assert block
    g.write(block);h.update(block);remaining-=len(block)
  records.append(dict(name=p.name,bytes=p.stat().st_size,sha256=h.hexdigest(),order=i+1))
assert sum(p['bytes'] for p in records)==size
receipt={'archive':OUT.name,'file_bytes':size,'archive_sha256':zip_sha,'zip_entries':len(manifest['files'])+1,'member_sha_manifest':'SHA256_ALL_FILES_MANIFEST.json','zip_crc_pass':True,'all_member_sha_pass':True,'parts':records,'reassemble':'Concatenate part01 through part10 as raw bytes in that exact order; verify archive_sha256; unzip and verify SHA256_ALL_FILES_MANIFEST.json; do NOT decompress each part separately','old_backtest_engines_modified':False}
(PARTS/'REASSEMBLE_SHA256_MANIFEST.json').write_text(json.dumps(receipt,indent=2)+'\n')
(ROOT/'ORIGINAL_ARCHIVE_RELEASE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('ARCHIVE',str(OUT),size,zip_sha)
print('PARTS',str(PARTS),records)

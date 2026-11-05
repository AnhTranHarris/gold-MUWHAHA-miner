"""Lossless additive artifact packager; hashes every archive member and CRC."""
from pathlib import Path
import hashlib, zipfile, json, sys
ROOT=Path('/mnt/data/r26')

def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def package(root,out):
 root=Path(root);out=Path(out)
 files=sorted(p for p in root.rglob('*') if p.is_file())
 manifest={'classification':'RESEARCH_ONLY_EXACT_ORIGINAL_BYTES','files':[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]}
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=5,allowZip64=True) as z:
  for p in files:z.write(p,p.relative_to(root).as_posix())
  z.writestr('R26_MANIFEST_SOURCE_BYTES_SHA256.json',json.dumps(manifest,indent=2)+'\n')
 with zipfile.ZipFile(out) as z:
  assert z.testzip() is None
  names=z.namelist()
  assert len(names)==len(files)+1
  for item in manifest['files']:
   i=z.getinfo(item['path'])
   assert i.file_size==item['bytes']
 # ZIP record proof stored OUTSIDE too
 print(json.dumps({'archive':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'members':len(files)+1,'source_root':str(root),'crc':'PASS'}))

if __name__=='__main__':package(sys.argv[1],sys.argv[2])

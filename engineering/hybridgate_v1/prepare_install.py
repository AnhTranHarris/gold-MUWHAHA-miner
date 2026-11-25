"""Stage the exact GitHub native candidate and pinned assets; never overwrite a terminal directory.
Uses Python standard library only. No downloads, training, or raw market data.
"""
from pathlib import Path
import argparse,ast,hashlib,io,json,re,shutil,struct,zipfile
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent

def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def sha_file(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def verified_zip(folder,pin):
 p=folder/pin['filename'];require(p.is_file(),f'missing {p.name}');require(sha_file(p)==pin['sha256'],f'archive hash mismatch {p.name}');return zipfile.ZipFile(p)
def npy(b):
 require(b[:6]==b'\x93NUMPY','invalid NPY magic');major=b[6];require(major in (1,2,3),'NPY version')
 n=struct.unpack_from('<H' if major==1 else '<I',b,8)[0];off=10 if major==1 else 12
 h=ast.literal_eval(b[off:off+n].decode('latin1' if major<3 else 'utf8'));shape=h['shape'];dt=h['descr']
 require(dt in ('<f4','<f8') and h['fortran_order'] is False and len(shape)==2 and all(type(x) is int and x>0 for x in shape),'unexpected NPY schema')
 raw=b[off+n:];require(len(raw)==shape[0]*shape[1]*int(dt[-1]),'NPY length mismatch');return shape,dt,raw

def fixture(npz):
 with zipfile.ZipFile(io.BytesIO(npz)) as z:
  x,xd,xb=npy(z.read('x.npy'));y,yd,yb=npy(z.read('y.npy'));r,rd,rb=npy(z.read('raw.npy'))
 require(x[0]==y[0] and y==r and xd=='<f4' and yd==rd=='<f8','fixture dimensions/dtypes')
 return struct.pack('<8sIII',b'HG5F\1\0\0\0',x[0],x[1],y[1])+xb+yb+rb

def stage(root,assets,dest,runtime_only=False):
 require(not dest.exists(),'destination already exists; never overwrite')
 pins=json.loads((HERE/'DEPENDENCY_PINS.json').read_text());qc=json.loads((HERE/'QC_INSTALL_MANIFEST.json').read_text());native=json.loads((HERE/'NATIVE_SOURCE_MANIFEST.json').read_text())
 require(len([x for x in qc if x.endswith('.hg5p')])==88,'model count');require(len([x for x in qc if x.startswith('MQL5/Scripts/')])==27,'QC source count')
 source={k:v for k,v in qc.items() if k.startswith('MQL5/Scripts/')}
 for rel,digest in {**source,**native}.items():require((root/rel).is_file() and sha_file(root/rel)==digest,'source hash mismatch '+rel)
 # Verify local source includes before any file is copied.
 headers={Path(k).name for k in source if k.endswith('.mqh')}|{Path(k).name for k in native if k.endswith('.mqh')}
 for rel in [*source,*native]:
  for inc in re.findall(r'^\s*#include\s+(?:"([^"]+)"|<HybridGateV1/([^>]+)>)',(root/rel).read_text(),re.M):require((inc[0] or inc[1]) in headers,'unresolved include '+str(inc))
 with verified_zip(assets,pins['Stage5_base']) as base,verified_zip(assets,pins['Stage5_D_I']) as di:
  dest.mkdir(parents=True,exist_ok=False);manifest={}
  def put(rel,b,expected):
   require(sha_bytes(b)==expected,'asset mismatch '+rel);p=dest/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);manifest[rel]=expected
  for rel,digest in native.items():put(rel,(root/rel).read_bytes(),digest)
  for rel,digest in source.items():
   b=(root/rel).read_bytes()
   if not runtime_only:put(rel,b,digest)
   if rel.endswith('.mqh') and Path(rel).name!='HG5CoreFixtureManifest.mqh':put('MQL5/Include/HybridGateV1/'+Path(rel).name,b,digest)
  for rel,digest in qc.items():
   name=Path(rel).name
   if rel.endswith('.hg5p'):put(rel,base.read('model_bank/'+name),digest)
   elif not runtime_only and rel.endswith('.hg5f'):put(rel,fixture(base.read('fixtures/inference/'+name.removesuffix('.hg5f')+'.npz')),digest)
   elif not runtime_only and name=='HG5CoreFixture.bin':put(rel,di.read('hg_stage5i/fixtures/HG5CoreFixture.bin'),digest)
  # License must accompany generated NumPy-derived math implementation.
  license=(HERE/'NUMPY_LICENSE.txt').read_bytes();put('NUMPY_LICENSE.txt',license,sha_bytes(license))
  require(all(sha_file(dest/k)==v for k,v in manifest.items()),'post-write verification failed')
  (dest/'INSTALL_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
  print(json.dumps({'status':'PASS staged bytes; not native compilation','files':len(manifest),'model_files':88,'fixtures':0 if runtime_only else 89,'source_files':sum(k.endswith(('.mqh','.mq5')) for k in manifest)},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--assets',type=Path,required=True);p.add_argument('--dest',type=Path,required=True);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--runtime-only',action='store_true');a=p.parse_args();stage(a.root,a.assets,a.dest,a.runtime_only)

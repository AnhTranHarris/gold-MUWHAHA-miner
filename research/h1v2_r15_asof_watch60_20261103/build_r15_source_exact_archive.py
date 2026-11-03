"""Create self-verifying immutable R15 additive research recovery package."""
from __future__ import annotations
import hashlib,json,zipfile
from pathlib import Path
BASE=Path(__file__).resolve().parent
TARGET=BASE/'H1V2_R15_WATCH60_BROKER_HINDSIGHT_FULL_SOURCE_AND_ALL_RESULTS_20261103.zip'
MANIFEST=BASE/'R15_MEMBER_SHA256_MANIFEST.json'
def sha(b):return hashlib.sha256(b).hexdigest()
paths=sorted(p for p in BASE.rglob('*') if p.is_file() and p!=TARGET and p!=MANIFEST
 if not any(z in p.parts for z in ('__pycache__','.pytest_cache')) and '.pyc' not in p.name)
files={str(p.relative_to(BASE)):{'sha256':sha(p.read_bytes()),'size':p.stat().st_size} for p in paths}
manifest={'purpose':'complete source exact RESEARCH R15 watch60 2026-11-03, all alternative source ordinal and full candidate receipts',
 'original_h1v2_teacher_sha':'edce573d9c53b743dc5de1b0d741c81370af52c1',
 'r9_v2_original_unchanged_sha':'ded3d0dff9d9112be52d9ddb29fbc7c6b9e2a1c0',
 'original_r14_parent_sha':'743bc5768fd39e34a7d2ea8d1528318c50692f8e',
 'not_actual_Coinexx_live_fills':True,'not_causal_oracle':True,'all_member_sha256_and_size':files}
MANIFEST.write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n',encoding='utf8')
with zipfile.ZipFile(TARGET,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8,allowZip64=True) as z:
 for p in paths+[MANIFEST]:
  b=p.read_bytes();r=str(p.relative_to(BASE))
  info=zipfile.ZipInfo(r,date_time=(2026,11,3,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
  z.writestr(info,b,compress_type=zipfile.ZIP_DEFLATED,compresslevel=8)
with zipfile.ZipFile(TARGET) as z:
 assert z.testzip() is None
 rec=json.loads(z.read(MANIFEST.name));expected=set(rec['all_member_sha256_and_size'])|{MANIFEST.name}
 assert expected==set(z.namelist())
 for name,v in rec['all_member_sha256_and_size'].items():
  b=z.read(name);assert len(b)==v['size'] and sha(b)==v['sha256'],name
print(json.dumps({'archive':str(TARGET),'sha256':sha(TARGET.read_bytes()),'bytes':TARGET.stat().st_size,
  'manifest_members':len(files),'all_member_sha256_verified':True,'zip_crc':True},indent=2))

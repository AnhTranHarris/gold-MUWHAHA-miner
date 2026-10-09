import hashlib,tarfile,json,os,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent; O=R/'output'; G=R/'src_legacy_reference'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
raw=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
assert sha(raw)=='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5','data hash mismatch'
files=[]
for p in R.glob('*.py'):
 if p.name.startswith('__'):continue
 files.append((p,'source/'+p.name))
for p in O.glob('*'):
 if not p.is_file():continue
 if p.name.startswith('JAN032_COMPLETE_') or p.name.endswith(('.tar','.tar.gz')):continue
 if p.name=='JAN032_Q_SWEEP.log':continue # interrupted after four settings; completed Q cases independently retained
 files.append((p,'results/'+p.name))
files=sorted(files,key=lambda x:x[1])
manifest={'checkpoint':'DAA_JAN032_ORIGINAL_SOURCE_RAW_TICK_REPLAY','status':'REAL_QUOTE_ORIGINAL_131E_SOURCE_MECHANICS_SUCCESS; GLOBAL_V1_FUNDED_CHILD_PARITY_NOT_CERTIFIED','month':'2026-01','source_raw_file':'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz','raw_data_sha256':sha(raw),'raw_tick_count':9135062,'source_fallback_commit':'e9189398fcf4fc47d7e2940adec54731ae047c31','source_classification':'restored legacy source dependencies, with manually recovered gp helper displayed in frozen GitHub path; P75 131E regression exact','r9_official_source':'research/delta_a_alpha/benchmarks/R9_REAL_SYNTH_JAN_JUL_2026.json','important':'archive contains no raw tick gzip and does not certify physical funding/margin or the later full whitepaper L0-L7 native/recovery implementation','files':{rel:{'size_bytes':p.stat().st_size,'sha256':sha(p)} for p,rel in files},'files_count':len(files)}
mfile=O/'JAN032_COMPLETE_SHA256_MANIFEST.json';mfile.write_text(json.dumps(manifest,indent=2))
afile=O/'DAA_JAN032_ORIGINAL_SOURCE_REAL_BIDASK_COMPLETE.tar.gz'
with tarfile.open(afile,'w:gz',compresslevel=6) as tar:
 for p,rel in files:tar.add(p,arcname=rel,recursive=False)
 tar.add(mfile,arcname='JAN032_COMPLETE_SHA256_MANIFEST.json',recursive=False)
with tarfile.open(afile,'r:gz') as tar:
 n=tar.getnames();assert len(n)==len(files)+1
 for p,rel in files:
  x=tar.extractfile(rel); assert x is not None
  h=hashlib.sha256(x.read()).hexdigest();assert h==manifest['files'][rel]['sha256'],rel
print('SOURCE_SHA_OK',True)
print('RECORD_FILES',len(files),'MANIFEST',mfile.name,'ARCHIVE_SIZE_BYTES',afile.stat().st_size)
print('ARCHIVE_SHA256',sha(afile))
print('ARCHIVE_MEMBERS_VERIFIED',len(n))
print('OUTPUTS',[(x.name,x.stat().st_size) for x in [O/'JAN032_ORIGINAL_V1_SOURCE_TICK_SCOREBOARD.xlsx',O/'DAA_JANUARY_032_FULL_SOURCE_REPLAY_AND_R9_COMPARISON.md',afile]])
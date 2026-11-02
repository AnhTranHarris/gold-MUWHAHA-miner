#!/usr/bin/env python3
from pathlib import Path
import hashlib,zipfile,json,sys,time
root=Path('/mnt/data/v2_30s_teacher_training');r=root/'results';out=root/'checkpoints';out.mkdir(exist_ok=True)
def hfile(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def pack(src,month):
 t=time.monotonic();files=[]
 for suffix in ['raw.pkl','features.pkl','micro.pkl','daily_baseline.csv','feature_provenance.json','micro_manifest.json']:
  p=r/f'{src}_{month}_{suffix}'
  if p.exists():files.append((p,p.name))
 for prefix in ['fold','volume']:
  for suffix in ['summary.json','selected_trades.csv.gz','trades.csv.gz']:
   p=r/f'{prefix}_{src}_{month}_{suffix}'
   if p.exists():files.append((p,p.name))
 for prefix in ['policy']:
  p=r/f'{prefix}_{src}_{month}'
  if p.is_dir():files.extend((f,f'{p.name}/{f.name}') for f in p.glob('*') if f.is_file())
 micro=r/'micro_optimized'/f'policy_{src}_{month}'
 if micro.is_dir():files.extend((f,'micro_optimized/'+micro.name+'/'+f.name) for f in micro.glob('*') if f.is_file())
 for prefix in ['fold','volume']:
  for suffix in ['summary.json','selected_trades.csv.gz','trades.csv.gz']:
   p=r/'micro_optimized'/f'{prefix}_{src}_{month}_{suffix}'
   if p.exists():files.append((p,'micro_optimized/'+p.name))
 source_refs=json.loads((root/'docs/SOURCE_DATA_SHA256.json').read_text())
 source_record=next(i for i in source_refs['raw_ticks_eight'] if i['source']==src and i['month']==month)
 manifest={'month':month,'source':src,'raw_tick_source_pin':source_record,
  'baseline_source_branch':'carson/r9-v2-eight-fullmonth-untrained-baseline-verified-20261101',
  'records_have_exact_entry_timestamp_no_sampling':True,
  'scientific_status':'UNAPPROVED',
  'file_hashes':{name:{'sha256':hfile(p),'bytes':p.stat().st_size} for p,name in files}}
 name=f'R9_V2_30S_TEACHER_{src.upper()}_2026_{month}_FULL_FEATURE_CHECKPOINT.zip'
 target=out/name
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as z:
  for p,n in files:z.write(p,n)
  z.writestr('MONTH_MANIFEST.json',json.dumps(manifest,indent=2))
 with zipfile.ZipFile(target) as z:
  assert z.testzip() is None
  for n,expected in manifest['file_hashes'].items():assert hashlib.sha256(z.read(n)).hexdigest()==expected['sha256']
 receipt={'source':src,'month':month,'zip':name,'bytes':target.stat().st_size,'sha256':hfile(target),'archived_files':len(files)+1,'sha256_integrity':'PASS','crc':'PASS','elapsed_s':round(time.monotonic()-t,2)}
 (out/f'{src}_{month}_RECEIPT.json').write_text(json.dumps(receipt,indent=2))
 print(json.dumps(receipt),flush=True)
if __name__=='__main__':pack(sys.argv[1],sys.argv[2])

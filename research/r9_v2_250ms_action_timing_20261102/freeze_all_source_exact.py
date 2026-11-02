#!/usr/bin/env python3
"""Source-exact eight independent immutable binary checkpoints, SHA256/CRC readback."""
from pathlib import Path
import zipfile,json,hashlib,argparse,datetime
ROOT=Path('/mnt/data/next_action_timing');OUT=ROOT/'checkpoints';OUT.mkdir(exist_ok=True)
MONTHS=['01','02','06','07'];SOURCES=['coinexx','dukascopy']
SOURCEFILES=[ROOT/n for n in ('src_action_timing.py','src_three_class_student.py','src_wait_value_model.py','analyze_timing_oracle.py','ablate_wait_features.py','freeze_all_source_exact.py','BUILD_RESEARCH_LOG.md')]
SOURCEFILES+=sorted((ROOT/'tests').glob('*.py'))
SOURCEFILES+=sorted((ROOT/'source').glob('*.py')) # original full reconstructed source from the verified previous checkpoint

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for part in iter(lambda:f.read(1<<20),b''):h.update(part)
 return h.hexdigest()

def freeze(src,mon):
 b=ROOT/'results'/f'{src}_{mon}_full';m=ROOT/'models'/f'{src}_{mon}'
 prog=json.loads((b/'PROGRESS_FULL.json').read_text());assert prog['status']=='COMPLETE'
 files=[]
 for p in sorted(b.glob('*.npz')):files.append((p,'source_month_labels/'+p.name))
 for p in sorted(m.rglob('*')):
  if p.is_file():files.append((p,'source_month_student/'+p.relative_to(m).as_posix()))
 for n in (f'{src}_{mon}_NEW_TIMING_HINDSIGHT_ORACLE.json',):
  files.append((ROOT/'results'/n,'inverse_oracle/'+n))
 for p in SOURCEFILES:files.append((p,'source_exact/'+p.relative_to(ROOT).as_posix()))
 manifest={'project':'R9_v2_250ms_action_timing_WAIT_student','status':'RESEARCH_REJECTED_NO_POLICY_PROMOTED',
    'source':src,'month':mon,'full_source_ticks':prog['input_ticks'],
    'full_250ms_events':prog['eligible_decisions'],'decisions_labeled':prog['completed_decisions'],
    'source_tick_sha256':prog['source_sha256'],'parent_original_branch':'carson/r9-v2-paired-action-firstpass-continuation-20261101',
    'new_branch':'carson/r9-v2-250ms-action-timing-wait-student-20261102',
    'files':{arc:{'sha256':sha(p),'bytes':p.stat().st_size} for p,arc in files}}
 out=OUT/f'R9_V2_250MS_TIMING_{src.upper()}_2026_{mon}_COMPLETE.zip'
 with zipfile.ZipFile(out,'w',zipfile.ZIP_STORED,allowZip64=True) as z:
  for p,arc in files:z.write(p,arc)
  z.writestr('SOURCE_EXACT_MANIFEST.json',json.dumps(manifest,indent=2))
 with zipfile.ZipFile(out) as z:
  assert z.testzip() is None
  for arc,rec in manifest['files'].items():assert hashlib.sha256(z.read(arc)).hexdigest()==rec['sha256']
 r={'source':src,'month':mon,'filename':out.name,'zip_sha256':sha(out),'zip_bytes':out.stat().st_size,
   'files':len(files)+1,'ticks':prog['input_ticks'],'decisions':prog['eligible_decisions'],
   'full_sha256_verified':True,'crc_ok':True,'approved':False}
 (OUT/f'{src}_{mon}_CHECKPOINT_RECEIPT.json').write_text(json.dumps(r,indent=2))
 print(json.dumps(r),flush=True);return r
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--source',choices=SOURCES,required=True);parser.add_argument('--month',choices=MONTHS,required=True)
 a=parser.parse_args();freeze(a.source,a.month)

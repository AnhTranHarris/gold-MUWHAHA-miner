"""R19-S3 source-exact frozen new-candidate full output and execution recovery archives."""
import json,hashlib,zipfile
from pathlib import Path
ROOT=Path('/mnt/data/h1v2_r19_broker_union');OUT=ROOT/'archives_r19_s3';OUT.mkdir(exist_ok=True)

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for v in iter(lambda:f.read(1<<20),b''):h.update(v)
 return h.hexdigest()

files=[]
for src in ('DUKASCOPY_RAW','MT5_BROKER_EXPORT'):
 for mon in ('01','02','06','07'):
  tag=f'R19S3_{src}_{mon}'
  base=ROOT/'results_s3_new_admission'
  paths=[base/f'{tag}_ALL_SOURCE_UTC_QUARTERS.csv',base/f'{tag}_ALL_TARGETED_CANDIDATE_SOURCE_ORDINALS_AND_DUAL_ACTION_LABELS.npz',base/f'{tag}_SOURCE_AND_OUTPUT_RECEIPT.json',base/f'{tag}_INDEPENDENT_SOURCE_VERIFIER_PASS.json',ROOT/'src'/'r19_s3_targeted_source_admission.py',ROOT/'verify_r19_s3_source_exact.py']
  for p in paths:
   if not p.exists():raise FileNotFoundError(p)
  names={('source/' if p.suffix=='.py' else 'evidence/')+p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths}
  msg=('R19-S3 OFFLINE HISTORICAL HINDSIGHT CAPACITY ONLY. Each source quote of first observed actual 25-ms bin is admitted only with observed 300-second fresh history after >15s raw quote drought, original source spread<=4, first actual quote after 100ms max additional age1s, actual entry fill spread<=4, same side-independent nominal price net+$0.10 before adverse opening liquidation -$0.10 within 60sec. Offline future-side evaluation and scheduling are FUTURE KNOWLEDGE, not an as-of student. Previously verified R19 selected original positions are NEVER displaced. These new quote candidate labels are distinct from original R11S1 15F/full30 zero adverse and original R9 dynamic exit. No dealer fills, account cash, margin risk, independent OOS or trade signal skill proven. All original R19-S1 source archives, R18 prior failures and GitHub branches remain unchanged.\n').encode()
  names['SCIENTIFIC_FIREBREAK.txt']={'bytes':len(msg),'sha256':hashlib.sha256(msg).hexdigest()}
  manifest={'tag':tag,'upstream_R18_immutable_SHA':'6572ad03ae76daa80e188f213a5a2d1279dac42b','all_exact_source_members':names}
  archive=OUT/f'{tag}_COMPLETE_25MS_NEW_ASOF_CANDIDATE_ALL_DUAL_ACTIONS_15M_HOUR_AND_HASHED_SOURCE_20261103.zip'
  with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   z.writestr('SCIENTIFIC_FIREBREAK.txt',msg)
   for p in paths:
    z.write(p,('source/' if p.suffix=='.py' else 'evidence/')+p.name)
   z.writestr('ALL_MEMBER_SHA256.json',json.dumps(manifest,indent=2))
  with zipfile.ZipFile(archive) as z:
   if z.testzip() is not None:raise AssertionError('CRC_ERR '+tag)
   for name,meta in names.items():
    data=z.read(name)
    assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256']
  files.append({'source':src,'month':mon,'archive':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive),'member_count':len(names),'local_all_member_SHA_and_CRC_PASS':True})
  print('R19S3_ARCHIVE_PASS',src,mon,archive.stat().st_size,flush=True)
master={'stage':'R19S3_EIGHT_SOURCE_25MS_COMPLETE_FUTURE_ORACLE_ONLY','source_months':len(files),'original_15F30S_unchanged':True,'archives':files}
(OUT/'R19S3_EIGHT_SOURCE_ARCHIVES_SHA256_MANIFEST.json').write_text(json.dumps(master,indent=2)+'\n')
print('R19S3_ALL_EIGHT_READY')

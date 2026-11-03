#!/usr/bin/env python3
"""Build two restartable source-exact archives, no original source alteration."""
from pathlib import Path
import zipfile,hashlib,json,os,time
ROOT=Path('/mnt/data');NEW=ROOT/'h1v2_r12_native';OUT=NEW/'reports';R12=ROOT/'h1v2_r12'

def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def pack(out,rows):
 pins={}
 if out.exists(): raise FileExistsError('archive name already exists (never silently overwrite): '+str(out))
 with zipfile.ZipFile(out,'w') as z:
  seen=set()
  for arc,p in rows:
   if arc in seen: raise ValueError('DUPLICATE_ARCHIVE_PATH '+arc)
   seen.add(arc);assert p.is_file(),p
   b=p.read_bytes();pins[arc]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
   compress=zipfile.ZIP_STORED if p.suffix in ('.zip','.npz','.gz') else zipfile.ZIP_DEFLATED
   z.writestr(arc,b,compress_type=compress,compresslevel=6)
  manifest={'scientific_class':'original future-informed hindsight no causal profit claim','total_pinned_member_count':len(pins),'sha256_of_complete_original_uncompressed_members':pins,'archive_unchanged_sources':True,'previous_R12D_branch_parent_SHA':'c46d6bd30ec5a4a2ca120dcd46246114eadbed98','no_original_Github_mutation':True}
  z.writestr('R12BN_EXACT_ARCHIVE_INTERNAL_SHA256_MANIFEST.json',json.dumps(manifest,indent=2)+'\n',compress_type=zipfile.ZIP_DEFLATED)
 with zipfile.ZipFile(out) as z:
  assert z.testzip() is None
  for arc,v in pins.items():
   b=z.read(arc);assert len(b)==v['bytes'] and hashlib.sha256(b).hexdigest()==v['sha256']
 print(out,'BYTES',out.stat().st_size,'sha',sha(out),'members',len(pins)+1,flush=True)
 return {'file':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'members':len(pins)+1,'internal_all_sha_verified':True,'zip_crc':True}

def run():
 a=[]
 def add(n,p):a.append((n,Path(p)))
 for p in sorted((NEW/'source').glob('*.py')):add('NEW_SOURCE/'+p.name,p)
 for p in sorted((NEW/'tests').glob('*.py')):add('TESTS/'+p.name,p)
 add('SOURCE_README_FULL_UNABRIDGED/README_R12BN_FULL_SOURCE_NO_SUMMARY.md',NEW/'README_R12BN_FULL_SOURCE_NO_SUMMARY.md')
 for name in ('H1V2_COMPLETE_DEEP_HOURLY_AUDIT_20261103.md','H1V2 R11 APPEND-ONLY R&D EXECUTION AND RECOVERY LEDGER — 20261102.txt','H1V2 R11 FULL SOURCE-LEVEL FORENSIC AUDIT — UNSHORTENED — 20261102.txt','H1V2 COMPLETE FORENSIC AUDIT — R0–R10 — ORIGINAL FULL TECHNICAL RECORD — 20261102.txt','H1V2_R12_UNABRIDGED_APPEND_ONLY_PROGRESS_LEDGER_20261103.txt'):
  add('HISTORIC_FULL_UNABRIDGED_RESEARCH/'+name,ROOT/name)
 for name in ('R12DQ_COMPLETE_ALL_11520_SOURCE_QUARTERS_S4_R12_R12DQ.csv','R12DQ_COMPLETE_ALL_2880_SOURCE_HOURS_S4_R12_R12DQ.csv','R12DQ_COMPLETE_ALL_208_PROVEN_INFEASIBLE_SOURCE_QUARTERS.csv'):
  add('IMMUTABLE_R12DQ_COMPLETE_SOURCE_CONTROL/'+name,ROOT/name)
 add('IMMUTABLE_R12DQ_FULL_PRIOR_SOURCE_AND_COMPLETE_EXECUTION_ARCHIVE.zip',ROOT/'R12DQ_A_UNABRIDGED_SOURCE_ORIGINAL_AUDIT_11520_QUARTER_SCIENCE_20261103.zip')
 add('ORIGINAL_R9_SYNTH_INDEX/R9_SYNTH_TICK_DRIVE_INDEX.csv',ROOT/'R9_SYNTH_TICK_DRIVE_INDEX.csv')
 for p in sorted((R12/'atomic_r9_synth').glob('*.entry_receipt.json')):
  add('ORIGINAL_R9_SYNTH_ALL_86_COMPLETE_SOURCE_DAILY_EVENT_RECEIPTS/'+p.name,p)
 for p in sorted(OUT.iterdir()):
  if not p.is_file() or p.suffix not in ('.csv','.json','.log'):continue
  add('FULL_NEW_R12BN_RESULT_SOURCE_HOUR_QUARTER_DAY_AND_EXECUTION_LOGS/'+p.name,p)
 archiveA=OUT/'R12BN_A_SOURCE_FULL_UNABRIDGED_11520_QUARTER_FOURMONTH_20261103.zip';x=pack(archiveA,a)
 b=[]
 for p in sorted((NEW/'atomic').glob('*.npz')):b.append(('FULL_OBSERVED_SOURCE_QUOTE_ORDINAL_TRACES/'+p.name,p))
 for p in sorted((NEW/'atomic').glob('*.json')):b.append(('PER_DAY_SOURCE_AND_TRACE_SHA256_RECEIPTS/'+p.name,p))
 archiveB=OUT/'R12BN_B_ALL_88_ATOMIC_NATIVE_SOURCE_QUOTE_TRACES_20261103.zip';y=pack(archiveB,b)
 allm={'archives':[x,y], 'full_months':['01','02','06','07'], 'full_source_calendar_quarters':11520, 'full_source_calendar_hours':2880, 'full_source_selected_traces_asof_first250':949204,'full_source_selected_traces_asof_distinct':984666,'source_daily_files_verification_performed':88,'source_R9_SYNTH_ticklog_original_unique_daily_SHA_pins':86,'not_broker_real':True,'no_policy_promotion':True}
 dest=OUT/'R12BN_TWO_ZIP_SOURCE_EXACT_RECOVERY_MANIFEST.json';dest.write_text(json.dumps(allm,indent=2)+'\n')
 return allm
if __name__=='__main__':print(json.dumps(run(),indent=2))

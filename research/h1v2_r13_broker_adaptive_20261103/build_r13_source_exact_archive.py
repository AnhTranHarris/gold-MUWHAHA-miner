#!/usr/bin/env python3
"""Reproducible append-only R13 artifact builder and unabridged report writer.

Avoid rewriting any original historic source. Every new source/result/trace/test
is independently manifest SHA-256 pinned; the ZIP itself is separately hashed.
"""
from __future__ import annotations
import csv, hashlib,json,os,zipfile
from pathlib import Path
R=Path(__file__).resolve().parent;T=R/'results'
SRC=Path('/mnt/data')

def sha(b):return hashlib.sha256(b).hexdigest()

def sha_file(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for block in iter(lambda:f.read(2**20),b''):h.update(block)
 return h.hexdigest()

def markdown_table_csv(p):
 with p.open(newline='',encoding='utf8') as f:rows=list(csv.reader(f))
 assert len(rows)>1
 out=['| '+' | '.join(x.replace('|','\\|') for x in rows[0])+' |',
      '|'+'|'.join('---' for _ in rows[0])+'|']
 out+=['| '+' | '.join(x.replace('|','\\|') for x in row)+' |' for row in rows[1:]]
 return '\n'.join(out)+'\n'

def report():
 sections=[
  '# R13 COMPLETE FULL-ROW BROKER-ADAPTIVE H1V2 RESEARCH REPORT — 2026-11-03\n',
  'READ WITH THE COMPLETE 85,961-character ORIGINAL 2026-11-03 H1V2 forensic audit and original 251,650-character R11 ledger included in the source ZIP. These are research-exposed, not blind OOS, never deployed. All future-selected entries are privileged. All full primary source quotes remain SHA-pinned external source, without source modification.\n',
  '## 0. Unabridged source mechanism, exact economics, original negative controls and recovery protocol\n',
  (R/'README_R13_SOURCE_EXACT.md').read_text(encoding='utf8'),
 ]
 parts=[
 ('45 FULL HOURLY SOURCE X 5 LANES X 3 HORIZON ENTRIES','R13_ALL_45_SOURCE_LANE_HORIZON_RESULTS.csv'),
 ('180 FULL 15-MINUTE SOURCE X 5 LANES X 3 HORIZONS X 4 QUARTERS','R13_ALL_180_SOURCE_QUARTER_LANE_HORIZON_RESULTS.csv'),
 ('135 COMPLETE FROZEN FUTURE SIGNAL DELAY/FRICTION SCENARIOS','R13_ALL_135_NEW_LANE_LATENCY_SLIPPAGE_SCENARIOS.csv'),
 ('540 COMPLETE DELAY/FRICTION SOURCE QUARTER BUCKETS','R13_ALL_540_QUARTER_DELAY_FRICTION_SCENARIOS.csv'),
 ('27 AS-OF DYNAMIC HORIZON 3-SOURCE DELAY/FRICTION SCENARIOS','R13_ALL_27_ASOF_DYNAMIC_HORIZON_DELAY_SCENARIOS.csv'),
 ('108 COMPLETE DYNAMIC HORIZON SOURCE QUARTER/FRICTION ROWS','R13_ALL_108_ASOF_DYNAMIC_HORIZON_DELAY_QUARTERS.csv'),
 ]
 for title,name in parts:
  p=T/name;rows=sum(1 for _ in p.open(newline=''))-1
  sections.append('\n## '+title+'\n')
  sections.append('VERBATIM, COMPLETE, original '+p.name+': '+str(rows)+' exact data rows; all columns retained. The full matching original CSV bytes are also in the research ZIP and SHA-pinned.\n')
  sections.append(markdown_table_csv(p))
 sections.append('\n## Full raw quote ordinal and original price exactness register\n')
 receipt=json.loads((T/'R13_FULL_SOURCE_INDEPENDENT_TRACE_REVERIFICATION.json').read_text())
 sections.append('```json\n'+json.dumps(receipt,indent=2)+'\n```\n')
 sections.append('\nAll 135 frozen future original signal stress and 27 dynamic source stress scenarios retain their COMPLETE original raw quote ordinals and BUY/SELL directions in 162 individually separate SHA-pinned NPZ arrays. Three full all-candidate label NPZ source arrays, three full 36,505 trade ordinal fixed trace CSV sources, three complete adaptive-source selected trace CSVs of 2,946 records, three dynamic candidate/label NPZs, tests and exact source headers remain separately in the ZIP. These binary arrays are preserved losslessly; no claim that this markdown substitutes for them.\n')
 final=R/'R13_COMPLETE_UNABRIDGED_RESEARCH_REPORT_20261103.md'
 final.write_text('\n'.join(sections),encoding='utf8')
 return final

def build():
 r=report()
 includes=[]
 for p in sorted(R.rglob('*')):
  if not p.is_file():continue
  if p.name.endswith('.pyc') or '__pycache__' in p.parts or '.pytest_cache' in p.parts:continue
  if p.name in ('R13_ALL_MEMBER_SHA256_MANIFEST.json','R13_SOURCE_EXACT_RECOVERY_PACKAGE_20261103.zip','R13_ARCHIVE_CHECKSUM_RECEIPT.json'):continue
  includes.append((str(p.relative_to(R)),p))
 parent=[
 ('IMMUTABLE_UPSTREAM/H1V2_COMPLETE_DEEP_HOURLY_AUDIT_20261103.md',SRC/'H1V2_COMPLETE_DEEP_HOURLY_AUDIT_20261103.md'),
 ('IMMUTABLE_UPSTREAM/H1V2_R11_APPEND_ONLY_COMPLETE_LEDGER_20261102.txt',SRC/'H1V2 R11 APPEND-ONLY R&D EXECUTION AND RECOVERY LEDGER — 20261102.txt'),
 ('IMMUTABLE_UPSTREAM/H1V2_R11_COMPLETE_HYPOTHESIS_REGISTER_20261102.txt',SRC/'H1V2 R11 COMPLETE HYPOTHESIS-FALSIFICATION MATRIX AND SOURCE CONTRACT — 20261102.txt'),
 ('IMMUTABLE_UPSTREAM/H1V2_R12_PROGRESS_LEDGER_THROUGH_SOURCE_0015.txt',SRC/'H1V2_R12_UNABRIDGED_APPEND_ONLY_PROGRESS_LEDGER_20261103.txt'),
 ('IMMUTABLE_UPSTREAM/R12C_CROSS_BROKER_ALPHA_HYPOTHESES_RESEARCH_CHARTER.md',SRC/'R12C_CROSS_BROKER_ALPHA_HYPOTHESES_RESEARCH_CHARTER.md'),
 ]
 for path,p in parent:
  if not p.is_file():raise FileNotFoundError(p)
  includes.append((path,p))
 assert len(set(x[0] for x in includes))==len(includes)
 pins={path:{'sha256':sha_file(p),'bytes':p.stat().st_size} for path,p in includes}
 manifest={'research':'H1V2_R13_BROKER_ADAPTIVE_ENTRY_FULL_UNABRIDGED','source_class':'research_hindsight_only',
  'immutable_GitHub_parent_R12C_SHA':'83c63e5c56f36729c8da1c461a344f79c321ef25',
  'original_input_source_SHA256':{k:v[1] for k,v in __import__('sys').modules['__main__'].__dict__.get('RAW_SOURCE_PINS',{}).items()} if False else {
  'R9_REAL_MT5_TESTER':'24e4b31935ead7b0eb039fe84dc8972c59500b362cac21721739f1b0c050b3d7',
  'R9_SYNTH_MT5_TESTER':'dcedb28f7453c80d2dec5ffe5d386dad1661134ba61765337155fbbaeb6213a2',
  'DUKASCOPY_RAW':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d'},
  'original_S1_horizon_helper_SHA256':'c52de41072911ad53dedadfb3dba1899ea112e41a9e58e48ea29a7903e3ec475',
  'member_count':len(pins),'members':pins,'archive_contains_original_raw_gzip':False,
  'research_not_predictive_or_live':True,
  'independent_trace_verification':json.loads((T/'R13_FULL_SOURCE_INDEPENDENT_TRACE_REVERIFICATION.json').read_text())}
 mf=R/'R13_ALL_MEMBER_SHA256_MANIFEST.json';mf.write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n')
 archive=R/'R13_SOURCE_EXACT_RECOVERY_PACKAGE_20261103.zip'
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for path,p in sorted(includes):z.write(p,arcname=path)
  z.write(mf,arcname=mf.name)
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None
  for path,props in pins.items():
   b=z.read(path);assert len(b)==props['bytes'] and sha(b)==props['sha256'],path
  assert len(z.namelist())==len(includes)+1
  assert json.loads(z.read(mf.name))['members']==pins
 receipt={'archive_sha256':sha_file(archive),'archive_bytes':archive.stat().st_size,
  'member_count_excluding_manifest':len(includes),'member_SHA256_all_verified':True,'ZipCRC_all_ok':True,
  'report_size_bytes':r.stat().st_size,'report_sha256':sha_file(r),'status':'SOURCE_EXACT_ARCHIVE_FULL_ALL_DATA_NO_HISTORIC_MUTATION'}
 (R/'R13_ARCHIVE_CHECKSUM_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(receipt,indent=2))
if __name__=='__main__':build()

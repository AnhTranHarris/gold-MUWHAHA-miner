#!/usr/bin/env python3
"""Build manifest + ZIP, verify CRC, member sizes and SHA256 one-for-one."""
import hashlib,json,zipfile,sys,os
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=Path('/mnt/data/R9_BNP_HAWKES_FOUR_MONTH_DEV_20261101.zip')
files=sorted([p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ('manifest.json',)])
manifest={'title':'R9_BNP_HAWKES_FOUR_MONTH_DEV_20261101','status':'UNAPPROVED_RESEARCH_ONLY',
          'base_github_branch':'carson/r9-bnp-hawkes-entry-v1-20261101',
          'source_r9_commit':'8729a6345655a7b4ea31facc81982004ee2b8921',
          'source_research':'existing Coinexx/Dukascopy chronological replay, existing BNP-Hawkes v1',
          'months':['2026-01','2026-02','2026-06','2026-07'],
          'source_tick_files':'original months retained in primary Google Drive and Dukascopy Drive; SHA pinned by collection reports',
          'files':[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2))
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files+[root/'manifest.json']:z.write(p,p.relative_to(root))
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 for record in manifest['files']:
  assert hashlib.sha256(z.read(record['path'])).hexdigest()==record['sha256']
summary={'archive':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'count':len(files)+1,'crc_ok':True,'member_sha256_all_match':True}
Path('/mnt/data/R9_BNP_HAWKES_FOUR_MONTH_DEV_20261101_receipt.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))

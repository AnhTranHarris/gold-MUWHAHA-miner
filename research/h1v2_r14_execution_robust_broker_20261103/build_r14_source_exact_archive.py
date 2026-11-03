"""Full R14 source-exact ZIP, immutable member SHA and integrity checks."""
from pathlib import Path
import hashlib,zipfile,json
R=Path(__file__).resolve().parent
OUT=Path('/mnt/data/H1V2_R14_BROKER_TRANSFER_ROBUST9_SOURCE_EXACT_20261103.zip')
files=[R/'README_R14_SOURCE_EXACT.md',R/'R14_COMPLETE_UNABRIDGED_SOURCE_RESEARCH_REPORT_20261103.md',R/'src/r14_robust_envelope.py',R/'tests/test_r14_robust_envelope.py',R/'verify_r14_source_exact.py',R/'build_full_r14_report.py',R/'build_r14_source_exact_archive.py']
files += sorted(x for x in (R/'results').iterdir() if x.is_file())
files += sorted(x for x in (R/'logs').iterdir() if x.is_file() and x.suffix in ('.log','.txt'))

def digest(b):return hashlib.sha256(b).hexdigest()
manifest={}
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
 for p in files:
  b=p.read_bytes();arc=str(p.relative_to(R));assert arc not in manifest
  z.writestr(arc,b);manifest[arc]={'sha256':digest(b),'bytes':len(b)}
 meta={'original_R13_parent_sha':'8d2e5524edd6f52f43503e30060285d909855925','original_R9_V2':'ded3d0dff9d9112be52d9ddb29fbc7c6b9e2a1c0',
       'source_event_classification':'RETROSPECTIVE_FUTURE_PRIVILEGED_NOT_EXECUTION','complete_members':manifest,
       'unabridged_full_72_source_hours_288_quarters':True,'complete_18_candidates_by_nine_stress':True}
 z.writestr('R14_ARCHIVE_COMPLETE_MEMBER_SHA256_MANIFEST.json',json.dumps(meta,indent=2).encode()+b'\n')
with zipfile.ZipFile(OUT) as z:
 assert z.testzip() is None
 meta=json.loads(z.read('R14_ARCHIVE_COMPLETE_MEMBER_SHA256_MANIFEST.json'))
 for name,pin in meta['complete_members'].items():
  b=z.read(name);assert len(b)==pin['bytes'] and digest(b)==pin['sha256']
 assert len(z.namelist())==len(manifest)+1
sha=digest(OUT.read_bytes())
print(json.dumps({'output':str(OUT),'bytes':OUT.stat().st_size,'sha256':sha,'member_count':len(manifest)+1,'all_member_hashes_verified':True,'zip_crc_pass':True},indent=2))

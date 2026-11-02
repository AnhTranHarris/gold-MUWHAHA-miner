"""Deterministic source-exact R5 compact recovery + Github source transport."""
from __future__ import annotations
import hashlib,json,zipfile
from pathlib import Path
BASE=Path('/mnt/data/h1v2_r5');OUT=Path('/mnt/data')
PARENTS={
 'github_r4_parent_sha':'469f5bff1ee9158c7048c80bccf289cce90feb82',
 'r4_zip_sha256':'df2d7044eb06f4bd79fb09dd981a748fe01d4226276a74e413f41d9186d6049d',
 'r3_zip_sha256':'f249843499c295e777d2d17ed0732ce429cb9cbad698f49eed4bd587bb8b7484',
 'r2_zip_sha256':'4105f83b7562c36cf9eab94c190bf99ea7b191ee9de713a25daf460e7e7f692e',
 'h1v2_base_zip_sha256':'9a79d633c72be310737aee06627e5e8ee9df9ae0fea2658f5a159ad9328a2e61'
}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run():
    # No mutated original dependency files; source-exact full H1V2/R2/R3/R4 is referenced by pin.
    files=[p for sub in ('src','tests','results') for p in (BASE/sub).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    files += [BASE/'RESEARCH_CHECKPOINT.md',BASE/'H1V2_R5_RESEARCH_VERIFICATION_20261102.md',OUT/'R9_V2_ENTRY_ASYMMETRY_SOURCE_AUDIT_20261102.md']
    files.sort(key=lambda p:str(p))
    manifests={('ORIGINAL_AUDIT/'+p.name if p.parent==OUT else str(p.relative_to(BASE))):sha(p) for p in files}
    report={'scope':'H1V2 R5 source-exact research only','parent_pins':PARENTS,
      'raw_feed_sha256':{'01':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
       '02':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d',
       '06':'34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2',
       '07':'e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7'},
      'members_sha256':manifests,'date':'2026-11-02'}
    content=json.dumps(report,sort_keys=True,indent=2).encode('utf-8')
    package=OUT/'H1V2_R5_SIX_MARK_EXCITATION_FOUR_MONTH_RECOVERY_20261102.zip'
    with zipfile.ZipFile(package,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
      for p in files:z.write(p,arcname='ORIGINAL_AUDIT/'+p.name if p.parent==OUT else str(p.relative_to(BASE)))
      z.writestr('SOURCE_EXACT_SHA256_MANIFEST.json',content)
    with zipfile.ZipFile(package) as z:
      assert z.testzip() is None
      for fn,h in manifests.items():assert hashlib.sha256(z.read(fn)).hexdigest()==h
    print('R5 package',package,package.stat().st_size,sha(package),'members',len(manifests))
    # Keep Github commit compact; binary model files in checksum verified Drive ZIP, not Github.
    ghfiles={}
    for p in files:
      if p.parent==OUT:continue
      rel=str(p.relative_to(BASE))
      if rel.startswith('src/') or rel.startswith('tests/') or p.suffix in ('.json','.md'):
        ghfiles['research/h1v2_r5_20261102/'+rel]=p.read_text(encoding='utf8')
    ghfiles['research/h1v2_r5_20261102/SOURCE_EXACT_SHA256_MANIFEST.json']=content.decode('utf8')
    trans=OUT/'H1V2_R5_GITHUB_SOURCE_TRANSPORT_20261102.json'
    trans.write_text(json.dumps({'branch':'carson/h1v2-r5-fitted-excitation-asymmetric-20261102','parent':PARENTS['github_r4_parent_sha'],'files':ghfiles}))
    print('transport',trans,trans.stat().st_size,'github_files',len(ghfiles))
    return package,trans
if __name__=='__main__':run()

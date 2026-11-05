from pathlib import Path
import hashlib,json
R=Path('/mnt/data/r26')
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
files=sorted([*R.joinpath('src').glob('*.py'),*R.joinpath('tests').glob('*.py'),*R.joinpath('verification').glob('*.json'),R/'README_R26_20261104_FULL_CERTIFICATION_AND_NO_DEPLOYMENT.md',R/'R26_CERTIFIED_ALL_48_SOURCE_MONTH_POLICY_COMPLETE_RECONCILIATION.csv'])
rec={'scope':'NEW ADDITIVE R26 RESEARCH AFTER HORIZON F02 CORRECTION','parent_sha':'f439e870cc7f1abaeb47aa2172140c424e31c05f','original_h1v2_EA_untouched':True,'source_modules_test_and_verification_sha256':[{'path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size} for p in files]}
p=(R/'R26_FROZEN_AFTER_F02_SOURCE_MANIFEST_20261104.json');p.write_text(json.dumps(rec,indent=2)+'\n');print(p,sha(p))

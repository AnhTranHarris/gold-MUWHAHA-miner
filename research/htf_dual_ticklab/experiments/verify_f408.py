"""Independent immutable-input and output recount, without replay engine changes."""
import io,zipfile,json,pathlib,hashlib
import numpy as np
D=pathlib.Path(__file__).parent
source=D.parent/'F394_F395_EIGHTCELL_NATIVE_PATH_FROZEN_RESEARCH_UNAPPROVED_20261024.zip'
r=json.loads((D/'F408_R01_ALL8_REPORT.json').read_text())
assert hashlib.sha256(source.read_bytes()).hexdigest()==r['source_zip_sha256']
with zipfile.ZipFile(source) as z:
 assert z.testzip() is None
 for name,v in r['cells'].items():
  p=D/f'F408_R01_{name}_SCORES_MASKS.npz'
  with np.load(p) as f:
   a={k:f[k] for k in f.files}
  raw=z.read(f'F395_S14_{name}_FROZEN_ORIGINAL_EVENT_MASK.npz')
  assert hashlib.sha256(raw).hexdigest()==r['source_members_sha256'][name]
  with np.load(io.BytesIO(raw)) as s:
   for k,src in [('original_index','original_index'),('t','t'),('side','side'),('truth','truth'),('source_parent_veto','final_source_shadow_veto')]:
    assert np.array_equal(a[k],s[src]),(name,k)
  keep=a['frozen_keep'];good=a['truth']==0;bad=~good
  assert len(keep)==v['original_n']
  assert int((good&keep).sum())==v['correct_kept']
  assert int((bad&~keep).sum())==v['incorrect_rejected']
  assert np.all((a['score_wrong']>=0)&(a['score_wrong']<=1))
  print('PASS',name,'N',len(keep))
print('PASS eight source-exact event/mask/score recounts')

"""Independent saved-event recount, without importing policy/count helpers."""
import hashlib,io,json,zipfile
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;W=R.parent
cut=json.loads((R/'results/FROZEN.json').read_text())['cut'];out=[]
for month in ('01','02','06','07'):
    a=np.load(R/'results'/f'mask_{month}.npz');p=np.load(R/'results'/f'prob_{month}.npy')
    with zipfile.ZipFile(W/'sources/filter08_recovered.zip') as z:
        with np.load(io.BytesIO(z.read(f'FILTER08/FITTED_CLASSIFIER_SCORES_dukascopy_{month}.npz'))) as src:
            for key in ('t','original_side','truth_class','kept'):assert np.array_equal(src[key],a[key])
    values=p[:,:,2]/(p[:,:,0]+np.float32(1e-6));values[~a['gates']]=0
    risk=values.max(axis=1);v=risk>cut
    np.testing.assert_array_equal(risk,a['risk']);np.testing.assert_array_equal(v,a['veto'])
    n=len(v);ix=np.arange(n);b=[int(.6*n),int(.8*n),int(.9*n)];t=a['t']
    masks={'FIT':(ix<b[0])&(t+40000<t[b[0]]),'CAL':(ix>=b[0])&(ix<b[1])&(t+40000<t[b[1]]),
        'VAL':(ix>=b[1])&(ix<b[2])&(t+40000<t[b[2]]),'SHADOW':ix>=b[2]} if month=='01' else {}
    masks['FULL_MIXED' if month=='01' else 'FULL_EXPOSED']=np.ones(n,bool)
    report=json.loads((R/'results'/f'score_{month}.json').read_text());y=a['truth_class']
    for name,m in masks.items():
        d=report['counts'][name]
        assert d['incorrect_veto']==int((v&m&(y!=0)).sum())
        assert d['correct_lost']==int((v&m&(y==0)).sum())
        assert d['opposite_veto']+d['neutral_veto']==d['incorrect_veto']
    out.append(dict(month=month,n=n,identity='PASS',frozen_mask='PASS',counts='PASS'))
for h in range(3):
    p=R/'models'/f'expert_{h}.txt';d=json.loads(p.with_suffix('.json').read_text())
    assert d['rounds']==128 and hashlib.sha256(p.read_bytes()).hexdigest()==d['sha256']
(R/'results/INDEPENDENT_RECOUNT.json').write_text(json.dumps(dict(status='PASS',rows=out),indent=2)+'\n')
print('PASS: every original identity, frozen mask, split count and three128-round model hashes.')

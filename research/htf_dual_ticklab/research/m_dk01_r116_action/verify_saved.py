"""Independent saved-output recount; no fitting or feature reconstruction."""
import hashlib
import io
import json
from pathlib import Path
import zipfile
import numpy as np

ROOT=Path(__file__).resolve().parent
ARCHIVE=ROOT.parent/'sources/filter08_recovered.zip'
records=[]
for month in ('01','02','06','07'):
    a=np.load(ROOT/'cache'/f'actions_{month}.npz')
    with zipfile.ZipFile(ARCHIVE) as z:
        orig=np.load(io.BytesIO(z.read(f'FILTER08/FITTED_CLASSIFIER_SCORES_dukascopy_{month}.npz')))
        for key in ('t','original_side','truth_class','kept'):
            assert np.array_equal(a[key],orig[key]),(month,key)
    n=len(a['t']); idx=np.arange(n); y=a['truth_class']
    for view in ('full','ablation','online'):
        p=np.load(ROOT/'results'/f'prob_{view}_{month}.npy')
        frozen=json.loads((ROOT/'results'/f'frozen_{view}.json').read_text())
        lam=frozen['selected']['multiplier']
        utility=p[:,:,2]-lam*p[:,:,1];utility[:,0]=0
        actions=np.argmax(utility,axis=1)
        saved=np.load(ROOT/'results'/f'decisions_{view}_{month}.npz')
        assert np.array_equal(saved['t'],a['t'])
        assert np.array_equal(saved['side'],a['original_side'])
        assert np.array_equal(saved['truth'],y)
        assert np.array_equal(saved['teacher_kept'],a['kept'])
        assert np.array_equal(saved['action'],actions)
        report=json.loads((ROOT/'results'/f'score_{view}_{month}.json').read_text())
        for latency in (0,250,1000):
            no=a['touch_'+str(latency)][idx,actions]<0
            counts=dict(incorrect_no_touch=int(np.count_nonzero(no&(y!=0))),
                correct_no_touch=int(np.count_nonzero(no&(y==0))),
                opposite_no_touch=int(np.count_nonzero(no&(y==1))),
                neutral_no_touch=int(np.count_nonzero(no&(y==2))))
            rr=next(r for r in report['counts'] if r['split'].startswith('FULL_') and r['latency']==latency)
            assert all(rr[k]==v for k,v in counts.items()),(month,view,latency)
            assert counts['incorrect_no_touch']==counts['opposite_no_touch']+counts['neutral_no_touch']
            if latency==250:
                assert np.array_equal(no,saved['no_touch'])
                records.append(dict(month=month,view=view,n=n,**counts))
out=dict(status='PASS',rows=records,original_event_total=sum(r['n'] for r in records if r['view']=='full'))
(ROOT/'results/INDEPENDENT_RECOUNT.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))

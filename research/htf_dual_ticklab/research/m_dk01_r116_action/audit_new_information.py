"""Descriptive diagnostic of NEW ordered/role features, not inference inputs."""
from pathlib import Path
import json
import numpy as np

ROOT=Path(__file__).resolve().parent
def mi(x,y,k=8):
    tab=np.bincount(x*2+y,minlength=k*2).reshape(k,2).astype(float)
    p=tab/tab.sum();expected=p.sum(axis=1)[:,None]*p.sum(axis=0)[None,:]
    m=p>0
    return float(np.sum(p[m]*np.log2(p[m]/expected[m])))

names=json.loads((ROOT/'cache/01.json').read_text())['features']
indices=[i for i,n in enumerate(names) if n.startswith(('signature_','role_'))]
jan=np.load(ROOT/'cache/x_01.npy',mmap_mode='r')
edges={i:np.quantile(jan[:int(.6*len(jan)),i],np.arange(1,8)/8) for i in indices}
rows=[]
for month in ('01','02','06','07'):
    x=np.load(ROOT/'cache'/f'x_{month}.npy',mmap_mode='r')
    a=np.load(ROOT/'cache'/f'actions_{month}.npz')
    sl=slice(int(.6*len(x)),None) if month=='01' else slice(None)
    for i in indices:
        bins=np.searchsorted(edges[i],x[sl,i],side='left')
        rows.append(dict(month=month,feature=names[i],
            original_bad_mi_bits=mi(bins,(a['truth_class'][sl]!=0).astype(int)),
            fitted_teacher_veto_mi_bits=mi(bins,(a['kept'][sl]==0).astype(int)),
            action35_no_touch_mi_bits=mi(bins,(a['touch_250'][sl,2]<0).astype(int))))
out=dict(kind='DESCRIPTIVE_ONLY_NEW_FEATURES',edges_fit='JAN_FIRST60_FEATURES_ONLY',
    jan_evaluation='LAST40_HISTORICALLY_EXPOSED',rows=rows)
(ROOT/'results/NEW_INFORMATION_ATLAS.json').write_text(json.dumps(out,indent=2)+'\n')
rank=[]
for i in indices:
    rr=[r for r in rows if r['feature']==names[i]]
    rank.append(dict(feature=names[i],min_bad_mi=min(r['original_bad_mi_bits'] for r in rr),
        min_action_mi=min(r['action35_no_touch_mi_bits'] for r in rr)))
print(json.dumps(sorted(rank,key=lambda r:r['min_bad_mi'],reverse=True)[:8],indent=2))

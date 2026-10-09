import numpy as np, pandas as pd
from pathlib import Path
r=Path('/mnt/data/feb042');z=np.load(r/'FEB042_JAN039_PREPARED_PROPOSALS.npz')
fe=pd.read_csv('/mnt/data/feb041/FEB041_COMPLETED_10M_CONTEXT.csv');ends=fe.bucket_end_ms.to_numpy(dtype=np.int64)
import sys,os
os.environ['DAA_JAN039_RESEARCH_DIR']='/mnt/data/feb041';sys.path[:0]=['/mnt/data/feb041','/mnt/data/feb041/original/source']
import feb041_legacy_engine as m
TM=m.t[z['E']];prior_idx=np.searchsorted(ends,TM,side='right')-1;valid=prior_idx>=0
q=np.full(TM.size,np.nan);q[valid]=fe.range_usd.to_numpy()[prior_idx[valid]]
ss=z['S'];p=z['P'];imp=z['imp20'];phase=z['phase'];spi=z['spread'];ex=z['excluded']
labels=['<4','4-8','8-16','16-32','32-64','64+'];bounds=[-1e10,4,8,16,32,64,1e10]
for s in [17,18,19,21,22,23,24,25,26,27,28]:
 print('\nSOURCE',s)
 for label,lo,hi in zip(labels,bounds[:-1],bounds[1:]):
  sel=(ss==s)&(q>=lo)&(q<hi)&(~ex)&(spi<=3)&(np.sign(z['D'])*imp>=0)
  pp=p[sel]
  if len(pp):print(label,'n',len(pp),'pnl',round(pp.sum()),'avg',round(pp.mean(),2),'win',round(np.mean(pp>0),2))

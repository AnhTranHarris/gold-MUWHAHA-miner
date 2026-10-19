"""Post-hoc *diagnostic only* already-fitted source-causal specialist forecasts.
Not eligible to select an exposed June-July winner. Original signal universe retained.
"""
import sys
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from execute_r00_078 import data,forecast
NAMES=['micro','structure','impulse','exhaustion','reclaim','pullback','cooperative']
rows=[]
for b in ('coinexx','dukascopy'):
 for m in ('06','07'):
  a=data(b,m);p=forecast(b,a);y=a['y'];st=a['state'];mask=a['expert_mask']
  stages={'impulse':st[:,17]>=2,'exhaustion':st[:,21]>=2,'reclaim':((st[:,24:26]>=2)|(st[:,28:30]>=2)).any(axis=1),'pullback':(st[:,33]>=2)|(st[:,36]>=2)}
  for name in NAMES:
   pp=p[name];side=np.where(pp[:,2]>=pp[:,0],1,-1)
   for status,sel in [('ALL',np.ones(len(y),bool)),('EPISODE_ACTIVE',stages.get(name,np.ones(len(y),bool)))]:
    rows.append({'broker':b,'month':m,'oracle':name,'cohort':status,'events':int(sel.sum()),'correct':int(np.sum((side==y)&sel)),'accuracy':float(np.mean(side[sel]==y[sel])) if sel.any() else None,'nonneutral':int(np.sum((y!=0)&sel))})
d=pd.DataFrame(rows);d.to_csv(ROOT/'results'/'R00_078_SPECIALIST_ABLATION_SOURCE_NATIVE.csv',index=False)
print(d[d.cohort=='ALL'].groupby('oracle')[['events','correct']].sum().assign(accuracy=lambda x:x.correct/x.events).sort_values('accuracy',ascending=False).to_string())
print('\nSPECIALIST ACTIVE\n',d[(d.cohort=='EPISODE_ACTIVE') & d.oracle.isin(['impulse','exhaustion','reclaim','pullback'])].groupby('oracle')[['events','correct']].sum().assign(accuracy=lambda x:x.correct/x.events).to_string())

#!/usr/bin/env python3
"""Post-exposed RESEARCH ONLY cooperative ablation of already-frozen F09/11/12/13 masks.
Original R00-054 same event universe, original source labels; no tuning/promotion on JUN/JUL.
"""
import sys,json,csv,hashlib,itertools
from pathlib import Path
sys.path.insert(0,'/mnt/data')
import numpy as np, pandas as pd
import R00_054_FILTER12_TRANSFER_STUDENT as m
R=Path('/mnt/data');O=R/'R00_054_FILTER13_CAUSAL_REGIME_MEMORY'
policies={
 'F09':lambda a,b,c,d:a,
 'F11':lambda a,b,c,d:b,
 'F12':lambda a,b,c,d:c,
 'F13':lambda a,b,c,d:d,
 'F09_OR_F13':lambda a,b,c,d:a|d,
 'F09_AND_F13':lambda a,b,c,d:a&d,
 'F09_OR_F12F13':lambda a,b,c,d:a|(c&d),
 'F09_OR_F11F13':lambda a,b,c,d:a|(b&d),
 'F09_OR_F11F12F13':lambda a,b,c,d:a|(b&c&d),
 'F09_OR_F11_OR_F13':lambda a,b,c,d:a|b|d,
 'F09F11_OR_F13':lambda a,b,c,d:(a&b)|d,
 'F09F12_OR_F13':lambda a,b,c,d:(a&c)|d,
 'F09F11_OR_F09F13':lambda a,b,c,d:(a&b)|(a&d),
 'F09_OR_F11_OR_F12_OR_F13':lambda a,b,c,d:a|b|c|d,
 'AT_LEAST_2_OF_4':lambda a,b,c,d:(a.astype(int)+b+c+d)>=2,
 'AT_LEAST_3_OF_4':lambda a,b,c,d:(a.astype(int)+b+c+d)>=3,
 'ALL_4':lambda a,b,c,d:a&b&c&d,
 'F09_OR_2_OF_OTHERS':lambda a,b,c,d:a|((b.astype(int)+c+d)>=2),
 'F13_OR_2_OF_OTHERS':lambda a,b,c,d:d|((a.astype(int)+b+c)>=2),
 'F12_OR_F13':lambda a,b,c,d:c|d,
 'F11_OR_F13':lambda a,b,c,d:b|d,
 'F11_AND_F13':lambda a,b,c,d:b&d,
 'F12_AND_F13':lambda a,b,c,d:c&d,
 'F11_OR_F12_OR_F13':lambda a,b,c,d:b|c|d,
 'BASELINE':lambda a,b,c,d:np.ones(len(a),bool),
 }
rows=[]
for broker in ('coinexx','dukascopy'):
 for month in ('06','07'):
  z=[]
  for dr,fn in [ ('R00_054_FILTER09_MONTH_INDEPENDENT',f'FROZEN_DECISIONS_{broker}_{month}.npz'),
      ('R00_054_FILTER11_COMMON_TRANSFER',f'TRANSFER_MASK_{broker}_{month}.npz'),
      ('R00_054_FILTER12_CAUSAL_STUDENT',f'FROZEN_DECISIONS_{broker}_{month}.npz'),
      ('R00_054_FILTER13_CAUSAL_REGIME_MEMORY',f'TRANSFER_FROZEN_{broker}_{month}.npz')]:
   with np.load(R/dr/fn) as x:
    t=x['t'].copy();y=x['label'].copy() if 'label' in x.files else x['y'].copy();
    mk=x['keep'].astype(bool).copy() if 'keep' in x.files else x['mask'].astype(bool).copy()
    z.append((t,y,mk))
  assert all(np.array_equal(z[0][0],v[0]) and np.array_equal(z[0][1],v[1]) for v in z[1:])
  t,y=z[0][0],z[0][1]; a,b,c,d=[v[2] for v in z]
  for name,fn in policies.items():
   pred=fn(a,b,c,d);result=m.evaluate(broker,t,y,pred)
   rows.append({'broker':broker,'month':month,'policy':name,**result})
  print('F13_COOP_DONE',broker,month,'identical_events',len(y))
df=pd.DataFrame(rows);df.to_csv(O/'F09_F11_F12_F13_COOPERATIVE_EXPOSED_ALL.csv',index=False)
summary=df.groupby('policy',as_index=False).agg({'signals':'sum','correct':'sum','opposite':'sum','neutral':'sum','incorrect_rejected':'sum','new_r9_hour_misses':'sum','new_r9_day_misses':'sum'})
summary['accuracy']=summary.correct/summary.signals
summary.to_csv(O/'F09_F11_F12_F13_COOPERATIVE_EXPOSED_SUMMARY.csv',index=False)
for x in summary.query('new_r9_hour_misses==0 and new_r9_day_misses==0').sort_values('accuracy',ascending=False).head(10).itertuples():
 print('R9_FULL_COVERAGE',x.policy,'correct',x.correct,'signals',x.signals,'accuracy',round(x.accuracy,6),'bad_rej',x.incorrect_rejected)
print('COOP_COMPLETE',len(rows))

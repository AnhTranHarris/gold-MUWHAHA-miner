#!/usr/bin/env python3
"""Recompute FILTER10 common 0.50/0.50 consensus on cached eight original-event arrays.
ATTENTION: teacher fitted to evaluation month's own labels; diagnostic overfit only.
No R00-054 trade execution, no new entry timing. Original R9 hour reference preserved.
"""
import csv, gzip, json, math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
R=Path('/mnt/data')
ref={}
with gzip.open(R/'R00_054_VALIDATION/continuation_results/R00_054_CONTIGUOUS_UTC_HOURLY.csv.gz','rt',newline='') as f:
 for x in csv.DictReader(f):ref[x['broker'],int(x['hour_key'])]=int(x['r9_synth_completed_trades'])
months=['01','02','06','07']
rows=[]
for broker in ('coinexx','dukascopy'):
 for month in months:
  with np.load(ROOT/f'ALL_MONTH_TEACHER_SCORES_{broker}_{month}.npz',allow_pickle=False) as a:
   t=a['t']; y=a['truth_class']; p=a['teacher_score']; side=a['side']
   assert p.shape==(len(y),4) and len(t)==len(side)
   assert np.all(t[1:]>=t[:-1]);assert set(np.unique(side)).issubset({-1,1})
   own=p[:,months.index(month)];other=(p.sum(axis=1)-own)/3
   keep=(.5*own+.5*other)>=.45
   n=int(keep.sum());correct=int((keep&(y==0)).sum());h=t//3600000
   u,idx=np.unique(h,return_inverse=True);g=np.bincount(idx,weights=(keep&(y==0)).astype('int8'));og=np.bincount(idx,weights=(y==0).astype('int8'))
   lost=0;daily={}
   for i,hr in enumerate(u):
    r=ref.get((broker,int(hr)),0)
    if not r:continue
    need=math.ceil(.9*r);lost+=int(og[i]>=need and g[i]<need)
    day=int(hr//24);v=daily.setdefault(day,[0,0,0]);v[0]+=r;v[1]+=g[i];v[2]+=og[i]
   dlost=sum(int(v[2]>=math.ceil(.9*v[0]) and v[1]<math.ceil(.9*v[0])) for v in daily.values())
   rows.append(dict(broker=broker,month=month,signals=n,correct=correct,accuracy=correct/max(1,n),correct_retention=correct/max(1,int((y==0).sum())),additional_r9_hour_misses=lost,additional_r9_day_misses=dlost))
assert sum(r['correct'] for r in rows)==1163029
assert sum(r['signals'] for r in rows)==1384192
assert all(r['additional_r9_hour_misses']==0 and r['additional_r9_day_misses']==0 and r['accuracy']>=.70 for r in rows)
print(json.dumps({'warning':'SAME_MONTH LABEL_FITTED TRAINING; NOT FOR PREDICTIVE DEPLOYMENT','results':rows},indent=2))

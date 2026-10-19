#!/usr/bin/env python3
"""Read-only overfit 03 audit of original R9 UTC hour/day correct-signal supply.
Fits NOTHING, freezes NOTHING, no evaluation month called 'blind'.
"""
from pathlib import Path
import sys,json,math,csv
import numpy as np,pandas as pd
from joblib import load
ROOT=Path('/mnt/data');HERE=ROOT/'R00_054_OVERFIT03_DISCOVERY';sys.path.insert(0,str(ROOT))
from R00_054_FAILURE_OVERFIT03 import get,features

ref=pd.read_csv(ROOT/'R00_054_VALIDATION/continuation_results/R00_054_CONTIGUOUS_UTC_HOURLY.csv.gz',compression='gzip')
ref=ref[ref.eligible_reference].copy();ref['month']=pd.to_datetime(ref.hour_key*3_600_000,unit='ms',utc=True).dt.month
ref=ref[ref.month.isin([6,7])]
qset=[.2,.3,.4,.5,.6,.7,.8];rows=[];fail_rows=[];same_cross=[]
models={b:load(HERE/f'EXPOSED_OVERFIT03_{b}_MODEL.joblib') for b in ('coinexx','dukascopy')}
meta={b:json.loads((HERE/f'{b}_OVERFIT_TRAINING_AND_TEST.json').read_text()) for b in models}
for br in models:
 for mo in ('06','07'):
  d,r=get(br,mo);X,names=features(d,r); y=r['correct'].astype(bool)
  p=models[br].predict_proba(X)[:,1]
  cross=models['dukascopy' if br=='coinexx' else 'coinexx'].predict_proba(X)[:,1]
  from sklearn.metrics import roc_auc_score
  same_cross.append(dict(broker=br,month=mo,own_auc=float(roc_auc_score(y,p)),cross_broker_auc=float(roc_auc_score(y,cross)),n=len(y)))
  h=r['t']//3_600_000
  uh,inv=np.unique(h,return_inverse=True)
  template=ref[(ref.broker==br)&(ref.month==int(mo))].copy()
  # incoming source monthly ZIPs can contain UTC offsets just beyond calendar boundaries;
  # compare source-UTC month, not a fabricated additional event or fixed time offset
  for q in [0]+qset:
   th=0 if q==0 else meta[br]['train_prob_quantiles'][str(q)]
   keep=np.ones(len(y),bool) if q==0 else p>=th
   c=np.bincount(inv,weights=(keep&y).astype(int),minlength=len(uh));a=np.bincount(inv,weights=keep.astype(int),minlength=len(uh))
   tdf=pd.DataFrame(dict(hour_key=uh,filtered_correct=c.astype('int64'),filtered_signal=a.astype('int64')))
   m=template.merge(tdf,on='hour_key',how='left').fillna({'filtered_correct':0,'filtered_signal':0})
   floor=np.ceil(.9*m.r9_synth_completed_trades.values-1e-12)
   success=(m.filtered_correct.values>=floor)&(m.filtered_signal.values>=floor)
   day=pd.to_datetime(m.hour_key*3_600_000,unit='ms',utc=True).dt.strftime('%Y-%m-%d')
   dag=pd.DataFrame({'day':day,'r9':m.r9_synth_completed_trades.values,'correct':m.filtered_correct.values,'signaled':m.filtered_signal.values}).groupby('day',as_index=False).sum()
   day_req=np.ceil(.9*dag.r9.values-1e-12)
   daypass=(dag.correct.values>=day_req)&(dag.signaled.values>=day_req)
   rows.append(dict(broker=br,month=mo,q=q,original_events=len(y),original_correct=int(y.sum()),accepted_signals=int(keep.sum()),correct_kept=int((keep&y).sum()),wrong_removed=int((~keep&~y).sum()),correct_lost=int((~keep&y).sum()),correct_retained_pct=100*(keep&y).sum()/y.sum(),accuracy_pct=100*(keep&y).sum()/max(1,keep.sum()),r9_hours=int(len(success)),r9_pass_hours=int(success.sum()),r9_fail_hours=int((~success).sum()),r9_days=int(len(daypass)),r9_pass_days=int(daypass.sum()),r9_fail_days=int((~daypass).sum())))
   for j in np.where(~success)[0]:
    row=m.iloc[j]
    fail_rows.append(dict(broker=br,month=mo,q=q,utc_hour=pd.Timestamp(int(row.hour_key)*3_600_000,unit='ms',tz='UTC').isoformat(),r9=int(row.r9_synth_completed_trades),correct=int(row.filtered_correct),signaled=int(row.filtered_signal),required=int(floor[j])))
  del d,r,X,p,cross
pd.DataFrame(rows).to_csv(HERE/'R9_HOURLY_DAILY_SUPPLY_AUDIT.csv',index=False)
pd.DataFrame(fail_rows).to_csv(HERE/'R9_FAILURE_WINDOWS_ALL_OVERFIT_CUTOFFS.csv',index=False)
pd.DataFrame(same_cross).to_csv(HERE/'CROSS_BROKER_TRANSFER_AUC.csv',index=False)
print(pd.DataFrame(rows)[['broker','month','q','accuracy_pct','correct_retained_pct','r9_pass_hours','r9_hours','r9_pass_days','r9_days']].to_string(index=False))
print('CROSS',same_cross)

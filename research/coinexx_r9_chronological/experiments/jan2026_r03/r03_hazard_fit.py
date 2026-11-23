"""Discrete-time survival entry reconstruction (January deliberate in-sample). Only at-risk
seconds are negative controls. Historical R9 entry/exit seconds are used for retrospective
training risk-set boundaries, NEVER as runtime decision inputs.
"""
import json,time
from pathlib import Path
import numpy as np,pandas as pd,lightgbm as lgb
R=Path(__file__).parent
ref=pd.read_csv('/mnt/data/jan2026_forensic_metrics/2026-01_ALL_27980_TRADES_manifest.csv')
ref['minute_id']=ref.entry_sec//60
first=ref[ref.leg==1].copy();second=ref[ref.leg==2].copy()
fm=first.set_index('minute_id').entry_sec.to_dict();fe=first.set_index('minute_id').exit_sec.to_dict()
sm=second.set_index('minute_id').entry_sec.to_dict()
side1=dict(zip(first.entry_sec,np.where(first.side=='BUY',1,2)));side2=dict(zip(second.entry_sec,np.where(second.side=='BUY',1,2)))
FEATURE=['phase','minute','hour','spread_c','gap_ms','minute_disp','minute_range','minute_ticks','m1_disp','m5_disp','m15_disp','h1_disp','m5_atr','m15_atr','h1_atr','ret1','ret5','ret10','ret20','ret30','ret60','ret300','eff10','eff30','eff60','range10','range60','quotes10','quotes60','quote_imbalance10','m5_position','m15_position','h1_position']
SAMPLE=R/'r03_hazard_train_sample.csv.gz'

def prep():
 if SAMPLE.exists():SAMPLE.unlink()
 count=0;pos=[0,0]
 for i,df in enumerate(pd.read_csv(R/'r03_phase_seconds.csv.gz',chunksize=180000)):
  minute=(df.sec//60);j=df.sec.to_numpy('int64')
  a=minute.map(fm).to_numpy(float);first_exit=minute.map(fe).to_numpy(float);b=minute.map(sm).to_numpy(float)
  # Positive original minutes: at-risk only BEFORE or AT first label; never treat post-entry as negative.
  # Empty minutes: deterministic subsample (no original point exists in this minute).
  first_train=(df.phase<=33) & (np.isfinite(a)&(j<=a) | (~np.isfinite(a)&((minute.to_numpy()%5)==0)))
  second_train=(df.phase<=47) & (np.isfinite(first_exit)&(j>first_exit)&(np.isfinite(b)&(j<=b) | ~np.isfinite(b)))
  keep=first_train | second_train
  out=df.loc[keep, ['sec']+FEATURE].copy()
  out['first_in_risk']=first_train[keep].astype('int8')
  out['second_in_risk']=second_train[keep].astype('int8')
  out['y_first']=out.sec.map(side1).fillna(0).astype('int8')
  out['y_second']=out.sec.map(side2).fillna(0).astype('int8')
  # Observed source seconds without an original quote near the original target are UNKNOWN, not positives.
  out.to_csv(SAMPLE,compression={'method':'gzip','compresslevel':1},mode='wt' if i==0 else 'at',header=i==0,index=False)
  count+=len(out);pos[0]+=int((out.y_first>0).sum());pos[1]+=int((out.y_second>0).sum())
 print(json.dumps({'risk_set_rows':count,'first_labels':pos[0],'second_labels':pos[1],'size_MB':round(SAMPLE.stat().st_size/1e6,2)}),flush=True)

def fit():
 df=pd.read_csv(SAMPLE)
 logs={}
 for leg in (1,2):
  sub=df[df[f'{"first" if leg==1 else "second"}_in_risk']==1]
  y=sub[f'y_{"first" if leg==1 else "second"}'].to_numpy('int8');x=sub[FEATURE].to_numpy('float32')
  weights=np.where(y==0,.65,2.0).astype('float32')
  model=lgb.LGBMClassifier(objective='multiclass',num_class=3,n_estimators=300,learning_rate=.065,max_depth=7,num_leaves=31,min_child_samples=90,reg_lambda=12,verbosity=-1,n_jobs=4)
  model.fit(x,y,sample_weight=weights)
  model.booster_.save_model(str(R/f'r03_hazard_leg{leg}.txt'))
  p=model.predict_proba(x,num_threads=4)
  prob=p[:,1:3].max(axis=1);side=p[:,1:3].argmax(axis=1)+1
  tab=[]
  for thr in (.15,.25,.35,.45,.55,.65,.75,.85,.9):
   hit=(prob>thr);matches=(hit&(side==y)&(y>0))
   tab.append({'threshold':thr,'signals':int(hit.sum()),'true_matches':int(matches.sum()),'train_positives':int((y>0).sum()),'precision':float(matches.sum()/max(hit.sum(),1))})
  logs[f'leg{leg}']={'risk_seconds':len(sub),'positive_target_seconds':int((y>0).sum()),'thresholds':tab,'top_features':sorted(zip(FEATURE,[int(a) for a in model.feature_importances_]),key=lambda v:-v[1])[:14]}
  print('LEG',leg,tab,flush=True)
 (R/'r03_hazard_fit.json').write_text(json.dumps({'name':'discrete-time causal entry hazard','study_month':'Jan2026 in sample','future_quote_leakage':False,'feature_columns':FEATURE,'training_risk_set_source':'original R9 book (labels and risk set ONLY)','models':logs},indent=2))
if __name__=='__main__':
 import sys
 t=time.time()
 if sys.argv[1]=='prep':prep()
 else:fit()
 print('elapsed',round(time.time()-t,2),flush=True)

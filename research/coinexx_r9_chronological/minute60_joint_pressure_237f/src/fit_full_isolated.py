"""Fit ONE nine-month final model, marked IN-SAMPLE ONLY, no AUC certification."""
import argparse,sys,json,time
from pathlib import Path
import numpy as np,joblib
from lightgbm import LGBMClassifier
sys.path.insert(0,'/mnt/data/r9_m60_joint_20261113/src')
from train_joint import ROOT,CONFIG,read_month,sha
p=argparse.ArgumentParser();p.add_argument('--family',required=True,choices=['joint','r9_specialist']);a=p.parse_args()
xs=[];ys=[];counter=0;tot_censored=0
start=time.monotonic()
for i in range(1,10):
 r=read_month(f'{i:02d}');counter+=r['n_entries']
 if a.family=='joint':
  good=r['good']; x=r['X_joint'][good];y=r['y'][good];tot_censored+=int((~good).sum())
 else:
  idx=2*np.arange(r['n_entries'])+(r['r9_side']<0)
  good=r['good'][idx]; x=r['X_joint'][idx][good];y=r['y'][idx][good];tot_censored+=int((~good).sum())
 xs.append(x);ys.append(y)
 del r
print('ORIGINAL',counter,'observed_actions',sum(len(q) for q in xs),'elapsed',time.monotonic()-start,flush=True)
if counter!=303934:raise RuntimeError('Incomplete R9 universe')
X=np.vstack(xs);Y=np.concatenate(ys);del xs,ys
assert X.shape[1]==237
model=LGBMClassifier(**CONFIG);model.fit(X,Y)
out=ROOT/'models'/f'FULL_JanSep_{a.family}_IN_SAMPLE_ONLY.joblib'
joblib.dump({'model':model,'config':CONFIG,'trained_months':'Jan-Sep 2026',
             'feature_count':X.shape[1],'model_family':a.family,
             'status':'IN_SAMPLE_ONLY_NOT_PROSPECTIVE_OOS_NOT_FOR_TRADING'},out,compress=3)
rec={'status':'IN_SAMPLE_TRAINING_COMPLETED_NOT_OOS','family':a.family,
  'source':'FROZEN_9_MONTH_COINEXX_BID_ASK_QUOTES','original_decisions':counter,
  'training_actions':len(Y),'excluded_censored_actions':tot_censored,
  'positive_rate':float(Y.mean()),'feature_count':X.shape[1],
  'model_file':out.name,'model_sha256':sha(out),'elapsed_seconds':time.monotonic()-start,
  'no_deployment_or_test_auc':True}
(ROOT/'results'/f'FULL_{a.family}_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n')
importance=model.booster_.feature_importance(importance_type='gain')
base=importance[:182];cross=importance[182:]
feature_names=json.loads((ROOT/'results'/'interaction_names.json').read_text())
imp={'family':a.family,'gain_fraction_explicit_interactions':float(cross.sum()/importance.sum()),
     'top_cross_interactions':sorted([{'name':n,'gain':float(s)} for n,s in zip(feature_names,cross)],key=lambda a:-a['gain'])[:15],
     'diagnostic_only_no_oos_gain_claim':True}
(ROOT/'results'/f'FULL_{a.family}_IMPORTANCE.json').write_text(json.dumps(imp,indent=2)+'\n')
print('FULL_FIT_DONE',json.dumps(rec),flush=True)

"""Verify saved shadow hazards against immutable fold AUC receipts, zero training mutation."""
import json,hashlib
from pathlib import Path
import joblib
import numpy as np
from sklearn.metrics import roc_auc_score
from train import ROOT,monthly,select_features,cumulative_incidence

def verify():
 out=[]
 for mm in ('05','06','07','08','09'):
  receipt=json.loads((ROOT/'results'/f'fold_{mm}.json').read_text())
  d=monthly(mm)
  for family,z in receipt['models'].items():
   p=ROOT/'models'/z['model_file']
   if hashlib.sha256(p.read_bytes()).hexdigest()!=z['model_sha256']:raise RuntimeError('SHA mismatched')
   pipeline=joblib.load(p)
   xx=select_features(d['X'],family)
   preds=cumulative_incidence(pipeline['classifier'],xx)
   c=d['cause'];h=d['hit'];valid=c!=-1
   for horizon in (5000,15000):
    y=(c==1)&(h>=0)&(h<=horizon)
    auc=roc_auc_score(y[valid],preds[horizon]['p_fav'][valid])
    saved=z[str(horizon)]['auc_all_actions']
    if abs(auc-saved)>1e-10:raise RuntimeError(f'AUC mismatch {family} {mm} {horizon}: {auc} vs {saved}')
   out.append({'month':mm,'family':family,'sha256':z['model_sha256'],
               'auc5':z['5000']['auc_all_actions'],'auc15':z['15000']['auc_all_actions']})
 print('VERIFIED',len(out),'saved model classifiers, 40 AUC values (5s/15s), deterministic return parity')
 return out

if __name__=='__main__':verify()

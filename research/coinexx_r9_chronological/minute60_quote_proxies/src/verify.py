"""Read-back integrity and deterministic scoring replay of all R9 quote-proxy models."""
from __future__ import annotations
import json,hashlib,sys,zipfile
from pathlib import Path
import joblib,numpy as np
root=Path('/mnt/data/r9_m60_proxy_20261113');sys.path.insert(0,str(root/'src'))
from train_proxy import read_month,scoring,FAMILIES,sha


def run():
 files=[];n=0
 for mm in range(1,10):
  f=root/'derived'/f'proxy_2026_{mm:02d}.npz'
  with np.load(f,allow_pickle=False) as z:
   receipt=json.loads((root/'derived'/f'proxy_receipt_{mm:02d}.json').read_text())
   assert receipt['proxy_sha256']==sha(f),'feature cache hash mismatch'
   assert z['features'].shape[1]==27
   n+=len(z['features'])
  files.append({'month':f'{mm:02d}','entries':receipt['original_r9_decisions'],'proxy_sha256':receipt['proxy_sha256'],'source_sha256':receipt['source_sha256']})
 assert n==303934
 tests=[]
 for mm in range(5,10):
  month=f'{mm:02d}';r=read_month(month)
  rec=json.loads((root/'results'/f'fold_{month}.json').read_text())
  for family,indices in FAMILIES.items():
   artifact=root/'models'/f'{family}_test_{month}_shadow.joblib'
   expected=rec['families'][family]
   assert expected['model_sha256']==sha(artifact),'model hash mismatch'
   clf=joblib.load(artifact)['model']
   x=np.concatenate([r['base'],r['proxy'][:,indices]],axis=1)
   metrics=scoring(r,clf.predict_proba(x)[:,1])
   for key in ('pooled_auc5','original_direction_auc5','pooled_average_precision5','original_direction_average_precision5'):
    assert abs(metrics[key]-expected[key])<1.e-12,(month,family,key,metrics[key],expected[key])
   tests.append({'month':month,'family':family,'pooled_auc5':metrics['pooled_auc5'],'original_direction_auc5':metrics['original_direction_auc5'],'sha256':sha(artifact)})
 expected_total=9*1+20*4
 assert len(tests)==20
 all_fit=root/'models'/'all_182_features_JanSep_in_sample_only.joblib'
 if all_fit.exists():
  receipt=json.loads((root/'results'/'all_months_fit_receipt.json').read_text())
  assert receipt['model_sha256']==sha(all_fit)
 out={'status':'SHA_AND_SAVED_MODEL_REPLAY_PASS','original_r9_decisions':n,'monthly_source_and_cache_receipts':files,
      'model_replay_count':len(tests),'reproduced_auc_ap_metrics':20*4,
      'models':tests,'all_month_model_verified':all_fit.exists(),
      'note':'No MetaEditor compile, live fills, or untouched-forward-month certification'}
 (root/'results'/'VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n')
 print('VERIFIED',n,'entries',len(tests),'models',len(tests)*4,'metrics')
 return out
if __name__=='__main__':run()

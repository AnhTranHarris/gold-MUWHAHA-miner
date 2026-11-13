"""Rebuild and persist five FAILING frozen 117-feature 15-second HFT ranking models.
All are SHADOW_ONLY and known to fail 0.75 AUC. Never use for trade execution.
"""
import hashlib,json
from pathlib import Path
import joblib
import numpy as np
from sklearn.metrics import roc_auc_score
from train_full import load,build_model
root=Path('/mnt/data/r9_m60_expanded');data=root/'full_derived';dest=root/'shadow_models';dest.mkdir(exist_ok=True)
rows,cols=load(data);proof=json.load(open(root/'full_results/five_fold_results.json'))
receipts=[]
for i in range(4,9):
 X=np.concatenate([z['feature'][z['label'][:,1]!=-1,:117] for z in rows[:i]])
 y=np.concatenate([(z['label'][:,1][z['label'][:,1]!=-1]==1).astype(np.int8) for z in rows[:i]])
 t=rows[i];ok=t['label'][:,1]!=-1;Xt=t['feature'][ok,:117];yt=(t['label'][ok,1]==1).astype(np.int8)
 m=build_model('conservative');m.fit(X,y);pr=m.predict_proba(Xt)[:,1]
 auc=float(roc_auc_score(yt,pr));expected=proof['folds'][i-4]['family']['r9_hft60_117']['auc']
 if abs(auc-expected)>1e-12:raise RuntimeError(f'rebuilt model parity failure: {i}, {auc}, {expected}')
 p=dest/f'fold_{i-3}_train_Jan_to_{rows[i-1]["month"]}_eval_{t["month"]}_FAIL_SHADOW_ONLY.joblib'
 joblib.dump({'classifier':m,'columns':cols[:117],'source_history':'original frozen R9 base, 60s HFT real ticks',
   'train_months':[z['month'] for z in rows[:i]],'eval_month':t['month'],
   'evaluation_auc':auc,'owner_auc_fail_below':.75,'status':'FAILED_RESEARCH_ONLY'},p,compress=3)
 loaded=joblib.load(p);c=loaded['classifier'].predict_proba(Xt)[:,1]
 if not np.array_equal(pr,c):raise RuntimeError('serialized score mismatch')
 h=hashlib.sha256(p.read_bytes()).hexdigest()
 receipts.append({'model_file':p.name,'sha256':h,'auc':auc,'train_samples':len(y),'eval_samples':len(yt),'all_fail':auc<.75})
 print('SAVED',p.name,'bytes',p.stat().st_size,'auc',auc,flush=True)
 (dest/'model_integrity.json').write_text(json.dumps(receipts,indent=2)+'\n')

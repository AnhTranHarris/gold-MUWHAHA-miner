"""Paired UTC-day resampling, two already-exposed months; descriptive only."""
import json,sys
import numpy as np,joblib
from sklearn.metrics import roc_auc_score
sys.path.insert(0,'/mnt/data/r9_m60_training_20261113')
from run_train import ROOT,OUT,read_month,predict_hazard
result={}; rng=np.random.default_rng(20261113)
for mm in ['07','08']:
 r=read_month(mm)
 saved_old=joblib.load(ROOT/'source_priority/models'/f'all_three_test_{mm}_FAILED_UNTIL_CERTIFIED.joblib')['model']
 saved_new=joblib.load(OUT/'models'/f'direct_test_{mm}_shadow.joblib')['model']
 old=predict_hazard(saved_old,r['X'])[5000]['p_fav']
 new=saved_new.predict_proba(r['X'])[:,1]
 y=((r['kind']==1)&(r['hit']>=0)&(r['hit']<=5000));valid=r['kind']!=-1
 days=(r['time_ms']//86400000)[::2]
 unique,group=np.unique(days,return_inverse=True)
 groups=[np.where(group==i)[0] for i in range(len(unique))]
 boot=[]
 for k in range(160):
  choose=rng.choice(len(unique),size=len(unique),replace=True)
  ids=np.concatenate([groups[i] for i in choose])
  both=(2*ids[:,None]+np.array([0,1])).reshape(-1)
  g=valid[both];iy=y[both][g]
  if iy.min()==iy.max():continue
  auc_old=roc_auc_score(iy,old[both][g]);auc_new=roc_auc_score(iy,new[both][g])
  boot.append((auc_old,auc_new,auc_new-auc_old))
 boot=np.array(boot)
 result[mm]={
    'n_utc_days':len(unique),'bootstrap_replicates':len(boot),
    'direct_pooled_auc5_ci_95':np.quantile(boot[:,1],[.025,.975]).tolist(),
    'paired_direct_minus_prior_auc_ci_95':np.quantile(boot[:,2],[.025,.975]).tolist(),
    'not_pristine_oos':True, 'method':'paired UTC day block nonparametric resampling; correlated buy/sell held together'
 }
 print(mm,result[mm],flush=True)
(OUT/'july_august_day_bootstrap.json').write_text(json.dumps(result,indent=2)+'\n')

"""Fixed direct-model ablation: quantify added CUSUM/intensity/BM information.
Existing event-time trend + QRB/QAF retained in both; identical labels/splits.
"""
import sys,json,hashlib,argparse
from pathlib import Path
import numpy as np,joblib
from sklearn.metrics import roc_auc_score
from lightgbm import LGBMClassifier
sys.path.insert(0,'/mnt/data/r9_m60_training_20261113')
from run_train import read_month,direct_params,area_metrics,ROOT,OUT

parser=argparse.ArgumentParser()
parser.add_argument("--folds", nargs="*", type=int, default=list(range(4,9)))
folds=parser.parse_args().folds
assert all(i in range(4,9) for i in folds)
p_out=OUT/"feature_group_ablation.json"
results=json.loads(p_out.read_text()) if p_out.exists() else {}
for ix in folds:
 mm=f'{ix+1:02}'
 train=[read_month(f'{i:02}') for i in range(1,ix+1)]
 test=read_month(mm)
 X=np.concatenate([r['X'] for r in train])
 kind=np.concatenate([r['kind'] for r in train]);hit=np.concatenate([r['hit'] for r in train])
 good=kind!=-1;y=(kind==1)&(hit>=0)&(hit<=5000)
 # New feature order: original 116, new CUSUM+intensity 23, Brownian 11, metadata last 5
 assert X.shape[1]==155
 old=np.concatenate((X[:,:116],X[:,-5:]),axis=1)
 m=LGBMClassifier(**direct_params());m.fit(old[good],y[good].astype('i1'))
 pred=m.predict_proba(np.concatenate((test['X'][:,:116],test['X'][:,-5:]),axis=1))[:,1]
 res=area_metrics(test,pred)
 full=json.loads((OUT/f'fold_{mm}.json').read_text())['models']['direct_5sec']
 results[mm]={'prior_121_features':res,'all_155_features_auc5':full['pooled_auc5'],
              'all_155_features_R9_auc5':full['r9_direction_auc5'],
              'increment_all_three_pooled_auc5':full['pooled_auc5']-res['pooled_auc5'],
              'increment_all_three_R9_auc5':full['r9_direction_auc5']-res['r9_direction_auc5']}
 print(mm,'old121',round(res['pooled_auc5'],6),'all155',round(full['pooled_auc5'],6),'lift',round(results[mm]['increment_all_three_pooled_auc5'],6),flush=True)
 (OUT/'feature_group_ablation.json').write_text(json.dumps(results,indent=2)+'\n')

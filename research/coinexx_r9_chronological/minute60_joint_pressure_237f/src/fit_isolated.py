"""Run exactly ONE joint R9 LightGBM fit per process to avoid OpenMP stalls.
Explicit exit after saving model/metrics. Retrospective research only.
"""
import sys,argparse,time,json,hashlib
from pathlib import Path
sys.path.insert(0,'/mnt/data/r9_m60_joint_20261113/src')
import numpy as np,joblib
from lightgbm import LGBMClassifier
from train_joint import read_month,get_train,metrics,CONFIG,ROOT,sha

ap=argparse.ArgumentParser();ap.add_argument('--month',choices=['05','06','07','08','09'],required=True)
ap.add_argument('--family',choices=['capacity_182','synergy_joint','original_side_specialist'],required=True)
a=ap.parse_args()
ix=int(a.month);t0=time.monotonic()
tr=[read_month(f'{i:02d}') for i in range(1,ix)]
te=read_month(a.month)
if max(x['entry_ms'][-1] for x in tr)+60000>=te['entry_ms'][0]:raise RuntimeError('Month boundary/purge failed')
key='joint' if a.family!='capacity_182' else 'appended'
only_r9=a.family=='original_side_specialist'
x,y=get_train(tr,key,selected_side=only_r9)
name='X_joint' if key=='joint' else 'X182'
print('BEGIN',a.month,a.family,'training',x.shape,'heldout',te[name].shape,'rate',y.mean(),'sec',round(time.monotonic()-t0,1),flush=True)
model=LGBMClassifier(**CONFIG);model.fit(x,y)
p=model.predict_proba(te[name])[:,1]
m=metrics(te,p)
file=ROOT/'models'/f'{a.family}_eval_{a.month}.joblib'
joblib.dump({'model':model,'model_name':a.family,'config':CONFIG,'train_months':[x['month'] for x in tr],
             'evaluation_month':a.month,'status':'RESEARCH_EXPOSED_MONTH_NO_DEPLOYMENT'},file,compress=3)
np.save(ROOT/'results'/f'pred_{a.month}_{a.family}.npy',p.astype('f4'))
m.update({'family':a.family,'evaluated_month':a.month,'train_months':[x['month'] for x in tr],
          'train_actions':len(x),'n_features':x.shape[1],'model_sha256':sha(file),
          'elapsed_seconds':time.monotonic()-t0,'data':'FROZEN_COINEXX_ASOF_R9_ENTRY_UNIVERSE'})
(ROOT/'results'/f'score_{a.month}_{a.family}.json').write_text(json.dumps(m,indent=2)+'\n')
print('DONE',a.month,a.family,'pool',round(m['pooled_auc'],6),'R9',round(m['r9_direction_auc'],6),'seconds',round(time.monotonic()-t0,1),flush=True)

"""Read saved fixed evaluation models and build full apples-to-apples folds.
No hyperparameter fitting/selection at assembly time.
"""
import sys,json,zipfile,io
from pathlib import Path
import numpy as np,joblib
sys.path.insert(0,'/mnt/data/r9_m60_joint_20261113/src')
from train_joint import read_month,metrics,summarize,ROOT
prior=Path('/mnt/data/R9_M60_JanSep_FullTraining_155Features_20261113.zip')
for mm in ['05','06','07','08','09']:
 r=read_month(mm);fold={'evaluation_month':mm,'train_months':[f'{i:02d}' for i in range(1,int(mm))],
   'training_decisions':int(sum(read_month(f'{i:02d}')['n_entries'] for i in range(1,int(mm)))),
   'test_decisions':r['n_entries'],'training_full_universe':True,
   'prior_exposure':'DEVELOPMENT_DATA_EXPOSED_MULTIPLE_TIMES','models':{}}
 with zipfile.ZipFile(prior) as z:
  saved=joblib.load(io.BytesIO(z.read(f'models/direct_test_{mm}_shadow.joblib')))
 p155=saved['model'].predict_proba(r['base'])[:,1]
 fold['models']['frozen_155']=metrics(r,p155)
 previously=joblib.load(Path('/mnt/data/r9_m60_proxy_20261113/models')/f'all_quote_proxies_test_{mm}_shadow.joblib')
 p182=previously['model'].predict_proba(r['X182'])[:,1]
 fold['models']['frozen_182_append']=metrics(r,p182)
 for fam in ['capacity_182','synergy_joint','original_side_specialist']:
  m=json.loads((ROOT/'results'/f'score_{mm}_{fam}.json').read_text())
  fold['models'][fam]=m
 pjoint=np.load(ROOT/'results'/f'pred_{mm}_synergy_joint.npy').astype('f8')
 pspecialist=np.load(ROOT/'results'/f'pred_{mm}_original_side_specialist.npy').astype('f8')
 fold['models']['fixed_half_joint_specialist']=metrics(r,.5*pjoint+.5*pspecialist)
 fold['models']['fixed_half_frozen_synergy']=metrics(r,.5*p155+.5*pjoint)
 (ROOT/'results'/f'fold_{mm}.json').write_text(json.dumps(fold,indent=2)+'\n')
 print('RECONCILE',mm,'frozen155',round(fold['models']['frozen_155']['pooled_auc'],5),
       'joint',round(fold['models']['synergy_joint']['pooled_auc'],5),
       'R9 joint',round(fold['models']['synergy_joint']['r9_direction_auc'],5),flush=True)
print('FINISHED',flush=True)
summarize()

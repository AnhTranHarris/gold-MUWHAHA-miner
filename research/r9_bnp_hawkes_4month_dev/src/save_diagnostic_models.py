#!/usr/bin/env python3
"""Save only the exact frozen *rejected development diagnostic* LightGBM models.
Never write a live-valid policy. Requires a previously computed development_summary.
"""
import json,sys,hashlib
from pathlib import Path
import numpy as np
from lightgbm import LGBMClassifier,LGBMRegressor,Booster
sys.path.insert(0,str(Path(__file__).resolve().parent))
from nonlinear_student_paired import fetch,FEAT_NAMES

def main(result_dir):
 p=Path(result_dir);summary=json.loads((p/'nonlinear_summary.json').read_text())
 assert summary['passing']==0 and summary['chosen_development_candidate'] is None
 diagnostic=summary['best_combined_diagnostic'];assert diagnostic is not None
 rows,x,roles,y,t,pay=fetch(p);fit=roles=='fit'
 weight=np.where((y[fit]==1)&(t[fit]==1),1+diagnostic['teacher_weight'],1.).astype('float64')
 config={'num_leaves':diagnostic['leaves'],'n_estimators':100,'max_depth':-1,'learning_rate':.035,
         'min_child_samples':170,'colsample_bytree':.9,'subsample':.9,'subsample_freq':1,
         'reg_lambda':8.,'random_state':731,'n_jobs':2,'verbosity':-1}
 clf=LGBMClassifier(**config);reg=LGBMRegressor(**config)
 clf.fit(x[fit],y[fit],sample_weight=weight);reg.fit(x[fit],pay[fit],sample_weight=weight)
 a=p/'REJECTED_dev_survival_classifier.txt';b=p/'REJECTED_dev_net_regressor.txt'
 clf.booster_.save_model(str(a));reg.booster_.save_model(str(b))
 for path,m in [(a,clf),(b,reg)]:
  restored=Booster(model_file=str(path))
  target=m.booster_.predict(x[:25]);got=restored.predict(x[:25])
  assert np.max(np.abs(target-got))<1e-12
 metadata={'status':'REJECTED_FOR_DEPLOYMENT','four_month_development_only':True,
           'model_config':config,'feature_names':FEAT_NAMES,
           'input_at_inference':'12 causal features from observed tick and completed multiscale buckets; no synthetic teacher',
           'score_formula':'0.6 * regressor(net) + 0.4 * (classifier(survival) - 0.5)',
           'selected_diagnostic_not_passed':diagnostic,
           'file_sha256':{a.name:hashlib.sha256(a.read_bytes()).hexdigest(),b.name:hashlib.sha256(b.read_bytes()).hexdigest()}}
 (p/'REJECTED_model_metadata.json').write_text(json.dumps(metadata,indent=2))
 print(json.dumps({'files':[a.name,b.name,'REJECTED_model_metadata.json'],'sha':metadata['file_sha256'],'status':metadata['status']},indent=2))
if __name__=='__main__':main(sys.argv[1])

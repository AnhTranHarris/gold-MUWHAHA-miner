"""Restartable R120 market-regime specialist fit; one family-head per process."""
import argparse,json,zipfile,io
from pathlib import Path
import numpy as np
from lightgbm import LGBMClassifier
import joblib
from r150_stage1_regime_probe import build_cell
p=argparse.ArgumentParser();p.add_argument('--head',choices=['opposite','neutral'],required=True)
p.add_argument('--max-trees',type=int,default=85);p.add_argument('--out',type=Path,default=Path('/mnt/data/r150_repair_advanced/models'))
a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
orig=Path('/mnt/data/F395_S14_OWNER_APPROVED_RESEARCH_ONLY_FULL_AUGUST_TRANSFER_UNVERIFIED_20261025.zip')
atlas=Path('/mnt/data/XAUUSD_F401_R120_MULTICLOCK_HTF_SESSION_GRID_CAUSAL_RESEARCH_UNAPPROVED_20261028.zip')
stage=Path('/mnt/data/r150_lean_candidate/staged')
d=build_cell('01',stage,atlas,orig);x=d[2][:,:16];y=d[0]['truth'];valid=d[0]['valid'].copy();valid[:int(len(y)*.60)]=False
model=LGBMClassifier(objective='binary',n_estimators=a.max_trees,num_leaves=31,max_depth=7,min_child_samples=320,
                     learning_rate=.065,reg_lambda=16.,colsample_bytree=.9,random_state=150,verbosity=-1,n_jobs=2)
model.fit(x[valid],(y[valid]=={'opposite':1,'neutral':2}[a.head]).astype('int8'),categorical_feature=[15])
joblib.dump(model,a.out/f'r120_conditional_{a.head}.joblib',compress=3)
for m in ('01','02','06','07'):
    x=build_cell(m,stage,atlas,orig)[2][:,:16]
    np.save(a.out/f'r120_conditional_{m}_{a.head}.npy',model.predict_proba(x)[:,1].astype('float32'))
print(json.dumps({'head':a.head,'trees':a.max_trees,'january_fit_rows':int(valid.sum()),'saved':'model and 4 original-month scores'}))

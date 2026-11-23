"""Strictly offline original-R9 teacher-forward first passage. Source-observed seconds,
5-second source-clock horizon, +20c vs -30c from current executable mark.
No future labels or chosen teacher quote ordinals are ever runtime features.
"""
from pathlib import Path
import numpy as np,pandas as pd,lightgbm as lgb,json,time
from sklearn.metrics import roc_auc_score
from r05_train_episode import EXIT_F,export_forest
R=Path(__file__).parent;t0=time.time()
a=pd.read_csv(R/'r05_exit_teacher.csv.gz')
mark=a.mark_c.to_numpy('int64');sec=a.sec.to_numpy('int64');rid=a.ref_id.to_numpy('int64')
label=np.full(len(a),-1,np.int8)
for j in range(1,9):
 idx=np.arange(len(a)-j);valid=(rid[idx]==rid[idx+j])&(sec[idx+j]-sec[idx]<=5)&(label[idx]==-1)
 z=idx[valid];delta=mark[z+j]-mark[z]
 good=delta>=20;bad=delta<=-30
 label[z[good]]=1;label[z[bad]]=0
# For censored windows, avoid fabricating future events. Fit only event-observed comparisons.
a['passage_event']=label
sel=label>=0
X=a.loc[sel,EXIT_F].to_numpy('float32');y=label[sel]
model=lgb.LGBMClassifier(n_estimators=100,learning_rate=.065,num_leaves=19,max_depth=7,min_child_samples=210,reg_lambda=18,n_jobs=4,verbosity=-1)
model.fit(X,y)
model.booster_.save_model(str(R/'r05_competing_passage_lgb.txt'))
nt,nn=export_forest(model,R/'r05_competing_passage_forest.txt',EXIT_F)
p=model.predict_proba(X)[:,1]
receipt={'teacher_rows':len(a),'event_observed_risk_rows':int(sel.sum()),'up_first':int((y==1).sum()),'down_first':int((y==0).sum()),'censored':int((~sel).sum()),'window_seconds':5,'barriers_cents_from_current_net':{'up':20,'down':-30},'training_AUC_JAN_ONLY':round(float(roc_auc_score(y,p)),5),'forest':{'trees':nt,'nodes':nn},'leadtime_future_events_are_ONLY_labels':True,'runtime_teacher_time_forbidden':True,'elapsed_s':round(time.time()-t0,2),'top_importance':sorted(zip(EXIT_F,model.feature_importances_.tolist()),key=lambda k:-k[1])[:15]}
(R/'r05_competing_receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2),flush=True)

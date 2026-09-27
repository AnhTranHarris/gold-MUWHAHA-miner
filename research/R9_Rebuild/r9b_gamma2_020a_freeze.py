import json, joblib
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.tree import DecisionTreeClassifier
C=Path('/mnt/data/r9b020a_cache')
feat=['owner_tf','owner_align','owner_dist','owner_age','owner_bos_age','owner_depth','lower_confirm','lower_conflict','struct_align_count','struct_conflict_count']
def metrics(x):
 x=np.asarray(x,float); x=x[np.isfinite(x)]
 if not len(x): return {'trades':0,'winners':0,'win':0,'net':0,'gp':0,'gl':0,'pf':0}
 gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
 return {'trades':len(x),'winners':int((x>0).sum()),'win':float((x>0).mean()),'net':float(x.sum()),'gp':gp,'gl':gl,'pf':gp/(-gl) if gl<0 else 1e9}
d=pd.concat([pd.read_pickle(C/f'R9B_020A_M{m:02d}.pkl.gz',compression='gzip') for m in range(1,5)],ignore_index=True)
y=np.where(np.maximum(d.cont_pnl.values,d.fade_pnl.values)<=0,2,np.where(d.cont_pnl.values>=d.fade_pnl.values,1,0))
X=d[feat].replace([np.inf,-np.inf],np.nan).fillna(99.).to_numpy(float)
tr=d.month.values<=3; ap=d.month.values==4
model=DecisionTreeClassifier(max_depth=4,min_samples_leaf=800,class_weight={0:1.0,1:1.0,2:1.5},random_state=17).fit(X[tr],y[tr])
proba=model.predict_proba(X); cls=model.classes_; pred=cls[np.argmax(proba,axis=1)]; conf=np.max(proba,axis=1)
act0=pred!=2; p0=np.where(act0,np.where(pred==1,d.cont_pnl.values,d.fade_pnl.values),np.nan); ref=metrics(p0[ap])
cands=[]
for th in [0.35,0.40,0.45,0.50,0.55,0.60]:
 act=(pred!=2)&(conf>=th); p=np.where(act,np.where(pred==1,d.cont_pnl.values,d.fade_pnl.values),np.nan); ma=metrics(p[ap])
 trr=ma['trades']/max(1,ref['trades']); wr=ma['winners']/max(1,ref['winners']); elig=(trr>=.95 and wr>=.97)
 cands.append({'threshold':th,'eligible':elig,'trade_retention':trr,'winner_retention':wr,'metrics':ma})
elig=[x for x in cands if x['eligible']]
pick=max(elig,key=lambda x:(x['metrics']['gl'],x['metrics']['net'],x['winner_retention'])) if elig else max(cands,key=lambda x:(x['trade_retention']+x['winner_retention'],x['metrics']['gl'],x['metrics']['net']))
freeze={'unit':'R9B_GAMMA2_HIERARCHICAL_PATTERN_STATE_020_A_STRUCTURAL_OWNER','stage':'FREEZE','train':'Jan-Mar','calibration':'April','features':feat,'model':{'max_depth':4,'min_samples_leaf':800,'class_weight_abstain':1.5,'random_state':17},'selected_threshold':pick['threshold'],'april_reference':ref,'april_candidates':cands,'feature_importance':{f:float(v) for f,v in zip(feat,model.feature_importances_) if v>0},'classes':[int(x) for x in cls],'august_accessed':False}
joblib.dump(model,C/'R9B_020A_MODEL.joblib')
json.dump(freeze,open(C/'R9B_020A_FREEZE.json','w'),indent=2,sort_keys=True)
print(json.dumps(freeze,indent=2,sort_keys=True))

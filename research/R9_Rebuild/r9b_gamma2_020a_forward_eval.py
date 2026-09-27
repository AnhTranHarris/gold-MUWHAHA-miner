import json, joblib, hashlib
from pathlib import Path
import numpy as np, pandas as pd
C=Path('/mnt/data/r9b020a_cache')
freeze=json.load(open(C/'R9B_020A_FREEZE.json')); model=joblib.load(C/'R9B_020A_MODEL.joblib')
feat=freeze['features']; th=freeze['selected_threshold']
def metrics(x):
 x=np.asarray(x,float); x=x[np.isfinite(x)]
 if not len(x): return {'trades':0,'winners':0,'win':0.,'net':0.,'gp':0.,'gl':0.,'pf':0.}
 gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
 return {'trades':int(len(x)),'winners':int((x>0).sum()),'win':float((x>0).mean()),'net':float(x.sum()),'gp':gp,'gl':gl,'pf':float(gp/(-gl)) if gl<0 else 1e9}
def score(df):
 X=df[feat].replace([np.inf,-np.inf],np.nan).fillna(99.).to_numpy(float)
 pr=model.predict_proba(X); cls=model.classes_; pred=cls[np.argmax(pr,axis=1)]; conf=np.max(pr,axis=1)
 act=(pred!=2)&(conf>=th); pnl=np.where(pred==1,df.cont_pnl.values,df.fade_pnl.values)
 return np.where(act,pnl,np.nan),pred,conf
months={}; frames=[]
for m in range(1,8):
 d=pd.read_pickle(C/f'R9B_020A_M{m:02d}.pkl.gz',compression='gzip'); p,pred,conf=score(d)
 d['stageA_pnl']=p; d['pred']=pred; d['conf']=conf; frames.append(d)
 months[str(m)]=metrics(p)
all_df=pd.concat(frames,ignore_index=True)
res={'unit':'R9B_GAMMA2_HIERARCHICAL_PATTERN_STATE_020_A_STRUCTURAL_OWNER','status':'VERIFIED_LOCAL_DIAGNOSTIC_NOT_PROMOTED','frozen_threshold':th,'months':months,
     'jan_jul':metrics(all_df.stageA_pnl.values),'may_jun':metrics(all_df.loc[all_df.month.isin([5,6]),'stageA_pnl'].values),'may_jul':metrics(all_df.loc[all_df.month>=5,'stageA_pnl'].values),'july':metrics(all_df.loc[all_df.month==7,'stageA_pnl'].values),
     'reference_017':{'jan_jul':{'trades':137288,'winners':97533,'win':0.7104262572,'net':-12342.1705,'gl':-38839.2360,'pf':0.6822241689},'may_jul':{'trades':53336,'winners':36175,'win':0.6782473376,'net':-6921.7605,'gl':-14064.0060,'pf':0.5078386272},'july':{'trades':16188,'winners':10052,'win':0.6209537929,'net':-2412.1930,'gl':-4135.0190,'pf':0.4166428256}},
     'reference_019':{'jan_jul':{'trades':136450,'winners':96908,'win':0.7102088677,'net':-11758.6895,'gl':-38062.8620,'pf':0.6910718511},'july':{'trades':16042,'winners':9903,'win':0.6173170428,'net':-2563.0005,'gl':-4259.6180}},
     'feature_importance':freeze['feature_importance'],'august_accessed':False}
for key in ['jan_jul','may_jul','july']:
 if key in res['reference_017']:
  a=res[key]; b=res['reference_017'][key]
  res.setdefault('delta_vs_017',{})[key]={'net':a['net']-b['net'],'gl_improvement':a['gl']-b['gl'],'trades_delta':a['trades']-b['trades'],'winners_delta':a['winners']-b['winners'],'win_pp':100*(a['win']-b['win'])}
for key in ['jan_jul','july']:
 a=res[key]; b=res['reference_019'][key]
 res.setdefault('delta_vs_019',{})[key]={'net':a['net']-b['net'],'gl_improvement':a['gl']-b['gl'],'trades_delta':a['trades']-b['trades'],'winners_delta':a['winners']-b['winners'],'win_pp':100*(a['win']-b['win'])}
res['owner_coverage']={str(m):float((frames[m-1].owner_tf>=0).mean()) for m in range(1,8)}
res['teacher_neither']={str(m):float((np.maximum(frames[m-1].cont_pnl,frames[m-1].fade_pnl)<=0).mean()) for m in range(1,8)}
out=C/'R9B_020A_RESULT.json'; json.dump(res,open(out,'w'),indent=2,sort_keys=True)
print(json.dumps(res,indent=2,sort_keys=True))

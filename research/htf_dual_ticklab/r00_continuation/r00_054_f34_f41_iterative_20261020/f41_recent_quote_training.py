#!/usr/bin/env python3
"""F41 causal quote multi-month model, train historical Jan Feb early June, calibrate late June, July transfer.
Original 76+F39 source-native 30. Broker tapes independent; output all original event IDs and fails.
"""
import io,sys,json,time,zipfile
from pathlib import Path
import numpy as np
from lightgbm import LGBMClassifier
from joblib import dump
ROOT=Path('/mnt/data');P=ROOT/'R00_054_F41_JANFEBJUNE_REAL_QUOTE_TRANSFER_20261020';P.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT))
from f40_quote_specialists_train import load,src,fast

def scores(c,models):
 x=c['X'];d={name:model.predict_proba(x)[:,1] for name,model in models.items()}
 d['opposite_neutral_coop']=1.-np.maximum(d['opposite'],d['neutral'])
 d['average_correct']=.6*d['correct']+.4*(1.-d['opposite'])
 d['nonneutral_correct']=d['correct']*(1.-d['neutral'])
 return d

def measure(c,s,cut,refs):
 mask=s>=cut;v=fast(c,mask);q=src.quota_stats(c,mask,refs)
 return dict(**v,quota_failures={k:len(q[k]) for k in ('newly_failed_hours','newly_failed_days','newly_failed_weeks','newly_failed_months')})

def main():
 specs={'experiment':'F41','predeclared_before_july':'Jan80%,Feb90%,June60% chronological fit, 40s purge and 1/5 thinning, two independent source broker streams; late June 35% policy selection, July frozen transfer','original_source':'F39 independently SHA-pinned source-native last64 bid/ask quote features, exact original 5-second event IDs, 76 source feature+shadow; no later quote','features':106,'model_outputs':['correct','opposite','neutral'],'cooperatives':['opposite_neutral_coop','average_correct','nonneutral_correct'],'thresholds':'June last35% q0..0.65 step0.05, good retention>=71% individually and zero additional June source R9 quota fails','goal':'on July both independent brokers good retention >=71%; incorrect rejection >=90%; R9 quota zero','not_blind':'July historically exposed to project, although not trained or tuned this iteration','not_original_filter05':'new F39 30 features, missing original Filter05 15','future_MQL5':'F39 30 MQL5 source counterpart; models require ONNX or exact tree native conversion and compiled parity; no EA release'}
 (P/'F41_PREDECLARED_CONTRACT.json').write_text(json.dumps(specs,indent=2)+'\n')
 refs=src.r9_reference();xall=[];yall=[]
 for month,frac in [('01',.80),('02',.90),('06',.60)]:
  for b in src.BROKERS:
   c=load(b,month);stop=int(len(c['t'])*frac)
   ids=np.flatnonzero(c['t']<c['t'][stop]-40000)[::5]
   xall.append(c['X'][ids]);yall.append(c['y'][ids]);print('F41 FIT',b,month,len(ids),flush=True)
 X=np.concatenate(xall);y=np.concatenate(yall);del xall,yall
 print('F41 FIT DIM',X.shape,flush=True)
 params=dict(n_estimators=230,num_leaves=63,learning_rate=.046,min_child_samples=165,reg_lambda=12.,reg_alpha=.3,colsample_bytree=.83,n_jobs=3,verbosity=-1,random_state=54041)
 models={}
 for name,cl in [('correct',0),('opposite',1),('neutral',2)]:
  model=LGBMClassifier(**params);model.fit(X,y==cl)
  dump(model,P/f'F41_MODEL_{name}.joblib',compress=3);models[name]=model
  print('TRAINED',name,flush=True)
 del X,y
 junes={b:load(b,'06') for b in src.BROKERS}
 p={b:scores(c,models) for b,c in junes.items()};grid=[];freeze={}
 for name in p['coinexx']:
  ix={b:np.arange(len(c['t']))>=int(len(c['t'])*.65) for b,c in junes.items()}
  both=np.concatenate([p[b][name][ix[b]] for b in src.BROKERS]);valids=[]
  for q in np.arange(0,.651,.05):
   cut=float(np.quantile(both,q));rows=[];valid=True
   for b,c in junes.items():
    r=measure(c,p[b][name],cut,refs)
    m=p[b][name][ix[b]]>=cut;correct=c['y'][ix[b]]==0
    rc=float(m[correct].mean());rej=float((~m[~correct]).mean())
    rows.append(dict(broker=b,June_heldout_correct_retention=rc,June_heldout_incorrect_rejection=rej,June_full_quota_failures=r['quota_failures']))
    valid=bool(valid) and bool(rc>=.71 and not any(r['quota_failures'].values()))
   result=dict(name=name,quantile=round(float(q),3),threshold=cut,valid=bool(valid),rows=rows);grid.append(result)
   if valid:valids.append(result)
  freeze[name]=max(valids,key=lambda v:min(r['June_heldout_incorrect_rejection'] for r in v['rows'])) if valids else None
 (P/'F41_ALL_JUNE_FROZEN_GRID.json').write_text(json.dumps(grid,indent=2)+'\n')
 (P/'F41_JUNE_FROZEN_POLICY.json').write_text(json.dumps(freeze,indent=2)+'\n')
 del junes,p
 results=[]
 for b in src.BROKERS:
  c=load(b,'07');score=scores(c,models)
  np.savez_compressed(P/f'F41_JULY_SCORES_{b}.npz',t=c['t'],side=c['side'],truth=c['y'],**{name:prob.astype('float32') for name,prob in score.items()})
  for name,policy in freeze.items():
   if policy is None:continue
   r=measure(c,score[name],policy['threshold'],refs)
   result=dict(broker=b,method=name,July_original_event_count=len(c['t']),June_frozen_threshold=policy['threshold'],**r,success=bool(r['correct_retention']>=.71 and r['incorrect_rejection']>=.90 and not any(r['quota_failures'].values())))
   results.append(result);print('F41 JULY',b,name,round(r['correct_retention'],5),round(r['incorrect_rejection'],5),sum(r['quota_failures'].values()),flush=True)
  del c,score
 (P/'F41_ALL_JULY_TRANSFER_RESULTS.json').write_text(json.dumps(results,indent=2)+'\n')
 print('DONE F41; SUCCESS?',any(v['success'] for v in results),flush=True)
if __name__=='__main__':main()
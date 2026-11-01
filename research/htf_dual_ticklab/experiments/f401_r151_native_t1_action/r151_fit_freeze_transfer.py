"""R151 causal action-time Jan FIT / February CAL+policy FREEZE / June-July transfer.

Never retroactively veto an original t0 order. Original class is used ONLY as
offline FIT label for an independent correct-signal guardian and grading.
All inference features are source-native pre-T1 R120 market-only, no matured
outcome or teacher ancestry. Every T1 order is hypothetical never-submitted.
"""
from pathlib import Path
import hashlib,json,os,sys
import numpy as np
import joblib
from lightgbm import LGBMClassifier,LGBMRegressor
from sklearn.isotonic import IsotonicRegression
from r151_native_action import ROOT,FEATURE_NAMES,sha256

HEADS=['favorable','adverse','early_adverse','correct_guard','net_ev']
BROKERS=['dukascopy','coinexx']
MONTHS=['01','02','06','07']
SEED=151

def load(b,m):
 with np.load(ROOT/f'R151_{b}_{m}_T1_MARKET_ONLY_FEATURES.npz') as a:
  X=a['X'];valid=a['valid']
 with np.load(ROOT/f'R151_{b}_{m}_T1_ACTION_OUTCOMES.npz') as a:
  t=a['t0'];truth=a['truth'];side=a['side'];cls=a['action_class'];gross=a['gross_raw'];elapsed=a['elapsed_ms'];t1=a['t1']
 assert len(X)==len(t)==len(valid)
 assert np.all(np.isfinite(X))
 assert np.all(t1[valid]>=t[valid]+15000)
 assert np.all(t1[valid]<t[valid]+16000)
 return X,valid,t,truth,side,cls,gross,elapsed,t1

def features(X):
 # pre-T1 R120+HTF and prior quote only. No teacher, matured class or t0+30 label.
 return X

def targets(truth,cls,gross,elapsed):
 return {'favorable':(cls==1).astype('int8'),
         'adverse':(cls==-1).astype('int8'),
         'early_adverse':((cls==-1)&(elapsed<=5000)).astype('int8'),
         'correct_guard':(truth==0).astype('int8'),
         'net_ev':gross.astype('float32')/1000-.20}

def predict(model,X):
 return model.predict(X) if isinstance(model,LGBMRegressor) else model.predict_proba(X)[:,1]

def train_one(b):
 X,v,t,truth,side,cls,gross,elapsed,t1=load(b,'01')
 # Jan first80% FIT with 45s embargo to protect future T1+30s labels.
 cut=t[int(len(t)*.80)]-45000
 fit=np.flatnonzero(v&(t<cut)&(cls!=-9))
 assert len(fit)>100000
 Y=targets(truth,cls,gross,elapsed)
 models={};params={'n_estimators':145,'learning_rate':.05,'num_leaves':31,'max_depth':7,'min_child_samples':450,
                  'max_bin':127,'colsample_bytree':.86,'subsample':.85,'subsample_freq':1,
                  'random_state':SEED,'n_jobs':2,'verbosity':-1}
 for head in HEADS:
  model=(LGBMRegressor(**params) if head=='net_ev' else LGBMClassifier(**params))
  model.fit(features(X[fit]),Y[head][fit])
  path=ROOT/f'R151_{b}_{head}_JAN_FROZEN.joblib';joblib.dump(model,path,compress=3)
  models[head]=model
 del X,v,t,truth,side,cls,gross,elapsed,t1
 # February CAL first60% with 45s embargo; policy selection last35%.
 X,v,t,truth,side,cls,gross,elapsed,t1=load(b,'02')
 cal_end=t[int(len(t)*.60)]-45000
 sel_start=t[int(len(t)*.65)]+45000
 cal=np.flatnonzero(v&(t<cal_end)&(cls!=-9))
 sel=np.flatnonzero(v&(t>sel_start)&(cls!=-9))
 assert len(cal)>80000 and len(sel)>50000
 Y=targets(truth,cls,gross,elapsed)
 calibrators={}
 pred={}
 for h in HEADS:
  raw=predict(models[h],features(X))
  if h!='net_ev':
   cali=IsotonicRegression(out_of_bounds='clip',y_min=0,y_max=1)
   cali.fit(raw[cal],Y[h][cal]);pred[h]=cali.predict(raw).astype('float32')
   joblib.dump(cali,ROOT/f'R151_{b}_{h}_FEB_ISOTONIC.joblib',compress=3)
   calibrators[h]=cali
  else:
   bias=float(np.mean(Y[h][cal]-raw[cal]));pred[h]=(raw+bias).astype('float32')
   calibrators[h]=bias
  del raw
 # Three DISTINCT mechanisms: action EV, competing-risk hazard, guardian arbitration.
 score={
  'M1_expected_native_net':pred['net_ev'],
  'M2_competing_firstpassage':2*pred['favorable']-1.5*pred['adverse']-.8*pred['early_adverse']-.2,
  'M3_guarded_competing':2*pred['favorable']-1.5*pred['adverse']-.8*pred['early_adverse']-.2+0.45*(pred['correct_guard']-.5),
 }
 # Predeclared frozen policy selection: choose February last35% threshold from
 # 90/95/98% score quantiles, min 500 selected, maximize realized T1 net/intent.
 # This is a calibration selection, not JuneJuly retuning or full EA economics.
 policies={};feb_rows=[]
 for name,sc in score.items():
  candidates=[]
  for q in [.90,.95,.98]:
   thr=float(np.quantile(sc[sel],q))
   picked=sel[sc[sel]>=thr]
   net=Y['net_ev'][picked]
   n=len(picked)
   rec={'family':name,'quantile':q,'threshold':thr,'n':n,
        'mean_hypothetical_net_usd_per_intent':float(net.mean()),
        'favorable':int((cls[picked]==1).sum()),'adverse':int((cls[picked]==-1).sum()),
        'time_exit':int((cls[picked]==0).sum()),'original_correct_in_selected':int((truth[picked]==0).sum())}
   candidates.append(rec);feb_rows.append(rec)
  # If all negative, still freeze the least-negative family policy for diagnostic transfer;
  # no action recommendation or 'success' promotion follows.
  chosen=max(candidates,key=lambda r:(r['mean_hypothetical_net_usd_per_intent'],r['n']))
  policies[name]={'threshold':chosen['threshold'],'quantile':chosen['quantile'],'feb_selection':chosen}
 (ROOT/f'R151_{b}_FEB_FROZEN_POLICIES.json').write_text(json.dumps(policies,indent=2))
 (ROOT/f'R151_{b}_FEB_ALL_CANDIDATES.json').write_text(json.dumps(feb_rows,indent=2))
 del X,v,t,truth,side,cls,gross,elapsed,t1,pred,score
 return models,calibrators,policies

def evaluate(b,models,calibrators,policies,m):
 X,v,t,truth,side,cls,gross,elapsed,t1=load(b,m)
 pred={}
 for h in HEADS:
  raw=predict(models[h],features(X))
  pred[h]=(raw+calibrators[h] if h=='net_ev' else calibrators[h].predict(raw)).astype('float32')
  del raw
 score={
  'M1_expected_native_net':pred['net_ev'],
  'M2_competing_firstpassage':2*pred['favorable']-1.5*pred['adverse']-.8*pred['early_adverse']-.2,
  'M3_guarded_competing':2*pred['favorable']-1.5*pred['adverse']-.8*pred['early_adverse']-.2+0.45*(pred['correct_guard']-.5),
 }
 results={'broker':b,'month':m,'n_original':len(t),'n_original_right':int((truth==0).sum()),
          'n_original_opposite':int((truth==1).sum()),'n_original_neutral':int((truth==2).sum()),
          'n_T1_valid':int(v.sum()),'n_T1_action_resolved':int((v&(cls!=-9)).sum()),
          'n_T1_missing':int((~v).sum()),
          'baseline_hypothetical_net_per_resolved_intent':float((gross[v&(cls!=-9)]/1000-.2).mean()),
          'families':{},'historically_exposed':m in ('06','07'),'t0_veto_claim':False}
 saved={'t0':t,'side':side,'truth':truth,'t1':t1,'valid':v}
 for name,sc in score.items():
  cut=policies[name]['threshold'];picked=v&(cls!=-9)&(sc>=cut)
  n=int(picked.sum());net=(gross[picked]/1000-.2)
  results['families'][name]={'frozen_threshold':cut,'n_hypothetical_T1_actions':n,
    'mean_hypothetical_net_usd_per_intent':float(net.mean()) if n else None,
    'hypothetical_net_sum_usd_IF_ALL_INDEPENDENT':float(net.sum()),
    'favorable_first':int((picked&(cls==1)).sum()),
    'adverse_first':int((picked&(cls==-1)).sum()),
    'time_exit':int((picked&(cls==0)).sum()),
    'original_correct_in_selected':int((picked&(truth==0)).sum()),
    'original_opposite_in_selected':int((picked&(truth==1)).sum()),
    'original_neutral_in_selected':int((picked&(truth==2)).sum()),
    'never_submitted_hypothetical':True,'no_shared_capital_claim':True}
  saved['select_'+name]=picked
  saved['score_'+name]=sc.astype('float32')
 path=ROOT/f'R151_{b}_{m}_FROZEN_T1_POLICY_MASKS.npz'
 np.savez_compressed(path,**saved)
 results['mask_sha256']=sha256(path)
 (ROOT/f'R151_{b}_{m}_FROZEN_EVAL.json').write_text(json.dumps(results,indent=2))
 print(json.dumps({k:v for k,v in results.items() if k!='families'}),flush=True)
 for name,r in results['families'].items():print(name,r['n_hypothetical_T1_actions'],r['mean_hypothetical_net_usd_per_intent'],flush=True)
 return results

def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--broker',choices=BROKERS,required=True);args=p.parse_args()
 models,cal,pol=train_one(args.broker)
 all_results=[evaluate(args.broker,models,cal,pol,m) for m in MONTHS]
 (ROOT/f'R151_{args.broker}_FROZEN_ALL_MONTHS.json').write_text(json.dumps(all_results,indent=2))
if __name__=='__main__':main()
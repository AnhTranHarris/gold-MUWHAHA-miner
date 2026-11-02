"""R152 original-source hypothetical T1/T2/LIMIT full-information action router.

Three distinct policy families, frozen on February, June/July exposed transfer.
No original t0 filled-order veto; no teacher or original truth at inference.
Original truth only trains a separate guardian and grades historical classes.
"""
from pathlib import Path
import json,hashlib,gc
import numpy as np,joblib
from lightgbm import LGBMRegressor,LGBMClassifier
from sklearn.isotonic import IsotonicRegression
from r152_paired_action_replay import ROOT,CONFIG,sha

SEED=152
HEADS=('T1','T2','LIMIT','UPLIFT','LIMIT_FILL','CORRECT_GUARD')
PARAMS=dict(n_estimators=95,learning_rate=.045,num_leaves=31,max_depth=7,
            min_child_samples=500,max_bin=127,colsample_bytree=.85,
            reg_lambda=3.,random_state=SEED,n_jobs=2,verbosity=-1)
FAMILIES={'A_PAIRED_OPTIMAL_STOP':(0.,.1,.25),
          'B_PASSIVE_LIMIT_HAZARD':(0.,.1,.25),
          'C_INDEPENDENT_CORRECT_RESCUE':(.55,.65,.75)}

def load(month):
 with np.load(ROOT/f'R152_DK_{month}_FEATURES_AND_ACTIONS.npz') as a:
  d={k:a[k] for k in a.files}
 n=len(d['t0'])
 assert d['X'].shape==(n,128) and np.isfinite(d['X']).all()
 assert np.all(d['t1'][d['t1_valid']]>=d['t0'][d['t1_valid']]+15000)
 assert np.all(d['t1'][d['t1_valid']]<d['t0'][d['t1_valid']]+16000)
 assert np.all(d['t2'][d['t2_valid']]>=d['t1'][d['t2_valid']]+5000)
 assert np.all(d['t2'][d['t2_valid']]<d['t1'][d['t2_valid']]+6000)
 return d

def Y(d):
 return {'T1':d['U_T1'],'T2':d['U_T2'],'LIMIT':d['U_LIMIT'],
  'UPLIFT':d['U_T2']-d['U_T1'],
  'LIMIT_FILL':d['limit_filled'].astype(np.int8),
  'CORRECT_GUARD':(d['truth']==0).astype(np.int8)}

def infer(models,cal,d):
 pred={}
 for name in HEADS:
  raw=(models[name].predict_proba(d['X'])[:,1] if name in ('LIMIT_FILL','CORRECT_GUARD') else models[name].predict(d['X']))
  pred[name]=(cal[name].predict(raw) if name in ('LIMIT_FILL','CORRECT_GUARD') else raw+cal[name]).astype(np.float32)
 return pred

def actions(pred,family,thr):
 n=len(pred['T1']);a=np.zeros(n,dtype=np.int8)
 p1,p2,pl=pred['T1'],pred['T2'],pred['LIMIT']
 if family=='A_PAIRED_OPTIMAL_STOP':
  # Paired-action causal uplift; T2 is a NEW unsubmitted order, not t0 delay veto.
  wait=(pred['UPLIFT']>thr)&(p2>0.)
  now=(~wait)&(p1>thr)
  a[wait]=2;a[now]=1
 elif family=='B_PASSIVE_LIMIT_HAZARD':
  # Distinct action/fill mechanism: no touch -> no fill, no artificial profit.
  choose=(pred['LIMIT_FILL']>.05)&(pl>np.maximum(np.maximum(p1,p2),0)+thr)
  a[choose]=3
 elif family=='C_INDEPENDENT_CORRECT_RESCUE':
  # Correct guardian uses only pre-T1 source state, never original label at inference.
  arr=np.column_stack((p1,p2,pl))
  choice=np.argmax(arr,axis=1)+1
  best=np.max(arr,axis=1)
  normal=best>0.10
  # Independently rescue an original-correct opportunity candidate even if
  # the expected-net head is cautious; no original t0 order is cancelled.
  rescue=(pred['CORRECT_GUARD']>=thr)&(best>-.1)
  a[normal|rescue]=choice[normal|rescue]
 else:raise ValueError(family)
 return a

def evaluate(d,pred,policies,month):
 truth=d['truth'];n=len(truth)
 util=np.column_stack((np.zeros(n,dtype=np.float32),d['U_T1'],d['U_T2'],d['U_LIMIT']))
 output={'month':month,'broker':'dukascopy','n_original':n,
         'original_classes':{str(c):int((truth==c).sum()) for c in (0,1,2)},
         'baseline_T1_net_per_original_intent':float(d['U_T1'].mean()),
         'baseline_T2_net_per_original_intent':float(d['U_T2'].mean()),
         'baseline_LIMIT_net_per_original_intent':float(d['U_LIMIT'].mean()),
         'families':{},'no_original_t0_veto':True,'L1_optimistic_only':True}
 masks={'t0':d['t0'],'side':d['side'],'truth':truth,'t1':d['t1'],'t2':d['t2']}
 for family,info in policies.items():
  a=actions(pred,family,info['threshold'])
  realized=util[np.arange(n),a]
  picked=a!=0
  result={'frozen_threshold':info['threshold'],'n_new_hypothetical_actions':int(picked.sum()),
   'action_counts':{str(k):int((a==k).sum()) for k in range(4)},
   'hypothetical_net_per_original_intent_USD':float(realized.mean()),
   'hypothetical_net_sum_USD_if_independent':float(realized.sum()),
   'mean_USD_per_action':float(realized[picked].mean()) if picked.any() else None,
   'original_correct_proposed':int((picked&(truth==0)).sum()),
   'original_opposite_proposed':int((picked&(truth==1)).sum()),
   'original_neutral_proposed':int((picked&(truth==2)).sum()),
   'original_correct_proposal_rate':float((picked&(truth==0)).sum()/max(1,(truth==0).sum())),
   'original_incorrect_nonproposal_rate':float((~picked&(truth!=0)).sum()/max(1,(truth!=0).sum())),
   'no_t0_veto_claim':True}
  output['families'][family]=result
  masks['action_'+family]=a
  masks['score_'+family]=np.asarray(pred['UPLIFT'] if family.startswith('A') else pred['LIMIT'] if family.startswith('B') else pred['CORRECT_GUARD'],dtype=np.float32)
 fn=ROOT/f'R152_DK_{month}_FROZEN_POLICY_ACTION_MASKS.npz';np.savez_compressed(fn,**masks)
 output['policy_mask_sha256']=sha(fn)
 (ROOT/f'R152_DK_{month}_FROZEN_POLICY_EVAL.json').write_text(json.dumps(output,indent=2))
 print('EVAL',month,json.dumps({k:v for k,v in output.items() if k!='families'}),flush=True)
 for f,v in output['families'].items():print('FAMILY',month,f,v['n_new_hypothetical_actions'],v['hypothetical_net_per_original_intent_USD'],flush=True)
 return output

def main():
 d=load('01');t=d['t0'];n=len(t)
 fit=t<t[int(n*.8)]-70000
 assert fit.sum()>100000
 y=Y(d);models={}
 for name in HEADS:
  dest=ROOT/f'R152_{name}_JAN_FROZEN.joblib'
  if dest.exists():
   models[name]=joblib.load(dest);print('TRAIN_REUSED_VERIFIED_LOCAL',name,flush=True);continue
  fast=dict(PARAMS,n_estimators=55,num_leaves=23,max_depth=6,max_bin=63,n_jobs=4)
  model=(LGBMClassifier(**fast) if name in ('LIMIT_FILL','CORRECT_GUARD') else LGBMRegressor(**fast))
  idx=np.flatnonzero(fit)[::2] # precommitted resource cap: Jan first80, deterministic half-stride
  model.fit(d['X'][idx],y[name][idx]);models[name]=model
  joblib.dump(model,dest,compress=3)
  print('TRAIN',name,int(len(idx)),flush=True)
 del d,t,y;gc.collect()
 d=load('02');t=d['t0'];n=len(t)
 cal_mask=t<t[int(n*.6)]-70000
 sel_mask=t>t[int(n*.65)]+70000
 assert cal_mask.sum()>100000 and sel_mask.sum()>80000
 yy=Y(d);cal={}
 for name in HEADS:
  raw=(models[name].predict_proba(d['X'])[:,1] if name in ('LIMIT_FILL','CORRECT_GUARD') else models[name].predict(d['X']))
  if name in ('LIMIT_FILL','CORRECT_GUARD'):
   iso=IsotonicRegression(out_of_bounds='clip',y_min=0,y_max=1)
   iso.fit(raw[cal_mask],yy[name][cal_mask]);cal[name]=iso
  else:
   cal[name]=float(np.mean(yy[name][cal_mask]-raw[cal_mask]))
  joblib.dump(cal[name],ROOT/f'R152_{name}_FEB_CAL_FROZEN.joblib',compress=3)
 pred=infer(models,cal,d)
 policies={};feb_candidates=[]
 util=np.column_stack((np.zeros(n,dtype=np.float32),d['U_T1'],d['U_T2'],d['U_LIMIT']))
 for family,thresholds in FAMILIES.items():
  rows=[]
  for thr in thresholds:
   a=actions(pred,family,thr);v=util[np.arange(n),a]
   sel=v[sel_mask];ns=int((a[sel_mask]!=0).sum())
   row={'family':family,'threshold':thr,'n_selected':ns,
        'Feb_last35_net_per_original_intent_USD':float(sel.mean()),
        'Feb_last35_net_sum_USD_if_independent':float(sel.sum())}
   rows.append(row);feb_candidates.append(row)
  # The 0-action abstain baseline is an explicit permitted candidate.
  best=max(rows,key=lambda x:(x['Feb_last35_net_per_original_intent_USD'],x['n_selected']))
  policies[family]={'threshold':best['threshold'],'February_selection':best}
 (ROOT/'R152_FEB_PRETRANSFER_ALL_CANDIDATES.json').write_text(json.dumps(feb_candidates,indent=2))
 (ROOT/'R152_FEB_FROZEN_POLICIES.json').write_text(json.dumps(policies,indent=2))
 print('FROZEN',json.dumps(policies),flush=True)
 results=[evaluate(d,pred,policies,'02')]
 del d,pred,t,yy,util;gc.collect()
 for month in ['01','06','07']:
  d=load(month);pred=infer(models,cal,d)
  results.append(evaluate(d,pred,policies,month))
  del d,pred;gc.collect()
 (ROOT/'R152_FROZEN_FOUR_MONTH_RESULTS.json').write_text(json.dumps(results,indent=2))
 print('R152_FOUR_MONTH_FROZEN_TRANSFER_COMPLETE',flush=True)

if __name__=='__main__':main()
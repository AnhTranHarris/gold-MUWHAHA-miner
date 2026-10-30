"""R150F-2 T0/T1 investigation: physically timed VOI, never act on teacher.
Jan/Feb fit, June predeclared quantile calibration, July exact frozen replay.
T1 gets privileged historical same-month teacher score in research only.
T0 runtime receives solely as-of-quote causal 24D source prefix.
"""
from __future__ import annotations
import os,io,zipfile,sys,json,pathlib,hashlib
os.environ['OMP_NUM_THREADS']='2';os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np, lightgbm as lgb
from sklearn.metrics import roc_auc_score,mean_squared_error
P=pathlib.Path('/mnt/data');R=P/'R150F2';Z=P/'R00_054_FILTER08_FOUR_MONTH_70PCT_OVERFIT_RESEARCH_20261019.zip'
CANDIDATES=(.75,.9,.95,.975,.99)

def cell(b,m):
 with np.load(R/'data'/f'R150F2_{b}_{m}_NATIVE_VOI.npz') as z:
  d={k:z[k] for k in z.files}
 with zipfile.ZipFile(Z) as z:
  with np.load(io.BytesIO(z.read(f'FILTER08/FITTED_CLASSIFIER_SCORES_{b}_{m}.npz'))) as teacher:
   # teacher is NEVER a T0 feature, a physical target, or action policy input
   assert np.array_equal(teacher['t'][d['source_ordinal']],d['t0'])
   d['teacher_hindsight']=teacher['score'][d['source_ordinal']].astype(np.float32)
 return d

def data(d,with_teacher=False):
 x=d['features'][:,0,:]; p=d['l1_mark_to_market_net_proxy'];label=d['physical_label'];truth=d['original_truth_for_audit_only']
 v=(label[:,0]>=0)&(label[:,2]>=0)&np.isfinite(p[:,0])&np.isfinite(p[:,2])
 if with_teacher:x=np.column_stack([x,d['teacher_hindsight']]);
 y=np.clip(p[:,2]-p[:,0],-4.,4.).astype(np.float32)
 return x[v],y[v],v

def model(b,t1):
 x=[];y=[]
 for m in ('01','02'):
  d=cell(b,m);a,z,v=data(d,t1);x.append(a);y.append(z)
 a=np.concatenate(x);z=np.concatenate(y)
 ds=lgb.Dataset(a,label=z)
 params=dict(objective='regression_l1',metric='l1',verbosity=-1,num_leaves=15,min_data_in_leaf=180,learning_rate=.035,
   lambda_l2=20.,feature_fraction=.85,seed=(15072 if t1 else 15071),num_threads=2,deterministic=True,force_col_wise=True,max_bin=63)
 m=lgb.train(params,ds,num_boost_round=140)
 # training checkpoint is written by the caller; no runtime teacher dependency
 return m,None

def score(b,m,md,t1):
 d=cell(b,m);x,y,v=data(d,t1)
 pred=md.predict(x,num_threads=2)
 orig=d['original_truth_for_audit_only'][v]
 out=dict(y=y,pred=pred,original_truth=orig,original_teacherscore=d['teacher_hindsight'][v],
  pnl0=d['l1_mark_to_market_net_proxy'][v,0],pnl250=d['l1_mark_to_market_net_proxy'][v,2])
 return out

def front(q,cut):
 pick=q['pred']>=cut
 p0=q['pnl0'];p1=q['pnl250'];delta=q['y']
 ix=np.flatnonzero(pick)
 return dict(selected=int(len(ix)),observations=int(len(pick)),mean_wait_minus_now=float(np.mean(delta[ix])) if len(ix) else None,
   chosen_immediate_proxy_mean=float(np.mean(p0[ix])) if len(ix) else None,
   chosen_wait_proxy_mean=float(np.mean(p1[ix])) if len(ix) else None,
   original_correct_count=int(np.count_nonzero(q['original_truth'][ix]==0)),
   effective_wait_coverage=int(len(ix)))

def study(b):
 candidate={}
 for name,t1 in [('T0',False),('T1',True)]:
  md,_=model(b,t1);mod=R/'models'/f'R150F2_{b}_{name}_VOI.txt';md.save_model(str(mod))
  june=score(b,'06',md,t1);july=score(b,'07',md,t1)
  cuts=np.unique(np.quantile(june['pred'],CANDIDATES))
  grid=[dict(cut=float(c),**front(june,c)) for c in cuts]
  # fixed June criterion: >=100 chosen and optimistic mark-to-market delta >=$0.05.
  viable=[x for x in grid if x['selected']>=100 and x['mean_wait_minus_now'] is not None and x['mean_wait_minus_now']>=.05]
  best=max(viable,key=lambda x:(x['selected'],x['mean_wait_minus_now'])) if viable else None
  frozen=float(best['cut']) if best else float('inf')
  evaluation=front(july,frozen)
  # unconstrained diagnostics are explicitly labeled NOT a selection rule.
  y=july['y'];pred=july['pred']
  teacher=july['original_teacherscore'];positive=(july['original_truth']==0)
  corr=float(np.corrcoef(teacher,y)[0,1]) if np.std(y)>1e-9 else None
  candidate[name]=dict(model_sha256=hashlib.sha256(mod.read_bytes()).hexdigest(),model_features=25 if t1 else 24,
    june_gate=best,june_grid=grid,july_frozen=evaluation,
    july_model_mae=float(np.mean(np.abs(y-pred))),july_teacher_score_vs_physical_wait_delta_pearson=corr,
    july_original_correct_count=int(positive.sum()),july_judgment='T1 privileged cannot be promoted' if t1 else 'T0 causal only, research gate')
  if name=='T0':
   np.savez_compressed(R/'results'/f'R150F2_{b}_JULY_FROZEN_SCORES.npz',pred=pred,observed_delta=y,original_truth_diagnostic_only=july['original_truth'],
     teacher_score_offline_only=teacher, selected_wait=np.isfinite(frozen)&(pred>=frozen),pnl_now=july['pnl0'],pnl_after_wait250=july['pnl250'],override_active=np.array([False]))
 report=dict(broker=b,cells=['01','02','06','07'],decision='R148B frozen; R150F2 no overrides',
  sample_design='8,000 uniformly random existing R148B vetoed native decision-eligible original events per month; conditional sample, NOT all events',
  physical_proxy='Marketable bid/ask at quote, 3.00 USD first-passage barrier each side, 30s horizon, 0.20 USD cost, 1 oz per 0.01 lot unit proxy, no actual fill',
  label_contract='new t0+15 source quote and later timed source quote; original t0+30..32 truth separate audit only',
  models=candidate)
 path=R/'results'/f'R150F2_{b}_VOI_TEACHER_FADE.json';path.write_text(json.dumps(report,indent=2,allow_nan=False));print(json.dumps({b:{x:{'june_selected':v['june_gate'],'july':v['july_frozen'],'july_mae':v['july_model_mae']} for x,v in candidate.items()}}),flush=True)
 return report

if __name__=='__main__':study(sys.argv[1])

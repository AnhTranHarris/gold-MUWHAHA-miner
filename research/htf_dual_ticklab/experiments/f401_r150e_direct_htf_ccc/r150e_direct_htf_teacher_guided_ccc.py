"""F401-R150E direct HTF cross-scale CCC experiment, UNAPPROVED.

Hypothesis: the strictly completed direct 36D HTF/interaction state improves
T0 teacher-free original-correct rescue among frozen R148B vetoes. The T1
hindsight teacher learns the residual as OFFLINE forensic grader; teacher never
appears in T0 predictors, cutoff choice, nor runtime. Jan+Feb FIT, June CAL,
July TEST per broker, no retune. Frozen R148B action unchanged.
"""
from __future__ import annotations
import os,sys,json,time,zipfile,io,pathlib,gc
os.environ['OMP_NUM_THREADS']='2';os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np, lightgbm as lgb
from sklearn.metrics import roc_auc_score, mean_absolute_error
ROOT=pathlib.Path('/mnt/data');OUT=ROOT/'R150E'
for x in ('models','masks','results'):(OUT/x).mkdir(parents=True,exist_ok=True)
ORACLE=ROOT/'R00_054_FILTER08_FOUR_MONTH_70PCT_OVERFIT_RESEARCH_20261019.zip'

def read(b,m):
 key=f'{b}_{m}'
 with np.load(ROOT/'R150C'/'features'/f'R150C_{key}_WORLD_STATE.npz') as s, \
      np.load(ROOT/'R150D'/'path'/f'R150D_{key}_R147_STRICT_PATH.npz') as p, \
      np.load(ROOT/'R150E'/'features'/f'R150E_{key}_R147_DIRECT_HTF_INTER36.npz') as h:
  assert np.array_equal(s['t'],p['t']) and np.array_equal(s['t'],h['t'])
  assert np.array_equal(s['side'],p['side']) and np.array_equal(s['side'],h['side'])
  assert np.array_equal(s['decision'],h['decision'])
  v=s['valid']&p['available']&h['valid']
  X=np.concatenate((s['X_source'],p['X'],h['X']),axis=1).astype(np.float32)
  parent=s['X_parent'].astype(np.float32)
  X=np.nan_to_num(X,nan=0.,posinf=0.,neginf=0.)
  assert X.shape==(len(v),397) and parent.shape==(len(v),6)
  return dict(X=X,par=parent,valid=v,truth=s['truth'],veto=s['r148_veto'],t=s['t'],side=s['side'],decision=s['decision'])

def sample(d,month,broker,maxn=41000):
 ix=np.flatnonzero(d['valid']&d['veto']);rng=np.random.default_rng(150000+int(month)+(0 if broker=='coinexx' else 100))
 if len(ix)>maxn:ix=np.sort(rng.choice(ix,size=maxn,replace=False))
 return ix

def fit(X,Y,seed,rounds=170):
 dataset=lgb.Dataset(X,label=Y,free_raw_data=True)
 return lgb.train(dict(objective='binary',verbosity=-1,learning_rate=.045,num_leaves=21,
   min_data_in_leaf=130,lambda_l2=12.,feature_fraction=.8,bagging_fraction=.8,
   bagging_freq=1,max_bin=95,seed=seed,num_threads=2),dataset,num_boost_round=rounds)

def oracle(z,d,b,m):
 path=f'FILTER08/FITTED_CLASSIFIER_SCORES_{b}_{m}.npz'
 with np.load(io.BytesIO(z.read(path))) as o:
  assert np.array_equal(o['t'],d['t']) and np.array_equal(o['original_side'],d['side']) and np.array_equal(o['truth_class'],d['truth'])
  return o['score'].astype(np.float32)

def score(models,d,only_valid_veto=True):
 eligible=d['valid']&d['veto'] if only_valid_veto else d['valid']
 ix=np.flatnonzero(eligible);out=np.zeros(len(d['truth']),np.float32)
 for k in range(0,len(ix),32000):
  q=ix[k:k+32000]
  X=np.column_stack([d['X'][q],d['par'][q]])
  out[q]=np.mean([m.predict(X,num_threads=2).astype(np.float32) for m in models],axis=0)
 return out

def recount(d,sc,cut):
 rescu=d['valid']&d['veto']&(sc>=cut) if cut<=1 else np.zeros(len(sc),bool)
 corr=int(np.count_nonzero(rescu&(d['truth']==0)));bad=int(np.count_nonzero(rescu&(d['truth']!=0)))
 parent=d['veto'];bad0=int(np.count_nonzero(parent&(d['truth']!=0)));correct0=int(np.count_nonzero(parent&(d['truth']==0)))
 return dict(parent_bad=bad0,parent_correct_lost=correct0,rescued_correct=corr,bad_readmitted=bad,
   hypothetical_bad_remaining=bad0-bad,hypothetical_correct_lost=correct0-corr,
   correct_rescue_precision=(corr/(corr+bad) if corr+bad else None)),rescu

def execute(b):
 t0=time.time();pieces=[]
 with zipfile.ZipFile(ORACLE) as z:
  for m in ('01','02'):
   d=read(b,m);ix=sample(d,m,b);pieces.append((d,ix,m,oracle(z,d,b,m)))
  X=np.concatenate([np.column_stack([d['X'][ix],d['par'][ix]]) for d,ix,_,t in pieces]).astype(np.float32)
  Y=np.concatenate([(d['truth'][ix]==0).astype(np.int8) for d,ix,_,t in pieces])
  # T1 trained offline only: residual teacher microscope conditional on frozen parent.
  TY=np.concatenate([(t[ix]>=0.5).astype(np.int8) for d,ix,m,t in pieces])
  # T1 parent-only teacher baseline, direct full causal state + parent teacher probe.
  TP=np.concatenate([d['par'][ix] for d,ix,m,t in pieces]).astype(np.float32)
  p0=OUT/'models'/f'{b}_T1_PARENT_TEACHER_MICROSCOPE.txt';p1=OUT/'models'/f'{b}_T1_FULL_TEACHER_MICROSCOPE.txt'
  teacher_parent=lgb.Booster(model_file=str(p0)) if p0.exists() else fit(TP,TY,15091,rounds=95)
  teacher_source=lgb.Booster(model_file=str(p1)) if p1.exists() else fit(X,TY,15092,rounds=95)
  teacher_parent.save_model(str(p0));teacher_source.save_model(str(p1))
  # Autonomous T0 original-CORRECT guardian fits two seeds, no teacher supervision.
  models=[]
  for seed in (15071,15073):
   mp=OUT/'models'/f'{b}_T0_DIRECT_HTF_CCC_seed{seed}.txt'
   model=lgb.Booster(model_file=str(mp)) if mp.exists() else fit(X,Y,seed,rounds=125)
   if not mp.exists():model.save_model(str(mp))
   models.append(model)
  del X,Y,TY,TP,pieces;gc.collect()
  d6=read(b,'06');d7=read(b,'07')
  s6=score(models,d6);s7=score(models,d7)
  # June cut selection exclusively June original class, not teacher.
  ix=np.flatnonzero(d6['valid']&d6['veto']);options=[]
  for cut in np.unique(np.quantile(s6[ix],[.90,.94,.96,.975,.985,.992,.996,.998,.999,1.] )):
   z6=d6['valid']&d6['veto']&(s6>=cut)
   cor=int(np.count_nonzero(z6&(d6['truth']==0)));bad=int(np.count_nonzero(z6&(d6['truth']!=0)))
   options.append(dict(cut=float(cut),correct_recovered=cor,bad_readmitted=bad,bad_per_correct=(bad/cor if cor else None)))
  eligible=[a for a in options if a['correct_recovered']>=100 and a['bad_readmitted']<=4.5*a['correct_recovered']]
  selected=max(eligible,key=lambda x:x['correct_recovered']) if eligible else None
  cut=selected['cut'] if selected else 1.1
  june,jm=recount(d6,s6,cut);july,julym=recount(d7,s7,cut)
  # Existing path CCC July as frozen predecessor benchmark, same original label (not action-time economic).
  old=json.loads((ROOT/'R150D'/'results'/f'R150D_{b}_RESTORED_PATH_RESULT.json').read_text())
  # Offline teacher after score, never used for T0 decisions.
  teach={}
  with zipfile.ZipFile(ORACLE) as z:
   for m,d in [('06',d6),('07',d7)]:
    target=oracle(z,d,b,m);ix=np.flatnonzero(d['valid']&d['veto'])
    pp=np.zeros(len(ix),np.float32);ff=np.zeros(len(ix),np.float32)
    for k in range(0,len(ix),27000):
     ii=ix[k:k+27000];pp[k:k+len(ii)]=teacher_parent.predict(d['par'][ii],num_threads=2)
     ff[k:k+len(ii)]=teacher_source.predict(np.column_stack([d['X'][ii],d['par'][ii]]),num_threads=2)
    # AUC original CORRECT on actual frozen vetoes
    prob=s6 if m=='06' else s7
    teach[m]=dict(teacher_mae_parent=float(np.mean(np.abs(pp-target[ix]))),teacher_mae_direct=float(np.mean(np.abs(ff-target[ix]))),
      correct_guard_auc=float(roc_auc_score(d['truth'][ix]==0,prob[ix])),
      teacher_candidate_corr=float(np.corrcoef(ff,prob[ix])[0,1]))
  for m,d,s,mask in [('06',d6,s6,jm),('07',d7,s7,julym)]:
   out=OUT/'masks'/f'R150E_{b}_{m}_DIRECT_HTF_CCC_SHADOW.npz'
   np.savez_compressed(out,t=d['t'],side=d['side'],truth=d['truth'],valid=d['valid'],r148_veto=d['veto'],
     t0_decision=d['decision'],ccc_score=s,shadow_rescue=mask,
     shadow_veto=d['veto']&~mask)
  out=dict(broker=b,mechanism='T0 direct completed HTF36 + strict path57 + source304 + parent6; T1 teacher microscope separate',
   training=['01','02'],calibration='06',test='07',teacher_runtime=False,teacher_T0=False,
   calibrator='June >=100 right rescued, <=4.5 bad readmitted per right, otherwise parent fallback',
   calibration_grid=options,calibration_selected=selected,june=june,july=july,
   predecessor_july=old['july'],teacher_microscope=teach,seconds=round(time.time()-t0,2),
   status='UNAPPROVED_NO_OVERRIDE')
 (OUT/'results'/f'R150E_{b}_DIRECT_HTF_RESEARCH.json').write_text(json.dumps(out,indent=2))
 print(json.dumps({k:out[k] for k in ['broker','calibration_selected','june','july','predecessor_july','teacher_microscope','seconds']},indent=2),flush=True)
 return out

if __name__=='__main__':execute(sys.argv[1])

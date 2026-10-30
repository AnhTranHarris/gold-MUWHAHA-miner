"""R150B source-frozen research: July-held diagnostic on late-UTC causal quote microstructure.

Cross-fitted privileged teacher residual is an AUXILIARY TRAINING representation,
never a runtime teacher input. True-label heads trained Jan/Feb only, cut selection
June only, evaluation July. All original arrays keep source event ordinal.
Frozen R148B was fitted on exposed months: NOT full-stack blind forward evidence.
"""
from __future__ import annotations
from pathlib import Path
import io,json,hashlib,zipfile,os,sys,time,gc
import numpy as np
import lightgbm as lgb
from scipy.special import logit,expit
ROOT=Path('/mnt/data/R150B');FF=ROOT/'features';RR=ROOT/'results';MM=ROOT/'models'
TZ=Path('/mnt/data/R00_054_FILTER08_FOUR_MONTH_70PCT_OVERFIT_RESEARCH_20261019.zip')
SEEDS=(15031,15037)

def load_cell(b,m,teacher=False):
 with np.load(FF/f'R150B_{b}_{m}_LATE_PREFIX.npz') as a:
  d={k:a[k].copy() for k in ['X','parent','t','side','truth','valid','base','ordinal','decision']}
 if teacher:
  with zipfile.ZipFile(TZ) as z:
   with np.load(io.BytesIO(z.read(f'FILTER08/FITTED_CLASSIFIER_SCORES_{b}_{m}.npz'))) as q:
    original_t=q['t'];score=q['score']
    assert np.array_equal(original_t[d['ordinal']],d['t']),'teacher exact source ordinal mismatch'
    d['teacher']=score[d['ordinal']].astype(np.float32)
 return d

def lm(kind,seed,depth=31):
 common=dict(n_estimators=95,num_leaves=depth,learning_rate=.055,min_child_samples=65,max_bin=127,
             colsample_bytree=.78,subsample=.82,subsample_freq=1,reg_lambda=65.,reg_alpha=2.,
             n_jobs=2,verbosity=-1,random_state=seed)
 return (lgb.LGBMRegressor(objective='regression',**common) if kind=='regression'
         else lgb.LGBMClassifier(objective='binary',**common))

def fit_on(m,xa,ya,seed):
 clf=lm('regression' if m=='reg' else 'bin',seed)
 if m=='bin':
  classes,counts=np.unique(ya,return_counts=True)
  if len(classes)<2: raise RuntimeError('class missing')
  weights=np.where(ya==1,min(5.,counts[0]/max(1,counts[1])),1.).astype(np.float32)
  clf.fit(xa,ya,sample_weight=weights)
 else: clf.fit(xa,ya)
 return clf.booster_

def predicted(m,x,kind='reg'):
 return m.predict(x,num_threads=2).astype(np.float32)

def teacher_residual(b):
 d1=load_cell(b,'01',True);d2=load_cell(b,'02',True)
 s1=np.flatnonzero(d1['valid']);s2=np.flatnonzero(d2['valid']);
 # For each fitting month, nuisance prediction is genuinely out-of-month.
 nuisance=[fit_on('reg',d1['parent'][s1],logit(np.clip(d1['teacher'][s1],.001,.999)),15001),
           fit_on('reg',d2['parent'][s2],logit(np.clip(d2['teacher'][s2],.001,.999)),15002)]
 residual=[];dsets=[d1,d2]
 for i,(d,ind) in enumerate(zip(dsets,[s1,s2])):
  tlog=logit(np.clip(d['teacher'][ind],.001,.999))
  res=np.clip(tlog-predicted(nuisance[1-i],d['parent'][ind]),-10,10)
  residual.append(res.astype(np.float32))
 # Source-only orthogonal learner receives NO compressed parent channels, only
 # full R149 179D + new marked quote 32D. Teacher only defines training target.
 X=np.vstack([d1['X'][s1],d2['X'][s2]]);Y=np.concatenate(residual)
 oof=[]
 # Crossfit residual model across months to generate unbiased *head-training* latents.
 r1=fit_on('reg',d1['X'][s1],residual[0],15013);r2=fit_on('reg',d2['X'][s2],residual[1],15017)
 pred1=predicted(r2,d1['X'][s1]);pred2=predicted(r1,d2['X'][s2]);oof=[pred1,pred2]
 nuisance_all=fit_on('reg',np.vstack([d1['parent'][s1],d2['parent'][s2]]),np.concatenate([logit(np.clip(d1['teacher'][s1],.001,.999)),logit(np.clip(d2['teacher'][s2],.001,.999))]),15021)
 residual_all=fit_on('reg',X,Y,15023)
 for n,mod in [('NUISANCE',nuisance_all),('RESIDUAL',residual_all)]:mod.save_model(str(MM/f'{b}_{n}.txt'))
 # Independent source student incremental teacher signal audit June/July.
 checks={}
 for mm in ['06','07']:
  c=load_cell(b,mm,True);ind=np.flatnonzero(c['valid']);ty=logit(np.clip(c['teacher'][ind],.001,.999))
  pn=predicted(nuisance_all,c['parent'][ind]);rz=predicted(residual_all,c['X'][ind])
  base_mae=np.mean(np.abs(expit(pn)-c['teacher'][ind]));aug_mae=np.mean(np.abs(expit(np.clip(pn+rz,-20,20))-c['teacher'][ind]))
  checks[mm]={'baseline_teacher_mae':float(base_mae),'orthogonal_augmented_mae':float(aug_mae),'mae_improvement':float(base_mae-aug_mae),'n':len(ind)}
 (RR/f'{b}_TEACHER_FIDELITY.json').write_text(json.dumps(checks,indent=2))
 return (d1,d2),(s1,s2),oof,residual_all,checks

def fit_heads(b,use_event:bool,use_teacher:bool,train,idx,oof):
 X=[];Y=[];BASE=[]
 for d,ii,z in zip(train,idx,oof):
  a=d['X'][ii] if use_event else d['X'][ii,:179]
  if use_teacher:a=np.column_stack([a,z])
  X.append(a);Y.append(d['truth'][ii]);BASE.append(d['base'][ii])
 X=np.vstack(X).astype(np.float32);y=np.concatenate(Y);base=np.concatenate(BASE)
 models={};name=f'{b}_E{int(use_event)}_T{int(use_teacher)}'
 for head,mask,positive in [
  ('rescue',base,y==0),('neutral',~base,y==2),('opposite',~base,y==1)]:
  target=positive[mask].astype(np.int8)
  clf=fit_on('bin',X[mask],target,SEEDS[0] + {'rescue':0,'neutral':3,'opposite':6}[head]);models[head]=clf
  clf.save_model(str(MM/f'{name}_{head}.txt'))
 return models

def score_cell(d,models,use_event,use_teacher,residual_model):
 x=d['X'] if use_event else d['X'][:,:179]
 if use_teacher:x=np.column_stack([x,predicted(residual_model,d['X'])])
 scores={}
 for name,model in models.items():scores[name]=predicted(model,x,'bin')
 return scores

def count(d,v):
 q=d['truth'];return {'opposite':int((v&(q==1)).sum()),'neutral':int((v&(q==2)).sum()),'bad':int((v&(q!=0)).sum()),'correct_lost':int((v&(q==0)).sum())}

def policy(d,sc,cut):
 rescue,neutral,opposite=cut
 return (d['base']&~(d['valid']&(sc['rescue']>=rescue)))|((~d['base'])&d['valid']&((sc['neutral']>=neutral)|(sc['opposite']>=opposite)))

def calibrate(d,sc):
 # Cuts fixed on donor June exclusively, NEVER target July. Cost of a candidate
 # relative to frozen parent includes rescues (both correct and bad releases).
 base=count(d,d['base']);best=(float('-inf'),None,None)
 vr=sc['rescue'][d['valid']&d['base']];vn=sc['neutral'][d['valid']&~d['base']];vo=sc['opposite'][d['valid']&~d['base']]
 # Failure-to-improve parent is a valid outcome. Infinity = no overrides.
 for cr in [np.inf,*np.quantile(vr,[.90,.96,.985,.997]).tolist()]:
  for cn in [np.inf,*np.quantile(vn,[.97,.985,.992,.997]).tolist()]:
   for co in [np.inf,*np.quantile(vo,[.97,.985,.992,.997]).tolist()]:
    mask=policy(d,sc,(cr,cn,co));metrics=count(d,mask)
    # Parent remains a valid fallback, and no new false-veto budget is spent.
    if metrics['correct_lost']>base['correct_lost']:continue
    extra=metrics['bad']-base['bad']
    quality=(extra,base['correct_lost']-metrics['correct_lost'])
    if quality>best[0:2]:best=(extra,quality[1],(float(cr),float(cn),float(co)),metrics)
 assert best[2] is not None
 return {'cuts':best[2],'cal_parent':base,'cal_challenger':best[3], 'cal_incremental_bad':int(best[0])}

def run_broker(b):
 st=time.monotonic();train,idx,oof,resid,checks=teacher_residual(b)
 cal=load_cell(b,'06');test=load_cell(b,'07');runs=[]
 for event,teacher in [(False,False),(True,False),(True,True)]:
  models=fit_heads(b,event,teacher,train,idx,oof)
  sc=score_cell(cal,models,event,teacher,resid);cuts=calibrate(cal,sc)
  tt=score_cell(test,models,event,teacher,resid);pv=policy(test,tt,cuts['cuts'])
  parent=count(test,test['base']);trial=count(test,pv)
  rec={'broker':b,'event_time_32D':event,'teacher_auxiliary':teacher,'test':'07','fit':['01','02'],'calibration':'06',
       'calibration':cuts,'test_parent':parent,'test_challenger':trial,
       'bad_delta':trial['bad']-parent['bad'],'correct_delta':trial['correct_lost']-parent['correct_lost'],
       'strict_source_decision':True,'full_stack_g08_blind':False,'r148_parent_unchanged':True,'R150_override_active':False}
  runs.append(rec);print(json.dumps({'cell':b,'method':(event,teacher),'delta':(rec['bad_delta'],rec['correct_delta']),'test':trial}),flush=True)
  np.savez_compressed(RR/f'{b}_E{int(event)}_T{int(teacher)}_JULY_MASK.npz',t=test['t'],truth=test['truth'],ordinal=test['ordinal'],valid=test['valid'],parent=test['base'],candidate=pv)
 (RR/f'{b}_COMPARATIVE.json').write_text(json.dumps({'teacher_fidelity':checks,'runs':runs},indent=2))
 print('FINISHED',b,'elapsed',round(time.monotonic()-st,1),flush=True)
if __name__=='__main__':run_broker(sys.argv[1])

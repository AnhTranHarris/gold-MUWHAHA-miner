#!/usr/bin/env python3
"""F37: chronological research transition Jan/Feb + early June fit -> final June calibration -> July source-month external transfer.
All original events intact, independent broker feed inference. MQL5 parity needs later verification.
"""
import sys,json,zipfile,io,time
from pathlib import Path
import numpy as np
from lightgbm import LGBMClassifier
from joblib import dump
ROOT=Path('/mnt/data');P=ROOT/'R00_054_F37_JANFEBJUNE_CAUSAL_TRANSFER_20261020';P.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT))
import f35_run as phase
import f34_run as past
src=phase.src

def loader(b,m):
 c=phase.build(b,m)
 with zipfile.ZipFile(src.SEVEN) as z: blob=z.read(f'evidence/FROZEN_R00_054_EVENTS_{b}_{m}.npz')
 with np.load(io.BytesIO(blob)) as f: d=f['d30'].copy()
 a=past.matured(c['t'],c['side'],d)
 c['X']=np.column_stack([c['X'],a]).astype('float32')
 return c

def raw(c,score,cut,refs):
 mask=score>=cut;y=c['y'];good=y==0;bad=~good;q=src.quota_stats(c,mask,refs)
 return {'kept_good':int(np.sum(mask&good)),'good_total':int(good.sum()),'rejected_bad':int(np.sum(~mask&bad)),'bad_total':int(bad.sum()),'correct_retention':float(mask[good].mean()),'bad_rejection':float((~mask[bad]).mean()),'new_quotas':{k:len(q[k]) for k in ('newly_failed_hours','newly_failed_days','newly_failed_weeks','newly_failed_months')}}

def run():
 contract={'experiment':'F37','source_exact':'all 8 original source caches and original frozen event quote timestamps; no raw quotes or original FILTER05 15 restored','fit_population':'Jan first80%, entire Feb, Jun first65% with last35% Jun excluded for calibration; only event t-33s historical matured labels','strict_sep':'Jun last35 calibration; July held-out source month evaluated once without refit or cutoff selection','broker_tapes':'not merged price quotes; fit data row pooled only and held-out tested independently','features':['76 original causal','240 event-to-event transitions','delayed past fully-matured outcomes'],'families':['J_F_B_Frozen_Regularized','J_F_B_Frozen_Deep'],'threshold_quantiles':'June heldout 0..0.7 step .05; preserve >=71% good both brokers and zero R9 interval quota breaches on whole June','desired':'71% correct kept, 90% incorrect rejected','MQL5':'reimplement causal lagged features and test model operator conversion before any EA'}
 (P/'F37_FROZEN_PROTOCOL.json').write_text(json.dumps(contract,indent=2)+'\n')
 refs=src.r9_reference()
 Xp=[];yp=[]
 for m in ('01','02','06'):
  for b in src.BROKERS:
   c=loader(b,m)
   if m=='01': portion=.8;thin=5
   elif m=='02': portion=.95;thin=5
   else:portion=.65;thin=4
   u=int(len(c['t'])*portion);ids=np.flatnonzero(c['t']<c['t'][u]-40000)[::thin]
   Xp.append(c['X'][ids]);yp.append((c['y'][ids]==0).astype(np.int8))
   print('FIT rows',b,m,len(ids),'dims',c['X'].shape[1],flush=True)
   del c
 X=np.concatenate(Xp);Y=np.concatenate(yp);del Xp,yp
 print('TRAIN',X.shape,flush=True)
 dim=X.shape[1]
 models={}
 for name,params in [('regularized',dict(n_estimators=240,num_leaves=45,min_child_samples=210,reg_lambda=14,learning_rate=.048)),('deeper',dict(n_estimators=360,num_leaves=121,min_child_samples=105,reg_lambda=7,learning_rate=.046))]:
  model=LGBMClassifier(**params,n_jobs=3,verbosity=-1,random_state=54037,colsample_bytree=.86,subsample=.85,subsample_freq=1)
  model.fit(X,Y)
  dump(model,P/f'F37_MODEL_{name}.joblib',compress=3);models[name]=model
 del X,Y
 june={b:loader(b,'06') for b in src.BROKERS}
 sc={b:{name:m.predict_proba(c['X'])[:,1] for name,m in models.items()} for b,c in june.items()}
 frozen={};grid=[]
 for name in models:
  calidx={b:np.arange(len(c['t']))>=int(len(c['t'])*.65) for b,c in june.items()}
  distribution=np.concatenate([sc[b][name][calidx[b]] for b in src.BROKERS]);validrules=[]
  for q in np.arange(0,.701,.05):
   cut=float(np.quantile(distribution,q));rows=[];valid=True
   for b,c in june.items():
    vals=raw(c,sc[b][name],cut,refs)
    rr=c['y'][calidx[b]]==0;mm=sc[b][name][calidx[b]]>=cut
    ret=mm[rr].mean();reject=(~mm[~rr]).mean()
    now=dict(broker=b,cal_ret=float(ret),cal_bad_rejection=float(reject),full_quota_fails=vals['new_quotas'])
    rows.append(now);valid = bool(valid) and bool(ret>=.71 and not any(vals['new_quotas'].values()))
   rule={'name':name,'q':round(float(q),3),'threshold':cut,'rows':rows,'valid':bool(valid)}
   grid.append(rule)
   if valid:validrules.append(rule)
  frozen[name]=max(validrules,key=lambda d:min(r['cal_bad_rejection'] for r in d['rows'])) if validrules else None
 (P/'F37_JUNE_CAL_GRID.json').write_text(json.dumps(grid,indent=2)+'\n')
 (P/'F37_JUNE_FROZEN_POLICY.json').write_text(json.dumps(frozen,indent=2)+'\n')
 del june,sc
 results=[]
 for b in src.BROKERS:
  c=loader(b,'07')
  for name,model in models.items():
   p=model.predict_proba(c['X'])[:,1]
   np.savez_compressed(P/f'F37_JULY_{b}_{name}_SOURCE_EVENT_SCORES.npz',t=c['t'],side=c['side'],y=c['y'],p=p.astype('float32'))
   if frozen[name] is not None:
    met=raw(c,p,frozen[name]['threshold'],refs)
    results.append({'broker':b,'month':'07','family':name,**met,'owner_pass':met['correct_retention']>=.71 and met['bad_rejection']>=.90 and not any(met['new_quotas'].values())})
    print('F37 RESULT',b,name,met,flush=True)
  del c
 (P/'F37_JULY_OUT_OF_FIT_SCORING.json').write_text(json.dumps(results,indent=2)+'\n')
 print('DONE',flush=True)
if __name__=='__main__':run()
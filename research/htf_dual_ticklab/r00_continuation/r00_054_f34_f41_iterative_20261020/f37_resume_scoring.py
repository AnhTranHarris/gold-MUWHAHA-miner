#!/usr/bin/env python3
"""F37 isolated resume: uses exact persisted trained models; no refit. Fixes JSON serialization of NumPy bool."""
import sys,json
from pathlib import Path
import numpy as np
from joblib import load
ROOT=Path('/mnt/data');sys.path.insert(0,str(ROOT))
from f37_recent_multi_month import loader,raw,P,src
refs=src.r9_reference(); models={x:load(P/f'F37_MODEL_{x}.joblib') for x in ('regularized','deeper')}
june={b:loader(b,'06') for b in src.BROKERS}
sc={b:{name:model.predict_proba(c['X'])[:,1] for name,model in models.items()} for b,c in june.items()}
frozen={};grid=[]
for name in models:
 calidx={b:np.arange(len(c['t']))>=int(len(c['t'])*.65) for b,c in june.items()}
 distribution=np.concatenate([sc[b][name][calidx[b]] for b in src.BROKERS]);validrules=[]
 for q in np.arange(0,.701,.05):
  cut=float(np.quantile(distribution,q));rows=[];valid=True
  for b,c in june.items():
   vals=raw(c,sc[b][name],cut,refs)
   rr=c['y'][calidx[b]]==0;mm=sc[b][name][calidx[b]]>=cut
   ret=float(mm[rr].mean());reject=float((~mm[~rr]).mean())
   now=dict(broker=b,cal_ret=ret,cal_bad_rejection=reject,full_quota_fails=vals['new_quotas'])
   rows.append(now);valid=bool(valid) and bool(ret>=.71 and not any(vals['new_quotas'].values()))
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
   results.append({'broker':b,'month':'07','family':name,**met,'owner_pass':bool(met['correct_retention']>=.71 and met['bad_rejection']>=.90 and not any(met['new_quotas'].values()))})
   print('F37 JULY',b,name,met,flush=True)
 del c
(P/'F37_JULY_OUT_OF_FIT_SCORING.json').write_text(json.dumps(results,indent=2)+'\n')
print('F37 DONE',flush=True)
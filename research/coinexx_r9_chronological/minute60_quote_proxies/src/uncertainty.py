"""Descriptive day-block paired bootstrap: exposed-month research, NOT independent OOS."""
from __future__ import annotations
import hashlib,io,json,sys,zipfile
from pathlib import Path
import joblib,numpy as np
from sklearn.metrics import roc_auc_score
ROOT=Path('/mnt/data/r9_m60_proxy_20261113');sys.path.insert(0,str(ROOT/'src'))
from train_proxy import read_month
BASE=Path('/mnt/data/R9_M60_JanSep_FullTraining_155Features_20261113.zip')

def run(B=160):
 rng=np.random.default_rng(20261113)
 buffers=[];obs=[]
 with zipfile.ZipFile(BASE) as z:
  for m in range(5,10):
   mm=f'{m:02d}';r=read_month(mm)
   ix=2*np.arange(r['n_entries'])+(r['r9_side']<0).astype(int)
   valid=r['good'][ix]
   zref=z.read(f'models/direct_test_{mm}_shadow.joblib')
   bmodel=joblib.load(io.BytesIO(zref))['model']
   pred0=bmodel.predict_proba(r['base'])[:,1][ix][valid]
   fams=['marked_hawkes','all_quote_proxies']
   pred=[pred0]
   for key in fams:
    art=joblib.load(ROOT/'models'/f'{key}_test_{mm}_shadow.joblib')['model']
    selected=list(range(12)) if key=='marked_hawkes' else list(range(27))
    x=np.concatenate([r['base'],r['proxy'][:,selected]],axis=1)
    pred.append(art.predict_proba(x)[:,1][ix][valid])
   y=r['y'][ix][valid]
   day=(r['entry_ms'][valid]//86400000).astype(np.int64)
   gids,inv=np.unique(day,return_inverse=True)
   groups=[np.where(inv==k)[0] for k in range(len(gids))]
   buffs={'month':mm,'y':y,'pred':pred,'groups':groups}
   buffers.append(buffs)
   obs.append({'month':mm,'n_days':len(groups),'n_valid_original_actions':len(y),
               'auc':[float(roc_auc_score(y,p)) for p in pred],
               'delta_marked':float(roc_auc_score(y,pred[1])-roc_auc_score(y,pred[0])),
               'delta_all':float(roc_auc_score(y,pred[2])-roc_auc_score(y,pred[0]))})
 draws=np.empty((B,2),float)
 for b in range(B):
  month_deltas=[]
  for z in buffers:
   gs=z['groups'];which=rng.integers(0,len(gs),size=len(gs));ix=np.concatenate([gs[i] for i in which]);y=z['y'][ix]
   if np.unique(y).size!=2:continue
   base=roc_auc_score(y,z['pred'][0][ix])
   month_deltas.append([roc_auc_score(y,z['pred'][1][ix])-base,
                        roc_auc_score(y,z['pred'][2][ix])-base])
  draws[b]=np.mean(month_deltas,axis=0)
 output={'status':'DESCRIPTIVE_BOOTSTRAP_RETROSPECTIVE_EXPOSED_MONTHS',
         'resamples':B,'unit':'calendar day within each heldout month; original R9 direction',
         'months':obs,'mean_observed_delta_marked':float(np.mean([v['delta_marked'] for v in obs])),
         'mean_observed_delta_all':float(np.mean([v['delta_all'] for v in obs])),
         'marked_95pct':[float(z) for z in np.quantile(draws[:,0],[.025,.975])],
         'all_95pct':[float(z) for z in np.quantile(draws[:,1],[.025,.975])],
         'warning':'A descriptive within-exposed-data CI, not a new independent confirmation or proof of a causal information gain.'}
 (ROOT/'results'/'UNCERTAINTY.json').write_text(json.dumps(output,indent=2)+'\n')
 print('DAY_BLOCK',json.dumps({k:v for k,v in output.items() if k not in ('months',)},indent=2))
 return output
if __name__=='__main__':run()

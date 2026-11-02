"""Restartable exact-month R9 hyper-reject experiment. Side/threshold/each replay separate.

Baseline samples cover all four full-month spans for fitting, exhaustive scoring
and original R9 R9 quote-side outcome labels cover EVERY 250ms candidate on replay.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,time
import numpy as np
import lightgbm as lgb
from r9_side_competing import OUT,MONTHS,load,augment,admission,eval_month,sha,FRACTIONS

def fit_one(side,mode,monthly_sample=85000,trees=85,leaves=55):
 months=MONTHS if mode=='all4' else tuple(m for m in MONTHS if m!='07')
 x=[];y=[];before=time.monotonic()
 for m in months:
  from r9_side_competing import sample_month
  xx,cc=sample_month(m,monthly_sample)
  x.append(xx);y.append(cc[:,side]+1)
  print('SAMPLED',mode,side,m,len(xx),flush=True)
 X=np.concatenate(x);Y=np.concatenate(y);del x,y
 count=np.bincount(Y,minlength=3)
 assert (count>0).all()
 # side-specific tri-class posterior uses independent neutral/wrong rejection
 mdl=lgb.LGBMClassifier(objective='multiclass',num_class=3,n_estimators=trees,
      num_leaves=leaves,learning_rate=.07,min_child_samples=160,max_bin=127,
      colsample_bytree=.82,reg_lambda=12,subsample=.85,subsample_freq=1,
      random_state=20261102,n_jobs=2,verbosity=-1)
 mdl.fit(X,Y)
 output=OUT/f'R9_{mode}_{"BUY" if side==0 else "SELL"}_competing.txt'
 mdl.booster_.save_model(str(output))
 receipt={'side':side,'fit_months':list(months),'n':len(Y),'class_distribution':count.tolist(),
 'model_sha256':sha(output),'trees':trees,'leaves':leaves,
 'selection':'in_sample if evaluating fit month; NOT prospective',
 'fit_seconds':round(time.monotonic()-before,2)}
 (OUT/f'R9_{mode}_{"BUY" if side==0 else "SELL"}_fit_part.json').write_text(json.dumps(receipt,indent=2))
 print('SAVED SIDE',mode,side,receipt['fit_seconds'],receipt['model_sha256'],flush=True)


def freeze(mode,monthly_sample=20000):
 months=MONTHS if mode=='all4' else tuple(m for m in MONTHS if m!='07')
 parts=[json.loads((OUT/f'R9_{mode}_{s}_fit_part.json').read_text()) for s in ('BUY','SELL')]
 for i,p in enumerate(parts):
  f=OUT/f'R9_{mode}_{"BUY" if i==0 else "SELL"}_competing.txt'
  if sha(f)!=p['model_sha256'] or p['fit_months']!=list(months):raise ValueError('fit part mismatch')
 models=[lgb.Booster(model_file=str(OUT/f'R9_{mode}_{s}_competing.txt')) for s in ('BUY','SELL')]
 before=time.monotonic();results=[];labs=[]
 for mon in months:
  from r9_side_competing import sample_month
  x,y=sample_month(mon,monthly_sample)
  p=np.stack([mdl.predict(x,num_threads=2) for mdl in models],axis=1)
  score,side,margin=admission(p)
  results.append(score);labs.append(y[np.arange(len(y)),side]==1)
  print('FROZEN SAMPLE SCORED',mode,mon,len(score),flush=True)
 score=np.concatenate(results);truth=np.concatenate(labs)
 thresholds={str(f):float(np.quantile(score,1-f)) for f in FRACTIONS}
 m={'mode':mode,'training_months':list(months),'frozen_thresholds':thresholds,
 'model_sha256':{str(p['side']):p['model_sha256'] for p in parts},
 'training_selected_correctness':{},'model_fit_part_receipts':parts,
 'threshold_sample_monthly':monthly_sample,'fit_features':'R8 41 as-of + R7 12 nested causal axes',
 'disclaimer':'training label resubstitution, not OOS or deployable performance'}
 for f in FRACTIONS:
  ix=score>=thresholds[str(f)]
  m['training_selected_correctness'][str(f)]={'n':int(ix.sum()),'good':int(truth[ix].sum()),
   'strict_precision':float(truth[ix].mean()) if ix.sum() else None}
 (OUT/f'R9_{mode}_FIT.json').write_text(json.dumps(m,indent=2))
 print('FROZEN',mode,'sec',round(time.monotonic()-before,2),flush=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['all4','lomo07'],default='all4')
 ap.add_argument('--side',choices=['BUY','SELL']);ap.add_argument('--freeze',action='store_true')
 ap.add_argument('--evaluate',choices=MONTHS)
 x=ap.parse_args()
 if x.side:fit_one(0 if x.side=='BUY' else 1,x.mode)
 elif x.freeze:freeze(x.mode)
 elif x.evaluate:eval_month(x.mode,x.evaluate)
 else:ap.error('need --side, --freeze or --evaluate')

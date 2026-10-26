"""F408 Jan/Feb fit/CAL/VAL, June/July historically exposed frozen transfer.

This is event-only research: it cannot certify original 4,178 R9 SYNTH floors
without their exact source-matched reference rows, nor quote/HTF provenance.
"""
from __future__ import annotations
import os,io,json,time,zipfile,hashlib,pathlib,sys
import numpy as np
import lightgbm as lgb
from f408_causal_event_hazard import features,load_original
ROOT=pathlib.Path(__file__).resolve().parent
SOURCE=ROOT.parent/'F394_F395_EIGHTCELL_NATIVE_PATH_FROZEN_RESEARCH_UNAPPROVED_20261024.zip'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='a3367cba013912749cc31a6c7fde034dfb6546c4fd6a182d40d774414748e41d'

def split(o,which):
 n=len(o['t']);t=o['t'];j60=int(.60*n);j80=int(.80*n);j80jan=int(.80*n)
 if which=='jan_fit':return (np.arange(n)<j80jan)&(t<t[j80jan]-40000)
 if which=='feb_fit':return (np.arange(n)<j60)&(t<t[j60]-40000)
 if which=='feb_cal':return (np.arange(n)>=j60)&(np.arange(n)<j80)&(t>t[j60]+40000)&(t<t[j80]-40000)
 if which=='feb_val':return (np.arange(n)>=j80)&(t>t[j80]+40000)
 raise ValueError(which)

def metrics(o,keep):
 truth=o['truth'];good=(truth==0);bad=~good
 out={'original_n':len(truth),'correct_total':int(good.sum()),'incorrect_total':int(bad.sum()),
 'correct_kept':int((keep&good).sum()),'incorrect_rejected':int((~keep&bad).sum()),
 'retained_precision':float((keep&good).sum()/max(keep.sum(),1)),
 'correct_retention':float((keep&good).sum()/max(good.sum(),1)),
 'incorrect_rejection':float((~keep&bad).sum()/max(bad.sum(),1))}
 return out

def quota_proxy(o,keep):
 # Not actual R9 SYNTH quotas: diagnostic ONLY, by original-event hour/day.
 t=o['t'];right=(o['truth']==0)
 out={}
 for unit,den in [('utc_hour',3600000),('utc_day',86400000)]:
  ids=t//den;_,inv=np.unique(ids,return_inverse=True)
  before=np.bincount(inv,weights=right);after=np.bincount(inv,weights=right&keep)
  eligible=before>0;fail=eligible&(after<.9*before)
  out[unit]={'nonempty':int(eligible.sum()),'below_90pct_original_correct':int(fail.sum()),
             'min_original_correct_retention':float(np.min(after[eligible]/before[eligible])) if eligible.any() else None}
 return out

def run():
 report={'id':'F408-R01','classification':'UNAPPROVED_EVENT_ONLY_HISTORICALLY_EXPOSED','source_zip_sha256':'a3367cba013912749cc31a6c7fde034dfb6546c4fd6a182d40d774414748e41d',
         'source_event_contract':'F395 original index/t0 UTC/side/truth, immutable; 30-32s historical midpoint label, not executed PnL',
         'feature_clock':'original t0, prior diagnostic labels available only if t_prior+33002ms <= current t0',
         'input_exclusions':['raw quote intensity','completed HTF price bars','FILTER08 in-month fitted teacher','live executed fills'],
         'model':'broker-specific LightGBM multiclass 3-way 127 leaves, 75 fixed trees, 0.045 lr, 100k fit cap, seed 408',
         'policy':'CAL-only q=.71 correct-score cut, max wrong-risk; applied without transfer retune',
         'cells':{},'source_members_sha256':{},'limitations':['no original R9 4178 hourly/day quota reference rows','no quote source or genuine closed-market-structure feature','historically exposed June/July','past labels require independent runtime streamer']}
 with zipfile.ZipFile(SOURCE) as z:
  assert z.testzip() is None
  for broker in ('coinexx','dukascopy'):
   ds={}
   for month in ('01','02','06','07'):
    o,sha=load_original(z,broker,month);X,names,end=features(o['t'],o['side'],o['truth']);o['X']=X;ds[month]=o
    report['source_members_sha256'][broker+'_'+month]=sha
    print('FEATURES',broker,month,len(o['t']),len(names),flush=True)
   jan, feb=ds['01'],ds['02']
   ja=np.flatnonzero(split(jan,'jan_fit'))[::3];fb=np.flatnonzero(split(feb,'feb_fit'))[::3]
   X=np.vstack((jan['X'][ja],feb['X'][fb]));y=np.r_[jan['truth'][ja],feb['truth'][fb]]
   if len(y)>100000:
    rng=np.random.default_rng(408);sel=np.sort(rng.choice(len(y),100000,replace=False));X,y=X[sel],y[sel]
   model=lgb.LGBMClassifier(objective='multiclass',num_class=3,num_leaves=127,n_estimators=75,
      learning_rate=.045,max_bin=127,min_child_samples=80,colsample_bytree=.9,subsample=1.,
      reg_lambda=10.,verbosity=-1,random_state=408,n_jobs=2)
   model.fit(X,y)
   booster=model.booster_;model_text=booster.model_to_string()
   model_path=ROOT/f'F408_R01_{broker}_3CLASS_MODEL.txt';model_path.write_text(model_text)
   report.setdefault('models',{})[broker]={'sha256':hashlib.sha256(model_path.read_bytes()).hexdigest(),
                                          'fit_rows':len(y),'class_count':np.bincount(y,minlength=3).tolist(),
                                          'feature_names':names}
   cal=split(feb,'feb_cal');calpred=model.predict_proba(feb['X'][cal]);risk=1-calpred[:,0]
   threshold=float(np.quantile(risk[feb['truth'][cal]==0],.71,method='higher'))
   report['models'][broker]['feb_cal_threshold']=threshold
   for month,o in ds.items():
    p=model.predict_proba(o['X']);r=1-p[:,0];keep=r<=threshold
    mask={'01':split(o,'jan_fit'),'02':split(o,'feb_cal')|split(o,'feb_val'),'06':np.ones(len(o['t']),bool),'07':np.ones(len(o['t']),bool)}[month]
    full=metrics(o,keep);full['quota_proxy']=quota_proxy(o,keep)
    original_survivor=~o['final_source_shadow_veto'];new_veto=~keep
    inc_bad=(new_veto&original_survivor&(o['truth']!=0)).sum();inc_good=(new_veto&original_survivor&(o['truth']==0)).sum()
    full['incremental_vs_F395']={'additional_incorrect_veto':int(inc_bad),'additional_correct_veto':int(inc_good),
                                'wrong_to_good_ratio':float(inc_bad/max(inc_good,1))}
    if month=='02':
     for tag in ('CAL','VAL'):
      m=split(o,'feb_'+tag.lower());part=metrics({k:v[m] for k,v in o.items() if k in ('truth',)},keep[m])
      full[tag]=part
    report['cells'][broker+'_'+month]=full
    np.savez_compressed(ROOT/f'F408_R01_{broker}_{month}_SCORES_MASKS.npz',
      original_index=o['original_index'],t=o['t'],side=o['side'],truth=o['truth'],
      source_parent_veto=o['final_source_shadow_veto'],score_wrong=r.astype(np.float32),
      frozen_keep=keep,fold=(np.where(mask,1,0)).astype(np.int8))
    print('CELL',broker,month,'correct',full['correct_retention'],'wrong_rej',full['incorrect_rejection'],
          'incremental',full['incremental_vs_F395'],flush=True)
   del ds
 report['qualified_all_exposed']=all(report['cells'][b+'_'+m]['correct_retention']>=.71 and report['cells'][b+'_'+m]['incorrect_rejection']>=.90 for b in ('coinexx','dukascopy') for m in ('06','07'))
 report['verified_R9_90pct_hour_day_floors']=False
 report['user_notification_qualified']=False
 (ROOT/'F408_R01_ALL8_REPORT.json').write_text(json.dumps(report,indent=2))
 print('QUALIFIED',report['qualified_all_exposed'],flush=True)
if __name__=='__main__':run()

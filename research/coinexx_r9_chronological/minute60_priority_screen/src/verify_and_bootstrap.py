"""Independent archived-model AUC readback and paired day-block uncertainty.

This is a retrospective diagnostic, not a true unseen test. Date-level bootstrap
preserves within-day dependence approximately. No tuning is performed with it.
"""
import hashlib,json,sys
from pathlib import Path
import numpy as np,joblib
from sklearn.metrics import roc_auc_score
from train_screen import ROOT,load_month,features,FAMILIES
import train as prior


def run(n_boot=180):
 folds=[]; store=[]
 for i in range(5,10):
  mm=f'{i:02}'
  receipt=json.loads((ROOT/'results'/f'fold_{mm}.json').read_text())
  r=load_month(mm);n=r['n_orig'];original_side=2*np.arange(n)+np.where(r['r9_side'][::2]==1,0,1)
  good=(r['cause']!=-1)
  yy=(r['cause']==1)&(r['hit']>=0)&(r['hit']<=5000)
  for fam in FAMILIES:
   path=ROOT/'models'/f'{fam}_test_{mm}_FAILED_UNTIL_CERTIFIED.joblib'
   sha=hashlib.sha256(path.read_bytes()).hexdigest()
   if sha!=receipt['models'][fam]['model_sha256']:raise AssertionError('saved model integrity failed')
   model=joblib.load(path)['model']
   prob=prior.cumulative_incidence(model,features(r['X'],fam,r['orig_width']))
   for horizon in (5000,15000):
    y=(r['cause']==1)&(r['hit']>=0)&(r['hit']<=horizon)
    auc=float(roc_auc_score(y[good],prob[horizon]['p_fav'][good]))
    orig_auc=float(roc_auc_score(y[original_side][good[original_side]],prob[horizon]['p_fav'][original_side][good[original_side]]))
    prior_result=receipt['models'][fam][str(horizon)]
    if abs(auc-prior_result['all_actions_auc'])>1e-12 or abs(orig_auc-prior_result['r9_action_auc'])>1e-12:
     raise AssertionError((mm,fam,horizon,auc,orig_auc,prior_result))
   if fam in ('frozen_baseline','all_three','brownian_geometry_only'):
    idx=original_side
    store.append((mm,fam,(r['time'][idx][good[idx]]//(24*3600*1000)).astype('i8'),yy[idx][good[idx]],prob[5000]['p_fav'][idx][good[idx]]))
  folds.append({'month':mm,'models_verified':len(FAMILIES),'original_entry_count':n})
  print('VERIFIED',mm,'all 5 models, both 5 and 15s, both pooled and original side',flush=True)
 # Paired dates within months: resample date blocks to form monthly R9-action AUC deltas.
 # Each rep reuses same day draws for both models; no inter-date independence assumption.
 rng=np.random.default_rng(20261113);monthly=[];aggregate=[]
 for mm in ('05','06','07','08','09'):
  data={f:(d,y,p) for m,f,d,y,p in store if m==mm}
  days,y,pbase=data['frozen_baseline'];days2,y2,pnew=data['all_three'];_,_,pgeo=data['brownian_geometry_only']
  if not np.array_equal(days,days2) or not np.array_equal(y,y2):raise AssertionError('paired response mismatch')
  uniq=np.unique(days);byday=[np.flatnonzero(days==dd) for dd in uniq]
  deltas=[];deltas_geo=[]
  for iteration in range(n_boot):
   indices=np.concatenate([byday[j] for j in rng.integers(0,len(byday),len(byday))])
   yy=y[indices]
   if not (np.any(yy) and np.any(~yy)):continue
   base=roc_auc_score(yy,pbase[indices])
   deltas.append(roc_auc_score(yy,pnew[indices])-base)
   deltas_geo.append(roc_auc_score(yy,pgeo[indices])-base)
  aggregate.append(np.array(deltas))
  monthly.append({'month':mm,'utc_days':len(uniq),'boot_reps':len(deltas),
   'delta_all_mean':float(np.mean(deltas)),'delta_all_p025':float(np.quantile(deltas,.025)),
   'delta_all_p975':float(np.quantile(deltas,.975)),
   'delta_geometry_mean':float(np.mean(deltas_geo)),'delta_geometry_p025':float(np.quantile(deltas_geo,.025)),
   'delta_geometry_p975':float(np.quantile(deltas_geo,.975))})
 # Paired within-month block resamples; equal-weight five held-out months.
 combined=np.mean(np.stack(aggregate),axis=0)
 report={'status':'RETROSPECTIVE_DIAGNOSTICS_ONLY', 'verified_models':25,
   'verified_auc_values':100, 'folds':folds,'r9_original_side_utc_day_block_bootstrap':monthly,
   'mean_monthly_delta_paired_day_bootstrap':{'mean':float(np.mean(combined)), 'p025':float(np.quantile(combined,.025)), 'p975':float(np.quantile(combined,.975))},
   'method_note':'Within-month paired UTC-day block bootstrap; mean-monthly CI uses synchronized replicate-level bootstrap draws, not pristine OOS inference.'}
 (ROOT/'results'/'model_replay_and_uncertainty.json').write_text(json.dumps(report,indent=2)+'\n')
 print('DONE',json.dumps(report['mean_monthly_delta_paired_day_bootstrap']),flush=True)
 return report

if __name__=='__main__':run()

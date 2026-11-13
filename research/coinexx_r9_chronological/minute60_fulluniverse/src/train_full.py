"""R9 60s *full candidate* chronological research: 5 expanding folds, 3 feature families.

No training on May-Sep future for their own evaluation month. Every original R9
entry with noncensored label is retained. Missing 60s history is retained as
NaNs for boosted trees, with frozen R9 source context; no hindsight filtering.
All score thresholds fixed on prior training months. Never a production EA.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from quant_state import COLS as STATE_COLS

MONTHS=[f'{i:02}' for i in range(1,10)]
BASE_N=14;HFT_N=103;STATE_N=28
FAMILIES={
 'r9_context_14':(14,'conservative'),
 'r9_hft60_117':(117,'conservative'),
 'r9_hft60_state_145':(145,'conservative'),
 'r9_hft60_state_145_capacity':(145,'capacity'),
}
HORIZONS={0:5,1:15,2:30}
FEE=20

def build_model(size):
 if size=='capacity':
  return LGBMClassifier(n_estimators=180,learning_rate=.05,num_leaves=31,max_depth=-1,
   min_child_samples=100,reg_alpha=1.,reg_lambda=15.,colsample_bytree=.86,
   subsample=.85,subsample_freq=1,random_state=20261113,n_jobs=4,verbosity=-1,
   max_bin=63,force_col_wise=True)
 return LGBMClassifier(n_estimators=96,learning_rate=.06,num_leaves=15,max_depth=-1,
  min_child_samples=100,reg_alpha=1.,reg_lambda=12.,colsample_bytree=.9,
  subsample=.85,subsample_freq=1,random_state=20261113,n_jobs=4,verbosity=-1,
  max_bin=63,force_col_wise=True)

def load(directory):
 rows=[];columns=None
 for m in MONTHS:
  p=Path(directory)/f'full_month_2026_{m}.npz';v=np.load(p,allow_pickle=False)
  if columns is None:columns=v['columns'].astype(str).tolist()
  elif columns!=v['columns'].astype(str).tolist():raise ValueError('schema mismatched')
  entry=v['entry_times'];lab=v['labels'];valid=v['valid'];features=v['features']
  if features.shape[1]!=145:raise ValueError('expected 145 feature columns')
  if np.any(~np.isfinite(features[:,:14])) or np.any(~np.isfinite(features[valid])):
   raise ValueError('invalid source base or valid history features')
  if np.any(np.isfinite(features[~valid,14:])):raise ValueError('invalid history not NaN')
  rows.append({'month':m,'feature':features,'label':lab,'valid':valid,'entry':entry,
   'ord':v['entry_ordinals'],'ret':v['terminal_return'],'side':v['side']})
 return rows,columns

def report_scores(y, pred, train_pred,train_y,ret,valid,entries,sessions):
 auc=float(roc_auc_score(y,pred))
 out={'n':int(len(y)),'positive_rate':float(y.mean()),'auc':auc,'ap':float(average_precision_score(y,pred)),
  'brier':float(brier_score_loss(y,np.clip(pred,0,1))),
  'training_base_rate':float(np.mean(train_y)),
  'score_p05_p50_p95':[float(z) for z in np.quantile(pred,[.05,.5,.95])],
  'all_quote_price_ev':float((ret-FEE).mean()/100),
  'full_history_coverage':float(valid.mean()),'history_coverage_count':int(valid.sum()),
  'validation_days':int(np.unique(entries//86400000).size),
  'retained':{},'validity_subgroups':{},'sessions':{},'daily_auc_summary':{}}
 for q in (.50,.80,.95):
  threshold=float(np.quantile(train_pred,q));kept=pred>=threshold
  out['retained'][f'prior_train_q{int(q*100)}']={'threshold':threshold,'count':int(kept.sum()),'fraction':float(kept.mean()),
   'positive_rate':float(y[kept].mean()) if kept.any() else None,
   'quote_ev':float((ret[kept]-FEE).mean()/100) if kept.any() else None}
 for name,mask in [('available',valid),('missing',~valid)]:
  out['validity_subgroups'][name]={'n':int(mask.sum()),'positive_rate':float(y[mask].mean()) if mask.any() else None,
   'auc':float(roc_auc_score(y[mask],pred[mask])) if len(np.unique(y[mask]))>1 else None}
 for ss in sorted(np.unique(sessions)):
  k=sessions==ss
  out['sessions'][str(int(ss))]={'n':int(k.sum()),'positive_rate':float(np.mean(y[k])),
   'auc':float(roc_auc_score(y[k],pred[k])) if len(np.unique(y[k]))>1 else None}
 daily=[]
 for day in np.unique(entries//86400000):
  k=(entries//86400000)==day
  if k.sum()>50 and len(np.unique(y[k]))==2:
   daily.append(float(roc_auc_score(y[k],pred[k])))
 out['daily_auc_summary']={'count_days':len(daily),'median':float(np.median(daily)) if daily else None,
  'p10':float(np.quantile(daily,.1)) if daily else None,
  'p90':float(np.quantile(daily,.9)) if daily else None,
  'fraction_over_0_6':float(np.mean(np.array(daily)>.6)) if daily else None}
 out['owner_gate']='FAIL' if auc<.75 else ('TARGET_MET_RESEARCH_ONLY' if auc>.80 else 'RESEARCH_ONLY')
 return out

def train(rows,columns,out_dir, with_horizon_diag=True):
 out_dir.mkdir(exist_ok=True,parents=True)
 results=[]
 for teix in range(4,9):
  t=time.monotonic(); month=rows[teix]['month']; trainr=rows[:teix];trn=len(trainr)
  trX=np.concatenate([r['feature'][r['label'][:,1]!=-1] for r in trainr])
  trY=np.concatenate([(r['label'][:,1][r['label'][:,1]!=-1]==1).astype(np.int8) for r in trainr])
  trEntry=np.concatenate([r['entry'][r['label'][:,1]!=-1] for r in trainr])
  testing=rows[teix];testmask=testing['label'][:,1]!=-1
  teX=testing['feature'][testmask];teY=(testing['label'][testmask,1]==1).astype(np.int8)
  teRet=testing['ret'][testmask,1];teValid=testing['valid'][testmask];teEntry=testing['entry'][testmask];teSession=teX[:,2]
  # For independent 30s label, decisions in training must predate first test decision by >= 60s.
  if trEntry.max()+60000>=teEntry.min():raise ValueError('purge violation: train overlaps future month')
  receipt={'fold':teix-3,'train_months':[x['month'] for x in trainr], 'evaluation_month':month,
    'train_total':int(len(trY)),'evaluation_total':int(len(teY)), 'all_universe':True,
    'test_censored':int((~testmask).sum()),'family':{}}
  for family,(col_count,capacity) in FAMILIES.items():
   model=build_model(capacity);start=time.monotonic()
   model.fit(trX[:,:col_count],trY)
   p=model.predict_proba(teX[:,:col_count])[:,1];trainp=model.predict_proba(trX[:,:col_count])[:,1]
   st=report_scores(teY,p,trainp,trY,teRet,teValid,teEntry,teSession)
   st['train_auc']=float(roc_auc_score(trY,trainp));st['time_sec']=round(time.monotonic()-start,2)
   st['features']=col_count
   if family=='r9_hft60_state_145_capacity' and teix==8:
    # Held-out posthoc diagnostic only. Not used for model selection.
    gain=np.asarray(model.feature_importances_,int)
    st['feature_gain_top20']=[{'feature':columns[i],'split_count':int(gain[i])}
      for i in np.argsort(gain)[-20:][::-1]]
   receipt['family'][family]=st
   print(f"FOLD {teix-3} eval={month} {family} train={st['train_auc']:.4f} OOS={st['auc']:.4f} "
     f"AP={st['ap']:.4f} train_q50={st['retained']['prior_train_q50']['count']} q50_EV={st['retained']['prior_train_q50']['quote_ev']} ",flush=True)
  receipt['time_sec']=round(time.monotonic()-t,2)
  results.append(receipt)
  (out_dir/f'fold_{teix-3}_2026_{month}.json').write_text(json.dumps(receipt,indent=2)+'\n')
  (out_dir/'five_fold_results.json').write_text(json.dumps({'status':'RESEARCH_SHADOW_ONLY','scope':'entire historical R9 entry universe, 60s past-only context',
   'owner_auc_fail_below':.75,'owner_auc_target_above':.80,'note':'All evaluated months previously exposed in pilot; not pristine future validation',
   'families':FAMILIES,'folds':results},indent=2)+'\n')
  del trX,trY,teX,teY
 # Distinguish target-horizon sensitivity without posthoc best-horizon selection.
 horizon_results=[]
 if with_horizon_diag:
  for horizon_i in (0,2):
   for teix in range(4,9):
    test=rows[teix];tx=test['feature'][test['label'][:,horizon_i]!=-1,:117]
    ty=(test['label'][test['label'][:,horizon_i]!=-1,horizon_i]==1).astype(np.int8)
    x=np.concatenate([r['feature'][r['label'][:,horizon_i]!=-1,:117] for r in rows[:teix]])
    y=np.concatenate([(r['label'][:,horizon_i][r['label'][:,horizon_i]!=-1]==1).astype(np.int8) for r in rows[:teix]])
    m=build_model('conservative');m.fit(x,y); p=m.predict_proba(tx)[:,1]
    val={'horizon_s':HORIZONS[horizon_i],'test_month':test['month'],'train_n':len(y),'test_n':len(ty),
      'base_rate':float(np.mean(ty)),'train_auc':float(roc_auc_score(y,m.predict_proba(x)[:,1])),
      'auc':float(roc_auc_score(ty,p))};horizon_results.append(val)
    print('HORIZON',val,flush=True)
  (out_dir/'horizon_sensitivity.json').write_text(json.dumps({'note':'predeclared diagnostic 5s/30s same 60-second 117 features; all months exposed',
    'results':horizon_results},indent=2)+'\n')
 return results,horizon_results

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--input-dir',type=Path,default=Path('/mnt/data/r9_m60_expanded/full_derived'))
 parser.add_argument('--out-dir',type=Path,default=Path('/mnt/data/r9_m60_expanded/full_results'))
 parser.add_argument('--no-horizons',action='store_true');args=parser.parse_args()
 rows,columns=load(args.input_dir)
 train(rows,columns,args.out_dir,not args.no_horizons)

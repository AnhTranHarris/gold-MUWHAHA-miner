"""Five strictly chronological R9 Priority-1 shadow training passes.

Every pass trains on earlier whole Coinexx source months and scores a distinct
later month; September is touched only by the fifth pass. No SYNTH reports or
future quote labels become input features. PnL is *quote-price* proxy only.

Outputs are shadow rankings, not on-policy trading strategies or MT5 fills.
"""
from __future__ import annotations
import argparse,gzip,hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import RobustScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score,brier_score_loss,log_loss
from extract import BASE_FIELDS,FEATURE_FIELDS

BASE=list(BASE_FIELDS)+['side']
PATH=[k for k in FEATURE_FIELDS if any(u in k for u in ('sig_area','bid_disp','ask_disp','spread_disp','signed_mid','eff','churn'))]
EVENT=[k for k in FEATURE_FIELDS if any(u in k for u in ('_events','_bid_only','_ask_only','_both','_up','_down','intensity','quote_gap_ms','signed_bid_ask_agreement'))]
ALL=BASE+FEATURE_FIELDS
RUNS=[
 {'id':'P1','months':['01','02','03','04'],'check':'05','feature':'baseline','family':'linear','c':0.5},
 {'id':'P2','months':['01','02','03','04','05'],'check':'06','feature':'path','family':'linear','c':0.3},
 {'id':'P3','months':['01','02','03','04','05','06'],'check':'07','feature':'path_events','family':'linear','c':0.2},
 {'id':'P4','months':['01','02','03','04','05','06','07'],'check':'08','feature':'path_events','family':'boosted','max_iter':80},
 {'id':'P5','months':['01','02','03','04','05','06','07','08'],'check':'09','feature':'path_events','family':'boosted','max_iter':120},
]

def colnames(version):
 if version=='baseline':return BASE
 if version=='path':return BASE+PATH
 if version=='path_events':return BASE+PATH+EVENT
 raise ValueError(version)

def create_model(spec):
 if spec['family']=='linear':
  return make_pipeline(SimpleImputer(strategy='median',keep_empty_features=True),
    RobustScaler(quantile_range=(10.0,90.0)),
    LogisticRegression(C=spec['c'],max_iter=1000,solver='lbfgs',tol=1e-4))
 return make_pipeline(SimpleImputer(strategy='median',keep_empty_features=True),
   HistGradientBoostingClassifier(max_iter=spec['max_iter'],learning_rate=.06,
     max_leaf_nodes=12,min_samples_leaf=300,l2_regularization=20.0,
     early_stopping=False,random_state=20261113))

def month_data(folder,month):
 p=folder/f'candidate_closes_2026_{month}.csv.gz'
 if not p.exists():raise FileNotFoundError(p)
 f=pd.read_csv(p,low_memory=False)
 if not len(f): raise ValueError(f'empty candidates for month {month}')
 f['signal_month']=pd.to_datetime(f.entry_time_msc,unit='ms',utc=True).dt.strftime('%m')
 # Trades exiting after month boundary remain in the file where they closed.
 # The label belongs to its *entry* month, not its exit month. All rows retain
 # exact pre-entry features and this is not a reordering of raw source ticks.
 return f

def chronological_evaluation(train:pd.DataFrame,test:pd.DataFrame,probs:np.ndarray,
   train_probs:np.ndarray,fee_u:int,features:list[str]) -> dict:
 y=(test.net_price_u.to_numpy()>fee_u).astype(int)
 train_y=(train.net_price_u.to_numpy()>fee_u).astype(int)
 net=test.net_price_u.to_numpy(dtype=float)-fee_u
 # Threshold computed on training predictions ONLY; no peek at current check.
 threshold=float(np.quantile(train_probs,.5))
 selected=probs>=threshold
 total=len(test)
 byday=pd.to_datetime(test.entry_time_msc,unit='ms',utc=True).dt.strftime('%Y-%m-%d')
 out={
  'raw_trades':total,'train_samples':len(train),'train_positive_fraction':float(train_y.mean()),
  'evaluation_positive_fraction':float(y.mean()),
  'all_quote_price_expectancy_u':float(net.mean()),
  'all_quote_price_sum_u':float(net.sum()),
  'roc_auc':float(roc_auc_score(y,probs)) if len(np.unique(y))>1 else None,
  'brier':float(brier_score_loss(y,probs)),
  'log_loss':float(log_loss(y,np.clip(probs,1e-7,1-1e-7),labels=[0,1])),
  'threshold_train_median':threshold,
  'selected_count':int(selected.sum()),
  'selected_fraction':float(selected.mean()),
  'selected_quote_price_expectancy_u':float(net[selected].mean()) if selected.any() else None,
  'selected_quote_price_sum_u':float(net[selected].sum()),
  'selected_positive_fraction':float(y[selected].mean()) if selected.any() else None,
  'daily_score_span':int(pd.Series(byday).nunique()),
 }
 daily=[]
 for d,idx in pd.Series(np.arange(total)).groupby(byday.to_numpy()):
  inds=idx.to_numpy(dtype=int)
  keep=selected[inds]
  daily.append({'date':d,'baseline_trades':int(len(inds)),
   'selected_trades':int(keep.sum()),
   'baseline_quote_price_net_u':float(net[inds].sum()),
   'selected_quote_price_net_u':float(net[inds][keep].sum())})
 out['daily']=daily
 # Train labels and check labels are for a frozen R9 baseline path; filtering
 # trades would alter later minute rearm and occupancy. Shadow only.
 return out

def main():
 a=argparse.ArgumentParser()
 a.add_argument('--input-dir',type=Path,default=Path('/mnt/data/r9_shadow_path_signatures/outputs'))
 a.add_argument('--output-dir',type=Path,default=Path('/mnt/data/r9_shadow_path_signatures/models'))
 a.add_argument('--price-cost-u',type=int,default=20)
 args=a.parse_args()
 args.output_dir.mkdir(parents=True,exist_ok=True)
 files={}
 results=[]
 for run in RUNS:
  # Lazily open months. September files are not opened or evaluated until P5.
  for m in run['months']+[run['check']]:
   if m not in files:
    files[m]=month_data(args.input_dir,m)
  full=pd.concat(list(files.values()),ignore_index=True)
  full['entry_month_real']=pd.to_datetime(full.entry_time_msc,unit='ms',utc=True).dt.strftime('%m')
  cols=colnames(run['feature'])
  tr=full[full.entry_month_real.isin(run['months'])].copy()
  ck=full[full.entry_month_real==run['check']].copy()
  if not len(tr) or not len(ck):raise RuntimeError('no train/check rows for '+run['id'])
  if any(k not in full.columns for k in cols):raise RuntimeError('missing feature column')
  tr=tr.sort_values('entry_time_msc',kind='stable')
  ck=ck.sort_values('entry_time_msc',kind='stable')
  # Mandatory purge: completed training trades must finish >=60s before
  # the first evaluation decision; no future outcome leaks across a fold.
  boundary=int(ck.entry_time_msc.min())
  tr=tr[tr.exit_time_msc<boundary-60000]
  if tr.entry_time_msc.max()>=ck.entry_time_msc.min():
   raise RuntimeError('train/test chronology collision')
  Xtr=tr[cols].to_numpy(dtype=float)
  Xck=ck[cols].to_numpy(dtype=float)
  y=(tr.net_price_u.to_numpy()>args.price_cost_u).astype(int)
  if len(np.unique(y))<2:raise RuntimeError('single class, cannot train')
  clf=create_model(run)
  clf.fit(Xtr,y)
  p=clf.predict_proba(Xck)[:,1]
  train_p=clf.predict_proba(Xtr)[:,1]
  stats=chronological_evaluation(tr,ck,p,train_p,args.price_cost_u,cols)
  stats['run_id']=run['id']
  stats['train_months']=[f'2026-{m}' for m in run['months']]
  stats['evaluation_month']=f'2026-{run["check"]}'
  stats['feature_family']=run['feature'];stats['model_family']=run['family']
  stats['feature_count']=len(cols)
  stats['cost_per_trade_quoted_price_u']=args.price_cost_u
  model_filename=f'{run["id"]}_shadow_{run["check"]}.joblib'
  model_path=args.output_dir/model_filename
  joblib.dump({'pipeline':clf,'feature_names':cols,
   'trained_months':run['months'],'evaluated_month':run['check'],
   'fee_u':args.price_cost_u,'status':'shadow_only'},model_path,compress=3)
  stats['model_file']=model_filename
  stats['model_sha256']=hashlib.sha256(model_path.read_bytes()).hexdigest()
  (args.output_dir/f'{run["id"]}_receipt.json').write_text(json.dumps(stats,indent=2)+'\n')
  print(f"{run['id']} train={','.join(run['months'])} eval={run['check']} n={len(ck):,} "
    f"AUC={stats['roc_auc']} Brier={stats['brier']:.4f} kept={stats['selected_count']:,} "
    f"all_quoteEV={stats['all_quote_price_expectancy_u']:.2f} "
    f"shadow_keptEV={stats['selected_quote_price_expectancy_u']}",flush=True)
  results.append({k:v for k,v in stats.items() if k!='daily'})
 (args.output_dir/'five_pass_results.json').write_text(json.dumps({
  'classification':'CAUSAL SHADOW RANKING, NOT ON-POLICY EXECUTION',
  'quote_units':'0.01 USD/XAU price, not verified account USD',
  'execution_qualification':'No dealer fill, margin, actual commission, stop-level or slippage parity',
  'September_holdout':'One use only, fifth pass; no Sep tuning',
  'five_passes':results},indent=2)+'\n')
 print('FIVE PASSES COMPLETE',flush=True)

if __name__=='__main__':main()

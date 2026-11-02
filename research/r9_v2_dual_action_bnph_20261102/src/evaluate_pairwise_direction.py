"""Calibrate direct pairwise direction and compare with independent-side baseline."""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
import lightgbm as lgb
import numpy as np
from sklearn.metrics import roc_auc_score
from repaired_training_common import action_labels,raw_action_predict,choose_prior_weight,calibrate_action_probs,apply_action_calibration,fit_iso,apply_iso
from repaired_features import FEATURE_VERSION,REPAIRED_FEATURE_COUNT

def sha256(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for z in iter(lambda:f.read(1<<20),b''):h.update(z)
 return h.hexdigest()

def load_verified(model_dir,name,receipt_name):
 model_dir=Path(model_dir);mp=model_dir/name;rp=model_dir/receipt_name
 if not rp.exists():raise FileNotFoundError(f'missing v5 fit receipt: {rp}')
 receipt=json.loads(rp.read_text())
 if receipt.get('feature_version')!=FEATURE_VERSION or int(receipt.get('feature_count',-1))!=REPAIRED_FEATURE_COUNT:raise ValueError(f'stale/incompatible fit receipt: {rp}')
 if receipt.get('model_sha256')!=sha256(mp):raise ValueError(f'model hash mismatch: {mp}')
 mdl=lgb.Booster(model_file=str(mp))
 if mdl.num_feature()!=REPAIRED_FEATURE_COUNT:raise ValueError(f'model feature mismatch: {mp}')
 return mdl

def load(root,day):
 root=Path(root);base=f'coinexx_01_{day}';return np.load(root/f'{base}_250ms_v5_X.npy',mmap_mode='r'),np.load(root/f'{base}_250ms_universe.npz')

def main(a):
 root=Path(a.root);mdl=load_verified(a.models,'coinexx_01_pairwise_direction_v2.txt','coinexx_01_pairwise_direction_v2_fit.json');buy=load_verified(a.baseline_models,'coinexx_01_250ms_v5_pilot_buy.txt','coinexx_01_250ms_v5_pilot_buy_fit.json');sell=load_verified(a.baseline_models,'coinexx_01_250ms_v5_pilot_sell.txt','coinexx_01_250ms_v5_pilot_sell_fit.json');models=(buy,sell)
 counts=np.zeros((2,3),float)
 for di,day in enumerate(a.fit_days):
  _,d=load(root,day);mask=np.ones(len(d['ts']),bool)
  if di==len(a.fit_days)-1:mask &= d['ts']<d['ts'][-1]-a.embargo_ms
  y=action_labels(d['good'].astype(np.uint8),d['neutral'].astype(np.uint8))[mask]
  for j in (0,1):counts[j]=[(y[:,j]==k).sum() for k in range(3)]
 priors=(counts+1)/(counts.sum(1,keepdims=True)+3)
 Xc,dc=load(root,a.cal_day);ts=dc['ts'];mid=int(ts[len(ts)//2]);ca=(ts>=ts[0]+a.embargo_ms)&(ts<mid-a.embargo_ms);cb=(ts>=mid+a.embargo_ms)&(ts<ts[-1]-a.embargo_ms)
 diff=dc['net'][:,0]-dc['net'][:,1];valid=np.isfinite(diff)&(~np.isclose(diff,0,atol=1e-7));y=(diff>0).astype(np.uint8);iso=fit_iso(mdl.predict(np.asarray(Xc[ca&valid],np.float32),num_threads=2),y[ca&valid])
 yact=action_labels(dc['good'].astype(np.uint8),dc['neutral'].astype(np.uint8));qa=raw_action_predict(models,np.asarray(Xc[ca],np.float32));w,_=choose_prior_weight(qa,yact[ca],priors);_,isos=calibrate_action_probs(qa,yact[ca],priors,w)
 def ev(day,mask):
  X,d=load(root,day);diff=d['net'][:,0]-d['net'][:,1];v=np.isfinite(diff)&(~np.isclose(diff,0,atol=1e-7))&mask;y=(diff>0).astype(np.uint8);p=apply_iso(iso,mdl.predict(np.asarray(X[v],np.float32),num_threads=2));pred=np.where(p>=.5,1,-1);good=d['good'][v].astype(np.uint8);one=good.sum(1)==1;truth=np.where(good[:,0]==1,1,-1);q=apply_action_calibration(raw_action_predict(models,np.asarray(X[v],np.float32)),priors,w,isos);base=np.where(q[:,0,2]>=q[:,1,2],1,-1);conf=(p>=.8)|(p<=.2)
  return dict(events=int(v.sum()),pairwise_net_auc=float(roc_auc_score(y[v],p)),pairwise_net_accuracy=float(np.mean(pred==np.where(y[v]==1,1,-1))),exactly_one_good=int(one.sum()),pairwise_strict_good_direction_accuracy=float(np.mean(pred[one]==truth[one])),independent_side_strict_good_direction_accuracy=float(np.mean(base[one]==truth[one])),high_confidence_n=int(conf.sum()),high_confidence_strict_good_n=int((conf&one).sum()),high_confidence_strict_good_accuracy=(float(np.mean(pred[conf&one]==truth[conf&one])) if (conf&one).any() else None))
 Xh,dh=load(root,a.holdout_day);hold=dh['ts']>=dh['ts'][0]+a.embargo_ms
 r=dict(identity='R9_V2_PAIRWISE_DIRECTION_V2',calibration_B=ev(a.cal_day,cb),holdout=ev(a.holdout_day,hold),prior_weight_for_independent_baseline=float(w),qualified_direction_policy=False,status='PAIRWISE_DIRECTION_DID_NOT_BEAT_INDEPENDENT_SIDE_BASELINE')
 Path(a.out).mkdir(parents=True,exist_ok=True);(Path(a.out)/'coinexx_01_pairwise_direction_v2_evaluation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--models',required=True);p.add_argument('--baseline-models',required=True);p.add_argument('--out',required=True);p.add_argument('--fit-days',nargs='+',default=['2026-01-06','2026-01-07']);p.add_argument('--cal-day',default='2026-01-08');p.add_argument('--holdout-day',default='2026-01-13');p.add_argument('--embargo-ms',type=int,default=60000);main(p.parse_args())

"""Compare base WAIT timing vs fitted-excitation augmentation on a frozen holdout."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import lightgbm as lgb
import numpy as np
from sklearn.metrics import roc_auc_score
from repaired_training_common import fit_iso,apply_iso
from decision import calibrate_binary_np
from timing_transition_features import wait_improves_target

def calibrate(model,X,d,embargo_ms):
 y,_=wait_improves_target(d,1000);ts=d['ts'];mid=int(ts[len(ts)//2]);ca=(ts>=ts[0]+embargo_ms)&(ts<mid-embargo_ms);cb=(ts>=mid+embargo_ms)&(ts<ts[-1]-embargo_ms)
 iso=fit_iso(model.predict(np.asarray(X[ca],np.float32),num_threads=2),y[ca]);p=apply_iso(iso,model.predict(np.asarray(X[cb],np.float32),num_threads=2));cut,info=calibrate_binary_np(p,y[cb].astype(bool),alpha=.10,min_bad=150);return iso,cut,float(roc_auc_score(y[cb],p))

def main(a):
 teacher=Path(a.teacher);base=Path(a.base_features);aug=Path(a.aug_features);bm=lgb.Booster(model_file=a.base_model);am=lgb.Booster(model_file=a.aug_model)
 d8=np.load(teacher/f'coinexx_01_{a.cal_day}_250ms_universe.npz');Xb8=np.load(base/f'coinexx_01_{a.cal_day}_wait_transition_X.npy',mmap_mode='r');Xa8=np.load(aug/f'coinexx_01_{a.cal_day}_wait_transition_hawkes_X.npy',mmap_mode='r');bi,bc,bcal=calibrate(bm,Xb8,d8,a.embargo_ms);ai,ac,acal=calibrate(am,Xa8,d8,a.embargo_ms)
 dh=np.load(teacher/f'coinexx_01_{a.holdout_day}_250ms_universe.npz');y,_=wait_improves_target(dh,1000);m=dh['ts']>=dh['ts'][0]+a.embargo_ms;Xb=np.load(base/f'coinexx_01_{a.holdout_day}_wait_transition_X.npy',mmap_mode='r');Xa=np.load(aug/f'coinexx_01_{a.holdout_day}_wait_transition_hawkes_X.npy',mmap_mode='r');pb=apply_iso(bi,bm.predict(np.asarray(Xb[m],np.float32),num_threads=2));pa=apply_iso(ai,am.predict(np.asarray(Xa[m],np.float32),num_threads=2));yy=y[m].astype(bool)
 def st(p,cut,cal):
  s=(p>=.8)&(p>cut);return dict(calibration_B_auc=cal,holdout_auc=float(roc_auc_score(yy,p)),cutoff=float(cut),selected=int(s.sum()),precision=(float(yy[s].mean()) if s.any() else None),p_max=float(p.max()))
 r=dict(identity='R9_V2_WAIT_FITTED_EXCITATION_INCREMENTAL_V1',base=st(pb,bc,bcal),augmented=st(pa,ac,acal),events=int(m.sum()),positives=int(yy.sum()));r['auc_delta']=r['augmented']['holdout_auc']-r['base']['holdout_auc']
 block=dh['ts'][m]//300000;u=np.unique(block);inds=[np.where(block==x)[0] for x in u];rng=np.random.default_rng(601);delta=[]
 for _ in range(a.bootstrap):
  sel=rng.integers(0,len(inds),len(inds));ix=np.concatenate([inds[i] for i in sel]);yq=yy[ix]
  if yq.min()==yq.max():continue
  delta.append(roc_auc_score(yq,pa[ix])-roc_auc_score(yq,pb[ix]))
 q=np.quantile(delta,[.025,.5,.975]);r['block_bootstrap']=dict(block_ms=300000,blocks=len(u),replicates=len(delta),mean=float(np.mean(delta)),median=float(q[1]),ci95=[float(q[0]),float(q[2])],positive_fraction=float(np.mean(np.asarray(delta)>0)))
 r['admit_fitted_excitation_as_research_feature']=bool(q[0]>0);r['qualified_timing_policy']=False;r['status']='INCREMENTAL_FEATURE_GAIN_WITHOUT_80PCT_GATE' if q[0]>0 else 'NO_INCREMENTAL_FEATURE_GAIN'
 Path(a.out).mkdir(parents=True,exist_ok=True);(Path(a.out)/'coinexx_01_wait_fitted_excitation_incremental.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--teacher',required=True);p.add_argument('--base-features',required=True);p.add_argument('--aug-features',required=True);p.add_argument('--base-model',required=True);p.add_argument('--aug-model',required=True);p.add_argument('--out',required=True);p.add_argument('--cal-day',default='2026-01-08');p.add_argument('--holdout-day',default='2026-01-15');p.add_argument('--embargo-ms',type=int,default=60000);p.add_argument('--bootstrap',type=int,default=200);main(p.parse_args())

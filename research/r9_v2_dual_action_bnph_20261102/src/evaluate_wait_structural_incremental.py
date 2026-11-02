"""Compare fitted-excitation WAIT baseline with full rolling-5m structural augmentation."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import lightgbm as lgb
import numpy as np
from sklearn.metrics import roc_auc_score
from repaired_training_common import fit_iso,apply_iso
from decision import calibrate_binary_np
from timing_transition_features import wait_improves_target
from structural_5m_features import STRUCTURAL_5M_NAMES

def calibrate(model,X,d,embargo_ms):
 y,_=wait_improves_target(d,1000);ts=d['ts'];mid=int(ts[len(ts)//2]);ca=(ts>=ts[0]+embargo_ms)&(ts<mid-embargo_ms);cb=(ts>=mid+embargo_ms)&(ts<ts[-1]-embargo_ms)
 iso=fit_iso(model.predict(np.asarray(X[ca],np.float32),num_threads=2),y[ca]);p=apply_iso(iso,model.predict(np.asarray(X[cb],np.float32),num_threads=2));cut,_=calibrate_binary_np(p,y[cb].astype(bool),alpha=.10,min_bad=150)
 return iso,cut,float(roc_auc_score(y[cb],p)),float(p.max())

def main(a):
 teacher=Path(a.teacher);base=Path(a.base_features);struct=Path(a.struct_features);bm=lgb.Booster(model_file=a.base_model);sm=lgb.Booster(model_file=a.struct_model)
 d8=np.load(teacher/f'coinexx_01_{a.cal_day}_250ms_universe.npz');Xb8=np.load(base/f'coinexx_01_{a.cal_day}_wait_transition_hawkes_X.npy',mmap_mode='r');Xs8=np.load(struct/f'coinexx_01_{a.cal_day}_wait_structural_X.npy',mmap_mode='r');bi,bc,bcal,bp=calibrate(bm,Xb8,d8,a.embargo_ms);si,sc,scal,sp=calibrate(sm,Xs8,d8,a.embargo_ms)
 d=np.load(teacher/f'coinexx_01_{a.holdout_day}_250ms_universe.npz');y,_=wait_improves_target(d,1000);m=d['ts']>=d['ts'][0]+a.embargo_ms;yy=y[m].astype(bool);Xb=np.load(base/f'coinexx_01_{a.holdout_day}_wait_transition_hawkes_X.npy',mmap_mode='r');Xs=np.load(struct/f'coinexx_01_{a.holdout_day}_wait_structural_X.npy',mmap_mode='r');pb=apply_iso(bi,bm.predict(np.asarray(Xb[m],np.float32),num_threads=2));ps=apply_iso(si,sm.predict(np.asarray(Xs[m],np.float32),num_threads=2));ab=float(roc_auc_score(yy,pb));ast=float(roc_auc_score(yy,ps))
 block=d['ts'][m]//300000;u=np.unique(block);inds=[np.where(block==x)[0] for x in u];rng=np.random.default_rng(602);delta=[]
 for _ in range(a.bootstrap):
  ix=np.concatenate([inds[i] for i in rng.integers(0,len(inds),len(inds))]);q=yy[ix]
  if q.min()==q.max():continue
  delta.append(roc_auc_score(q,ps[ix])-roc_auc_score(q,pb[ix]))
 q=np.quantile(delta,[.025,.5,.975]);gain=sm.feature_importance(importance_type='gain');offset=sm.num_feature()-len(STRUCTURAL_5M_NAMES);top=[]
 for i in np.argsort(gain[offset:])[::-1][:20]:top.append(dict(name=STRUCTURAL_5M_NAMES[int(i)],gain=float(gain[offset+i])))
 r=dict(identity='R9_V2_FULL5M_STRUCTURAL_INCREMENTAL_V1',calibration_B=dict(base_auc=bcal,structural_auc=scal,delta=scal-bcal,base_pmax=bp,structural_pmax=sp),holdout=dict(day=a.holdout_day,events=int(m.sum()),positives=int(yy.sum()),base_auc=ab,structural_auc=ast,delta=ast-ab,base_selected_p80=int(((pb>=.8)&(pb>bc)).sum()),structural_selected_p80=int(((ps>=.8)&(ps>sc)).sum()),structural_pmax=float(ps.max())),block_bootstrap=dict(block_ms=300000,blocks=len(u),replicates=len(delta),mean=float(np.mean(delta)),median=float(q[1]),ci95=[float(q[0]),float(q[2])],positive_fraction=float(np.mean(np.asarray(delta)>0))),top_structural_features=top,admit_full5m_structural_feature=bool(q[0]>0 and ast>ab),qualified_timing_policy=False)
 r['status']='ADMIT_RESEARCH_FEATURE_ONLY_NO_POLICY' if r['admit_full5m_structural_feature'] else 'REJECT_FULL5M_STRUCTURAL_V1';Path(a.out).mkdir(parents=True,exist_ok=True);(Path(a.out)/'coinexx_01_full5m_structural_incremental.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--teacher',required=True);p.add_argument('--base-features',required=True);p.add_argument('--struct-features',required=True);p.add_argument('--base-model',required=True);p.add_argument('--struct-model',required=True);p.add_argument('--out',required=True);p.add_argument('--cal-day',default='2026-01-08');p.add_argument('--holdout-day',default='2026-01-16');p.add_argument('--embargo-ms',type=int,default=60000);p.add_argument('--bootstrap',type=int,default=200);main(p.parse_args())
"""Calibrate and verify side-specific R9 realized exit-value models."""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import lightgbm as lgb
import numpy as np

def segment(mm,qm,X,d,mask,j,norm):
 pm=mm.predict(np.asarray(X[mask],np.float32),num_threads=2);pq=qm.predict(np.asarray(X[mask],np.float32),num_threads=2)
 mmu,msd,qmu,qsd=norm;score=.7*(pm-mmu)/msd+.3*(pq-qmu)/qsd;net=d['net'][mask,j].astype(float);order=np.argsort(score)[::-1]
 out=dict(events=len(net),pred_mean_max=float(pm.max()),pred_q20_max=float(pq.max()),all_pred_mean_negative=bool(np.all(pm<0)),all_pred_q20_negative=bool(np.all(pq<0)),overall_mean=float(net.mean()),overall_positive_rate=float((net>0).mean()))
 for frac in (.001,.005,.01,.05):
  n=max(150,int(len(net)*frac));v=net[order[:n]];mean=float(v.mean());lcb=mean-1.64*float(v.std(ddof=1))/math.sqrt(n)
  out[f'top_{frac:.3f}']=dict(n=n,positive_rate=float((v>0).mean()),mean_net=mean,mean_lcb=lcb,q20=float(np.quantile(v,.2)))
 return out

def main(a):
 root=Path(a.root);mod=Path(a.models);Xc=np.load(root/f'coinexx_01_{a.cal_day}_250ms_v5_X.npy',mmap_mode='r');dc=np.load(root/f'coinexx_01_{a.cal_day}_250ms_universe.npz');ts=dc['ts'];mid=int(ts[len(ts)//2]);ca=(ts>=ts[0]+a.embargo_ms)&(ts<mid-a.embargo_ms);cb=(ts>=mid+a.embargo_ms)&(ts<ts[-1]-a.embargo_ms)
 Xh=np.load(root/f'coinexx_01_{a.holdout_day}_250ms_v5_X.npy',mmap_mode='r');dh=np.load(root/f'coinexx_01_{a.holdout_day}_250ms_universe.npz');hold=dh['ts']>=dh['ts'][0]+a.embargo_ms
 sides={};qualified=False
 for j,side in enumerate(('buy','sell')):
  mm=lgb.Booster(model_file=str(mod/f'coinexx_01_exit_value_{side}_mean.txt'));qm=lgb.Booster(model_file=str(mod/f'coinexx_01_exit_value_{side}_q20.txt'))
  pma=mm.predict(np.asarray(Xc[ca],np.float32),num_threads=2);pqa=qm.predict(np.asarray(Xc[ca],np.float32),num_threads=2);norm=(float(pma.mean()),float(pma.std()+1e-12),float(pqa.mean()),float(pqa.std()+1e-12))
  score=.7*(pma-norm[0])/norm[1]+.3*(pqa-norm[2])/norm[3];net=dc['net'][ca,j].astype(float);order=np.argsort(score)[::-1];best=None
  for n in np.unique(np.clip(np.geomspace(150,len(order),220).astype(int),150,len(order))):
   v=net[order[:n]];pos=float((v>0).mean());mean=float(v.mean());lcb=mean-1.64*float(v.std(ddof=1))/math.sqrt(n);q20=float(np.quantile(v,.2))
   if pos>=.80 and lcb>0 and q20>0:best=dict(n=int(n),positive_rate=pos,mean_net=mean,mean_lcb=lcb,q20=q20,score_threshold=float(score[order[n-1]]));qualified=True
  sides[side]=dict(calibration_A_qualifying_region=best,calibration_B=segment(mm,qm,Xc,dc,cb,j,norm),holdout=segment(mm,qm,Xh,dh,hold,j,norm))
 r=dict(identity='R9_V2_EXIT_VALUE_V1',fit_days=a.fit_days,calibration_day=a.cal_day,holdout_day=a.holdout_day,calibration_qualifying_region=qualified,sides=sides,qualified_value_policy=False,status='NO_POSITIVE_CONSERVATIVE_EXIT_VALUE_REGION')
 p=Path(a.out)/'coinexx_01_exit_value_evaluation.json';p.write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--models',required=True);p.add_argument('--out',required=True);p.add_argument('--fit-days',nargs='+',default=['2026-01-06','2026-01-07']);p.add_argument('--cal-day',default='2026-01-08');p.add_argument('--holdout-day',default='2026-01-12');p.add_argument('--embargo-ms',type=int,default=60000);main(p.parse_args())

"""Freeze Jan8 calibration and evaluate direct WAIT-improvement on untouched Jan9."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import lightgbm as lgb
import numpy as np
from sklearn.metrics import roc_auc_score,brier_score_loss,log_loss
from repaired_training_common import fit_iso,apply_iso
from decision import calibrate_binary_np
from timing_transition_features import wait_improves_target,TIMING_FEATURE_NAMES,TIMING_FEATURE_VERSION

def load(features,teacher,day,max_wait):
 X=np.load(Path(features)/f'coinexx_01_{day}_wait_transition_X.npy',mmap_mode='r');d=np.load(Path(teacher)/f'coinexx_01_{day}_250ms_universe.npz');y,_=wait_improves_target(d,max_wait);return X,d,y

def stats(y,p,cut):
 y=np.asarray(y,bool);p=np.asarray(p,float);out=dict(events=len(y),positive=int(y.sum()),positive_rate=float(y.mean()),auc=float(roc_auc_score(y,p)),brier=float(brier_score_loss(y,p)),logloss=float(log_loss(y,p,labels=[0,1])))
 s=(p>=.8)&(p>cut);n=int(s.sum());c=int(y[s].sum()) if n else 0;out['strict_gate']=dict(cutoff=float(cut),selected=n,precision=(c/n if n else None),capture=(c/y.sum() if y.sum() else None));return out

def main(a):
 mdl=lgb.Booster(model_file=str(Path(a.models)/'coinexx_01_wait_transition_v1.txt'))
 Xc,dc,yc=load(a.features,a.teacher,a.cal_day,a.max_wait_ms);ts=dc['ts'];mid=int(ts[len(ts)//2]);ca=(ts>=ts[0]+a.embargo_ms)&(ts<mid-a.embargo_ms);cb=(ts>=mid+a.embargo_ms)&(ts<ts[-1]-a.embargo_ms)
 iso=fit_iso(mdl.predict(np.asarray(Xc[ca],np.float32),num_threads=2),yc[ca]);pb=apply_iso(iso,mdl.predict(np.asarray(Xc[cb],np.float32),num_threads=2));cut,info=calibrate_binary_np(pb,yc[cb].astype(bool),alpha=a.alpha,min_bad=150)
 Xh,dh,yh=load(a.features,a.teacher,a.check_day,a.max_wait_ms);chk=dh['ts']>=dh['ts'][0]+a.embargo_ms;ph=apply_iso(iso,mdl.predict(np.asarray(Xh[chk],np.float32),num_threads=2))
 gain=mdl.feature_importance(importance_type='gain');ii=np.argsort(gain)[::-1][:30]
 r=dict(identity='R9_V2_WAIT_TRANSITION_V1',version=TIMING_FEATURE_VERSION,calibration_A_rows=int(ca.sum()),calibration_B_rows=int(cb.sum()),np_cutoff=float(cut),np_info=info,
        calibration_B=stats(yc[cb],pb,cut),check=stats(yh[chk],ph,cut),baseline_old_conditional_wait_direct_target_check_auc=a.baseline_auc,
        top_features=[dict(name=TIMING_FEATURE_NAMES[int(i)],gain=float(gain[i])) for i in ii],qualified_timing_policy=False,status='RESEARCH_ONLY_NO_80PCT_WAIT_GATE')
 p=Path(a.out)/'coinexx_01_wait_transition_v1_evaluation.json';p.write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--features',required=True);p.add_argument('--teacher',required=True);p.add_argument('--models',required=True);p.add_argument('--out',required=True);p.add_argument('--cal-day',default='2026-01-08');p.add_argument('--check-day',default='2026-01-09');p.add_argument('--embargo-ms',type=int,default=60000);p.add_argument('--max-wait-ms',type=int,default=1000);p.add_argument('--alpha',type=float,default=.10);p.add_argument('--baseline-auc',type=float,default=.5707709766430428);main(p.parse_args())

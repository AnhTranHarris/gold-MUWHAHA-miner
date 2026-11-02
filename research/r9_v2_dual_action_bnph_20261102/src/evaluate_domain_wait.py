"""Chronological calibration/holdout evaluator for source-agnostic direct WAIT model."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import lightgbm as lgb
import numpy as np
from sklearn.metrics import roc_auc_score,brier_score_loss,log_loss
from repaired_training_common import fit_iso,apply_iso
from decision import calibrate_binary_np
from timing_transition_features import wait_improves_target
from path_config import artifact_stem

def load(root,source,month,day):
 stem=artifact_stem(source,month,day);return np.load(Path(root)/f'{stem}_wait_transition_X.npy',mmap_mode='r'),np.load(Path(root)/f'{stem}_250ms_universe.npz')
def stats(y,p,cut):
 y=np.asarray(y,bool);p=np.asarray(p,float);s=(p>=.8)&(p>cut);n=int(s.sum());return dict(events=len(y),positive=int(y.sum()),positive_rate=float(y.mean()),auc=float(roc_auc_score(y,p)),brier=float(brier_score_loss(y,p)),logloss=float(log_loss(y,p,labels=[0,1])),pmax=float(p.max()),selected_p80=n,precision_p80=(float(y[s].mean()) if n else None))
def main(a):
 source=a.source.lower();month=str(a.month).zfill(2);mdl=lgb.Booster(model_file=str(Path(a.models)/f'{source}_{month}_wait_transition_domain_v2.txt'));Xc,dc=load(a.root,source,month,a.cal_day);yc,_=wait_improves_target(dc,a.max_wait_ms);ts=dc['ts'];mid=int(ts[len(ts)//2]);ca=(ts>=ts[0]+a.embargo_ms)&(ts<mid-a.embargo_ms);cb=(ts>=mid+a.embargo_ms)&(ts<ts[-1]-a.embargo_ms);iso=fit_iso(mdl.predict(np.asarray(Xc[ca],np.float32),num_threads=2),yc[ca]);pb=apply_iso(iso,mdl.predict(np.asarray(Xc[cb],np.float32),num_threads=2));cut,info=calibrate_binary_np(pb,yc[cb].astype(bool),alpha=.10,min_bad=150);Xh,dh=load(a.root,source,month,a.holdout_day);yh,_=wait_improves_target(dh,a.max_wait_ms);m=dh['ts']>=dh['ts'][0]+a.embargo_ms;ph=apply_iso(iso,mdl.predict(np.asarray(Xh[m],np.float32),num_threads=2));r=dict(identity='R9_V2_DOMAIN_WAIT_TRANSITION_V2_EVALUATION',source=source,month=month,calibration_day=a.cal_day,holdout_day=a.holdout_day,np_cutoff=float(cut),np_info=info,calibration_B=stats(yc[cb],pb,cut),holdout=stats(yh[m],ph,cut),qualified_timing_policy=False,status='DOMAIN_RESEARCH_NO_POLICY');Path(a.out).mkdir(parents=True,exist_ok=True);(Path(a.out)/f'{source}_{month}_wait_transition_domain_v2_evaluation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',choices=('coinexx','dukascopy'),required=True);p.add_argument('--month',required=True);p.add_argument('--root',required=True);p.add_argument('--models',required=True);p.add_argument('--out',required=True);p.add_argument('--cal-day',required=True);p.add_argument('--holdout-day',required=True);p.add_argument('--embargo-ms',type=int,default=60000);p.add_argument('--max-wait-ms',type=int,default=1000);main(p.parse_args())
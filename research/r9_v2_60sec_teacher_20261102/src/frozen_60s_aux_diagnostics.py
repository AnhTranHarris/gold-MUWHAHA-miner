#!/usr/bin/env python3
"""Heldout causal accuracy of the 5-30s hindsight-derived auxiliary student.
Capacity chosen by EARLIER calibration AUC only. No check optimization; no
claim that late future oracle action is executable by currently <=3s WAIT.
"""
import json
from pathlib import Path
import numpy as np,lightgbm as lgb
from sklearn.metrics import roc_auc_score
from train_60s_reachable import load,chronological_partition
ROOT=Path('/mnt/data/v2_new_research/sixty')

def run(s,m):
 folder=ROOT/'models_60s_aux'/f'{s}_{m}'
 raw=json.loads((folder/'FOLD_60S_AUX.json').read_text())
 trials=[x for x in raw['calibration_trials'] if x['late_penalty']==0.0]
 # Selection is based on training-period CALIBRATION AUC, NOT heldout labels.
 best=max(trials,key=lambda x:x['cal_late_auc'] if x['cal_late_auc'] is not None else -.1)
 i=best['capacity_idx'];v=load(s,m,ROOT);_,cal,chk,_=chronological_partition(v['entry_utc_ms'])
 model=lgb.Booster(model_file=str(folder/f'future_60s_{i}.txt'))
 pred_cal=model.predict(v['X'][cal]);pred_chk=model.predict(v['X'][chk]);y_cal=v['teacher_60s_later_rescue'][cal];y_chk=v['teacher_60s_later_rescue'][chk]
 threshold=float(np.quantile(pred_cal,.85));chosen=pred_chk>threshold
 outcome={'source':s,'month':m,'chosen_capacity_cal_only':i,
  'calibration_late_auc':best['cal_late_auc'],
  'heldout_late_auc':float(roc_auc_score(y_chk,pred_chk)) if 0<y_chk.sum()<len(y_chk) else None,
  'heldout_base_rate':float(y_chk.mean()),
  'heldout_q85_retro_selected':int(chosen.sum()),
  'heldout_q85_late_precision':float(y_chk[chosen].mean()) if chosen.any() else None,
  'earlier_calibration_q85_threshold':threshold,
  'future_at_runtime':False,'on_policy':False,
  'meaning':'auxiliary prediction of 5-30s future same-side rescue, not proof of later executable entry or R9 profit'}
 (folder/'FROZEN_HELDOUT_60S_DIAGNOSTIC.json').write_text(json.dumps(outcome,indent=2))
 print(s,m,'late_AUC',outcome['heldout_late_auc'],'precision',outcome['heldout_q85_late_precision'],'baseline',outcome['heldout_base_rate'])
 return outcome

if __name__=='__main__':
 for s in ('coinexx','dukascopy'):
  for m in ('01','02','06','07'):run(s,m)

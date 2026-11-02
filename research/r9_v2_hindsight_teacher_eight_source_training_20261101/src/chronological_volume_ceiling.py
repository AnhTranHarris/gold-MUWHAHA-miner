#!/usr/bin/env python3
"""Held-out score ranking diagnostic at prorated 85% R9 volume demand.
EX POST threshold over check cohort is a diagnostic of rank, NOT tradeable.
"""
import argparse,json,math
from pathlib import Path
import numpy as np,lightgbm as lgb
from sklearn.metrics import roc_auc_score,average_precision_score
ROOT=Path('/mnt/data/r9_v2_eight_source_training_20261101');SYNTH={'01':27980,'02':33523,'06':31801,'07':24382}
DATES={'01':20260119,'02':20260218,'06':20260617,'07':20260717}
def load(s,m,k):return np.load(ROOT/'checkpoints'/f'{s}_{m}_{k}.npy',mmap_mode='r')
def run(s,m):
 model=lgb.Booster(model_file=str(ROOT/'checkpoints'/f'{s}_{m}_chrono_fitted.txt'))
 X=load(s,m,'X');dates=load(s,m,'date');y=load(s,m,'win');net=load(s,m,'net')
 mask=dates>DATES[m];yy=np.asarray(y[mask]);N=len(yy)
 scores=model.predict(np.asarray(X[mask],dtype=np.float32),num_threads=4)
 quota_rate=math.ceil(.85*SYNTH[m])/len(y);K=max(1,int(math.ceil(N*quota_rate)))
 top=np.argpartition(scores,-K)[-K:]
 winners=int(yy[top].sum());pnl=float(np.sum(net[mask][top],dtype=np.float64))
 metrics={'source':s,'month':m,'evaluation_rows':N,'baseline_positive_rate':round(float(yy.mean()),6),
  'auc':round(float(roc_auc_score(yy,scores)),6),'average_precision':round(float(average_precision_score(yy,scores)),6),
  'full_month_synth_85pct_floor':int(math.ceil(.85*SYNTH[m])),'requested_quota_share_of_baseline':round(quota_rate,6),
  'heldout_check_prorated_quota':K,'best_score_rank_topK_wins':winners,
  'score_rank_topK_survival_rate':round(winners/K,6),'score_rank_topK_net':round(pnl,2),
  'requires_80pct':True,'80pct_pass':winners/K>=.8,
  'disclaimer':'Model fit on earlier dates; top-K threshold selected ex post on check rows. Diagnostic only; no new trade replay.'}
 (ROOT/'results'/f'{s}_{m}_heldout_volume_ranking.json').write_text(json.dumps(metrics,indent=2))
 print(s,m,metrics,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--month',required=True);a=p.parse_args();run(a.source,a.month)

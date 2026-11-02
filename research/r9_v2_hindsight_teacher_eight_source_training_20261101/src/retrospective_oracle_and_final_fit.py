#!/usr/bin/env python3
"""Hindsight-only capacity proof and final in-sample student fits across full source-months.

The oracle knows future outcomes and is NEVER a runtime feature. Its positive
potential is an upper bound on a fixed observed candidate stream, not a
replayable trading policy or proof of economic transfer.
"""
import argparse,json,time,math
from pathlib import Path
import numpy as np,lightgbm as lgb
ROOT=Path('/mnt/data/r9_v2_eight_source_training_20261101');MONTHS=('01','02','06','07')
SYNTH={'01':27980,'02':33523,'06':31801,'07':24382}
def arr(src,m,k):return np.load(ROOT/'checkpoints'/f'{src}_{m}_{k}.npy',mmap_mode='r')
def oracle(src):
 r={};rows=0
 for m in MONTHS:
  y=arr(src,m,'win');net=arr(src,m,'net');dates=arr(src,m,'date');weeks=arr(src,m,'week')
  s=y.astype(bool);n=int(s.sum());floor=math.ceil(.85*SYNTH[m]);byday={}
  for d in np.unique(dates):
   ix=dates==d;selected=int((s&ix).sum());byday[str(d)]={'trades':selected,'survival':1.0 if selected else None,'pass':bool(selected)}
  byweek={}
  for w in np.unique(weeks):
   ix=weeks==w;selected=int((s&ix).sum());byweek[str(w)]={'trades':selected,'survival':1.0 if selected else None,'pass':bool(selected)}
  r[m]={'candidate_count':len(y),'perfect_hindsight_available_survivors':n,
     'monthly_floor':floor,'monthly_floor_feasible':n>=floor,
     'oracle_winner_only_pnl':round(float(np.sum(net[s],dtype=np.float64)),2),
     'daily_pass':sum(v['pass'] for v in byday.values()),'daily_total':len(byday),
     'weekly_pass':sum(v['pass'] for v in byweek.values()),'weekly_total':len(byweek),
     'daily':byday,'weekly':byweek}
  rows+=len(y)
 (ROOT/'results'/f'{src}_hindsight_oracle_ceiling.json').write_text(json.dumps({'source':src,'status':'HINDSIGHT_ONLY_NON_DEPLOYABLE','months':r,'total_rows':rows},indent=2))
 for m,v in r.items():print('ORACLE',src,m,'winners',v['perfect_hindsight_available_survivors'],'floor',v['monthly_floor'],'days',v['daily_pass'],'/',v['daily_total'],flush=True)
def final_fit(src):
 X=np.concatenate([np.asarray(arr(src,m,'X')) for m in MONTHS],axis=0)
 Y=np.concatenate([np.asarray(arr(src,m,'win')) for m in MONTHS])
 T=np.concatenate([np.asarray(arr(src,m,'teacher')) for m in MONTHS])
 W=np.ones(len(Y),np.float32);W[(Y>0)&(T>0)]=1.05
 model=lgb.train({'objective':'binary','metric':'binary_logloss','num_leaves':27,'max_depth':7,'learning_rate':.055,
     'min_data_in_leaf':180,'feature_fraction':.82,'lambda_l2':10.,'num_threads':4,'verbosity':-1,
     'seed':20261101,'deterministic':True,'force_col_wise':True},
     lgb.Dataset(X,label=Y,weight=W),num_boost_round=105)
 path=ROOT/'checkpoints'/f'{src}_full_4month_teacher_guided_IN_SAMPLE.txt';model.save_model(str(path))
 meta=json.loads((ROOT/'checkpoints'/f'{src}_01_mmap.json').read_text())
 score={'source':src,'role':'FINAL IN-SAMPLE TRAINED STUDENT; NOT VALIDATED OR DEPLOYABLE',
  'months':list(MONTHS),'n':len(Y),'positive':int(Y.sum()),'teacher_marked_training':int(T.sum()),
  'runtime_teacher_feature':False,'teacher_weight_positive_only':.05,'feature_count':X.shape[1],
  'feature_names':meta['features'],'model_path':path.name}
 (ROOT/'results'/f'{src}_final_full_sample_model_receipt.json').write_text(json.dumps(score,indent=2))
 print('FINAL_FIT',src,len(Y), 'features',X.shape[1],path.name,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--only',choices=['oracle','fit','both'],default='both');a=p.parse_args()
 if a.only in ('oracle','both'):oracle(a.source)
 if a.only in ('fit','both'):final_fit(a.source)

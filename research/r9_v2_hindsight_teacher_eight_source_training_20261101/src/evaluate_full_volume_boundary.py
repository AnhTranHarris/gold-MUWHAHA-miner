#!/usr/bin/env python3
"""Grade entire eight months at mandatory 85% SYNTH volume, not a low-trade threshold.
This is explicitly optimistic IN-SAMPLE ranking and BASELINE-CANDIDATE SUBSET only.
Not a fresh filtered trading replay, no out-of-sample claim.
"""
import argparse,math,json
from pathlib import Path
import numpy as np,lightgbm as lgb
ROOT=Path('/mnt/data/r9_v2_eight_source_training_20261101');MON=('01','02','06','07')
SYNTH={'01':27980,'02':33523,'06':31801,'07':24382}
def a(src,m,k):return np.load(ROOT/'checkpoints'/f'{src}_{m}_{k}.npy',mmap_mode='r')
def evaluate(src):
 model=lgb.Booster(model_file=str(ROOT/'checkpoints'/f'{src}_full_4month_teacher_guided_IN_SAMPLE.txt'))
 result={}
 for m in MON:
  X=a(src,m,'X');y=a(src,m,'win');net=a(src,m,'net');ds=a(src,m,'date');w=a(src,m,'week');neutral=a(src,m,'neutral')
  score=model.predict(np.asarray(X),num_threads=4)
  floor=math.ceil(.85*SYNTH[m]);top=np.argpartition(score,-floor)[-floor:];sel=np.zeros(len(score),dtype=bool);sel[top]=True
  wins=int(y[sel].sum());pnl=float(np.sum(net[sel],dtype=np.float64));wr=wins/floor
  byday={};byweek={}
  for field,vals,bucket in [('day',ds,byday),('week',w,byweek)]:
   for v in np.unique(vals):
    ix=sel&(vals==v);n=int(ix.sum());good=int(y[ix].sum());bucket[str(int(v))]={'trades':n,'win30':good,'rate':good/n if n else None,'pass_80pct':bool(n>0 and good/n>=.8)}
  result[m]={'source':src,'month':m,'status':'OPTIMISTIC_IN_SAMPLE_SCORE_UPPER_BOUND_NON_EXECUTABLE',
     'base_candidate_count':len(y),'quota_trades':floor,'30s_survivors':wins,'30s_survival_rate':round(wr,6),
     'net':round(pnl,2),'mean_score_selected':round(float(np.mean(score[sel])),6),
     'selected_neutral':int(neutral[sel].sum()),
     'days_passing_80':sum(v['pass_80pct'] for v in byday.values()),'total_days':len(byday),
     'weeks_passing_80':sum(v['pass_80pct'] for v in byweek.values()),'total_weeks':len(byweek),
     'daily':byday,'weekly':byweek}
  print('IN_SAMPLE_QUOTA',src,m,'count',floor,'survival',round(wr,4),'net',round(pnl,2),'days',result[m]['days_passing_80'],'/',result[m]['total_days'],flush=True)
 (ROOT/'results'/f'{src}_in_sample_full_volume_boundary.json').write_text(json.dumps(result,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);a0=p.parse_args();evaluate(a0.source)

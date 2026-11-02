#!/usr/bin/env python3
"""OFF-POLICY held-out diagnostic under calibration-only q=.85 threshold.
Never identify it as completed v2 on-policy trades or policy approval.
"""
from pathlib import Path
import json,datetime as dt
import lightgbm as lgb,numpy as np
from train_60s import load,chronological_partition,SYNTH,MONS
ROOT=Path('/mnt/data/v2_new_research/sixty')

def record(source,month):
 root=ROOT/'models'/f'{source}_{month}';rec=json.loads((root/'FOLD_RECEIPT.json').read_text());v=load(source,month,ROOT)
 _,cal,chk,split=chronological_partition(v['entry_utc_ms'])
 model=rec['frozen_research_model'];thr=next(q['threshold'] for q in rec['trials'][model]['sweep'] if q['quantile']==.85)
 three=lgb.Booster(model_file=str(root/f'three_{model}.txt'));wait=lgb.Booster(model_file=str(root/f'wait_{model}.txt'))
 p=three.predict(v['X'][chk]);w=wait.predict(v['X'][chk]);score=p[:,2]-1.2*p[:,0]-.45*p[:,1]-.2*w
 selected=score>thr
 t=v['entry_utc_ms'][chk];true=v['observed_class'][chk];net=v['realized_net'][chk]
 days=np.unique(t//86400000)
 daily=[]
 for d in days:
  mask=(t//86400000==d)&selected
  total=int(mask.sum());good=int(np.sum(true[mask]==1))
  daily.append({'utc_date':dt.datetime.fromtimestamp(int(d)*86400,dt.timezone.utc).date().isoformat(),
        'trades':total,'strict_good':good,'rate':good/total if total else None,'passes':bool(total and good/total>=.8)})
 weeks={}
 for d in daily:
  a=dt.date.fromisoformat(d['utc_date']);wk=f'{a.isocalendar().year}-W{a.isocalendar().week:02d}'
  w=weeks.setdefault(wk,{'trades':0,'strict_good':0})
  w['trades']+=d['trades'];w['strict_good']+=d['strict_good']
 for wk,x in weeks.items():x['rate']=x['strict_good']/x['trades'] if x['trades'] else None;x['passes']=bool(x['trades'] and x['rate']>=.8)
 count=int(selected.sum());good=int(np.sum(true[selected]==1))
 ans={'source':source,'month':month,'status':'FROZEN_CALIBRATION_THRESHOLD_OFF_POLICY_DIAGNOSTIC_ONLY',
     'threshold_source':'ONLY earlier calibration q=.85 (not selected on heldout)',
     'n_check_legacy_positions':len(t),'selected':count,'correct':good,
     'strict_rate':good/count if count else None,'net':round(float(np.sum(net[selected])),3),
     'active_days':len(days),'days_passing_80':sum(z['passes'] for z in daily),
     'weeks_passing_80':sum(z['passes'] for z in weeks.values()),'total_weeks':len(weeks),
     'daily':daily,'weekly':weeks,'monthly_floor_entire_source_month':int(np.ceil(.85*SYNTH[month])),
     'percentage_of_source_month_available_in_check_days':len(days)/len(np.unique(v['entry_utc_ms']//86400000)),
     'cannot_claim_new_trade_count_or_month_floor':True,'price_cost_model':'same original R9 idealized executable quote-side .02 fee'}
 (root/'FROZEN_Q85_HELDOUT_DIAGNOSTIC.json').write_text(json.dumps(ans,indent=2))
 print(source,month,'check',len(t),'chosen',count,'correct_pct',ans['strict_rate'],'net',ans['net'],'days 80',ans['days_passing_80'],'/',len(days))
 return ans

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--source');p.add_argument('--month');a=p.parse_args()
 record(a.source,a.month)

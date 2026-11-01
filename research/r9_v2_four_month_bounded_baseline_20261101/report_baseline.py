#!/usr/bin/env python3
"""Report frozen v2 default policy selected-trade results. No model refitting/tuning."""
import csv,glob,hashlib,json,math,os,statistics
from pathlib import Path
B=Path(__file__).resolve().parent
C=B/'bounded_collections';R=B/'results'
def asrow(rs):
  n=len(rs); profit=sum(max(x['net'],0.) for x in rs); loss=sum(min(x['net'],0.) for x in rs)
  equity=0;peak=0;dd=0
  for x in sorted(rs,key=lambda q:q['utc_ms']):
    equity+=x['net'];peak=max(peak,equity);dd=max(dd,peak-equity)
  return dict(trades=n,net=round(equity,4),avg_net=round(equity/n,4) if n else None,
      wins=sum(x['net']>0 for x in rs),win_rate=round(sum(x['net']>0 for x in rs)/n,4) if n else None,
      gross_profit=round(profit,4),gross_loss=round(loss,4),
      profit_factor=round(profit/-loss,4) if loss<0 else None,
      max_realized_peak_to_trough_loss=round(dd,4),
      net_if_fee_020=round(equity-0.18*n,4),
      mean_spread=round(sum(x['spread'] for x in rs)/n,4) if n else None)
def report():
  summaries=[json.load(open(p)) for p in sorted(C.glob('*_collection.json'))]
  wf=json.load(open(R/'walkforward_summary.json'));led=json.load(open(R/'walkforward_selected_trades.json'))
  per=[]
  for m in ('01','02','06','07'):
    for s in ('coinexx','dukascopy'):
      r=[x for x in led if x['month']==m and x['source']==s]
      d=next((x for x in summaries if x['month']==m and x['source']==s),None)
      per.append({'month':m,'source':s,'ticks_scanned':d['counts']['ticks'],'paired_candidate_paths':d['records'],
                 'snapshot_candidates':d['counts']['decisions'],**asrow(r)})
  fold_status=[{'month':f['month'],'status':f['status'],'train':f.get('train'),
                'cal':f.get('cal'),'dev':f.get('development')} for f in wf['folds']]
  sha={}
  for f in [Path('/mnt/data/r9_entry_router_v2/src/router_v2_features.py'),Path('/mnt/data/r9_entry_router_v2/src/router_v2_labels.py'),
            Path('/mnt/data/r9_entry_router_v2/src/router_v2_model.py'),Path('/mnt/data/r9_entry_router_v2/src/router_v2_train.py'),
            Path('/mnt/data/r9_entry_router_v2/src/router_v2_dataset.py'),B/'bounded_trace_v2.py']:
    sha[f.name]=hashlib.sha256(f.read_bytes()).hexdigest()
  out={'status':'BOUNDED_DIAGNOSTIC_NOT_FULL_MONTH_BASELINE','policy':'FROZEN_ROUTER_V2_DEFAULTS_NO_HYPERPARAMETER_SEARCH',
       'original_v2_branch':'carson/r9-probabilistic-entry-router-v2-20261101',
       'v2_base_commit':'35056fa38c11a7b2e9b9d6bab984af3368e905be',
       'design':'four UTC windows (00,06,12,18) per development role day, 9min each, 5min warmup, <=100 500ms snapshots per window',
       'nonrepresentative_sampling':True,'modified_entry_model':False,'fit_default_teacher_weight':0.10,
       'np_alpha':0.10,'min_utility':0,'scan_ms':500,'round_trip_fee_usd':0.02,
       'source_archives':[{'source':d['source'],'month':d['month'],'name':d['source_name'],'sha256':d['source_sha256']} for d in summaries],
       'hashes':sha,'folds':fold_status,'monthly_broker':per,'aggregate':asrow(led),'source_totals':{s:asrow([x for x in led if x['source']==s]) for s in ('coinexx','dukascopy')},
       'ticks_scanned':sum(d['counts']['ticks'] for d in summaries),
       'paired_paths':sum(d['records'] for d in summaries),
       'limitations':['not full development days or full-month entry PnL','fixed 4 UTC windows/day; sampling affects selected trade distribution',
        'local 5m state warmed afresh each window; minute-bar context retained','quote replay idealized fills, no slippage or broker stop-level/margin model',
        'fee fixed 0.02 USD/trade, additional 0.18 USD/trade stress is diagnostic only',
        'repeated partial overlapping 500ms hypothetical candidates are training data, NOT trades',
        'development checks are previously sampled dates; not clean untouched OOS',
        'no futures in runtime feature vector, synthetic teacher weak training-only']}
  (R/'baseline_scorecard.json').write_text(json.dumps(out,indent=2))
  headers=['month','source','ticks_scanned','paired_candidate_paths','trades','net','win_rate','profit_factor','net_if_fee_020']
  with (R/'baseline_scorecard.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=headers,extrasaction='ignore');w.writeheader();w.writerows(per)
  return out
if __name__=='__main__':
 d=report();print(json.dumps({'aggregate':d['aggregate'],'sources':d['source_totals'],'per':d['monthly_broker'],'folds':d['folds']},indent=2))

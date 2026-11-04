"""R18-S1 empirical bid/ask payoff asymmetry, eight original source-months.

Purely retrospective exact source-ordinal decomposition, no entry predictor.
Broker commissions are represented solely by the archived +$0.02/oz
quoted-price fee; NOT real 0.01 lot USD PnL or live dealer fills.
"""
from __future__ import annotations
import csv,json,sys,hashlib
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/data')
LAB=ROOT/'h1v2_r18_dualbroker';OUT=LAB/'results_r18_FROZEN_DELAY'
sys.path.insert(0,str(LAB/'src'))
import r18_broker_multihorizon as r18
from r18_frozen_latency_economic_stress import get_frozen

SOURCES=('DUKASCOPY_RAW','MT5_BROKER_EXPORT');MONS=('01','02','06','07')
LABELS=('lag0_slip0','lag0_slip20','lag0_slip50','lag100_slip0','lag100_slip20','lag100_slip50',
        'lag500_slip0','lag500_slip20','lag500_slip50')

def stat(v):
 if len(v)==0:return (None,)*5
 return [float(np.mean(v)),float(np.median(v)),float(np.quantile(v,.05)),
         float(np.quantile(v,.95)),float(np.min(v))]

def run_one(src,mon):
 t,b,a,signal,side,_,provenance=get_frozen(src,mon)
 assert np.all(np.diff(t)>=0)
 tag=f'R18_LATENCY_{src}_{mon}'
 path=OUT/(tag+'_ALL_FROZEN_SOURCE_ORDINAL_OUTCOME_TRACES.npz')
 rows=[]
 with np.load(path,allow_pickle=False) as d:
  for label in LABELS:
   state=d[label+'_outcome'];fill=d[label+'_fill_ord'];net=d[label+'_realized_quote_pnl_raw_or_sentinel']
   goods=state==1;bads=(state==0)|(state==2);complete=goods|bads
   assert np.array_equal(d[label+'_signal_ord'],signal)
   assert np.array_equal(d[label+'_future_selected_side'],side)
   values=net[goods].astype(np.int64);loss=net[bads].astype(np.int64)
   assert np.all(values>=100)
   # A strict TIMEOUT failure may nevertheless liquidate at >=+$0.10 net
   # AFTER the 60s deadline. Classification and modeled economics differ.
   if np.any((state==0)&(net>=100)):
    raise RuntimeError('STOP_GROUP_FIRST_PASS_TP_CONTRADICTION')
   good_spread=(a[fill[goods]].astype(np.int64)-b[fill[goods]].astype(np.int64))/1000
   bad_spread=(a[fill[bads]].astype(np.int64)-b[fill[bads]].astype(np.int64))/1000
   mean_win=float(values.mean()/1000) if len(values) else None
   mean_loss=float(loss.mean()/1000) if len(loss) else None
   breakeven=None
   if mean_win is not None and mean_loss is not None and mean_loss<0:
    breakeven=-mean_loss/(mean_win-mean_loss)
   row={'source':src,'month':'2026-'+mon,'model':label,
    'original_hindsight_source_signal_count':len(state),'completed_win':int(goods.sum()),
    'completed_stop':int((state==0).sum()),'completed_timeout':int((state==2).sum()),
    'source_censored':int((state==-3).sum()),'quote_rejected':int((state==-1).sum()),
    'position_busy_skip':int((state==-2).sum()),
    'completed_strict_quality':float(goods.sum()/complete.sum()) if np.any(complete) else None,
    'completed_non_strict_but_positive_net':int((bads&(net>0)).sum()),
    'completed_timeout_positive_net':int(((state==2)&(net>0)).sum()),
    'completed_bad_negative_net':int((bads&(net<0)).sum()),
    'mean_win_quoted_price_usd_per_oz':mean_win,
    'median_win_quoted_price_usd_per_oz':float(np.median(values)/1000) if len(values) else None,
    'p05_win_quoted_price_usd_per_oz':float(np.quantile(values,.05)/1000) if len(values) else None,
    'mean_bad_quoted_price_usd_per_oz':mean_loss,
    'median_bad_quoted_price_usd_per_oz':float(np.median(loss)/1000) if len(loss) else None,
    'p05_bad_quoted_price_usd_per_oz':float(np.quantile(loss,.05)/1000) if len(loss) else None,
    'empirical_break_even_completed_quality_under_means':breakeven,
    'mean_completed_good_fill_spread_usd':float(good_spread.mean()) if len(good_spread) else None,
    'median_completed_good_fill_spread_usd':float(np.median(good_spread)) if len(good_spread) else None,
    'mean_completed_bad_fill_spread_usd':float(bad_spread.mean()) if len(bad_spread) else None,
    'median_completed_bad_fill_spread_usd':float(np.median(bad_spread)) if len(bad_spread) else None,
    'net_realized_quoted_price_sum_per_oz_NOT_CASH':float(net[complete].astype(np.int64).sum()/1000),
    'cash_equity_trading_or_true_broker_commission_MODELED':False,
    'source_selected_future_oracle_not_deployable':True}
   rows.append(row)
 return rows

def main():
 rows=[]
 for src in SOURCES:
  for mon in MONS:
   rows+=run_one(src,mon)
   print('COMPLETE',src,mon,flush=True)
 assert len(rows)==72
 path=LAB/'results_r18_FROZEN_DELAY/R18S1_ALL_72_SOURCE_MONTH_LATENCY_SCENARIO_PAYOFF_GEOMETRY_FORENSICS.csv'
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 h=hashlib.sha256(path.read_bytes()).hexdigest()
 (path.with_suffix('.json')).write_text(json.dumps({'source_scenarios':72,
  'status':'OFFLINE_FUTURE_INFORMED_SIGNAL_REPLAY_NO_LIVE_BROKER_CASH',
  'source_month_count':8,'output_csv_sha256':h,
  'quoted_price_units_not_real_lot_economics':True,
  'all_72_loss_and_win_per_source_model_preserved':True},indent=2)+'\n')
 print('ALL72',h,flush=True)
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--source',choices=SOURCES)
 ap.add_argument('--month',choices=MONS)
 x=ap.parse_args()
 if bool(x.source)!=bool(x.month):ap.error('Need both source and month')
 if x.source:
  rows=run_one(x.source,x.month)
  p=OUT/f'R18S1_PAYOFF_GEOMETRY_{x.source}_{x.month}_9_SCENARIOS.csv'
  with p.open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
  print('ATOMIC_PAYOFF_COMPLETE',p.name,len(rows),hashlib.sha256(p.read_bytes()).hexdigest())
 else:
  chunks=[]
  for source in SOURCES:
   for mon in MONS:
    p=OUT/f'R18S1_PAYOFF_GEOMETRY_{source}_{mon}_9_SCENARIOS.csv'
    with p.open(newline='') as f:chunks.extend(csv.DictReader(f))
  assert len(chunks)==72
  p=OUT/'R18S1_ALL_72_SOURCE_MONTH_LATENCY_SCENARIO_PAYOFF_GEOMETRY_FORENSICS.csv'
  with p.open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(chunks[0]));w.writeheader();w.writerows(chunks)
  print('ASSEMBLED_72',hashlib.sha256(p.read_bytes()).hexdigest())


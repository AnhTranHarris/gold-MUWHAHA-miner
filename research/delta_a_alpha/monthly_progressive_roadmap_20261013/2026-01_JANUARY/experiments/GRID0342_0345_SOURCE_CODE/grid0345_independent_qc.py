"""Read-only independent QC of GRID0342–0344 original Dukascopy tick research.
No experiment has any right to modify original V1 or overwrite predecessor work.
"""
from pathlib import Path
import sys,json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parent
DATA=Path('/mnt/data/R8_JAN_DUKAS_RESEARCH')
t=np.load(DATA/'ticks_t.npy',mmap_mode='r');ask=np.load(DATA/'ticks_ask.npy',mmap_mode='r');bid=np.load(DATA/'ticks_bid.npy',mmap_mode='r')
assert len(t)==9135062 and np.all(np.diff(t)>=0)
raw=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
assert hashlib.sha256(raw.read_bytes()).hexdigest()=='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
complete=json.loads((ROOT/'grid0343_ten_start_results.json').read_text());raws=complete['partials'];assert len(complete['ten_random_days'])==10
checks=2
for name,rec in complete['cases'].items():
 rows=[x for x in raws if x['policy']==name];assert len(rows)==10 and all(not x.get('INCOMPLETE') for x in rows);checks+=2
 assert len({x['day'] for x in rows})==10;checks+=1
 assert rec['positive']==sum(x['positive'] for x in rows);checks+=1
 assert rec['no_stopout']==sum(x['pass_margin'] for x in rows);checks+=1
 assert rec['nonruin']==sum(x['pass_nonruin'] for x in rows);checks+=1
 assert rec['count']==sum(x['trades_closed'] for x in rows);checks+=1
 assert abs(rec['min_cash']-min(x['final_cash'] for x in rows))<1e-8;checks+=1
 assert abs(rec['worst_hour']-max(x['worst_hour_drawdown'] for x in rows))<1e-8;checks+=1
 assert rec['hit5000']==sum(x['targeted5000'] for x in rows);checks+=1
endogenous=json.loads((ROOT/'grid0344_fully_endogenous_results.json').read_text());assert len(endogenous)==4;checks+=1
for name,s in endogenous.items():
 with np.load(ROOT/(name+'_exact_quote_trade_ledger.npz')) as z:
  ei=z['entry_idx'];xi=z['exit_idx'];side=z['side'];p=z['net'];n=len(ei)
 assert n==s['trades'] and n>0;checks+=2
 assert np.all(ei>=0) and np.all(xi<len(t)) and np.all(ei<xi);checks+=1
 assert np.all(ei[1:]>xi[:-1]);checks+=1
 assert np.all((side==1)|(side==-1));checks+=1
 # Integer quote precision 1/1000 and $0.20 fee. Exact executed Bid/Ask geometry.
 calc=np.where(side>0,bid[xi].astype(float)-ask[ei].astype(float),bid[ei].astype(float)-ask[xi].astype(float))/1000.-.20
 assert np.max(np.abs(calc-p))<1e-8;checks+=1
 assert abs(100+float(np.sum(p))-s['end_cash'])<1e-7;checks+=1
 assert abs(float(np.sum(p[p>0]))-s['gross_profit'])<1e-7;checks+=1
 assert abs(float(np.sum(p[p<=0]))-s['gross_loss'])<1e-7;checks+=1
 assert s['max_tick_dd']>=0 and s['worst_hour_dd']>=0;checks+=1
record=dict(qc_state='PASS_RESEARCH_CHECKS_ONLY',checks=checks,cases=list(complete['cases']),endogenous=list(endogenous),raw_tick_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),cannot_claim='not month-blind, not broker-certified, no 5000 success, no production approval')
(ROOT/'grid0345_independent_qc_results.json').write_text(json.dumps(record,indent=2));print('INDEPENDENT_QC',record,flush=True)

"""GRID0347 read-only original quote execution-ledger auditor; never promotes research."""
from pathlib import Path
import hashlib,json,gzip
import numpy as np
ROOT=Path(__file__).parent
SRC=Path('/mnt/data/R8_JAN_DUKAS_RESEARCH')
RAW=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
results=json.loads((ROOT/'GRID0346_JANUARY_STRUCTURAL_MICRO_CAPITAL_RESULTS.json').read_text())
t=np.load(SRC/'ticks_t.npy',mmap_mode='r');a=np.load(SRC/'ticks_ask.npy',mmap_mode='r');b=np.load(SRC/'ticks_bid.npy',mmap_mode='r')
checks=0
assert len(t)==9135062 and len(a)==len(t)==len(b);checks+=1
assert np.all(t[1:]>=t[:-1]) and np.all(a>=b);checks+=1
assert hashlib.sha256(RAW.read_bytes()).hexdigest()=='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5';checks+=1
with gzip.open(RAW,'rt') as f:
 next(f)
 for i in range(3):
  x=next(f).strip().split(',');assert (int(x[0]),int(x[1]),int(x[2]))==(int(t[i]),int(a[i]),int(b[i]));checks+=1
assert results['seed']==20261014 and len(results['cohort'])==10;checks+=1
vresults={}
for name,info in results['variants'].items():
 assert len(info['results'])==10 and info['reached_5000']==0;checks+=1
 assert info['profitable_count']==sum(r['final_cash']>100 for r in info['results']);checks+=1
 assert info['nonruin']==sum(r['min_equity']>0 for r in info['results']);checks+=1
 assert info['trades']==sum(r['trades'] for r in info['results']);checks+=1
 assert abs(info['worst_hour_dd']-max(x['worst_hour_dd'] for x in info['results']))<1e-6;checks+=1
 with np.load(ROOT/(name+'_original_quote_deals.npz')) as z:
  ei=z['entry_idx'];xi=z['exit_idx'];side=z['side'];p=z['net'];n=len(p)
 assert n==info['trades'] and n>0;checks+=1
 assert np.all(ei>=0)&np.all(xi<len(t))&np.all(ei<=xi);checks+=1
 assert np.all(np.isin(side,[-1,1]));checks+=1
 calc=np.where(side>0,b[xi].astype(float)-a[ei].astype(float),b[ei].astype(float)-a[xi].astype(float))/1000.-.20
 assert np.max(np.abs(calc-p))<1e-8;checks+=1
 k=0
 for ep in info['results']:
  m=ep['trades'];segment=p[k:k+m];ki=ei[k:k+m];kx=xi[k:k+m]
  assert abs(100+float(np.sum(segment))-ep['final_cash'])<=.002;checks+=1
  assert abs(float(np.sum(np.maximum(segment,0)))-ep['grossprofit'])<.002;checks+=1
  assert abs(float(np.sum(np.minimum(segment,0)))-ep['grossloss'])<.002;checks+=1
  if m>1:assert np.all(ki[1:]>kx[:-1]);checks+=1
  k+=m
 assert k==n;checks+=1
 vresults[name]={'trades':n,'positive_starts':info['profitable_count'],'reached_5000':info['reached_5000'],'cash_range':[info['ending_min'],info['ending_max']],'worst_hour_dd':info['worst_hour_dd']}
summary={'qc':'PASS_RESEARCH_LEDGER_IDENTITY_NOT_BROKER_CERTIFICATION', 'independent_assertions':checks,'sha256_original_jan_ticks':hashlib.sha256(RAW.read_bytes()).hexdigest(),'variants':vresults,'limitation':'in-sample January original tick price-model, not forward tested, no R9 parity or $5k success; broker contract/margin unknown'}
(ROOT/'GRID0347_INDEPENDENT_LEDGER_QC.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))

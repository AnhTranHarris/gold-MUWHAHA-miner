"""GRID0327 independent original-tick audit for source-conditional GRID0325/0326.
Read-only; each funded accepted entry repriced on actual raw Ask/Bid, close
repriced at actual opposing raw quote and cash, floating/hours reconstructed.
"""
from __future__ import annotations
import hashlib,json,time
from pathlib import Path
import numpy as np
import grid0326_source_conditioned_hourly_pareto as p
import grid0315_independent_7day_margin_liquidation_qc as qc
from grid0307_random_start_lowcapital_original_tick import TICK_SOURCE
ROOT=Path(__file__).resolve().parent
POLICIES=[('ORDINARY_SHOCK_0P35_M20',.35,.20),('ORDINARY_SHOCK_0P50_M20',.5,.20)]

def main():
 start=time.time();res=json.load(open(ROOT/'grid0326_original_source_conditional_pareto_results.json'))
 t,bid,ask,z,kind,owner,pgid,r9,orig=p.p.cohort.sim.prior.g.g.base.p.ancestor.base.materialize()
 sha=hashlib.file_digest(TICK_SOURCE.open('rb'),'sha256').hexdigest();assert sha=='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
 _,days=p.p.cohort.select_days(r9,t);assert days==res['dates'];count=0;checked=[]
 for d in days:
  day=int(np.datetime64(d+'T00:00:00','ms').astype('int64'));lo=np.searchsorted(t,day,'left');hi=np.searchsorted(t,day+7*86400000,'left')
  tt=t[lo:hi];b=bid[lo:hi];a=ask[lo:hi]
  mask=(z['entry_idx']>=lo)&(z['entry_idx']<hi)
  zz={k:v[mask].copy() for k,v in z.items()};kk=kind[mask];oo=owner[mask]
  zz['entry_idx']-=lo;trunc=zz['exit_idx']>=hi;zz['exit_idx']=np.minimum(zz['exit_idx']-lo,hi-lo-1)
  keep=zz['entry_idx']<zz['exit_idx'];zz={k:v[keep] for k,v in zz.items()};kk=kk[keep];oo=oo[keep];trunc=trunc[keep]
  for j in np.flatnonzero(trunc):
   ix=int(zz['exit_idx'][j]);dr=int(zz['direction'][j]);zz['net_cash'][j]=dr*(int(b[ix] if dr>0 else a[ix])-int(zz['entry_price_raw'][j]))/1000.-.20
  pre,shock=p.p.sim.features(tt,b,a)
  assert np.all(tt[pre]<=tt-1000) or tt[0]==tt[pre[0]] # first quotes before 1s warmup.
  for name,minimum,budget in POLICIES:
   x=p.p.sim.run(tt,b,a,zz,kk,oo,pgid,cash=100.,admission_margin_fraction=budget,stopout_ratio=.5,
                 screen_quote_idx=pre,pre_request_shock_5s=shock,min_observed_5s_shock=minimum,screen_sources=p.ORD)
   deals=x.pop('booked_ledger');ad=x.pop('accepted_indices');y=qc.reconstruct(tt,b,a,zz,ad,deals)
   saved=next(v for v in res['episodes'] if v['date']==d and v['name']==name)
   vals=[(x['final_cash'],y['close_cash']),(x['final_cash'],saved['final_cash']),
      (x['min_tick_equity'],y['min_equity']),(x['worst_hour_drawdown'],y['worst_hour_dd']),
      (x['max_tick_drawdown'],y['max_equity_dd']),(x['trades_closed'],y['closed_trades']),
      (x['worst_hour_drawdown'],saved['worst_hour'])]
   for a0,b0 in vals:assert abs(a0-b0)<1e-5,(d,name,a0,b0);count+=1
   checked.append(dict(date=d,variant=name,cash=y['close_cash'],minimum_equity=y['min_equity'],
                       worst_hour=y['worst_hour_dd'],trades=y['closed_trades'],stopout=x['forced_events']))
  print('Original tick QC',d,'PASSED',flush=True)
 assert count==140 and len(checked)==20
 r={'status':'RESEARCH_ONLY_UNPROMOTED_READONLY_QC','assertions':count,'runs':len(checked),
    'source_sha256':sha,'seed':p.p.cohort.SEED,'original_tick_count':len(t),
    'source_limited':['prior original historically chosen source and exits','500x hypothetical leverage/commission',
                      'no broker-native order request evidence','no 75% R9 OVERFIT six-dimension teacher scoring'],
    'results':checked,'elapsed_sec':time.time()-start}
 (ROOT/'grid0327_source_routing_independent_qc.json').write_text(json.dumps(r,indent=2))
 print('GRID0327 INDEPENDENT ASSERTIONS',count,'PASS',flush=True)
if __name__=='__main__':main()

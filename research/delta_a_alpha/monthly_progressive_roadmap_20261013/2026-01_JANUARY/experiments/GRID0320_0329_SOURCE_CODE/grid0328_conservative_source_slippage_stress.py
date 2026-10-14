"""GRID0328: original quote seven-day source-conditional candidate at adverse fill slippage.
No bid/ask midpoint fills, no post-hoc favorable fills, no martingale.
Exact real Coinexx slippage unverified; these are hypothetical additional close costs.
"""
from __future__ import annotations
import json,time
from pathlib import Path
import numpy as np
import grid0326_source_conditioned_hourly_pareto as p
ROOT=Path(__file__).resolve().parent
POLICIES=[('CONTROL_0P00',0.),('ADVERSE_0P10',.10),('ADVERSE_0P30',.30),('ADVERSE_0P50',.50)]

def main():
 st=time.time();t,bid,ask,z,kind,owner,pgid,r9,origin=p.p.cohort.sim.prior.g.g.base.p.ancestor.base.materialize()
 _,dates=p.p.cohort.select_days(r9,t);rows=[]
 for d in dates:
  day=int(np.datetime64(d+'T00:00:00','ms').astype('int64'));lo=np.searchsorted(t,day,'left');hi=np.searchsorted(t,day+7*86400000,'left')
  tt=t[lo:hi];b=bid[lo:hi];a=ask[lo:hi]
  mask=(z['entry_idx']>=lo)&(z['entry_idx']<hi)
  zz={k:v[mask].copy() for k,v in z.items()};kk=kind[mask];oo=owner[mask]
  zz['entry_idx']-=lo;trunc=zz['exit_idx']>=hi;zz['exit_idx']=np.minimum(zz['exit_idx']-lo,hi-lo-1)
  keep=zz['entry_idx']<zz['exit_idx'];zz={k:v[keep] for k,v in zz.items()};kk=kk[keep];oo=oo[keep];trunc=trunc[keep]
  for j in np.flatnonzero(trunc):
   ix=int(zz['exit_idx'][j]);dr=int(zz['direction'][j]);zz['net_cash'][j]=dr*(int(b[ix] if dr>0 else a[ix])-int(zz['entry_price_raw'][j]))/1000.-.20
  pre,shock=p.p.sim.features(tt,b,a)
  for name,slip in POLICIES:
   x=p.p.sim.run(tt,b,a,zz,kk,oo,pgid,cash=100.,admission_margin_fraction=.20,stopout_ratio=.5,
                 screen_quote_idx=pre,pre_request_shock_5s=shock,min_observed_5s_shock=.5,
                 screen_sources=p.ORD,max_tick_slippage_usd=slip)
   x.pop('booked_ledger');x.pop('accepted_indices')
   rows.append(dict(date=d,policy=name,net=x['net_cash'],final=x['final_cash'],trades=x['trades_closed'],
                    min_equity=x['min_tick_equity'],worst_hour=x['worst_hour_drawdown'],stopouts=x['forced_events']))
  print('DONE',d,flush=True)
 s={}
 for name,*_ in POLICIES:
  x=[v for v in rows if v['policy']==name]
  s[name]=dict(starts=len(x),positive=sum(y['final']>100 for y in x),nonruin=sum(y['min_equity']>0 for y in x),
   no_stopout=sum(y['stopouts']==0 for y in x),best_cash=max(y['final'] for y in x),worst_cash=min(y['final'] for y in x),
   total_trades=sum(y['trades'] for y in x),worst_hour=max(y['worst_hour'] for y in x),
   reach_10000=sum(y['final']>=10000. for y in x))
  print(name,s[name],flush=True)
 o=dict(id='GRID0328_ORIGINAL_JAN_ADVERSE_SLIPPAGE_TEN_START',status='UNPROMOTED_NOT_COINEXX_CERTIFICATION',
    seed=p.p.cohort.SEED,days=dates,stress=POLICIES,summary=s,episodes=rows,
    limitations=['Additional slippage is modeled as negative cash on closing quotes, not real physical adverse quote fill',
     'Historical source candidate and exit generation not endogenous',
     '500x margin assumed, real broker conditions unknown',
     'No assumption that historical ten starts guarantee future survival'],elapsed_s=time.time()-st)
 (ROOT/'grid0328_conservative_slippage_original_tick_results.json').write_text(json.dumps(o,indent=2))
if __name__=='__main__':main()

"""GRID0325 10 seeded seven-calendar-day source-aware shock screen.
Same source, quote windows, and predecessor reference. Children require paid parents.
"""
from __future__ import annotations
import json,time
from pathlib import Path
import numpy as np
import grid0324_source_conditioned_pre_request_routing as sim
import grid0313_seven_day_ten_start_stopout_frontier as cohort
ROOT=Path(__file__).resolve().parent
POLICIES=[
 ('CONTROL',0.,()),('ALL_SHOCK_0P5',.5,()),
 ('COVERAGE_GC0_ONLY',.5,('coverage_gc0',)),('COVERAGE_GC2_ONLY',.5,('coverage_gc2',)),
 ('WD_PARENT_ONLY',.5,('WD_PHYSICAL_PARENT',)),('WD_CHILD_ONLY',.5,('WD_FUNDED_CHILD',)),
 ('NY16_ONLY',.5,('NATIVE_NY16',)),
 ('BOTH_COVERAGE',.5,('coverage_gc0','coverage_gc2')),
 ('COVERAGE_AND_PARENT',.5,('coverage_gc0','coverage_gc2','WD_PHYSICAL_PARENT')),
 ('ALL_ORDINARY',.5,tuple(['coverage_gc0','coverage_gc2','NATIVE_NY16','ASIA02_CONT','LATE21_LONG','LONDON10_ROTATE_LONG','OVERLAP13_SHORT','coldstart']))
]

def main():
 t0=time.time();t,bid,ask,z,kind,owner,pgid,r9,orig=cohort.sim.prior.g.g.base.p.ancestor.base.materialize()
 _,days=cohort.select_days(r9,t)
 out=[]
 for d in days:
  day=int(np.datetime64(d+'T00:00:00','ms').astype('int64'));lo=np.searchsorted(t,day,'left');hi=np.searchsorted(t,day+7*86400000,'left')
  tt=t[lo:hi];b=bid[lo:hi];a=ask[lo:hi]
  mask=(z['entry_idx']>=lo)&(z['entry_idx']<hi)
  zz={k:v[mask].copy() for k,v in z.items()};kk=kind[mask];oo=owner[mask]
  zz['entry_idx']-=lo;trunc=zz['exit_idx']>=hi;zz['exit_idx']=np.minimum(zz['exit_idx']-lo,hi-lo-1)
  keep=zz['entry_idx']<zz['exit_idx'];zz={k:v[keep] for k,v in zz.items()};kk=kk[keep];oo=oo[keep];trunc=trunc[keep]
  for j in np.flatnonzero(trunc):
   ix=int(zz['exit_idx'][j]);dr=int(zz['direction'][j]);zz['net_cash'][j]=dr*(int(b[ix] if dr>0 else a[ix])-int(zz['entry_price_raw'][j]))/1000.-.20
  pre,shock=sim.features(tt,b,a)
  for name,minshock,srcs in POLICIES:
   x=sim.run(tt,b,a,zz,kk,oo,pgid,cash=100.,admission_margin_fraction=.20,stopout_ratio=.5,
             screen_quote_idx=pre,pre_request_shock_5s=shock,min_observed_5s_shock=minshock,screen_sources=srcs)
   x.pop('booked_ledger');x.pop('accepted_indices')
   out.append(dict(date=d,policy=name,final_cash=x['final_cash'],trades=x['trades_closed'],
                   min_equity=x['min_tick_equity'],worst_hour=x['worst_hour_drawdown'],
                   min_margin=x['min_margin_ratio_observed'],stopout=x['forced_events'],
                   blocked=x['denied'].get('pre_request_microstructure',0)))
  print('DONE',d,round(time.time()-t0,2),flush=True)
 summaries={}
 for name,*_ in POLICIES:
  arr=[x for x in out if x['policy']==name]
  summaries[name]=dict(n=len(arr),nonruin=sum(v['min_equity']>0 for v in arr),no_stopout=sum(v['stopout']==0 for v in arr),
      positive=sum(v['final_cash']>100 for v in arr),cash_min=min(v['final_cash'] for v in arr),
      cash_max=max(v['final_cash'] for v in arr),median_cash=float(np.median([v['final_cash'] for v in arr])),
      worst_hour=max(v['worst_hour'] for v in arr),min_equity=min(v['min_equity'] for v in arr),
      trade_total=sum(v['trades'] for v in arr),hit10000=sum(v['final_cash']>=10000 for v in arr))
  print(name,summaries[name],flush=True)
 result=dict(status='UNPROMOTED_NOT_MONTH_BLIND_PRODUCER',id='GRID0325_10_START_SOURCE_CONDITIONAL_MICROSTRUCTURE',seed=cohort.SEED,days=days,
             policies=POLICIES,summary=summaries,episodes=out,
             caveats=['All source events and planned exit times selected from historical January research, not endogenous runtime',
                      'Quote screen at least one second prior to entry-side price, but actual originating intent time unknown',
                      '500x leverage assumed, Coinexx rule book and real slippage unknown',
                      '10/10 sampled pass is not probability one future survival'],elapsed_s=time.time()-t0)
 path=ROOT/'grid0325_ten_start_source_conditioned_results.json';path.write_text(json.dumps(result,indent=2))
 print('SAVED',path,flush=True)
if __name__=='__main__':main()

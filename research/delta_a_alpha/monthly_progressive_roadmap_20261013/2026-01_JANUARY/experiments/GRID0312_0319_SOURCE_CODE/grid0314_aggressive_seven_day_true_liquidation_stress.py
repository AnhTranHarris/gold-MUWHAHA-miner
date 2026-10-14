"""GRID0314 fixed-lot aggressive admission/forced-close stresses, SAME GRID0313 predeclared sample.
All stressed settings chosen without seeing new sample outcomes, preserve failed variants.
"""
import json,time
from pathlib import Path
import numpy as np
import grid0313_seven_day_ten_start_stopout_frontier as p
ROOT=Path(__file__).resolve().parent
POLICIES=[
 ('MARGIN35_LIQ50',.35,.5,0.,'worst_first',0.),
 ('MARGIN45_LIQ50',.45,.5,0.,'worst_first',0.),
 ('MARGIN55_LIQ50',.55,.5,0.,'worst_first',0.),
 ('MARGIN65_LIQ50',.65,.5,0.,'worst_first',0.),
 ('MARGIN65_DEF200_WORST',.65,.5,2.,'worst_first',0.),
 ('MARGIN65_DEF200_FLATTEN',.65,.5,2.,'flatten',0.),
 ('MARGIN35_LIQ50_SLIP10',.35,.5,0.,'worst_first',.10),
 ('MARGIN20_LIQ50_SLIP10',.20,.5,0.,'worst_first',.10),
]

def main():
 t0=time.time();t,bid,ask,z,kind,owner,pgid,r9,orig=p.sim.prior.g.g.base.p.ancestor.base.materialize()
 eligible,days=p.select_days(r9,t);assert days==json.load(open(ROOT/'grid0313_seven_day_100usd_stopout_froniter.json'))['sample_dates']
 results=[]
 for day in days:
  start=int(np.datetime64(day+'T00:00:00','ms').astype('int64'))
  lo=int(np.searchsorted(t,start,'left'));hi=int(np.searchsorted(t,start+7*86400000,'left'))
  mask=(z['entry_idx']>=lo)&(z['entry_idx']<hi)
  zz={k:v[mask].copy() for k,v in z.items()};kk=kind[mask];oo=owner[mask]
  zz['entry_idx']-=lo
  truncated=zz['exit_idx']>=hi
  zz['exit_idx']=np.minimum(zz['exit_idx']-lo,hi-lo-1)
  keep=zz['entry_idx']<zz['exit_idx'];zz={k:v[keep] for k,v in zz.items()};kk=kk[keep];oo=oo[keep];truncated=truncated[keep]
  et=t[lo:hi];eb=bid[lo:hi];ea=ask[lo:hi]
  for j in np.flatnonzero(truncated):
   x=int(zz['exit_idx'][j]);d=int(zz['direction'][j]);out=int(eb[x] if d>0 else ea[x]);en=int(zz['entry_price_raw'][j]);zz['net_cash'][j]=d*(out-en)/1000.-.20
  for name,fraction,stop,defense,style,slip in POLICIES:
   o=p.sim.run(et,eb,ea,zz,kk,oo,pgid,cash=100.,admission_margin_fraction=fraction,
       stopout_ratio=stop,defensive_ratio=defense,liquidation_style=style,defensive_flatten=style=='flatten',
       max_tick_slippage_usd=slip)
   ledger=o.pop('booked_ledger');o.pop('accepted_indices')
   o.update(day=day,policy=name,slippage_usd_per_closed_trade=slip,
            reached_10000=bool(o['final_cash']>=10000.),
            booked_cash_check=abs(100+sum(row[2] for row in ledger)-o['final_cash'])<1.e-6)
   if not o['booked_cash_check']:raise AssertionError('cash ledger mismatch')
   results.append(o)
   print(day,name,'final',round(o['final_cash'],2),'N',o['trades_closed'],'minEQ',round(o['min_tick_equity'],2),
     'minMar',round(o['min_margin_ratio_observed'] or 0,2),'forced',o['forced_events'],'preempt',o['defensive_events'],flush=True)
 summary={}
 for name,*_ in POLICIES:
  a=[v for v in results if v['policy']==name]
  summary[name]={'nonruin':sum(x['min_tick_equity']>0 for x in a),
        'no_broker_stopout':sum(x['forced_events']==0 for x in a),'target10000':sum(x['reached_10000'] for x in a),
        'cash_min':min(x['final_cash'] for x in a),'cash_max':max(x['final_cash'] for x in a),
        'min_equity':min(x['min_tick_equity'] for x in a),'N':sum(x['trades_closed'] for x in a),
        'forced_events':sum(x['forced_events'] for x in a)}
 out={'id':'GRID0314_AGGRESSIVE_MARGIN_FORCED_LIQUIDATION_SEVEN_DAY_10_SEEDED_JAN_STARTS','sample_dates':days,
       'policies':POLICIES,'summary':summary,'episodes':results,'scientific_status':'RESEARCH_UNPROMOTED_HISTORICALLY_SELECTED_JANUARY_SOURCES',
       'elapsed_seconds':round(time.time()-t0,1)}
 f=ROOT/'grid0314_aggressive_liquidation_seven_day_results.json';f.write_text(json.dumps(out,indent=2));print('SAVED',f,flush=True)
if __name__=='__main__':main()

"""GRID0326: original tick 7-day source-specific risk-vs-throughput Pareto refinement.
Reuses same deterministic sampled starts, not a month/date execution switch.
"""
from __future__ import annotations
import json,time
from pathlib import Path
import numpy as np
import grid0325_ten_start_source_conditional_microstructure as p
ROOT=Path(__file__).resolve().parent
ORD=next(v[2] for v in p.POLICIES if v[0]=='ALL_ORDINARY')
CANDIDATES=[('ORDINARY_SHOCK_0P35_M20',.35,.20),('ORDINARY_SHOCK_0P50_M20',.5,.20),
 ('ORDINARY_SHOCK_0P65_M20',.65,.20),('ORDINARY_SHOCK_0P75_M20',.75,.20),
 ('ORDINARY_SHOCK_1P00_M20',1.0,.20),('ORDINARY_SHOCK_0P50_M25',.5,.25),
 ('ORDINARY_SHOCK_0P65_M25',.65,.25),('ORDINARY_SHOCK_0P75_M25',.75,.25)]

def main():
 start=time.time();t,bid,ask,z,kind,owner,pgid,r9,origin=p.cohort.sim.prior.g.g.base.p.ancestor.base.materialize()
 _,days=p.cohort.select_days(r9,t);out=[]
 for d in days:
  day=int(np.datetime64(d+'T00:00:00','ms').astype('int64'));lo=np.searchsorted(t,day,'left');hi=np.searchsorted(t,day+7*86400000,'left')
  tt=t[lo:hi];b=bid[lo:hi];a=ask[lo:hi]
  mask=(z['entry_idx']>=lo)&(z['entry_idx']<hi)
  zz={k:v[mask].copy() for k,v in z.items()};kk=kind[mask];oo=owner[mask]
  zz['entry_idx']-=lo;trunc=zz['exit_idx']>=hi;zz['exit_idx']=np.minimum(zz['exit_idx']-lo,hi-lo-1)
  keep=zz['entry_idx']<zz['exit_idx'];zz={k:v[keep] for k,v in zz.items()};kk=kk[keep];oo=oo[keep];trunc=trunc[keep]
  for j in np.flatnonzero(trunc):
   ix=int(zz['exit_idx'][j]);dr=int(zz['direction'][j]);zz['net_cash'][j]=dr*(int(b[ix] if dr>0 else a[ix])-int(zz['entry_price_raw'][j]))/1000.-.20
  pre,shock=p.sim.features(tt,b,a)
  for name,minimum,budget in CANDIDATES:
   r=p.sim.run(tt,b,a,zz,kk,oo,pgid,cash=100.,admission_margin_fraction=budget,stopout_ratio=.5,
              screen_quote_idx=pre,pre_request_shock_5s=shock,min_observed_5s_shock=minimum,screen_sources=ORD)
   r.pop('booked_ledger');r.pop('accepted_indices')
   out.append(dict(date=d,name=name,final_cash=r['final_cash'],trades=r['trades_closed'],
                   min_equity=r['min_tick_equity'],worst_hour=r['worst_hour_drawdown'],
                   forced=r['forced_events'],min_margin_ratio=r['min_margin_ratio_observed']))
  print('DONE',d,'seconds',round(time.time()-start,2),flush=True)
 summary={}
 for name,*_ in CANDIDATES:
  a=[v for v in out if v['name']==name]
  summary[name]={'starts':10,'positive':sum(x['final_cash']>100 for x in a),
   'no_broker_stops':sum(x['forced']==0 for x in a),'nonruin':sum(x['min_equity']>0 for x in a),
   'trade_total':sum(x['trades'] for x in a),'minimum_ending':min(x['final_cash'] for x in a),
   'maximum_ending':max(x['final_cash'] for x in a),'median_ending':float(np.median([x['final_cash'] for x in a])),
   'worst_hourly_dd':max(x['worst_hour'] for x in a),'min_equity':min(x['min_equity'] for x in a),
   'seven_day_100x':sum(x['final_cash']>=10000 for x in a)}
  print(name,summary[name],flush=True)
 outdict=dict(id='GRID0326_ORDINARY_SOURCE_ASOF_SHOCK_PARETO',status='UNPROMOTED_SOURCE_SELECTED_ORIGINAL_JANUARY',
     seed=p.cohort.SEED,dates=days,parameters=CANDIDATES,summary=summary,episodes=out,
     limitations=['Hypothetical 500x margin / 0.01 lot / .20 fee / original January selected candidate population',
                  'Historical 10 starts cannot guarantee 100 percent survivability',
                  'Not a fully endogenous month blind V1 pipeline',
                  'Known original intent timestamp not available, 1-sec pre-entry quote used instead'],elapsed_s=time.time()-start)
 path=ROOT/'grid0326_original_source_conditional_pareto_results.json';path.write_text(json.dumps(outdict,indent=2))
if __name__=='__main__':main()

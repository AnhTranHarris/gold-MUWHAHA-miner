"""GRID0330 unpromoted. Initial 0.01-lot slot capacity sweep.
Original ancestor event streams and quote-side closes; full tick margin and forced closes;
no increase in lot size and no capacity expansion driven by losses. 10 precommitted
Jan starts, 7 complete calendar days each, $100 initial, historical in sample.
"""
import json, time
from pathlib import Path
import numpy as np
import grid0325_ten_start_source_conditional_microstructure as prev
import grid0324_source_conditioned_pre_request_routing as sim
root=Path(__file__).resolve().parent
ALL_ORD=('coverage_gc0','coverage_gc2','NATIVE_NY16','ASIA02_CONT','LATE21_LONG','LONDON10_ROTATE_LONG','OVERLAP13_SHORT','coldstart')
POLICIES=[('P20_INIT2',.20,2),('P20_INIT4',.20,4),('P20_INIT6',.20,6),('P20_INIT8',.20,8),('P30_INIT4',.30,4),('P30_INIT8',.30,8)]

def main():
 t0=time.time(); t,bid,ask,z,kind,owner,pgid,r9,origin=prev.cohort.sim.prior.g.g.base.p.ancestor.base.materialize()
 eligible,days=prev.cohort.select_days(r9,t)
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
  for name,margin,initial in POLICIES:
   x=sim.run(tt,b,a,zz,kk,oo,pgid,cash=100.,initial_cap=initial,admission_margin_fraction=margin,stopout_ratio=.5,
             screen_quote_idx=pre,pre_request_shock_5s=shock,min_observed_5s_shock=.5,
             screen_sources=ALL_ORD)
   out.append(dict(date=d,policy=name,final=round(x['final_cash'],6),min_equity=round(x['min_tick_equity'],6),
                   min_ratio=x['min_margin_ratio_observed'],worst_hour=round(x['worst_hour_drawdown'],6),
                   max_dd=round(x['max_tick_drawdown'],6),trades=x['trades_closed'],peak_open=x['peak_open'],
                   forced=x['forced_events'],defensive=x['defensive_events'],denials=x['denied']))
  print('DONE',d,'secs',round(time.time()-t0,2),flush=True)
 summary={}
 for name,_,_ in POLICIES:
  q=[v for v in out if v['policy']==name]
  summary[name]=dict(nonruin=sum(v['min_equity']>0 for v in q),no_forced=sum(v['forced']==0 for v in q),
       positive=sum(v['final']>100 for v in q),seven_day_target=sum(v['final']>=10000 for v in q),
       minimum_final=min(v['final'] for v in q),maximum_final=max(v['final'] for v in q),
       total_trades=sum(v['trades'] for v in q),max_worst_hour=max(v['worst_hour'] for v in q),
       lowest_marked_equity=min(v['min_equity'] for v in q),forced_events=sum(v['forced'] for v in q))
  print(name,json.dumps(summary[name]),flush=True)
 result=dict(id='GRID0330_INIT_CAPACITY_CAUSAL_MARGINAL_RESEARCH',status='UNPROMOTED_JANUARY_ORIGINAL_SOURCE_CANDIDATES_HISTORICALLY_SELECTED',sample_seed=prev.cohort.SEED,days=days,
     policies=POLICIES,source_origin=origin,summary=summary,episodes=out,
     limitations=['Cohort is original Jan historical-source-selected candidate stream, not endogenous engine','0.01 lot research 1oz, 500:1 and stopout ratio hypothetical','Full period contains no out of sample source period','100% in ten does not imply future 100% survival'],elapsed_seconds=time.time()-t0)
 dst=root/'grid0330_initial_capacity_survival_sweep.json';dst.write_text(json.dumps(result,indent=2));print('SAVED',dst)
if __name__=='__main__':main()

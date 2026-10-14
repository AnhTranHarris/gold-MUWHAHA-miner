"""GRID0332 unpromoted. Combine original R9 source-specific delayed-shock routing
with previously BOOKED-CASH gated eight-slot permission. Causal asof, $100/7d,
10 seeded starts, original Dukascopy ticks and real Bid/Ask sides; no Martingale.
Original source events and scheduled exits remain historically selected, hence this
research is NOT an endogenous L0-L7 signal/execution certification.
"""
from pathlib import Path
import time,json
import numpy as np
import grid0324_source_conditioned_pre_request_routing as original
import grid0313_seven_day_ten_start_stopout_frontier as cohort
from grid0330_initial_capacity_survival_sweep import ALL_ORD
ROOT=Path(__file__).resolve().parent
SRC=original.S
p='        earned=initial_cap\n        for bal_thresh,slots in earned_cash_tiers:'
r='''        earned=initial_cap
        if balance>=150. and src in ('coverage_gc0','coverage_gc2') and pre_request_shock_5s is not None and float(pre_request_shock_5s[ei])>=1.0:
            earned=max(earned,8)
        for bal_thresh,slots in earned_cash_tiers:'''
assert SRC.count(p)==1
SRC=SRC.replace(p,r)
SRC=SRC.replace('@njit(cache=True)','@njit(cache=False)')
ns={'__file__':str(ROOT/'grid0312_tick_stopout_executable.py')}
exec(compile(SRC,'grid0332_source_locked_earned_shock_slots','exec'),ns)
run=ns['run']

def main():
 start=time.time();t,bid,ask,z,kind,owner,pgid,r9,origin=cohort.sim.prior.g.g.base.p.ancestor.base.materialize()
 _,days=cohort.select_days(r9,t);out=[]
 for d in days:
  day=int(np.datetime64(d+'T00:00:00','ms').astype('int64'));lo=np.searchsorted(t,day,'left');hi=np.searchsorted(t,day+7*86400000,'left')
  tt=t[lo:hi];b=bid[lo:hi];a=ask[lo:hi]
  mask=(z['entry_idx']>=lo)&(z['entry_idx']<hi)
  zz={k:v[mask].copy() for k,v in z.items()};kk=kind[mask];oo=owner[mask]
  zz['entry_idx']-=lo;trunc=zz['exit_idx']>=hi;zz['exit_idx']=np.minimum(zz['exit_idx']-lo,hi-lo-1)
  keep=zz['entry_idx']<zz['exit_idx'];zz={k:v[keep] for k,v in zz.items()};kk=kk[keep];oo=oo[keep];trunc=trunc[keep]
  for j in np.flatnonzero(trunc):
   ix=int(zz['exit_idx'][j]);dr=int(zz['direction'][j]);zz['net_cash'][j]=dr*(int(b[ix] if dr>0 else a[ix])-int(zz['entry_price_raw'][j]))/1000.-.20
  pre,shock=original.features(tt,b,a)
  x=run(tt,b,a,zz,kk,oo,pgid,cash=100.,initial_cap=2,admission_margin_fraction=.20,stopout_ratio=.5,
       screen_quote_idx=pre,pre_request_shock_5s=shock,min_observed_5s_shock=.5,screen_sources=ALL_ORD)
  row=dict(date=d,final=x['final_cash'],min_equity=x['min_tick_equity'],worst_hour=x['worst_hour_drawdown'],
      trades=x['trades_closed'],stopout_events=x['forced_events'],peak_open=x['peak_open'],
      denied=x['denied']);out.append(row)
  print('DONE',d,'cash',round(row['final'],3),'trades',row['trades'],'secs',round(time.time()-start,2),flush=True)
 summary=dict(n=len(out),nonruin=sum(x['min_equity']>0 for x in out),no_stopouts=sum(x['stopout_events']==0 for x in out),
    positive=sum(x['final']>100 for x in out),min_final=min(x['final'] for x in out),max_final=max(x['final'] for x in out),
    total_trades=sum(x['trades'] for x in out),worst_hour=max(x['worst_hour'] for x in out),seven_day_10000=sum(x['final']>=10000 for x in out))
 result=dict(id='GRID0332_EARNED_CASH_COVERAGE_ONLY_SHOCK_CAPACITY',status='UNPROMOTED_NOT_ENDOGENOUS_JAN',config=dict(initial_cap=2,early_cap_coverage_only=8,min_prior_booked_cash=150.,shock5s=1.,margin_fraction=.20),sample_dates=days,source_original=origin,summary=summary,episodes=out,elapsed_seconds=time.time()-start)
 (ROOT/'grid0332_profit_funded_shock_slots_results.json').write_text(json.dumps(result,indent=2))
 print('SUMMARY',json.dumps(summary),flush=True)
if __name__=='__main__':main()

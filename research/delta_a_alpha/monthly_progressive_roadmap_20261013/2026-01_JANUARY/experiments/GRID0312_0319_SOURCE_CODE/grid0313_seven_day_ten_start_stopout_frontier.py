"""GRID0313 seven *complete* UTC-day windows (no hindsight) in January.
Ten seed-selected starts from the trading dates whose full 7-calendar-day window is
inside original January source; never search results to choose favorable starts.
Tests defensive early-liquidation and hypothetical broker stopout separately.
"""
import sys,time,json,hashlib
from pathlib import Path
import numpy as np
import grid0312_tick_stopout_executable as sim
from grid0307_random_start_lowcapital_original_tick import TICK_SOURCE
ROOT=Path(__file__).resolve().parent
SEED=20261014;HORIZON_DAYS=7
POLICIES=[
 ('S20_BROKER50_WORST',.20,.50,0.,'worst_first'),
 ('S20_BROKER100_WORST',.20,1.0,0.,'worst_first'),
 ('S20_DEFENSIVE200_WORST',.20,.50,2.0,'worst_first'),
 ('S20_DEFENSIVE300_FLATTEN',.20,.50,3.0,'flatten'),
 ('S25_DEFENSIVE200_WORST',.25,.50,2.0,'worst_first'),
 ('S30_DEFENSIVE300_WORST',.30,.50,3.0,'worst_first'),
]

def select_days(r9,t):
    last=int(t[-1]);days=sorted(r9['daily']);eligible=[d for d in days if int(np.datetime64(d+'T00:00:00','ms').astype('int64'))+HORIZON_DAYS*86400000<=last]
    assert len(eligible)>=10,(eligible,last)
    picked=sorted(np.random.default_rng(SEED).choice(eligible,10,replace=False).tolist())
    return eligible,picked

def main():
 st=time.time();t,b,a,z,kind,owner,pgid,r9,orig=sim.prior.g.g.base.p.ancestor.base.materialize()
 eligible,days=select_days(r9,t)
 print('SEED',SEED,'eligible',eligible,'PICKED',days,flush=True)
 episode=[]
 for d in days:
  lo=int(np.searchsorted(t,int(np.datetime64(d+'T00:00:00','ms').astype('int64')),'left'))
  hi=int(np.searchsorted(t,int(np.datetime64(d+'T00:00:00','ms').astype('int64'))+HORIZON_DAYS*86400000,'left'))
  assert hi<=len(t) and hi>lo
  mask=(z['entry_idx']>=lo)&(z['entry_idx']<hi)&(z['exit_idx']<len(t))
  zz={k:v[mask].copy() for k,v in z.items()}
  # Clamped future scheduled exits to window-end: if a position remains, it will
  # physically close on last quote, using current opposing Bid/Ask, not its hindsight exit.
  zz['entry_idx']-=lo
  zz['exit_idx']=np.minimum(zz['exit_idx']-lo,hi-lo-1)
  keep=zz['entry_idx']<zz['exit_idx']
  zz={k:v[keep] for k,v in zz.items()};kk=kind[mask][keep];oo=owner[mask][keep]
  # CRITICAL: would-be scheduled cash for positions truncated to seven-day boundary
  # must be repriced to last observable raw opposing executable quote.
  truncated=(z['exit_idx'][mask][keep]>=hi)
  eb=b[lo:hi];ea=a[lo:hi];et=t[lo:hi]
  for j in np.flatnonzero(truncated):
   ix=int(zz['exit_idx'][j]);direction=int(zz['direction'][j]);
   exit_px=int(eb[ix] if direction>0 else ea[ix]);en=int(zz['entry_price_raw'][j]);
   zz['net_cash'][j]=((exit_px-en)*direction)/1000.-.20
  assert np.all(zz['exit_idx']>zz['entry_idx'])
  for name,frac,stop,defense,style in POLICIES:
   x=sim.run(et,eb,ea,zz,kk,oo,pgid,cash=100.,admission_margin_fraction=frac,stopout_ratio=stop,
         defensive_ratio=defense,liquidation_style=style,defensive_flatten=style=='flatten')
   ledger=x.pop('booked_ledger');accepted=x.pop('accepted_indices')
   x.update(date=d,policy=name,execution_model='original Bid/Ask quotes 7 complete UTC days',
           min_earned_10000_7days=x['final_cash']>=10000.,num_accepted=len(accepted),
           forced_close_count=sum(1 for u in ledger if u[3]=='forced'),
           defensive_close_count=sum(1 for u in ledger if u[3]=='defensive'),
           clean_without_broker_stopout=x['forced_events']==0,
           modeled_nonruin=x['min_tick_equity']>0,
           sample_ticks=len(et),truncated_horizon_candidates=int(truncated.sum()))
   episode.append(x)
   print(d,name,'cash',round(x['final_cash'],2),'N',x['trades_closed'],'minEQ',round(x['min_tick_equity'],2),'minRatio',round(x['min_margin_ratio_observed'] or 0,2),
      'stopouts',x['forced_events'],'defensive',x['defensive_events'],'maxhourDD',round(x['worst_hour_drawdown'],2),flush=True)
 summary={}
 for name,*_ in POLICIES:
  q=[v for v in episode if v['policy']==name]
  summary[name]={'starts':len(q),'nonruin':sum(v['modeled_nonruin'] for v in q),
    'no_broker_stopout':sum(v['clean_without_broker_stopout'] for v in q),
    '10000_7days':sum(v['min_earned_10000_7days'] for v in q),
    'min_close_equity':min(v['final_cash'] for v in q),'max_close_equity':max(v['final_cash'] for v in q),
    'lowest_ticked_equity':min(v['min_tick_equity'] for v in q),
    'max_worst_hourly_dd':max(v['worst_hour_drawdown'] for v in q),
    'trades':sum(v['trades_closed'] for v in q),
    'broker_stopout_events':sum(v['forced_events'] for v in q)}
 out={'id':'GRID0313_TEN_SEEDED_JAN_SEVEN_COMPLETE_DAYS_REAL_BOOKED_LIQUIDATION',
      'status':'UNPROMOTED_SEVEN_DAY_SOURCE_CANDIDATES_HISTORICALLY_SELECTED',
      'date_seed':SEED,'eligible_dates':eligible,'sample_dates':days,'start_cash':100.,
      'month_tick_source_sha256':hashlib.file_digest(TICK_SOURCE.open('rb'),'sha256').hexdigest(),
      'limitations':['Broker margin at 500:1, stop-out ratio, per-position liquidation priority and fill slippage are hypothetical',
        'Potential intra-quote execution slippage beyond quoted Bid/Ask not priced (stress separately)',
        'Historically chosen source candidates and scheduled exits, NOT an endogenous V1 runtime',
        'Samples are ten historical episodes, not proof of future 100% survival',
        'Seven calendar-day horizon, not a set of 7 trading days or previous month-end horizon',
        'A 10000 target is a measured aspiration, never permitted as signal feature'],
      'policies':POLICIES,'summary':summary,'episodes':episode,'elapsed_seconds':round(time.time()-st,3)}
 file=ROOT/'grid0313_seven_day_100usd_stopout_froniter.json';file.write_text(json.dumps(out,indent=2))
 print('SAVED',file,'ELAPSED',time.time()-st,flush=True)
if __name__=='__main__':main()

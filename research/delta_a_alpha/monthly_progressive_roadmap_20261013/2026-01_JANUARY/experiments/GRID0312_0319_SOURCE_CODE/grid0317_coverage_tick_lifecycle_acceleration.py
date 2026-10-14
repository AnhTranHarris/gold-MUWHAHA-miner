"""GRID0317 causal coverage source portfolio slot-recycling research.

Only for coverage_gc0 / coverage_gc2 (independently identified as positive after-cost
in GRID0316 booked trials). TP, SL, time-out evaluated on actual executable Bid/Ask,
never on future MFE/MAE at admission. Other source exits unchanged. Every order
remains 0.01 lot; dynamic exit only changes duration and at-time settled PnL.

Research caveat: source candidates remain from original historically inspected
January source search; not a fully endogenous month-blind L0-L7 generator.
"""
import json,time
from pathlib import Path
import numpy as np
from numba import njit
import grid0313_seven_day_ten_start_stopout_frontier as p
ROOT=Path(__file__).resolve().parent

@njit(cache=True)
def causal_exit_pass(t,bid,ask,E,X,R,D,filtered_idx,tp_usd,sl_usd,hold_ms,exit_out,pnl_out):
 for ii in range(len(filtered_idx)):
  j=int(filtered_idx[ii]);start=int(E[j]);x=int(X[j]);dr=int(D[j]);en=int(R[j]);
  if hold_ms>0:
   stopms=int(t[start])+int(hold_ms)
  else:stopms=9223372036854775807
  newx=x
  for k in range(start+1,x+1):
   px=int(bid[k]) if dr>0 else int(ask[k]);net=dr*(px-en)/1000.-.20
   if (tp_usd>0 and net>=tp_usd) or (sl_usd>0 and net<=-sl_usd) or int(t[k])>=stopms:
    newx=k;break
  out=int(bid[newx]) if dr>0 else int(ask[newx])
  exit_out[j]=newx;pnl_out[j]=dr*(out-en)/1000.-.20

POLICIES=[
 ('CONTROL_PRESERVED_EXIT',0.,0.,0),
 ('GC0GC2_TP2_SL2_60S',2.,2.,60000),
 ('GC0GC2_TP4_SL3_120S',4.,3.,120000),
 ('GC0GC2_TP6_SL4_180S',6.,4.,180000),
 ('GC0GC2_TP3_SL5_60S',3.,5.,60000),
 ('GC0GC2_TP8_SL6_240S',8.,6.,240000)
]

def main():
 st=time.time();t,bid,ask,z,kind,owner,pgid,r9,orig=p.sim.prior.g.g.base.p.ancestor.base.materialize()
 eligible,days=p.select_days(r9,t)
 assert days==json.load(open(ROOT/'grid0313_seven_day_100usd_stopout_froniter.json'))['sample_dates']
 target=np.flatnonzero(np.isin(z['source'],['coverage_gc0','coverage_gc2']))
 print('ORIGINAL SOURCE TARGET',len(target),'of',len(z['entry_idx']),'candidate trades',flush=True)
 all_episodes=[];source_triggers={}
 for name,tp,sl,hold in POLICIES:
  if tp==0:
   ex=z['exit_idx'];pnl=z['net_cash']
  else:
   ex=z['exit_idx'].copy();pnl=z['net_cash'].copy()
   causal_exit_pass(t,bid,ask,z['entry_idx'],z['exit_idx'],z['entry_price_raw'],z['direction'],target,tp,sl,hold,ex,pnl)
  source_triggers[name]={'changed_count':int(np.sum(ex[target]!=z['exit_idx'][target])),
                         'source_raw_earlier_monetization_net_change':float(np.sum(pnl[target]-z['net_cash'][target]))}
  for day in days:
   d=int(np.datetime64(day+'T00:00:00','ms').astype('int64'))
   lo=int(np.searchsorted(t,d,'left'));hi=int(np.searchsorted(t,d+7*86400000,'left'))
   mask=(z['entry_idx']>=lo)&(z['entry_idx']<hi)
   zz={k:v[mask].copy() for k,v in z.items()}
   zz['exit_idx']=ex[mask].copy();zz['net_cash']=pnl[mask].copy();zz['entry_idx']-=lo
   trunc=zz['exit_idx']>=hi;zz['exit_idx']=np.minimum(zz['exit_idx']-lo,hi-lo-1)
   keep=zz['entry_idx']<zz['exit_idx'];zz={k:v[keep] for k,v in zz.items()};kk=kind[mask][keep];oo=owner[mask][keep];trunc=trunc[keep]
   et=t[lo:hi];bb=bid[lo:hi];aa=ask[lo:hi]
   for j in np.flatnonzero(trunc):
    x=int(zz['exit_idx'][j]);dr=int(zz['direction'][j]);out=int(bb[x] if dr>0 else aa[x]);en=int(zz['entry_price_raw'][j]);zz['net_cash'][j]=dr*(out-en)/1000.-.20
   r=p.sim.run(et,bb,aa,zz,kk,oo,pgid,cash=100.,admission_margin_fraction=.20,stopout_ratio=.5,
             defensive_ratio=0.,liquidation_style='worst_first')
   r.pop('booked_ledger');r.pop('accepted_indices')
   r.update(day=day,policy=name,seven_day_target_met=bool(r['final_cash']>=10000.),
            survival_observed=bool(r['min_tick_equity']>0. and r['forced_events']==0))
   all_episodes.append(r)
   print(name,day,'final',round(r['final_cash'],2),'trades',r['trades_closed'],
         'min eq',round(r['min_tick_equity'],2),'hourDD',round(r['worst_hour_drawdown'],2),flush=True)
 summary={}
 for name,*_ in POLICIES:
  a=[x for x in all_episodes if x['policy']==name]
  summary[name]={'survival_out_of_ten':sum(x['survival_observed'] for x in a),
                 'target_10000_count':sum(x['seven_day_target_met'] for x in a),
                 '7d_ending_range':[min(x['final_cash'] for x in a),max(x['final_cash'] for x in a)],
                 'max_worst_hour_dd':max(x['worst_hour_drawdown'] for x in a),
                 'completed_trade_count':sum(x['trades_closed'] for x in a),
                 'gross_loss_sum':sum(x['net_cash'] for x in a if x['net_cash']<0),
                 'improved_over_baseline_starts':sum(x['final_cash']>next(y['final_cash'] for y in all_episodes if y['policy']=='CONTROL_PRESERVED_EXIT' and y['day']==x['day']) for x in a)}
 path=ROOT/'grid0317_coverage_short_cycle_ten_starts.json';path.write_text(json.dumps({
    'id':'GRID0317_AFTER_COST_CAUSAL_COVERAGE_TICK_LIFECYCLE_ACCELERATOR',
    'source_genealogy':'preserved fully processed GRID0283 parent-child original Dukascopy January tick sources',
    'status':'UNPROMOTED_HISTORICALLY_SELECTED_SOURCE_POPULATION_NOT_OUT_OF_SAMPLE',
    'source_changes':source_triggers,'sample_dates':days,'policies':POLICIES,'summary':summary,
    'all_episodes':all_episodes,'elapsed_seconds':round(time.time()-st,2)},indent=2));print('SAVED',path,flush=True)
if __name__=='__main__':main()

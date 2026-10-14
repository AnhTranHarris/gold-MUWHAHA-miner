"""GRID0339: purely R8-inspired one-position-at-all-times risk control.
Historic January source events remain preselected (never assert new entry-edge).
Fixed 0.01 lot, ten random $100 seven-day original Dukascopy quote episodes.
"""
from pathlib import Path
import json,sys,time
import numpy as np
ROOT=Path('/mnt/data/r8_followup_20261014')
sys.path.insert(0,'/mnt/data/jan_work/engine')
import grid0324_source_conditioned_pre_request_routing as sim
import grid0313_seven_day_ten_start_stopout_frontier as cohort
from grid0330_initial_capacity_survival_sweep import ALL_ORD

def main():
 now=time.time();z0=np.load(ROOT/'original_research_candidate_unfiltered_cache.npz');z={k:z0[k] for k in ('entry_idx','exit_idx','entry_price_raw','direction','net_cash','source')};kk=z0['kind'];owner=z0['owner'];pgid=z0['pgid']
 P=Path('/mnt/data/R8_JAN_DUKAS_RESEARCH');t=np.load(P/'ticks_t.npy',mmap_mode='r');bid=np.load(P/'ticks_bid.npy',mmap_mode='r');ask=np.load(P/'ticks_ask.npy',mmap_mode='r');r9=json.loads(Path('/mnt/data/jan_recovery_20261013/ORIGINAL/r9_synth_jan_daily_weekly.json').read_text());_,days=cohort.select_days(r9,t)
 rr=[]
 for day in days:
  d=int(np.datetime64(day+'T00:00:00','ms').astype('int64'));lo=int(np.searchsorted(t,d));hi=int(np.searchsorted(t,d+7*86400000));tt=np.asarray(t[lo:hi]);b=np.asarray(bid[lo:hi]);a=np.asarray(ask[lo:hi]);mask=(z['entry_idx']>=lo)&(z['entry_idx']<hi);q={k:v[mask].copy() for k,v in z.items()};k=kk[mask];o=owner[mask];q['entry_idx']-=lo;clamp=q['exit_idx']>=hi;q['exit_idx']=np.minimum(q['exit_idx']-lo,hi-lo-1);valid=q['entry_idx']<q['exit_idx'];q={key:v[valid] for key,v in q.items()};k=k[valid];o=o[valid];clamp=clamp[valid]
  for j in np.flatnonzero(clamp):
    ix=int(q['exit_idx'][j]);dr=int(q['direction'][j]);q['net_cash'][j]=dr*(int(b[ix] if dr>0 else a[ix])-int(q['entry_price_raw'][j]))/1000.-.20
  pre,shock=sim.features(tt,b,a)
  x=sim.run(tt,b,a,q,k,o,pgid,cash=100.,initial_cap=1,earned_cash_tiers=((100.,1),),cap=1,admission_margin_fraction=.20,stopout_ratio=.5,screen_quote_idx=pre,pre_request_shock_5s=shock,min_observed_5s_shock=.5,screen_sources=ALL_ORD)
  ent=dict(date=day,final_cash=x['final_cash'],trades=x['trades_closed'],min_equity=x['min_tick_equity'],worst_hour_dd=x['worst_hour_drawdown'],max_tick_dd=x['max_tick_drawdown'],stopouts=x['forced_events'],peak_open=x['peak_open']);rr.append(ent)
  print(day,round(ent['final_cash'],2),ent['trades'],round(ent['worst_hour_dd'],2),round(time.time()-now,1),flush=True)
 sm={'starts':len(rr),'nonruin':sum(x['min_equity']>0 for x in rr),'no_stopout':sum(x['stopouts']==0 for x in rr),'positive':sum(x['final_cash']>100 for x in rr),'hit10000_7days':sum(x['final_cash']>=10000 for x in rr),'min_final':min(x['final_cash'] for x in rr),'max_final':max(x['final_cash'] for x in rr),'trade_count_total':sum(x['trades'] for x in rr),'worst_hour_dd':max(x['worst_hour_dd'] for x in rr),'max_tick_dd':max(x['max_tick_dd'] for x in rr),'max_positions':max(x['peak_open'] for x in rr)}
 result=dict(state='RESEARCH_ONLY',source='Dukascopy Jan 2026 with historically-selected GRID0283 source candidates, no endogenous R8 signal',policy='R8_STRICT_MAX_ONE_AT_ALL_BALANCES',summary=sm,episodes=rr,minutes=(time.time()-now)/60)
 (ROOT/'grid0339_r8_strict_single_position_results.json').write_text(json.dumps(result,indent=2));print('SUMMARY',json.dumps(sm),flush=True)
if __name__=='__main__':main()

"""GRID0340: R8 strict single-asset rule with strictly earned permission for second ticket.
Entry candidate universe originated from historically selected Jan source, not endogenous.
Research-only; original Jan Dukascopy tick replay, 10 seeded $100 7d periods.
"""
import json,time,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,'/mnt/data/jan_work/engine')
import grid0324_source_conditioned_pre_request_routing as sim
import grid0313_seven_day_ten_start_stopout_frontier as cohort
from grid0330_initial_capacity_survival_sweep import ALL_ORD
ROOT=Path('/mnt/data/r8_followup_20261014')
POLICIES={'R8_CAP1':((100.,1),),'EARNED_110':((100.,1),(110.,2)),'EARNED_125':((100.,1),(125.,2)),'EARNED_150':((100.,1),(150.,2))}
def main():
 st=time.time();z0=np.load(ROOT/'original_research_candidate_unfiltered_cache.npz');z={key:z0[key] for key in ('entry_idx','exit_idx','entry_price_raw','direction','net_cash','source')};kind=z0['kind'];owner=z0['owner'];pgid=z0['pgid'];p=Path('/mnt/data/R8_JAN_DUKAS_RESEARCH');t=np.load(p/'ticks_t.npy',mmap_mode='r');b=np.load(p/'ticks_bid.npy',mmap_mode='r');a=np.load(p/'ticks_ask.npy',mmap_mode='r');r9=json.loads(Path('/mnt/data/jan_recovery_20261013/ORIGINAL/r9_synth_jan_daily_weekly.json').read_text());_,days=cohort.select_days(r9,t);rows=[]
 for day in days:
  d=int(np.datetime64(day+'T00:00:00','ms').astype('int64'));lo=int(np.searchsorted(t,d));hi=int(np.searchsorted(t,d+7*86400000));tt=np.asarray(t[lo:hi]);bid=np.asarray(b[lo:hi]);ask=np.asarray(a[lo:hi]);mask=(z['entry_idx']>=lo)&(z['entry_idx']<hi);zz={key:v[mask].copy() for key,v in z.items()};kk=kind[mask];oo=owner[mask];zz['entry_idx']-=lo;tr=zz['exit_idx']>=hi;zz['exit_idx']=np.minimum(zz['exit_idx']-lo,hi-lo-1);ok=zz['entry_idx']<zz['exit_idx'];zz={key:v[ok] for key,v in zz.items()};kk=kk[ok];oo=oo[ok];tr=tr[ok]
  for j in np.flatnonzero(tr):
   ix=int(zz['exit_idx'][j]);dr=int(zz['direction'][j]);zz['net_cash'][j]=dr*(int(bid[ix] if dr>0 else ask[ix])-int(zz['entry_price_raw'][j]))/1000.-.20
  pre,shock=sim.features(tt,bid,ask)
  for name,tiers in POLICIES.items():
   x=sim.run(tt,bid,ask,zz,kk,oo,pgid,cash=100.,initial_cap=1,earned_cash_tiers=tiers,cap=2 if len(tiers)>1 else 1,admission_margin_fraction=.20,stopout_ratio=.5,screen_quote_idx=pre,pre_request_shock_5s=shock,min_observed_5s_shock=.5,screen_sources=ALL_ORD)
   row={k:x[k] for k in ('final_cash','trades_closed','min_tick_equity','max_tick_drawdown','worst_hour_drawdown','forced_events','peak_open')};row.update(day=day,policy=name);rows.append(row);print('DONE',day,name,round(x['final_cash'],3),x['trades_closed'],round(x['worst_hour_drawdown'],3),round(time.time()-st,1),flush=True)
 summ={}
 for name in POLICIES:
  q=[v for v in rows if v['policy']==name]
  summ[name]={'positive':sum(v['final_cash']>100 for v in q),'nonruin':sum(v['min_tick_equity']>0 for v in q),'no_stopouts':sum(v['forced_events']==0 for v in q),'ntrades':sum(v['trades_closed'] for v in q),'min_final':min(v['final_cash'] for v in q),'max_final':max(v['final_cash'] for v in q),'worst_hour_dd':max(v['worst_hour_drawdown'] for v in q),'full_tick_dd':max(v['max_tick_drawdown'] for v in q),'max_positions':max(v['peak_open'] for v in q),'10k_7day':sum(v['final_cash']>=10000 for v in q)}
 out=dict(status='UNPROMOTED_RESEARCH_ONLY',cohort=days,source='original Dukascopy with January retrospectively-selected producer',settings={name:tiers for name,tiers in POLICIES.items()},summary=summ,episodes=rows,limitations=['Original historically selected candidate universe, not source-generated V1','500:1 hypothetical 1oz/0.01lot, broker-specific economics unconfirmed','Overlapping 7d sample windows not statistically independent','No market discontinuity guarantee'])
 (ROOT/'grid0340_r8_strict_to_earned_2slot_results.json').write_text(json.dumps(out,indent=2));print('SUMMARY',json.dumps(summ),flush=True)
if __name__=='__main__':main()

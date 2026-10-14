"""GRID0336: R8 one-at-a-time micro-account until booked equity earns limited concurrent slots.
Inherently hypothetical GRID0325 source candidate universe, not endogenous signal producer.
Use 10 seed-fixed 7-day windows with original raw Dukascopy Bid/Ask and physical stopout.
"""
import json,time,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from grid0335_r8_directional_efficiency_combination import r8_asof_micro
sys.path.insert(0,'/mnt/data/jan_work/engine')
import grid0324_source_conditioned_pre_request_routing as sim
import grid0313_seven_day_ten_start_stopout_frontier as cohort
from grid0330_initial_capacity_survival_sweep import ALL_ORD
P=Path('/mnt/data/r8_followup_20261014');DAY=86400000
# No level is selected based on the calendar or future profits.
POLICIES={
'BASE_TWO':(((100.,2),(150.,4),(300.,8),(500.,16),(1000.,32),(2000.,64)),0.,False),
'R8_INITIAL_ONE':(((100.,1),(150.,2),(300.,4),(500.,8),(1000.,16),(2000.,64)),0.,False),
'ONE_EARNED_110':(((100.,1),(110.,2),(200.,4),(500.,8),(1000.,16),(2000.,64)),0.,False),
'ONE_EARNED_125':(((100.,1),(125.,2),(250.,4),(500.,8),(1000.,16),(2000.,64)),0.,False),
'ONE_EARNED_140':(((100.,1),(140.,2),(280.,4),(500.,8),(1000.,16),(2000.,64)),0.,False),
#'ONE_EARNED_110_EFF60':(((100.,1),(110.,2),(200.,4),(500.,8),(1000.,16),(2000.,64)),.6,False),
#'ONE_EARNED_125_EFF60':(((100.,1),(125.,2),(250.,4),(500.,8),(1000.,16),(2000.,64)),.6,False),
}

def main():
 start=time.time();Q=np.load(P/'original_research_candidate_unfiltered_cache.npz')
 z={k:Q[k] for k in ('entry_idx','exit_idx','entry_price_raw','direction','net_cash','source')};kind=Q['kind'];owner=Q['owner'];pgid=Q['pgid']
 m=Path('/mnt/data/R8_JAN_DUKAS_RESEARCH')
 t=np.load(m/'ticks_t.npy',mmap_mode='r');bid=np.load(m/'ticks_bid.npy',mmap_mode='r');ask=np.load(m/'ticks_ask.npy',mmap_mode='r')
 r9=json.loads(Path('/mnt/data/jan_recovery_20261013/ORIGINAL/r9_synth_jan_daily_weekly.json').read_text());_,days=cohort.select_days(r9,t)
 rows=[]
 for day in days:
  d=int(np.datetime64(day+'T00:00:00','ms').astype('int64'));lo=int(np.searchsorted(t,d));hi=int(np.searchsorted(t,d+7*DAY));tt=np.asarray(t[lo:hi]);b=np.asarray(bid[lo:hi]);a=np.asarray(ask[lo:hi]);mask=(z['entry_idx']>=lo)&(z['entry_idx']<hi)
  zz={k:v[mask].copy() for k,v in z.items()};kk=kind[mask];oo=owner[mask];zz['entry_idx']-=lo;trunc=zz['exit_idx']>=hi;zz['exit_idx']=np.minimum(zz['exit_idx']-lo,hi-lo-1);valid=zz['entry_idx']<zz['exit_idx']
  zz={k:v[valid] for k,v in zz.items()};kk=kk[valid];oo=oo[valid];trunc=trunc[valid]
  for j in np.flatnonzero(trunc):
   ix=int(zz['exit_idx'][j]);dr=int(zz['direction'][j]);zz['net_cash'][j]=dr*(int(b[ix] if dr>0 else a[ix])-int(zz['entry_price_raw'][j]))/1000.-.20
  pre,shock=sim.features(tt,b,a)
  _,disp,eff=r8_asof_micro(tt,b,a,zz['entry_idx']);ordinary=(kk==0)&np.isin(zz['source'],list(ALL_ORD))
  for name,(tiers,threshold,_) in POLICIES.items():
   keep=np.ones(len(kk),bool)
   if threshold:keep[ordinary]&=eff[ordinary]>=threshold
   zf={k:v[keep] for k,v in zz.items()};kf=kk[keep];of=oo[keep]
   result=sim.run(tt,b,a,zf,kf,of,pgid,cash=100.,initial_cap=int(tiers[0][1]),earned_cash_tiers=tiers,admission_margin_fraction=.20,stopout_ratio=.5,screen_quote_idx=pre,pre_request_shock_5s=shock,min_observed_5s_shock=.5,screen_sources=ALL_ORD)
   record={key:result[key] for key in ['final_cash','trades_closed','min_tick_equity','max_tick_drawdown','worst_hour_drawdown','forced_events','min_margin_ratio_observed','peak_open','net_cash']};record.update(date=day,policy=name,prefilter_removed=int(np.sum(~keep)),no_stopout=result['forced_events']==0,positive=result['final_cash']>100,nonruin=result['min_tick_equity']>0)
   rows.append(record)
   print('DATE',day,'POL',name,'cash',round(result['final_cash'],3),'trades',result['trades_closed'],'worsthour',round(result['worst_hour_drawdown'],3),'secs',round(time.time()-start,2),flush=True)
 sm={}
 for policy in POLICIES:
  q=[x for x in rows if x['policy']==policy]
  sm[policy]={"survive":sum(x['nonruin'] and x['no_stopout'] for x in q),"positive":sum(x['positive'] for x in q),"min_final":min(x['final_cash'] for x in q),"max_final":max(x['final_cash'] for x in q),"total_trades":sum(x['trades_closed'] for x in q),"worst_hour":max(x['worst_hour_drawdown'] for x in q),"max_tick_dd":max(x['max_tick_drawdown'] for x in q),"reach10000":sum(x['final_cash']>=10000 for x in q)}
 print('SUMMARY',json.dumps(sm),flush=True)
 path=P/'grid0336_r8_singleton_earned_safe_results.json';path.write_text(json.dumps({'unpromoted':True,'source':'original Dukascopy Bid/Ask + historical research candidates', 'dates':days,'modeled_contract':{'leverage':500,'lot':.01,'notional_oz':1,'fee':.20,'margin_admission':.20,'stopout_ratio':.5},'important_limitations':['source cells historically selected using Jan outcomes; not blind/independent producer','future scheduled exits from source study; not live endogenous lifecycle','Coinexx contract/stopout not independently verified','ten overlapping seeded windows do not imply future survival probability'],'settings':{k:v[0] for k,v in POLICIES.items()},'summary':sm,'episodes':rows},indent=2))
 print('SAVED',path,'seconds',time.time()-start,flush=True)
if __name__=='__main__':main()

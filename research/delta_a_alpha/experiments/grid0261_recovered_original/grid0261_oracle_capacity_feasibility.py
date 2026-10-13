"""OFFLINE SOURCE DENSITY upper bound, NOT broker funded; hindsight max profit.
Greedy earliest positive quote sample, fixed 60-sec committed capacity occupancy;
counts ignored calendar months when admission made, only UTC chronological.
"""
from grid0261_60pct_r9_oracle_reachability import oracle_events
from grid0261_intrinsic_time_research import load_month
import numpy as np, heapq, json, time
from pathlib import Path
out=Path('/mnt/data/grid0261_intrinsic')
results={};tickcount=0;all_possible=0
for month in range(1,8):
 t,a,b=load_month(month);x,c=oracle_events(t,a,b)
 eligible=x[np.maximum(x[:,2],x[:,3])>=2100]
 d={}
 for cap in (1,2,4,5,6,7,8,16):
  active=[];n=0
  for idx in eligible[:,0]:
   stamp=int(t[idx]);
   while active and active[0]<=stamp:heapq.heappop(active)
   if len(active)<cap:
    n+=1;heapq.heappush(active,stamp+60000)
  d[str(cap)]={'admissible_hindsight_candidates_60s_occupancy':n,'share_of_nonphysical_eligible':round(n/max(1,len(eligible)),4)}
 results[str(month)]={'original_tick_count':int(len(t)),'hindsight_nonoverlap_2p1_candidates':int(len(eligible)),'fixed_exit_60sec_slot_density_upper_by_slot':d}
 print(month,results[str(month)],flush=True)
 del t,a,b,x
results['important_interpretation']='This is an OFFLINE hindsight-direction-and-best-exit candidate filter; 60s positions occupy their slots even if earlier hindsight target could be found. IT IS NOT A CAUSAL FILLED PORTFOLIO, NOR AN UPPER BOUND on all possible strategies; it is a ceiling for precisely this sampled oracle-selected candidate population. Execution fee and spread in candidate threshold, but no actual funded margin/impact/verified spread.'
results['sixty_pct_completed_trade_goal']=131606
for cap in (1,2,4,5,6,7,8,16):results[f'total_hindsight_60s_occupancy_{cap}_slot']=sum(results[str(k)]['fixed_exit_60sec_slot_density_upper_by_slot'][str(cap)]['admissible_hindsight_candidates_60s_occupancy'] for k in range(1,8))
(out/'GRID0261_ORACLE_OVERLAP_AND_60PCT_SLOT_FEASIBILITY.json').write_text(json.dumps(results,indent=2))

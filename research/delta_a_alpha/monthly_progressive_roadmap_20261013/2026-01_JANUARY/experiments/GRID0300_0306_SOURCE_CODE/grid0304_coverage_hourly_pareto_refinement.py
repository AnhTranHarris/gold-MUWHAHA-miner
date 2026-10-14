"""GRID0304: distinct source-concentration/Watchdog-hour pressure Pareto combinations.
All inputs are original January Bid/Ask source and preserved original candidates.
Optimization/selection is OFFLINE; runtime source code cannot see R9 target labels.
"""
from pathlib import Path
import json,time
import grid0303_causal_coverage_source_caps as g
ROOT=Path(__file__).resolve().parent

def main():
 st=time.perf_counter();t,bid,ask,z,kind,owner,pgid,r9,origin=g.g.base.p.ancestor.base.materialize()
 pairs=[(216,216),(224,224),(232,232),(240,240),(248,248),(256,256),
        (224,240),(240,224),(232,248),(248,232),(224,256),(256,224)]
 configs=[(c0,c2,s) for c0,c2 in pairs for s in [100.,400.,800.]]
 results=[]
 for i,(c0,c2,soft) in enumerate(configs):
  name=f'G0{c0}_G2{c2}_PARENT_PRESSURE{soft:g}'
  r=g.run(t,bid,ask,z,kind,owner,pgid,r9,name,c0,c2,soft,64)
  results.append(r)
  d=sum(v['net']>0 for v in r['daily'].values());w=sum(v['net']>0 for v in r['weekly'].values());qual=r['net']>=r['r9_synth_month_target'] and d==21 and w==5
  print(i,name,'net',round(r['net'],2),'n',r['trades'],'max_hourly_DD',round(r['max_hourly_tick_equity_drawdown_usd'],2),
       'fullDD',round(r['max_all_tick_floating_equity_dd'],2),'day/week',d,w,'R9 weekly',r['r9_synth_weeks_net_met'],'target',qual,flush=True)
 qualified=[r for r in results if r['net']>=r['r9_synth_month_target'] and all(v['net']>0 for v in r['daily'].values()) and all(v['net']>0 for v in r['weekly'].values())]
 pareto=[]
 for r in qualified:
  dominated=any((q['net']>=r['net'] and q['max_hourly_tick_equity_drawdown_usd']<=r['max_hourly_tick_equity_drawdown_usd'] and (q['net']>r['net'] or q['max_hourly_tick_equity_drawdown_usd']<r['max_hourly_tick_equity_drawdown_usd'])) for q in qualified)
  if not dominated:pareto.append(r)
 pareto.sort(key=lambda r:r['max_hourly_tick_equity_drawdown_usd'])
 print('QUALIFIED',len(qualified),'PARETO',[(r['name'],round(r['net'],1),round(r['max_hourly_tick_equity_drawdown_usd'],1)) for r in pareto],flush=True)
 out=ROOT/'grid0304_coverage_hourly_pareto_full_january.json'
 out.write_text(json.dumps({'id':'GRID0304_RISK_PROFIT_FRONTIER_SOURCE_CONCENTRATION_AND_INTRAHOUR_PRESSURE',
   'status':'ORIGINAL_TICK_HISTORICAL_RESEARCH_ONLY_NOT_OWNER_ACCEPTED','source_sha256':g.g.base.p.ancestor.base.back.SRC_SHA,
   'risk_priority':'minimize each UTC trading day peak-to-trough worst hour under cash-period consistency gates',
   'variants':results,'qualified':[r['name'] for r in qualified],'pareto':[r['name'] for r in pareto],
   'seconds':time.perf_counter()-st},indent=2))
 print('SAVED',out,'time',round(time.perf_counter()-st,1),flush=True)
if __name__=='__main__':main()

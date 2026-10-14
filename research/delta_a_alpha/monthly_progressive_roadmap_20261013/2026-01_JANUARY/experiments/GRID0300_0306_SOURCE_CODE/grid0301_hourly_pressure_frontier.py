"""GRID0301 distinct as-of earned-parent intrahour pressure cap frontier.
Baseline derived from original Grid0297, replayed on unmodified original Jan ticks.
Runs risk-only as-of parameter combinations; no R9 target is available to runtime logic.
"""
import json,time,math
from pathlib import Path
import grid0300_hourly_equity_governor as g
ROOT=Path(__file__).resolve().parent

def main():
 st=time.perf_counter();t,bid,ask,z,kind,owner,pgid,r9,origin=g.base.p.ancestor.base.materialize()
 tests=[]
 # Distinct pressure state and parent inventory caps, not repeated threshold-only tuning.
 for soft in [50,100,200,400,800,1200]:
  for softcap in [8,32,64,96,128]:
   tests.append((f'PRESSURE_{soft}_PARENT{softcap}',0,soft,softcap))
 # Coexisting irreversible within-hour new-entry lock, broad enough to retain profitable campaign.
 for hard in [900,1500,2400]:
  for soft,cap in [(100,32),(200,64),(400,64)]:
   tests.append((f'PRESSURE_{soft}_PARENT{cap}_STOP{hard}',hard,soft,cap))
 rows=[]
 for i,(name,hard,soft,cap) in enumerate(tests):
  r=g.run(t,bid,ask,z,kind,owner,pgid,r9,name,hard,soft,cap)
  rows.append(r)
  d=sum(v['net']>0 for v in r['daily'].values()); w=sum(v['net']>0 for v in r['weekly'].values())
  status=(r['net']>=r['r9_synth_month_target'] and d==21 and w==5)
  print(i,name,'net',round(r['net'],2),'trades',r['trades'],'hdd',round(r['max_hourly_tick_equity_drawdown_usd'],2),
       'p95',round(r['p95_hourly_tick_equity_drawdown_usd'],2),'full_dd',round(r['max_all_tick_floating_equity_dd'],2),
       'day+',d,'week+',w,'R9weeks',r['r9_synth_weeks_net_met'],'floor',status,flush=True)
 qualified=[r for r in rows if r['net']>=r['r9_synth_month_target'] and all(v['net']>0 for v in r['daily'].values()) and all(v['net']>0 for v in r['weekly'].values())]
 winners=sorted(qualified,key=lambda r:(r['max_hourly_tick_equity_drawdown_usd'],-r['net']))
 print('QUALIFIED',len(qualified),'TOP 10',[(x['name'],round(x['net'],1),round(x['max_hourly_tick_equity_drawdown_usd'],1),x['r9_synth_weeks_net_met']) for x in winners[:10]],flush=True)
 out=ROOT/'grid0301_hourly_pressure_combination_full_january.json'
 out.write_text(json.dumps({'id':'GRID0301_ORIGINAL_TICK_HOURLY_DRAWDOWN_PRESSURE_COMBINATION_FRONTIER',
 'status':'RESEARCH_ONLY_IN_SAMPLE_NO_INTEGRATION_OR_ACCEPTANCE',
 'source_sha256':g.base.p.ancestor.base.back.SRC_SHA,
 'scope':'UTC hourly realized+floating equity mark to market, 21 trading days, original 9,135,062 quotes',
 'variants':rows,'qualifying_names':[r['name'] for r in winners],'seconds':time.perf_counter()-st},indent=2))
 print('SAVED',out, 'secs',round(time.perf_counter()-st,1),flush=True)
if __name__=='__main__':main()

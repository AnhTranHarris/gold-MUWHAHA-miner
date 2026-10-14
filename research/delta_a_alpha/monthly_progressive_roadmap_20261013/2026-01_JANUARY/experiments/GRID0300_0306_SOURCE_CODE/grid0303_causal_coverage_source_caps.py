"""GRID0303 causal physical source-specific capacity for original gc0/gc2 L3.
Original full January Dukascopy ticks. No month/date outcome in runtime features.
Research only; preserve GRID0297/GRID0300 source bytes.
"""
import json,time,heapq
from pathlib import Path
from collections import deque,Counter
import numpy as np,pandas as pd
import grid0300_hourly_equity_governor as g
ROOT=Path(__file__).resolve().parent
source=g.source
old='hourly_soft_parent_cap=16):';new='hourly_soft_parent_cap=16,gc0_cap=0,gc2_cap=0):'
assert source.count(old)==1;source=source.replace(old,new)
anchor="        if typ==0 and loss_pause_n>0 and current<source_pause_until.get(str(z['source'][k]),-1):"
assert source.count(anchor)==1
source=source.replace(anchor,"""        if typ==0 and gc0_cap and str(z['source'][k])=='coverage_gc0' and live_by_source.get('coverage_gc0',0)>=gc0_cap:
            ledger_events['source_specific_gc0_cap']+=1;continue
        if typ==0 and gc2_cap and str(z['source'][k])=='coverage_gc2' and live_by_source.get('coverage_gc2',0)>=gc2_cap:
            ledger_events['source_specific_gc2_cap']+=1;continue
"""+anchor)
anchor="    r.update(hourly_entry_lock_usd=hourly_entry_lock_usd,hourly_soft_parent_usd=hourly_soft_parent_usd,"
assert source.count(anchor)==1;source=source.replace(anchor,"    r.update(gc0_cap=gc0_cap,gc2_cap=gc2_cap)\n"+anchor)
ns=dict(g.ns);exec(source,ns);replay=ns['physical_replay']

def run(t,bid,ask,z,kind,owner,pgid,r9,name,gc0,gc2,hours_parent=0.,hours_cap=16):
    t0=time.perf_counter()
    r=replay(t,bid,ask,z,kind,owner,pgid,r9,cash=100000.,cap=256,
             loss_pause_n=2,pause_ms=300000,native16_cap=2,earned_native_cap=32,
             earned_wins=7,earned_window=10,earned_edge=12,parent_cap=16,
             earned_parent_cap=192,parent_wins=4,parent_window=6,parent_edge=4,
             hourly_entry_lock_usd=0.,hourly_soft_parent_usd=hours_parent,hourly_soft_parent_cap=hours_cap,
             gc0_cap=gc0,gc2_cap=gc2)
    r['name']=name;r['seconds']=time.perf_counter()-t0
    return r

def main():
 st=time.perf_counter();t,bid,ask,z,kind,owner,pgid,r9,origin=g.base.p.ancestor.base.materialize()
 configs=[('GRID0297_CONTROL',0,0,0.,16),
          ('SOFT400_PARENT64_CONTROL',0,0,400.,64)]
 for src in ['gc0','gc2']:
  for cap in [32,64,96,128,160,192,224]:
   configs.append((f'SOURCE_{src.upper()}_CAP{cap}',cap if src=='gc0' else 0,cap if src=='gc2' else 0,0.,16))
 for cap0 in [64,128,192,224]:
  for cap2 in [64,128,192,224]:
   configs.append((f'GC0_{cap0}_GC2_{cap2}',cap0,cap2,0.,16))
 for cap0,cap2 in [(128,128),(160,160),(192,192),(224,224),(128,192),(192,128)]:
  configs.append((f'COMBINED_SOFT400_GC0_{cap0}_GC2_{cap2}',cap0,cap2,400.,64))
 results=[]
 for ix,(name,c0,c2,soft,pc) in enumerate(configs):
  r=run(t,bid,ask,z,kind,owner,pgid,r9,name,c0,c2,soft,pc)
  results.append(r)
  d=sum(x['net']>0 for x in r['daily'].values());w=sum(x['net']>0 for x in r['weekly'].values())
  valid=r['net']>=r['r9_synth_month_target'] and d==21 and w==5
  print(ix,name,'net',round(r['net'],2),'n',r['trades'],'maxhourdd',round(r['max_hourly_tick_equity_drawdown_usd'],2),
        'overalldd',round(r['max_all_tick_floating_equity_dd'],2),'grossloss',round(r['gross_loss'],2),
        'pos',d,w,'R9 weekly',r['r9_synth_weeks_net_met'],'passes',valid,flush=True)
 valid=[r for r in results if r['net']>=r['r9_synth_month_target'] and all(x['net']>0 for x in r['daily'].values()) and all(x['net']>0 for x in r['weekly'].values())]
 print('QUALIFIED',len(valid),'TOP',[(v['name'],round(v['net'],1),round(v['max_hourly_tick_equity_drawdown_usd'],1)) for v in sorted(valid,key=lambda a:a['max_hourly_tick_equity_drawdown_usd'])[:15]],flush=True)
 out=ROOT/'grid0303_coverage_source_inventory_full_january.json'
 out.write_text(json.dumps({'id':'GRID0303_ASOF_ORIGINAL_COVERAGE_NATIVE_GC0_GC2_PHYSICAL_SOURCE_CAPS',
       'status':'RESEARCH_ONLY_UNPROMOTED','source_sha256':g.base.p.ancestor.base.back.SRC_SHA,
       'variants':results,'qualified_ids':[x['name'] for x in valid],
       'source_context':'L3 coverage source cap independent of protected NY and funded Watchdog parent/governor',
       'seconds_total':time.perf_counter()-st},indent=2))
 print('SAVED',out,round(time.perf_counter()-st,1),flush=True)
if __name__=='__main__':main()

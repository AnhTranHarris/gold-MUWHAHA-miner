"""GRID0296: original tick source + funded Watchdog parent heat adaptive to CLOSED parent outcomes.
Only historical completed physically booked parent PnL opens extra parent slots;
rollback is immediate when evidence deteriorates; no calendar targets consulted.
Inherits exact J0295 cap/quote arithmetic; research-only.
"""
from pathlib import Path
from collections import deque,Counter
import heapq,json,time,numpy as np,pandas as pd
import grid0295_child_exposure_governor as p
SOURCE=p.source
SOURCE=SOURCE.replace('child_cap=0,parent_cap=0):','child_cap=0,parent_cap=0,earned_parent_cap=0,parent_wins=3,parent_window=6,parent_edge=0.0):')
SOURCE=SOURCE.replace('child_live=0;parent_live=0','child_live=0;parent_live=0;parent_recent=deque(maxlen=parent_window);parent_cap_earned_events=0')
SOURCE=SOURCE.replace('if kind[j]==1:parent_live-=1', 'if kind[j]==1:\n                parent_live-=1;parent_recent.append(net)')
SOURCE=SOURCE.replace("if typ==1 and parent_cap and parent_live>=parent_cap:", "if typ==1 and earned_parent_cap>parent_cap and parent_cap and len(parent_recent)>=parent_window and sum(q>0 for q in parent_recent)>=parent_wins and sum(parent_recent)>=parent_edge:\n            permitted_parent_cap=earned_parent_cap;parent_cap_earned_events+=1\n        else:\n            permitted_parent_cap=parent_cap\n        if typ==1 and permitted_parent_cap and parent_live>=permitted_parent_cap:")
SOURCE=SOURCE.replace('r.update(child_cap=child_cap,parent_cap=parent_cap,','r.update(child_cap=child_cap,parent_cap=parent_cap,earned_parent_cap=earned_parent_cap,parent_wins=parent_wins,parent_window=parent_window,parent_edge=parent_edge,parent_cap_earned_events=parent_cap_earned_events,')
namespace={'np':np,'pd':pd,'deque':deque,'Counter':Counter,'heapq':heapq,'back':p.ancestor.base.back,'json':json,'Path':Path,'ROOT':p.ancestor.base.ROOT,'time':time};exec(SOURCE,namespace)
physical_replay=namespace['physical_replay']

def main():
 t0=time.perf_counter();t,bid,ask,z,kind,owner,pgid,r9,origin=p.ancestor.base.materialize()
 configs=[('CONTROL_PARENT_NONE',0,0,3,6,0),('PARENT16',16,0,3,6,0),('PARENT32',32,0,3,6,0),
   ('PA16_RAISE32_4of6_4',16,32,4,6,4),('PA16_RAISE64_4of6_4',16,64,4,6,4),('PA16_RAISE96_4of6_4',16,96,4,6,4),
   ('PA16_RAISE128_4of6_4',16,128,4,6,4),('PA32_RAISE128_4of6_4',32,128,4,6,4),
   ('PA16_RAISE64_5of8_8',16,64,5,8,8),('PA16_RAISE128_5of8_8',16,128,5,8,8),
   ('PA32_RAISE128_5of8_8',32,128,5,8,8),('PA64_RAISE128_5of8_8',64,128,5,8,8),
   ('PA16_RAISE128_6of10_12',16,128,6,10,12),('PA32_RAISE128_6of10_12',32,128,6,10,12)]
 res=[]
 for name,cap,raised,wins,win,edge in configs:
  r=physical_replay(t,bid,ask,z,kind,owner,pgid,r9,cash=100000.,cap=256,loss_pause_n=2,pause_ms=300000,native16_cap=2,earned_native_cap=32,earned_wins=7,earned_window=10,earned_edge=12,parent_cap=cap,earned_parent_cap=raised,parent_wins=wins,parent_window=win,parent_edge=edge)
  r['name']=name;res.append(r)
  print(name,'net',round(r['net'],2),'N',r['trades'],'GL',round(r['gross_loss'],2),'DD',round(r['max_all_tick_floating_equity_dd'],2),'posdays',sum(v['net']>0 for v in r['daily'].values()),'posweeks',sum(v['net']>0 for v in r['weekly'].values()),'r9day',r['r9_synth_days_net_met'],'r9week',r['r9_synth_weeks_net_met'],'parent admit',r['verified_parent'],flush=True)
 path=Path(__file__).parent/'grid0296_parent_earned_full_january_results.json';path.write_text(json.dumps({'id':'GRID0296_ASOF_FUNDED_PARENT_EARNED_DYNAMIC_INVENTORY','tick_source_sha256':p.ancestor.base.back.SRC_SHA,'status':'NOT_ACCEPTED_RESEARCH_ONLY','results':res,'seconds':time.perf_counter()-t0},indent=2));print(path)
if __name__=='__main__':main()

"""GRID0295 original source-preserving WD child inventory cap, complement GRID0293.
As-of quota check based strictly on previously admitted and not-yet-closed child IDs.
No retrospective profit, R9 reference or calendar date enters source admission.
"""
from pathlib import Path
from collections import deque
import json,time
import grid0293_earned_capacity_dynamic as ancestor
import numpy as np
import pandas as pd
import heapq
from collections import Counter
source=ancestor.MOD
source=source.replace('earned_edge=0.0):', 'earned_edge=0.0,child_cap=0,parent_cap=0):')
source=source.replace('cap_up_count=0;native_closes=0','cap_up_count=0;native_closes=0;child_live=0;parent_live=0')
source=source.replace('if kind[j]==0:\n                close_source', 'if kind[j]==2:child_live-=1\n            if kind[j]==1:parent_live-=1\n            if kind[j]==0:\n                close_source')
source=source.replace('if len(live)>=cap:', '''if typ==2 and child_cap and child_live>=child_cap:
            ledger_events['bounded_child_inventory']+=1;continue
        if typ==1 and parent_cap and parent_live>=parent_cap:
            ledger_events['bounded_parent_inventory']+=1;continue
        if len(live)>=cap:''')
source=source.replace('elif typ==2:physical_child+=1', 'elif typ==2:physical_child+=1;child_live+=1')
source=source.replace('paid_parent[pidx]=True;physical_parent+=1', 'paid_parent[pidx]=True;physical_parent+=1;parent_live+=1')
source=source.replace('r.update(native16_cap=native16_cap,other_source_cap=other_source_cap,', 'r.update(child_cap=child_cap,parent_cap=parent_cap,native16_cap=native16_cap,other_source_cap=other_source_cap,')
namespace={k:getattr(ancestor.base,k) for k in ('np','pd','Counter','heapq','back','json','Path','ROOT','time')};namespace['deque']=deque
exec(source,namespace);physical_replay=namespace['physical_replay']

def main():
 t0=time.perf_counter();t,bid,ask,z,kind,owner,pgid,r9,origin=ancestor.base.materialize()
 configs=[('CONTROL_UNLIMITED',0,0),('CHILD192',192,0),('CHILD128',128,0),('CHILD96',96,0),('CHILD64',64,0),('CHILD48',48,0),('CHILD32',32,0),('CHILD24',24,0),('CHILD16',16,0),('CHILD8',8,0),('CHILD128_PARENT16',128,16),('CHILD64_PARENT16',64,16),('CHILD128_PARENT8',128,8),('CHILD64_PARENT8',64,8)]
 results=[]
 for name,ch,pa in configs:
  r=physical_replay(t,bid,ask,z,kind,owner,pgid,r9,cash=100000.,cap=256,loss_pause_n=2,pause_ms=300000,native16_cap=2,earned_native_cap=32,earned_wins=7,earned_window=10,earned_edge=12,child_cap=ch,parent_cap=pa)
  r['name']=name;results.append(r)
  print(name,'net',round(r['net'],2),'N',r['trades'],'GL',round(r['gross_loss'],2),'DD',round(r['max_all_tick_floating_equity_dd'],2),'posdays',sum(v['net']>0 for v in r['daily'].values()),'posweeks',sum(v['net']>0 for v in r['weekly'].values()),'R9day',r['r9_synth_days_net_met'],'R9week',r['r9_synth_weeks_net_met'],'paidchild',r['verified_child'],flush=True)
 outfile=Path(__file__).parent/'grid0295_watchdog_child_parent_heat_full_january_results.json'
 outfile.write_text(json.dumps({'id':'GRID0295_ORIGINAL_QUOTE_WD_CHILD_INVENTORY','source_sha256':ancestor.base.back.SRC_SHA,'hypothesis':'Bound only already-filled physically-open Watchdog child and parent ownership, separate L7 sleeve cap','status':'RESEARCH_ONLY_NOT_ENGINE_INTEGRATED','results':results,'runtime_seconds':time.perf_counter()-t0},indent=2));print('SAVED',outfile)
if __name__=='__main__':main()

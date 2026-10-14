"""GRID0298 portfolio capacity reservation for legitimate funded parent/child opportunities.
New risk-collision mechanism: priority for already known source kind, no future profit.
Original Dukascopy Bid/Ask, source genealogy and all common controls unchanged.
"""
from pathlib import Path
from collections import deque,Counter
import numpy as np,pandas as pd,heapq,json,time
import grid0296_parent_earned_exposure as p
SRC=p.SOURCE
SRC=SRC.replace('parent_edge=0.0):','parent_edge=0.0,reserve_wd_slots=0):')
SRC=SRC.replace('if len(live)>=cap:\n', '''if typ==0 and reserve_wd_slots>0 and len(live)>=cap-reserve_wd_slots:
            ledger_events['reserve_slots_for_parent_child']+=1;continue
        if len(live)>=cap:
''')
SRC=SRC.replace('r.update(child_cap=child_cap,parent_cap=parent_cap,','r.update(reserve_wd_slots=reserve_wd_slots,child_cap=child_cap,parent_cap=parent_cap,')
n={'np':np,'pd':pd,'deque':deque,'Counter':Counter,'heapq':heapq,'back':p.p.ancestor.base.back,'json':json,'Path':Path,'ROOT':p.p.ancestor.base.ROOT,'time':time};exec(SRC,n)
physical_replay=n['physical_replay']

def main():
 t0=time.perf_counter();t,bid,ask,z,kind,owner,pgid,r9,origin=p.p.ancestor.base.materialize()
 combos=[('PARENT192_CTRL',192,0),('PA192_RESV8',192,8),('PA192_RESV16',192,16),('PA192_RESV32',192,32),('PA192_RESV64',192,64),('PA192_RESV96',192,96),('PA192_RESV128',192,128),
         ('PA256_RESV8',256,8),('PA256_RESV16',256,16),('PA256_RESV32',256,32),('PA256_RESV64',256,64),('PA256_RESV96',256,96),('PA256_RESV128',256,128)]
 res=[]
 for name,raise_cap,reserve in combos:
  r=physical_replay(t,bid,ask,z,kind,owner,pgid,r9,cash=100000.,cap=256,loss_pause_n=2,pause_ms=300000,native16_cap=2,earned_native_cap=32,earned_wins=7,earned_window=10,earned_edge=12,parent_cap=16,earned_parent_cap=raise_cap,parent_wins=4,parent_window=6,parent_edge=4,reserve_wd_slots=reserve)
  r['name']=name;res.append(r)
  print(name,'net',round(r['net'],2),'trades',r['trades'],'grossloss',round(r['gross_loss'],2),'dd',round(r['max_all_tick_floating_equity_dd'],2),'positive_days',sum(v['net']>0 for v in r['daily'].values()),'positive_weeks',sum(v['net']>0 for v in r['weekly'].values()),'R9days',r['r9_synth_days_net_met'],'R9weeks',r['r9_synth_weeks_net_met'],'parents',r['verified_parent'],flush=True)
 file=Path(__file__).parent/'grid0298_watchdog_physical_slot_reservation_full_results.json'
 file.write_text(json.dumps({'experiment':'GRID0298_ASOF_PHYSICAL_PRIORITY_CROWDING_SLOTS','source_sha256':p.p.ancestor.base.back.SRC_SHA,'status':'RESEARCH_ONLY_NO_PROMOTION','results':res,'runtime_seconds':time.perf_counter()-t0},indent=2));print('SAVED',file)
if __name__=='__main__':main()

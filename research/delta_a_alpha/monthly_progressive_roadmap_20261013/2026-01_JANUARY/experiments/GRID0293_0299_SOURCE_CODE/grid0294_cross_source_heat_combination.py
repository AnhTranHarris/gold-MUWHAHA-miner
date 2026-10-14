"""GRID0294 source-level correlation/crowding cap overlay, cumulative on GRID0293.
Speculative reconstructible portfolio heat idea; original parents untouched.
No date/month/OVERFIT features used by admission.
"""
from pathlib import Path
import json,time
import grid0293_earned_capacity_dynamic as a
ROOT=Path(__file__).resolve().parent

def main():
 t0=time.perf_counter();t,bid,ask,z,kind,owner,pgid,r9,origin=a.base.materialize()
 configs=[
 ('CTRL_EARN32_SRC_UNLIMITED',0,256),
 ('OTHER_CAP256',256,256),('OTHER_CAP128',128,256),('OTHER_CAP64',64,256),('OTHER_CAP32',32,256),('OTHER_CAP16',16,256),
 ('OTHER_CAP8',8,256),('OTHER_CAP4',4,256),
 ('ALL_CAP64_OTHER32',32,64),('ALL_CAP64_OTHER16',16,64),
 ('ALL_CAP32_OTHER16',16,32),('ALL_CAP128_OTHER64',64,128)
 ]
 rows=[]
 for name,other,globalcap in configs:
  r=a.physical_replay(t,bid,ask,z,kind,owner,pgid,r9,cash=100000.,cap=globalcap,loss_pause_n=2,pause_ms=300000,native16_cap=2,earned_native_cap=32,earned_wins=7,earned_window=10,earned_edge=12,other_source_cap=other)
  r['name']=name;rows.append(r)
  print(name,'net',round(r['net'],2),'n',r['trades'],'GL',round(r['gross_loss'],2),'DD',round(r['max_all_tick_floating_equity_dd'],2),'days+',sum(v['net']>0 for v in r['daily'].values()),'weeks+',sum(v['net']>0 for v in r['weekly'].values()),'daysR9',r['r9_synth_days_net_met'],'weeksR9',r['r9_synth_weeks_net_met'],flush=True)
 out=ROOT/'grid0294_cross_source_crowding_full_january_results.json';out.write_text(json.dumps({'experiment':'GRID0294_ORIGINAL_RAW_BIDASK_CROSS_SOURCE_PHYSICAL_EXPOSURE','source_sha256':a.base.back.SRC_SHA,'status':'RESEARCH_ONLY_UNPROMOTED','hypothesis':'Risk budget per source rather than all 256 slots contested in FIFO','results':rows,'runtime_seconds':time.perf_counter()-t0},indent=2));print('SAVED',out)
if __name__=='__main__':main()

"""GRID0297 upper-cap earned-parent frontier, preserving GRID0296 exact source.
Original 9,135,062 Dukascopy tick quotes, owner-governed research only.
"""
from pathlib import Path
import json,time
import grid0296_parent_earned_exposure as p
ROOT=Path(__file__).resolve().parent

def main():
 t0=time.perf_counter();t,bid,ask,z,kind,owner,pgid,r9,origin=p.p.ancestor.base.materialize()
 combos=[
 ('RAISE128_3of5_2',16,128,3,5,2),('RAISE160_3of5_2',16,160,3,5,2),('RAISE192_3of5_2',16,192,3,5,2),('RAISE224_3of5_2',16,224,3,5,2),
 ('RAISE256_3of5_2',16,256,3,5,2),('RAISE160_4of6_4',16,160,4,6,4),('RAISE192_4of6_4',16,192,4,6,4),('RAISE224_4of6_4',16,224,4,6,4),
 ('RAISE256_4of6_4',16,256,4,6,4),('BASE32_RAISE160_4of6_4',32,160,4,6,4),('BASE32_RAISE192_4of6_4',32,192,4,6,4),
 ('RAISE160_5of6_4',16,160,5,6,4),('RAISE192_5of6_4',16,192,5,6,4),('RAISE192_4of6_8',16,192,4,6,8),
 ('RAISE192_2of4_1',16,192,2,4,1),('RAISE224_2of4_1',16,224,2,4,1)
 ]
 results=[]
 for name,cap,raise_cap,wins,window,edge in combos:
  r=p.physical_replay(t,bid,ask,z,kind,owner,pgid,r9,cash=100000.,cap=256,loss_pause_n=2,pause_ms=300000,native16_cap=2,earned_native_cap=32,earned_wins=7,earned_window=10,earned_edge=12,parent_cap=cap,earned_parent_cap=raise_cap,parent_wins=wins,parent_window=window,parent_edge=edge)
  r['name']=name;results.append(r)
  print(name,'net',round(r['net'],2),'N',r['trades'],'grossloss',round(r['gross_loss'],2),'equitydd',round(r['max_all_tick_floating_equity_dd'],2),'days+',sum(v['net']>0 for v in r['daily'].values()),'weeks+',sum(v['net']>0 for v in r['weekly'].values()),'R9d',r['r9_synth_days_net_met'],'R9w',r['r9_synth_weeks_net_met'],flush=True)
 out=ROOT/'grid0297_earned_parent_robustness_frontier_full_results.json'
 out.write_text(json.dumps({'experiment':'GRID0297_ASOF_WD_PARENT_EARNED_RISK_RETURN_FRONTIER','source_sha256':p.p.ancestor.base.back.SRC_SHA,'status':'NOT_ACCEPTED_NOT_LIVE','variants':results,'seconds':time.perf_counter()-t0},indent=2))
 print('SAVED',out)
if __name__=='__main__':main()

"""GRID0306 bounded original-tick account-size sensitivity; NOT certified survivability.
Replays exactly the same as-of source logic and original Bid/Ask feed; changing
initial cash is an offline test scenario, not a calendar feature or lot scaling.
"""
from pathlib import Path
import json,time
import grid0303_causal_coverage_source_caps as m
ROOT=Path(__file__).resolve().parent

def main():
 start=time.perf_counter()
 t,bid,ask,z,kind,owner,pgid,r9,origin=m.g.base.p.ancestor.base.materialize()
 results=[]
 for cash in [100.,200.,300.,500.]:
  r=m.replay(t,bid,ask,z,kind,owner,pgid,r9,cash=cash,cap=256,
   loss_pause_n=2,pause_ms=300000,native16_cap=2,earned_native_cap=32,
   earned_wins=7,earned_window=10,earned_edge=12,parent_cap=16,
   earned_parent_cap=192,parent_wins=4,parent_window=6,parent_edge=4,
   hourly_entry_lock_usd=0.,hourly_soft_parent_usd=400.,hourly_soft_parent_cap=64,
   gc0_cap=256,gc2_cap=224)
  results.append({'initial_capital':cash,'trades':r['trades'],'net':r['net'],
    'min_tick_equity':r['min_actual_tick_equity'],
    'min_tick_equity_to_initial':r['min_actual_tick_equity']/cash,
    'hourly_drawdown':r['max_hourly_tick_equity_drawdown_usd'],
    'full_tick_drawdown':r['max_all_tick_floating_equity_dd'],
    'positive_days':sum(v['net']>0 for v in r['daily'].values()),
    'positive_weeks':sum(v['net']>0 for v in r['weekly'].values())})
  print('start',cash,'net',round(r['net'],2),'min_EQ',round(r['min_actual_tick_equity'],2),flush=True)
 out=ROOT/'grid0306_research_low_capital_diagnostic.json'
 out.write_text(json.dumps({'id':'GRID0306_LOW_CAPITAL_REPLAY_DIAGNOSTIC',
   'source_sha256':m.g.base.p.ancestor.base.back.SRC_SHA,
   'status':'NO_SURVIVABILITY_CERTIFICATION','assumptions':'hypothetical leverage 500, 1oz/0.01 lot, .20 roundtrip, 250ms original quote',
   'variants':results,'seconds':time.perf_counter()-start},indent=2))
if __name__=='__main__':main()

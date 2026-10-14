"""GRID0293 research-only: as-of paid-close evidence increases NATIVE_NY16 concurrency.
No forward PnL, zero use of month/day/performance targets in admission.
Starts from original source-exact GRID0290 source; modifies only physical L7 cap.
"""
from __future__ import annotations
from collections import deque
import numpy as np
import grid0290_funded_portfolio_source_heat_cap as base

# Exact code provenance: parent script unchanged in the same January source archive.
# This source reconstructs as a pure source-to-source patch of the original
# physical_replay function for an independent trial; no live engine mutations.
from pathlib import Path
SOURCE = Path(base.__file__).read_text()
START = SOURCE.index('def physical_replay(')
END = SOURCE.index('\ndef main():', START)
ORIGINAL=SOURCE[START:END]

# Insert lagged source-profit inventory when actual funded native trades close.
MOD = ORIGINAL.replace('other_source_cap=0):', 'other_source_cap=0,earned_native_cap=0, earned_wins=3, earned_window=6, earned_edge=0.0):')
MOD = MOD.replace('source_losses={};source_pause_until={};pause_count=0;live_by_source={}', 'source_losses={};source_pause_until={};pause_count=0;live_by_source={};native_recent=deque(maxlen=earned_window);cap_up_count=0;native_closes=0')
MOD = MOD.replace("live_by_source[close_source]=live_by_source.get(close_source,0)-1", "live_by_source[close_source]=live_by_source.get(close_source,0)-1\n                if close_source=='NATIVE_NY16':\n                    native_recent.append(net);native_closes+=1")
MOD = MOD.replace('limit=native16_cap if source==\'NATIVE_NY16\' else other_source_cap', "limit=native16_cap if source=='NATIVE_NY16' else other_source_cap\n            if source=='NATIVE_NY16' and earned_native_cap>native16_cap and len(native_recent)>=earned_window and sum(q>0 for q in native_recent)>=earned_wins and sum(native_recent)>=earned_edge:\n                limit=earned_native_cap;cap_up_count+=1")
MOD = MOD.replace('r.update(native16_cap=native16_cap,other_source_cap=other_source_cap)', 'r.update(native16_cap=native16_cap,other_source_cap=other_source_cap,earned_native_cap=earned_native_cap,earned_wins=earned_wins,earned_window=earned_window,earned_edge=earned_edge,native_closed_seen=native_closes,eligible_cap_raise_events=cap_up_count)')
assert MOD!=ORIGINAL and 'native_recent.append(net)' in MOD
NAMESPACE={k:getattr(base,k) for k in ('np','pd','Counter','heapq','back','json','Path','ROOT','time')};NAMESPACE['deque']=deque
exec(MOD, NAMESPACE)
physical_replay=NAMESPACE['physical_replay']


def main():
 import json,time
 t0=time.perf_counter();t,bid,ask,z,kind,owner,pgid,r9,origin=base.materialize()
 print('GRID0293 source',origin,flush=True)
 configs=[
  ('PRESERVED_CONTROL',2,0,3,6,0),
  ('EARNED4_4of6_usd2',2,4,4,6,2),
  ('EARNED8_4of6_usd4',2,8,4,6,4),
  ('EARNED16_4of6_usd4',2,16,4,6,4),
  ('EARNED8_5of8_usd8',2,8,5,8,8),
  ('EARNED16_6of8_usd8',2,16,6,8,8),
  ('EARNED32_7of10_usd12',2,32,7,10,12),
  ('EARNED8_5of8_usd4',1,8,5,8,4),
  ('EARNED4_3of5_usd1',1,4,3,5,1),
  ('EARNED6_4of6_usd3',1,6,4,6,3),
 ]
 results=[]
 for name,basic,raised,wins,window,threshold in configs:
  r=physical_replay(t,bid,ask,z,kind,owner,pgid,r9,cash=100000.,cap=256,loss_pause_n=2,pause_ms=300000,native16_cap=basic,earned_native_cap=raised,earned_wins=wins,earned_window=window,earned_edge=threshold)
  r['name']=name;results.append(r)
  print(name,'net',round(r['net'],2),'trades',r['trades'],'GL',round(r['gross_loss'],2),'dd',round(r['max_all_tick_floating_equity_dd'],2),'posdays',sum(v['net']>0 for v in r['daily'].values()),'posweeks',sum(v['net']>0 for v in r['weekly'].values()),'R9days',r['r9_synth_days_net_met'],'R9weeks',r['r9_synth_weeks_net_met'],'eligible up',r['eligible_cap_raise_events'],flush=True)
 outfile=base.ROOT/'grid0293_earned_capacity_full_january_results.json'
 outfile.write_text(json.dumps({'experiment':'GRID0293_ORIGINAL_RAW_BIDASK_EARNED_PHYSICAL_CONCURRENCY','source_sha256':base.back.SRC_SHA,'hypothesis':'Increasing position slots based only on prior funded CLOSED native-source outcomes','broker_only':False,'status':'RESEARCH_ONLY_NOT_ACCEPTED','results':results,'runtime_seconds':time.perf_counter()-t0},indent=2));print('FILE',outfile)
if __name__=='__main__':main()

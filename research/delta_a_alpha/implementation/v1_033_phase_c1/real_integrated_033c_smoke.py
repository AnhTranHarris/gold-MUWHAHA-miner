"""Genuine real-tick PHASE C partial L1/L3/L4 online-funded smoke.

Not original full V1 and not comparable to JAN039/FEB047 profits. 131D
coverage is historical fitted, original 075 119-eligible parent stream not ported.
"""
from __future__ import annotations
import json,hashlib
from pathlib import Path
import numpy as np,pandas as pd
from real_dukas_event_smoke_033 import orig_completed_state_fn,load_window,EXPECTED
from v1_funded_core_033 import Quote,Structure,Limits,FundedEngine,OriginalHourlyHeartbeatL3
from original_online_sources_033c import Original131DSessionL3,Funded119WatchdogL4

def run(root:Path,out:Path,max_quotes:int=350000):
    for tag in ('jan','feb'):
        fn=root/f'XAUUSD_DUKAS_2026_{"01" if tag=="jan" else "02"}_ticks.csv(3).gz'
        h=hashlib.sha256()
        with fn.open('rb') as f:
            for ch in iter(lambda:f.read(4*1024*1024),b''):h.update(ch)
        assert h.hexdigest()==EXPECTED[tag]
    ms=lambda ts:int(pd.Timestamp(ts,tz='UTC').value//1000000)
    jan=load_window(root/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz',ms('2026-01-22'),ms('2026-02-01'))
    feb=load_window(root/'XAUUSD_DUKAS_2026_02_ticks.csv(3).gz',ms('2026-02-02 06:30:00'),ms('2026-02-03 19:00:00')).iloc[:max_quotes]
    z=pd.concat((jan,feb),ignore_index=True)
    t=z.timestamp_ms_utc.to_numpy(np.int64);a=z.ask_raw.to_numpy(np.int32);b=z.bid_raw.to_numpy(np.int32)
    assert np.all(t[1:]>=t[:-1])
    state_fn=orig_completed_state_fn(root/'JAN037_ITERATIVE_XAUUSD_TICK_RESEARCH_BUNDLE.zip')
    states={};ends={}
    for n,tf in [('h4',14400000),('h1',3600000),('m15',900000),('m5',300000)]:
        states[n]=state_fn(t,b,tf,8,21)
        buck=t//tf;starts=np.r_[0,np.flatnonzero(buck[1:]!=buck[:-1])+1]
        last=np.r_[starts[1:]-1,len(t)-1]
        prev=np.searchsorted(buck[starts],buck,side='left')-1
        en=np.full(len(t),-1,np.int64);valid=prev>=0;en[valid]=t[last[prev[valid]]]
        ends[n]=en
    start=len(jan)
    grid=Original131DSessionL3(); wd=Funded119WatchdogL4(); hb=OriginalHourlyHeartbeatL3(50)
    eng=FundedEngine(Limits(max_open=32,max_layer_open=32,max_same_direction=32,
                 max_per_source_open=32,max_per_cell_side=16,max_orders_per_second=4,
                 max_orders_per_tick=1,max_underwater_open_usd=8000,max_spread_usd=3.0),
                 [hb,grid,wd],broker_contract_verified=True)
    for i in range(start,len(t)):
        tm=int(t[i]);en=tuple(int(ends[k][i]) for k in ('h4','h1','m15','m5'))
        if all(x>0 for x in en):
            # Exactly original completed-EMA sign state: insufficient for owner
            # H4 environment/H1 structural location/M15 phase/M5 transfer.
            s=Structure('DIAGNOSTIC',*(int(states[k][i]) for k in ('h4','h1','m15','m5')),
                 max(en),f'GRID:{tm//600000}',(tm//600000)%6,en)
        else:s=None
        eng.process_quote(Quote(tm,int(a[i]),int(b[i])),s)
    output={'status':'DIAGNOSTIC_PARTIAL_V1_NOT_SOURCE_COMPLETE',
       'january_context_quotes':len(jan),'february_real_quotes':len(feb),
       'source_parity':{'original_019':'ALREADY_PASS_43105_ENTRIES_PHASE_B','original_131c':'PASS_40784_L1_EVENTS_PHASE_C'},
       'original_131d_exposed_session_grid_shadow_events':grid.shadow_ladder_events,
       'original_131d_source_proposals':grid.source_candidates,
       'physically_accepted_131d':sum(x['event']=='FILL' and str(x.get('source','')).startswith('ORIG_131D_') for x in eng.events),
       'physical_119_parent_windows':len(wd.parents),
       'physical_119_children':sum(x['event']=='FILL' and x.get('layer')=='L4' for x in eng.events),
       'watchdog_source_parity':'INCOMPLETE_UNTIL_ORIGINAL_075_PARENT_SOURCE_RECONSTRUCTED',
       'broker_contract':'MOCK_RESEARCH_100K_NOT_COINEXX',
       'source_state':'PREVIOUS_COMPLETED_EMA_SIGNS_ONLY_NOT_FULL_V1_L2',
       'score_diagnostic_only':eng.score(),
       'full_V1_portfolio_economics':'NOT_YET_POSSIBLE',
       'august':'SEALED','march':'ON_HOLD'}
    out.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output))
    return output

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--root',default='/mnt/data');p.add_argument('--max-quotes',type=int,default=350000);p.add_argument('--out',default='/mnt/data/DAA_033_implementation_phase_c/REAL_INTEGRATED_033C_SMOKE.json');args=p.parse_args()
    run(Path(args.root),Path(args.out),args.max_quotes)
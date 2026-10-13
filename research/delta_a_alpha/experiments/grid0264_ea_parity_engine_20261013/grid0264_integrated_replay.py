"""GRID0264 trace replay: old GRID0263 source replaced by actual cumulative adapter.

Research outcomes NEVER broker certified. Read saved JSON before repeating tests.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
import argparse,glob,gzip,hashlib,json
import numpy as np
from v1_grid_python_source_to_shadow_port_0264 import Grid0264ResearchRuntime,SourceLifecyclePolicy
from v1_grid_funded_quote_gate_0262_hardened import HardenedBrokerPhysics
from grid0263_recovered_router_hardened_replay import CompletedAsOfBar,research_geometry
from v1_grid_original_tick_stream_0262 import stream_original_ticks

SOURCES=(
  'OMEGAFX_M5_COMPLETED_VIRTUAL_CHILD',
  'OMEGAFX_M5_FINE_FIRST_TOUCH_V1',
  'OMEGAFX_M1_COMPLETED_FIRST_TOUCH_V1',
  'OMEGAFX_CAUSAL_VIRTUAL_RUNG',
  'OMEGAFX_ACKNOWLEDGED_FILL_ANCHOR',
  'GRID0253_COMPLETED_H4_BREAK_PULLBACK_RECROSS',
  'GRID0254_H4_TWO_COMPLETED_M1_ACCEPTANCE',
  'APRIL136A_CAUSAL_NATIVE_MINUTE_RUNG',
)

def run(month,limit,*,first_1s=False,permission=True):
    if not 1<=month<=7:raise ValueError('August sealed: only Jan-Jul')
    # Explicit modeled dollar fees: $52 per 1.00 lot -> $0.52 at 0.01 lots,
    # strictly hypothetical, NOT Coinexx contract and not target-profit evidence.
    physics=HardenedBrokerPhysics(contract_oz_per_lot=100,leverage=500,
        min_lot=.01,lot_step=.01,min_stop_raw=100,roundtrip_usd_per_lot=52,
        source_note='ASSUMED 1oz per 0.01 lot, $0.52/roundtrip; NO BROKER PROOF')
    policies=tuple(SourceLifecyclePolicy(x,2200,30_000,250,1800,
              profit_target_raw=3600,trail_arm_raw=2000,trail_distance_raw=900) for x in SOURCES)
    engine=Grid0264ResearchRuntime(physics=physics,starting_cash_usd=300,
                                     policies=policies,max_positions=16)
    h1=CompletedAsOfBar(3600000);m5=CompletedAsOfBar(300000)
    if first_1s:
        path=Path('/mnt/data/grid0261_intrinsic_followon')/f'j0261_M{month:02d}_original_first_1s_QBV.npz'
        with np.load(path) as z:
            t=z['t'][:limit].copy();b=z['b'][:limit].copy();a=z['a'][:limit].copy()
        ticks=zip(t,b,a)
    else:
        hits=glob.glob('/mnt/data/XAUUSD_DUKAS_2026_'+f'{month:02d}'+'_ticks.csv*.gz')
        if len(hits)!=1:raise ValueError('input requires exactly one intact original Jan-Jul gzip')
        ticks=((o.quote.utc_ms,o.quote.bid_raw,o.quote.ask_raw) for o in stream_original_ticks(hits[0],
               permission=lambda ms,b,a:permission,maximum=limit))
    nc=0
    for ms,bb,aa in ticks:
        ms,bb,aa=int(ms),int(bb),int(aa)
        a_h1=h1.update(ms,bb,aa);a_m5=m5.update(ms,bb,aa)
        engine.on_original_tick(time_ms=ms,bid_raw=bb,ask_raw=aa,
            h1_completed=a_h1,m5_completed=a_m5,geometry=research_geometry(ms),
            hypothetical_research_tradable=permission)
        nc+=1
    s=engine.summary(); f=engine.funding
    gross=sum(x.net_usd for x in f.settlements)
    if abs((f.initial_cash+gross)-f.cash)>1e-6:
        raise AssertionError('shadow cash not conserved')
    compact='\n'.join(f'{e.event_id}|{e.entry_ms}|{e.exit_ms}|{e.entry_raw}|{e.observed_exit_raw}|{e.net_usd:.8f}|{e.reason}' for e in f.settlements)
    if engine.sources.router.funded.counts['ack_fills'] or engine.sources.router.funded.counts['ack_closes']:
        raise AssertionError('ILLEGAL broker paid source derived from hypothetical shadow')
    return {'month':month,'kind':'ORIGINAL_RAW_ALL_ROWS_NO_RESAMPLING' if not first_1s else 'CAUSAL_FIRST_OBSERVED_QUOTE_PER_SECOND',
     'input_observations':nc, 'source_events':s['counters'].get('source_events',0),
     'accepted_research':s['counters'].get('accepted_for_next_observed_quote',0),
     'shadow_closes':len(f.settlements),'shadow_open':len(f.open),
     'shadow_cash':round(f.cash,6),'shadow_fee_assumption_per_trade_usd':.52,
     'cash_reconciles':True,'broker_paid_anchors_minted':0,
     'sha256_of_exact_shadow_settlements':hashlib.sha256(compact.encode()).hexdigest(),
     'execution':'HYPOTHETICAL_OFFLINE_NOT_MT5_CERTIFIED'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--month',type=int,default=1)
    ap.add_argument('--limit',type=int,default=205000);ap.add_argument('--one-second',action='store_true')
    ap.add_argument('--deny',action='store_true')
    opts=ap.parse_args()
    print(json.dumps(run(opts.month,opts.limit,first_1s=opts.one_second,permission=not opts.deny),indent=2))

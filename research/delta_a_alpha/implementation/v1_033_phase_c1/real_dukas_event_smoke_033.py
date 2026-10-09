"""Real Dukascopy Jan-Feb XAUUSD quote-path *implementation* smoke test.

Not full V1 economics. Sources: the unchanged original 019 online L3 entry
formula and original stmr_janjul completed EMA8/21 state helper.
This reproduces original helper states as a *diagnostic*; it DOES NOT claim that
EMA sign is sufficient to implement the full owner H4/H1/M15/M5 role contracts.
"""
from __future__ import annotations
import argparse, hashlib, json, sys, time, zipfile, ast
from pathlib import Path
import numpy as np
import pandas as pd
from v1_funded_core_033 import Quote, Structure, Limits, FundedEngine, OriginalHourlyHeartbeatL3

EXPECTED={
'jan':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
'feb':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d'}


def orig_completed_state_fn(archive: Path):
    with zipfile.ZipFile(archive) as z:
        source=z.read('032_source/stmr_janjul.py').decode()
    node=next(x for x in ast.parse(source).body if isinstance(x,ast.FunctionDef) and x.name=='bar_states_span')
    mod=ast.Module(body=[node],type_ignores=[]);ast.fix_missing_locations(mod)
    env={'np':np};exec(compile(mod,'original_stmr_janjul_bar_states_span','exec'),env)
    return env['bar_states_span']


def load_window(gz_path:Path,lo_ms:int,hi_ms:int):
    arr=[]
    for ch in pd.read_csv(gz_path,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],
                          dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'},chunksize=500000):
        cut=ch[(ch.timestamp_ms_utc>=lo_ms)&(ch.timestamp_ms_utc<hi_ms)]
        if len(cut):arr.append(cut)
    if not arr:raise RuntimeError('No genuine quotes in requested window')
    return pd.concat(arr,ignore_index=True)


def run(root:Path,out:Path, max_events:int=65000):
    t0=time.monotonic()
    jan=root/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'
    feb=root/'XAUUSD_DUKAS_2026_02_ticks.csv(3).gz'
    for tag,f in [('jan',jan),('feb',feb)]:
        h=hashlib.sha256()
        with f.open('rb') as fp:
            for ch in iter(lambda:fp.read(4*1024*1024),b''):h.update(ch)
        assert h.hexdigest()==EXPECTED[tag],f'{tag} corrupt'
    ms=lambda t:int(pd.Timestamp(t,tz='UTC').value//1000000)
    # Ten true Jan prehistory days and all Feb quotes until the replay end.
    frames=[load_window(jan,ms('2026-01-22'),ms('2026-02-01')),
            load_window(feb,ms('2026-02-01'),ms('2026-02-04'))]
    df=pd.concat(frames,ignore_index=True)
    t=df.timestamp_ms_utc.to_numpy(np.int64);ask=df.ask_raw.to_numpy(np.int32);bid=df.bid_raw.to_numpy(np.int32)
    assert np.all(t[1:]>=t[:-1]);assert np.all(ask>=bid)
    states={};ends={}; src=orig_completed_state_fn(root/'JAN037_ITERATIVE_XAUUSD_TICK_RESEARCH_BUNDLE.zip')
    # Original bar_states_span uses previous bar's completed state, never current unfinished bar.
    for name,tf in [('h4',4*3600000),('h1',3600000),('m15',900000),('m5',300000)]:
        states[name]=src(t,bid,tf,8,21)
        buck=t//tf;start=np.r_[0,np.flatnonzero(buck[1:]!=buck[:-1])+1]
        last_indices=np.r_[start[1:]-1,len(t)-1]
        prev=np.searchsorted(buck[start],buck,side='left')-1
        en=np.full(len(t),-1,np.int64);good=prev>=0;en[good]=t[last_indices[prev[good]]]
        ends[name]=en
    sample=np.flatnonzero((t>=ms('2026-02-02 06:30:00'))&(t<ms('2026-02-03 19:00:00')))
    if len(sample)>max_events:
        # Consecutive quote path, not downsampled or synthetic; stop after N.
        sample=sample[:max_events]
    if not len(sample):raise RuntimeError('No February quotes')
    eng=FundedEngine(Limits(max_open=16,max_layer_open=16,max_same_direction=16,
                            max_per_cell_side=8,max_orders_per_second=3,max_orders_per_tick=1,
                            max_spread_usd=3.0, max_underwater_open_usd=8000),
                     [OriginalHourlyHeartbeatL3(50)],broker_contract_verified=True)
    # Diagnostic validated contract values are assumed for this research smoke only.
    for i in sample:
        ti=int(t[i]);en=tuple(int(ends[k][i]) for k in ('h4','h1','m15','m5'))
        # Use last observable prior tick for completed-bar provenance.
        ready=all(x>0 for x in en)
        s=Structure('HOURLY_DEBUG',int(states['h4'][i]),int(states['h1'][i]),int(states['m15'][i]),
                    int(states['m5'][i]),max(en),f'HB_{ti//600000}',(ti//600000)%6,en) if ready else None
        eng.process_quote(Quote(ti,int(ask[i]),int(bid[i])),s)
    report=dict(schema='v1_033_original019_real_dukas_tick_kernel_smoke',
                title='EXECUTION ENGINE DIAGNOSTIC NOT FULL ORIGINAL L0-L7 PORTFOLIO PERFORMANCE',
                data_hashes=EXPECTED,
                quotes=int(len(sample)),warmup_quote_count=int(len(t)-len(sample)),
                quote_range_ms=[int(t[sample[0]]),int(t[sample[-1]])],
                original_019_source='032_source/gamma02_campaign_heartbeat_019.py',
                original_state='032_source/stmr_janjul.py (completed EMA signs; insufficient for complete V1 structural roles)',
                computed_in_seconds=round(time.monotonic()-t0,3),score=eng.score(),
                accepted_entrances=sum(x['event']=='FILL' for x in eng.events),
                exit_count=len(eng.closed),
                note='Cannot infer Jan/Feb V1 profit targets from this diagnostic. Full L1 native/WATCHDOG L4/native L5/recovery L6/broker L7 source parity still incomplete.')
    out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',default='/mnt/data');parser.add_argument('--out',default='/mnt/data/DAA_033_implementation/REAL_DUKAS_SMOKE_033.json');parser.add_argument('--max-events',type=int,default=50000)
    a=parser.parse_args();run(Path(a.root),Path(a.out),a.max_events)
"""Independent original-131C source-level event identity test on RAW Feb ticks.

NOT a whole-V1 or full-MTF economic test: only L1 source 131C first-touch.
"""
from __future__ import annotations
import ast,hashlib,json,zipfile
from pathlib import Path
import numpy as np,pandas as pd
from numba import njit
from v1_funded_core_033 import Quote
from original_online_sources_033c import Original131CSessionGridL1
from real_dukas_event_smoke_033 import load_window

EXPECTED_FEB_SHA256='ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d'

def original_131c_function(archive: Path):
    with zipfile.ZipFile(archive) as z:
        source=z.read('032_source/general_session_state_discovery_131c.py').decode()
    f=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='build_events')
    f.decorator_list=[]
    mod=ast.Module(body=[f],type_ignores=[])
    ast.fix_missing_locations(mod)
    env={'np':np}
    exec(compile(mod,'VERBATIM_131C_FROM_JAN037','exec'),env)
    return njit(cache=False)(env['build_events'])

def run(root:Path,out:Path,nquotes:int=1136212):
    market=root/'XAUUSD_DUKAS_2026_02_ticks.csv(3).gz'
    with market.open('rb') as fp:
        h=hashlib.sha256()
        for buf in iter(lambda:fp.read(8*1024*1024),b''):h.update(buf)
    assert h.hexdigest()==EXPECTED_FEB_SHA256
    start=int(pd.Timestamp('2026-02-02 06:30:00',tz='UTC').value//1000000)
    stop=int(pd.Timestamp('2026-02-03 19:00:00',tz='UTC').value//1000000)
    frame=load_window(market,start,stop).iloc[:nquotes]
    t=frame.timestamp_ms_utc.to_numpy(np.int64)
    a=frame.ask_raw.to_numpy(np.int32)
    b=frame.bid_raw.to_numpy(np.int32)
    assert np.all(a>=b) and np.all(t[1:]>=t[:-1])
    mid=((a.astype(np.int64)+b.astype(np.int64))//2).astype(np.int64)
    original=original_131c_function(root/'JAN037_ITERATIVE_XAUUSD_TICK_RESEARCH_BUNDLE.zip')
    by_step = {}
    for step_raw in (250, 75):
        ei,dirs=original(t,mid,step_raw)
        online=Original131CSessionGridL1(step_raw)
        oi=[];od=[]
        for i in range(len(t)):
            for event in online.on_tick(Quote(int(t[i]),int(a[i]),int(b[i]))):
                oi.append(i);od.append(event.direction)
        matched=(np.array_equal(ei,np.asarray(oi,dtype=np.int64)) and
                 np.array_equal(dirs,np.asarray(od,dtype=np.int8)))
        by_step[str(step_raw)]={'original_events':len(ei),'ported_events':len(oi),
                               'index_direction_exact_match':bool(matched)}
        if not matched:raise AssertionError(f'Original131C first-touch mismatch: step {step_raw}')
    result={'scope':'ORIGINAL_131C_FIRST_TOUCH_SOURCE_ONLY',
            'data':'DUKAS_REAL_BIDASK_FEB', 'feb_sha256':EXPECTED_FEB_SHA256,
            'original_source':'JAN037_ARCHIVE/032_source/general_session_state_discovery_131c.py',
            'quote_count':len(t), 'step_250_and_131d_step_75':by_step,
            'month_blind_market_decisions':True,
            'whole_owner_V1_source_parity':'INCOMPLETE', 'economic_validity':'NOT_TESTED'}
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
    return result

if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('--root',default='/mnt/data');a.add_argument('--nquotes',type=int,default=1136212);a.add_argument('--out',default='/mnt/data/DAA_033_implementation_phase_c/REAL_131C_PARITY_033C.json');z=a.parse_args()
    run(Path(z.root),Path(z.out),z.nquotes)
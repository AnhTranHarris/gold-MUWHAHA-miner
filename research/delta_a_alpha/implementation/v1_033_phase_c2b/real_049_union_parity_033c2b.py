"""Untouched archived 001/017/019 -> 049 union entry-parity on Feb raw ticks.

No future-pnl/exit arrays used. Uses original 131E completed EMA sign
proxy (NOT V1 role-separated HTF structural state); genuine Jan history.
"""
import json,hashlib
from pathlib import Path
import numpy as np,pandas as pd
from real_dukas_event_smoke_033 import orig_completed_state_fn,load_window,EXPECTED
from test_original_ny049_union_033c2b import original_events,port_events

def run(root=Path('/mnt/data'),count=1136212):
    def sha(p):
        h=hashlib.sha256()
        with p.open('rb') as f:
            for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
        return h.hexdigest()
    j=root/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz';f=root/'XAUUSD_DUKAS_2026_02_ticks.csv(3).gz'
    assert sha(j)==EXPECTED['jan'] and sha(f)==EXPECTED['feb']
    ms=lambda a:int(pd.Timestamp(a,tz='UTC').value//1000000)
    a=load_window(j,ms('2026-01-22'),ms('2026-02-01'))
    b=load_window(f,ms('2026-02-02 06:30:00'),ms('2026-02-03 19:00:00')).iloc[:count]
    z=pd.concat((a,b),ignore_index=True)
    t=z.timestamp_ms_utc.to_numpy(np.int64);bid=z.bid_raw.to_numpy(np.int64);ask=z.ask_raw.to_numpy(np.int64)
    fn=orig_completed_state_fn(root/'JAN037_ITERATIVE_XAUUSD_TICK_RESEARCH_BUNDLE.zip')
    states={n:fn(t,bid,tf,8,21) for n,tf in [('h4',14400000),('h1',3600000),('m15',900000),('m5',300000)]}
    offset=len(a);T=t[offset:];A=ask[offset:];B=bid[offset:];mid=((A+B)//2)
    r=original_events(T,mid,*(states[n][offset:] for n in ('h4','h1','m15','m5')))
    c=port_events(T,A,B,*(states[n][offset:] for n in ('h4','h1','m15','m5')))
    dif=[(x,y) for x,y in zip(r,c) if x!=y][:5]
    status=(r==c)
    out={'status':'PASS_EXACT' if status else 'FAIL','scope':'ENTRY_INDEX_DIRECTION_UTC_SOURCE_ONLY_049_ORIGINAL_001_017_019_UNION',
        'february_raw_bidask_quotes':len(b),'authentic_prior_january_quotes':len(a),'source_indices_original':len(r),
        'source_indices_ported':len(c),'mismatch_first5':dif,'source_order':{'first_original':r[:3],'last_original':r[-3:]},
        'original_049_funded_parent_selection_parity':'NOT_THIS_TEST',
        'original_l2_completed_htf_role_parity':'NOT_TESTED_ONLY_ORIGINAL_EMA_SIGN_PROXY',
        'august':'SEALED','september':'RESERVED'}
    (Path(__file__).parent/'REAL_049_UNION_PARITY_033C2B.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out));assert status
    return out
if __name__=='__main__':run()
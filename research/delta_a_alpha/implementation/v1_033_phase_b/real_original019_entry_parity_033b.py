"""Read-only original 019 parity on genuine February Dukascopy source ticks.

Uses original 131E EMA-sign state only for a source-level parity test; this
DOES NOT satisfy full owner L2 structural context and cannot prove V1 P&L.
"""
from __future__ import annotations
import ast, hashlib, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from real_dukas_event_smoke_033 import orig_completed_state_fn, load_window
from v1_funded_core_033 import Quote, Structure, OriginalHourlyHeartbeatL3

REPO_BUNDLE='JAN037_ITERATIVE_XAUUSD_TICK_RESEARCH_BUNDLE.zip'
EXPECTED_FEB='ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d'

def original_function(bundle:Path):
    with zipfile.ZipFile(bundle) as z: doc=z.read('032_source/gamma02_campaign_heartbeat_019.py').decode()
    tree=ast.parse(doc)
    names={'THR','NY17_MIN','NY18_MIN','NY18_MAX','TP16','SL16','H16','TP17','SL17','H17','TP18','SL18','H18'}
    funcs={'london_rule','ny_dir','heartbeat_candidates'}
    nodes=[]
    for n in tree.body:
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in names for t in n.targets):nodes.append(n)
        elif isinstance(n,ast.FunctionDef) and n.name in funcs:
            n.decorator_list=[];nodes.append(n)
    mod=ast.Module(body=nodes,type_ignores=[]);ast.fix_missing_locations(mod)
    ns={'np':np}
    exec(compile(mod,'LITERAL_ORIGINAL_019_BUNDLE','exec'),ns)
    return ns['heartbeat_candidates']

def run(root:Path, out:Path, max_events:int=260000):
    gz=root/'XAUUSD_DUKAS_2026_02_ticks.csv(3).gz'
    assert hashlib.sha256(gz.read_bytes()).hexdigest()==EXPECTED_FEB
    ts=lambda s:int(pd.Timestamp(s,tz='UTC').value//1000000)
    # Source-window February 2–3 includes the original L3 UTC London/NY hours.
    # Actual 10-day JAN prehistory for EMA warmup, not invented previous bars.
    hist=load_window(root/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz',ts('2026-01-22'),ts('2026-02-01'))
    feb=load_window(gz,ts('2026-02-02 06:30:00'),ts('2026-02-03 19:00:00'))
    if len(feb)>max_events: feb=feb.iloc[:max_events].copy()
    z=pd.concat([hist,feb],ignore_index=True)
    t=z.timestamp_ms_utc.to_numpy(np.int64)
    b=z.bid_raw.to_numpy(np.int32);a=z.ask_raw.to_numpy(np.int32)
    hfn=orig_completed_state_fn(root/REPO_BUNDLE)
    states={name:hfn(t,b,tf,8,21) for name,tf in [('h4',14400000),('h1',3600000),('m15',900000),('m5',300000)]}
    tt=t[len(hist):];aa=a[len(hist):];bb=b[len(hist):]
    h4=states['h4'][len(hist):];h1=states['h1'][len(hist):];m15=states['m15'][len(hist):];m5=states['m5'][len(hist):]
    mid=(aa.astype(np.int64)+bb.astype(np.int64))//2
    original=original_function(root/REPO_BUNDLE)
    exp=original(tt,mid,h4,h1,m15,m5,50,4)
    expected=list(zip(*[x.tolist() for x in exp]))
    adapter=OriginalHourlyHeartbeatL3(50);got=[]
    for i,tm in enumerate(tt):
        ti=int(tm)
        # These states are already completed-only by original helper.
        s=Structure('SOURCE_ONLY',int(h4[i]),int(h1[i]),int(m15[i]),int(m5[i]),ti-1,'ORIGINAL019')
        for prop in adapter.propose(Quote(ti,int(aa[i]),int(bb[i])),s,None):
            got.append((i,prop.side,int(prop.source.rsplit('UTC',1)[1]),prop.ttl_ms,int(round(prop.tp_usd*1000)),int(round(prop.sl_usd*1000))))
    report={'status':'ENTRY_PARITY_ONLY_NOT_V1_ECONOMIC','ticks':len(tt),'genuine_jan_prehistory_quotes':len(hist),
            'original_019_proposals':len(expected),'ported_019_proposals':len(got),'exact_source_records_match':expected==got,
            'first_mismatch':next(((j,expected[j],got[j]) for j in range(min(len(expected),len(got))) if expected[j]!=got[j]),None),
            'original_source_bundle_sha256':hashlib.sha256((root/REPO_BUNDLE).read_bytes()).hexdigest(),
            'feb_sha256':EXPECTED_FEB,'source_state':'ORIGINAL_131E_COMPLETED_EMA_SIGN_ONLY_NOT_FULL_V1_L2'}
    out.write_text(json.dumps(report,indent=2)+'\n')
    if not report['exact_source_records_match']:raise AssertionError(report['first_mismatch'])
    print(json.dumps(report,indent=2))
    return report

if __name__=='__main__':
    import argparse
    ar=argparse.ArgumentParser();ar.add_argument('--root',default='/mnt/data');ar.add_argument('--max-events',type=int,default=260000);ar.add_argument('--out',default='/mnt/data/DAA_033_implementation_phase_b/REAL_019_PARITY_033B.json');args=ar.parse_args()
    run(Path(args.root),Path(args.out),args.max_events)
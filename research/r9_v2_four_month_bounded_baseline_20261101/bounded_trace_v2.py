#!/usr/bin/env python3
"""Reproducible BOUNDED frozen-v2 baseline diagnostic. NOT a full-month test.

Preserves original RouterV2FeatureEngine, ActivePath and BayesianCompetingRiskModel
without editing their implementation. Limits observation emission to four fixed UTC
windows/day and 100 500ms decision slots per window. Preserves all intervening
completed-minute geometry, while warming local state independently per window.
Uses only earlier fit/NP calibration days for each chronological development check.
"""
from __future__ import annotations
import argparse,collections,csv,datetime as dt,gzip,json,hashlib,sys,time
from pathlib import Path
from dataclasses import dataclass
ROOT=Path(__file__).resolve().parent
SRC=Path('/mnt/data/r9_entry_router_v2/src')
sys.path.insert(0,str(SRC))
from router_v2_dataset import DAYS,ROLES,iter_ticks,read_teacher,teacher_mark,decision_neutral_gate,source_path
from router_v2_features import RouterV2FeatureEngine,VERSION
from router_v2_labels import ActivePath,outcome_class
from router_v2_train import walkforward,training_example,replay_dev
from router_v2_model import BayesianCompetingRiskModel
HOURS=(0,6,12,18)
WINDOW_MS=9*60_000
CAP=100
SCAN_MS=500

@dataclass
class P:
    path:ActivePath
    q:object
    f:dict
    day:str
    role:str
    native:int

def run_one(root,source,month,teacher,output):
    months=DAYS[month]; dayroles=dict(zip(months,ROLES))
    windows=[]
    for d in months:
        midnight=int(dt.datetime.strptime(d,'%Y-%m-%d').replace(tzinfo=dt.timezone.utc).timestamp()*1000)
        for h in HOURS: windows.append((midnight+h*3600_000,midnight+h*3600_000+WINDOW_MS,d,dayroles[d],h))
    windows.sort();index=0; current=-1
    eng=RouterV2FeatureEngine();active=[];records=[];counts=collections.Counter();last_slot=None;window_qualified=0
    t0=time.monotonic(); sourcefile=source_path(root,source,month)
    for q in iter_ticks(str(sourcefile),source):
        counts['ticks']+=1
        while index<len(windows) and q.utc_ms>=windows[index][1]:index+=1
        inwindow=index<len(windows) and windows[index][0]<=q.utc_ms<windows[index][1]
        if not inwindow:
            eng.minutes.add(q)
            continue
        if current!=index:
            current=index;window_qualified=0;last_slot=None;counts['windows_entered']+=1
            eng.reset_local();eng.last_ms=None
        if active:
            remain=[]
            for p in active:
                o=p.path.update(q)
                if o is None:remain.append(p);continue
                records.append({'source':source,'month':month,'date':p.day,'role':p.role,'utc_ms':o.entry_ms,
                     'native_ms':p.native,'side':o.side,'spread':o.spread,'entry':o.entry_price,
                     'initial_stop':o.initial_stop,'exit_utc_ms':o.exit_ms,'exit_type':o.exit_type,
                     'exit_price':o.exit_price,'net':o.net,'mfe':o.mfe,'mae':o.mae,
                     'cvar_proxy':o.cvar_proxy,'class':outcome_class(o),'teacher':o.teacher,
                     'target_010_ms':o.first_target_ms['0.10'],'target_030_ms':o.first_target_ms['0.30'],
                     'target_050_ms':o.first_target_ms['0.50'],'adverse_stop_ms':o.adverse_stop_ms,
                     'features':p.f})
                counts['labeled']+=1
            active=remain
        eng.add(q)
        # The first five minutes warm completed 250ms buckets, same as production readiness.
        start,end,day,role,h=windows[index]
        if window_qualified>=CAP or q.utc_ms<start+5*60_000: continue
        slot=q.utc_ms//SCAN_MS
        if slot==last_slot:continue
        last_slot=slot;counts['scan_slots']+=1
        feature=eng.snapshot(q)
        if feature is None or not decision_neutral_gate(feature,q):continue
        for side in (1,-1):
            native=q.native_ms or q.utc_ms
            active.append(P(ActivePath(q,side,teacher_mark(q,source,side,teacher)),q,eng.oriented(feature,side),day,role,native))
            counts['started']+=1
        window_qualified+=1;counts['decisions']+=1
    counts['censored']+=len(active)
    path=output/f'{source}_{month}_router_v2_paths.csv.gz'
    if records:
        cols=[*records[0].keys()]
        with gzip.open(path,'wt',newline='') as g:
            w=csv.DictWriter(g,fieldnames=cols);w.writeheader()
            for rec in records:
                d=rec.copy();d['features']=json.dumps(d['features'],separators=(',',':'))
                w.writerow(d)
    else:path.write_bytes(gzip.compress(b''))
    result={'source':source,'month':month,'scope':'BOUNDED_DEV_WINDOWS_NOT_FULL_MONTH',
            'window_hours_utc':HOURS,'window_minutes':9,'warmup_minutes':5,'max_decisions_per_window':CAP,
            'scan_ms':SCAN_MS,'source_name':sourcefile.name,'source_sha256':hashlib.sha256(sourcefile.read_bytes()).hexdigest(),
            'feature_engine':VERSION,'counts':dict(counts),'records':len(records),'elapsed_s':round(time.monotonic()-t0,2)}
    (output/f'{source}_{month}_collection.json').write_text(json.dumps(result,indent=2))
    return result

def main():
    a=argparse.ArgumentParser();a.add_argument('--source',choices=('coinexx','dukascopy'),required=True)
    a.add_argument('--month',choices=tuple(DAYS),required=True);a.add_argument('--data-root',default='/mnt/data')
    a.add_argument('--teacher',default='/mnt/data/r9_four_month_dev/results/synth_teacher_minutes.csv')
    a.add_argument('--out',default='/mnt/data/r9_v2_baseline_4month/bounded_collections')
    x=a.parse_args();out=Path(x.out);out.mkdir(parents=True,exist_ok=True)
    print(json.dumps(run_one(x.data_root,x.source,x.month,read_teacher(x.teacher),out),indent=2),flush=True)
if __name__=='__main__':main()

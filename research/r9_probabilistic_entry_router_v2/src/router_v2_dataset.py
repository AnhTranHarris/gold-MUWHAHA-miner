#!/usr/bin/env python3
"""Chronological real-tick dataset builder for R9 Probabilistic Entry Router v2.

Processes complete source files in original order so rolling 5m and HTF context are
causal. Only declared development days emit BUY/SELL candidate labels. Future ticks
are used after each decision exclusively to resolve first-passage/R9-style outcomes.
"""
from __future__ import annotations
import argparse,collections,csv,datetime as dt,gzip,hashlib,json,sys,time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict,Iterator,List,Tuple
sys.path.insert(0,str(Path(__file__).resolve().parent))
from router_v2_features import Quote,RouterV2FeatureEngine,VERSION
from router_v2_labels import ActivePath,outcome_class

DAYS={
 '01': ('2026-01-06','2026-01-12','2026-01-20','2026-01-27'),
 '02': ('2026-02-03','2026-02-10','2026-02-19','2026-02-26'),
 '06': ('2026-06-02','2026-06-09','2026-06-18','2026-06-25'),
 '07': ('2026-07-02','2026-07-09','2026-07-16','2026-07-28'),
}
ROLES=('fit','fit','np_calibration','development_check')
SCAN_MS=500
SOURCE_SPREAD_CEILING=1.50


def coinexx_offset_minutes(native_ms:int)->int:
    ymd=int(dt.datetime.fromtimestamp(native_ms/1000,dt.timezone.utc).strftime('%Y%m%d'))
    return 180 if 20260309<=ymd<20261102 else 120


def iter_ticks(path:str,source:str)->Iterator[Quote]:
    with gzip.open(path,'rt',newline='') as f:
        for r in csv.DictReader(f):
            if source=='coinexx':
                native=int(r['time_msc']);utc=native-coinexx_offset_minutes(native)*60_000
                bid=float(r['bid']);ask=float(r['ask']);flags=int(r.get('flags') or 0)
                last=float(r.get('last') or 0);vol=float(r.get('volume') or 0);vr=float(r.get('volume_real') or 0)
            elif source=='dukascopy':
                utc=native=int(r['timestamp_ms_utc']);bid=int(r['bid_raw'])/1000;ask=int(r['ask_raw'])/1000
                flags=0;last=vol=vr=0.
            else:raise ValueError(source)
            if 0<bid<=ask:yield Quote(utc,bid,ask,native,flags,last,vol,vr)


def read_teacher(path:str)->Dict[Tuple[str,int],int]:
    d={}
    with open(path,newline='') as f:
        for r in csv.DictReader(f):d[(r['native_minute'],int(r['side']))]=int(r['positive'])
    return d


def teacher_mark(q:Quote,source:str,side:int,teacher:dict)->int:
    # teacher timestamps are Coinexx server-native. Convert Dukascopy UTC to observed Coinexx clock.
    native=q.native_ms if source=='coinexx' else q.utc_ms+coinexx_offset_minutes(q.utc_ms+120*60_000)*60_000
    key=dt.datetime.fromtimestamp(native/1000,dt.timezone.utc).strftime('%Y.%m.%d %H:%M')
    return int(teacher.get((key,side),0)>0)


def date_role_map(month:str)->Dict[str,str]:
    return dict(zip(DAYS[month],ROLES))


def decision_neutral_gate(f:dict,q:Quote)->bool:
    """Direction-neutral opportunity gate; both BUY and SELL are later labeled.

    It rejects only unusable execution states or completely inert markets. It does
    not choose direction and is intentionally permissive for high-volume research.
    """
    if q.spread>SOURCE_SPREAD_CEILING:return False
    if f.get('state_quote_drought',0)>0.55:return False
    activity=max(f.get('hawk_burst_1000',0),f.get('hawk_burst_5000',0))
    movement=abs(f.get('disp_5s',0))+0.5*abs(f.get('disp_1s',0))
    volatility=max(0.,f.get('vol_ratio_5s_5m',0))
    event=abs(f.get('hawk_dir_1000',0))+abs(f.get('hawk_spread_1000',0))
    return activity+movement+0.5*volatility+0.25*event>=0.45


@dataclass
class Pending:
    path:ActivePath
    source:str
    month:str
    date:str
    role:str
    features:dict
    native_ms:int


def source_path(root:str,source:str,month:str)->Path:
    if source=='coinexx':return Path(root)/f'XAUUSD_MT5_BROKER_2026_{month}_ticks_ALL.csv.gz'
    return Path(root)/f'XAUUSD_DUKAS_2026_{month}_ticks.csv.gz'


def build_month(path:str,source:str,month:str,teacher_path:str,out_dir:str,scan_ms:int=SCAN_MS,limit:int|None=None)->dict:
    teacher=read_teacher(teacher_path);roles=date_role_map(month);eng=RouterV2FeatureEngine();active:List[Pending]=[]
    counts=collections.Counter();last_slot=None;records=[];out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    first=None;last=None;t0=time.monotonic()
    for i,q in enumerate(iter_ticks(path,source)):
        if limit is not None and i>=limit:break
        counts['ticks_scanned']+=1;first=q.utc_ms if first is None else first;last=q.utc_ms
        # resolve already-open hypothetical actions before using current quote for a new decision.
        if active:
            rem=[]
            for p in active:
                o=p.path.update(q)
                if o is None:rem.append(p);continue
                records.append({
                    'source':p.source,'month':p.month,'date':p.date,'role':p.role,'utc_ms':o.entry_ms,'native_ms':p.native_ms,
                    'side':o.side,'spread':o.spread,'entry':o.entry_price,'initial_stop':o.initial_stop,
                    'exit_utc_ms':o.exit_ms,'exit_type':o.exit_type,'exit_price':o.exit_price,'net':o.net,'mfe':o.mfe,'mae':o.mae,
                    'cvar_proxy':o.cvar_proxy,'class':outcome_class(o),'teacher':o.teacher,
                    'target_010_ms':o.first_target_ms['0.10'],'target_030_ms':o.first_target_ms['0.30'],'target_050_ms':o.first_target_ms['0.50'],
                    'adverse_stop_ms':o.adverse_stop_ms,'features':p.features,
                });counts['labeled']+=1
            active=rem
        eng.add(q)
        day=dt.datetime.fromtimestamp(q.utc_ms/1000,dt.timezone.utc).strftime('%Y-%m-%d')
        role=roles.get(day)
        if role is None:continue
        counts['selected_ticks']+=1
        slot=q.utc_ms//scan_ms
        if slot==last_slot:continue
        last_slot=slot;counts['scan_slots']+=1
        f=eng.snapshot(q)
        if f is None:counts['not_ready']+=1;continue
        if not decision_neutral_gate(f,q):counts['neutral_reject']+=1;continue
        counts['decision_points']+=1
        # Same causal state, two counterfactual executable actions. WAIT is model action, not future-labeled trade.
        for side in (1,-1):
            oriented=eng.oriented(f,side);tm=teacher_mark(q,source,side,teacher)
            active.append(Pending(ActivePath(q,side,tm),source,month,day,role,oriented,q.native_ms or q.utc_ms));counts['actions_started']+=1
    counts['censored']+=len(active)
    outfile=out/f'{source}_{month}_router_v2_paths.csv.gz'
    fields=['source','month','date','role','utc_ms','native_ms','side','spread','entry','initial_stop','exit_utc_ms','exit_type','exit_price',
            'net','mfe','mae','cvar_proxy','class','teacher','target_010_ms','target_030_ms','target_050_ms','adverse_stop_ms','features']
    with gzip.open(outfile,'wt',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in records:
            row=dict(r);row['features']=json.dumps(r['features'],separators=(',',':'),sort_keys=True);w.writerow(row)
    rep={'version':VERSION,'source':source,'month':month,'input':Path(path).name,'input_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),
         'teacher':Path(teacher_path).name,'scan_ms':scan_ms,'spread_ceiling':SOURCE_SPREAD_CEILING,'counts':dict(counts),'records':len(records),
         'first_utc_ms':first,'last_utc_ms':last,'elapsed_s':round(time.monotonic()-t0,2),'output':outfile.name,
         'runtime_teacher_feature':False,'future_features':False,'htf_context_from_completed_1m_bars':True}
    (out/f'{source}_{month}_router_v2_collection.json').write_text(json.dumps(rep,indent=2))
    return rep


def read_paths(path:str):
    with gzip.open(path,'rt',newline='') as f:
        for r in csv.DictReader(f):
            for k in ('utc_ms','native_ms','side','exit_utc_ms'):r[k]=int(r[k])
            for k in ('target_010_ms','target_030_ms','target_050_ms','adverse_stop_ms'):
                r[k]=int(r[k]) if r[k] not in ('','None',None) else None
            for k in ('spread','entry','initial_stop','exit_price','net','mfe','mae','cvar_proxy'):r[k]=float(r[k])
            r['teacher']=int(r['teacher']);r['features']=json.loads(r['features'])
            yield r


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data-root',required=True);ap.add_argument('--teacher',required=True);ap.add_argument('--out',required=True)
    ap.add_argument('--source',choices=('coinexx','dukascopy'),required=True);ap.add_argument('--month',choices=tuple(DAYS),required=True)
    ap.add_argument('--limit',type=int);ap.add_argument('--scan-ms',type=int,default=SCAN_MS)
    a=ap.parse_args();p=source_path(a.data_root,a.source,a.month)
    print(json.dumps(build_month(str(p),a.source,a.month,a.teacher,a.out,a.scan_ms,a.limit),indent=2))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Replay Delta-A-alpha March vertical-grid discovery 135 from durable timestamp streams.

This reproduces the portfolio accounting/frontier metrics without reparsing raw ticks.
It does NOT rediscover cells. Cell-selection evidence is in
DAA_MARCH_VERTICAL_GRID_CELLS_135.json.
"""
from pathlib import Path
import argparse, heapq, json
from datetime import datetime, timezone
import numpy as np

SYNTH_DAILY = {'2026-03-02': 3969.61, '2026-03-03': 5535.6, '2026-03-04': 3336.62, '2026-03-05': 2943.72, '2026-03-06': 2703.84, '2026-03-09': 3703.33, '2026-03-10': 2285.67, '2026-03-11': 1549.34, '2026-03-12': 1922.11, '2026-03-13': 2025.39, '2026-03-16': 2356.52, '2026-03-17': 1282.16, '2026-03-18': 2162.82, '2026-03-19': 5036.06, '2026-03-20': 4153.22, '2026-03-23': 8729.1, '2026-03-24': 5420.61, '2026-03-25': 3294.31, '2026-03-26': 4149.12, '2026-03-27': 2933.14, '2026-03-30': 3095.24, '2026-03-31': 3111.1}
SYNTH_WEEKLY = {'2026-W10': 18489.39, '2026-W11': 11485.84, '2026-W12': 14990.78, '2026-W13': 24526.28, '2026-W14': 6206.34}

def load_stream(data,name):
    return tuple(data[f"{name}_{k}"] for k in ["E_MS","X_MS","R","D","P","H"])

def dedup(parts):
    seen=set(); out=[]
    for src,Q in parts:
        E,X,R,D,P,H=Q
        for k in range(len(E)):
            e=int(E[k])
            if e in seen: continue
            seen.add(e)
            out.append((e,int(X[k]),int(R[k]),int(D[k]),float(P[k]),float(H[k]),src))
    out.sort(key=lambda r:r[0])
    return out

def cap(rec,n):
    h=[]; out=[]; skips=0; mo=0
    for i,r in enumerate(rec):
        now=r[0]
        while h and h[0][0] <= now: heapq.heappop(h)
        if len(h)>=n:
            skips+=1; continue
        out.append(r); heapq.heappush(h,(r[1],i)); mo=max(mo,len(h))
    return out,mo,skips

def merge_watchdog(wd,supp,capn):
    E,X,R,D,P,H=wd
    rec=[(int(E[k]),int(X[k]),int(R[k]),int(D[k]),float(P[k]),float(H[k]),"WATCHDOG") for k in range(len(E))]
    rec.extend(supp)
    rec.sort(key=lambda r:(r[0],0 if r[6]=="WATCHDOG" else 1))
    return cap(rec,capn)

def score(rec):
    p=np.asarray([r[4] for r in rec],float)
    gp=float(p[p>0].sum()); gl=float(p[p<=0].sum())
    # closed-trade balance DD ordered by exit time
    order=np.argsort(np.asarray([r[1] for r in rec],np.int64),kind="stable")
    pp=p[order]; bal=np.cumsum(pp); prior=np.r_[0.,bal[:-1]]; peak=np.maximum.accumulate(prior)
    bdd=float(np.max(peak-bal)) if len(p) else 0.
    daily={};weekly={}
    for r in rec:
        d=datetime.fromtimestamp(r[1]/1000,tz=timezone.utc)
        ds=d.strftime("%Y-%m-%d"); y,w,_=d.isocalendar(); ws=f"{y}-W{w:02d}"
        if ds.startswith("2026-03"): daily[ds]=daily.get(ds,0.)+r[4]
        weekly[ws]=weekly.get(ws,0.)+r[4]
    return dict(net=float(p.sum()),trades=len(p),gross_loss=gl,
                pf=float(gp/-gl if gl<0 else 999.),win=float(np.mean(p>0)),
                expectancy=float(np.mean(p)),balance_dd=bdd,
                positive_days=sum(daily.get(k,0)>0 for k in SYNTH_DAILY),
                beat_days=sum(daily.get(k,0)>=v for k,v in SYNTH_DAILY.items()),
                positive_weeks=sum(weekly.get(k,0)>0 for k in SYNTH_WEEKLY),
                beat_weeks=sum(weekly.get(k,0)>=v for k,v in SYNTH_WEEKLY.items()),
                daily=daily,weekly=weekly)

def variant(z,native,hv,asia,capn):
    parts=[
        (native,load_stream(z,native)),
        ("COVQ",load_stream(z,"COVQ")),
        (hv,load_stream(z,hv)),
        ("GQSEL",load_stream(z,"GQSEL")),
        ("COLD",load_stream(z,"COLD")),
        (asia,load_stream(z,asia)),
        ("REC1",load_stream(z,"REC1")),
    ]
    supp=dedup(parts); supp,_,_=cap(supp,capn)
    final,mo,sk=merge_watchdog(load_stream(z,"WDQ"),supp,capn)
    return score(final),mo,sk

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--streams",default="DAA_MARCH_VERTICAL_GRID_STREAMS_135.npz")
    args=ap.parse_args()
    with np.load(args.streams) as z:
        data={k:z[k] for k in z.files}
        specs={
            "profit":("NAT","HV2","ASIA",600),
            "balanced":("NAT","HV8","ASIA8",448),
            "quality":("NAT15","HV20","ASIA20",448),
            "ultra":("NAT30","HV20","ASIA20",448),
            "cap92":("NAT15","HV20","ASIA20",92),
        }
        out={}
        for name,spec in specs.items():
            s,mo,sk=variant(data,*spec); s["maxopen_event"]=mo; s["skips"]=sk; out[name]=s
        print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
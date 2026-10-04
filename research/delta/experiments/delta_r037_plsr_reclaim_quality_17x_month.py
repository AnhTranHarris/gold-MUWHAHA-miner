"""Month-isolated worker for DELTA R037 PLSR reclaim-quality 17X.

Uses the committed self-contained 17X core semantics. Each invocation processes
exactly one preregistered evaluation month and atomically writes one result, so an
outer message/tool timeout cannot erase already completed months.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import delta_r037_plsr_reclaim_quality_17x as core

MONTHS=("01A","02","03","04","05","06","07")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--month",choices=MONTHS,required=True)
    ap.add_argument("--current",type=Path,required=True)
    ap.add_argument("--prev",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    if a.month!="01A" and a.prev is None:
        ap.error("--prev is required for Feb-Jul")

    key="01" if a.month=="01A" else a.month
    P={key:a.current}
    if a.month!="01A":
        P[f"{int(a.month)-1:02d}"]=a.prev

    df,start,end=core.load(P,a.month)
    t=df.timestamp_ms_utc.to_numpy("int64")
    if t.size==0 or (t[1:]<t[:-1]).any():
        raise SystemExit(f"17X chronology mismatch {a.month}: {t.size}")
    aa,bb=core.p75(t,df.ask_raw.to_numpy("int64"),df.bid_raw.to_numpy("int64"))

    baseline=core.sim(core.props(t,aa,bb,start,end),t,aa,bb,start,end)
    configs={}
    for cid in core.CFG:
        configs[cid]=core.sim(core.props(t,aa,bb,start,end,cid),t,aa,bb,start,end)

    out={
        "schema":"delta-r037-plsr-reclaim-quality-17x-month-v1",
        "unit":"R037_PLSR_RECLAIM_QUALITY_CROSS_MONTH_17X",
        "month":a.month,
        "surface":"DUKAS_COINEXX_LIKE_P75",
        "loaded_ticks":int(t.size),
        "economic_ticks":int(((t>=start)&(t<end)).sum()),
        "baseline":baseline,
        "configs":configs,
        "numeric_retuning":False,
        "august_accessed":False,
        "mql5_authorized":False,
    }
    core.aw(a.output,out)
    print(json.dumps({"month":a.month,"baseline":baseline,"configs":configs},separators=(",",":")))

if __name__=="__main__":
    main()

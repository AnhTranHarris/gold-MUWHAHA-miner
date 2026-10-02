from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
from numba import njit
from coinexx_r9_adapter import run_raw_r9,raw_result_dict

DAY_MS=86_400_000
US_DST_START_2026_MS=np.int64(1772953200000)
UK_DST_START_2026_MS=np.int64(1774746000000)
PROFILE_NAMES=("P50","P75","P90")
PROFILE_POINTS=np.array([[19,19,19,19],[20,20,21,21],[35,34,23,37]],dtype=np.int64)
WARMUP_MS=90*60*1000

@njit(cache=True)
def session_code_2026(t):
    tod=t%DAY_MS
    ls=7*3_600_000 if t>=UK_DST_START_2026_MS else 8*3_600_000;le=ls+8*3_600_000+30*60_000
    ns=12*3_600_000 if t>=US_DST_START_2026_MS else 13*3_600_000;ne=ns+9*3_600_000
    il=ls<=tod<le;inn=ns<=tod<ne
    if il and inn:return 2
    if il:return 1
    if inn:return 3
    return 0

@njit(cache=True)
def _q_half_raw2_to_tick(target2,tick):return ((target2+tick)//(2*tick))*tick

@njit(cache=True)
def materialize_quotes(t,src_ask,src_bid,profile_idx,price_scale=1000):
    n=t.size;tick=max(1,int(round(.01*price_scale)));ask=np.empty(n,np.int32);bid=np.empty(n,np.int32);maxerr2=0
    for i in range(n):
        s=session_code_2026(np.int64(t[i]));spread=PROFILE_POINTS[profile_idx,s]*tick
        mid2=np.int64(src_ask[i])+np.int64(src_bid[i]);b=_q_half_raw2_to_tick(mid2-spread,tick);a=b+spread
        bid[i]=b;ask[i]=a;e=abs((2*b+spread)-mid2)
        if e>maxerr2:maxerr2=e
    return ask,bid,maxerr2

def profile_index(name):
    n=name.upper()
    if n not in PROFILE_NAMES:raise KeyError(n)
    return PROFILE_NAMES.index(n)

def build_month(cache_root:Path,month:int,profile:str):
    d=cache_root/f"2026_{month:02d}"
    t0=np.load(d/"t_ms.npy",mmap_mode="r");sa0=np.load(d/"ask_raw.npy",mmap_mode="r");sb0=np.load(d/"bid_raw.npy",mmap_mode="r")
    trade_start_ms=int(t0[0]);warmup_ticks=0
    if month>1:
        pd=cache_root/f"2026_{month-1:02d}"
        pt=np.load(pd/"t_ms.npy",mmap_mode="r");pa=np.load(pd/"ask_raw.npy",mmap_mode="r");pb=np.load(pd/"bid_raw.npy",mmap_mode="r")
        cut=int(pt[-1])-WARMUP_MS;i=int(np.searchsorted(pt,cut,"left"));warmup_ticks=len(pt)-i
        t=np.concatenate((pt[i:],t0));sa=np.concatenate((pa[i:],sa0));sb=np.concatenate((pb[i:],sb0))
    else:
        t=t0;sa=sa0;sb=sb0
    a,b,e2=materialize_quotes(t,sa,sb,profile_index(profile),1000)
    return t,a,b,e2,trade_start_ms,warmup_ticks,len(t0)

def run_control(cache_root:Path,month:int,profile:str):
    t,a,b,e2,trade_start,warmup_ticks,scored_ticks=build_month(cache_root,month,profile)
    ints,fl=run_raw_r9(t,a,b,1000,trade_start);r=raw_result_dict(ints,fl)
    r.update({"month":month,"profile":profile.upper(),"ticks_scored":scored_ticks,"warmup_ticks":warmup_ticks,
              "warmup_policy":"90m prior-month tail" if month>1 else "cold-start: no Dec-2025 corpus",
              "surface":"DUKAS_COINEXX_LIKE_MODELED","max_midpoint_error_price":e2/(2*1000.0)})
    return r

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--cache-root",type=Path,required=True);ap.add_argument("--month",type=int,choices=range(1,8),required=True);ap.add_argument("--profile",choices=PROFILE_NAMES,required=True)
    a=ap.parse_args();print(json.dumps(run_control(a.cache_root,a.month,a.profile),indent=2))
if __name__=="__main__":main()

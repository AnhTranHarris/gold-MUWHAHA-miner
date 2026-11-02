"""Corrected direction-neutral 250 ms opportunity/timing universe for R9 v2.

This is an OFFLINE teacher generator, not a filled-trade backtest. It scans every
observed 250 ms quote slot after a 5 minute warmup, applies only execution-validity
(spread) filtering, and independently labels BUY and SELL with the source-exact
R9 30 second lifecycle. Later source records at the same millisecond are honored.
No historical 250 ms delay-teacher labels are consumed.

Overlapping candidate labels are research observations. They MUST NOT be counted
as simultaneous filled positions; final policy evaluation requires one-position
on-policy replay over the original tick sequence.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, math, time
from pathlib import Path
import numpy as np
from numba import njit
from build_repaired_matrix import load_raw
from raw_repaired_features import candidate_indices_250ms

FEE=.02
HOLD_MS=30_000

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for c in iter(lambda:f.read(1<<20),b''):h.update(c)
    return h.hexdigest()

@njit(cache=True)
def _round_tick(v):
    return round(math.floor(v/.01+.5)*.01,2)

@njit(cache=True)
def replay_candidate_pairs(t,bid,ask,idx,fee=.02,hold_ms=30000):
    """Independent BUY/SELL teacher outcomes at exact raw candidate indices."""
    m=len(idx)
    net=np.full((m,2),np.nan,np.float32);good=np.zeros((m,2),np.uint8);neutral=np.zeros((m,2),np.uint8)
    cause=np.zeros((m,2),np.int8);exit_ms=np.full((m,2),-1,np.int64);duration=np.full((m,2),-1,np.int32)
    mfe=np.zeros((m,2),np.float32);mae=np.zeros((m,2),np.float32)
    first_good_ms=np.full((m,2),-1,np.int64);first_bad_ms=np.full((m,2),-1,np.int64)
    for r in range(m):
        i=idx[r];t0=t[i]
        for col in range(2):
            side=1 if col==0 else -1
            entry=ask[i] if side>0 else bid[i]
            liq0=bid[i] if side>0 else ask[i]
            stop=_round_tick(bid[i]-.30 if side>0 else ask[i]+.30)
            fg=-1;fb=-1;maxf=0.;maxa=0.;j=i+1
            while j<len(t):
                px=bid[j] if side>0 else ask[j]
                excursion=(px-entry)*side
                displacement=(px-liq0)*side
                if excursion>maxf:maxf=excursion
                if excursion<maxa:maxa=excursion
                if fg<0 and excursion-fee>=.10-1e-9:
                    fg=j;first_good_ms[r,col]=t[j]
                if fb<0 and displacement<=-.10+1e-9:
                    fb=j;first_bad_ms[r,col]=t[j]
                stop_hit=(px<=stop) if side>0 else (px>=stop)
                if stop_hit:break
                if excursion>=.10-1e-12:
                    newstop=_round_tick(px-side*.03)
                    if side>0:
                        if newstop>stop:stop=newstop
                    else:
                        if newstop<stop:stop=newstop
                if t[j]-t0>=hold_ms:break
                j+=1
            if j>=len(t):continue
            n=(px-entry)*side-fee;net[r,col]=n;exit_ms[r,col]=t[j];duration[r,col]=t[j]-t0;mfe[r,col]=maxf;mae[r,col]=maxa
            if fg>=0 and (fb<0 or fg<fb):cause[r,col]=1
            elif fb>=0 and (fg<0 or fb<fg):cause[r,col]=-1
            else:neutral[r,col]=1
            if cause[r,col]==1 and n>0 and duration[r,col]<=hold_ms:good[r,col]=1
    return net,good,neutral,cause,exit_ms,duration,mfe,mae,first_good_ms,first_bad_ms

def timing_labels(ts,good,net):
    """One-observation WAIT teacher: predict the next observed candidate, never a best future delay."""
    ts=np.asarray(ts,np.int64);good=np.asarray(good,np.uint8);net=np.asarray(net,np.float32);m=len(ts)
    next_dt=np.full(m,-1,np.int32);next_any=np.zeros(m,np.uint8);next_buy=np.zeros(m,np.uint8);next_sell=np.zeros(m,np.uint8)
    wait_improves=np.zeros(m,np.uint8);next_oracle=np.full(m,np.nan,np.float32)
    if m>1:
        d=ts[1:]-ts[:-1];next_dt[:-1]=np.minimum(d,np.iinfo(np.int32).max).astype(np.int32)
        next_buy[:-1]=good[1:,0];next_sell[:-1]=good[1:,1];next_any[:-1]=good[1:].any(axis=1).astype(np.uint8)
        now_any=good[:-1].any(axis=1);wait_improves[:-1]=((~now_any)&(next_any[:-1]==1)).astype(np.uint8)
        next_oracle[:-1]=np.nanmax(net[1:],axis=1)
    return dict(next_dt_ms=next_dt,next_any_good=next_any,next_buy_good=next_buy,next_sell_good=next_sell,
                wait_improves_strict=wait_improves,next_oracle_net=next_oracle)

def day_bounds(day:str):
    d=dt.datetime.strptime(day,'%Y-%m-%d').replace(tzinfo=dt.timezone.utc)
    a=int(d.timestamp()*1000);return a,a+86_400_000

def main(a):
    start=time.monotonic();raw=Path(a.raw);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    t,bid,ask=load_raw(raw,a.source,a.month);idx=candidate_indices_250ms(t,bid,ask,a.warmup_ms,a.max_spread)
    if a.day:
        lo,hi=day_bounds(a.day);m=(t[idx]>=lo)&(t[idx]<hi);idx=idx[m]
    if a.max_candidates and len(idx)>a.max_candidates:idx=idx[:a.max_candidates]
    if len(idx)==0:raise ValueError('no candidates')
    print('candidates',len(idx),'first',int(t[idx[0]]),'last',int(t[idx[-1]]),flush=True)
    result=replay_candidate_pairs(t,bid,ask,idx,FEE,HOLD_MS)
    net,good,neutral,cause,exit_ms,duration,mfe,mae,fg,fb=result
    timing=timing_labels(t[idx],good,net)
    name=f'{a.source}_{a.month}'+(f'_{a.day}' if a.day else '_FULL')+'_250ms_universe'
    path=out/(name+'.npz')
    np.savez_compressed(path,idx=idx,ts=t[idx],bid=bid[idx],ask=ask[idx],net=net,good=good,neutral=neutral,cause=cause,
                        exit_ms=exit_ms,duration=duration,mfe=mfe,mae=mae,first_good_ms=fg,first_bad_ms=fb,**timing)
    valid=np.isfinite(net).all(axis=1);anygood=good.any(axis=1);both=good.sum(axis=1)==2
    receipt=dict(source=a.source,month=a.month,day=a.day,scope='ALL_OBSERVED_250MS_DIRECTION_NEUTRAL_TEACHER_CANDIDATES',
        candidates=len(idx),valid_pair_outcomes=int(valid.sum()),candidate_first_ms=int(t[idx[0]]),candidate_last_ms=int(t[idx[-1]]),
        buy_strict_good=int(good[:,0].sum()),sell_strict_good=int(good[:,1].sum()),any_strict_good=int(anygood.sum()),
        any_strict_good_rate=float(anygood.mean()),neither_strict_good=int((~anygood).sum()),both_strict_good=int(both.sum()),
        wait_improves_next_observed=int(timing['wait_improves_strict'].sum()),
        raw_tick_sha256=sha256(raw),dataset_sha256=sha256(path),fee=FEE,hold_ms=HOLD_MS,max_spread=a.max_spread,warmup_ms=a.warmup_ms,
        historical_250ms_sell_bug_teacher_used=False,same_millisecond_later_source_records_used=True,
        overlapping_teacher_candidates_are_not_filled_trades=True,
        status='TEACHER_UNIVERSE_ONLY_REQUIRES_CAUSAL_FEATURES_AND_ONE_POSITION_ON_POLICY_REPLAY',elapsed_sec=round(time.monotonic()-start,2))
    rp=out/(name+'_receipt.json');rp.write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',choices=('coinexx','dukascopy'),required=True);p.add_argument('--month',required=True)
    p.add_argument('--raw',required=True);p.add_argument('--out',required=True);p.add_argument('--day');p.add_argument('--max-candidates',type=int)
    p.add_argument('--warmup-ms',type=int,default=300000);p.add_argument('--max-spread',type=float,default=1.50);main(p.parse_args())

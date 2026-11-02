#!/usr/bin/env python3
"""R9 v2 source-exact NEW eligible-event/action-time research, not a published policy.

NEW vs prior paired baseline: creates decision events from all chronological quote
250ms slots, not just previous entry timestamps. BUY and SELL at NOW, or at
+250ms/+1s/+3s are independent executable quote actions. Hindsight outcomes
are teacher-only. Waiting is an online re-evaluation, not permission to select
future-best prices. Strict good = first NET +0.10 before liquidation-side -0.10,
then actual R9 stop/trail/timeout exit positive within 30s. Wrong = adverse
first or negative completed outcome. Neutral = neither initial barrier within
30s (or truncated/uncertain). Never insert future labels into runtime features.
"""
from __future__ import annotations
import argparse,gzip,json,hashlib,math,time
from pathlib import Path
import numpy as np,pandas as pd
from numba import njit, prange

DELAYS=(0,250,1000,3000)
COINEXX_MONTHS={'01','02','06','07'}

@njit(cache=False)
def quote_events(ts,bid,ask,slot_ms=250,min_move=.02):
    """Every material completed-slot transition from the complete quote stream.
    No monthly sampling, time-of-day exclusion, arbitrary 10-second polling,
    baseline lane / old-position filter or hindsight guidance.
    Output tick index strictly references quote visible at decision time.
    """
    n=len(ts)
    ix=np.empty(n,np.int64);k=0
    prev_slot=-1
    prev_mid=0.
    start=ts[0] if n else 0
    for i in range(n):
        slot=ts[i]//slot_ms
        if slot!=prev_slot:
            mid=(bid[i]+ask[i])*.5
            if ts[i]-start>=300000 and (k==0 or abs(mid-prev_mid)>=min_move):
                ix[k]=i;k+=1;prev_mid=mid
            prev_slot=slot
    return ix[:k]

@njit(cache=False)
def align_delays(ts,ix,delays):
    out=np.full((len(ix),len(delays)),-1,np.int64)
    n=len(ts)
    for p in range(len(ix)):
        i=ix[p]
        out[p,0]=i
        for k in range(1,len(delays)):
            target=ts[i]+delays[k]
            lo=i+1;hi=n
            while lo<hi:
                mid=(lo+hi)//2
                if ts[mid]<target:lo=mid+1
                else:hi=mid
            if lo<n and ts[lo]-ts[i]<=delays[k]+5000:
                out[p,k]=lo
    return out

@njit(cache=False)
def round_stop(x):
    return round(math.floor(x/.01+0.5)*.01,2)

@njit(cache=False)
def label_trade(ts,bid,ask,i,side):
    """Return code 1 correct, -1 incorrect, 0 neutral; exact R9-style close.
    End of source is censored and NEVER counted as good. Running NET uses
    executable exit bid for BUY, ask for SELL and the assumed $0.02 cost.
    """
    if i<0 or i>=len(ts)-1:return 0,np.nan,-1,0,0
    t0=ts[i];e=ask[i] if side>0 else bid[i]
    liq0=bid[i] if side>0 else ask[i]
    stop=round_stop(bid[i]-.30 if side>0 else ask[i]+.30)
    first=0;first_time=-1;last=-1
    for j in range(i+1,len(ts)):
        liq=bid[j] if side>0 else ask[j]
        gross=(liq-e)*side
        movement=(liq-liq0)*side
        if first==0:
            if gross-.02>=.10-1e-9:
                first=1;first_time=ts[j]-t0
            elif movement<=-.10+1e-9:
                first=-1;first_time=ts[j]-t0
        hit=(liq<=stop if side>0 else liq>=stop)
        if hit:
            last=j;break
        if gross>=.10-1e-12:
            newstop=round_stop(liq-side*.03)
            if side>0:
                if newstop>stop:stop=newstop
            else:
                if newstop<stop:stop=newstop
        if ts[j]-t0>=30000:
            last=j;break
    if last<0:return 0,np.nan,-1,first,first_time
    net=(bid[last]-e)*side-.02 if side>0 else (ask[last]-e)*side*(-1)-.02
    dt=ts[last]-t0
    if dt>30000:return 0,net,dt,first,first_time
    if first==1 and net>0:return 1,net,dt,first,first_time
    if first==0:return 0,net,dt,first,first_time
    return -1,net,dt,first,first_time

@njit(cache=False, parallel=True)
def label_actions(ts,bid,ask,at):
    n=len(at);m=at.shape[1]
    y=np.zeros((n,m,2),np.int8)
    net=np.full((n,m,2),np.nan,np.float32)
    dt=np.full((n,m,2),-1,np.int32)
    cause=np.zeros((n,m,2),np.int8)
    firstdt=np.full((n,m,2),-1,np.int32)
    for p in prange(n):
        for k in range(m):
            ix=at[p,k]
            if ix<0:continue
            for h in range(2):
                side=1 if h==0 else -1
                o,v,d,c,f=label_trade(ts,bid,ask,ix,side)
                y[p,k,h]=o;net[p,k,h]=v;dt[p,k,h]=d;cause[p,k,h]=c;firstdt[p,k,h]=f
    return y,net,dt,cause,firstdt

def load_ticks(source,month):
    root=Path('/mnt/data')
    if source=='coinexx':
        f=root/f'XAUUSD_MT5_BROKER_2026_{month}_ticks_ALL.csv.gz'
        d=pd.read_csv(f,usecols=['time_msc','bid','ask'])
        offset=120 if month in ('01','02') else 180
        t=d.time_msc.to_numpy(np.int64)-offset*60000
        b=d.bid.to_numpy(np.float64);a=d.ask.to_numpy(np.float64)
    else:
        f=root/f'XAUUSD_DUKAS_2026_{month}_ticks.csv.gz'
        d=pd.read_csv(f,usecols=['timestamp_ms_utc','bid_raw','ask_raw'])
        t=d.timestamp_ms_utc.to_numpy(np.int64)
        b=d.bid_raw.to_numpy(np.float64)/1000.;a=d.ask_raw.to_numpy(np.float64)/1000.
    del d
    assert np.all(t[1:]>=t[:-1]);assert np.all(a>=b)
    return t,b,a,f

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
    return h.hexdigest()

def execute(source,month,out:Path,per_chunk=25000,limit=None):
    out.mkdir(parents=True,exist_ok=True)
    t,b,a,raw=load_ticks(source,month)
    ixs=quote_events(t,b,a)
    if limit is not None:ixs=ixs[:limit]
    # Do not report prefix probes as full month datasets.
    chunks=[];tot={'correct':0,'incorrect':0,'neutral':0};start=time.monotonic()
    progress=out/'PROGRESS_FULL.json'
    prior=json.loads(progress.read_text()) if progress.exists() else {}
    saved={d['file']:d for d in prior.get('parts', [])}
    input_hash=prior.get('source_sha256') or sha(raw)
    for k in range(0,len(ixs),per_chunk):
        block=ixs[k:k+per_chunk]
        fname=f'{source}_{month}_action_events_{k//per_chunk:05d}.npz'
        # Full reproducible restart: never recompute already verified chunks.
        if fname in saved:
            meta=saved[fname]
            assert len(block)==meta['n_decisions'] and sha(out/fname)==meta['sha256']
            chunks.append(meta)
            for typ in tot:tot[typ]+=meta['labels'][typ]
            continue
        at=align_delays(t,block,np.array(DELAYS,np.int64))
        y,net,dt,cause,firstdt=label_actions(t,b,a,at)
        np.savez_compressed(out/fname,decision_tick=block,decision_time=t[block],action_tick=at,
                            label=y,net=net,duration=dt,first_cause=cause,first_cause_dt=firstdt)
        hashes={s:int(np.count_nonzero(y==v)) for s,v in [('correct',1),('incorrect',-1),('neutral',0)]}
        for s in tot:tot[s]+=hashes[s]
        chunks.append({'file':fname,'n_decisions':len(block),'sha256':sha(out/fname),'labels':hashes,
                       'first_time_ms':int(t[block[0]]),'last_time_ms':int(t[block[-1]])})
        # Write restartable full-length ledger EACH chunk to avoid losing progress.
        (out/'PROGRESS_FULL.json').write_text(json.dumps({'source':source,'month':month,
          'input_ticks':len(t),'eligible_decisions':len(ixs),'completed_decisions':min(k+len(block),len(ixs)),
          'source_sha256':input_hash,'parts':chunks,'label_counts':tot,
          'status':'PROBE' if limit is not None else ('COMPLETE' if k+len(block)>=len(ixs) else 'IN_PROGRESS')},indent=2))
        print(f'{source} {month}: {k+len(block):,}/{len(ixs):,} decisions; {time.monotonic()-start:.1f}s',flush=True)
    return {'source':source,'month':month,'eligible_decisions':len(ixs),'label_counts':tot,'status':'PROBE' if limit else 'COMPLETE'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',choices=['coinexx','dukascopy'],required=True)
    p.add_argument('--month',choices=['01','02','06','07'],required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--limit',type=int,default=None)
    p.add_argument('--chunk',type=int,default=25000)
    a=p.parse_args();print(execute(a.source,a.month,a.out,a.chunk,a.limit))

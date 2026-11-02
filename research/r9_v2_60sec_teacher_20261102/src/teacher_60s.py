#!/usr/bin/env python3
"""Source-exact up-to-60s hindsight teacher for v2 observed-WAIT entry times.

All future paths are exclusively OFFLINE labels. No future tick, first-passage
cause, chosen delay, or oracle side can appear in an online decision feature.
Every BUY enters ASK / exits BID; SELL enters BID / exits ASK.
Exact R9 stop/trail/30s exit; 60s is the maximum research look-ahead measured
from the original decision, including delayed entries. Never prolong R9 exits.
"""
from __future__ import annotations
import argparse,csv,gzip,json,hashlib
from pathlib import Path
import numpy as np,pandas as pd
from numba import njit

DELAYS=np.array([0,250,1000,3000,5000,15000,30000],np.int64)

@njit(cache=False)
def tickround(x):return round(np.floor(x/.01+.5)*.01,2)

@njit(cache=False)
def forward_action(ts,bid,ask,entry_index,side,fee=.02,horizon_ms=30000):
    """Return class +1 correct / -1 incorrect / 0 neutral, net, first cause,
    first event elapsed, realized close elapsed, exit index.
    Match source tick ordinal, including equal timestamp later records.
    """
    n=len(ts)
    if entry_index<0 or entry_index>=n-1:return 0,np.nan,0,-1,-1,-1
    t0=ts[entry_index];e=ask[entry_index] if side>0 else bid[entry_index]
    liq0=bid[entry_index] if side>0 else ask[entry_index]
    stop=tickround(bid[entry_index]-.30 if side>0 else ask[entry_index]+.30)
    first=0;first_dt=-1
    for j in range(entry_index+1,n):
        px=bid[j] if side>0 else ask[j]
        gross=(px-e)*side
        move=(px-liq0)*side
        if first==0:
            if gross-fee>=.10-1e-9:
                first=1;first_dt=ts[j]-t0
            elif move<=-.10+1e-9:
                first=-1;first_dt=ts[j]-t0
        stop_hit=(px<=stop if side>0 else px>=stop)
        if stop_hit:
            net=gross-fee;elapsed=ts[j]-t0
            if elapsed>horizon_ms:return 0,net,first,first_dt,elapsed,j
            if first==1 and round(net,5)>0:return 1,net,first,first_dt,elapsed,j
            if first==0:return 0,net,first,first_dt,elapsed,j
            return -1,net,first,first_dt,elapsed,j
        if gross>=.10-1e-12:
            proposed=tickround(px-side*.03)
            if side>0:
                if proposed>stop:stop=proposed
            else:
                if proposed<stop:stop=proposed
        if ts[j]-t0>=horizon_ms:
            net=gross-fee;elapsed=ts[j]-t0
            if elapsed>horizon_ms:return 0,net,first,first_dt,elapsed,j
            if first==1 and round(net,5)>0:return 1,net,first,first_dt,elapsed,j
            if first==0:return 0,net,first,first_dt,elapsed,j
            return -1,net,first,first_dt,elapsed,j
    return 0,np.nan,first,first_dt,-1,-1

@njit(cache=False)
def build_labels(ts,bid,ask,entry_ix,sides):
    n=len(entry_ix);nd=len(DELAYS)
    lab=np.zeros((n,nd),np.int8)
    net=np.full((n,nd),np.nan,np.float32)
    first=np.zeros((n,nd),np.int8)
    first_dt=np.full((n,nd),-1,np.int32)
    exit_dt=np.full((n,nd),-1,np.int32)
    selected_tick=np.full((n,nd),-1,np.int64)
    for k in range(n):
        i=entry_ix[k];t0=ts[i]
        for q in range(nd):
            target=t0+DELAYS[q]
            if DELAYS[q]==0:idx=i
            else:
                lo=i+1;hi=len(ts)
                while lo<hi:
                    mid=(lo+hi)//2
                    if ts[mid]<target:lo=mid+1
                    else:hi=mid
                idx=lo
            # Must be a sufficiently timely observed quote with full 30s
            # opportunity inside the 60s decision teaching horizon.
            if idx>=len(ts) or ts[idx]>t0+DELAYS[q]+5000 or ts[idx]>t0+30000:
                continue
            c,v,f,ft,et,x=forward_action(ts,bid,ask,idx,sides[k])
            if x<0 or ts[x]>t0+60000:continue
            lab[k,q]=c;net[k,q]=v;first[k,q]=f
            first_dt[k,q]=ft;exit_dt[k,q]=et;selected_tick[k,q]=idx
    return lab,net,first,first_dt,exit_dt,selected_tick


def source_file(source,mon):
    root=Path('/mnt/data')
    return root/(f'XAUUSD_MT5_BROKER_2026_{mon}_ticks_ALL.csv.gz' if source=='coinexx' else f'XAUUSD_DUKAS_2026_{mon}_ticks.csv.gz')

def load_raw(source,mon):
    file=source_file(source,mon)
    if source=='coinexx':
        data=pd.read_csv(file,usecols=['time_msc','bid','ask'])
        ts=data.time_msc.to_numpy(np.int64).copy()
        # EXACT original per-tick summer/winter time conversion; no fixed seasonal offset across DST.
        from datetime import datetime,timezone
        # For 2026 requested months offsets constant within month.
        offset=120 if mon in ('01','02') else 180
        ts-=offset*60000
        b=data.bid.to_numpy(np.float64);a=data.ask.to_numpy(np.float64)
    else:
        data=pd.read_csv(file,usecols=['timestamp_ms_utc','bid_raw','ask_raw'])
        ts=data.timestamp_ms_utc.to_numpy(np.int64)
        b=data.bid_raw.to_numpy(np.float64)/1000.;a=data.ask_raw.to_numpy(np.float64)/1000.
    assert np.all(ts[1:]>=ts[:-1]) and np.all(b<=a)
    return ts,b,a,file

def load_entries(path):
    v=pd.read_csv(path,usecols=['entry_ms','exit_ms','side','entry_tick_index','feature_bins','class','net'])
    assert v.entry_tick_index.notna().all() and v.feature_bins.notna().all()
    X=np.asarray([np.fromstring(x,sep=',',dtype=np.uint8) for x in v.feature_bins],np.uint8)
    assert X.shape==(len(v),19)
    return v,X

def hash_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
    return h.hexdigest()

def execute(source,mon,root):
    root=Path(root);out=root/'teacher'/f'{source}_{mon}';out.mkdir(exist_ok=True,parents=True)
    progress=out/'receipt.json'
    if progress.exists():
        r=json.loads(progress.read_text());print(json.dumps({'status':'EXISTS_NOT_OVERWRITTEN',**r}));return r
    entries_path=root/'results'/f'{source}_{mon}_full'/'trades.csv.gz'
    v,X=load_entries(entries_path);ts,b,a,raw=load_raw(source,mon)
    ix=v.entry_tick_index.to_numpy(np.int64)
    assert np.all(ts[ix]==v.entry_ms.to_numpy(np.int64))
    assert np.all(np.diff(ix)>0)
    lab,net,cause,firstdt,exitdt,idx=build_labels(ts,b,a,ix,v.side.to_numpy(np.int8))
    # Every NOW counterfactual must reconcile with the observed exact R9
    # lifecycle. This is necessary before any future teacher is trusted.
    orig=np.where(v['class'].to_numpy()=='CORRECT',1,np.where(v['class'].to_numpy()=='INCORRECT',-1,0))
    mismatch_class=int(np.count_nonzero(orig!=lab[:,0]))
    discrepancy=np.abs(v.net.to_numpy(np.float64)-net[:,0])
    censored=(v.exit_ms.to_numpy(np.int64)-v.entry_ms.to_numpy(np.int64)>60000)
    # A gap >60s is unknowable to a 60s teacher; preserve the neutral
    # censoring, never treat an overnight quote as a 30s entry success.
    mismatch_net=int(np.count_nonzero((~np.isfinite(discrepancy)|(discrepancy>1e-4))&~censored))
    if mismatch_class or mismatch_net:raise AssertionError(f'R9 reconciliation FAILED {source} {mon}: class={mismatch_class} net={mismatch_net}; do not publish')
    # Teacher future success = success AFTER a wait, with same side at newly
    # observed quote; target never enters the real-time feature vector.
    wait_rescue=((lab[:,0]!=1)&(lab[:,1:]==1).any(axis=1)).astype(np.uint8)
    npz=out/'teacher_60s.npz'
    np.savez_compressed(npz,X=X,entry_utc_ms=v.entry_ms.to_numpy(np.int64),entry_ix=ix,
          side=v.side.to_numpy(np.int8),observed_class=orig,realized_net=v.net.to_numpy(np.float32),
          delay_ms=DELAYS,delay_class=lab,delay_net=net,first_cause=cause,
          first_event_elapsed_ms=firstdt,exit_elapsed_ms=exitdt,delay_tick_ix=idx,
          wait_rescue=wait_rescue)
    counts={str(int(delay)):{'correct':int(np.sum(lab[:,i]==1)),
          'incorrect':int(np.sum(lab[:,i]==-1)),'neutral':int(np.sum(lab[:,i]==0))} for i,delay in enumerate(DELAYS)}
    receipt={'source':source,'month':mon,'source_sha256':hash_file(raw),'original_trade_sha256':hash_file(entries_path),
         'teacher_file_sha256':hash_file(npz),'trades':len(v),'counts_by_delay':counts,
         'wait_rescue':int(wait_rescue.sum()),'class_mismatch':mismatch_class,'net_mismatch':mismatch_net,
         'censored_after_60s':int(censored.sum()),
         'future_as_feature':False,'status':'COMPLETE_VERIFIED'}
    progress.write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
    return receipt

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True,choices=['coinexx','dukascopy']);ap.add_argument('--month',required=True,choices=['01','02','06','07']);ap.add_argument('--root',default='/mnt/data/v2_new_research/sixty');z=ap.parse_args()
    execute(z.source,z.month,z.root)

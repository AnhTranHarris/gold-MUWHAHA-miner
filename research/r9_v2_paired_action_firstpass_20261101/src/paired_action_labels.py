#!/usr/bin/env python3
"""Different research mechanism: paired BUY/SELL first-passage and native-R9 exit labels.

Never passed to inference: the future real quote path. Entry set is the EXACT
full-month untrained-lane trade-event set (off-policy fixed opportunities).
This does not simulate newly available trades after skipped/reversed positions.
Original v2/repair source remains unchanged. Same-millisecond event sequence
is resolved by source index. 0.01 lot, research fee=0.02, no slippage.
"""
from __future__ import annotations
import argparse,gzip,zipfile,json,time,hashlib,math
from pathlib import Path
import numpy as np, pandas as pd
from numba import njit
RAW=Path('/mnt/data')
OUT=RAW/'r9_v2_counterfactual_action_20261101'/'results'
SYNTH={'01':27980,'02':33523,'06':31801,'07':24382}

@njit(cache=True)
def find_quote(ts,bid,ask,t0,px0,sides):
    n=len(ts);m=len(t0);found=np.full(m,-1,np.int64)
    p=0
    for k in range(m):
        t=t0[k]
        while p<n and ts[p]<t:p+=1
        j=p
        while j<n and ts[j]==t:
            v=ask[j] if sides[k]>0 else bid[j]
            if abs(v-px0[k])<1.e-5:
                found[k]=j;break
            j+=1
    return found

@njit(cache=True)
def money_tick(v):
    return round(math.floor(v/.01+0.5)*.01,2)

@njit(cache=True)
def replay_pairs(ts,bid,ask,idx,sides,ref_exit,ref_net):
    m=len(idx)
    # per original entry: original direction, opposite direction
    net=np.full((m,2),np.nan,np.float32)
    within=np.zeros((m,2),np.uint8)
    good=np.zeros((m,2),np.uint8)
    neutral=np.zeros((m,2),np.uint8)
    cause=np.zeros((m,2),np.int8)
    duration=np.full((m,2),-1,np.int32)
    exit_time=np.full((m,2),-1,np.int64)
    maxfav=np.zeros((m,2),np.float32)
    maxadv=np.zeros((m,2),np.float32)
    exact_matches=0
    for k in range(m):
        i=idx[k]
        if i<0:continue
        t0=ts[i];entry_ask=ask[i];entry_bid=bid[i]
        for option in range(2):
            s=sides[k] if option==0 else -sides[k]
            e=entry_ask if s>0 else entry_bid
            stop=money_tick(entry_bid-.30 if s>0 else entry_ask+.30)
            liq0=entry_bid if s>0 else entry_ask
            first_good=-1;first_bad=-1;maxf=-1.e12;maxa=1.e12
            j=i+1
            while j<len(ts):
                liquid=bid[j] if s>0 else ask[j]
                gross=(liquid-e)*s
                d=(liquid-liq0)*s
                if gross>maxf:maxf=gross
                if gross<maxa:maxa=gross
                if first_good<0 and gross-.02>=.10-1e-9:first_good=j
                if first_bad<0 and d<=-.10+1e-9:first_bad=j
                stop_hit=liquid<=stop if s>0 else liquid>=stop
                if stop_hit:
                    break
                if gross>=.10-1e-12:
                    newstop=money_tick(liquid-s*.03)
                    if s>0:
                        if newstop>stop:stop=newstop
                    else:
                        if newstop<stop:stop=newstop
                if ts[j]-t0>=30000:break
                j+=1
            if j>=len(ts):continue
            n=(liquid-e)*s-.02
            net[k,option]=n
            exit_time[k,option]=ts[j]
            dtime=ts[j]-t0
            duration[k,option]=dtime
            within[k,option]=1 if dtime<=30000 else 0
            maxfav[k,option]=maxf;maxadv[k,option]=maxa
            if first_good>=0 and (first_bad<0 or first_good<first_bad):cause[k,option]=1
            elif first_bad>=0 and (first_good<0 or first_bad<first_good):cause[k,option]=-1
            else:neutral[k,option]=1
            if cause[k,option]==1 and n>0 and dtime<=30000:good[k,option]=1
        # reference baseline modeled net should agree exactly with original R9 exit model
        if not np.isnan(net[k,0]) and abs(net[k,0]-ref_net[k])<.00001 and exit_time[k,0]==ref_exit[k]:exact_matches+=1
    return net,within,good,neutral,cause,duration,exit_time,maxfav,maxadv,exact_matches

def load(src,month):
    raw=RAW/(f'XAUUSD_MT5_BROKER_2026_{month}_ticks_ALL.csv.gz' if src=='coinexx' else f'XAUUSD_DUKAS_2026_{month}_ticks.csv.gz')
    columns=['time_msc','bid','ask'] if src=='coinexx' else ['timestamp_ms_utc','bid_raw','ask_raw']
    with gzip.open(raw,'rt') as f:
        df=pd.read_csv(f,usecols=columns)
    if src=='coinexx':
        offset=(120 if month in ('01','02') else 180)*60000
        t=df.time_msc.to_numpy(np.int64)-offset
        b=df.bid.to_numpy(np.float64);a=df.ask.to_numpy(np.float64)
    else:
        t=df.timestamp_ms_utc.to_numpy(np.int64)
        b=df.bid_raw.to_numpy(np.float64)/1000.;a=df.ask_raw.to_numpy(np.float64)/1000.
    assert np.all(t[1:]>=t[:-1])
    z=zipfile.ZipFile(RAW/f'R9_V2_FULLMONTH_{src.upper()}_2026_{month}_EXACT.zip')
    with gzip.open(z.open('full_run/trades.csv.gz'),'rt') as f:
        tr=pd.read_csv(f)
    z.close()
    return t,b,a,tr,raw

def filehash(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()

def main(src,mon):
    start=time.monotonic();OUT.mkdir(parents=True,exist_ok=True)
    path=OUT/f'{src}_{mon}_paired_counterfactual.npz';report=OUT/f'{src}_{mon}_paired_receipt.json'
    if path.exists() and report.exists():
        prior=json.loads(report.read_text());assert filehash(path)==prior['dataset_sha256'];print('VERIFIED EXISTING '+str(report));return
    t,b,a,tr,raw=load(src,mon)
    sides=tr.side.to_numpy(np.int8);entry=tr.entry_ms.to_numpy(np.int64)
    matched=find_quote(t,b,a,entry,tr.entry_price.to_numpy(np.float64),sides)
    outputs=replay_pairs(t,b,a,matched,sides,tr.exit_ms.to_numpy(np.int64),tr.net.to_numpy(np.float64))
    net,within,good,neutral,cause,dur,ext,mfe,mae,exact=outputs
    assert int((matched>=0).sum())==len(tr), 'missing exact quote matches'
    if exact!=len(tr):
        mismatch=np.where((np.abs(net[:,0]-tr.net.to_numpy())>=1e-5)|(ext[:,0]!=tr.exit_ms.to_numpy()))[0]
        print('MISMATCH SAMPLE',src,mon, len(mismatch),mismatch[:10].tolist(),flush=True)
    np.savez_compressed(path,ts=entry,side=sides,matched=matched,net=net,within=within,good=good,neutral=neutral,cause=cause,duration=dur,exit_time=ext,mfe=mfe,mae=mae)
    # Oracle is impossible at runtime; quantify same-event action selection supply only.
    best=np.argmax(net,axis=1)
    bestnet=net[np.arange(len(tr)),best]
    both_good=(good.sum(axis=1)==2)
    anygood=(good.sum(axis=1)>0)
    quota=int(math.ceil(.85*SYNTH[mon]));oracle_good=int(anygood.sum())
    results={'source':src,'month':mon,'ticks':len(t),'baseline_entries':len(tr),'exact_quote_matches':int((matched>=0).sum()),
      'baseline_replay_exact_matches':int(exact), 'baseline_replay_discrepancies':len(tr)-int(exact),
      'baseline_net':round(float(net[:,0].sum(dtype=np.float64)),2),
      'opposite_net_if_forced':round(float(net[:,1].sum(dtype=np.float64)),2),
      'best_side_hindsight_mean_net':round(float(bestnet.mean(dtype=np.float64)),5),
      'any_side_strict_good_count':oracle_good,'any_side_strict_good_rate':round(oracle_good/len(tr),6),
      'both_sides_strict_good_count':int(both_good.sum()),
      'original_side_strict_good_rate':round(float(good[:,0].mean()),6),
      'opposite_side_strict_good_rate':round(float(good[:,1].mean()),6),
      'monthly_85percent_synth_floor':quota,
      'hindsight_supply_reaches_floor':oracle_good>=quota,
      'source_tick_sha256':filehash(raw),'dataset_sha256':filehash(path),
      'schema':'paired same-time BUY/SELL counterfactual R9-style lifecycle and first +0.10 net before -0.10 liquidation displacement; future labels teacher-only',
      'scientific_boundary':'OFF-POLICY fixed baseline entries. No newly freed opportunity replay. No hindsight side selection may be presented as runtime foresight.',
      'elapsed_sec':round(time.monotonic()-start,2)}
    report.write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2),flush=True)

if __name__=='__main__':
    pa=argparse.ArgumentParser();pa.add_argument('--source',required=True,choices=('coinexx','dukascopy'));pa.add_argument('--month',required=True,choices=('01','02','06','07'));args=pa.parse_args();main(args.source,args.month)

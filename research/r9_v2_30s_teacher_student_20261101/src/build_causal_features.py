#!/usr/bin/env python3
"""Construct past-only full-source XAUUSD quote/event features at each frozen v2 entry.
Every 1s window ends BEFORE the entry second; current executable spread/evidence
come only from the original, timestamped entry decision. No target or teacher data
is used anywhere in the causal feature calculation.
"""
from __future__ import annotations
import argparse, json, time
from pathlib import Path
import numpy as np, pandas as pd

ROOT=Path('/mnt/data');OUT=ROOT/'v2_30s_teacher_training/results';OUT.mkdir(parents=True,exist_ok=True)
HORIZONS=(1,5,15,45,300,900,3600,14400)

def make_features(source,month):
    start_time=time.monotonic();s=source.lower();m=f'{int(month):02d}'
    if s=='coinexx':
        fp=ROOT/f'XAUUSD_MT5_BROKER_2026_{m}_ticks_ALL.csv.gz'
        ticks=pd.read_csv(fp,compression='gzip',usecols=['time_msc','bid','ask'],dtype={'time_msc':'int64','bid':'float32','ask':'float32'})
        offset=120 if m in ('01','02') else 180
        ms=ticks.pop('time_msc').to_numpy()-offset*60000
    else:
        fp=ROOT/f'XAUUSD_DUKAS_2026_{m}_ticks.csv.gz'
        ticks=pd.read_csv(fp,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
        ms=ticks.pop('timestamp_ms_utc').to_numpy();ticks=ticks.rename(columns={'bid_raw':'bid','ask_raw':'ask'})
        ticks['bid']=ticks.bid/1000;ticks['ask']=ticks.ask/1000
    bid=ticks.bid.to_numpy(dtype=np.float64,copy=False)
    ask=ticks.ask.to_numpy(dtype=np.float64,copy=False)
    mid=(bid+ask)*.5
    spr=ask-bid
    db=np.diff(bid,prepend=bid[0]);da=np.diff(ask,prepend=ask[0]);ds=np.diff(spr,prepend=spr[0])
    eps=1e-7
    sec=(ms//1000).astype(np.int64)
    # Do not invent time buckets for seconds without quotes.
    data=pd.DataFrame({'sec':sec, 'mid':mid.astype(np.float32),'sp':spr.astype(np.float32),
        'bu':(db>eps).astype(np.int8),'bd':(db<-eps).astype(np.int8),
        'au':(da>eps).astype(np.int8),'ad':(da<-eps).astype(np.int8),
        'sw':(ds>eps).astype(np.int8),'sn':(ds<-eps).astype(np.int8),
        'bid_only':((np.abs(db)>eps)&(np.abs(da)<=eps)).astype(np.int8),
        'ask_only':((np.abs(da)>eps)&(np.abs(db)<=eps)).astype(np.int8),
        'joint':((np.abs(db)>eps)&(np.abs(da)>eps)).astype(np.int8)})
    # Every grouped second uses only quotes received that second.
    bars=data.groupby('sec',sort=True).agg(mid=('mid','last'),spread=('sp','last'),
        n=('mid','size'),bu=('bu','sum'),bd=('bd','sum'),au=('au','sum'),ad=('ad','sum'),
        sw=('sw','sum'),sn=('sn','sum'),bid_only=('bid_only','sum'),ask_only=('ask_only','sum'),joint=('joint','sum'))
    del data,ticks,mid,spr,bid,ask,db,da,ds,sec,ms
    seconds=bars.index.to_numpy(dtype=np.int64)
    mid=bars['mid'].to_numpy(dtype=np.float64)
    n=bars['n'].to_numpy(dtype=np.float64)
    spread=bars['spread'].to_numpy(dtype=np.float64)
    frame=pd.DataFrame(index=np.arange(len(bars)))
    frame['second_utc']=seconds
    frame['q_mid']=mid
    frame['q_spread']=spread
    frame['q_last_sec_count']=n
    # Time-based windows without forward fill. All arrays are shifted to completed
    # seconds by the searchsorted(join) below; no current partial 1s bar leaks.
    dtidx=pd.to_datetime(seconds,unit='s',utc=True)
    series=pd.Series(mid,index=dtidx)
    for h in HORIZONS:
        left=np.searchsorted(seconds,seconds-h+1,side='left')
        span=np.arange(len(seconds))-left+1
        # Intrinsic readiness is time span, not just number of quote seconds.
        frame[f'ready_{h}s']=(seconds-seconds[left]>=max(0,h-2)).astype('int8')
        frame[f'disp_{h}s']=(mid-mid[left]).astype('float32')
        if h!=1:
            r=series.rolling(f'{h}s',min_periods=1)
            lo=r.min().to_numpy();hi=r.max().to_numpy()
            frame[f'range_{h}s']=(hi-lo).astype('float32')
            # Bollinger position from completed seconds only.
            mean=r.mean().to_numpy();std=r.std(ddof=0).fillna(0).to_numpy()
            frame[f'bbpos_{h}s']=np.clip((mid-mean)/(2*std+1e-7),-10,10).astype('float32')
            frame[f'vol_{h}s']=std.astype('float32')
            frame[f'location_{h}s']=((mid-lo)/(hi-lo+1e-6)).astype('float32')
        # Causal tick-event rate per observed wall-clock interval.
        c=np.r_[0,np.cumsum(n)]
        frame[f'quote_rate_{h}s']=((c[np.arange(1,len(n)+1)]-c[left])/h).astype('float32')
        if h in (1,5,15,45,300):
            for label in ('bu','bd','au','ad','sw','sn','bid_only','ask_only','joint'):
                x=bars[label].to_numpy(dtype=np.float64)
                cum=np.r_[0,np.cumsum(x)]
                frame[f'{label}_rate_{h}s']=((cum[np.arange(1,len(x)+1)]-cum[left])/h).astype('float32')
        if h in (5,45,300):
            a=frame[f'bu_rate_{h}s']+frame[f'au_rate_{h}s']
            b=frame[f'bd_rate_{h}s']+frame[f'ad_rate_{h}s']
            frame[f'quote_pressure_{h}s']=((a-b)/(a+b+1e-4)).astype('float32')
            ss=frame[f'sn_rate_{h}s'];sw=frame[f'sw_rate_{h}s']
            frame[f'spread_pressure_{h}s']=((ss-sw)/(ss+sw+1e-4)).astype('float32')

    # Associating an entry to its most recent COMPLETED second gives a fixed
    # causal 0-999ms data boundary. Entry's actual spread/evidence remain allowed.
    entries=pd.read_pickle(OUT/f'{s}_{m}_raw.pkl')
    prevsec=(entries.entry_ms.to_numpy(dtype='int64')//1000)-1
    indices=np.searchsorted(seconds,prevsec,side='right')-1
    chosen=frame.iloc[np.maximum(0,indices)].reset_index(drop=True)
    chosen.loc[indices<0,chosen.columns.difference(['second_utc'])]=np.nan
    # The H1/H4 context flags explicitly identify unready windows.
    chosen['lag_to_completed_s']=((entries.entry_ms.to_numpy()//1000)-chosen['second_utc'].to_numpy())
    # Existing v2 engine candidate features. They were calculated at entry before
    # any outcome and are not recomputed from hindsight paths.
    for col in ['side','spread','evidence','entry_price','entry_ms','exit_ms','net','mfe','mae','lane','win','target','neutral','hour','day_id','week_id']:
        chosen[col]=entries[col].to_numpy()
    chosen['source']=s
    chosen['month']=int(m)
    chosen.to_pickle(OUT/f'{s}_{m}_features.pkl')
    summary={'source':s,'month':m,'source_ticks':int(sum(n)),'observed_seconds':int(len(seconds)),
        'entries':int(len(chosen)),'features':int(chosen.shape[1]),
        'max_lag_to_completed_sec':int(chosen.lag_to_completed_s.max()),
        'ready_4h_fraction':float(chosen['ready_14400s'].mean()),
        'duration_s':round(time.monotonic()-start_time,2)}
    (OUT/f'{s}_{m}_feature_provenance.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary),flush=True)
    return summary
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('month');args=p.parse_args()
    make_features(args.source,args.month)

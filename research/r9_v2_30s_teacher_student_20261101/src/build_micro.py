#!/usr/bin/env python3
"""Exact completed-250ms quote-side event history, fully source-order causal.
Only source ticks < (entry_ms//250)*250 belong to a predictive feature.
Never references outcome columns or SYNTH teaching labels.
"""
import sys,time,json
from pathlib import Path
import numpy as np,pandas as pd
R=Path('/mnt/data/v2_30s_teacher_training/results');DATA=Path('/mnt/data')

def run(source,m):
    t=time.monotonic();m=f'{int(m):02d}'
    if source=='coinexx':
        z=DATA/f'XAUUSD_MT5_BROKER_2026_{m}_ticks_ALL.csv.gz'
        d=pd.read_csv(z,usecols=['time_msc','bid','ask'],dtype={'time_msc':'int64','bid':'float32','ask':'float32'})
        ms=d.time_msc.to_numpy(dtype=np.int64,copy=False)-(120 if m in ('01','02') else 180)*60000
        bid=d.bid.to_numpy(dtype=np.float32,copy=False);ask=d.ask.to_numpy(dtype=np.float32,copy=False)
    else:
        z=DATA/f'XAUUSD_DUKAS_2026_{m}_ticks.csv.gz'
        d=pd.read_csv(z,usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
        ms=d.timestamp_ms_utc.to_numpy(dtype=np.int64,copy=False)
        bid=d.bid_raw.to_numpy(dtype=np.float64)/1000;ask=d.ask_raw.to_numpy(dtype=np.float64)/1000
    slot=ms//250
    boundaries=np.r_[0,np.flatnonzero(slot[1:]!=slot[:-1])+1]
    unique_slots=slot[boundaries]
    end=np.r_[boundaries[1:]-1,len(slot)-1]
    midclose=(bid[end].astype('float64')+ask[end].astype('float64'))*.5
    midopen=(bid[boundaries].astype('float64')+ask[boundaries].astype('float64'))*.5
    spread=ask-bid
    delta_bid=np.diff(bid.astype('float64'),prepend=float(bid[0]));delta_ask=np.diff(ask.astype('float64'),prepend=float(ask[0]))
    # Delta zero across a large gap does not invent quote response; no synthetic ticks.
    eps=1e-7;dsp=delta_ask-delta_bid
    events={
        'bu':(delta_bid>eps), 'bd':(delta_bid<-eps),'au':(delta_ask>eps),'ad':(delta_ask<-eps),
        'sw':(dsp>eps),'sn':(dsp<-eps),
        'bidonly':((abs(delta_bid)>eps)&(abs(delta_ask)<=eps)),
        'askonly':((abs(delta_ask)>eps)&(abs(delta_bid)<=eps)),
        'joint':((abs(delta_bid)>eps)&(abs(delta_ask)>eps)),
        'upjoint':((delta_bid>eps)&(delta_ask>eps)),
        'downjoint':((delta_bid<-eps)&(delta_ask<-eps))
    }
    event_counts={key:np.add.reduceat(v.astype('int16'),boundaries).astype('int32') for key,v in events.items()}
    event_counts['ticks']=(end-boundaries+1).astype('int32')
    cs={name:np.r_[0,np.cumsum(v,dtype=np.int64)] for name,v in event_counts.items()}
    entries=pd.read_pickle(R/f'{source}_{m}_raw.pkl')
    entry_slot=entries.entry_ms.to_numpy(dtype=np.int64)//250
    # EXACT strict cutoff: no quote in the entry's incomplete 250-ms slot.
    ri=np.searchsorted(unique_slots,entry_slot,side='left')-1
    ri=np.maximum(ri,0)
    features={}
    for horizon in (250,500,1000,5000):
        hs=horizon//250
        lo=np.searchsorted(unique_slots,entry_slot-hs,side='left')
        hi=ri+1
        lo=np.minimum(lo,hi)
        valid=hi>lo
        qcount=np.maximum(1,cs['ticks'][hi]-cs['ticks'][lo])
        suffix=f'{horizon}ms'
        for name in ('bu','bd','au','ad','sw','sn','bidonly','askonly','joint','upjoint','downjoint'):
            total=cs[name][hi]-cs[name][lo]
            features[f'micro_{name}_{suffix}']=(total/qcount).astype(np.float32)
        features[f'micro_tickrate_{suffix}']=(qcount/(horizon/1000)).astype(np.float32)
        features[f'micro_disp_{suffix}']=np.where(valid,midclose[ri]-midopen[np.minimum(len(midopen)-1,lo)],0.).astype(np.float32)
        ups=(cs['bu'][hi]-cs['bu'][lo])+(cs['au'][hi]-cs['au'][lo]);dns=(cs['bd'][hi]-cs['bd'][lo])+(cs['ad'][hi]-cs['ad'][lo])
        features[f'micro_pressure_{suffix}']=((ups-dns)/(ups+dns+1)).astype(np.float32)
        features[f'micro_quote_divergence_{suffix}']=(((cs['bu'][hi]-cs['bu'][lo])-(cs['bd'][hi]-cs['bd'][lo])-(cs['au'][hi]-cs['au'][lo])+(cs['ad'][hi]-cs['ad'][lo]))/qcount).astype(np.float32)
        features[f'micro_ready_{suffix}']=(unique_slots[ri]-unique_slots[np.minimum(lo,len(unique_slots)-1)]>=max(0,hs-1)).astype(np.int8)
    features['micro_lag_ms']=((entry_slot-unique_slots[ri])*250).astype(np.int32)
    features['micro_latest_spread']=spread[end[ri]].astype(np.float32)
    features['micro_last_250ms_disp']=(midclose[ri]-midopen[ri]).astype(np.float32)
    # Explicit stale after quotes drought; no future quote filling.
    dfeat=pd.DataFrame(features)
    dfeat.to_pickle(R/f'{source}_{m}_micro.pkl')
    rec={'source':source,'month':m,'quotes_scanned':int(len(ms)),'completed_250ms_slots':int(len(unique_slots)),
         'entries_joined':int(len(entries)),'micro_features':len(features),'strictly_prior_to_entry_slot':True,
         'max_micro_lag_ms':int(features['micro_lag_ms'].max()),'elapsed_s':round(time.monotonic()-t,2)}
    (R/f'{source}_{m}_micro_manifest.json').write_text(json.dumps(rec,indent=2))
    print(rec,flush=True)
if __name__=='__main__':run(sys.argv[1],sys.argv[2])

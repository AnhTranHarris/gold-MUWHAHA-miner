#!/usr/bin/env python3
"""Complete-month as-of tick feature extraction for the high-volume v2 trade stream.

For each recorded entry match the ORIGINAL quote at the same millisecond AND
at the entry execution price (ask for buy, bid for sell). Compute all event
features only from ticks with index <= matched quote. Any ambiguous/missing
match fails closed and is excluded from supervised fitting.
This is a historical candidate-stream trainer, not yet a filtered-policy rerun.
"""
from __future__ import annotations
import argparse,datetime as dt,gzip,json,zipfile,os,time,hashlib
from pathlib import Path
import numpy as np,pandas as pd
from numba import njit
ROOT=Path('/mnt/data')
HORIZONS=np.array([250,500,1000,5000,15000,45000,300000,900000,3600000,14400000],dtype=np.int64)

@njit(cache=True)
def match_entries(ts,bid,ask,entry_t,entry_px,side):
    n=len(ts);m=len(entry_t);out=np.full(m,-1,np.int64)
    # seek through millisecond-ordered source tick records; may match later ticks at same ms
    i=0
    for j in range(m):
        t=entry_t[j]
        while i<n and ts[i]<t: i+=1
        k=i
        while k<n and ts[k]==t:
            px=ask[k] if side[j]>0 else bid[k]
            if abs(px-entry_px[j])<0.00001:
                out[j]=k;break
            k+=1
    return out

@njit(cache=True)
def extract(t,bid,ask,matches):
    m=len(matches);n=len(t);q=((bid+ask)*.5);sp=ask-bid
    names_len=7+len(HORIZONS)*8
    data=np.full((m,names_len),np.nan,np.float32)
    # prefix events; both bid and ask changes are observable not true LOB flow
    bu=np.zeros(n+1,np.int64); bd=bu.copy();au=bu.copy();ad=bu.copy();sw=bu.copy();sn=bu.copy()
    ss=np.zeros(n+1,np.float64);ss2=ss.copy();diff2=ss.copy()
    for i in range(1,n+1):
        j=i-1
        ss[i]=ss[i-1]+sp[j];ss2[i]=ss2[i-1]+sp[j]*sp[j]
        if j>0:
            d1=bid[j]-bid[j-1];d2=ask[j]-ask[j-1];dsp=sp[j]-sp[j-1];dq=q[j]-q[j-1]
            diff2[i]=diff2[i-1]+dq*dq
            bu[i]=bu[i-1]+int(d1>1e-9);bd[i]=bd[i-1]+int(d1<-1e-9)
            au[i]=au[i-1]+int(d2>1e-9);ad[i]=ad[i-1]+int(d2<-1e-9)
            sw[i]=sw[i-1]+int(dsp>1e-9);sn[i]=sn[i-1]+int(dsp<-1e-9)
        else:
            diff2[i]=diff2[i-1];bu[i]=bu[i-1];bd[i]=bd[i-1];au[i]=au[i-1];ad[i]=ad[i-1];sw[i]=sw[i-1];sn[i]=sn[i-1]
    for row in range(m):
        i=matches[row]
        if i<0:continue
        data[row,0]=sp[i]
        data[row,1]=q[i]
        data[row,2]=bid[i]
        data[row,3]=ask[i]
        data[row,4]=(bu[i+1]-bd[i+1])-(au[i+1]-ad[i+1])
        data[row,5]=(q[i]-q[max(0,i-1)])
        data[row,6]=(sp[i]-sp[max(0,i-1)])
        col=7
        for k in range(len(HORIZONS)):
            horizon=HORIZONS[k]
            j=np.searchsorted(t,t[i]-horizon,side='left')
            ct=i-j+1
            disp=q[i]-q[j]
            spread_mean=(ss[i+1]-ss[j])/ct
            bid_delta=bid[i]-bid[j];ask_delta=ask[i]-ask[j]
            moveup=(bu[i+1]-bu[j])+(au[i+1]-au[j])
            movedown=(bd[i+1]-bd[j])+(ad[i+1]-ad[j])
            spreadcompress=(sn[i+1]-sn[j])-(sw[i+1]-sw[j])
            rv=diff2[i+1]-diff2[j]
            data[row,col]=disp;data[row,col+1]=spread_mean;data[row,col+2]=bid_delta
            data[row,col+3]=ask_delta;data[row,col+4]=(moveup-movedown)/(moveup+movedown+1.0)
            data[row,col+5]=spreadcompress/(ct+1)
            data[row,col+6]=np.sqrt(max(rv,0.0))
            data[row,col+7]=ct/(horizon/1000)
            col+=8
    return data

def source_file(src,month):
    return ROOT/(f'XAUUSD_MT5_BROKER_2026_{month}_ticks_ALL.csv.gz' if src=='coinexx' else f'XAUUSD_DUKAS_2026_{month}_ticks.csv.gz')

def load_ticks(src,month):
    path=source_file(src,month)
    cols=['time_msc','bid','ask'] if src=='coinexx' else ['timestamp_ms_utc','bid_raw','ask_raw']
    chunks=[]
    with gzip.open(path,'rt') as f:
        for c in pd.read_csv(f,usecols=cols,chunksize=1000000):
            chunks.append(c)
    df=pd.concat(chunks,ignore_index=True);del chunks
    if src=='coinexx':
        tm=df['time_msc'].to_numpy(np.int64)-int(120 if month in ('01','02') else 180)*60000
        bid=df['bid'].to_numpy(np.float64);ask=df['ask'].to_numpy(np.float64)
    else:
        tm=df['timestamp_ms_utc'].to_numpy(np.int64)
        bid=df['bid_raw'].to_numpy(np.float64)*.001;ask=df['ask_raw'].to_numpy(np.float64)*.001
    assert np.all(tm[1:]>=tm[:-1]),'nonchronological input ticks'
    return tm,bid,ask

def load_trades(src,month):
    z=zipfile.ZipFile(ROOT/f'R9_V2_FULLMONTH_{src.upper()}_2026_{month}_EXACT.zip')
    with gzip.open(z.open('full_run/trades.csv.gz'),'rt') as f: df=pd.read_csv(f)
    z.close()
    assert np.all(df.entry_ms.to_numpy()[1:]>=df.entry_ms.to_numpy()[:-1])
    return df

def main():
    pa=argparse.ArgumentParser();pa.add_argument('--source',choices=['coinexx','dukascopy'],required=True);pa.add_argument('--month',choices=['01','02','06','07'],required=True);a=pa.parse_args()
    start=time.monotonic();out=ROOT/'r9_v2_eight_source_training_20261101/checkpoints';out.mkdir(parents=True,exist_ok=True)
    trades=load_trades(a.source,a.month);tm,bid,ask=load_ticks(a.source,a.month)
    idx=match_entries(tm,bid,ask,trades.entry_ms.to_numpy(np.int64),trades.entry_price.to_numpy(np.float64),trades.side.to_numpy(np.int8))
    print('match',a.source,a.month,len(trades),np.count_nonzero(idx>=0),'of',len(idx),flush=True)
    matrix=extract(tm,bid,ask,idx)
    names=['spread_actual','mid','bid','ask','quote_side_imbalance','delta_mid_tick','delta_spread_tick']
    for h in HORIZONS:
        names.extend([f'{k}_{h}' for k in ('mid_displacement','spread_mean','bid_displacement','ask_displacement','revision_imbalance','spread_compress','realized_vol','tick_rate')])
    fdf=pd.DataFrame(matrix,columns=names)
    # never give model future result, executed price, or raw absolute gold price that makes date identifiable
    fdf=fdf.drop(columns=['mid','bid','ask'])
    df=pd.concat([trades,fdf],axis=1)
    df['matched_quote']=idx>=0
    df['duration_ms']=df.exit_ms-df.entry_ms
    df['label_30s_win']=((df.net>0)&(df.duration_ms<=30000)).astype(np.uint8)
    df['label_30s_neutral']=((df.duration_ms>30000)|(df.net.abs()<=.02+1e-10)).astype(np.uint8)
    df['label_30s_adverse']=((df.duration_ms<=30000)&(df.net<-.02-1e-10)).astype(np.uint8)
    datetimes=pd.to_datetime(df.entry_ms,unit='ms',utc=True)
    df['utc_hour']=datetimes.dt.hour.astype(np.int8)
    df['utc_weekday']=datetimes.dt.dayofweek.astype(np.int8)
    df['day']=datetimes.dt.strftime('%Y-%m-%d')
    df['week']=datetimes.dt.strftime('%G-W%V')
    df['source']=a.source;df['month']=a.month
    df['side']=df.side.astype(np.int8)
    df['lane_code']=(df.lane=='continuation').astype(np.int8)
    # model feed for horizon 15m 1h 4h only when actual lookback available
    for h in (900000,3600000,14400000):
        df[f'ready_{h}']=((df.entry_ms-tm[0])>=h).astype(np.uint8)
    path=out/f'{a.source}_{a.month}_tick_asof.pkl.gz'
    df.to_pickle(path,compression={'method':'gzip','compresslevel':1})
    report={'source':a.source,'month':a.month,'rows':len(df),'tick_rows':len(tm),'exact_price_timestamp_matched':int((idx>=0).sum()),'mismatch_count':int((idx<0).sum()),'labeled_win':int(df.label_30s_win.sum()),'labeled_neutral':int(df.label_30s_neutral.sum()),'labeled_adverse':int(df.label_30s_adverse.sum()),'dataset':path.name,'dataset_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'elapsed_sec':round(time.monotonic()-start,2)}
    (out/f'{a.source}_{a.month}_feature_receipt.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':main()

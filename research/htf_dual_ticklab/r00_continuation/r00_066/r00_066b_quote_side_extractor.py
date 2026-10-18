"""R00-066 native quote-prefix feature adapter layered on EXISTING R00-063 extractor.

No independent quote timestamp reader reconstruction: use same recorded raw input column and
clock shift from the unchanged published R00-063 Python engine. No target/y is read here.
Event row quote_index is the original source index. No forward dependency is permitted.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

FEATURE_NAMES=['bid_tick_delta','ask_tick_delta','last_bid_only','last_ask_only','last_both','spread_tick_delta']
for w in (4,16,64,256): FEATURE_NAMES += [f'bid_net_{w}',f'ask_net_{w}',f'spread_change_{w}',f'time_for_{w}_quotes_ms']
for w in (16,64,256):FEATURE_NAMES += [f'bid_update_count_{w}',f'ask_update_count_{w}',f'bid_signed_pressure_{w}',f'ask_signed_pressure_{w}']
FEATURE_NAMES += ['since_last_bid_ms','since_last_ask_ms']

def quote_features(t:np.ndarray,b:np.ndarray,a:np.ndarray,indices:np.ndarray,events:np.ndarray)->np.ndarray:
    t=np.asarray(t,dtype=np.int64);b=np.asarray(b,dtype=np.float64);a=np.asarray(a,dtype=np.float64)
    i=np.asarray(indices,dtype=np.int64);et=np.asarray(events,dtype=np.int64)
    if not(len(t)==len(a)==len(b)) or len(t)==0 or np.any(i<0) or np.any(i>=len(t)):
        raise ValueError('source and indices must exist')
    if not np.array_equal(t[i],et):raise ValueError('event not matched to exact authorized original quote index and UTC')
    if np.any(np.diff(t)<0) or np.any(a<b):raise ValueError('incorrect raw chronology/quote spread')
    db=np.empty(len(t));da=np.empty(len(t));db[0]=0;da[0]=0;db[1:]=np.diff(b);da[1:]=np.diff(a)
    cb=np.abs(db)>1e-8;ca=np.abs(da)>1e-8
    prev=np.maximum(i-1,0);s=a-b
    columns=[db[i],da[i],(cb&~ca)[i].astype(float),(~cb&ca)[i].astype(float),(cb&ca)[i].astype(float),s[i]-s[prev]]
    for w in (4,16,64,256):
        p=np.maximum(i-w,0)
        columns.extend([b[i]-b[p],a[i]-a[p],s[i]-s[p],(t[i]-t[p])/1000])
    c_b=np.cumsum(cb,dtype=np.int64);c_a=np.cumsum(ca,dtype=np.int64)
    for w in (16,64,256):
        p=np.maximum(i-w,0)
        count_b=c_b[i]-c_b[p];count_a=c_a[i]-c_a[p]
        columns.extend([count_b,count_a,(b[i]-b[p])/np.maximum(count_b,1),(a[i]-a[p])/np.maximum(count_a,1)])
    lastb=np.maximum.accumulate(np.where(cb,np.arange(len(t)),0));lasta=np.maximum.accumulate(np.where(ca,np.arange(len(t)),0))
    columns.extend([(t[i]-t[lastb[i]])/1000,(t[i]-t[lasta[i]])/1000])
    X=np.column_stack(columns).astype(np.float32)
    assert X.shape==(len(i),len(FEATURE_NAMES))
    assert np.all(np.isfinite(X))
    return X


def read_quotes_existing_contract(filepath,broker,month):
    """Exact unchanged R00-063 input schema and timezone transform. Source hash must be checked before call."""
    if broker=='dukascopy':
        df=pd.read_csv(filepath,usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
        t=df['timestamp_ms_utc'].to_numpy(copy=True)
        ask=df['ask_raw'].to_numpy(dtype=np.float64)/1000
        bid=df['bid_raw'].to_numpy(dtype=np.float64)/1000
    else:
        df=pd.read_csv(filepath,usecols=['time_msc','bid','ask'],dtype={'time_msc':'int64','bid':'float32','ask':'float32'})
        t=df['time_msc'].to_numpy(copy=True)
        t-=(120 if month in ('01','02') else 180)*60000
        ask=df['ask'].to_numpy(dtype=np.float64)
        bid=df['bid'].to_numpy(dtype=np.float64)
    del df
    return t,bid,ask

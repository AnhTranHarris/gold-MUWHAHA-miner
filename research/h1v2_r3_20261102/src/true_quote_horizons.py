"""H1V2 R3 additive TRUE first-to-current multi-horizon quote features.

Unlike the repaired 99 geometry 'terminal range location' proxy, these
features represent actual as-of quote displacement and genuine raw arrival
counts. No future rows, no midpoint execution prices, no OHLC interpolation.
R9 execution and teacher labels remain original bid/ask tick-ordinal.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
from h1v2_teacher import read_ticks
from h1v2_freeze import PINNED

MONTHS=('01','02','06','07')
HORIZONS_MS=np.array([250,1000,5000,15000,30000,60000,300000,900000,3600000,14400000],np.int64)

def calc(t,b,a,ix):
    """Each lower/anchor tick is already observed (<=current index)."""
    if len(ix)==0:return np.empty((0,len(HORIZONS_MS)*3),np.float32)
    assert np.all((ix>=0)&(ix<len(t))) and np.all(t[1:]>=t[:-1])
    now=t[ix]
    mid=(b+a)*.5
    columns=[]
    for h in HORIZONS_MS:
        # Prior cutoff quote, never a future quote; use most recent quote at
        # or before t-h (right - 1). Missing history flagged distinctly.
        start=np.searchsorted(t,now-h,side='right')-1
        old=np.maximum(start,0)
        valid=(start>=0)&(now-t[old]>=h)&(now-t[old]<=h+600000)
        # Protect against sessions closing: if earlier quote is stale > 10min
        # beyond desired boundary, the exact HTF anchor is unavailable.
        displacement=np.where(valid,mid[ix]-mid[old],np.nan)
        abs_travel=np.where(valid,np.abs(displacement),np.nan)
        first=np.searchsorted(t,now-h,side='left')
        count=(ix-first+1).clip(0)
        quote_rate=np.where(valid,count/np.maximum(h/1000.,.001),np.nan)
        columns.extend([displacement.astype(np.float32),abs_travel.astype(np.float32),quote_rate.astype(np.float32)])
        assert np.all(old<=ix)
    return np.column_stack(columns).astype(np.float32)

def feat_classes(z):
    """Input z columns = signed true displacement, magnitude and raw event rate."""
    h=HORIZONS_MS;d=z[:,0::3];rate=z[:,2::3]
    out={}
    for j,label in [(0,'250ms'),(1,'1s'),(2,'5s'),(3,'15s'),(4,'30s'),(5,'60s'),(6,'5m'),(7,'15m'),(8,'1h'),(9,'4h')]:
        cut=.02 if j<=2 else (.10 if j<=5 else .30)
        val=d[:,j];out['true_trend_'+label]=np.where(np.isnan(val),3,np.where(val>cut,2,np.where(val<-cut,0,1))).astype(np.int16)
        n=rate[:,j]
        out['quote_rate_'+label]=np.where(np.isnan(n),3,np.where(n>10,2,np.where(n<2,0,1))).astype(np.int16)
    return out

def run(raw_root=Path('/mnt/data'),atlas_root=Path('/mnt/data/h1v2_r2/results'),out_root=Path('/mnt/data/h1v2_r3/results')):
    out_root.mkdir(exist_ok=True,parents=True)
    receipt={}
    for m in MONTHS:
        raw=raw_root/f'XAUUSD_DUKAS_2026_{m}_ticks.csv.gz'
        digest=hashlib.sha256(raw.read_bytes()).hexdigest()
        assert digest==PINNED[m],f'raw source hash changed for {m}'
        with np.load(atlas_root/f'H1V2_R2_{m}_SIDE_INDEPENDENT_HARD_NEGATIVES.npz',allow_pickle=False) as dataset:
            ix=dataset['ix'].copy();timestamp=dataset['ts'].copy()
        t,b,a=read_ticks(raw)
        assert np.array_equal(t[ix],timestamp)
        x=calc(t,b,a,ix)
        assert np.mean(np.isfinite(x[:,:18]))>.95, 'too many unavailable subminute quote anchors'
        p=out_root/f'H1V2_R3_TRUE_PATH_{m}.npz'
        np.savez_compressed(p,asof_X=x,ix=ix,ts=timestamp,horizons_ms=HORIZONS_MS)
        sha=hashlib.sha256(p.read_bytes()).hexdigest()
        receipt[m]={'sha256':sha,'source_sha256':digest,'rows':len(ix), 'features':x.shape[1],
            'fraction_valid_4h':float(np.mean(np.isfinite(x[:,-3]))),
            'fraction_valid_15m':float(np.mean(np.isfinite(x[:,7*3]))),
            'first_250ms_true_disp_p50':float(np.nanmedian(x[:,0]))}
        print('source-month',m,'quote-features',receipt[m],flush=True)
    (out_root/'H1V2_R3_TRUE_PATH_RECEIPT.json').write_text(json.dumps(receipt,indent=2))
    return receipt

if __name__=='__main__':run()

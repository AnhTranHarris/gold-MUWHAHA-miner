"""F401 research preflight — native marked quote arrival information, strictly before t0.

No trading signals are promoted here. Preserve immutable source-event (time,index,side,
truth) and use the frozen F395 survivor mask and F398 H1023 scores as controls.
Source quote updates are L1 BID/ASK changes, *not* aggressive trade direction or L2 flow.
All features deliberately stop at the last COMPLETE 1s/5s/HTF bar before t0.
No 30-32s diagnostic outcome enters an online state before its 33.001s maturity.
"""
from __future__ import annotations
import argparse, hashlib, io, json, math, pathlib, zipfile
from dataclasses import dataclass
from typing import Iterator
import numpy as np

try:
    import pandas as pd
except ImportError:
    pd = None

MONTHS=('01','02','06','07')
BROKERS=('coinexx','dukascopy')
MARKS=('bid_only','ask_only','joint','unchanged','bid_up','bid_down','ask_up','ask_down')
WINDOWS=(2,10,30,120,300)
PERIODS=(60,300,900,3600)

@dataclass
class SecondsState:
    start_sec: int
    end_sec: int
    counts: dict
    open_mid: np.ndarray
    close_mid: np.ndarray
    high_mid: np.ndarray
    low_mid: np.ndarray
    spread_last: np.ndarray
    quote_count: np.ndarray
    source_rows: int


def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(8<<20),b''):
            h.update(b)
    return h.hexdigest()


def quote_chunk_reader(path, broker, month, chunksize=500_000) -> Iterator[tuple[np.ndarray,np.ndarray,np.ndarray]]:
    if pd is None:
        raise RuntimeError('pandas is required for CSV.GZ source streaming')
    if broker=='coinexx':
        names=['time_msc','bid','ask']
        for d in pd.read_csv(path,usecols=names,chunksize=chunksize):
            yield (d['time_msc'].to_numpy(np.int64)-(120 if month in ('01','02') else 180)*60_000,
                d['bid'].to_numpy(np.float64),d['ask'].to_numpy(np.float64))
    else:
        names=['timestamp_ms_utc','bid_raw','ask_raw']
        for d in pd.read_csv(path,usecols=names,chunksize=chunksize):
            yield (d['timestamp_ms_utc'].to_numpy(np.int64),
                d['bid_raw'].to_numpy(np.float64)*.001,d['ask_raw'].to_numpy(np.float64)*.001)


def marked_seconds(chunks, first_sec, last_sec):
    """Stream original published quote rows. Compare adjacent quotes across chunks.
    Never infer signed taker flow from quote revisions. Does not smooth same-ms order.
    """
    n=last_sec-first_sec+1
    if n<=0 or n>10_000_000: raise ValueError('invalid or unexpectedly large source span')
    cnt={name:np.zeros(n,dtype=np.int32) for name in MARKS}
    qcount=np.zeros(n,dtype=np.int32)
    op=np.full(n,np.nan);cl=np.full(n,np.nan)
    hi=np.full(n,-np.inf);lo=np.full(n,np.inf);spr=np.full(n,np.nan)
    last=None;last_time=None;row_total=0
    for t,bid,ask in chunks:
        if not len(t):continue
        if np.any(~np.isfinite(bid)) or np.any(~np.isfinite(ask)) or np.any(ask<bid):
            raise ValueError('invalid source price/spread')
        if np.any(np.diff(t)<0) or (last_time is not None and t[0]<last_time):
            raise ValueError('source quote UTC chronology violated')
        sec=t//1000-first_sec
        full_mid=(bid+ask)*.5
        # Count each native quote, even if prices unchanged; mark classification is
        # anchored to the previous source quote, and persists over CSV chunks.
        all_prevb=np.r_[last[0] if last is not None else bid[0],bid[:-1]]
        all_preva=np.r_[last[1] if last is not None else ask[0],ask[:-1]]
        # Retain the last quote for cross-chunk comparisons even if out of the
        # bounded target window; original raw tick rows remain untouched.
        prev_last=last
        last=(bid[-1],ask[-1]);last_time=int(t[-1]);row_total+=len(t)
        eligible=(sec>=0)&(sec<n)
        if not np.any(eligible):continue
        bid=bid[eligible];ask=ask[eligible];sec=sec[eligible]
        prevb=all_prevb[eligible];preva=all_preva[eligible]
        mid=full_mid[eligible]
        np.add.at(qcount,sec,1)
        u,starts=np.unique(sec,return_index=True)
        ends=np.r_[starts[1:],len(sec)]-1
        missing=np.isnan(op[u]);op[u[missing]]=mid[starts[missing]]
        cl[u]=mid[ends];spr[u]=(ask-bid)[ends]
        np.maximum.at(hi,sec,mid);np.minimum.at(lo,sec,mid)
        bc=bid!=prevb;ac=ask!=preva
        masks={
            'bid_only':bc&~ac,'ask_only':ac&~bc,'joint':bc&ac,
            'unchanged':~bc&~ac,'bid_up':bid>prevb,'bid_down':bid<prevb,
            'ask_up':ask>preva,'ask_down':ask<preva,
        }
        if prev_last is None and eligible[0]:
            masks['unchanged'][0]=False  # first ever source row has no predecessor
        for name,mask in masks.items():
            if np.any(mask): np.add.at(cnt[name],sec[mask],1)
    return SecondsState(first_sec,last_sec,cnt,op,cl,hi,lo,spr,qcount,row_total)


def bayesian_poisson_changepoint(k, hazard=1/200, max_run=48, a0=.5, b0=1.):
    """Finite-run-length conjugate Gamma/Poisson Bayesian online CP posterior.
    Each observation is a COMPLETED 5-second source-bin marked-arrival count.
    H(r=0) records a change; growth is run-length capped, never looks forward.
    """
    from scipy.special import gammaln
    if not (0<hazard<1) or max_run<2:raise ValueError('invalid hazard/runlength')
    k=np.asarray(k,dtype=np.float64)
    if np.any(k<0) or np.any(k!=np.floor(k)):raise ValueError('Poisson count must be nonnegative integer')
    probs=np.zeros(max_run,dtype=np.float64);probs[0]=1.
    shape=np.full(max_run,a0);rate=np.full(max_run,b0)
    posterior_cp=np.empty(len(k),dtype=np.float32)
    posterior_run=np.empty(len(k),dtype=np.float32)
    idx=np.arange(max_run)
    for j,count in enumerate(k):
        logpred=(gammaln(count+shape)-gammaln(shape)-gammaln(count+1)
                 +shape*np.log(rate/(rate+1))+count*np.log(1/(rate+1)))
        pred=np.exp(logpred-np.max(logpred));w=probs*pred
        new=np.zeros_like(probs);new[0]=hazard*w.sum()
        new[1:]=(1-hazard)*w[:-1]
        # Truncate run lengths >= max_run and renormalize retained posterior.
        # Never merge a nonconjugate overflow mixture into one fake Gamma state.
        total=new.sum()
        if total<=0:raise FloatingPointError('Bayesian update lost probability mass')
        new/=total
        newshape=np.full_like(shape,a0+count);newrate=np.full_like(rate,b0+1)
        newshape[1:]=shape[:-1]+count;newrate[1:]=rate[:-1]+1
        # capped tail combines two hypotheses; keep conservative summary from newer branch
        probs,shape,rate=new,newshape,newrate
        posterior_cp[j]=probs[0];posterior_run[j]=np.dot(idx,probs)
    return posterior_cp,posterior_run


def features_at_t0(d:SecondsState, event_ms, side, *, compute_cp=True):
    """Only last COMPLETE second/bar is visible; nothing from event's own second.

    The original quote-index is immutable; this conservatively excludes even
    preceding quotes in the same millisecond/second to avoid ambiguous ordering.
    """
    ev=np.asarray(event_ms,dtype=np.int64);sg=np.asarray(side,dtype=np.int8)
    if ev.shape!=sg.shape or np.any(~np.isin(sg,[-1,1])):raise ValueError('invalid events/sides')
    prevsec=ev//1000-1-d.start_sec
    valid=(prevsec>=0)&(prevsec<len(d.quote_count))
    j=np.clip(prevsec,0,len(d.quote_count)-1)
    cols=[];names=[]
    def add(name,arr):
        arr=np.asarray(arr,dtype=np.float64)
        if arr.shape!=ev.shape:raise ValueError(f'{name} wrong shape')
        arr=np.nan_to_num(arr,nan=0,posinf=0,neginf=0)
        cols.append(np.where(valid,arr,0).astype(np.float32));names.append(name)
    add('observed_completed_second',valid.astype(float))
    for window in WINDOWS:
        a=np.maximum(0,j-window+1)
        for typ in MARKS:
            c=np.r_[0,d.counts[typ].cumsum(dtype=np.int64)]
            add(f'{typ}_n{window}s',c[j+1]-c[a])
        q=np.r_[0,d.quote_count.cumsum(dtype=np.int64)]
        add(f'quotes_n{window}s',q[j+1]-q[a])
        add(f'quote_drought_n{window}s',(q[j+1]-q[a]==0).astype(float))
    # Last completed one-second spread, 5/15/60 min completed-HTF hazards.
    s_last=np.full(len(d.quote_count),np.nan);seen=np.flatnonzero(d.quote_count>0)
    if len(seen):
        prev=np.searchsorted(seen,np.arange(len(d.quote_count)),side='right')-1
        good=prev>=0;s_last[good]=d.spread_last[seen[prev[good]]]
    add('last_completed_spread',s_last[j]);
    # Midpoint for fully completed source candle; no partial candle extrapolation.
    if len(seen):
        lastclose=np.full(len(d.quote_count),np.nan);lastclose[seen]=d.close_mid[seen]
    else:lastclose=np.full(len(d.quote_count),np.nan)
    for period in PERIODS:
        # Group full calendar bars using epoch-second UTC alignment.
        bar_ids=(np.arange(len(d.quote_count))+d.start_sec)//period
        starts=np.r_[0,np.flatnonzero(np.diff(bar_ids))+1]
        ends=np.r_[starts[1:],len(d.quote_count)]
        if len(starts)<2: continue
        b_hi=np.maximum.reduceat(d.high_mid,starts)
        b_lo=np.minimum.reduceat(d.low_mid,starts)
        b_open=np.full(len(starts),np.nan);b_close=np.full(len(starts),np.nan)
        for bar_idx,(a,z) in enumerate(zip(starts,ends)):
            s=np.flatnonzero(d.quote_count[a:z]>0)
            if len(s):b_open[bar_idx]=d.open_mid[a+s[0]];b_close[bar_idx]=d.close_mid[a+s[-1]]
        # Last bar whose right boundary is <= decision timestamp. Since this is
        # index by complete seconds, it's strictly < current event-second.
        eb=(ev//1000)//period-1
        b=np.searchsorted(bar_ids[starts],eb,side='right')-1
        ok=(b>=0)&(b<len(starts));safe=np.clip(b,0,len(starts)-1)
        good=valid&ok&np.isfinite(b_open[safe])
        add(f'completed_{period}s_body_signed',np.where(good,(b_close[safe]-b_open[safe])*sg,0))
        add(f'completed_{period}s_range',np.where(good,b_hi[safe]-b_lo[safe],0))
        add(f'completed_{period}s_age_bars',np.where(good,(ev//1000)//period-bar_ids[starts[safe]],0))
    if compute_cp:
        # Native bid-only/ask-only/joint counts in EXACTLY completed 5s bins.
        bins=(np.arange(len(d.quote_count))+d.start_sec)//5
        a=np.r_[0,np.flatnonzero(np.diff(bins))+1]
        native=d.counts['bid_only']+d.counts['ask_only']+d.counts['joint']
        bin_count=np.add.reduceat(native,a)
        cp,run=bayesian_poisson_changepoint(bin_count)
        # Ignore the entire current 5-second bucket even when partially observed.
        ebin=ev//5000-1
        pos=np.searchsorted(bins[a],ebin,side='right')-1
        good=pos>=0;pos=np.maximum(pos,0)
        add('bocpd_5s_posterior_cp',np.where(good,cp[pos],0))
        add('bocpd_5s_posterior_run',np.where(good,run[pos],0))
    return np.column_stack(cols),names


def verify_event_source(archive):
    """Read immutable F395 source-event identities without mutating source ZIP."""
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise ValueError('original F395 ZIP CRC failure')
        source={}
        for broker in BROKERS:
            for month in MONTHS:
                key=f'{broker}_{month}'
                p=f'F395_S14_{key}_FROZEN_ORIGINAL_EVENT_MASK.npz'
                with np.load(io.BytesIO(z.read(p))) as d:
                    ix=d['original_index'];t=d['t'];side=d['side'];truth=d['truth']
                    if not np.array_equal(ix,np.arange(len(ix))):raise ValueError(f'{key} event index changed')
                    if np.any(np.diff(t)<0):raise ValueError(f'{key} event chronology changed')
                    if not set(np.unique(truth)).issubset({0,1,2}):raise ValueError(f'{key} truth class changed')
                    source[key]={'rows':len(t),'right':int((truth==0).sum()),
                        'bad':int((truth!=0).sum()),'kept':int((~d['final_source_shadow_veto']).sum())}
    return source


def validate_source_pins(archive, quote_file,broker,month):
    with zipfile.ZipFile(archive) as z:
        pins=json.loads(z.read('F386_S04_S05_SOURCE_DEPENDENCY_PINS.json'))['original_quote_files']
    filename=f'XAUUSD_MT5_BROKER_2026_{month}_ticks_ALL.csv.gz' if broker=='coinexx' else f'XAUUSD_DUKAS_2026_{month}_ticks.csv.gz'
    if pathlib.Path(quote_file).name!=filename:raise ValueError('source filename does not match original registry')
    expected=pins[filename]['registered_sha256']
    actual=sha256(quote_file)
    if expected!=actual:raise ValueError(f'SHA mismatch: {filename} expected {expected} observed {actual}')
    return expected


def main():
    p=argparse.ArgumentParser(description='F401 bounded source-native marked quote information preflight')
    p.add_argument('--approved-source-archive',required=True)
    p.add_argument('--broker',choices=BROKERS,required=True)
    p.add_argument('--month',choices=MONTHS,required=True)
    p.add_argument('--quote-file',required=True)
    p.add_argument('--output',required=True)
    args=p.parse_args()
    hash_used=validate_source_pins(args.approved_source_archive,args.quote_file,args.broker,args.month)
    with zipfile.ZipFile(args.approved_source_archive) as z:
        pth=f'F395_S14_{args.broker}_{args.month}_FROZEN_ORIGINAL_EVENT_MASK.npz'
        with np.load(io.BytesIO(z.read(pth))) as d:
            ev=d['t'].copy();side=d['side'].copy();truth=d['truth'].copy()
            orig=d['original_index'].copy();parent=d['final_source_shadow_veto'].copy()
    first_sec=int(ev.min()//1000)-3601
    last_sec=int(ev.max()//1000)+1
    seconds=marked_seconds(quote_chunk_reader(args.quote_file,args.broker,args.month),first_sec,last_sec)
    X,names=features_at_t0(seconds,ev,side)
    out=pathlib.Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(out,X=X,t=ev,side=side,truth=truth,original_index=orig,f395_parent_veto=parent,
                        feature_names=np.array(names),source_sha256=hash_used)
    print(json.dumps({'status':'F401_UNSCORED_PREORDER_FEATURE_EXTRACTION','source_sha256':hash_used,
        'quote_rows':seconds.source_rows,'original_events':len(ev),'features':len(names),
        'artifact':str(out),'note':'No trained model, no matched placebo, no approval or trading result.'},indent=2))

if __name__=='__main__':main()

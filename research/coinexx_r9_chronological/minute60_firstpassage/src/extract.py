"""Source-ordered Coinexx XAUUSD R9 entry universe: 60s as-of sequences +
independent strict first-passage labels from actual future bid/ask ticks.

No synthetic M1 paths. No future information in X. Future path ONLY for y.
The R9 candidate reference is frozen and is not recomputed or relabeled.
"""
import argparse,csv,gzip,hashlib,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

RAW = Path('/mnt/data')  # Convenience default only, can override in CLI
CACHE=RAW/'r9_shadow_path_signatures/outputs'
N_SAMPLES=120
STEP_MS=500
HORIZONS=np.array([5000,15000,30000],dtype=np.int64)
TARGET=50 # quote price cents favorable (gross) = modeled cost 20 + net 30
STOP=30   # adverse gross 30 = modeled net -50
COST=20
LABEL={1:'TARGET_FIRST',0:'STOP_FIRST',2:'NO_BARRIER',-1:'CENSORED'}

@njit(cache=True)
def first_passage(ms,bid,ask,ordinals,sides,entry_prices):
    """Each row uses the actual preselected R9 entry price, then real quote-side exits.

    Labels = +1 target first, 0 stop first, 2 no barrier before horizon,
    -1 censored (gap > 10 seconds or insufficient future data).
    """
    n=len(ordinals); lab=np.full((n,3),-1,np.int8)
    hit_ms=np.full((n,3),-1,np.int32)
    lastret=np.full((n,3),0,np.int32)
    for k in range(n):
        ix=ordinals[k]; t0=ms[ix]; side=sides[k]; entry=entry_prices[k]
        prev=t0; res=2; ht=-1; next_h=0; last=-(ask[ix]-bid[ix])
        j=ix+1
        while j<len(ms) and next_h<3:
            dt=ms[j]-t0
            if dt>HORIZONS[2]:break
            if ms[j]-prev>10000:
                res=-1;break
            while next_h<3 and dt>HORIZONS[next_h]:
                lab[k,next_h]=res;hit_ms[k,next_h]=ht;lastret[k,next_h]=last
                next_h+=1
            if next_h>=3:break
            pnl=bid[j]-entry if side==1 else entry-ask[j]
            last=pnl
            if pnl>=TARGET:
                res=1;ht=int(dt);break
            if pnl<=-STOP:
                res=0;ht=int(dt);break
            prev=ms[j]
            j+=1
        if res==1 or res==0:
            while next_h<3:
                lab[k,next_h]=res;hit_ms[k,next_h]=ht;lastret[k,next_h]=last
                next_h+=1
        elif res==-1:
            while next_h<3:
                lab[k,next_h]=-1;lastret[k,next_h]=last
                next_h+=1
        else:
            while next_h<3:
                h=HORIZONS[next_h]
                # when month ends earlier than horizon no continuous observation.
                if j>=len(ms) and (ms[-1]-t0)<h:
                    lab[k,next_h]=-1
                else:
                    lab[k,next_h]=2
                lastret[k,next_h]=last
                next_h+=1
    return lab,hit_ms,lastret


def make_sequences(ms,bid,ask,ordinals,sides):
    """500ms sample grid [t0-59.5s, ..., t0], each sampled at the last
    actual observed quote <= grid time, clipped by exact decision ordinal.
    No use of row after entry even for duplicate equal-ms timestamps.
    """
    n=len(ordinals);x=np.empty((n,5,N_SAMPLES),np.float32)
    valid=np.ones(n,bool);invalid_reason={}
    offsets=(np.arange(N_SAMPLES,dtype=np.int64)-N_SAMPLES+1)*STEP_MS
    midpoint=(bid.astype(np.int64)+ask.astype(np.int64))*.5
    spread=(ask-bid).astype(np.float32)
    for k,(at,side) in enumerate(zip(ordinals,sides)):
        t0=ms[at]
        grid=t0+offsets
        if grid[0]<ms[0]:
            valid[k]=False;invalid_reason['warmup']=invalid_reason.get('warmup',0)+1;continue
        indices=np.searchsorted(ms,grid,side='right')-1
        # Equal-millisecond ordinals never introduce future source quotes.
        np.minimum(indices,at,out=indices)
        ages=grid-ms[indices]
        if np.any(ages>2500):
            valid[k]=False;invalid_reason['stale_60s']=invalid_reason.get('stale_60s',0)+1;continue
        mid=midpoint[indices];spr=spread[indices]
        returns=np.diff(mid,prepend=mid[0]);tickcounts=np.diff(indices,prepend=indices[0]);tickcounts=np.clip(tickcounts,0,100000)
        # Past-only normalization from the complete observed <=t0 window.
        scale=np.sqrt(np.mean(returns**2)+1.0)
        x[k,0]=np.clip(side*returns/scale,-15,15)
        x[k,1]=np.clip((spr-np.median(spr))/max(np.median(spr),1),-5,15)
        x[k,2]=np.log1p(tickcounts)
        x[k,3]=np.clip(side*(mid-mid[0])/(scale*np.sqrt(N_SAMPLES)),-15,15)
        x[k,4]=np.clip(np.abs(returns)/scale,0,15)
    return x,valid,invalid_reason


def extract_month(m, sample_n=4096, out=None, raw_dir=RAW, cache_dir=CACHE):
    out=Path(out) if out is not None else RAW/'r9_minute_rocket/output'
    out.mkdir(parents=True,exist_ok=True)
    raw_dir=Path(raw_dir);cache_dir=Path(cache_dir)
    receipt=json.loads((cache_dir/'source_receipt.json').read_text())
    source=receipt['source_months'][m]
    raw=raw_dir/f'XAUUSD_MT5_BROKER_2026_{m}_ticks_ALL.csv.gz'
    h=hashlib.sha256()
    with raw.open('rb') as fh:
        for chunk in iter(lambda:fh.read(4*1024*1024),b''):h.update(chunk)
    if h.hexdigest()!=source['source_sha256']:raise ValueError('Coinexx source SHA mismatch')
    df=pd.read_csv(raw,usecols=['time_msc','bid','ask'],dtype={'time_msc':np.int64,'bid':np.float64,'ask':np.float64})
    ms=df.time_msc.to_numpy(); bid=np.rint(df.bid.to_numpy()*100).astype(np.int32);ask=np.rint(df.ask.to_numpy()*100).astype(np.int32)
    assert len(ms)==source['rows'] and np.all(np.diff(ms)>=0) and np.all(ask>=bid)
    assert np.max(np.abs(df.bid.to_numpy()*100-bid))<1e-6, 'price precision invalid'
    del df
    ref=pd.read_csv(cache_dir/f'candidate_closes_2026_{m}.csv.gz')
    offset=sum(receipt['source_months'][f'{m2:02}']['rows'] for m2 in range(1,int(m)))
    at=ref.entry_ordinal.to_numpy(np.int64)-offset-1
    assert np.all(at>=0) and np.all(at<len(ms))
    assert np.array_equal(ms[at],ref.entry_time_msc.to_numpy(np.int64)),'source ordinal/timestamp mismatch'
    side=ref.side.to_numpy(np.int8)
    ep=ref.entry_price_u.to_numpy(np.int32)
    assert np.array_equal(ep,np.where(side==1,ask[at],bid[at])),'source exact entry quote mismatch'
    labels,hit,terminal=first_passage(ms,bid,ask,at,side,ep)
    ix=np.unique(np.linspace(0,len(at)-1,num=min(sample_n,len(at)),dtype=int))
    seq,valid,reasons=make_sequences(ms,bid,ask,at[ix],side[ix]); sel=ix[valid]
    f=ref.iloc[sel]
    columns=['entry_ordinal','entry_time_msc','side','spread_u','session','r9_atr_u',
             'r9_disp_signed_u','r9_eff','r9_range_u','r9_turns','rearm','minute_second',
             'entry_overshoot_u','w10000_signed_mid_disp','w10000_eff','w10000_events']
    z=f[columns].to_numpy(dtype=np.float32)
    outpath=out/f'multiscale_2026_{m}.npz'
    np.savez_compressed(outpath,X=seq[valid],base=z,labels=labels[sel],
       hit_ms=hit[sel],ret=terminal[sel],ordinals=ref.entry_ordinal.to_numpy(np.int64)[sel],
       entry_times=ms[at[sel]],columns=np.array(columns))
    distribution={str(horizon):{name:int(np.sum(labels[:,j]==code)) for code,name in LABEL.items()} for j,horizon in enumerate(HORIZONS)}
    receipt={'month':m,'n_ticks':len(ms),'total_candidate_opportunities':len(at),'all_candidate_labels_by_horizon':distribution,
      'selected_chronological_uniform':len(ix),'valid_history_sequences':int(valid.sum()),'sequence_exclusions':reasons,
      'npz_sha256':hashlib.sha256(outpath.read_bytes()).hexdigest(),
      'raw_source_sha256':source['source_sha256'],
      'sample_method':'uniform sequence index determined before label observation (not label filtered)',
      'barriers':'TARGET gross +50, STOP gross -30, price cents; cost +20 price cents deducted in economics, not broker USD',
      'causality':'all features sampled at or before exact source entry ordinal; labels use only later observed quotes; quote gap >10s censored',
      'status':'shadow research, not EA fills or approval'}
    (out/f'receipt_2026_{m}.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('MONTH',m,'ticks',len(ms),'candidates',len(at),'sample_valid',int(valid.sum()),'label30',distribution['30000'],flush=True)
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--months',nargs='+',default=['01','02'])
    p.add_argument('--n',type=int,default=4096)
    p.add_argument('--raw-dir',type=Path,default=RAW)
    p.add_argument('--cache-dir',type=Path,default=CACHE)
    p.add_argument('--out',type=Path,default=RAW/'r9_minute_rocket/output')
    a=p.parse_args()
    for m in a.months:extract_month(m,a.n,a.out,a.raw_dir,a.cache_dir)

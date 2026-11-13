"""Exact-source full R9 candidate universe: all 60-second past-only features and fixed first-passage labels.
Never changes original source or previous model receipts; writes per-month derived caches.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
from extract import first_passage,LABEL
from hft import hft_features
from quant_state import state_features,COLS as STATE_COLS

REPO=Path('/mnt/data/r9_m60_expanded')
BASE_COLS=['side','spread_u','session','r9_atr_u','r9_disp_signed_u','r9_eff','r9_range_u','r9_turns','rearm','minute_second','entry_overshoot_u','w10000_signed_mid_disp','w10000_eff','w10000_events']
ALL_FEATURES=BASE_COLS+[f'hft_{i:03}' for i in range(103)]+STATE_COLS

def sha256(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()

def gather(ms,mid,spread,entries,sides,batch=768):
    """Return exact as-of sequences for each candidate; any stale grid point => unscorable.
    No quote with ordinal greater than candidate entry ordinal may be used.
    """
    n=len(entries);seq=np.zeros((n,5,120),np.float32);valid=np.ones(n,dtype=bool)
    times=ms[entries];offsets=(np.arange(120,dtype=np.int64)-119)*500
    invalid_first=invalid_stale=0
    for low in range(0,n,batch):
        high=min(n,low+batch); at=entries[low:high];side=sides[low:high];grid=times[low:high,None]+offsets
        first=(grid[:,0]<ms[0]);invalid_first+=int(first.sum())
        idx=np.searchsorted(ms,grid,side='right')-1
        idx=np.maximum(idx,0);idx=np.minimum(idx,at[:,None])
        ages=grid-ms[idx]
        stale=(ages>2500).any(axis=1)
        invalid_stale+=int((stale &~first).sum())
        ok=~(stale|first)
        valid[low:high]=ok
        if not np.any(ok):continue
        ix=idx[ok]; sid=side[ok]
        mids=mid[ix]; sp=spread[ix];r=np.diff(mids,axis=1,prepend=mids[:,:1])
        scale=np.sqrt(np.mean(r*r,axis=1)+1.)
        cnt=np.diff(ix,axis=1,prepend=ix[:,:1])
        med=np.median(sp,axis=1)
        out=seq[low:high][ok]
        # indexing through slice-of-boolean yields a copy; write back explicitly.
        out[:,0,:]=np.clip(sid[:,None]*r/scale[:,None],-15,15)
        out[:,1,:]=np.clip((sp-med[:,None])/np.maximum(med[:,None],1.),-5,15)
        out[:,2,:]=np.log1p(np.clip(cnt,0,100000))
        out[:,3,:]=np.clip(sid[:,None]*(mids-mids[:,:1])/(scale[:,None]*np.sqrt(120.)),-15,15)
        out[:,4,:]=np.clip(np.abs(r)/scale[:,None],0,15)
        seq[np.arange(low,high)[ok]]=out
    return seq,valid,{'warmup':invalid_first,'stale_60s':invalid_stale}

def month(month,raw_dir,cache_dir,out_dir):
 raw=raw_dir/f'XAUUSD_MT5_BROKER_2026_{month}_ticks_ALL.csv.gz'
 meta=json.loads((cache_dir/'source_receipt.json').read_text())['source_months'][month]
 digest=sha256(raw)
 if digest!=meta['source_sha256']:raise ValueError('sha256 original raw differs')
 df=pd.read_csv(raw,usecols=['time_msc','bid','ask'],dtype={'time_msc':np.int64,'bid':np.float64,'ask':np.float64})
 ms=df.time_msc.to_numpy(copy=True)
 bid=np.rint(df.bid.to_numpy()*100).astype(np.int32)
 ask=np.rint(df.ask.to_numpy()*100).astype(np.int32)
 if len(ms)!=meta['rows'] or np.any(np.diff(ms)<0) or np.any(ask<bid):raise ValueError('bad source chronology/quotes')
 del df
 ref=pd.read_csv(cache_dir/f'candidate_closes_2026_{month}.csv.gz')
 receipt=json.loads((cache_dir/'source_receipt.json').read_text())
 offset=sum(receipt['source_months'][f'{m:02}']['rows'] for m in range(1,int(month)))
 ix=ref.entry_ordinal.to_numpy(np.int64)-offset-1
 sides=ref.side.to_numpy(np.int8); prices=ref.entry_price_u.to_numpy(np.int32)
 if np.any(ix<0) or np.any(ix>=len(ms)):raise ValueError('bad entry ordinal')
 if not np.array_equal(ms[ix],ref.entry_time_msc.to_numpy(np.int64)):raise ValueError('entry timestamp mismatch')
 if not np.array_equal(prices,np.where(sides==1,ask[ix],bid[ix])):raise ValueError('entry side price mismatch')
 label,hit,terminal=first_passage(ms,bid,ask,ix,sides,prices)
 midpoint=(bid.astype(np.float64)+ask.astype(np.float64))*0.5
 spreads=(ask-bid).astype(np.float64)
 seq,valid,reasons=gather(ms,midpoint,spreads,ix,sides)
 base=ref[BASE_COLS].to_numpy(np.float32)
 # Features are NULL (not zero) when 60s is invalid. These rows stay in eligibility receipt.
 data=np.full((len(ix),len(ALL_FEATURES)),np.nan,np.float32)
 data[:,:len(BASE_COLS)]=base
 if np.any(valid):
  data[valid,len(BASE_COLS):len(BASE_COLS)+103]=hft_features(seq[valid])
  data[valid,len(BASE_COLS)+103:]=state_features(seq[valid])
 output=out_dir/f'full_month_2026_{month}.npz'
 np.savez_compressed(output, features=data,valid=valid,labels=label,terminal_return=terminal,
      entry_ordinals=ref.entry_ordinal.to_numpy(np.int64),entry_times=ref.entry_time_msc.to_numpy(np.int64),
      exit_times=ref.exit_time_msc.to_numpy(np.int64),side=sides,columns=np.array(ALL_FEATURES),hit_ms=hit)
 counts={str(h):{v:int((label[:,i]==k).sum()) for k,v in LABEL.items()} for i,h in enumerate((5000,15000,30000))}
 by_class={LABEL[k]:{'full':int((label[:,1]==k).sum()),'invalid_60s':int(((label[:,1]==k)&(~valid)).sum())} for k in LABEL}
 out={'month':month,'raw_rows':len(ms),'raw_sha256':digest,'candidate_count':len(ix),'valid_60s':int(valid.sum()),
      'missing_60s':int((~valid).sum()),'missing_causes':reasons,'labels':counts,'label_missingness':by_class,
      'feature_count':len(ALL_FEATURES),'derived_sha256':sha256(output),
      'no_future':'all features <= entry ordinal; future ticks used for label only','cost':'gross +50/-30 cents; shadow fee 20 cents; no verified fills'}
 (out_dir/f'full_receipt_2026_{month}.json').write_text(json.dumps(out,indent=2)+'\n')
 print('DONE',month,'ticks',len(ms),'trades',len(ix),'valid',int(valid.sum()),'missing',reasons,'labels15',counts['15000'],flush=True)
 return out

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--raw-dir',type=Path,default=Path('/mnt/data'))
 p.add_argument('--cache-dir',type=Path,default=REPO)
 p.add_argument('--out-dir',type=Path,default=REPO/'full_derived')
 p.add_argument('--months',nargs='+',default=[f'{m:02}' for m in range(1,10)])
 a=p.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
 for m in a.months:month(m,a.raw_dir,a.cache_dir,a.out_dir)

import argparse, hashlib, json, os, tempfile, time
from pathlib import Path
import numpy as np, pandas as pd

def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def atomic_json(p,obj):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=str(p.parent),prefix=p.name+'.tmp.')
    with os.fdopen(fd,'w',encoding='utf-8') as f:
        json.dump(obj,f,indent=2,sort_keys=True,allow_nan=True); f.flush(); os.fsync(f.fileno())
    os.replace(tmp,p)

def aggregate_m5_atr(t,mid):
    bar=t//300000
    ids,idx,cnt=np.unique(bar,return_index=True,return_counts=True)
    last=idx+cnt-1
    c=mid[last]; h=np.maximum.reduceat(mid,idx); l=np.minimum.reduceat(mid,idx)
    end=((ids+1)*300).astype(np.int64)
    prev=np.r_[np.nan,c[:-1]]
    tr=np.maximum(h-l,np.maximum(np.abs(h-prev),np.abs(l-prev)))
    atr=np.full(len(tr),np.nan); e=np.nan
    for i,x in enumerate(tr):
        if not np.isfinite(x): continue
        e=x if not np.isfinite(e) else (13/14)*e+(1/14)*x
        if i>=13: atr[i]=e
    base=pd.Series(atr).rolling(50,min_periods=50).mean().to_numpy()
    ratio=atr/(base+1e-12)
    return end,atr,base,ratio

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--month',type=int,required=True)
    ap.add_argument('--raw',required=True); ap.add_argument('--events',required=True); ap.add_argument('--out-dir',required=True)
    a=ap.parse_args(); t0=time.time(); out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    m=a.month; job=f'C28_REGIME_FEATURE_M{m:02d}'; man=out/f'{job}.json'
    atomic_json(man,{'job_id':job,'status':'STARTED','month':m,'started_epoch':t0})
    ev=pd.read_pickle(a.events,compression='gzip').sort_values('time_ms').reset_index(drop=True)
    d=pd.read_csv(a.raw,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int64','bid_raw':'int64'})
    t=d.timestamp_ms_utc.to_numpy(np.int64); mid=(d.ask_raw.to_numpy(np.float64)+d.bid_raw.to_numpy(np.float64))/2000.0
    end,atr,base,ratio=aggregate_m5_atr(t,mid); del d
    active_sec=np.unique(t//1000)
    event_sec=ev.time_ms.to_numpy(np.int64)//1000
    sidx=np.searchsorted(active_sec,event_sec,side='left')-1
    source_sec=np.full(len(ev),-1,dtype=np.int64)
    sok=sidx>=0; source_sec[sok]=active_sec[sidx[sok]]
    j=np.searchsorted(end,source_sec,side='right')-1
    ok=j>=0
    recon=np.full(len(ev),np.nan); bas=np.full(len(ev),np.nan); rat=np.full(len(ev),np.nan)
    recon[ok]=atr[j[ok]]; bas[ok]=base[j[ok]]; rat[ok]=ratio[j[ok]]
    stored=ev.atr_m5.to_numpy(float)
    diff=np.abs(recon-stored); both=np.isfinite(recon)&np.isfinite(stored)
    maxdiff=float(np.nanmax(diff[both])) if both.any() else None
    p999=float(np.nanquantile(diff[both],.999)) if both.any() else None
    if both.any() and maxdiff>1e-9:
        raise RuntimeError(f'ATR equivalence failed maxdiff={maxdiff}')
    z=ev[['month','time_ms','side','rearm','s10_eff','s10_disp_al','s10_range','s10_turns','s10_ticks','s10_volimb_al','atr_m5','cont_harv_pnl','fade_harv_pnl','cont_r9_pnl','fade_r9_pnl']].copy()
    z['atr_m5_base50']=bas; z['atr_m5_ratio50']=rat
    op=out/f'{job}.pkl.gz'; tmp=Path(str(op)+'.tmp'); z.to_pickle(tmp,compression='gzip'); os.replace(tmp,op)
    final={'job_id':job,'status':'COMPLETED_LOCAL','month':m,'rows':int(len(z)),'finite_ratio':int(np.isfinite(rat).sum()),
           'atr_equivalence_max_abs_diff':maxdiff,'atr_equivalence_p999_abs_diff':p999,
           'raw_sha256':sha256(a.raw),'events_sha256':sha256(a.events),'output_sha256':sha256(op),
           'output':str(op),'elapsed_seconds':time.time()-t0,
           'feature_definition':'completed M5 Wilder ATR14 / rolling mean of current+previous49 completed M5 ATR14; event source clock = last active second strictly before event tick second, matching V2 sec_idx; completed bar lookup by end'}
    atomic_json(man,final); print(json.dumps(final,indent=2))
if __name__=='__main__': main()

"""Recover actual observed fill/first-barrier UTC milliseconds from pinned raw ticks.

No artificial fill at signal+latency; original sorted source ordinal is preserved.
Requires full original monthly source including R18 June/July UTC tail correction.
"""
from __future__ import annotations
import argparse,sys,json,hashlib,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
import r24_firstpass_engine as r

def restore(source,month):
 start=time.monotonic();mon=f'{int(month):02d}';dest=r.R24/'results'/source/mon
 p=dest/f'R24_{source}_{mon}_1000MS';f=np.load(str(p)+'_fill_source_quote_ordinal.npy',mmap_mode='r');ev=np.load(str(p)+'_first_event_source_quote_ordinal.npy',mmap_mode='r')
 t,b,a=r.raw_month(source,mon,verify=True)
 if (f>=len(t)).any() or (ev>=len(t)).any():raise ValueError('SOURCE_ORDINAL_MAPPING_DRIFT')
 fp=np.where(f>=0,t[np.maximum(f,0)],-1).astype(np.int64)
 ep=np.where(ev>=0,t[np.maximum(ev,0)],-1).astype(np.int64)
 np.save(str(p)+'_actual_fill_utc_ms.npy',fp)
 np.save(str(p)+'_first_barrier_2SIDE_utc_ms.npy',ep)
 # TIMEOUT refers to first *actually observed* quote >= specified horizon,
 # rather than assuming an artificial quote exists exactly at the horizon.
 end=np.full((len(f),3),-1,np.int64)
 eligible=np.flatnonzero(f>=0)
 for h,ms in enumerate((15000,30000,60000)):
  idx=np.searchsorted(t,fp[eligible]+ms,side='left')
  valid=idx<len(t)
  end[eligible[valid],h]=t[idx[valid]]
 np.save(str(p)+'_true_timeout_first_observed_utc_ms.npy',end)
 files=[Path(str(p)+'_actual_fill_utc_ms.npy'),Path(str(p)+'_first_barrier_2SIDE_utc_ms.npy'),Path(str(p)+'_true_timeout_first_observed_utc_ms.npy')]
 receipt={'source':source,'month':mon,'raw_sha256':r.source_pin(source,mon),'source_quote_rows':len(t),
    'actual_fill_timestamps':int(np.count_nonzero(fp>=0)),'actual_first_barrier_timestamps':int(np.count_nonzero(ep>=0)),
    'june_mt5_uses_SHA_pinned_JULY_UTC_TAIL':bool(source=='MT5_BROKER_EXPORT' and mon=='06'),
    'no_interpolation':True,'seconds':round(time.monotonic()-start,3),
    'members':{q.name:hashlib.file_digest(open(q,'rb'),'sha256').hexdigest() for q in files}}
 (dest/f'R24_{source}_{mon}_ACTUAL_BROKER_QUOTE_CLOCK_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(receipt,indent=2))
 return receipt

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',choices=r.SOURCE_NAMES,required=True);p.add_argument('--month',choices=('01','02','06','07'),required=True);a=p.parse_args();restore(a.source,a.month)

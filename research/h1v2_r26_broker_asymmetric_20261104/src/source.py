"""R26 strict source reader, all source bytes pinned, 1s quote decision candidates.
READ-ONLY original source; no R9 SYNTH input is ever passed to policy code.
"""
from __future__ import annotations
from datetime import datetime,timezone
from pathlib import Path
import hashlib
import numpy as np
import pandas as pd

ROOT=Path('/mnt/data')
PINS={
 ('DUKASCOPY_RAW','01'):'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
 ('DUKASCOPY_RAW','02'):'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d',
 ('DUKASCOPY_RAW','06'):'34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2',
 ('DUKASCOPY_RAW','07'):'e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7',
 ('MT5_BROKER_EXPORT','01'):'1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8',
 ('MT5_BROKER_EXPORT','02'):'5de772aab4d15ebf18aa48850e847c98e2bcb639064790bbed9d87a598c3bf05',
 ('MT5_BROKER_EXPORT','06'):'3033ccb257d067aecc123f3791d9dddc5c95841b9bba167ff1ca0cf1589dc2b4',
 ('MT5_BROKER_EXPORT','07'):'d9d47d40abb33935414edfb5c11f0c518d8c9cc27221da182dab0bc49b0b708d'
}

def file_for(source,month):
 return ROOT/(f'XAUUSD_DUKAS_2026_{month}_ticks.csv.gz' if source=='DUKASCOPY_RAW' else f'XAUUSD_MT5_BROKER_2026_{month}_ticks_ALL.csv.gz')

def source_month(source, month, verify_sha=True, june_halo=True):
 p=file_for(source,month)
 if verify_sha:
  with p.open('rb') as f: h=hashlib.file_digest(f,'sha256').hexdigest()
  assert h==PINS[(source,month)],('SHA_MISMATCH',source,month,h)
 if source=='DUKASCOPY_RAW':
  f=pd.read_csv(p,usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
  t=f.timestamp_ms_utc.to_numpy();b=f.bid_raw.to_numpy();a=f.ask_raw.to_numpy()
 else:
  f=pd.read_csv(p,usecols=['time_msc','bid','ask'],dtype={'time_msc':'int64','bid':'float64','ask':'float64'})
  offset=2 if month in ('01','02') else 3
  t=f.time_msc.to_numpy()-offset*3600000
  b=np.rint(f.bid.to_numpy()*1000).astype(np.int32)
  a=np.rint(f.ask.to_numpy()*1000).astype(np.int32)
 del f
 if source=='MT5_BROKER_EXPORT' and month=='06' and june_halo:
  p2=file_for(source,'07')
  if verify_sha:
   with p2.open('rb') as file: assert hashlib.file_digest(file,'sha256').hexdigest()==PINS[(source,'07')]
  tail=pd.read_csv(p2,usecols=['time_msc','bid','ask'],dtype={'time_msc':'int64','bid':'float64','ask':'float64'})
  tj=tail.time_msc.to_numpy()-3*3600000
  end=int(datetime(2026,7,1,tzinfo=timezone.utc).timestamp()*1000)
  mask=(tj>t[-1])&(tj<end+60000)
  assert mask.any() and tj[mask][0]-t[-1]>15000
  t=np.r_[t,tj[mask]]
  b=np.r_[b,np.rint(tail.bid.to_numpy()[mask]*1000).astype(np.int32)]
  a=np.r_[a,np.rint(tail.ask.to_numpy()[mask]*1000).astype(np.int32)]
 assert len(t) and np.all(t[1:]>=t[:-1]) and np.all(a>=b)
 return t,b,a

def source_candidates(t,b,a,month,source, cap=4000):
 """First source tick in *occupied* 1s bins, past 300s since >15s gap.
 Does not choose side or use future label, quota or partial source inside 1s.
 """
 ix=np.flatnonzero(np.r_[True, t[1:]//1000!=t[:-1]//1000]).astype(np.int32)
 gapstart=np.flatnonzero(np.r_[True,np.diff(t)>15000]).astype(np.int32)
 p=np.searchsorted(gapstart,ix,side='right')-1
 epoch_ms=t[ix]-t[gapstart[p]]
 sp=a[ix].astype(np.int64)-b[ix].astype(np.int64)
 start=int(datetime(2026,int(month),1,tzinfo=timezone.utc).timestamp()*1000)
 nextmon=(int(month)+1 if int(month)!=12 else 1)
 end=int(datetime(2027 if nextmon==1 else 2026,nextmon,1,tzinfo=timezone.utc).timestamp()*1000)
 # For June broker June offset / July halo, source quote beyond June end is context not decision
 accept=(epoch_ms>=300000)&(sp>=0)&(sp<=cap)&(t[ix]>=start)&(t[ix]<end)
 return ix[accept]


def sample_features(t,b,a,ids):
 """As-of-only, source-ordinal mark/cross-timescale features from BID and ASK.
 Output all numeric arrays and do not compute any subsequent prices.
 """
 now=t[ids]; bid=b[ids].astype(np.int64);ask=a[ids].astype(np.int64);mid=bid+ask;sp=ask-bid
 f={'id':ids,'t':now,'bid':bid,'ask':ask,'spread':sp}
 for ms in (500,2000,6000,15000,60000):
  x=np.searchsorted(t,now-ms,side='right')-1
  x=np.maximum(x,0)
  f[f'bid{ms}']=bid-b[x]
  f[f'ask{ms}']=ask-a[x]
  f[f'mid{ms}']=mid-(b[x].astype(np.int64)+a[x].astype(np.int64))
  f[f'past_spread{ms}']=a[x].astype(np.int64)-b[x].astype(np.int64)
  f[f'count{ms}']=ids-x
 return f

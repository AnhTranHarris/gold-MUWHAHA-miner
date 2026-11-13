"""Causal quote-only proxy extraction from source-exact Coinexx Jan-Sep 2026."""
from __future__ import annotations
import argparse,hashlib,json,sys,time
from pathlib import Path
import numpy as np,pandas as pd
from proxy_features import proxy_states,FEATURE_NAMES
ROOT=Path('/mnt/data/r9_m60_proxy_20261113')
DATA=Path('/mnt/data')
DEPS=ROOT/'deps'
RECEIPT=json.loads((DEPS/'source_receipt.json').read_text())['source_months']

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for buf in iter(lambda:f.read(4*1024*1024),b''):h.update(buf)
 return h.hexdigest()

def run(mm):
 st=time.monotonic();source=DATA/f'XAUUSD_MT5_BROKER_2026_{mm}_ticks_ALL.csv.gz'
 expected=RECEIPT[mm]
 actual=sha(source)
 if actual!=expected['source_sha256']:raise RuntimeError(f'{mm} SHA mismatch')
 df=pd.read_csv(source,usecols=['time_msc','bid','ask'],dtype={'time_msc':'int64','bid':'float64','ask':'float64'})
 ts=df.time_msc.to_numpy(np.int64,copy=True)
 bid=np.rint(df.bid.to_numpy(np.float64)*100).astype(np.int32)
 ask=np.rint(df.ask.to_numpy(np.float64)*100).astype(np.int32)
 del df
 if len(ts)!=expected['rows'] or np.any(np.diff(ts)<0) or np.any(ask<bid):raise RuntimeError('Bad chronology or bid/ask or source count')
 with np.load(DEPS/f'event_2026_{mm}.npz',allow_pickle=False) as ev:
  ordinal0=sum(RECEIPT[f'{m:02}']['rows'] for m in range(1,int(mm)))
  ix=ev['ordinal'].astype(np.int64)-ordinal0-1
  if (ix<0).any() or (ix>=len(ts)).any() or np.any(np.diff(ix)<=0):raise RuntimeError('Original ordinal validity failed')
  if not np.array_equal(ts[ix],ev['entry']):raise RuntimeError('Original source entry timestamps do not match')
  features=proxy_states(ts,bid,ask,ix)
  if features.shape!=(len(ix),len(FEATURE_NAMES)) or not np.isfinite(features).all():raise RuntimeError('feature invalid')
  out=ROOT/'derived'/f'proxy_2026_{mm}.npz'
  np.savez_compressed(out,features=features,entry=ev['entry'],ordinal=ev['ordinal'],feature_names=np.array(FEATURE_NAMES))
  result={'month':mm,'raw_rows':len(ts),'original_r9_decisions':len(ix),'source_sha256':actual,
          'proxy_sha256':sha(out),'feature_count':len(FEATURE_NAMES),
          'nonzero_marked_up':int((features[:,0]!=0).sum()),
          'nonzero_latent_pressure':int((features[:,12]!=0).sum()),
          'nonzero_spread_shock':int((features[:,22]!=0).sum()),
          'seconds':round(time.monotonic()-st,2),'status':'EXACT_ORDINAL_ASOF_SHADOW'}
  (ROOT/'derived'/f'proxy_receipt_{mm}.json').write_text(json.dumps(result,indent=2)+'\n')
  print('EXTRACTED',json.dumps(result),flush=True)
  return result

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--months',nargs='+',default=[f'{i:02}' for i in range(1,10)])
 for m in ap.parse_args().months:run(m)

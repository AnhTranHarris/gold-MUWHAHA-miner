"""Atomic/day-sharded inference; all model predictors use frozen current/past-only features.
No oracle or R9 quota is available to this action model. Each day is independent
as a write unit but its 300s feature history is from original full-month source.
"""
from __future__ import annotations
import argparse,datetime,hashlib,json,os,sys,time
from pathlib import Path
import numpy as np
from r23h24_competing_hazard import BASE,source_arrays,prefix_features,load_models,FEEDS

def score_one_day(s,mon,day,overwrite=False):
 a=source_arrays(s,mon);t=a['t']
 begin=int(datetime.datetime(2026,int(mon),day,tzinfo=datetime.timezone.utc).timestamp()*1000)
 end=begin+86400000
 lo=int(np.searchsorted(t,begin));hi=int(np.searchsorted(t,end))
 folder=BASE/'score_days'/s/mon;folder.mkdir(parents=True,exist_ok=True)
 name=f'R23H24_{s}_{mon}_{day:02d}_CAUSAL_SCORE_DAY.npz';path=folder/name
 recpath=folder/(name+'.receipt.json')
 if path.exists() and recpath.exists() and not overwrite:
  old=json.loads(recpath.read_text())
  assert old['sha256']==hashlib.file_digest(path.open('rb'),'sha256').hexdigest()
  assert old['start_row']==lo and old['end_row']==hi
  return old
 fx=prefix_features(a['x'][lo:hi],t[lo:hi]);n=hi-lo
 hazard,held,wait=load_models(mon)
 # All six broker/side/horizon inputs batched, exactly fixed side/H metadata.
 perm_side=np.array([0,0,0,1,1,1],np.float32)
 perm_stage=np.array([0,1,2,0,1,2],np.float32)
 xx=np.empty((n*6,59),np.float32)
 xx[:,:57]=np.repeat(fx,6,axis=0)
 xx[:,57]=np.tile(perm_side,n);xx[:,58]=np.tile(perm_stage,n)
 q=hazard.predict(xx,num_threads=2).reshape(n,2,3,4)
 hs=held.predict(xx,num_threads=2).reshape(n,2,3)
 ww=wait.predict(fx,num_threads=2).astype(np.float32)
 # Conditional survival (no first passage) between observation horizons.
 out=np.zeros((n,2,3,4),np.float32)
 remain=np.ones((n,2),np.float64)
 for k in range(3):
  if k:out[:,:,k,:]=out[:,:,k-1,:]
  out[:,:,k,0]+=remain*q[:,:,k,0]   # first STOP
  out[:,:,k,1]+=remain*q[:,:,k,1]   # first TARGET
  out[:,:,k,3]+=remain*q[:,:,k,3]   # first quote GAP / censor
  remain*=q[:,:,k,2]
  out[:,:,k,2]=remain               # event-free through H
 hs=np.minimum.accumulate(hs,axis=2).astype(np.float32)
 if n: assert np.max(np.abs(out.sum(axis=3)-1))<1e-4
 assert np.all(np.diff(out[:,:,:,1],axis=2)>=-1.e-5)
 assert np.all(np.diff(out[:,:,:,0],axis=2)>=-1.e-5)
 assert np.all(np.diff(hs,axis=2)<=1.e-5)
 tmp=path.with_suffix('.tmp')
 with tmp.open('wb') as f:np.savez_compressed(f,cause=out,held=hs,wait10=ww)
 os.replace(tmp,path)
 receipt={'source':s,'month':mon,'day':day,'start_row':lo,'end_row':hi,'rows':n,
   'utc_start':datetime.datetime.fromtimestamp(begin/1000,datetime.timezone.utc).isoformat(),
   'input_model_ref':str(BASE/'models'/mon/f'R23H24_{mon}_MODEL_SHA_RECEIPT.json'),
   'feature_contract':'R23H24 source prefix only; no R9 quotas, future label, news, or oracle in predictors',
   'probabilities':'conditional first STOP/TARGET/GAP and independent event-free at 15/30/60; held_H independent, WAIT10 separate',
   'sha256':hashlib.file_digest(path.open('rb'),'sha256').hexdigest(),'size':path.stat().st_size}
 recpath.write_text(json.dumps(receipt,indent=2)+'\n')
 return receipt

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',choices=FEEDS,required=True);ap.add_argument('--month',choices=('01','02','06','07'),required=True)
 ap.add_argument('--day-from',type=int,default=1);ap.add_argument('--day-to',type=int,default=1)
 args=ap.parse_args()
 maxday=(datetime.date(2026,int(args.month)+1,1)-datetime.timedelta(days=1)).day
 if args.day_from<1 or args.day_to>maxday:ap.error('day outside original month')
 for day in range(args.day_from,args.day_to+1):
  start=time.monotonic()
  r=score_one_day(args.source,args.month,day)
  print(json.dumps({'source':args.source,'month':args.month,'day':day,'rows':r['rows'],'sha':r['sha256'],'secs':round(time.monotonic()-start,3)}),flush=True)

if __name__=='__main__':main()

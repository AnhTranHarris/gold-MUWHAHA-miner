"""R23H24 additive, observed-quote minimum-horizon adverse-stop labels.
No future-informed path, fill, or hindsight membership is an INPUT feature.
Every held_H label is a future OFFLINE supervised response only.
Original R23, R24 files and R9 trading system are immutable.
"""
from __future__ import annotations
import argparse,hashlib,json,sys,time,os
from pathlib import Path
import numpy as np
from numba import njit
BASE=Path(os.environ.get('R23H24_WORKSPACE','/mnt/data/r23h24_workspace')).expanduser().resolve()
sys.path.insert(0,str(BASE/'r24_source_archive'/'source'))
import r24_firstpass_engine as upstream
H=(15000,30000,60000)
# held status: 0 adverse STOP, 1 full horizon survived, 2 right-CENSORED by gap/coverage, 3 unfilled

@njit(cache=False)
def _first_extreme(size,nodes,left,right,threshold,is_min):
 """Earliest observed ordinal violating one physical bid/ask barrier, [left,right)."""
 if right<=left:return -1
 # scan canonical ordered segment decomposition, O(log N) bound checks
 L=left+size;R=right+size
 aa=np.empty(64,np.int64);bb=np.empty(64,np.int64);na=0;nb=0
 while L<R:
  if L&1:aa[na]=L;na+=1;L+=1
  if R&1:R-=1;bb[nb]=R;nb+=1
  L//=2;R//=2
 for k in range(na+nb):
  node=aa[k] if k<na else bb[nb-1-(k-na)]
  if (is_min and nodes[node]>threshold) or ((not is_min) and nodes[node]<threshold):continue
  while node<size:
   lo=node*2
   if (is_min and nodes[lo]<=threshold) or ((not is_min) and nodes[lo]>=threshold):node=lo
   else:node=lo+1
  return int(node-size)
 return -1

@njit(cache=False)
def _labels(t,b,a,fill,gap_after,size,bmin,amax):
 n=len(fill); held=np.full((n,2,3),3,np.int8)
 stop_ix=np.full((n,2,3),-1,np.int32)
 end_ix=np.full((n,3),-1,np.int32)
 for k in range(n):
  f=fill[k]
  if f<0:continue
  start=t[f]
  for h_idx in range(3):
   deadline=start+(15000 if h_idx==0 else (30000 if h_idx==1 else 60000))
   # first observed quote at or after deadline, without fabricating a quote
   finish=np.searchsorted(t,deadline,side='left')
   past=np.searchsorted(t,deadline,side='right')
   gap=gap_after[f]
   check_end=min(gap,past)
   # Same-ms later quote ordinals are valid observed events
   for side in range(2):
    if side==0: ix=_first_extreme(size,bmin,f+1,check_end,int(b[f])-100,True)
    else: ix=_first_extreme(size,amax,f+1,check_end,int(a[f])+100,False)
    if ix>=0:
     held[k,side,h_idx]=0;stop_ix[k,side,h_idx]=ix
    elif gap<=finish or finish>=len(t) or t[finish]-deadline>15000:
     held[k,side,h_idx]=2
    else:
     held[k,side,h_idx]=1
   if finish<len(t) and gap>finish and t[finish]-deadline<=15000:end_ix[k,h_idx]=finish
 return held,stop_ix,end_ix

def run(source,mon):
 dest=BASE/'prepared/results'/source/mon
 stem=f'R24_{source}_{mon}_1000MS'
 receipt=json.loads((dest/f'R24_{source}_{mon}_SOURCE_PREPARATION_ATOMIC_receipt.json').read_text())
 paths={k:dest/(stem+'_'+k+'.npy') for k in ('fill_source_quote_ordinal','labels_2SIDE_3HORIZON','signal_utc_ms')}
 for k,p in paths.items():
  assert p.is_file(),(k,p)
 # Original SHA already verified by preserved R24; verify again before loading
 assert upstream.sha(upstream.source_file(source,mon))==receipt['source_sha256']
 t,b,a=upstream.raw_month(source,mon,verify=True)
 fill=np.load(paths['fill_source_quote_ordinal'],mmap_mode='r')
 assert len(fill)==receipt['source_eligible_asof_decisions_after_v5_300s_warmup_and_spread']
 size,_,bmin,amax,_=upstream.build_tree(b,a)
 gi=np.flatnonzero(np.diff(t)>15000)+1
 # For each fill quote ordinal f, first quote AFTER a >15s drought; if none, len(t)
 nextgapidx=np.searchsorted(gi,np.arange(len(t)),side='right')
 nextgap=np.where(nextgapidx<len(gi),gi[np.minimum(nextgapidx,len(gi)-1)],len(t)).astype(np.int32) if len(gi) else np.full(len(t),len(t),np.int32)
 held,stops,ends=_labels(t,b,a,fill,nextgap,size,bmin,amax)
 assert np.all(held[fill<0]==3)
 # label remains UNKNOWN on censored path; no imputation
 out=BASE/'held'/source/mon;out.mkdir(exist_ok=True,parents=True)
 results={}
 for name,arr in [('HELD',held),('FIRST_STOP_SOURCE_ORDINAL',stops),('FIRST_HORIZON_QUOTE_ORDINAL',ends)]:
  target=out/(stem+'_'+name+'.npy');tmp=target.with_suffix('.npy.tmp')
  with tmp.open('wb') as fh:np.save(fh,arr,allow_pickle=False)
  os.replace(tmp,target)
  results[name]={'path':str(target.relative_to(BASE)),'sha256':upstream.sha(target),'shape':list(arr.shape)}
 counts={s:{str(h//1000):{str(n):int(np.sum(held[:,i,j]==q)) for q,n in ((0,'STOP'),(1,'SURVIVED'),(2,'CENSORED'),(3,'UNFILLED'))} for j,h in enumerate(H)} for i,s in enumerate(('BUY','SELL'))}
 meta={'source':source,'month':mon,'parent_raw_SHA256':receipt['source_sha256'],'parent_prep_SHA256':upstream.sha(dest/f'R24_{source}_{mon}_SOURCE_PREPARATION_ATOMIC_receipt.json'),
  'contract':'full minimum 15/30/60s hold without observed opening-liquidation adverse 0.10; no spurious quote interpolation; FILL+100ms; economic PNL NOT COMPUTED',
  'source_quote_rows':len(t),'decision_rows':len(fill),'counts':counts,'files':results,'model_trained':False}
 f=out/(stem+'_HELD_ATOMIC_RECEIPT.json');tmp=f.with_suffix('.json.tmp');tmp.write_text(json.dumps(meta,indent=2,allow_nan=False)+'\n');os.replace(tmp,f)
 print(json.dumps({'source':source,'month':mon,'decision_rows':len(fill),'counts':counts,'receipt':str(f)},indent=2),flush=True)
 return meta

if __name__=='__main__':
 pa=argparse.ArgumentParser();pa.add_argument('source',choices=upstream.SOURCE_NAMES);pa.add_argument('month',choices=('01','02','06','07'));a=pa.parse_args();run(a.source,a.month)

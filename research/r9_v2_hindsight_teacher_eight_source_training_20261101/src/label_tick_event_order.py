#!/usr/bin/env python3
"""Hindsight label only: exact post-entry quote-event ordering.

This labeler never feeds future tick events into runtime feature columns.
Event favorable = exit-side net excursion >= +$0.10 after $0.02 fee;
event adverse = liquidation-side price moves >= $0.10 against the
liquidation-side price available at the entry quote (spread excluded).
Observe only ticks strictly AFTER entry event by source sequence index.
Classify future event ordering until recorded exit or 30s, whichever first.
This first-passage research barrier does not replace broker-native R9 SL.
"""
from pathlib import Path
import argparse,json,hashlib,time,sys
import numpy as np,pandas as pd
from numba import njit
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_exact_tick_features import load_ticks,load_trades,match_entries
ROOT=Path('/mnt/data/r9_v2_eight_source_training_20261101')
@njit(cache=True)
def annotate(t,bid,ask,idx,entryt,exitt,entrypx,exitpx,side,realnet):
 n=len(idx)
 labels=np.zeros(n,np.uint8);neutral=np.zeros(n,np.uint8);fav=np.full(n,-1,np.int64);adverse=np.full(n,-1,np.int64)
 exits_found=0
 for k in range(n):
  i=idx[k];s=side[k]
  if i<0:neutral[k]=1;continue
  liq0=bid[i] if s>0 else ask[i]
  first_fav=-1;first_adv=-1;fav_idx=-1;adv_idx=-1
  cap=entryt[k]+30000;lim=min(exitt[k],cap)
  j=i+1
  while j<len(t) and t[j]<=lim:
   px=bid[j] if s>0 else ask[j]
   # Time difference only for recorded event; tick source sequence is authoritative
   ex=(px-entrypx[k])*s-0.02
   disp=(px-liq0)*s
   if first_fav<0 and ex>=.10-1e-9:first_fav=t[j];fav_idx=j
   if first_adv<0 and disp<=-.10+1e-9:first_adv=t[j];adv_idx=j
   # Stop at the recorded exit quote price; do not use ticks after position closure
   if t[j]==exitt[k] and abs(px-exitpx[k])<.00001:
    exits_found+=1;break
   if first_fav>=0 and first_adv>=0:break
   j+=1
  fav[k]=first_fav;adverse[k]=first_adv
  if first_fav>=0 and (first_adv<0 or fav_idx<adv_idx) and realnet[k]>0 and exitt[k]-entryt[k]<=30000:
   labels[k]=1
  elif first_fav<0 and first_adv<0:
   neutral[k]=1
 return labels,neutral,fav,adverse,exits_found

def main(source,month):
 start=time.monotonic()
 tr=load_trades(source,month);t,bid,ask=load_ticks(source,month)
 entryt=tr.entry_ms.to_numpy(np.int64);exitt=tr.exit_ms.to_numpy(np.int64);side=tr.side.to_numpy(np.int8)
 entrypx=tr.entry_price.to_numpy(np.float64);exitpx=tr.exit_price.to_numpy(np.float64)
 idx=match_entries(t,bid,ask,entryt,entrypx,side)
 good,neu,fav,adv,count=annotate(t,bid,ask,idx,entryt,exitt,entrypx,exitpx,side,tr.net.to_numpy(np.float64))
 base=ROOT/'checkpoints'/f'{source}_{month}'
 for name,arr in (('ordered_good',good),('ordered_neutral',neu),('first_fav_ms',fav),('first_adverse_ms',adv)):
  np.save(str(base)+f'_{name}.npy',arr,allow_pickle=False)
 rr={'source':source,'month':month,'rows':len(good),'ordered_good':int(good.sum()),'ordered_neutral':int(neu.sum()),
     'ordered_adverse_or_failure':int(len(good)-good.sum()-neu.sum()),'exit_price_matching_seen':int(count),
     'entry_quote_matches':int((idx>=0).sum()),'elapsed_s':round(time.monotonic()-start,2),
     'label_contract':'first +0.10 executable NET before -0.10 from ENTRY liquidation quote, AND favorable real close <=30s; no future in features'}
 (ROOT/'checkpoints'/f'{source}_{month}_ordered_barrier_receipt.json').write_text(json.dumps(rr,indent=2))
 print(json.dumps(rr,indent=2),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--month',required=True);a=p.parse_args();main(a.source,a.month)

"""F401-R152: original-source Dukascopy hypothetical T1/T2/limit action replay.

The original t0 orders are immutable. The proposed T1/T2/LIMIT actions are
NEVER SUBMITTED and may not be interpreted as vetoes of existing R9 fills.
All runtime market states are the original GitHub R120 publisher at the new
hypothetical decision clock, strictly prior quotes and completed HTF bars.
Original truth is a training-only independent guardian label, never a runtime
feature. Native L1 touch is an optimistic fill proxy, not execution proof.
"""
from __future__ import annotations
import argparse,gc,hashlib,io,json,zipfile,time
from pathlib import Path
import numpy as np,pandas as pd
from numba import njit
from r120_multiclock_geometry import build_states,FEATURES
from r120_htf_bridge import make_macro_native
from r151_t1_core import action_t1_index,first_touch

ROOT=Path('/mnt/data/F401_R152_PAIRED_ACTION_20261102');ROOT.mkdir(exist_ok=True)
R32=Path('/mnt/data/F401_R32_PRE_T0_EVENTFLOW_COMPLETE_SOURCE_MODELS_MASKS_20261027.zip')
PINS={'01':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
'02':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d',
'06':'34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2',
'07':'e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7'}
CONFIG={'T1_offset_ms':15000,'T1_window_ms':1000,'T2_wait_ms':5000,'T2_window_ms':1000,
        'limit_improvement_raw':500,'limit_TTL_ms':2000,'target_raw':2000,'stop_raw':1500,
        'horizon_ms':30000,'assumed_cost_usd_per_ounce':0.20}

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for block in iter(lambda:f.read(4<<20),b''):h.update(block)
 return h.hexdigest()

def original(month):
 with zipfile.ZipFile(R32) as z:
  assert z.testzip() is None
  with np.load(io.BytesIO(z.read(f'F401_R32_PRE_T0_EVENTFLOW_20261027/R32_dukascopy_{month}_FROZEN_POLICY_EVENT_MASKS.npz'))) as a:
   return tuple(a[k].copy() for k in ('t','side','truth'))

@njit(cache=True)
def limit_replay(t,bid,ask,entry_idx,side,improvement=500,ttl=2000,target=2000,stop=1500,horizon=30000):
 n=len(entry_idx)
 fill_idx=np.full(n,-1,dtype=np.int32)
 out=np.full(n,-9,dtype=np.int8);gross=np.zeros(n,dtype=np.int32)
 for i in range(n):
  k=entry_idx[i]
  if k<0 or k>=len(t):continue
  s=side[i];ref=ask[k] if s>0 else bid[k]
  limit_px=ref-s*improvement
  f=-1
  for p in range(k+1,len(t)):
   if t[p]>t[k]+ttl:break
   if t[p]<=t[k]:continue
   if (s>0 and ask[p]<=limit_px) or (s<0 and bid[p]>=limit_px):
    f=p;break
  if f<0:continue
  fill_idx[i]=f
  entry=ask[f] if s>0 else bid[f]
  last=-1
  for p in range(f+1,len(t)):
   if t[p]>t[f]+horizon:break
   if t[p]<=t[f]:continue
   last=p
   px=bid[p] if s>0 else ask[p]
   pnl=s*(px-entry)
   if pnl>=target:
    out[i]=1;gross[i]=pnl;break
   if pnl<=-stop:
    out[i]=-1;gross[i]=pnl;break
  if out[i]==-9 and last>=0:
   out[i]=0;gross[i]=s*((bid[last] if s>0 else ask[last])-entry)
 return fill_idx,out,gross

def first_future_index(t,anchor,valid,delta,window):
 query=np.where(valid,anchor+delta,0)
 ix=np.searchsorted(t,query,side='left')
 safe=np.minimum(ix,len(t)-1)
 okay=valid&(ix<len(t))&(t[safe]<query+window)
 return np.where(okay,ix,-1).astype(np.int64)

def action_utility(cls,gross,fill=None):
 # Missing, unfilled, or unresolvable observations receive ZERO, not a fabricated win.
 u=np.where(cls!=-9,gross.astype(np.float32)/1000-CONFIG['assumed_cost_usd_per_ounce'],0.).astype(np.float32)
 if fill is not None:u=np.where(fill>=0,u,0.)
 return u

def run_month(month):
 file=Path(f'/mnt/data/XAUUSD_DUKAS_2026_{month}_ticks.csv.gz')
 digest=sha(file)
 if digest!=PINS[month]:raise ValueError(f'RAW_SOURCE_PIN_MISMATCH {month}')
 t0,side,truth=original(month)
 df=pd.read_csv(file,compression='gzip',dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32','ask_volume':'float32','bid_volume':'float32'})
 t,bid,ask,av,bv=(df[k].to_numpy(copy=True) for k in ('timestamp_ms_utc','bid_raw','ask_raw','ask_volume','bid_volume'))
 del df;gc.collect()
 if not(np.diff(t)>=0).all() or not(np.diff(t0)>=0).all() or np.any(ask<bid):raise ValueError('SOURCE_CLOCK_OR_SPREAD')
 ix1=action_t1_index(t,t0);v1=ix1>=0
 anchor=np.where(v1,t[np.maximum(ix1,0)],t0+15000)
 ix2=first_future_index(t,anchor,v1,5000,1000);v2=ix2>=0
 c1,g1,el1,ex1=first_touch(t,bid,ask,ix1,side,2000,1500,30000)
 c2,g2,el2,ex2=first_touch(t,bid,ask,ix2,side,2000,1500,30000)
 il,cl,gl=limit_replay(t,bid,ask,ix1,side)
 u1=action_utility(c1,g1);u2=action_utility(c2,g2);ul=action_utility(cl,gl,il)
 # R120 ORIGINAL SOURCE: event-as-of strictly before first quote of T1;
 # completed M1/M5/M15/H1 macro bars only; no invented candles.
 print("R152_STAGE R120_SIX_CLOCK_START",month,flush=True)
 X=build_states(t,bid,ask,av,bv,anchor,side)
 print("R152_STAGE R120_SIX_CLOCK_DONE",month,flush=True)
 print("R152_STAGE HTF_START",month,flush=True)
 H,hnames,meta=make_macro_native(t,bid,ask,anchor,side)
 print("R152_STAGE HTF_DONE",month,flush=True)
 assert X.shape==(len(t0),92) and H.shape==(len(t0),36)
 # Features contain only native prefix and published HTF states.
 # Include side/UTC in features only through original R120 side-normalized values.
 Z=np.column_stack((X,H)).astype(np.float32)
 assert np.isfinite(Z).all()
 Z[~v1]=0
 fn=ROOT/f'R152_DK_{month}_FEATURES_AND_ACTIONS.npz'
 print("R152_STAGE SAVE_START",month,flush=True)
 np.savez(fn,X=Z,t0=t0,side=side,truth=truth,t1=np.where(v1,anchor,-1),
  t2=np.where(v2,t[np.maximum(ix2,0)],-1),t1_valid=v1,t2_valid=v2,
  t1_cls=c1,t2_cls=c2,limit_cls=cl,limit_filled=il>=0,
  t1_gross=g1,t2_gross=g2,limit_gross=gl,
  U_T1=u1,U_T2=u2,U_LIMIT=ul)
 receipt={'broker':'dukascopy','month':month,'n_original':len(t0),'n_native_quotes':len(t),
  'raw_pin':digest,'event_classes':{str(c):int((truth==c).sum()) for c in (0,1,2)},
  'T1_valid':int(v1.sum()),'T2_valid':int(v2.sum()),'LIMIT_touch':int((il>=0).sum()),
  'action_mean_USD_per_original_intent':{n:float(u.mean()) for n,u in [('T1',u1),('T2',u2),('LIMIT',ul)]},
  'feature_shape':list(Z.shape),'macro_metadata':meta,'output_sha256':sha(fn),
  'original_t0_order_immutable':True,'all_actions_hypothetical_unsubmitted':True,
  'L1_touch_not_broker_fill':True,'no_R9_quota_claim':True}
 (ROOT/f'R152_DK_{month}_SOURCE_RECEIPT.json').write_text(json.dumps(receipt,indent=2))
 print(json.dumps({k:v for k,v in receipt.items() if k!='macro_metadata'}),flush=True)
 del X,H,Z,t,bid,ask,av,bv,ix1,ix2;gc.collect()
 return receipt

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--month',required=True,choices=['01','02','06','07']);args=p.parse_args()
 run_month(args.month)
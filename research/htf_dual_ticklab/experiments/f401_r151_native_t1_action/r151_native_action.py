"""F401-R151 source-native T1 *hypothetical unsubmitted* action research.

This module never changes or cancels an original t0 signal, never claims an
actual R9 pre-OrderSend intent, and never labels original t0+30s outcomes as
T1 economic results. T1 is the first native quote in [t0+15s,t0+16s).
All R120 market features are strictly pre-T1, all HTF bars fully closed.
L1 touch is a hypothetical optimistic fill proxy, NOT queue/fill proof.
"""
from __future__ import annotations
import argparse,hashlib,io,json,os,sys,zipfile,gc
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit
from r120_multiclock_geometry import build_states, FEATURES
from r120_htf_bridge import make_macro_native

ROOT=Path('/mnt/data/F401_R151_NATIVE_T1_ACTION_20261101')
R32=Path('/mnt/data/F401_R32_PRE_T0_EVENTFLOW_COMPLETE_SOURCE_MODELS_MASKS_20261027.zip')
REGISTRY={
 ('dukascopy','01'):('XAUUSD_DUKAS_2026_01_ticks.csv.gz','d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',0),
 ('dukascopy','02'):('XAUUSD_DUKAS_2026_02_ticks.csv.gz','ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d',0),
 ('dukascopy','06'):('XAUUSD_DUKAS_2026_06_ticks.csv.gz','34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2',0),
 ('dukascopy','07'):('XAUUSD_DUKAS_2026_07_ticks.csv.gz','e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7',0),
 ('coinexx','01'):('XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz','1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8',7200000),
 ('coinexx','02'):('XAUUSD_MT5_BROKER_2026_02_ticks_ALL.csv.gz','5de772aab4d15ebf18aa48850e847c98e2bcb639064790bbed9d87a598c3bf05',7200000),
 ('coinexx','06'):('XAUUSD_MT5_BROKER_2026_06_ticks_ALL.csv.gz','3033ccb257d067aecc123f3791d9dddc5c95841b9bba167ff1ca0cf1589dc2b4',10800000),
 ('coinexx','07'):('XAUUSD_MT5_BROKER_2026_07_ticks_ALL.csv.gz','d9d47d40abb33935414edfb5c11f0c518d8c9cc27221da182dab0bc49b0b708d',10800000),
}
SELECT_MICRO=[0,1,2,3,4,5,7,8,10,11,13,14,15,16,18,19,21,22,25,26,27,29,30,33,36,37,38,40,41,44,47,48,49,51,52,55,58,59,60,62,63,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91]
SELECT_HTF=[0,1,2,3,4,5,8,9,10,11,12,13,14,17,18,19,20,21,22,23,26,27,28,29,30,31,32,35]
FEATURE_NAMES=[FEATURES[i] for i in SELECT_MICRO]+[f'HTF_{i}' for i in SELECT_HTF]+['T1_delay_ms','pre_T1_spread_raw','pre_T1_bid_delta','pre_T1_ask_delta']

def sha256(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for block in iter(lambda:f.read(4<<20),b''):h.update(block)
 return h.hexdigest()

def load_events(broker,month):
 with zipfile.ZipFile(R32) as z:
  with np.load(io.BytesIO(z.read(f'F401_R32_PRE_T0_EVENTFLOW_20261027/R32_{broker}_{month}_FROZEN_POLICY_EVENT_MASKS.npz'))) as x:
   return {k:x[k].copy() for k in ('t','side','truth')}

def load_ticks(broker,month):
 fn,pin,offset=REGISTRY[(broker,month)];path=Path('/mnt/data')/fn
 actual=sha256(path)
 if actual!=pin:raise ValueError(f'PIN_MISMATCH {fn}: {actual} != {pin}')
 if broker=='dukascopy':
  d=pd.read_csv(path,compression='gzip',dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32','ask_volume':'float32','bid_volume':'float32'})
  t=d.timestamp_ms_utc.to_numpy(copy=True);bid=d.bid_raw.to_numpy(copy=True);ask=d.ask_raw.to_numpy(copy=True)
  av=d.ask_volume.to_numpy(copy=True);bv=d.bid_volume.to_numpy(copy=True)
 else:
  d=pd.read_csv(path,compression='gzip',usecols=['time_msc','bid','ask'],dtype={'time_msc':'int64','bid':'float64','ask':'float64'})
  t=d.time_msc.to_numpy(copy=True)-offset
  bid=np.rint(d.bid.to_numpy(copy=True)*1000).astype(np.int32)
  ask=np.rint(d.ask.to_numpy(copy=True)*1000).astype(np.int32)
  # MT5's volume/volume_real fields are zero. Never invent actual traded volume.
  av=np.zeros(len(t),dtype=np.float32);bv=np.zeros(len(t),dtype=np.float32)
 del d;gc.collect()
 if not (np.diff(t)>=0).all():raise ValueError('UNSORTED_NATIVE_QUOTES')
 if np.any(ask<bid):raise ValueError('NEGATIVE_NATIVE_SPREAD')
 return (t,bid,ask,av,bv),actual

from r151_t1_core import first_touch, action_t1_index

def process(broker,month,features=True):
 ev=load_events(broker,month);(t,bid,ask,av,bv),digest=load_ticks(broker,month)
 t0=ev['t'];side=ev['side'];truth=ev['truth']
 assert len(t0)>0 and np.all(np.diff(t0)>=0) and np.isin(side,[-1,1]).all()
 idx=action_t1_index(t,t0)
 valid=idx>=0;safe=np.maximum(idx,0);T1=t[safe]
 # T1 quote is the *hypothetical* action price, never an already-filled R9 order.
 outcomes,gross,elapsed,exit_idx=first_touch(t,bid,ask,idx,side)
 assert np.all(outcomes[~valid]==-9)
 assert np.all((T1[valid]>=t0[valid]+15000)&(T1[valid]<t0[valid]+16000))
 assert np.all((exit_idx[valid]>=idx[valid])|(outcomes[valid]==-9))
 feature_file=None
 if features:
  # Existing R120 source, untouched. T1 source states consume only t_tick<T1.
  # Invalid events get sentinel T1=t0+15000, excluded from training.
  state_t=np.where(valid,T1,t0+15000)
  X=build_states(t,bid,ask,av,bv,state_t,side)
  H,_,meta=make_macro_native(t,bid,ask,state_t,side)
  pre=np.maximum(np.searchsorted(t,state_t,side='left')-1,0)
  pre2=np.maximum(pre-1,0)
  add=np.column_stack((T1-t0,ask[pre]-bid[pre],bid[pre]-bid[pre2],ask[pre]-ask[pre2])).astype(np.float32)
  Z=np.column_stack((X[:,SELECT_MICRO],H[:,SELECT_HTF],add)).astype(np.float32)
  assert Z.shape==(len(t0),len(FEATURE_NAMES)) and np.isfinite(Z).all()
  Z[~valid]=0
  feature_file=ROOT/f'R151_{broker}_{month}_T1_MARKET_ONLY_FEATURES.npz'
  np.savez_compressed(feature_file,X=Z,valid=valid)
  del X,H,Z;gc.collect()
 mask_file=ROOT/f'R151_{broker}_{month}_T1_ACTION_OUTCOMES.npz'
 np.savez_compressed(mask_file,t0=t0,side=side,truth=truth,t1=np.where(valid,T1,-1),valid=valid,
  action_class=outcomes,gross_raw=gross,elapsed_ms=elapsed,exit_quote_index=exit_idx)
 counts={str(c):int(np.sum(outcomes==c)) for c in [-9,-1,0,1]}
 stats={'broker':broker,'month':month,'source_sha256':digest,'n_original_events':len(t0),
        'n_native_quotes':len(t),'original_correct':int((truth==0).sum()),
        'original_opposite':int((truth==1).sum()),'original_neutral':int((truth==2).sum()),
        'T1_native_window_valid':int(valid.sum()),'T1_native_window_invalid':int((~valid).sum()),
        'action_outcome_counts':counts,'target_raw':2000,'stop_raw':1500,'horizon_ms':30000,
        'hypothetical_only':True,'t0_orders_immutable':True,'no_true_fill_claim':True,
        'feature_count':len(FEATURE_NAMES) if features else 0,
        'outcome_npz_sha256':sha256(mask_file),
        'feature_npz_sha256':sha256(feature_file) if features else None}
 (ROOT/f'R151_{broker}_{month}_RECEIPT.json').write_text(json.dumps(stats,indent=2))
 print(json.dumps(stats),flush=True)
 return stats

def main():
 p=argparse.ArgumentParser();p.add_argument('--broker',choices=['dukascopy','coinexx'],required=True)
 p.add_argument('--month',choices=['01','02','06','07'],required=True)
 p.add_argument('--no-features',action='store_true');args=p.parse_args()
 process(args.broker,args.month,not args.no_features)
if __name__=='__main__':main()
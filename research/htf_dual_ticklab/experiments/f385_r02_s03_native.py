#!/usr/bin/env python3
"""F385-R02-S03 original-t0 native quote-clock + completed HTF specialist.
Research-only: original R00-054 t, side and label immutable. No replay engine replacement.
Only source-pinned Coinexx/Dukascopy Jan/Feb/June/July native quote tapes.
Ambiguous same-ms Coinexx original event quote index is unproved: conservatively
use earliest same-ms quote, set ambiguous events to NEVER VETO and report counts.
All labels are t0+30..32s midpoint signs, NOT execution after-cost PnL.
"""
from __future__ import annotations
import os
os.environ.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2')
import io, zipfile, json, pathlib, hashlib, gc, time
import numpy as np, pandas as pd
P=pathlib.Path('/mnt/data');OUT=P/'F385_R02_S03_RESEARCH_ONLY';OUT.mkdir(exist_ok=True)
Z=zipfile.ZipFile(P/'F383_R01_R02_EIGHTCELL_FOURMONTH_UNAPPROVED_RESEARCH_COMPLETE_20261024.zip')
PINS={
'coinexx':{'01':'1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8','02':'5de772aab4d15ebf18aa48850e847c98e2bcb639064790bbed9d87a598c3bf05','06':'3033ccb257d067aecc123f3791d9dddc5c95841b9bba167ff1ca0cf1589dc2b4','07':'d9d47d40abb33935414edfb5c11f0c518d8c9cc27221da182dab0bc49b0b708d'},
'dukascopy':{'01':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5','02':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d','06':'34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2','07':'e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7'}}
B=('coinexx','dukascopy');M=('01','02','06','07')
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def original(b,m):
 d=np.load(io.BytesIO(Z.read(f'F383_{b}_{m}_SOURCE_EVENT_MASK_AND_THREE_SCORES.npz')))
 return {k:d[k].copy() for k in d.files}
def quote_input(b,m):
 path=P/(f'XAUUSD_MT5_BROKER_2026_{m}_ticks_ALL.csv.gz' if b=='coinexx' else f'XAUUSD_DUKAS_2026_{m}_ticks.csv.gz')
 digest=sha(path);assert digest==PINS[b][m],('source SHA mismatch',b,m)
 if b=='coinexx':
  d=pd.read_csv(path,usecols=['time_msc','bid','ask','flags'],dtype={'time_msc':'int64','bid':'float32','ask':'float32','flags':'uint32'})
  t=d.time_msc.to_numpy()- (120 if m in ('01','02') else 180)*60000
  bid=d.bid.to_numpy();ask=d.ask.to_numpy();extra=d['flags'].to_numpy()
 else:
  d=pd.read_csv(path,usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
  t=d.timestamp_ms_utc.to_numpy();rb=d.bid_raw.to_numpy(dtype=np.int32);ra=d.ask_raw.to_numpy(dtype=np.int32);bid=rb.astype(np.float32)/1000;ask=ra.astype(np.float32)/1000;extra=(rb,ra)
 assert np.all(np.diff(t)>=0) and np.all(ask>=bid) and np.isfinite(bid).all() and np.isfinite(ask).all()
 del d;gc.collect()
 return t,bid,ask,path.name,digest,extra

def make_features(b,m):
 y=original(b,m);ev=y['t'];side=y['side'];truth=y['truth'];n=len(ev)
 tm,bid,ask,name,digest,extra=quote_input(b,m)
 left=np.searchsorted(tm,ev,'left');right=np.searchsorted(tm,ev,'right')-1
 assert np.array_equal(tm[left],ev) and np.array_equal(tm[right],ev)
 ambiguous=right>left;ix=left # conservative earliest source index; NO veto for ambiguous
 mid=(bid+ask)*.5
 vals=[];names=[]
 def add(name,x):
  x=np.asarray(x,dtype=np.float32)
  assert x.shape==(n,) and np.all(np.isfinite(x)),(name,x.shape)
  vals.append(x);names.append(name)
 add('side',side);add('utc_hour_sin',np.sin(2*np.pi*(ev%86400000)/86400000));add('utc_hour_cos',np.cos(2*np.pi*(ev%86400000)/86400000))
 spread=ask[ix]-bid[ix];add('spread',spread);add('native_gap_prev_ms',np.maximum(0,ev-tm[np.maximum(ix-1,0)]))
 db=np.empty(len(tm),np.float32);da=np.empty(len(tm),np.float32)
 db[0]=0;da[0]=0;np.subtract(bid[1:],bid[:-1],out=db[1:]);np.subtract(ask[1:],ask[:-1],out=da[1:])
 if b=='coinexx':
  flags=extra;cb=(flags&2)!=0;ca=(flags&4)!=0;bu=db>.001;bd=db<-.001;au=da>.001;ad=da<-.001
 else:
  rb,ra=extra;dbr=np.r_[0,np.diff(rb)];dar=np.r_[0,np.diff(ra)]
  cb=dbr!=0;ca=dar!=0;bu=dbr>0;bd=dbr<0;au=dar>0;ad=dar<0
 marks={'bid_only':cb&~ca,'ask_only':ca&~cb,'both':cb&ca,'bid_up':bu,'bid_down':bd,'ask_up':au,'ask_down':ad}
 # Native quote-time conditional marked renewal: no sampled-event-gap substitution.
 window_left={w:np.searchsorted(tm,ev-w,'left') for w in (1000,5000,15000,30000,60000)}
 for k in (1,2,8,32,64,256):
  lag=np.maximum(ix-k,0)
  add(f'quote_elapsed_q{k}_ms',ev-tm[lag]);add(f'quote_mid_delta_q{k}_side',(mid[ix]-mid[lag])*side)
 for k,mark in marks.items():
  # last source-native mark as of the actual event quote (never a future row).
  last=np.maximum.accumulate(np.where(mark,np.arange(len(tm),dtype=np.int32),-1))
  prev=last[ix];valid=prev>=0
  add(f'age_last_{k}_ms',np.where(valid,ev-tm[np.maximum(prev,0)],600000))
  cs=np.empty(len(mark)+1,dtype=np.int32);cs[0]=0;np.cumsum(mark.astype(np.int32),out=cs[1:])
  for w in (1000,5000,30000,60000):
   l=window_left[w]
   count=cs[ix+1]-cs[l]
   add(f'{k}_count_{w}ms',count)
   if w==1000:add(f'{k}_rate_per_ms',count/np.maximum(ev-tm[l],1))
  del cs,last
 # Cross-scale quote intensity regime transition and signed quote hazard.
 for w in (1000,5000,15000,30000,60000):
  l=window_left[w];count=(ix-l+1).astype(np.float32)
  add(f'all_quotes_count_{w}ms',count)
  add(f'all_quotes_rate_{w}ms',count/np.maximum(ev-tm[l],1))
  add(f'mid_move_{w}ms_side',(mid[ix]-mid[l])*side)
  add(f'spread_change_{w}ms',(ask[ix]-bid[ix])-(ask[l]-bid[l]))
  if w in (5000,60000):
   add(f'mid_vol_proxy_{w}ms',np.abs(mid[ix]-mid[l])/np.sqrt(np.maximum(count,1)))
 # Causal published completed M1/M5/M15/H1 OHLC/structure. Do NOT use partial current bar extremes.
 for tf in (60000,300000,900000,3600000):
  slot=tm//tf;start=np.r_[0,np.flatnonzero(np.diff(slot)!=0)+1];stop=np.r_[start[1:],len(tm)]
  bstart=slot[start]*tf;end=(slot[start]+1)*tf
  high=np.maximum.reduceat(mid,start);low=np.minimum.reduceat(mid,start)
  op=mid[start];close=mid[stop-1];rng=np.maximum(high-low,.001)
  # last completed bar: its close becomes visible only at or after the next quote timestamp.
  k=np.searchsorted(end,ev,'right')-1;valid=k>=3;kk=np.maximum(k,3)
  h0=high[kk];l0=low[kk];c0=close[kk];o0=op[kk];r0=rng[kk]
  prefix=np.r_[0.,np.cumsum(rng,dtype=np.float64)];left8=np.maximum(0,kk-7)
  avg8=(prefix[kk+1]-prefix[left8])/np.maximum(kk-left8+1,1)
  p4hi=np.maximum.reduce([high[kk],high[kk-1],high[kk-2],high[kk-3]])
  p4lo=np.minimum.reduce([low[kk],low[kk-1],low[kk-2],low[kk-3]])
  add(f'htf{tf}_completed_range',np.where(valid,r0,0))
  add(f'htf{tf}_range_to_trailing8',np.where(valid,r0/np.maximum(avg8,.001),0))
  add(f'htf{tf}_last_body_side',np.where(valid,(c0-o0)*side,0))
  add(f'htf{tf}_last_close_delta_side',np.where(valid,(c0-close[kk-1])*side,0))
  add(f'htf{tf}_favorable_barrier_distance',np.where(valid,np.where(side>0,h0-mid[ix],mid[ix]-l0),0))
  add(f'htf{tf}_adverse_barrier_distance',np.where(valid,np.where(side>0,mid[ix]-l0,h0-mid[ix]),0))
  add(f'htf{tf}_4bar_favorable_barrier',np.where(valid,np.where(side>0,p4hi-mid[ix],mid[ix]-p4lo),0))
  add(f'htf{tf}_4bar_adverse_barrier',np.where(valid,np.where(side>0,mid[ix]-p4lo,p4hi-mid[ix]),0))
  # Published sweep-and-reclaim: bar k exceeds k-1 extreme but closes back within it.
  swup=(h0>high[kk-1])&(c0<high[kk-1]);swdown=(l0<low[kk-1])&(c0>low[kk-1])
  add(f'htf{tf}_last_sweep_favorable',np.where(valid,np.where(side>0,swup,swdown),0))
  add(f'htf{tf}_last_sweep_adverse',np.where(valid,np.where(side>0,swdown,swup),0))
  # Completed 3-bar swing pivot at k-1 becomes confirmed only when bar k has closed.
  swinghi=(high[kk-1]>high[kk-2])&(high[kk-1]>high[kk]);swinglo=(low[kk-1]<low[kk-2])&(low[kk-1]<low[kk])
  add(f'htf{tf}_confirmed_swing_favorable',np.where(valid,np.where(side>0,swinghi,swinglo),0))
  add(f'htf{tf}_confirmed_swing_adverse',np.where(valid,np.where(side>0,swinglo,swinghi),0))
  add(f'htf{tf}_completed_bar_age_ms',np.where(valid,ev-end[kk],0))
  add(f'htf{tf}_last4_range',np.where(valid,p4hi-p4lo,0))
  del slot,start,stop,bstart,end,high,low,op,close,rng,k,kk,valid,h0,l0,c0,o0,r0,prefix,left8,avg8,p4hi,p4lo,swup,swdown,swinghi,swinglo;gc.collect()
 x=np.column_stack(vals).astype(np.float32,copy=False)
 assert x.shape[0]==n and np.isfinite(x).all()
 np.save(OUT/f'F385_S03_{b}_{m}_T0_FEATURES.npy',x)
 np.savez_compressed(OUT/f'F385_S03_{b}_{m}_SOURCE_EVENT_IDENTITY.npz',original_index=y['original_index'],t=ev,side=side,truth=truth,ambiguous_same_ms=ambiguous)
 receipt={'broker':b,'month':m,'raw_filename':name,'raw_sha256':digest,'native_rows':len(tm),'original_events':n,'original_correct':int((truth==0).sum()),'original_opposite':int((truth==1).sum()),'original_neutral':int((truth==2).sum()),'exact_event_time_match':True,'same_ms_ambiguous_no_veto':int(ambiguous.sum()),'feature_dimensions':x.shape[1],'feature_sha256':sha(OUT/f'F385_S03_{b}_{m}_T0_FEATURES.npy'),'identity_sha256':sha(OUT/f'F385_S03_{b}_{m}_SOURCE_EVENT_IDENTITY.npz'),'source_quote_index_policy':'first same-ms index, ambiguous events NEVER VETO; original quote index not silently assumed','mark_provenance':('actual Coinexx native MqlTick BID/ASK flags' if b=='coinexx' else 'exact Dukascopy raw integer bid/ask quote revisions; no MqlTick flags'),'htf_publication':'only last bar with end<=event t; past-confirmed 3-bar swing; no incomplete current bar extreme'}
 print('FEATURED',b,m,receipt['native_rows'],receipt['original_events'],x.shape[1],receipt['same_ms_ambiguous_no_veto'],flush=True)
 del y,tm,bid,ask,mid,db,da,cb,ca,marks,vals,x,extra;gc.collect()
 return receipt,names

def features_main():
 allr={};name0=None
 for b in B:
  for m in M:
   r,names=make_features(b,m)
   if name0 is None:name0=names
   else:assert name0==names
   allr[f'{b}_{m}']=r
 (OUT/'F385_S03_FEATURE_PROVENANCE.json').write_text(json.dumps({'features':name0,'cells':allr,'core_engine_sha':'ca4b58aec597174b6f6d18ab2f36cba6836e4f4c','parent_F383_zip_sha':'f0658a38685c4c2326e98ca8bfb4a3947ed65ffdfa68d5946afd455b0b25ddf0'},indent=2))
 print('FEATURES COMPLETE',len(name0),flush=True)
if __name__=='__main__':features_main()

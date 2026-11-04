"""Exact as-of quote-ordinal microstructure path features (no tick interpolation)."""
from __future__ import annotations
import numpy as np
from numba import njit

PATH_NAMES=(
 'bid_only_fraction_64','ask_only_fraction_64','joint_fraction_64','opposing_fraction_64',
 'bid_uptick_fraction_64','ask_uptick_fraction_64','bid_flip_fraction_64','ask_flip_fraction_64',
 'bid_signed_move_64','ask_signed_move_64','relative_bid_ask_lead_64',
 'same_ms_revision_fraction_64','quote_age_span_ms_64','last_ordinal_gap_ms',
 'max_ordinal_gap_ms_64','quote_event_rate_per_s_64',
)

@njit(cache=False)
def _features(t,b,a,signal):
 n=len(signal); out=np.zeros((n,16),np.float32)
 for i in range(n):
  s=signal[i];k=64 if s>=64 else s
  if k==0:continue
  first=s-k
  bidonly=0;askonly=0;both=0;opposing=0;bu=0;au=0;bf=0;af=0;same=0;maxdt=0
  lastbs=0;lastas=0
  for q in range(first+1,s+1):
   db=int(b[q])-int(b[q-1]);da=int(a[q])-int(a[q-1]);dt=int(t[q])-int(t[q-1])
   if db!=0 and da==0:bidonly+=1
   if da!=0 and db==0:askonly+=1
   if db!=0 and da!=0:both+=1
   if (db>0 and da<0) or (db<0 and da>0):opposing+=1
   if db>0:bu+=1
   if da>0:au+=1
   bs=1 if db>0 else (-1 if db<0 else 0)
   az=1 if da>0 else (-1 if da<0 else 0)
   if bs!=0:
    if lastbs!=0 and bs!=lastbs:bf+=1
    lastbs=bs
   if az!=0:
    if lastas!=0 and az!=lastas:af+=1
    lastas=az
   if dt==0:same+=1
   if dt>maxdt:maxdt=dt
  span=max(int(t[s])-int(t[first]),1)
  den=float(k)
  out[i,0]=bidonly/den;out[i,1]=askonly/den;out[i,2]=both/den
  out[i,3]=opposing/den;out[i,4]=bu/den;out[i,5]=au/den
  out[i,6]=bf/den;out[i,7]=af/den
  out[i,8]=(int(b[s])-int(b[first]))/(100.0+abs(int(b[s])-int(b[first])))
  out[i,9]=(int(a[s])-int(a[first]))/(100.0+abs(int(a[s])-int(a[first])))
  out[i,10]=(bidonly-askonly)/den
  out[i,11]=same/den;out[i,12]=min(span,300000)
  out[i,13]=min(int(t[s])-int(t[s-1]),300000)
  out[i,14]=min(maxdt,300000);out[i,15]=k*1000.0/span
 return out

def quote_path_features(t,b,a,signal_ordinals):
 tt=np.asarray(t,dtype=np.int64);bb=np.asarray(b,dtype=np.int32);aa=np.asarray(a,dtype=np.int32)
 ix=np.asarray(signal_ordinals,dtype=np.int32)
 if not len(tt) or not(len(tt)==len(bb)==len(aa)) or np.any(np.diff(tt)<0) or np.any(aa<bb):
  raise ValueError('NONMONOTONIC_OR_INVALID_ORIGINAL_QUOTE_SOURCE')
 if np.any(ix<0) or np.any(ix>=len(tt)):raise ValueError('SIGNAL_SOURCE_ORDINAL_OUT_OF_RANGE')
 return _features(tt,bb,aa,ix)

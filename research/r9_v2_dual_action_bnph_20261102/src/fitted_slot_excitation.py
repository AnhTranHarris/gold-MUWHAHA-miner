"""Fitted nonnegative six-mark 250 ms quote-slot excitation model.

Discrete-time Hawkes approximation, not a continuous-time point-process MLE.
Each current slot's event counts are predicted from strictly prior slot multi-tau
decayed event states plus session-specific baselines. Excitation is nonnegative
and scaled to branching spectral radius <= 0.95.
"""
from __future__ import annotations
import datetime as dt, math
from zoneinfo import ZoneInfo
import numpy as np
from numba import njit
MODEL_VERSION='r9_v2_fitted_slot_excitation_v1'
TAUS_MS=np.asarray((250.,1000.,5000.,15000.,45000.),np.float64)
MARKS=('BU','BD','AU','AD','SW','SN')
SESSIONS=('rollover','overlap','london','new_york','tokyo','sydney','off')
SLOT_MS=250

@njit(cache=True)
def _states(slot_start,counts,taus):
 n=len(slot_start);p=len(taus)*6;X=np.zeros((n,p),np.float32);state=np.zeros((len(taus),6),np.float64)
 for r in range(n):
  if r:
   delta=slot_start[r]-slot_start[r-1]
   for z in range(len(taus)):
    d=math.exp(-delta/taus[z])
    for m in range(6):state[z,m]=(state[z,m]+counts[r-1,m])*d
  c=0
  for z in range(len(taus)):
   for m in range(6):X[r,c]=state[z,m];c+=1
 return X

def _local_minute(slot_start,zone):
 """Vectorized UTC->local minute mapping with DST-aware IANA time zones."""
 minute_id=np.asarray(slot_start,np.int64)//60000
 uniq,inv=np.unique(minute_id,return_inverse=True)
 z=ZoneInfo(zone);mapped=np.empty(len(uniq),np.int16)
 for i,m in enumerate(uniq):
  utc=dt.datetime.fromtimestamp(int(m)*60,dt.timezone.utc)
  local=utc.astimezone(z);mapped[i]=local.hour*60+local.minute
 return mapped[inv]

def session_index_utc(slot_start):
 """Map quote slots to the original local-session contract for any month."""
 sm=_local_minute(slot_start,'Australia/Sydney');tm=_local_minute(slot_start,'Asia/Tokyo')
 lm=_local_minute(slot_start,'Europe/London');nm=_local_minute(slot_start,'America/New_York')
 out=np.full(len(sm),6,np.int8)
 sydney=(sm>=8*60)&(sm<17*60);tokyo=(tm>=8*60)&(tm<17*60)
 london=(lm>=8*60)&(lm<16*60+30);ny=(nm>=8*60)&(nm<17*60)
 overlap=london&ny;rollover=(nm>=16*60+55)&(nm<17*60+15)
 out[sydney]=5;out[tokyo]=4;out[ny]=3;out[london]=2;out[overlap]=1;out[rollover]=0
 return out

# Compatibility alias for older January-only research scripts. The implementation
# is now DST-aware and portable; no January-specific UTC offsets remain.
session_index_january_utc=session_index_utc

def slot_dataset(t,bid,ask,day):
 d=dt.datetime.strptime(day,'%Y-%m-%d').replace(tzinfo=dt.timezone.utc);lo=int(d.timestamp()*1000);hi=lo+86400000
 a=int(np.searchsorted(t,lo,'left'));b=int(np.searchsorted(t,hi,'left'))
 if b-a<10:raise ValueError('insufficient day ticks')
 tt=t[a:b];bb=bid[a:b];aa=ask[a:b];slot=(tt//SLOT_MS)*SLOT_MS;uniq,inv=np.unique(slot,return_inverse=True);n=len(uniq);counts=np.zeros((n,6),np.float32)
 db=np.zeros(len(tt));da=np.zeros(len(tt));ds=np.zeros(len(tt));db[1:]=bb[1:]-bb[:-1];da[1:]=aa[1:]-aa[:-1];spr=aa-bb;ds[1:]=spr[1:]-spr[:-1]
 for m,v in enumerate((db,-db,da,-da,ds,-ds)):counts[:,m]=np.bincount(inv,weights=(v>1e-10).astype(np.float32),minlength=n)
 Xstate=_states(uniq,counts,TAUS_MS);sess=session_index_utc(uniq);return uniq,counts,Xstate,sess

def design_matrix(Xstate,sess,scales=None):
 Xstate=np.asarray(Xstate,np.float64);sess=np.asarray(sess,np.int64)
 if scales is None:scales=np.maximum(1e-6,np.sqrt(np.mean(Xstate*Xstate,axis=0)))
 z=Xstate/scales;one=np.zeros((len(z),len(SESSIONS)),np.float64);one[np.arange(len(z)),sess]=1.
 return np.column_stack((z,one)),np.asarray(scales,np.float64)

def fit_nonnegative_ridge(X,Y,ridge=25.,iterations=20000,tol=1e-10):
 X=np.asarray(X,np.float64);Y=np.asarray(Y,np.float64);G=X.T@X;H=X.T@Y;reg=np.eye(G.shape[0])*float(ridge);reg[-len(SESSIONS):,-len(SESSIONS):]=0.;G=G+reg
 step=1./(float(np.linalg.eigvalsh(G).max())+1e-12);C=np.maximum(0.,np.linalg.solve(G+np.eye(G.shape[0])*1e-8,H))
 for i in range(iterations):
  Cn=np.maximum(0.,C-step*(G@C-H))
  if i%100==0 and float(np.max(np.abs(Cn-C)))<tol:C=Cn;break
  C=Cn
 return C

def branching_matrix(coef,scales):
 beta=np.asarray(coef[:30],float)/np.asarray(scales,float)[:,None];B=np.zeros((6,6),float);c=0
 for tau in TAUS_MS:
  persistence=1.-math.exp(-SLOT_MS/tau)
  for src in range(6):
   for target in range(6):B[target,src]+=beta[c,target]/max(persistence,1e-9)
   c+=1
 return B

def stabilize(coef,scales,max_radius=.95):
 C=np.asarray(coef,float).copy();B=branching_matrix(C,scales);rho=float(max(abs(np.linalg.eigvals(B))));scale=1. if rho<=max_radius else max_radius/rho
 C[:30]*=scale;B2=branching_matrix(C,scales);rho2=float(max(abs(np.linalg.eigvals(B2))));return C,rho,rho2,scale,B2

def predict(X,coef):return np.maximum(1e-9,np.asarray(X,float)@np.asarray(coef,float))

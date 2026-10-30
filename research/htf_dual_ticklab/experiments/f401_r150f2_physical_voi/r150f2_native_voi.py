"""F401-R150F2 — strictly causal new-quote active observation / L1 passage study.

NO order submissions; L1 bid/ask marketable-entry quote *proxy*, not actual fills.
NO FILTER08 teacher labels or scores as model inputs or physical outcomes.
Original R148B action remains immutable. Only a NEVER_SUBMITTED new-intent concept.
All physical outcome clocks restart from the chosen actual observation quote.
"""
from __future__ import annotations
import os, sys, json, gc, pathlib, hashlib, time
os.environ['OMP_NUM_THREADS']='2';os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from numba import njit
from importlib.util import spec_from_file_location,module_from_spec

ROOT=pathlib.Path('/mnt/data'); OUT=ROOT/'R150F2';DELAYS=np.array([0,100,250,500],np.int64)
HORIZON_MS=30000;BARRIER_RAW=3000;TARGET_GRACE_MS=1000;COST_USD=.20

def importer():
 p=ROOT/'R149/research/r149_causal_latent.py';s=spec_from_file_location('r149_original_source_loader',p);m=module_from_spec(s);s.loader.exec_module(m);return m

@njit(cache=True)
def causal_quote_features(t,bid,ask,idx,side):
 """All inputs are <= latest already-observed quote at idx; not future/outcome."""
 x=np.zeros(24,dtype=np.float32)
 if idx<33:return x
 cur=(bid[idx]+ask[idx])/2.;spread=ask[idx]-bid[idx]
 x[0]=side; x[1]=spread/1000.;x[2]=np.log1p(idx)
 for j,k in enumerate((2,8,16,32)):
  q=idx-k
  x[3+j]=side*(cur-(bid[q]+ask[q])/2.)/1000.
  x[7+j]=(spread-(ask[q]-bid[q]))/1000.
  x[11+j]=(t[idx]-t[q])/1000.
 # signed bid/ask quote revision asymmetry for last 16 non-synthetic source updates
 sb=0.;sa=0.;pc=0.;pos=0;neg=0
 for z in range(idx-15,idx+1):
  db=bid[z]-bid[z-1];da=ask[z]-ask[z-1];sb+=db;sa+=da
  dmid=(db+da)*.5*side;pc+=abs(dmid)
  if dmid>0:pos+=1
  if dmid<0:neg+=1
 x[15]=side*sb/1000.;x[16]=side*sa/1000.
 x[17]=side*(sb+sa)/(.001+pc)
 x[18]=(pos-neg)/16.;x[19]=pos/16.;x[20]=neg/16.
 x[21]=(t[idx]-t[idx-1])/1000.
 h=(t[idx]%86400000)/86400000.*2.*np.pi
 x[22]=np.sin(h);x[23]=np.cos(h)
 return x

@njit(cache=True)
def new_action_outcome(t,bid,ask,idx,side,barrier_raw=BARRIER_RAW,horizon_ms=HORIZON_MS):
 """L1 visible bid/ask mark, only ticks AFTER source action quote, first hit.
 label: 1 favorable, 0 adverse, 2 right-censored. PnL L1 proxy not filled trade.
 """
 entry=ask[idx] if side==1 else bid[idx]
 end=t[idx]+horizon_ms
 last=idx
 for j in range(idx+1,len(t)):
  if t[j]>end:break
  if t[j]<=t[idx]:continue  # same-ms future rows excluded
  last=j
  close=bid[j] if side==1 else ask[j]
  m=side*(close-entry)
  if m>=barrier_raw:return 1,j, (m/1000.-COST_USD)
  if m<=-barrier_raw:return 0,j,(m/1000.-COST_USD)
 if last==idx:return 2,last,-COST_USD
 close=bid[last] if side==1 else ask[last]
 return 2,last,side*(close-entry)/1000.-COST_USD

@njit(cache=True)
def reftime(t,bid,ask,event_t,side,indices):
 n=len(event_t);d=len(DELAYS)
 x=np.zeros((n,d,24),np.float32)
 label=np.full((n,d),-1,np.int8)
 obs=np.full((n,d),-1,np.int64)
 elapsed=np.full((n,d),-1,np.int32)
 finish=np.full((n,d),-1,np.int64)
 pnl=np.full((n,d),np.nan,np.float32)
 for i in range(n):
  base=indices[i]
  if base<33 or base>=len(t):continue
  first=t[base]
  if not(event_t[i]+15000<=first<event_t[i]+16000):continue
  for k in range(d):
   target=first+DELAYS[k]
   j=base if k==0 else base+1
   while j<len(t) and t[j]<target:j+=1
   if j>=len(t) or t[j]>target+TARGET_GRACE_MS:continue
   if k>0 and t[j]<=first:continue
   obs[i,k]=t[j];elapsed[i,k]=t[j]-first
   x[i,k,:]=causal_quote_features(t,bid,ask,j,side[i])
   a,b,p=new_action_outcome(t,bid,ask,j,side[i]);label[i,k]=a;finish[i,k]=t[b];pnl[i,k]=p
 return x,label,obs,elapsed,finish,pnl

def make(b,m,n_sample=8000,seed=15062):
 mod=importer(); t,bid,ask=mod.load_ticks(b,m)
 from numpy.random import default_rng
 with np.load(ROOT/f'R150C/features/R150C_{b}_{m}_WORLD_STATE.npz',allow_pickle=False) as z:
  ev=z['t'].astype('int64');side=z['side'].astype('int8');valid=z['valid'].astype(bool);veto=z['r148_veto'].astype(bool);truth=z['truth'].astype('int8');dec=z['decision']
 # Choose from the original population where R148B vetoed + verified native quote.
 # No outcome labels (truth) or teacher scores influence the random sampling.
 idx=np.flatnonzero(valid&veto)
 rng=default_rng(seed+int(m)+(1701 if b=='dukascopy' else 0))
 chosen=np.sort(rng.choice(idx,size=min(n_sample,len(idx)),replace=False))
 nt=np.searchsorted(t,ev[chosen]+15000,side='left')
 xx,ll,oo,ee,ff,pp=reftime(t,bid,ask,ev[chosen],side[chosen],nt)
 validx=(ll[:,0]>=0)
 output=OUT/'data'/f'R150F2_{b}_{m}_NATIVE_VOI.npz'
 np.savez_compressed(output,source_ordinal=chosen,t0=ev[chosen],side=side[chosen],original_truth_for_audit_only=truth[chosen],
 original_r148_veto=veto[chosen],features=xx,physical_label=ll,observation_ms=oo,waiting_elapsed_ms=ee,exit_quote_ms=ff,
 l1_mark_to_market_net_proxy=pp,valid_decision=validx,delay_requested_ms=DELAYS)
 h=hashlib.sha256(output.read_bytes()).hexdigest()
 info=dict(broker=b,month=m,raw_sha256=mod.PINS[f'{b}_{m}'],observations=int(n_sample),valid_now=int(validx.sum()),
 present_by_delay=[int((ll[:,k]>=0).sum()) for k in range(len(DELAYS))],physical_class_by_delay=[[(int((ll[:,k]==i).sum())) for i in (1,0,2)] for k in range(len(DELAYS))],sha256=h,
 source='genuine native quote timestamps; source-linked original ordinals',barrier_usd=BARRIER_RAW/1000,horizon_ms=HORIZON_MS,
 no_filled_order_executable_proof=True,original_label_never_physical_target=True)
 (OUT/'results'/f'R150F2_{b}_{m}_RECEIPT.json').write_text(json.dumps(info,indent=2))
 print(json.dumps(info),flush=True)
 del t,bid,ask,xx,ll,oo,ee,ff,pp;gc.collect()
 return info

if __name__=='__main__':make(sys.argv[1],sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else 8000)

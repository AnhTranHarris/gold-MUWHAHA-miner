"""F401-R150F3U — additive causal Bayesian evidence-quality state.

Source inputs: only exact R150F2 first native quote as-of t0+15, 24D
real quote-prefix features, source ordinals and native observed timestamps.
No future labels, hindsight, orderbook, fabricated OHLC or true tick-stream
BOCPD is used. The change point posterior is on *SAMPLED R148B-VETO EVENTS*,
not on the full quote tape; that material limitation is explicit.
"""
from __future__ import annotations
import numpy as np
from scipy.special import gammaln, logsumexp

FEATURE_NAMES = (
 'beta_signed_quote_revision','beta_quote_imbalance_confidence',
 'beta_positive_probability','beta_posterior_std','quote_move_density',
 'short_long_direction_coherence','path_curvature_2_8_32','path_8_32_contrast',
 'absolute_32quote_return','signed_quote_path_efficiency','spread_to_path_energy',
 'spread_revision_acceleration','spread_2_32_change','quote_2_32_time_ratio',
 'quote_8_32_time_ratio','quote_event_rate_32','quote_event_rate_16',
 'quote_age_fraction','signed_bid_ask_disagreement','bid_ask_revision_strength',
 'trend_reliability_interaction','direction_quality_interaction',
 'shock_quote_spread_interaction','path_efficiency_quote_reliability',
 'sampled_event_bocpd_changepoint_1','sampled_event_bocpd_expected_run_1',
 'sampled_event_bocpd_entropy_1','sampled_event_bocpd_surprise_1',
 'sampled_event_bocpd_changepoint_2','sampled_event_bocpd_expected_run_2',
 'sampled_event_bocpd_entropy_2','sampled_event_bocpd_surprise_2',
)

def beta_quote_reliability(x):
 """Feature block 24: native quote-revision Beta posterior + physical path interactions.

 x must be 24 source columns (index 0-23). None of the features use
 event truth, teacher score, future tick, physical outcome or price after now.
 """
 x=np.asarray(x,dtype=np.float64)
 assert x.ndim==2 and x.shape[1]==24
 pos=np.clip(x[:,19]*16,0,16);neg=np.clip(x[:,20]*16,0,16)
 moves=pos+neg
 # Symmetric Jeffreys Beta prior for direction conditional on nonzero revisions.
 a=pos+.5; b=neg+.5
 pm=a/(a+b);var=a*b/((a+b)**2*(a+b+1))
 q_density=moves/16
 directional=2*pm-1
 qconf=np.maximum(0,1-2*np.sqrt(var)) * q_density
 path=x[:,[3,4,5,6]]
 sign=np.sign(path)
 coherent=(sign==np.sign(path[:,3:4])).mean(axis=1)
 curv=path[:,0]-2*path[:,1]+path[:,3]
 t2,t8,t16,t32=[np.maximum(x[:,i],0.001) for i in (11,12,13,14)]
 sp=np.maximum(0,x[:,1])
 eps=0.01
 rev=np.abs(x[:,15])+np.abs(x[:,16])
 signed_eff=x[:,17]
 z=np.column_stack([
  directional,qconf,pm,np.sqrt(var),q_density,coherent,
  curv,path[:,1]-path[:,3],np.abs(path[:,3]),signed_eff,
  sp/(np.abs(path[:,3])+eps),x[:,7]-2*x[:,8]+x[:,10],x[:,7]-x[:,10],
  t2/t32,t8/t32,32/t32,16/t16,
  np.maximum(x[:,21],0)/t32,
  np.abs(x[:,15]-x[:,16])/(rev+eps),rev,
  (coherent*directional),qconf*np.tanh(path[:,3]/1.5),
  sp/(q_density+0.05),signed_eff*qconf])
 return np.clip(np.nan_to_num(z,nan=0,posinf=0,neginf=0),-1e6,1e6).astype(np.float32)

class GaussianNIGBOCPD:
 """Real Normal-Inverse-Gamma Bayesian online changepoint recursion (one scalar).

 This is applied only to chronologically ordered *sampled source events*;
 it is NOT a claim about the full 32M native quote tick sequence.
 Hazard accounts for elapsed physical time, thus not pretending each sampled
 event is an equally spaced tick. Output uses only current/past inputs.
 """
 def __init__(self,max_run=48,base_hazard_s=600.0):
  self.max_run=max_run;self.base_hazard_s=base_hazard_s
  self.reset()
 def reset(self):
  k=self.max_run+1
  self.logprobs=np.full(k,-np.inf);self.logprobs[0]=0.
  self.mu=np.zeros(k);self.kk=np.ones(k)*.25
  self.alpha=np.ones(k)*2.5;self.beta=np.ones(k)*2.5
  self.last_t=None
 def update(self,v,t):
  if self.last_t is not None and t<self.last_t:raise ValueError('nonmonotonic quote timestamp')
  dt=0 if self.last_t is None else float(t-self.last_t)/1000
  h=np.clip(1-np.exp(-max(dt,0)/self.base_hazard_s),1e-5,.99999)
  prev=self.logprobs.copy();alive=np.isfinite(prev)
  df=2*self.alpha;scale2=self.beta*(self.kk+1)/(self.alpha*self.kk)
  # Student-t posterior predictive log pdf, scalar.
  pred=(gammaln((df+1)/2)-gammaln(df/2)-.5*np.log(np.pi*df*scale2)
   -.5*(df+1)*np.log1p((v-self.mu)**2/(df*scale2)))
  newlog=np.full_like(prev,-np.inf)
  newlog[0]=logsumexp(prev[alive]+pred[alive]+np.log(h))
  newlog[1:]=prev[:-1]+pred[:-1]+np.log1p(-h)
  # truncation: oldest states coalesced; stable max run is a discretization.
  newlog[-1]=np.logaddexp(newlog[-1],prev[-1]+pred[-1]+np.log1p(-h))
  newlog-=logsumexp(newlog)
  mu_old=self.mu.copy();k_old=self.kk.copy();a_old=self.alpha.copy();b_old=self.beta.copy()
  # Run length 0 means model reset BEFORE taking today's observation,
  # then posterior updated with today's observation.
  mu_prior=0.;k_prior=.25;a_prior=2.5;b_prior=2.5
  self.kk[0]=k_prior+1
  self.mu[0]=(k_prior*mu_prior+v)/self.kk[0]
  self.alpha[0]=a_prior+.5
  self.beta[0]=b_prior+ .5*k_prior/(k_prior+1)*(v-mu_prior)**2
  self.kk[1:]=k_old[:-1]+1
  self.mu[1:]=(k_old[:-1]*mu_old[:-1]+v)/self.kk[1:]
  self.alpha[1:]=a_old[:-1]+.5
  self.beta[1:]=b_old[:-1]+.5*k_old[:-1]/(k_old[:-1]+1)*(v-mu_old[:-1])**2
  self.logprobs=newlog;self.last_t=t
  p=np.exp(newlog);expected=np.dot(p,np.arange(len(p)))
  entropy=-np.dot(p,np.log(np.maximum(p,1e-300)))
  marginal=logsumexp(prev[alive]+pred[alive])
  return np.array([p[0],expected/self.max_run,entropy/np.log(len(p)), -marginal],dtype=np.float32)

def chronology_state(x,t,month_lengths,fit_scale=None):
 """Return two genuine Bayesian sampled-event posterior streams, reset each month.
 Fit center/scale from labelled-free FIT ONLY, supply scale for heldout eval.
 """
 x=np.asarray(x,dtype=np.float64)
 t=np.asarray(t,dtype=np.int64)
 assert len(t)==len(x) and sum(month_lengths)==len(t)
 scalars=np.column_stack([
   np.sign(x[:,6])*np.log1p(np.abs(x[:,6])),
   np.log1p(np.maximum(0,x[:,1]))+.15*np.log1p(np.maximum(0,x[:,21]))
 ])
 if fit_scale is None:
  med=np.median(scalars,axis=0)
  scale=np.maximum(np.subtract(*np.percentile(scalars,[75,25],axis=0)),.1)
 else:med,scale=fit_scale
 z=np.clip((scalars-med)/scale,-15,15)
 out=np.zeros((len(x),8),dtype=np.float32)
 at=0
 for n in month_lengths:
  a,b=GaussianNIGBOCPD(),GaussianNIGBOCPD()
  for i in range(at,at+n):
   out[i,:4]=a.update(float(z[i,0]),int(t[i]))
   out[i,4:]=b.update(float(z[i,1]),int(t[i]))
  at+=n
 return np.clip(out,-1e3,1e3), (med,scale)

def augmented_source_features(source_24,t,month_lengths,fit_indices=None):
 x=np.asarray(source_24,dtype=np.float32)
 base=beta_quote_reliability(x)
 if fit_indices is None:scale=None
 else:
  raw=np.column_stack([np.sign(x[:,6])*np.log1p(np.abs(x[:,6])),np.log1p(np.maximum(0,x[:,1]))+.15*np.log1p(np.maximum(0,x[:,21]))])
  rr=raw[np.asarray(fit_indices)];scale=(np.median(rr,axis=0),np.maximum(np.subtract(*np.percentile(rr,[75,25],axis=0)),.1))
 cp,stats=chronology_state(x,t,month_lengths,fit_scale=scale)
 return np.column_stack([base,cp]).astype(np.float32),stats

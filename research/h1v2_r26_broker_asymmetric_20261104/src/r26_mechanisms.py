"""R26 broker-conditioned entry hypothesis family. Research only.

All inputs are prefix-derived (at or BEFORE signal ordinal); no historical
hindsight membership, future quote, result label, quota, or calendar reference
enters choose_actions. Source-specific executable Bid/Ask, not candle close.

Each action returns side 1 BUY, -1 SELL, 0 WAIT; target = NET quoted-price
profit in raw x.001 units after fee; stop = adverse price distance measured
from opening liquidation quote; H = maximum first-quote observed exit seconds.
Each policy differs in bid/ask response geometry and WEIGHTED risk floor.
No claim that fixed/variable stops or historical in-sample research are safe.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass

NAME=(
 'C1_RIDGE_CONTINUATION_8S',
 'C2_CONVEXITY_PIVOT_16S',
 'C3_SPREAD_RECOVERY_12S',
 'C4_STRUCTURE_PULLBACK_25S',
 'C5_HETEROGENEOUS_META_12S',
 'C6_THROUGHPUT_DIAGNOSTIC_12S',
)

@dataclass(frozen=True)
class ActionSet:
 side: np.ndarray
 net_target: np.ndarray
 stop_dist: np.ndarray
 horizon_ms: np.ndarray


def choose_actions(features:dict,source:str)->ActionSet:
 """Causal-only six cycles; never consume labels/source reference.

 Rates and spread used to pick expert; source-specific geometry is
 deliberately distinct. No future fill price available to this function.
 """
 if source not in ('DUKASCOPY_RAW','MT5_BROKER_EXPORT'):
  raise ValueError('invalid source')
 n=len(features['id']);sp=np.asarray(features['spread'],np.float64)
 m05=np.asarray(features['mid500'],np.float64)/2
 m2=np.asarray(features['mid2000'],np.float64)/2
 m6=np.asarray(features['mid6000'],np.float64)/2
 m15=np.asarray(features['mid15000'],np.float64)/2
 m60=np.asarray(features['mid60000'],np.float64)/2
 b2=np.asarray(features['bid2000'],np.float64)
 a2=np.asarray(features['ask2000'],np.float64)
 s2=np.asarray(features['past_spread2000'],np.float64)
 s6=np.asarray(features['past_spread6000'],np.float64)
 rate6=np.asarray(features['count6000'],np.float64)
 rate15=np.asarray(features['count15000'],np.float64)
 spread_ratio=sp/np.maximum(s6,1)
 concord=(np.sign(b2)==np.sign(a2))&(np.sign(b2)!=0)
 positive=np.isfinite(sp)&(sp>=0)
 # Independent regimes: Dukascopy requires stronger source-observed margin to
 # compensate for much larger typical bid/ask. Not a single global cutoff.
 duka=source=='DUKASCOPY_RAW'
 scale=1.25 if duka else .62
 base=np.maximum(sp,100)
 m=np.zeros((len(NAME),n),np.int8)
 strength=np.zeros((4,n),np.float32)
 # C1: cross-timeframe IMPULSE persistence, not old R25 XSC raw sign
 # Trigger requires within-source quote participation, slope acceleration and
 # that micro convexity agrees at 0.5,2,6,15s.
 sign=np.sign(m2).astype(np.int8)
 convex=np.abs(m05)+np.abs(m2)/3
 gate=(np.abs(m2)>scale*.54*base)&(np.abs(m6)>scale*1.12*base)&(np.abs(m15)>.45*np.abs(m6))&concord
 gate&=(np.sign(m05)==sign)&(np.sign(m6)==sign)&(np.sign(m15)==sign)&(rate6>=8)&positive
 m[0]=np.where(gate,sign,0)
 strength[0]=(convex+np.abs(m6)*.2)/base
 # C2: convexity exhaustion / micro reversal, different from prior LSR snap
 # Countertrend only after observed 15s excursion AND multi-timeframe reversal;
 # path direction changes after a burst, not hindsight side.
 sign2=-np.sign(m15).astype(np.int8)
 gate2=(np.abs(m15)>scale*1.85*base)&(np.abs(m2)>.38*base)&(np.sign(m2)==sign2)&(np.sign(m05)==sign2)
 gate2&=(np.sign(m60)==np.sign(m15))&(rate15>=20)&concord&positive
 m[1]=np.where(gate2,sign2,0)
 strength[1]=(np.abs(m15)*.6+np.abs(m2)*.4)/base
 # C3: actual ASK/BID spread recovery, not presumed orderbook queue fill
 # Spread must have contracted from both prior observed snapshots; side follows
 # correlated observed mark move, NOT prior future clean-looking buys.
 sign3=np.sign(m2).astype(np.int8)
 gate3=(s2>sp*1.08)&(s6>sp*1.12)&(np.abs(m2)>scale*.32*base)&(np.abs(m6)>scale*.65*base)
 gate3&=(np.sign(m6)==sign3)&(np.sign(m05)==sign3)&concord&positive
 m[2]=np.where(gate3,sign3,0)
 strength[2]=(s2-sp+np.abs(m2))/base
 # C4: trend-pullback-after-reclaim, 15/60 directional trend while 2s pulls
 # back and last 0.5s regains trend side; SOURCE observed, not price limit fill.
 sign4=np.sign(m15).astype(np.int8)
 gate4=(np.abs(m15)>scale*1.05*base)&(np.abs(m60)>scale*2.3*base)
 gate4&=(np.sign(m60)==sign4)&(np.sign(m2)==-sign4)&(np.abs(m2)>.15*base)
 gate4&=(np.sign(m05)==sign4)&(np.abs(m05)>.06*base)&(rate6>12)&positive
 m[3]=np.where(gate4,sign4,0)
 strength[3]=(np.abs(m15)+np.abs(m60)*.25)/base
 # C5: mixture router, density gate and best causal confidence (not quota).
 # Specialist with maximum as-of source-normalized geometric strength,
 # fails closed to WAIT if no eligible expert; does not use future correctness.
 scores=np.where(m[:4]!=0,strength,-1.0)
 choose=np.argmax(scores,axis=0)
 best=scores[choose,np.arange(n)]
 k=choose
 m[4]=np.where(best>=.7,m[k,np.arange(n)],0)
 # C6: independent high-volume diagnostic, no oracle outcome: sign3s voting.
 # A positive count cannot be interpreted as a correct trade result.
 sign6=np.sign(m2+.35*m6).astype(np.int8)
 m[5]=np.where((np.abs(m2)>.12*base)&(np.abs(m6)>.18*base)&(rate6>=3)&positive,sign6,0)

 # Quote barrier geometry: positive NET TP over execution bid/ask after fee;
 # stop is *additional* adverse raw movement from opening liquidation quote.
 # Respect economic reality: Dukas target is not smaller than its spread tax,
 # but this can reduce win probability; a bounded research falsification.
 targets=np.zeros((len(NAME),n),np.int32)
 stops=np.zeros_like(targets)
 durations=np.zeros_like(targets)
 for i in range(len(NAME)):
  if duka:
   # Source spread is large; avoid fake .10 tick micro win when market already
   # imposes a large opening liquidation deficit. No target below 120 raw.
   net=np.maximum(120, .22*sp + .16*np.abs(m6))
   adverse=np.maximum(130, .18*np.abs(m2)+70)
  else:
   net=np.maximum(90, .10*sp+.11*np.abs(m6))
   adverse=np.maximum(100, .14*np.abs(m2)+70)
  if i==1:net*=.85;adverse*=.9
  if i==2:net*=.7;adverse*=.72
  if i==3:net*=1.1;adverse*=1.1
  if i==5:net*=.85;adverse*=.85
  # bound protection to avoid enormous hidden stop costs
  targets[i]=np.minimum(np.rint(net),1800).astype(np.int32)
  stops[i]=np.minimum(np.rint(adverse),900).astype(np.int32)
  durations[i]=[8000,16000,12000,25000,12000,12000][i]
  # Allow higher H for slow and more expensive Dukas in C3 C4 only.
  if duka and i in (2,3):durations[i,:]=int([8000,16000,12000,25000,12000,12000][i]*1.4)
 return ActionSet(m,targets,stops,durations)

"""F401-R150T: Native QUOTE-clock Bayesian state (research-only, no orders).

This composes the original F3U GaussianNIGBOCPD mathematics on ALL observed
native quote revisions, not the former sample of parent-vetoed FILTER events.
Input data: UTC timestamp_ms and genuine broker BID/ASK raw integer 0.001 quotes.
Never feeds truth, teacher, matured outcome, parent score, or future data.
All state is updated once per source quote; prediction snapshots are as-of the
strictly earlier quote (not the T1 decision quote).

CAVEATS: Truncated Bayesian run length is an approximation; NIG priors/hazards
remain an untrained research proposal until calibration on physical quote data;
no economic signal or original source-root certification is implied.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
from pathlib import Path
import sys
import numpy as np

_HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(_HERE/'original_f3u'))
from r150f3u_bayesian_reliability import GaussianNIGBOCPD

FEATURE_NAMES=(
    'quote_bayes_return_cp_probability','quote_bayes_return_run_expectation',
    'quote_bayes_return_entropy','quote_bayes_return_surprise',
    'quote_bayes_spread_cp_probability','quote_bayes_spread_run_expectation',
    'quote_bayes_spread_entropy','quote_bayes_spread_surprise',
    'quote_bayes_beta_positive_p','quote_bayes_beta_direction_std',
    'quote_bayes_signed_revision_confidence','quote_bayes_nonzero_quote_density',
    'quote_bayes_sign_entropy','quote_bayes_abs_path_dollars',
    'quote_bayes_signed_net_dollars','quote_bayes_directional_efficiency',
    'quote_bayes_quote_reversal_fraction','quote_bayes_spread_widen_fraction',
    'quote_bayes_bid_ask_disagreement','quote_bayes_spread_dollars',
    'quote_bayes_interarrival_ema_ms','quote_bayes_last_quote_age_ms',
    'quote_bayes_observed_quote_count','quote_bayes_observation_uncertainty',
)
FORBIDDEN=('truth','teacher','label','oracle','outcome','matured','r24','r148','r150g')
assert not any(x in name for name in FEATURE_NAMES for x in FORBIDDEN)

@dataclass(frozen=True)
class BayesObservation:
    decision_ms:int
    quotes_seen:int
    last_quote_ms:int
    vector:np.ndarray

class NativeQuoteBayes:
    """One chronological full-quote source-native state per broker/session tape."""
    def __init__(self, hazard_seconds:float=180., max_run:int=48):
        if hazard_seconds<=0 or max_run<8:raise ValueError('invalid BOCPD configuration')
        self._ret=GaussianNIGBOCPD(max_run=max_run,base_hazard_s=hazard_seconds)
        self._spread=GaussianNIGBOCPD(max_run=max_run,base_hazard_s=hazard_seconds)
        self.count=0;self.last_t=None;self.last_bid=None;self.last_ask=None
        self.last_mid=None;self.start_mid=None
        self.last_sign=0;self.reversals=0;self.n_nonzero=0
        self.pos=0;self.neg=0;self.zero=0;self.widen=0;self.discord=0
        self.sum_abs_mid_ticks=0.;self.dt_ema=0.;self.latest_return_cp=np.zeros(4,np.float32)
        self.latest_spread_cp=np.zeros(4,np.float32)

    def observe(self,timestamp_ms:int,bid_raw:int,ask_raw:int)->None:
        t=int(timestamp_ms);bid=int(bid_raw);ask=int(ask_raw)
        if bid<=0 or ask<=bid:raise ValueError('non-positive bid or non-positive spread')
        if self.last_t is not None and t<self.last_t:raise ValueError('quote time moved backward')
        mid=(bid+ask)*0.5;spread=(ask-bid)/1000.
        if self.last_t is not None:
            dt=t-self.last_t
            db=bid-self.last_bid;da=ask-self.last_ask
            delta=(mid-self.last_mid)/1000.
            sg=1 if delta>0 else -1 if delta<0 else 0
            self.pos+=sg==1;self.neg+=sg==-1;self.zero+=sg==0
            self.n_nonzero+=sg!=0
            self.sum_abs_mid_ticks+=abs(delta)
            self.widen+=(ask-bid)>(self.last_ask-self.last_bid)
            self.discord+=(db*da)<0
            if sg and self.last_sign and sg!=self.last_sign:self.reversals+=1
            if sg:self.last_sign=sg
            self.dt_ema=dt if self.count==1 else (.98*self.dt_ema+.02*dt)
            self.latest_return_cp=self._ret.update(float(np.clip(delta,-10.,10.)),t)
            spread_delta=(ask-bid-(self.last_ask-self.last_bid))/1000.
            self.latest_spread_cp=self._spread.update(float(np.clip(spread_delta,-10.,10.)),t)
        else:
            self.start_mid=mid
        self.count+=1;self.last_t=t;self.last_bid=bid;self.last_ask=ask;self.last_mid=mid

    def snapshot(self,decision_ms:int,side:int)->BayesObservation:
        d=int(decision_ms)
        if self.count==0:raise ValueError('no native source quote state')
        if self.last_t>=d:raise ValueError('must exclude decision and future quotes')
        if side not in (-1,1):raise ValueError('side must be -1 or +1')
        a=self.pos+.5;b=self.neg+.5
        posterior=a/(a+b);sd=math.sqrt(a*b/((a+b)**2*(a+b+1)))
        count=max(1,self.count-1);nonzero=self.pos+self.neg
        p_pos=(self.pos+.5)/(count+1.5)
        p_neg=(self.neg+.5)/(count+1.5)
        p_zero=(self.zero+.5)/(count+1.5)
        entropy=-sum(p*math.log(p) for p in (p_pos,p_neg,p_zero))/math.log(3)
        net=(self.last_mid-self.start_mid)*side/1000.
        total=self.sum_abs_mid_ticks
        conf=(2*posterior-1)*max(0,1-2*sd)*nonzero/count
        vec=np.array([
            *self.latest_return_cp,*self.latest_spread_cp,
            posterior,sd,conf*side,nonzero/count,entropy,total,net,
            net/(total+1e-9),self.reversals/max(1,nonzero-1),
            self.widen/count,self.discord/count,(self.last_ask-self.last_bid)/1000.,
            self.dt_ema,d-self.last_t,self.count,
            min(1.,float(entropy+sd)/2.),
        ],dtype=np.float32)
        assert len(vec)==len(FEATURE_NAMES)==24 and np.isfinite(vec).all()
        vec.setflags(write=False)
        return BayesObservation(decision_ms=d,quotes_seen=self.count,last_quote_ms=self.last_t,vector=vec)

def asof_quote_bayes(t_ms:np.ndarray,bid_raw:np.ndarray,ask_raw:np.ndarray,
                     decision_ms:int,side:int,hazard_seconds:float=180.,max_run:int=48):
    """Strict pre-decision deterministic research replay, never includes T1 tick."""
    t=np.asarray(t_ms,dtype=np.int64)
    b=np.asarray(bid_raw,dtype=np.int64)
    a=np.asarray(ask_raw,dtype=np.int64)
    if not (t.ndim==b.ndim==a.ndim==1 and len(t)==len(b)==len(a)):
        raise ValueError('malformed native quotes')
    if np.any(t[1:]<t[:-1]):raise ValueError('unsorted native quotes')
    engine=NativeQuoteBayes(hazard_seconds,max_run)
    for i in range(int(np.searchsorted(t,int(decision_ms),side='left'))):
        engine.observe(int(t[i]),int(b[i]),int(a[i]))
    return engine.snapshot(decision_ms,side)

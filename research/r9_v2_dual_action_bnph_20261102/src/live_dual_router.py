"""Dual-action online research router over ORIGINAL complete FastClock + R9 exit.

At every eligible 250ms quote event, it generates [BUY, SELL] views from the
SAME causal state, predicts both, optionally WAITs, then repeats both after
later quotes. The old specialist side is recorded only as a continuous context
feature; it never nominates or locks the action. Preserves the original source-exact 102-feature diagnostic contract and, for
version-aware repaired policies, composes the new 228-feature ordered quote-state
contract from the same causal tick stream. Source feature parity is tested.

Not deployment code: training is baseline-timestamp off-policy and neither
model calibration nor profitability criteria passed. FAIL CLOSED by default.
"""
from __future__ import annotations
import bisect,collections,math,sys
from pathlib import Path
import numpy as np
from source_exact import two_views
from decision import DualActionPolicy,Prediction,Limits
from competing_hawkes import CompetingQuoteHawkes
from repaired_features import LaggedQuoteGeometry,compose_repaired_features,FEATURE_VERSION

# Reuse exact frozen v2 & high-volume feature clock, never reconstruct.
RESTORE=Path('/mnt/data/v2_new_research/restore')
sys.path.insert(0,str(RESTORE/'repair'/'src'))
sys.path.insert(0,str(RESTORE/'original_v2'/'src'))
from high_volume_stream import FastClock,specialist_evidence,TickExactActivePath

HORIZONS=(250,500,1000,5000,15000,45000,300000,900000,3600000,14400000)
PREFIX=('bu','bd','au','ad','sw','sn','ss','path','rv')

class ExactQuoteState:
    """Bounded rolling <=4h quote state. Pure prefix feature parity with
    original causal_dual_features.asof (no book depth or true traded volume).
    """
    def __init__(self):
        self.t=[];self.b=[];self.a=[];self.p={k:[0.] for k in PREFIX}
        self.max_keep_ms=14400000+5000
    def append(self,q):
        t=int(q.utc_ms);bid=float(q.bid);ask=float(q.ask)
        if self.t and t<self.t[-1]:raise ValueError('nonchronological')
        if ask<bid:raise ValueError('crossed quote')
        i=len(self.t);oldb=self.b[-1] if i else bid;olda=self.a[-1] if i else ask
        spread=ask-bid;oldspread=olda-oldb;db=bid-oldb;da=ask-olda
        ds=spread-oldspread;dm=(db+da)/2
        incr=dict(bu=int(db>1e-10),bd=int(db<-1e-10),au=int(da>1e-10),ad=int(da<-1e-10),
                  sw=int(ds>1e-10),sn=int(ds<-1e-10),ss=spread,path=abs(dm),rv=dm*dm)
        self.t.append(t);self.b.append(bid);self.a.append(ask)
        for k,v in incr.items():self.p[k].append(self.p[k][-1]+v)
        # Batch trimming, not a per-tick costly left-pop. This preserves the
        # entire requested 4h history plus an explicit 5s buffer.
        if len(self.t)>100000 and self.t[0]<t-self.max_keep_ms-30000:
            cut=bisect.bisect_left(self.t,t-self.max_keep_ms)
            if cut>25000:
                self.t=self.t[cut:];self.b=self.b[cut:];self.a=self.a[cut:]
                for k in PREFIX:self.p[k]=self.p[k][cut:]
    def vector(self,evidence=0.,lane_reversal=0.):
        i=len(self.t)-1
        if i<0:raise ValueError('uninitialized')
        t=self.t[-1];bid=self.b[-1];ask=self.a[-1]
        j0=max(0,i-1);db=bid-self.b[j0];da=ask-self.a[j0]
        spread=ask-bid
        hour=(t//3600000)%24;dow=((t//86400000)+3)%7
        out=[spread,db,da,db-da,(db+da)/2,(db-da)/(abs(db)+abs(da)+.001),
             evidence,lane_reversal,math.sin(2*math.pi*hour/24),math.cos(2*math.pi*hour/24),
             math.sin(2*math.pi*dow/7),math.cos(2*math.pi*dow/7)]
        for h in HORIZONS:
            j=bisect.bisect_left(self.t,t-h)
            n=i-j+1;m=(bid+ask)*.5;mj=(self.b[j]+self.a[j])*.5;delta=m-mj
            d={k:self.p[k][i+1]-self.p[k][j] for k in PREFIX}
            up=d['bu']+d['au'];down=d['bd']+d['ad'];total=up+down
            out.extend([delta,d['ss']/n,bid-self.b[j],ask-self.a[j],
                        (up-down)/(total+1),(d['sn']-d['sw'])/(n+1),
                        math.sqrt(max(0,d['rv'])),n/(h/1000),
                        abs(delta)/(max(0,d['path'])+.0001)])
        z=np.asarray(out,np.float32)
        assert len(z)==102
        return z

class FrozenDualPolicy:
    """Research-only full-feature trained tri-class model and calibration.
    Use on historical checks ONLY. No simulated broker order is released unless
    strict source-parity and independent performance acceptance have passed.
    """
    def __init__(self,model_file,policy_file,accept_for_research=False):
        import lightgbm as lgb
        self.model=lgb.Booster(model_file=str(model_file))
        with np.load(policy_file) as d:
            self.cutoffs=d['cutoffs'].copy();self.payoff=d['payoff_bins'].copy()
        if self.model.num_feature()!=103:raise ValueError('feature mismatch')
        self.feature_version='legacy_r9_v2_102_sideview_v1'
        self.accept_for_research=bool(accept_for_research)
    def evaluate(self,x):
        # Side order is absolutely [BUY,SELL], independent of baseline.
        q=self.model.predict(two_views(x.reshape(1,-1),np.array([1],np.int8)),num_threads=1)
        forecasts=[]
        for j,side in enumerate((1,-1)):
            p=q[j];k=min(19,int(p[2]*20))
            forecasts.append(Prediction(side,float(p[2]),float(p[0]),float(p[1]),
                                        float(self.payoff[j,k])))
        return forecasts
    def action(self,x,spread):
        buy,sell=self.evaluate(x)
        limits=Limits()
        policy=DualActionPolicy(self.cutoffs[0],self.cutoffs[1],limits)
        side,reason=policy.decide(buy,sell,spread)
        if not self.accept_for_research:return 0,'FAIL_CLOSED_RESEARCH_ONLY'
        return side,reason

class DualObservedRouter:
    """Reevaluation after every observed tick-slot, no fixed pending.side.

    Does not execute orders: research shadow decisions use complete original
    FastClock, independent exact 102-feature quote state and repaired ordered quote
    geometry. If policy is absent, all eligible decisions WAIT; this is the only
    safe default.
    """
    def __init__(self,policy=None):
        self.clock=FastClock();self.quotes=ExactQuoteState();self.geometry=LaggedQuoteGeometry();self.policy=policy
        self.hawkes=CompetingQuoteHawkes();self.last_hawkes=None
        self.count=collections.Counter();self.history=[]
        self.last_action=0
        self.active=None;self.completed=[];self.fee=.02
    def on_quote(self,q):
        # Original R9 exits run on every chronological tick, not just 250ms.
        closed=False
        if self.active is not None:
            result=self.active.update(q)
            if result is not None:
                self.completed.append(dict(entry_ms=result.entry_ms,exit_ms=result.exit_ms,
                                           side=result.side,net=result.net,exit_type=result.exit_type))
                self.count['completed_positions']+=1
                self.active=None;closed=True
        self.quotes.append(q)
        self.geometry.append(q)
        self.hawkes.observe(q.utc_ms,q.bid,q.ask)
        flushed=self.clock.add(q)
        self.count['ticks']+=1
        if not flushed:return 0
        if closed or self.active is not None:return 0
        if not self.clock.ready():self.count['warmup']+=1;return 0
        f=self.clock.features(q)
        old_side,evidence,lane,pressure,cost=specialist_evidence(f)
        # Old specialist is causal contextual observation, NOT direction choice.
        x=self.quotes.vector(evidence=float(evidence),lane_reversal=float(lane=='reversal'))
        # Six-channel quote excitation remains excluded from the frozen legacy
        # diagnostic. The repaired v4 contract admits its causal state as model
        # input only; it is never added post-hoc as a probability boost.
        self.last_hawkes=self.hawkes.features()
        policy_x=x
        if self.policy is not None and getattr(self.policy,'feature_version',None)==FEATURE_VERSION:
            policy_x=compose_repaired_features(x,self.geometry,self.last_hawkes)
        side,reason=self.policy.action(policy_x,q.spread) if self.policy else (0,'NO_CALIBRATED_DUAL_POLICY')
        self.count['decision_events']+=1;self.count[reason]+=1
        if side:
            self.count['selected_research_actions']+=1
            self.active=TickExactActivePath(q,side,fee=self.fee)
        self.last_action=side
        return side

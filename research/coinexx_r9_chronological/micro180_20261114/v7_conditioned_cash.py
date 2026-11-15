"""Source-native Micro180 V7: setup-conditioned, dual-side past-only cash audit.

This is a candidate-timestamp research overlay, *not* a validated profitable model.
It REUSES the existing 180s millisecond-aligned bar/quote engine and V6 cash
accounting; no tick tape regeneration, no old AUC feature model, no DOM claims.

Past comparisons use only completed original 1s bars strictly before current
second. For each past anchor, both setup and the 6-second first-passage outcome
are entirely in already completed history. Gaussian similarity weights are
predeclared engineering priors, not fitted classification probabilities.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite, sqrt
from statistics import median
from typing import Optional

from coinexx_r9.models import Tick
from micro180 import RollingThreeMinute
from v6_past_only_utility import PastOnlyCashMicroV6, V6Spec


@dataclass(frozen=True)
class V7Spec:
    horizon_seconds: int = 6
    anchor_stride_seconds: int = 7
    min_effective_samples: float = 4.0
    similarity_width: float = 0.55
    uncertainty_multiplier: float = 1.0
    min_buy_penalized_cash: float = 0.0
    min_sell_penalized_cash: float = 0.0
    # Preserve candidate/entry volume in SHADOW mode. Gate opt-in, never silent.
    enable_cash_gate: bool = False
    # Do not silently alter V6's profit lock/horizon or $2 intended risk.
    enable_conditioned_holding: bool = False
    min_hold_increment: float = 0.0
    hold_horizon_seconds: int = 3

    def __post_init__(self):
        n=(self.min_effective_samples,self.similarity_width,
           self.uncertainty_multiplier,self.min_buy_penalized_cash,
           self.min_sell_penalized_cash,self.min_hold_increment)
        if (self.horizon_seconds<2 or self.horizon_seconds>12 or
            not self.horizon_seconds<=self.anchor_stride_seconds<=25 or
            not 2<=self.min_effective_samples<=24 or
            not .15<=self.similarity_width<=2 or
            not 0<=self.uncertainty_multiplier<=4 or
            any(not isfinite(v) for v in n) or
            any(not -2<=v<=2 for v in n[3:]) or
            not -.5<=self.min_hold_increment<=1.75 or
            not 1<=self.hold_horizon_seconds<=10):
            raise ValueError('Invalid frozen V7 conditioned-cash settings')


@dataclass(frozen=True)
class ConditionedCashEvidence:
    side: int
    sample_count: int
    effective_samples: float
    mean_cash: float
    penalized_cash: float
    profit_first_weight: float
    adverse_first_weight: float
    observed_anchor_gaps: int
    usable: bool


@dataclass(frozen=True)
class _Setup:
    eff5: float
    eff15: float
    spread_ratio: float
    quote_intensity: float


def _contiguous(q, first: int, last: int, max_gap_ms: int=2_000) -> bool:
    return (first>=0 and last<len(q) and all(
        0 < q[j].start_ms-q[j-1].start_ms<=max_gap_ms
        and 0 < q[j].first_ms-q[j-1].last_ms<=max_gap_ms
        for j in range(first+1,last+1)))


def _setup(q, i: int, side: int, bid_now: int, ask_now: int, count_now: int) -> Optional[_Setup]:
    # Validate the real quote link INTO a historical anchor, not only its
    # preceding 15 observed seconds. i=len(q) is the LIVE candidate.
    if i<15 or not _contiguous(q,i-15,min(i,len(q)-1)): return None
    side_closes=[x.bid_close if side>0 else x.ask_close for x in q[i-15:i]]
    liq=bid_now if side>0 else ask_now
    def eff(seq):
        values=seq+[liq]
        length=sum(abs(a-b) for a,b in zip(values,values[1:]))
        return max(-1.,min(1.,side*(values[-1]-values[0])/max(1,length)))
    spr_reference=max(1.,float(median([x.spread_close for x in q[i-15:i]])))
    now_spread=ask_now-bid_now
    intensity_baseline=sum(x.n for x in q[i-15:i])/15.
    return _Setup(eff(side_closes[-5:]),eff(side_closes),
        now_spread/spr_reference, min(4.,count_now/max(1.,intensity_baseline)))


def conditioned_cash_first_passage(r:RollingThreeMinute,t:Tick,side:int,
       *,k:float=1.0,cost:float=.20,minimum_net:float=.10,
       adverse_net:float=-2.0,spec:V7Spec=V7Spec()) -> ConditionedCashEvidence:
    """Estimate the past-only conditioned first-hit cash at an actual tick.

    V7 setup: signed 5s/15s executable-side efficiencies, relative quoted
    spread, short quote activity (not traded volume). Kernel weighting compares
    actual current candidate to *historical anchor setups*, not unconditional
    past moving returns. Both sides should be called, even if only one 5s
    candidate is currently eligible, to prevent swapped SELL labels.
    """
    if side not in (-1,1) or k<=0 or cost<0 or minimum_net<0 or adverse_net>=0:
        raise ValueError('Invalid BUY/SELL economics')
    q=r.closes(t.time_msc,180_000)
    empty=ConditionedCashEvidence(side,0,0.,0.,float('-inf'),0.,0.,0,False)
    if len(q)<30 or t.time_msc-q[-1].last_ms>2500:
        return empty
    # Current incomplete tick is an OBSERVATION at decision time. It is never
    # inserted as a completed historical candle or a historic label.
    if not _contiguous(q,len(q)-15,len(q)-1):return empty
    current=_setup(q,len(q),side,t.bid_u,t.ask_u,
                   r.current[1000].n if 1000 in r.current else 1)
    if current is None:return empty
    values=[]; weights=[];first_hits=0.;stops=0.;gap_count=0
    horizon=spec.horizon_seconds
    # Anchor i's conditioning input consists ONLY of q[:i] and q[i]'s close;
    # all q[i+1:i+h] are past relative to CURRENT tick, never current labels.
    for i in range(15,len(q)-horizon,spec.anchor_stride_seconds):
        if not _contiguous(q,i-15,i+horizon):
            gap_count+=1;continue
        anchor=q[i]
        ctx=_setup(q,i,side,anchor.bid_close,anchor.ask_close,anchor.n)
        if ctx is None:
            gap_count+=1;continue
        # Compare only the SAME direction's executable-side structure.
        if ctx.eff5*current.eff5<0 or ctx.eff15*current.eff15<0:continue
        differences=(
            (ctx.eff5-current.eff5)/spec.similarity_width,
            (ctx.eff15-current.eff15)/spec.similarity_width,
            (ctx.spread_ratio-current.spread_ratio)/.5,
            (ctx.quote_intensity-current.quote_intensity)/1.5,
        )
        dist2=sum(z*z for z in differences)
        w=exp(-.5*dist2)
        if w<.01:continue
        entry=anchor.ask_close if side>0 else anchor.bid_close
        outcome=None;reason='timeout'
        for j in range(i+1,i+horizon+1):
            liq=q[j].bid_close if side>0 else q[j].ask_close
            outcome=side*(liq-entry)*k/100.-cost
            if outcome>=minimum_net:
                reason='profit';break
            if outcome<=adverse_net:
                reason='adverse';break
        if outcome is None:continue
        values.append(outcome);weights.append(w)
        if reason=='profit':first_hits+=w
        if reason=='adverse':stops+=w
    if not values:return empty
    sumw=sum(weights);sumw2=sum(w*w for w in weights)
    effective=sumw*sumw/sumw2
    mu=sum(w*x for w,x in zip(weights,values))/sumw
    variance=sum(w*(x-mu)**2 for w,x in zip(weights,values))/sumw
    # Explicit *heuristic* uncertainty penalty, NOT a calibrated confidence bound.
    penalized=mu-spec.uncertainty_multiplier*sqrt(variance/max(1,effective))
    return ConditionedCashEvidence(side,len(values),round(effective,6),
            mu,penalized,first_hits/sumw,stops/sumw,gap_count,
            effective>=spec.min_effective_samples)


def conditioned_incremental_hold(r:RollingThreeMinute,t:Tick,side:int,
       *,k:float=1.0,spec:V7Spec=V7Spec()) -> Optional[float]:
    """Past-only *incremental* cash utility of holding versus exit NOW.

    A trade has already paid entry spread/fee; the historical hold path starts
    from an executable *liquidation* quote and never charges the old fee twice.
    The sample is matched to the CURRENT SIDE-SPECIFIC setup, not unconditional.
    """
    if side not in (-1,1) or k<=0:raise ValueError('side/k')
    q=r.closes(t.time_msc,180_000)
    h=spec.hold_horizon_seconds
    if len(q)<30 or t.time_msc-q[-1].last_ms>2500 or not _contiguous(q,len(q)-15,len(q)-1):
        return None
    cur=_setup(q,len(q),side,t.bid_u,t.ask_u,
           r.current[1000].n if 1000 in r.current else 1)
    if cur is None:return None
    weights=[];increment=[]
    for i in range(15,len(q)-h,spec.anchor_stride_seconds):
        if not _contiguous(q,i-15,i+h):continue
        anchor=q[i]
        a=_setup(q,i,side,anchor.bid_close,anchor.ask_close,anchor.n)
        if a is None or a.eff5*cur.eff5<0 or a.eff15*cur.eff15<0:continue
        dd=((a.eff5-cur.eff5)/spec.similarity_width,
            (a.eff15-cur.eff15)/spec.similarity_width,
            (a.spread_ratio-cur.spread_ratio)/.5,
            (a.quote_intensity-cur.quote_intensity)/1.5)
        w=exp(-.5*sum(d*d for d in dd))
        if w<.01:continue
        before=anchor.bid_close if side>0 else anchor.ask_close
        after=q[i+h].bid_close if side>0 else q[i+h].ask_close
        weights.append(w);increment.append(side*(after-before)*k/100.)
    if not weights:return None
    sumw=sum(weights); effective=sumw*sumw/sum(w*w for w in weights)
    if effective<spec.min_effective_samples:return None
    mean=sum(w*x for w,x in zip(weights,increment))/sumw
    var=sum(w*(x-mean)**2 for w,x in zip(weights,increment))/sumw
    return mean-spec.uncertainty_multiplier*sqrt(var/max(1.,effective))


class SetupConditionedMicroV7(PastOnlyCashMicroV6):
    """Research-only extension preserving the full V6 risk/hold lifecycle.

    Base V6 economic filter is intentionally SHADOW to avoid double gating.
    V7 can be explicitly enabled after source-parity and benchmark checks.
    """
    def __init__(self,cfg,cash,micro_spec,*,v5=None,
                 v6:V6Spec=V6Spec(),v7:V7Spec=V7Spec()):
        from v5_path_lifecycle import V5Spec
        v5=v5 if v5 is not None else V5Spec()
        if v7.enable_conditioned_holding and not (micro_spec.experimental_runner and v5.enable_protected_continuation):
            raise ValueError("V7 conditional hold requires an enabled, stop-protected V5/V6 runner")
        from dataclasses import replace
        super().__init__(cfg,cash,micro_spec,v5=v5,v6=replace(v6,audit_only=True))
        self.v7=v7
        self._v7_entry_quote_key=None
        self._v7_evidence={}
        self._v7_hold_quote_key=None
        self._v7_hold_cache={}

    def _open_trade(self,t:Tick,side:int):
        # Same second / even same millisecond is not the same candidate.
        quote_key=(t.ordinal,t.time_msc,t.bid_u,t.ask_u,
                   self.rolling.current[1000].n)
        if self._v7_entry_quote_key!=quote_key:
            self._v7_entry_quote_key=quote_key
            self._v7_evidence={}
        for d in (1,-1):
            if d not in self._v7_evidence:
                self._v7_evidence[d]=conditioned_cash_first_passage(
                    self.rolling,t,d,k=self.cash.k,cost=self.cash.cost,
                    minimum_net=self.micro_spec.min_net_cash,
                    adverse_net=-self.micro_spec.hard_risk_cash,spec=self.v7)
        b=self._v7_evidence[1];s=self._v7_evidence[-1]
        chosen=b if side>0 else s
        self.stats['v7_candidate_evaluations']+=1
        if not chosen.usable:self.stats['v7_sparse_conditional']+=1
        goal=self.v7.min_buy_penalized_cash if side>0 else self.v7.min_sell_penalized_cash
        if not chosen.usable or chosen.penalized_cash<=goal:
            self.stats['v7_nonpositive_conditional']+=1
            if self.v7.enable_cash_gate:return
        self._signal_meta.update(v7_buy_est=round(b.penalized_cash,5),
              v7_sell_est=round(s.penalized_cash,5),
              v7_effective=chosen.effective_samples,
              v7_gate_enabled=self.v7.enable_cash_gate)
        return super()._open_trade(t,side)

    def _manage_position(self,t:Tick):
        p=self.position
        if p is not None and self.v7.enable_conditioned_holding:
            liq=t.bid_u if p.side>0 else t.ask_u
            net=p.side*(liq-p.entry_price_u)*self.cash.k/100.-self.cash.cost
            age=t.time_msc-p.entry_time_msc
            s=self.micro_spec
            forced=(age>=s.max_lifetime_ms or net<=-s.hard_risk_cash or
                    net>=s.preferred_max_net_cash or
                    self.rolling.last_gap_ms>s.max_quote_gap_ms or
                    (self.cash.governor and (self.account.day_lock or self.account.permanent_lock)))
            if not forced and s.min_net_cash<=net<s.preferred_max_net_cash:
                self.stats['v7_hold_evaluations']+=1
                # Exact executable-quote cache; never reuse a stale same-ms
                # hold forecast after price/spread/quote-count changes.
                quote_key=(t.ordinal,t.time_msc,t.bid_u,t.ask_u,
                           self.rolling.current[1000].n)
                if quote_key!=self._v7_hold_quote_key:
                    self._v7_hold_quote_key=quote_key
                    self._v7_hold_cache={}
                if p.side not in self._v7_hold_cache:
                    self._v7_hold_cache[p.side]=conditioned_incremental_hold(
                         self.rolling,t,p.side,k=self.cash.k,spec=self.v7)
                utility=self._v7_hold_cache[p.side]
                if utility is None or utility<=self.v7.min_hold_increment:
                    self.stats['v7_hold_not_positive']+=1
                    self._record_close(t,'v7_conditioned_hold_harvest',liq)
                    return
        return super()._manage_position(t)

    def report(self):
        r=super().report()
        r['v7_setup_conditioned']={
            'research_only':True,'model_auc_used':False,
            'past_only_completed_seconds':True,
            'separate_buy_sell_candidate_labels':True,
            'not_calibrated_probabilities':True,
            'millisecond_source_order':True,
            'hard_cap_cash_intended':self.micro_spec.hard_risk_cash,
            'cash_010_first_observed':self.micro_spec.min_net_cash,
            'cash_175_preferred':self.micro_spec.preferred_max_net_cash,
            'volume_rule_max_entries_minute':self.micro_spec.max_entries_per_source_minute,
            'shadow_only':not self.v7.enable_cash_gate,
            'conditional_hold_enabled':self.v7.enable_conditioned_holding,
            'conditional_hold_evaluations':self.stats['v7_hold_evaluations'],
            'conditional_hold_not_positive':self.stats['v7_hold_not_positive'],
            'v7_conditioned_candidate_evaluations':self.stats['v7_candidate_evaluations'],
            'v7_sparse_conditional':self.stats['v7_sparse_conditional'],
            'v7_nonpositive_conditional':self.stats['v7_nonpositive_conditional']}
        return r

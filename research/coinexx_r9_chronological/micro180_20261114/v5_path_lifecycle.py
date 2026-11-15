"""R9 Micro180 V5 quote-path admission and protected cash-exit experiment.

Extends the existing historical millisecond quote/candle engine. No new data
cache, no old 155-feature AUC, no simulated passive fills. Research only.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import ceil, isfinite
from typing import Optional
from statistics import median

from coinexx_r9.models import Tick
from micro180 import Micro180R9
from asymmetric_v3 import AsymmetricMicroR9, AsymSpec
from v5_ms_path import MsQuarterPath


@dataclass(frozen=True)
class V5Spec:
    # Predeclared hypotheses. Negative results are legitimate failures.
    min_buy_path: float = -0.05
    min_sell_path: float = -0.05
    min_coherence: float = 0.25
    min_history: int = 30
    max_spread_relative: float = 1.50
    use_m1_price_indicator: bool = True
    permit_early_adverse_exit: bool = False
    adverse_net_cash: float = -0.45
    adverse_path_max: float = -0.45
    min_adverse_age_ms: int = 1500
    enable_protected_continuation: bool = False
    hold_buy_path: float = 0.25
    hold_sell_path: float = 0.25
    protect_cost_cash: float = 0.0  # conservative round-trip costs already in ResearchCash

    def __post_init__(self):
        values=(self.min_buy_path,self.min_sell_path,self.min_coherence,
                self.max_spread_relative,self.adverse_net_cash,self.adverse_path_max,
                self.hold_buy_path,self.hold_sell_path,self.protect_cost_cash)
        if (any(not isfinite(x) for x in values) or
            not -2<=self.min_buy_path<=2 or not -2<=self.min_sell_path<=2 or
            not 0<=self.min_coherence<=1 or not 15<=self.min_history<=180 or
            self.max_spread_relative<1 or not 0<=self.min_adverse_age_ms<=30000 or not -2<=self.adverse_path_max<=0 or
            not -2<=self.adverse_net_cash<=0 or self.protect_cost_cash<0 or
            not -2<=self.hold_buy_path<=2 or not -2<=self.hold_sell_path<=2):
            raise ValueError('V5 invalid causal quote/exit controls')


@dataclass(frozen=True)
class PathEvidence:
    side: int
    score: float
    coherence: float
    directional_efficiency: float
    tail_persistence: float
    recent_reversal: float
    spread_relative: float
    quote_activity_ratio: float
    native_price_bias: float
    ms250_efficiency: float=0.0
    ms250_coherence: float=0.0


def path_evidence(ring, t:Tick, side:int, min_history:int=30,
                  ms250:Optional[MsQuarterPath]=None)->Optional[PathEvidence]:
    """Previous CLOSED second Bid/Ask quotes only; t is current executable quote.

    Unlike a sorted price-feature vector, this stores the ORDER of signs and
    late reversals. Does not claim trade direction or true trade volume.
    """
    if side not in (-1, 1): raise ValueError('BUY=+1 or SELL=-1')
    if not 15<=min_history<=180:raise ValueError('history')
    q5=ring.closes(t.time_msc,5_000)
    q15=ring.closes(t.time_msc,15_000)
    q30=ring.closes(t.time_msc,30_000)
    q180=ring.closes(t.time_msc,180_000)
    if (len(q5)<2 or len(q15)<7 or len(q30)<12 or
        len(q180)<min_history or t.time_msc-q5[-1].last_ms>2500):
        return None
    if any(b.start_ms-a.start_ms>2500 for q in (q5,q15,q30)
           for a,b in zip(q,q[1:])):return None
    quotes=[x.bid_close if side>0 else x.ask_close for x in q15]
    now=t.bid_u if side>0 else t.ask_u
    steps=[side*(b-a) for a,b in zip(quotes,quotes[1:])]
    steps.append(side*(now-quotes[-1]))
    path=sum(abs(x) for x in steps)
    eff=sum(steps)/max(1.,path)
    # Last 2 completed transitions and the current observed quote are decisive.
    tail=steps[-3:]
    denom=sum(abs(x) for x in tail)
    signed_tail=sum(tail)/max(1.,denom)
    reversal=sum(abs(x) for x in tail if x<0)/max(1.,denom)
    # Only a common price update of BOTH sides counts as corroborating movement.
    paired=0
    for a,b in zip(q15,q15[1:]):
        db=side*(b.bid_close-a.bid_close)
        da=side*(b.ask_close-a.ask_close)
        if db>0 and da>0:paired+=1
    coherent=paired/max(1,len(q15)-1)
    spreads=sorted(x.spread_close for x in q15)
    ref=max(1.,float(median(spreads)))
    spr=t.spread_points/ref
    qrate5=sum(x.n for x in q5)/5.0
    qrate180=sum(x.n for x in q180)/180.0
    intensity=min(3.,qrate5/max(.05,qrate180))
    bias=ring.m1.bias(side)
    bias=0.0 if bias is None else bias
    # Separate order-sensitive within-second path; no future/current-second OHLC.
    micro=ms250.signature(t.time_msc,side) if ms250 is not None else None
    ms_eff=micro.efficiency if micro is not None else 0.0
    ms_coh=micro.coherence if micro is not None else 0.0
    # Asymmetric coefficients are deliberately small and research-unfitted.
    if side>0:
        score=(.36*eff+.24*signed_tail+.28*coherent+.10*bias
               +.05*min(2.,intensity-1.)-.27*max(0.,spr-1.)-.20*reversal
               +.12*ms_eff+.08*(ms_coh-.50))
    else:
        score=(.34*eff+.26*signed_tail+.26*coherent+.12*bias
               +.06*min(2.,intensity-1.)-.30*max(0.,spr-1.)-.20*reversal
               +.12*ms_eff+.08*(ms_coh-.50))
    return PathEvidence(side,score,coherent,eff,signed_tail,reversal,spr,intensity,bias,ms_eff,ms_coh)


class PathLifecycleV5(AsymmetricMicroR9):
    """Observe 5s candidate → check 15s structure → apply 30s veto → V5 permission.

    The original Micro180 protective SL/quote-time risk rules continue to apply;
    optional early exit and protected hold are separately switchable.
    """
    def __init__(self,cfg,cash,spec,quant:AsymSpec=AsymSpec(active=False),v5:V5Spec=V5Spec()):
        super().__init__(cfg,cash,spec,quant)
        self.v5=v5
        self.ms250=MsQuarterPath()

    def _push_second(self,t:Tick):
        super()._push_second(t)
        self.ms250.update(t)

    def _open_trade(self,t:Tick,side:int):
        e=path_evidence(self.rolling,t,side,self.v5.min_history,self.ms250)
        if e is None:
            self.stats['v5_sparse_path']+=1;return
        required=self.v5.min_buy_path if side>0 else self.v5.min_sell_path
        if e.coherence<self.v5.min_coherence or e.score<required:
            self.stats['v5_quote_path_veto']+=1;return
        if e.spread_relative>self.v5.max_spread_relative:
            self.stats['v5_spread_veto']+=1;return
        # A null Wilder indicator is NOT assumed positive. The previous
        # micro quote-only checks remain the causal-price fallback.
        bias=self.rolling.m1.bias(side)
        if self.v5.use_m1_price_indicator and bias is not None and bias<-0.50:
            self.stats['v5_indicator_veto']+=1;return
        self._signal_meta.update(v5_score=round(e.score,6),
            v5_coherence=round(e.coherence,5),v5_eff=round(e.directional_efficiency,5),
            v5_tail=round(e.tail_persistence,5),v5_rev=round(e.recent_reversal,5),
            v5_spread_ratio=round(e.spread_relative,5),
            v5_quote_activity=round(e.quote_activity_ratio,5),
            v5_ms250_efficiency=round(e.ms250_efficiency,5),
            v5_ms250_coherence=round(e.ms250_coherence,5),
            v5_price_indicator='completed_m1' if bias is not None else 'quote_only_proxy')
        # Skip AsymmetricMicroR9's older aggregate feature gate. We have a
        # distinct, explicitly order-sensitive eligibility test above.
        Micro180R9._open_trade(self,t,side)


    def _manage_position(self,t:Tick):
        p=self.position
        if p is None:return
        s=self.micro_spec
        liq=t.bid_u if p.side>0 else t.ask_u
        net=p.side*(liq-p.entry_price_u)*self.cash.k/100.0-self.cash.cost
        age=t.time_msc-p.entry_time_msc
        # Parent handles forced exits: $2 first-available, +$1.75, 30s,
        # gap, and account lock. Do not delay these under any hold policy.
        if (net<=-s.hard_risk_cash or net>=s.preferred_max_net_cash or
            age>=s.max_lifetime_ms or self.rolling.last_gap_ms>s.max_quote_gap_ms or
            (self.cash.governor and (self.account.day_lock or self.account.permanent_lock))):
            return Micro180R9._manage_position(self,t)
        if (self.v5.permit_early_adverse_exit and age>=self.v5.min_adverse_age_ms
                and net<=self.v5.adverse_net_cash):
            e=path_evidence(self.rolling,t,p.side,self.v5.min_history,self.ms250)
            if e is not None and e.score<=self.v5.adverse_path_max and e.tail_persistence<0:
                self._record_close(t,'v5_adverse_path',liq);return
        if net<s.min_net_cash:
            return # Base protective stop is independent and checked before EA.
        if not self.v5.enable_protected_continuation:
            return Micro180R9._manage_position(self,t)
        e=path_evidence(self.rolling,t,p.side,self.v5.min_history,self.ms250)
        target=self.v5.hold_buy_path if p.side>0 else self.v5.hold_sell_path
        if e is None or e.score<target or e.tail_persistence<0:
            self._record_close(t,'v5_cash_harvest',liq);return
        # Only continue after an *already feasible* stop protects observed
        # >=+$0.10 NET, including modeled roundtrip costs. No stop widening.
        needed_cash=s.min_net_cash+self.cash.cost+self.v5.protect_cost_cash
        required_move=ceil(needed_cash/self.cash.k*100-1e-12)
        desired=p.entry_price_u+p.side*required_move
        min_dist=self.cfg.tick_size_points+(self.cfg.broker_stops_points if self.cfg.respect_broker_stops else 0)
        legal=(desired<=liq-min_dist if p.side>0 else desired>=liq+min_dist)
        original_better=(desired>p.sl_u if p.side>0 else desired<p.sl_u)
        old_protection=p.side*(p.sl_u-p.entry_price_u)*self.cash.k/100.0-self.cash.cost
        if legal and original_better:
            p.sl_u=desired
            self.stats['v5_causal_stop_lock']+=1
        elif old_protection<s.min_net_cash+self.v5.protect_cost_cash-1e-9:
            self._record_close(t,'v5_no_legal_stop_harvest',liq);return
        self.stats['v5_protected_holds']+=1

    def report(self):
        r=super().report()
        r['v5_lifecycle']={
          'research_only':True,'asymmetric':True,'ordered_quote_path':True,'observed_250ms_bins':self.ms250.rows>0,
          'no_AUC':True,'real_volume':False,'native_MT5_parity':False,
          'cash_risk_objective':self.micro_spec.hard_risk_cash,
          'cash_first_harvest':self.micro_spec.min_net_cash,
          'cash_preferred_cap':self.micro_spec.preferred_max_net_cash,
          'exit_mode':'protected_continuation' if self.v5.enable_protected_continuation else 'first_net_0.10',
          'v5_entry_veto':int(self.stats['v5_quote_path_veto']),
          'v5_sparse':int(self.stats['v5_sparse_path']),
          'v5_early_adverse':int(self.stats['closed_v5_adverse_path']),
          'v5_protected_holds':int(self.stats['v5_protected_holds'])}
        return r

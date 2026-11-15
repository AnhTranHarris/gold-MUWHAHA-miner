"""R9 Micro180 V6: causal 180s executable-side first-passage cash prior.

Every anchor AND its whole evaluation horizon are in already COMPLETED real
1-second quote closes. This is not a learned forecast, AUC, true volume, or
a substitute for first-passage testing at ACTUAL candidate timestamps.

Non-overlapping 8-second starting anchors mitigate label overlap. The
uncertainty penalty is deliberately a heuristic, NOT a calibrated CI.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Optional
from statistics import mean

from coinexx_r9.models import Tick
from micro180 import RollingThreeMinute, Micro180R9
from v5_path_lifecycle import PathLifecycleV5, V5Spec


@dataclass(frozen=True)
class V6Spec:
    window_ms: int = 180_000
    horizon_seconds: int = 6
    stride_seconds: int = 8
    min_observations: int = 8
    uncertainty_scale: float = 1.0
    min_buy_cash_edge: float = -0.35
    min_sell_cash_edge: float = -0.35
    audit_only: bool = False
    enable_holding_utility: bool = False
    min_hold_increment: float = 0.0
    hold_horizon_seconds: int = 3

    def __post_init__(self):
        z=(self.uncertainty_scale,self.min_buy_cash_edge,
           self.min_sell_cash_edge,self.min_hold_increment)
        if (self.window_ms!=180_000 or self.horizon_seconds<2 or
            self.horizon_seconds>15 or self.stride_seconds<self.horizon_seconds or
            self.stride_seconds>30 or not 4<=self.min_observations<=30 or
            not 0<=self.uncertainty_scale<=5 or
            not 1<=self.hold_horizon_seconds<=10 or
            any(not isfinite(x) for x in z) or
            min(self.min_buy_cash_edge,self.min_sell_cash_edge)<-2 or
            max(self.min_buy_cash_edge,self.min_sell_cash_edge)>2 or
            not -.5<=self.min_hold_increment<=1.75):
            raise ValueError('Invalid V6 past-only first-passage controls')


@dataclass(frozen=True)
class HistoricalCashEvidence:
    side: int
    sample_count: int
    historical_mean_net: float
    penalized_net: float
    first_profit_fraction: float
    first_stop_fraction: float
    worst_net: float
    count_quote_gaps: int

    @property
    def sufficient(self)->bool:
        return self.sample_count>0


def _completed_second_path(r:RollingThreeMinute, now_ms:int)->list:
    # Never include the active second, even if its intra-second extrema are known.
    return r.closes(now_ms,180_000)


def _valid_path(q, i:int,j:int)->bool:
    if j>=len(q):return False
    return all(0 < q[k].start_ms-q[k-1].start_ms<=2_000 for k in range(i+1,j+1))


def _uncertainty(values:list[float],factor:float)->tuple[float,float]:
    m=sum(values)/len(values)
    if len(values)==1:return m,m
    var=sum((v-m)**2 for v in values)/(len(values)-1)
    return m,m-factor*sqrt(var/len(values))


def past_cash_first_passage(r:RollingThreeMinute,now_ms:int,side:int,
     *,cash_per_price_dollar:float=1.,extra_roundtrip_cost:float=.20,
     minimum_net:float=.10,adverse_net:float=-2.,
     spec:V6Spec=V6Spec())->HistoricalCashEvidence:
    """Past path estimate for executable BUY Ask→Bid / SELL Bid→Ask.

    For each non-overlapping historical anchor, follow historical COMPLETED
    second closes in source chronological order until the first cash barrier or
    the predeclared finite timeout. No output depends on current or future bars.
    """
    if side not in (-1,1):raise ValueError('side')
    if (cash_per_price_dollar<=0 or extra_roundtrip_cost<0 or
        minimum_net<0 or adverse_net>=0):raise ValueError('economics')
    q=_completed_second_path(r,now_ms)
    vals=[];hit_profit=0;hit_loss=0;gaps=0
    horizon=spec.horizon_seconds
    stride=spec.stride_seconds
    for i in range(0,len(q)-horizon,stride):
        end=i+horizon
        if not _valid_path(q,i,end):
            gaps+=1;continue
        entry=q[i].ask_close if side>0 else q[i].bid_close
        outcome=None
        for j in range(i+1,end+1):
            liquidation=q[j].bid_close if side>0 else q[j].ask_close
            net=side*(liquidation-entry)*cash_per_price_dollar/100.-extra_roundtrip_cost
            if net>=minimum_net:
                outcome=net;hit_profit+=1;break
            if net<=adverse_net:
                outcome=net;hit_loss+=1;break
            outcome=net
        vals.append(outcome)
    if not vals:
        return HistoricalCashEvidence(side,0,0.,float('-inf'),0.,0.,0.,gaps)
    mu,penalized=_uncertainty(vals,spec.uncertainty_scale)
    n=len(vals)
    return HistoricalCashEvidence(side,n,mu,penalized,
        hit_profit/n,hit_loss/n,min(vals),gaps)


def incremental_hold_prior(r:RollingThreeMinute,now_ms:int,side:int,
         *,cash_per_price_dollar:float=1.,spec:V6Spec=V6Spec())->Optional[float]:
    """Past-only USD change from *continuing* an existing liquidation quote.

    Entry spread and previous paid fee are intentionally NOT paid again.
    This estimate is unconditional on a current +$0.10 milestone and cannot
    be treated as a calibrated expected hold benefit.
    """
    q=_completed_second_path(r,now_ms)
    vals=[];h=spec.hold_horizon_seconds
    for i in range(0,len(q)-h,max(spec.stride_seconds,h)):
        if not _valid_path(q,i,i+h):continue
        a=q[i].bid_close if side>0 else q[i].ask_close
        b=q[i+h].bid_close if side>0 else q[i+h].ask_close
        vals.append(side*(b-a)*cash_per_price_dollar/100.)
    if len(vals)<spec.min_observations:return None
    return _uncertainty(vals,spec.uncertainty_scale)[1]


class PastOnlyCashMicroV6(PathLifecycleV5):
    """Preexisting 5s observation / 15s confirmation / 15s+30s permission
    PLUS independently assessed executable-side cash response priors.

    Prior calculations for BUY and SELL are performed before the proposed
    side is risk-admitted. The detector still requires a causal 5s candidate;
    never flip into an opposite trade that lacks structural permission.
    """

    def __init__(self,cfg,cash,micro_spec,*,v5:V5Spec=V5Spec(),
                 v6:V6Spec=V6Spec()):
        super().__init__(cfg,cash,micro_spec,v5=v5)
        self.v6=v6
        self._v6_sec=-1
        self._v6_prior={}

    def _past(self,t:Tick,side:int)->HistoricalCashEvidence:
        sec=t.time_msc//1000
        if sec!=self._v6_sec:
            self._v6_sec=sec;self._v6_prior={}
        if side not in self._v6_prior:
            self._v6_prior[side]=past_cash_first_passage(
                self.rolling,t.time_msc,side,cash_per_price_dollar=self.cash.k,
                extra_roundtrip_cost=self.cash.cost,
                minimum_net=self.micro_spec.min_net_cash,
                adverse_net=-self.micro_spec.hard_risk_cash,spec=self.v6)
        return self._v6_prior[side]

    def _open_trade(self,t:Tick,side:int):
        # Compute independent BUY and SELL evidence BEFORE selecting the
        # candidate's economic permission. No old upside/sell-label inversion.
        buy=self._past(t,+1)
        sell=self._past(t,-1)
        chosen=buy if side>0 else sell
        other=sell if side>0 else buy
        self.stats['v6_dual_action_evaluations']+=1
        if chosen.sample_count < self.v6.min_observations:
            self.stats['v6_sparse_prior']+=1
            if not self.v6.audit_only:return
        floor=self.v6.min_buy_cash_edge if side>0 else self.v6.min_sell_cash_edge
        if chosen.penalized_net<floor:
            self.stats['v6_negative_cash_prior']+=1
            if not self.v6.audit_only:return
        self._signal_meta.update({
            'v6_past_side':side,
            'v6_past_sample_count':chosen.sample_count,
            'v6_past_side_cash':round(chosen.penalized_net,5),
            'v6_past_opposite_cash':round(other.penalized_net,5),
            'v6_past_buy_cash':round(buy.penalized_net,5),
            'v6_past_sell_cash':round(sell.penalized_net,5),
            'v6_past_only_unconditional_proxy':True,
            'v6_audit_only':self.v6.audit_only,
        })
        super()._open_trade(t,side)

    def _manage_position(self,t:Tick):
        p=self.position
        if p is None:return
        if not self.v6.enable_holding_utility:
            return super()._manage_position(t)
        liq=t.bid_u if p.side>0 else t.ask_u
        net=p.side*(liq-p.entry_price_u)*self.cash.k/100.-self.cash.cost
        # Parent handles hard stop, gaps, timeout, account, cap *before* any
        # discretionary runner. Never defer it to a historical utility probe.
        if net>=self.micro_spec.min_net_cash and net<self.micro_spec.preferred_max_net_cash:
            utility=incremental_hold_prior(self.rolling,t.time_msc,p.side,
                          cash_per_price_dollar=self.cash.k,spec=self.v6)
            if utility is None or utility<=self.v6.min_hold_increment:
                # Respect mandatory forced-exit precedence: if any forced limit
                # has tripped, parent must close for that reason.
                age=t.time_msc-p.entry_time_msc
                if (net<=-self.micro_spec.hard_risk_cash or
                    age>=self.micro_spec.max_lifetime_ms or
                    self.rolling.last_gap_ms>self.micro_spec.max_quote_gap_ms or
                    (self.cash.governor and (self.account.day_lock or self.account.permanent_lock))):
                    return super()._manage_position(t)
                self._record_close(t,'v6_hold_no_positive_increment',liq)
                return
        return super()._manage_position(t)

    def report(self):
        r=super().report()
        r['v6_past_cash']={
            'status':'research_only_unvalidated_noncausal_classifier_absent',
            'past_only_complete_seconds':True,'millisecond_source_order':True,
            'separate_buy_sell_cash_estimates':True,
            'uncertainty_is_heuristic':True,
            'econ_gate_audit_only':self.v6.audit_only,
            'cash_prior_veto':int(self.stats['v6_negative_cash_prior']),
            'cash_prior_sparse':int(self.stats['v6_sparse_prior']),
            'dual_action_evaluations':int(self.stats['v6_dual_action_evaluations']),
            'holding_utility_enabled':self.v6.enable_holding_utility}
        return r

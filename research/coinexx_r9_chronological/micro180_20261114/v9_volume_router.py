"""Experimental V9: volume-preserving four-lane R9 entry + exact-ms Micro180 lifecycle.

Forks existing, source-verified GitHub R9 dual-basket and V8 micro180 source.
Uses the EXISTING original Coinexx data directly, never creates tick caches.
Quotes, not transaction prints; positive expectancy is not presumed.
"""
from __future__ import annotations
import math
from collections import Counter
from dataclasses import dataclass
from statistics import median
from typing import Optional

from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config
from on_policy_cash_replay import ResearchCash
from dual_basket import DualBasketMixin, DualBasketSpec
from micro180 import Micro180R9, Micro180Spec
from v5_ms_path import MsQuarterPath


@dataclass(frozen=True)
class V9Spec:
    entry_action: str = 'preserve_breakout'  # or optional isolated countertrend diagnostic
    entry_signal_mode: str = 'executable_or'  # price-side accurate BUY Bid/SELL Ask
    min_5s_span_ms: int = 1000
    min_15s_span_ms: int = 2500
    rearm_rule: str = 'either_new_basket'  # independent 5s OR 15s clock permits a NEW setup
    rearm_cooldown_ms: int = 1500  # research-only, separate from V8 frozen 3000ms
    exit_action: str = 'first_cash010'       # or optional protective early-adverse experimental arm
    adverse_cash_trigger: float = -.28
    adverse_min_hold_ms: int = 750
    adverse_efficiency_limit: float = -.55
    adverse_coherence_limit: float = .20
    override_side_score_margin: float = .65
    minimum_counterflow_score: float = .38

    def __post_init__(self):
        if (self.entry_signal_mode not in ('executable_or','mid_or_original')
                or not 0 <= self.min_5s_span_ms < 5000
                or not 0 <= self.min_15s_span_ms < 15000
                or not 500 <= self.rearm_cooldown_ms <= 3000
                or self.rearm_rule not in ('either_new_basket','both_new_baskets')
                or self.entry_action not in ('preserve_breakout','counterflow_if_exhausted','reverse_all_research')
                or self.exit_action not in ('first_cash010','early_path_defense')
                or not -1.99 < self.adverse_cash_trigger < 0
                or not 250 <= self.adverse_min_hold_ms <= 30000
                or not -1 <= self.adverse_efficiency_limit <= 0
                or not 0 <= self.adverse_coherence_limit <= 1
                or self.override_side_score_margin < 0
                or self.minimum_counterflow_score < 0):
            raise ValueError('Invalid experimental V9 volume/router specification')


@dataclass(frozen=True)
class DirectionalQuant:
    side: int
    usable: bool
    score: float
    executable_breakout_z15: float
    executable_breakout_z30: float
    efficiency_5s: float
    efficiency_15s: float
    efficiency_30s: float
    quote_250ms_efficiency: float
    quote_250ms_coherence: float
    spread_stress: float
    m1_direction_bias: Optional[float]
    reason: str = ''


def directional_quant(rolling, path:MsQuarterPath, t:Tick, side:int) -> DirectionalQuant:
    """Independent BUY Bid-exit and SELL Ask-cover scores on *current* quote.

    BUY B15= (Bid_t-max(Bid_prev_completed15))/sigma15; SELL B15=
    (min(Ask_prev_completed15)-Ask_t)/sigma15. No midpoint fill or true-volume claim.
    Sub-minute 250ms and 1s observations are original source-ms ordered, 180s
    bounded; source gaps => not usable, but observation-only default keeps throughput.
    Scores are deterministic engineering heuristics, NEVER probabilities.
    """
    if side not in (-1,1): raise ValueError('side must be BUY +1 or SELL -1')
    empty=DirectionalQuant(side,False,0.,0.,0.,0.,0.,0.,0.,0.,1.,None,'sparse history')
    q5=rolling.closes(t.time_msc,5000)
    q15=rolling.closes(t.time_msc,15000)
    q30=rolling.closes(t.time_msc,30000)
    if len(q5)<3 or len(q15)<9 or len(q30)<18: return empty
    if t.time_msc-q15[-1].last_ms>2500 or any(
        b.start_ms-a.start_ms>2000 for seq in (q5,q15,q30)
        for a,b in zip(seq,seq[1:])
    ):return empty
    exec_now=t.bid_u if side>0 else t.ask_u
    def closes(seq):return [b.bid_close if side>0 else b.ask_close for b in seq]
    def eff(seq):
        v=closes(seq)+[exec_now]
        travel=sum(abs(b-a) for a,b in zip(v,v[1:]))
        return max(-1.,min(1.,side*(v[-1]-v[0])/max(1.,travel)))
    q=closes(q15)
    delta=[b-a for a,b in zip(q,q[1:])]
    sigma=max(1.,math.sqrt(sum(d*d for d in delta)/max(1,len(delta))))
    p15=max(q) if side>0 else min(q)
    p30=max(closes(q30)) if side>0 else min(closes(q30))
    z15=side*(exec_now-p15)/sigma
    z30=side*(exec_now-p30)/sigma
    path5=path.signature(t.time_msc,side,window_ms=5000)
    ps=path5.efficiency if path5 else 0.
    pc=path5.coherence if path5 else 0.
    spreads=[b.spread_close for b in q15]
    stress=t.spread_points/max(1.,float(median(spreads)))
    bias=rolling.m1.bias(side)
    e5,e15,e30=eff(q5),eff(q15),eff(q30)
    # Independent coefficients deliberately *not* claimed trained or profitable.
    # Prior V7 high AUC/first-passage kernel did not discriminate candidates.
    if side>0:
        value=(.27*math.tanh(z15/3.)+.08*math.tanh(z30/3.)
               +.22*e5+.15*e15+.08*e30+.12*ps+.10*pc
               +.08*(bias or 0.)-.20*max(0.,stress-1.))
    else:
        value=(.22*math.tanh(z15/3.)+.12*math.tanh(z30/3.)
               +.18*e5+.18*e15+.10*e30+.12*ps+.08*pc
               +.10*(bias or 0.)-.24*max(0.,stress-1.))
    return DirectionalQuant(side,True,round(value,6),round(z15,5),round(z30,5),
           round(e5,5),round(e15,5),round(e30,5),round(ps,5),round(pc,5),
           round(stress,5),round(bias,5) if bias is not None else None,'observed quote')


class VolumePreservingMicroV9(DualBasketMixin,Micro180R9):
    """Existing four-lane OR router; no hard indicator veto in default version.

    V8 180s rolling geometry / cash risk / M1 indicator paths remain inherited.
    A frozen 1.5s research cooldown spans basket and minute boundaries.
    Every completed position is on-policy, not a frozen future-label replay.
    """
    def __init__(self,cfg:R9Config,cash:ResearchCash,
                 v9:V9Spec=V9Spec(),dual:DualBasketSpec=DualBasketSpec(),
                 micro:Micro180Spec=Micro180Spec()):
        if micro.experimental_runner:
            raise ValueError('V9 cash exit experiment is not a validated runner')
        super().__init__(cfg,cash,micro,dual_spec=dual)
        self.v9=v9
        self.path=MsQuarterPath()
        self.v9_stats=Counter()

    def _push_second(self,t:Tick):
        super()._push_second(t)
        self.path.update(t)

    def _volume_rearm_ready(self,t:Tick)->bool:
        if self._last_exit_ms is None:return True
        if t.time_msc-self._last_exit_ms<self.v9.rearm_cooldown_ms:return False
        new5=self.rolling.current[5000].start_ms!=self._last_closed_basket
        new15=self.rolling.current[15000].start_ms!=self._last_closed_15s_basket
        return (new5 or new15) if self.v9.rearm_rule=='either_new_basket' else (new5 and new15)

    def _start_minute_cycle(self,t:Tick):
        prior=self._entry_minute
        super()._start_minute_cycle(t)
        if self._entry_minute!=prior:
            # Two inherited routers each track a cap; reset both in lockstep.
            self._entries_this_minute=0
        if not self._volume_rearm_ready(t):
            self.pending_mode=0
            self.v9_stats['cooldown_rejection_ticks']+=1
        if self._entries_this_minute>=self.micro_spec.max_entries_per_source_minute:
            self.pending_mode=0

    def _arm_opposite_after_exit(self):
        super()._arm_opposite_after_exit()
        if self._last_exit_ms is not None and self.rolling.previous_msc is not None:
            if (self.rolling.previous_msc-self._last_exit_ms<self.v9.rearm_cooldown_ms
                    or (self.rolling.current[5000].start_ms==self._last_closed_basket
                        and self.rolling.current[15000].start_ms==self._last_closed_15s_basket)
                    or (self.v9.rearm_rule=='both_new_baskets' and
                        (self.rolling.current[5000].start_ms==self._last_closed_basket
                         or self.rolling.current[15000].start_ms==self._last_closed_15s_basket))):
                self.pending_mode=0

    def _process_entries(self,t:Tick):
        if self.v9.entry_signal_mode=='mid_or_original':
            return super()._process_entries(t)
        if self.pending_mode==0 or self._entries_in_minute>=self._cap():return
        if self.cash.governor and (self.account.day_lock or self.account.permanent_lock):
            self.v9_stats['governor_blocks_entry']+=1;return
        if not self._gate(t):return
        if self.rolling.last_gap_ms>self.micro_spec.max_quote_gap_ms:
            self.v9_stats['quote_gap_veto']+=1;return
        levels15,levels30=self.rolling.price_levels(
            t.time_msc,self.dual_spec.minimum_completed_15s,
            self.dual_spec.minimum_completed_30s,
            self.dual_spec.max_completed_second_age*1000+999)
        if levels15 is None or levels30 is None:
            self.v9_stats['missing_completed_seconds']+=1;return
        # Only SOURCE-OBSERVED completed Bid and Ask second closes are levels.
        vote={1:[],-1:[]}
        for width,bar,threshold in (
            (5,self.rolling.current[5000],self.v9.min_5s_span_ms),
            (15,self.rolling.current[15000],self.v9.min_15s_span_ms),
        ):
            if bar.last_ms-bar.first_ms<threshold or bar.max_gap_ms>self.micro_spec.max_quote_gap_ms:
                continue
            displacement=bar.bid_close+bar.ask_close-bar.bid_open-bar.ask_open
            for bwidth,levels in ((15,levels15),(30,levels30)):
                lane=f'{width}s_basket_{bwidth}s_breakout'
                # BUY: Bid must clear historic completed Bid close; SELL: Ask
                # must clear historic completed Ask close. No midquote fills.
                if (self.pending_mode in (1,2)
                    and displacement>=2*self.dual_spec.minimum_mid_displacement_cents
                    and t.bid_u>=levels[0]+self.dual_spec.breakout_extra_cents):
                    vote[1].append(lane)
                if (self.pending_mode in (-1,2)
                    and displacement<=-2*self.dual_spec.minimum_mid_displacement_cents
                    and t.ask_u<=levels[1]-self.dual_spec.breakout_extra_cents):
                    vote[-1].append(lane)
        if vote[1] and vote[-1]:
            self.v9_stats['conflicting_quote_votes']+=1;return
        side=1 if vote[1] else -1 if vote[-1] else 0
        if not side:
            self.v9_stats['no_executable_breakout']+=1;return
        if not self._quality(side):
            self.v9_stats['s1_veto']+=1;return
        self._qualifying_lanes=tuple(vote[side])
        try:self._open_trade(t,side)
        finally:self._qualifying_lanes=()

    def _open_trade(self,t:Tick,side:int):
        if self._entries_in_minute>=self._cap() or self._entries_this_minute>=self.micro_spec.max_entries_per_source_minute:
            self.v9_stats['cap_block']+=1;return
        buy=directional_quant(self.rolling,self.path,t,1)
        sell=directional_quant(self.rolling,self.path,t,-1)
        before=side
        # Default never blocks a previously permitted four-lane OR entry.
        if self.v9.entry_action=='reverse_all_research':
            side=-side
        elif self.v9.entry_action=='counterflow_if_exhausted':
            primary=buy if side>0 else sell
            counter=sell if side>0 else buy
            if (primary.usable and counter.usable
                    and counter.score>=self.v9.minimum_counterflow_score
                    and counter.score-primary.score>=self.v9.override_side_score_margin
                    and counter.quote_250ms_efficiency>.30):
                side=-side
        if side!=before:self.v9_stats['reversed_side']+=1
        self._signal_meta={
            'v9_router':'dual_or_5_15_and_15_30',
            'v9_original_side':before,'v9_actual_side':side,
            'v9_buy_score':buy.score if buy.usable else 'missing',
            'v9_sell_score':sell.score if sell.usable else 'missing',
            'v9_buy_z15':buy.executable_breakout_z15,
            'v9_sell_z15':sell.executable_breakout_z15,
            'v9_buy_m1_bias':buy.m1_direction_bias,
            'v9_sell_m1_bias':sell.m1_direction_bias,
            'v9_indicator_source':'m1_wilder_quote' if buy.m1_direction_bias is not None else '180s_quote_proxy',
        }
        self.v9_stats['entry_indicator_usable' if buy.usable and sell.usable else 'entry_indicator_sparse']+=1
        super()._open_trade(t,side)

    def _manage_position(self,t:Tick):
        p=self.position
        if p is not None and self.v9.exit_action=='early_path_defense':
            age=t.time_msc-p.entry_time_msc
            liq=t.bid_u if p.side>0 else t.ask_u
            net=p.side*(liq-p.entry_price_u)*self.cash.k/100.0-self.cash.cost
            if (self.v9.adverse_min_hold_ms<=age<self.micro_spec.max_lifetime_ms
                    and -self.micro_spec.hard_risk_cash<net<=self.v9.adverse_cash_trigger):
                observed=self.path.signature(t.time_msc,p.side,window_ms=1500)
                if (observed is not None
                        and observed.efficiency<=self.v9.adverse_efficiency_limit
                        and observed.coherence<=self.v9.adverse_coherence_limit):
                    self.v9_stats['defensive_exit']+=1
                    self._record_close(t,'v9_ms_path_defense',liq)
                    return
        super()._manage_position(t)

    def report(self):
        r=super().report()
        r['v9']={
            'source_exact_ms_quote_engine':True,
            'rolling_three_minutes':True,'original_dual_or_gate':self.v9.entry_signal_mode=='mid_or_original',
            'entry_signal_mode':self.v9.entry_signal_mode,
            'indicator_gate_is_shadow':True,
            'not_true_transaction_volume':True,
            'native_MQL5_parity_certified':False,
            'entry_action':self.v9.entry_action,
            'rearm_cooldown_ms':self.v9.rearm_cooldown_ms,
            'rearm_rule':self.v9.rearm_rule,
            'exit_action':self.v9.exit_action,
            'quant_buy_sell_asymmetric':True,
            'counters':dict(self.v9_stats),
            'dual_entry_count':self._entries_in_minute,
            'risk_gov_enabled':self.cash.governor,
        }
        return r

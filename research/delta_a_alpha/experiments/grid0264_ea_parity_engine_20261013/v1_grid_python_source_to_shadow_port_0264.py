"""GRID0264 — genuinely cumulative source -> causal shadow-funding research runner.

NOT live MT5, NOT full Vertical L1-L7. For the ONLY future production side,
use VerifiedMT5PositionLedger0264 + PaidSourcePositionBridge0264 with MT5
HistoryDeal evidence rather than this model's hypothetical fills.

This runner closes the old disconnected G0 / quote-funding research pipeline.
It does not invent missing H4/H1/M15/M5 permissions, source signatures,
execution fills, protective broker ACKs, trades from overfit hindsight, or
Coinexx broker specifications. Non-white-listed sources are rejected.
"""
from __future__ import annotations
from dataclasses import dataclass
from collections import Counter
from types import SimpleNamespace
from v1_grid_cumulative_source_adapter_0264 import CumulativeCreatorAdapter
from v1_grid_funded_quote_gate_0262_hardened import (HardenedBrokerPhysics,StrictExecutionQuote)
from v1_grid_observed_lifecycle_0262_hardened import HardenedExitPolicy
from v1_grid_ea_parity_shadow_risk_0264 import CostReservedObservedFundingEngine0264
from v1_grid_funded_quote_gate_0259 import ResearchIntent

@dataclass(frozen=True)
class SourceLifecyclePolicy:
    source: str
    stop_distance_raw:int
    max_hold_ms:int
    min_latency_ms:int=250
    ttl_ms:int=2000
    profit_target_raw:int|None=None
    trail_arm_raw:int|None=None
    trail_distance_raw:int|None=None
    def __post_init__(self):
        if (not self.source or self.stop_distance_raw<=0 or self.max_hold_ms<=0
                or self.min_latency_ms<1 or self.ttl_ms<self.min_latency_ms):
            raise ValueError('explicit strictly causal bounded lifecycle required')
        if ((self.profit_target_raw is not None and self.profit_target_raw<=0)
            or (self.trail_arm_raw is None)!=(self.trail_distance_raw is None)
            or (self.trail_arm_raw is not None and (self.trail_arm_raw<0 or self.trail_distance_raw<=0))):
            raise ValueError('invalid target or trailing policy')

class Grid0264ResearchRuntime:
    """One observed original quote, one cumulative G0, one SHADOW account.

    Caller supplies H1/M5 already-completed states, as-of confirmed trading
    permission (or *explicit* hypothetical research permission), session
    geometry, and predeclared lifecycle policies. This deliberately exposes
    missing inputs rather than fabricating unavailable multi-HTF states.
    """
    def __init__(self, *, physics:HardenedBrokerPhysics, starting_cash_usd:float,
                 policies:tuple[SourceLifecyclePolicy,...],
                 source_adapter:CumulativeCreatorAdapter|None=None,
                 max_positions:int=16):
        if not policies or len({x.source for x in policies})!=len(policies):
            raise ValueError('all selected source types require a unique lifecycle')
        if physics.specs_broker_verified:
            raise ValueError('research runtime may not assert verified external MT5 contract')
        self.sources=source_adapter if source_adapter is not None else CumulativeCreatorAdapter()
        self.funding=CostReservedObservedFundingEngine0264(starting_cash_usd=starting_cash_usd,
                   physics=physics,max_shared_positions=max_positions,
                   exit_policies=tuple(HardenedExitPolicy(p.source,
                          arm_raw=p.trail_arm_raw if p.trail_arm_raw is not None else 10**12,
                          trail_raw=p.trail_distance_raw if p.trail_distance_raw is not None else 10**12,
                          profit_target_raw=p.profit_target_raw) for p in policies))
        self.policies={x.source:x for x in policies}
        self.counts=Counter()
        self.last_ms=None
        self.last_settlements=()
    def on_original_tick(self,*,time_ms:int,bid_raw:int,ask_raw:int,
                         h1_completed,m5_completed,geometry:str,
                         hypothetical_research_tradable:bool,
                         completed_grid_signs=(None,None,None,None),
                         completed_m5_tr_raw=None,m5_tr_asof_ms=None):
        if type(hypothetical_research_tradable) is not bool:
            raise TypeError('explicit strictly hypothetical tradability bool required')
        if not geometry:raise ValueError('observed session geometry required')
        if self.last_ms is not None and time_ms<self.last_ms:
            raise ValueError('out of order original source quote')
        # Source and funding share the SAME chronology. Settle old funded
        # shadow positions before new source proposals; same-tick filling
        # prohibited by positive latency and hardened execution gate.
        q=StrictExecutionQuote(time_ms,bid_raw,ask_raw,hypothetical_research_tradable)
        closed=self.funding.on_observed_quote(q)
        self.last_settlements=closed
        raw=SimpleNamespace(time_ms_utc=time_ms,bid_raw=bid_raw,ask_raw=ask_raw)
        candidates=self.sources.on_tick(raw,h1_completed,geometry,
                    last_completed_m5=m5_completed,
                    broker_tradable=hypothetical_research_tradable,
                    completed_grid_signs=completed_grid_signs,
                    completed_m5_tr_raw=completed_m5_tr_raw,
                    m5_tr_asof_ms=m5_tr_asof_ms)
        self.last_ms=time_ms
        self.counts['ticks']+=1
        self.counts['source_events']+=len(candidates)
        for item in candidates:
            if item.side not in (-1,1):
                self.counts['unsigned_quarantined']+=1;continue
            policy=self.policies.get(item.source)
            if policy is None:
                self.counts['unconfigured_quality_or_lifecycle']+=1;continue
            if not hypothetical_research_tradable or item.available_ms!=time_ms:
                self.counts['nonexecutable_or_stale_source']+=1;continue
            uid=f'{item.available_ms}:{item.time_ms}:{item.source}:{item.side}:{item.rung}:{item.crossing_level_usd}'
            intent=ResearchIntent(uid,item.source,time_ms,item.side,
                      policy.stop_distance_raw,policy.max_hold_ms,
                      min_latency_ms=policy.min_latency_ms,
                      ttl_ms=policy.ttl_ms)
            try:
                self.funding.offer(intent)
                self.counts['accepted_for_next_observed_quote']+=1
            except ValueError:
                self.counts['invalid_or_duplicate_intent']+=1
        return {'sources':candidates,'shadow_closed':closed,
                'cumulative_source_ack_fills':self.sources.router.funded.counts['ack_fills'],
                'shadow_cash':self.funding.cash}
    def summary(self):
        return {'execution':'CAUSAL_DUKASCOPY_OBSERVATIONS_HYPOTHETICAL_SHADOW_ONLY',
                'counters':dict(self.counts),'shadow':self.funding.summary(),
                'G0_stats':self.sources.stats(),
                'MT5_broker_fills_claimed':0,
                'full_vertical_certified':False,
                'broker_clock_verified':False}

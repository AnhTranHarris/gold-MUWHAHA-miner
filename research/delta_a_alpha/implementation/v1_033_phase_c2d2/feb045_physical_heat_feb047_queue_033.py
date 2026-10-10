"""DAA033 C2D3-H: source-native FEB045 account heat and FEB047 queued profit protection.

AUTHORITIES, READ AS WHOLE:
  FEB045_UNIFIED_HEAT_GRID_RESEARCH_BUNDLE.zip/FEB045/heat_engine.py
  FEB045_UNIFIED_HEAT_GRID_RESEARCH_BUNDLE.zip/FEB045/engine_statecaps.py
  FEB047_PORTFOLIO_REPAIR_RESEARCH_BUNDLE.zip/FEB047/queued_reduce_only_047.py
  FEB047_PORTFOLIO_REPAIR_RESEARCH_BUNDLE.zip/FEB047/FEB047_STRICT_BEST.json
Original FEB047 accepts a frozen source ledger; this module deliberately does NOT.
Every decision re-reads one genuine physically funded FundedEngine portfolio.
February-fitted source rules are available on any observed matching market state;
no calendar month selector, outcome tape, future tick, DCA or loss-sized position.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from math import isfinite
from typing import Iterable

from v1_funded_core_033c import Quote, Proposal, Position, Close, Structure, FundedEngine
from feb045_source_native_context_033 import FEB045NativeQualityL3


def original_feb_source(obj: Proposal | Position) -> int | None:
    if obj.layer != 'L3' or not obj.source.startswith('ORIGINAL_F045_S'):
        return None
    part = obj.source[len('ORIGINAL_F045_S'):]
    return int(part) if part.isdecimal() else None


@dataclass(frozen=True)
class PhysicalHeatConfig045:
    shock_usd: float = 0.0
    heat_global_usd: float = 1e12
    heat_s22_usd: float = 1e12
    heat_s25_usd: float = 1e12
    heat_s27_usd: float = 1e12
    source_maxopen_extra: int = 4096
    same_source_min_gap_usd: float = 0.0
    source_cooldown_ms: int = 0

    def __post_init__(self):
        vals=(self.shock_usd,self.heat_global_usd,self.heat_s22_usd,
              self.heat_s25_usd,self.heat_s27_usd,self.same_source_min_gap_usd)
        if not all(isfinite(x) and x >= 0 for x in vals):
            raise ValueError('Finite, nonnegative source heat and shock required')
        if self.source_maxopen_extra < 1 or self.source_cooldown_ms < 0:
            raise ValueError('Bad FEB045 original source physical capacity')


class FEB045PhysicalHeatL3:
    """Add FEB045 source-heat checks to already-source-filtered FEB045 L3 offers.

    quote-side long/down and short/up stresses are separate: account heat is
    max(stressed long, stressed short), not their sum. Source-own heat is the
    sum of nonnegative two-sided sourced floats as in ORIGINAL engine_statecaps.
    Prior source price/time update ONLY on a genuine on_funded_entry callback.
    """
    def __init__(self, upstream: FEB045NativeQualityL3, config: PhysicalHeatConfig045 | None=None):
        self.upstream=upstream
        self.config=config or PhysicalHeatConfig045()
        self.last_actual_entry: dict[tuple[int,int], tuple[int,int]] = {}
        self.denials: dict[str,int] = {}
        self.source_proposals = 0

    def on_market_quote(self, q: Quote, engine: FundedEngine) -> None:
        self.upstream.on_market_quote(q,engine)

    def _reject(self, label: str) -> None:
        self.denials[label]=self.denials.get(label,0)+1

    def propose(self,q:Quote,s:Structure,engine:FundedEngine)->Iterable[Proposal]:
        c=self.config; proposals=[]
        for p in self.upstream.propose(q,s,engine):
            src=original_feb_source(p)
            if src is None:
                proposals.append(p);continue
            self.source_proposals+=1
            existing=list(engine.positions.values())
            longs=[x for x in existing if x.side==1]
            shorts=[x for x in existing if x.side==-1]
            shock=c.shock_usd * 1000
            one=engine.one_oz_size
            # Original FEB045 long/down and short/up stressed price-side marks.
            stressed_l=max(0.,sum(x.entry_raw-(q.bid_raw-shock) for x in longs)/1000*one)
            stressed_s=max(0.,sum((q.ask_raw+shock)-x.entry_raw for x in shorts)/1000*one)
            if max(stressed_l,stressed_s)>=c.heat_global_usd:
                self._reject('FEB045_ACCOUNT_DIRECTIONAL_STRESS');continue
            source=[x for x in existing if original_feb_source(x)==src]
            sl=[x for x in source if x.side==1]
            ss=[x for x in source if x.side==-1]
            source_stress=(max(0.,sum(x.entry_raw-(q.bid_raw-shock) for x in sl)/1000*one)
                   +max(0.,sum((q.ask_raw+shock)-x.entry_raw for x in ss)/1000*one))
            limit={22:c.heat_s22_usd,25:c.heat_s25_usd,27:c.heat_s27_usd}.get(src,1e12)
            if source_stress>=limit:
                self._reject('FEB045_SOURCE_PHYSICAL_STRESS');continue
            if len(source)>=c.source_maxopen_extra:
                self._reject('FEB045_SOURCE_EXTRA_PHYSICAL_CAP');continue
            last=self.last_actual_entry.get((src,p.side))
            if last is not None:
                previous_raw,previous_ms=last
                current_raw=q.ask_raw if p.side==1 else q.bid_raw
                if (c.same_source_min_gap_usd>0 and
                    abs(current_raw-previous_raw)<c.same_source_min_gap_usd*1000):
                    self._reject('FEB045_SAME_SOURCE_FUNDED_PRICE_GAP');continue
                if (c.source_cooldown_ms>0 and
                    q.time_ms-previous_ms<c.source_cooldown_ms):
                    self._reject('FEB045_SAME_SOURCE_FUNDED_COOLDOWN');continue
            proposals.append(p)
        return tuple(proposals)

    def on_funded_entry(self,pos:Position,q:Quote,s:Structure,engine:FundedEngine)->None:
        src=original_feb_source(pos)
        if src is not None:
            self.last_actual_entry[(src,pos.side)]=(pos.entry_raw,q.time_ms)
        cb=getattr(self.upstream,'on_funded_entry',None)
        if cb is not None:cb(pos,q,s,engine)

    def on_funded_close(self, close:Close, engine:FundedEngine)->None:
        self.upstream.on_funded_close(close,engine)


@dataclass(frozen=True)
class StrictQueue047:
    # Exact selected FEB047_STRICT_BEST.json, all numerics frozen from original source.
    retreat_usd: float=2.0
    window_samples: int=36
    min_profit_usd: float=7.0
    close_batch: int=32
    cooldown_seconds: float=60.0
    side_limit: int=400
    source_only: bool=True
    require_dd_usd: float=0.0

    def __post_init__(self):
        if (self.retreat_usd<=0 or not isfinite(self.retreat_usd)
            or self.window_samples<1 or self.window_samples>96
            or self.min_profit_usd<0 or not isfinite(self.min_profit_usd)
            or self.close_batch<1 or self.cooldown_seconds<0
            or self.side_limit<1 or self.require_dd_usd<0):
            raise ValueError('Bad FEB047 frozen strict queue settings')


class FEB047QueuedProfitReduceL7:
    """5s observed-quote signal; one reduce request per tick through shared L7.

    The *engine* owns the physical queue, executes under combined rate and
    performs a second profit check at the final executable Bid/Ask quote.
    Call this adapter with the SAME FundedEngine as all source owners.
    """
    def __init__(self, config:StrictQueue047|None=None):
        self.config=config or StrictQueue047()
        self._last_time=-1
        self._bucket=None
        self._samples:deque[float]=deque(maxlen=self.config.window_samples)
        self._peak_monitor_equity:float|None=None
        self._last_action_ms=-10**15
        self._pending=0
        self._side=0
        self._awaiting:set[int]=set()
        self.actions=0
        self.early_actual_exits=0
        self.actual_net_of_early_exits=0.0
        self.guard_cancellations=0
        self.clock_observations=0

    def on_market_quote(self,q:Quote,engine:FundedEngine)->None:
        if q.time_ms<self._last_time:raise ValueError('Out-of-order FEB047 quote')
        self._last_time=q.time_ms
        if (engine.limits.max_orders_per_tick != 1 or
            engine.limits.max_orders_per_second > 10):
            raise ValueError('Original strict FEB047 requires shared <=1/tick and <=10/sec L7 order budget')
        bucket=q.time_ms//5000
        observe=(bucket!=self._bucket)
        self._bucket=bucket
        longs=sum(x.side==1 for x in engine.positions.values())
        shorts=len(engine.positions)-longs
        dominant=1 if longs>=shorts else -1
        if observe:
            self.clock_observations+=1
            mid=(q.ask_raw+q.bid_raw)/2000
            self._samples.append(mid)
            balance=engine.balance
            equity=balance+sum(engine._mark(x,q)-engine.limits.commission_roundtrip_usd/2
                               for x in engine.positions.values())
            self._peak_monitor_equity=max(self._peak_monitor_equity or equity,equity)
            dd=self._peak_monitor_equity-equity
            extreme=(max(self._samples)-mid if dominant==1 else mid-min(self._samples))
            c=self.config
            if (self._pending==0 and extreme>=c.retreat_usd
                and max(longs,shorts)>=c.side_limit
                and q.time_ms-self._last_action_ms>=c.cooldown_seconds*1000
                and dd>=c.require_dd_usd):
                self._side=dominant
                self._pending=min(c.close_batch,int(max(longs,shorts)*.25))
                if self._pending:
                    self._last_action_ms=q.time_ms
                    self.actions+=1
        if self._pending<=0:return
        if self._awaiting:
            # A previously requested close is pending L7 rate execution. Do not
            # submit a second physical close before the first has settled.
            dropped={pid for pid in self._awaiting
                     if pid not in engine.positions or
                     pid not in engine._profit_reduce_guards}
            if dropped:
                self._awaiting.difference_update(dropped)
                self.guard_cancellations+=sum(pid in engine.positions for pid in dropped)
            if self._awaiting:return
        for pid,p in engine.positions.items():
            if p.side!=self._side:continue
            if self.config.source_only and original_feb_source(p) not in (22,25):continue
            net=engine._mark(p,q)-engine.limits.commission_roundtrip_usd
            if net+1e-9<self.config.min_profit_usd:continue
            engine.request_profit_reduce(pid,minimum_net_usd=self.config.min_profit_usd)
            self._awaiting.add(pid)
            return
        self._pending=0

    def on_funded_close(self,close:Close,engine:FundedEngine)->None:
        if close.position_id in self._awaiting:
            self._awaiting.discard(close.position_id)
            if close.reason=='FEB047_PROFIT_REDUCE':
                assert close.net_usd+1e-9>=self.config.min_profit_usd
                self.early_actual_exits+=1
                self.actual_net_of_early_exits+=close.net_usd
                self._pending=max(0,self._pending-1)
            else:
                # Regular SL/TP/TTL supersedes a queued profit request.
                self._pending=0

    def propose(self,q:Quote,s:Structure,engine:FundedEngine)->Iterable[Proposal]:
        return ()
"""GRID0264: EA-portable, fail-closed G0 adapter to the *cumulative* source router.

No physical fills. Produces one chronology-qualified old-funnel-compatible
GridOpportunity per UTC millisecond from the actual GRID0246-0258 source router.
The raw non-directional April136B auction event is never guessed into BUY/SELL.
Broker permission is explicit. Delayed events are available only now, not then.
"""
from __future__ import annotations
from collections import Counter, deque
from dataclasses import dataclass
import math

from v1_grid_strategy_source_router import GridStrategySourceRouter
from v1_grid_h4_retest_0253 import FinishedH4Rung
from v1_grid_h4_second_acceptance_0254 import H4AsOfBoundary

H4_MS=14_400_000
M1_MS=60_000
SCALE=1000

@dataclass(frozen=True)
class EACompatibleSource:
    time_ms:int
    available_ms:int
    side:int
    source:str
    rung:int
    crossing_level_usd:float
    original_bid_raw:int
    original_ask_raw:int
    paid_proposal_id:int|None=None
    research_horizon_ms:int|None=None

class CompletedM1H4Observations:
    """Source-neutral completed-bar M1/H4 feed; no forged missing bars."""
    def __init__(self):
        self.last_ms=None
        self.m1_bucket=None
        self.m1_close=None
        self.prior_m1_close=None
        self.h4_bucket=None
        self.h4_high=self.h4_low=self.h4_close=None
        self.h4_completed=deque(maxlen=48)
        self.h4_last_close=None

    def observe(self, q):
        ms,bid,ask=q.time_ms_utc,q.bid_raw,q.ask_raw
        if not (isinstance(ms,int) and isinstance(bid,int) and isinstance(ask,int)):
            raise TypeError('integer UTC milliseconds and original raw quotes required')
        if ms<0 or bid<=0 or ask<bid or (self.last_ms is not None and ms<self.last_ms):
            raise ValueError('malformed or out-of-order original quote')
        self.last_ms=ms
        h4=ms//H4_MS
        if self.h4_bucket is None:
            self.h4_bucket=h4;self.h4_high=self.h4_low=self.h4_close=bid
        elif h4>self.h4_bucket:
            h,l,c=self.h4_high,self.h4_low,self.h4_close
            tr=max(h-l,abs(h-self.h4_last_close),abs(l-self.h4_last_close)) if self.h4_last_close is not None else h-l
            self.h4_completed.append((self.h4_bucket*H4_MS,(self.h4_bucket+1)*H4_MS,h,l,c,tr))
            self.h4_last_close=c
            self.h4_bucket=h4;self.h4_high=self.h4_low=self.h4_close=bid
        else:
            self.h4_high=max(self.h4_high,bid)
            self.h4_low=min(self.h4_low,bid)
            self.h4_close=bid
        m1=ms//M1_MS
        finished=None
        if self.m1_bucket is None:
            self.m1_bucket=m1;self.m1_close=bid
        elif m1>self.m1_bucket:
            end=(self.m1_bucket+1)*M1_MS
            finished=(end,self.prior_m1_close,self.m1_close)
            self.prior_m1_close=self.m1_close
            self.m1_bucket=m1;self.m1_close=bid
        else:
            self.m1_close=bid
        if finished is None or finished[0]>ms:return None
        # Six and fourteen genuinely completed H4 candles; do not fake gaps.
        end,prior,close=finished
        past=[x for x in self.h4_completed if x[1]<=((end-1)//H4_MS)*H4_MS]
        if len(past)<14:return None
        last14=past[-14:]
        if any(b[1]!=a[1]+H4_MS for a,b in zip(last14,last14[1:])):return None
        atr=max(1,int(round(sum(x[5] for x in last14)/14)))
        top=max(x[2] for x in past[-6:]);bottom=min(x[3] for x in past[-6:])
        trratio=past[-1][5]/atr
        owner_start=((end-1)//H4_MS)*H4_MS
        if past[-1][1]>owner_start:raise AssertionError('future H4 reference')
        return (end,prior,close,
            FinishedH4Rung(owner_start,top,bottom,atr,trratio),
            H4AsOfBoundary(owner_start,top,bottom,atr,trratio))

class CumulativeCreatorAdapter:
    """Preserves legacy .on_tick/.stats API while using current cumulative G0."""
    def __init__(self,router=None, *, max_delayed_ms=2_000):
        if max_delayed_ms<0:raise ValueError('negative candidate TTL')
        self.router=router if router is not None else GridStrategySourceRouter()
        self.bars=CompletedM1H4Observations()
        self.max_delayed_ms=max_delayed_ms
        self.last_release_ms=None
        self.counts=Counter()

    def on_tick(self,q,last_completed_h1,session_geometry,*,last_completed_m5=None,
                last_completed_h4=None,broker_tradable=False,
                completed_grid_signs=None,completed_m5_tr_raw=None,m5_tr_asof_ms=None):
        if type(broker_tradable) is not bool:raise TypeError('explicit broker permission')
        observed=self.bars.observe(q)
        if observed is not None:
            end,prior,close,h4,h4_second=observed
            # Each callback requires observed completed minutes and H4 state.
            if prior is not None:
                self.router.on_completed_m1(end_ms=end,prev_close_raw=prior,close_raw=close,h4=h4)
            self.router.on_completed_m1_second(end_ms=end,close_raw=close,h4=h4_second)
        opts=self.router.on_tick(q,last_completed_h1,session_geometry,
           m5=last_completed_m5,broker_tradable=broker_tradable,
           completed_grid_signs=completed_grid_signs,
           completed_m5_tr_raw=completed_m5_tr_raw,m5_tr_asof_ms=m5_tr_asof_ms)
        results=[]
        for c in opts:
            available=q.time_ms_utc if c.available_ms is None else c.available_ms
            if c.side not in (-1,1):
                self.counts['unsigned_auction_quarantined']+=1;continue
            if c.time_ms>q.time_ms_utc or available!=q.time_ms_utc:
                raise AssertionError('backdated/future source availability')
            if q.time_ms_utc-c.time_ms>self.max_delayed_ms:
                self.counts['stale_source_quarantined']+=1;continue
            if c.bid_raw<=0 or c.ask_raw<c.bid_raw or c.level_raw<=0:
                raise ValueError('invalid source quote or price')
            if not broker_tradable:
                self.counts['not_executable']+=1;continue
            if self.last_release_ms==q.time_ms_utc:
                self.counts['same_ms_quarantined']+=1;continue
            self.last_release_ms=q.time_ms_utc
            results.append(EACompatibleSource(c.time_ms,available,c.side,c.source,c.rung,
                c.level_raw/SCALE,c.bid_raw,c.ask_raw,c.paid_proposal_id,c.research_horizon_ms))
            self.counts['released']+=1
            break
        return tuple(results)

    def stats(self):
        return dict(stage='G0_CURRENT_CUMULATIVE_SOURCE_ROUTER_NO_PHYSICAL_FILLS',
                    adapter_counters=dict(self.counts),current_router=self.router.stats(),
                    finished_h4=self.bars.h4_completed.__len__())

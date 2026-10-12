"""Delta-A-alpha G0 grid prototype: exact creator parent plus finer M5 first-touch lattice.

Research-only pre-L1 opportunity generation. Imports the existing, unchanged
CreatorGridGenesis (not a new replacement strategy). The output has the exact
GridOpportunity contract consumed by FourSessionV1. Never allocates positions,
lot sizes, cash, MT5 orders, margin or outcomes. The existing L1-L7 engine keeps
sole authority for physical qualification and execution.

Micro geometry is a *research hypothesis*: NOT an empirically profitable setting.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Optional
from v1_creator_grid_genesis import CreatorGridGenesis, GridOpportunity

SCALE=1000

@dataclass(frozen=True)
class MicroGridSettings:
    min_gap_usd: float = 0.35
    quoted_spread_multiple: float = 1.35
    completed_m5_range_fraction: float = 0.075
    maximum_gap_usd: float = 12.0
    maximum_quote_gap_ms: int = 60_000
    maximum_distinct_levels_per_bar: int = 100

    def __post_init__(self):
        if min(self.min_gap_usd,self.quoted_spread_multiple,
               self.completed_m5_range_fraction,self.maximum_gap_usd,
               self.maximum_quote_gap_ms,self.maximum_distinct_levels_per_bar)<=0:
            raise ValueError('invalid microgrid geometry')
        if self.min_gap_usd>self.maximum_gap_usd:
            raise ValueError('minimum gap larger than maximum gap')

class GridReadyPrototype:
    """Drop-in on_tick interface for the existing FourSessionV1 generator.

    One primary grid event PER observed tick even on large price jumps. Within
    one *completed* M5 epoch, each rung and side may fire only once; later
    retracements can update research state but cannot manufacture more tickets.
    Micro candidates are price-location hypotheses, not automatic BUY/SELL.
    """
    def __init__(self, settings: MicroGridSettings|None=None, *, parent=None):
        self.settings=settings or MicroGridSettings()
        self.parent=parent if parent is not None else CreatorGridGenesis()
        self.last_ms:Optional[int]=None
        self.prev_ask:Optional[float]=None
        self.completed_m5_start:Optional[int]=None
        self.anchor:Optional[float]=None
        self.micro_gap:Optional[float]=None
        self.geometry:Optional[str]=None
        self.seen:set[tuple[int,int]]=set()
        self.micro_events=0
        self.parent_events_forwarded=0
        self.duplicate_rung_rejections=0
        self.skipped_levels=0
        self.stale_resets=0
        self.unaffordable_quotes=0
        self.handoff_events=0

    @property
    def ready(self)->bool:
        return bool(self.parent.ready)

    def _micro(self,tick,completed_h1,completed_m5,session_geometry,broker_tradable,hiatus):
        now=int(tick.time_ms_utc)
        if not broker_tradable or not self.ready or completed_m5 is None:
            self.prev_ask=None
            return ()
        m5=completed_m5
        if m5.end_ms>now:
            raise AssertionError('unfinished completed M5 bar exposed')
        if self.completed_m5_start is not None and m5.start_ms<self.completed_m5_start:
            raise ValueError('backward completed M5 state')
        ask=tick.ask_raw/SCALE
        bid=tick.bid_raw/SCALE
        spread=ask-bid
        epoch=(self.completed_m5_start!=m5.start_ms or self.geometry!=session_geometry)
        if epoch or self.micro_gap is None:
            self.completed_m5_start=m5.start_ms
            self.geometry=session_geometry
            self.anchor=m5.close_raw/SCALE
            self.micro_gap=max(self.settings.min_gap_usd,
               spread*self.settings.quoted_spread_multiple,
               (m5.high_raw-m5.low_raw)/SCALE*self.settings.completed_m5_range_fraction)
            self.micro_gap=round(self.micro_gap,3)
            self.prev_ask=ask
            self.seen.clear()
            return ()
        previous=self.prev_ask
        self.prev_ask=ask
        if hiatus:
            self.stale_resets+=1
            return ()
        if self.micro_gap>self.settings.maximum_gap_usd or spread>=self.micro_gap:
            self.unaffordable_quotes+=1
            self.prev_ask=None  # next quote cannot bridge an inadmissible interval
            return ()
        if previous is None or previous==ask:
            return ()
        # Half-open price cells; exactly one actual crossed level on this tick.
        before=math.floor((previous-self.anchor)/self.micro_gap)
        after=math.floor((ask-self.anchor)/self.micro_gap)
        if before==after:
            return ()
        direction=1 if after<before else -1  # creator BUY dip / SELL rise
        boundary=before if direction==1 else before+1
        key=(direction,boundary)
        if key in self.seen or len(self.seen)>=self.settings.maximum_distinct_levels_per_bar:
            self.duplicate_rung_rejections+=1
            return ()
        self.seen.add(key)
        self.skipped_levels+=max(0,abs(after-before)-1)
        h1s=getattr(self.parent,'h1',())
        high=getattr(self.parent,'cached_high',None)
        low=getattr(self.parent,'cached_low',None)
        if high is None or low is None:  # parent supplied by canonical creator source
            return ()
        level=self.anchor+boundary*self.micro_gap
        e=GridOpportunity(now,direction,max(1,abs(boundary)),level,ask,bid,
             high,low,self.micro_gap,session_geometry,now-m5.end_ms,
             source='OMEGAFX_M5_FINE_FIRST_TOUCH_V1')
        self.micro_events+=1
        return (e,)

    def on_tick(self,tick,last_completed_h1,session_geometry:str,*,
                last_completed_m5=None,broker_tradable:bool=True):
        now=int(tick.time_ms_utc)
        if self.last_ms is not None and now<self.last_ms:
            raise ValueError('unordered quote chronology')
        if tick.bid_raw<=0 or tick.ask_raw<tick.bid_raw:
            raise ValueError('invalid bid/ask')
        hiatus=self.last_ms is not None and now-self.last_ms>self.settings.maximum_quote_gap_ms
        self.last_ms=now
        # Must update original parent on EVERY tick regardless of micro activity.
        parent=self.parent.on_tick(tick,last_completed_h1,session_geometry,
                                  last_completed_m5=last_completed_m5,
                                  broker_tradable=broker_tradable)
        micro=self._micro(tick,last_completed_h1,last_completed_m5,
                          session_geometry,broker_tradable,hiatus)
        if parent:
            self.parent_events_forwarded+=1
        chosen=tuple(parent[:1]) if parent else tuple(micro[:1])
        self.handoff_events+=len(chosen)
        return chosen

    def stats(self)->dict:
        return {'parent_events_forwarded':self.parent_events_forwarded,
                'micro_events_generated':self.micro_events,
                'distinct_handoff_events':self.handoff_events,
                'duplicate_rung_rejections':self.duplicate_rung_rejections,
                'skipped_quote_jump_levels_not_filled':self.skipped_levels,
                'stale_quote_resets':self.stale_resets,
                'unaffordable_quote_intervals':self.unaffordable_quotes,
                'parent_original_events':getattr(self.parent,'total_events',None)}

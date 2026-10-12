"""Delta-A-alpha G0 multispeed virtual grid, original creator + completed S1/M1/M5.

Research-only G0; NO orders/cash/lot/margin. S1 and M1 first touches are
based solely on PREVIOUS COMPLETED source Bid/Ask bars. Original 48-active-H1
CreatorGridGenesis and M5 GridReadyPrototype remain intact. One event/tick,
strict no-lookahead, no martingale, no date-label routing. Actual L1..L7 alone
authorizes qualification/funding; raw G0 is never a filled position.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import math
from v1_grid_ready_prototype import GridReadyPrototype
from v1_creator_grid_genesis import GridOpportunity

SCALE=1000

@dataclass(frozen=True)
class SpeedGridSettings:
    s1_gap_floor_usd:float=.25
    m1_gap_floor_usd:float=.35
    spread_multiple:float=1.4
    s1_completed_range_fraction:float=.12
    m1_completed_range_fraction:float=.075
    max_gap_usd:float=12.0
    max_quote_gap_ms:int=60_000
    max_first_touches_per_bar:int=24
    def __post_init__(self):
        if min(self.s1_gap_floor_usd,self.m1_gap_floor_usd,
               self.spread_multiple,self.s1_completed_range_fraction,
               self.m1_completed_range_fraction,self.max_gap_usd,
               self.max_quote_gap_ms,self.max_first_touches_per_bar)<=0:
            raise ValueError('positive geometry bounds required')

class _ClosedQuoteLattice:
    """Only a previous, fully completed quote bar owns next epoch's level grid."""
    def __init__(self,*,width_ms:int,gap_floor:float,range_fraction:float,
                 settings:SpeedGridSettings,source:str):
        self.width_ms=width_ms
        self.gap_floor=gap_floor
        self.range_fraction=range_fraction
        self.settings=settings
        self.source=source
        self.bar_index:Optional[int]=None
        self.o=self.h=self.l=self.c=None
        self.level_anchor:Optional[float]=None
        self.level_gap:Optional[float]=None
        self.last_geometry:Optional[str]=None
        self.prev_ask:Optional[float]=None
        self.seen=set()
        self.generated=0
        self.repeated_rung_rejected=0
        self.unaffordable_quotes=0
        self.skipped_jump_levels=0
        self.completed_bars=0
    def on_quote(self,*,ms:int,bid_raw:int,ask_raw:int,geometry:str,
                 ready:bool,tradable:bool,hiatus:bool,
                 rolling_high:Optional[float],rolling_low:Optional[float]):
        midpoint=(bid_raw+ask_raw)//2
        epoch=ms//self.width_ms
        ask=ask_raw/SCALE
        spread=(ask_raw-bid_raw)/SCALE
        if self.bar_index is not None and epoch<self.bar_index:
            raise ValueError('nonmonotonic tier quote timestamp')
        if self.bar_index is None:
            self.bar_index=epoch
            self.o=self.h=self.l=self.c=midpoint
            self.prev_ask=None
            return ()
        if epoch!=self.bar_index:
            prior_span=(self.h-self.l)/SCALE
            prior_close=self.c/SCALE
            self.completed_bars+=1
            self.bar_index=epoch
            self.o=self.h=self.l=self.c=midpoint
            self.level_anchor=prior_close
            self.level_gap=round(max(self.gap_floor,
                                     spread*self.settings.spread_multiple,
                                     prior_span*self.range_fraction),3)
            self.last_geometry=geometry
            self.prev_ask=ask
            self.seen.clear()
            return ()
        self.h=max(self.h,midpoint);self.l=min(self.l,midpoint);self.c=midpoint
        if hiatus or self.last_geometry!=geometry or not tradable or not ready:
            self.prev_ask=None
            return ()
        prior=self.prev_ask
        self.prev_ask=ask
        if self.level_anchor is None or self.level_gap is None:
            return ()
        gap=self.level_gap
        if gap>self.settings.max_gap_usd or spread>=gap:
            self.unaffordable_quotes+=1
            self.prev_ask=None
            return ()
        if prior is None or ask==prior:return ()
        old=math.floor((prior-self.level_anchor)/gap)
        new=math.floor((ask-self.level_anchor)/gap)
        if old==new:return ()
        side=1 if new<old else -1
        boundary=old if side==1 else old+1
        key=(side,boundary)
        if key in self.seen or len(self.seen)>=self.settings.max_first_touches_per_bar:
            self.repeated_rung_rejected+=1
            return ()
        self.seen.add(key)
        self.skipped_jump_levels+=max(0,abs(new-old)-1)
        if rolling_high is None or rolling_low is None:return ()
        level=self.level_anchor+boundary*gap
        self.generated+=1
        return (GridOpportunity(ms,side,max(1,abs(boundary)),level,ask,bid_raw/SCALE,
                   rolling_high,rolling_low,gap,geometry,
                   ms-(self.bar_index*self.width_ms),self.source),)

class MultiSpeedGridGenesis:
    """Drop-in G0 generator, one chronological price event per quote."""
    def __init__(self,settings:SpeedGridSettings|None=None,*,parent=None):
        self.settings=settings or SpeedGridSettings()
        self.parent=parent if parent is not None else GridReadyPrototype()
        self.s1=_ClosedQuoteLattice(width_ms=1000,gap_floor=self.settings.s1_gap_floor_usd,
              range_fraction=self.settings.s1_completed_range_fraction,
              settings=self.settings,source='OMEGAFX_S1_COMPLETED_FIRST_TOUCH_V1')
        self.m1=_ClosedQuoteLattice(width_ms=60000,gap_floor=self.settings.m1_gap_floor_usd,
              range_fraction=self.settings.m1_completed_range_fraction,
              settings=self.settings,source='OMEGAFX_M1_COMPLETED_FIRST_TOUCH_V1')
        self.latest_ms:Optional[int]=None
        self.handoff=0
        self.parent_handoff=0
        self.m1_handoff=0
        self.s1_handoff=0
        self.collisions_deduped=0
    @property
    def ready(self):return self.parent.ready
    def on_tick(self,tick,last_completed_h1,session_geometry:str,*,last_completed_m5=None,
                broker_tradable:bool=True):
        now=tick.time_ms_utc
        if self.latest_ms is not None and now<self.latest_ms:
            raise ValueError('unordered source quote')
        if tick.ask_raw<tick.bid_raw or tick.bid_raw<=0:
            raise ValueError('unusable source quote')
        hiatus=(self.latest_ms is not None and now-self.latest_ms>self.settings.max_quote_gap_ms)
        self.latest_ms=now
        parent=self.parent.on_tick(tick,last_completed_h1,session_geometry,
                                    last_completed_m5=last_completed_m5,
                                    broker_tradable=broker_tradable)
        original=self.parent.parent
        rh=getattr(original,'cached_high',None)
        rl=getattr(original,'cached_low',None)
        kw=dict(ms=now,bid_raw=tick.bid_raw,ask_raw=tick.ask_raw,
                geometry=session_geometry,ready=self.ready,tradable=broker_tradable,
                hiatus=hiatus,rolling_high=rh,rolling_low=rl)
        minute=self.m1.on_quote(**kw)
        second=self.s1.on_quote(**kw)
        tier=parent if parent else (minute if minute else second)
        if int(bool(parent))+int(bool(minute))+int(bool(second))>1:
            self.collisions_deduped+=int(bool(parent))+int(bool(minute))+int(bool(second))-1
        if not tier:return ()
        self.handoff+=1
        if parent:self.parent_handoff+=1
        elif minute:self.m1_handoff+=1
        else:self.s1_handoff+=1
        return tuple(tier[:1])
    def stats(self)->dict:
        return {'g0_handoff_total':self.handoff,
                'creator_parent_or_m5_handoff':self.parent_handoff,
                'm1_handoff':self.m1_handoff,'s1_handoff':self.s1_handoff,
                'm1_generated_before_priority':self.m1.generated,
                's1_generated_before_priority':self.s1.generated,
                'one_quote_collision_dedup':self.collisions_deduped,
                'm1_repeat_rejections':self.m1.repeated_rung_rejected,
                's1_repeat_rejections':self.s1.repeated_rung_rejected,
                'parent_details':self.parent.stats()}

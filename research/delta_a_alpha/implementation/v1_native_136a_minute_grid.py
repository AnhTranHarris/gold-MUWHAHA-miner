"""Causal ORIGINAL 136A 50-raw per-minute extension event manufacturer.

Primary source: accepted apr_native_markout_136.py `build_events`.
Original event logic: UTC hours 07..19, H4/H1 sign agreement, anchor first
observed midpoint of each minute, first strictly advancing 50-raw extension.
No original April outcome-selected cell whitelist, P&L, TP, SL, or order logic.
Safeguards: only PREVIOUS COMPLETED H4/H1, quote gap/spread reset, one
virtual opportunity per observed quote; all L2-L7 permissions remain elsewhere.
The H4/H1 sign reconstruction is a transparent approximation pending exact
provenance of historical precomputed state arrays, NOT asserted bit parity.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from v1_creator_grid_genesis import GridOpportunity

HOUR_MS=3_600_000
MIN_MS=60_000
SCALE=1000

@dataclass(frozen=True)
class Native136ASettings:
    step_raw:int=50
    max_quote_gap_ms:int=60_000
    max_spread_raw:int=1250
    max_h4_age_ms:int=8*HOUR_MS
    max_h1_age_ms:int=2*HOUR_MS
    def __post_init__(self):
        if min(self.step_raw,self.max_quote_gap_ms,self.max_spread_raw,
               self.max_h4_age_ms,self.max_h1_age_ms)<=0:
            raise ValueError('invalid native minute grid settings')

class Native136AMinuteGrid:
    def __init__(self,settings:Native136ASettings|None=None):
        self.settings=settings or Native136ASettings()
        self.last_ms:Optional[int]=None
        self.minute:Optional[int]=None
        self.anchor:Optional[int]=None
        self.direction:int=0
        self.last_extension:int=0
        self.raw_generated=0
        self.spread_denied=0
        self.htf_unresolved=0
        self.stale_htf=0
        self.session_inactive=0
        self.reanchors=0
        self.hiatus_resets=0

    @staticmethod
    def _sign(bar,now:int)->int:
        if bar is None:return 0
        if bar.end_ms>now:raise AssertionError('future/unfinished HTF bar')
        return (bar.close_raw>bar.open_raw)-(bar.close_raw<bar.open_raw)

    def _reset(self,minute:int|None=None,mid:int|None=None,d:int=0):
        self.minute=minute;self.anchor=mid;self.direction=d;self.last_extension=0
        self.reanchors+=1

    def on_tick(self,tick,completed_h4,completed_h1,geometry:str,*,
                broker_tradable:bool=True)->tuple[GridOpportunity,...]:
        now=int(tick.time_ms_utc)
        if self.last_ms is not None and now<self.last_ms:
            raise ValueError('nonmonotonic native 136A quote')
        if tick.bid_raw<=0 or tick.ask_raw<tick.bid_raw:
            raise ValueError('invalid native 136A BidAsk')
        hiatus=self.last_ms is not None and now-self.last_ms>self.settings.max_quote_gap_ms
        self.last_ms=now
        hour=(now//HOUR_MS)%24
        if not 7<=hour<=19:
            self.session_inactive+=1
            self._reset()
            return ()
        h4=self._sign(completed_h4,now)
        h1=self._sign(completed_h1,now)
        if (completed_h4 is not None and completed_h1 is not None and
            (now-completed_h4.end_ms>self.settings.max_h4_age_ms or
             now-completed_h1.end_ms>self.settings.max_h1_age_ms)):
            self.stale_htf+=1
            self._reset()
            return ()
        d=h4 if h4!=0 and h4==h1 else 0
        if d==0:
            self.htf_unresolved+=1
            self._reset()
            return ()
        spread=tick.ask_raw-tick.bid_raw
        if not broker_tradable or spread>self.settings.max_spread_raw or hiatus:
            self.spread_denied+=int(spread>self.settings.max_spread_raw)
            self.hiatus_resets+=int(hiatus)
            self._reset()
            return ()
        minute=now//MIN_MS
        mid=(tick.bid_raw+tick.ask_raw)//2
        if self.minute!=minute or self.direction!=d or self.anchor is None:
            self._reset(minute,mid,d)
            return ()
        x=(mid-self.anchor)*d
        if x<=self.last_extension:return ()
        level=(x//self.settings.step_raw)*self.settings.step_raw
        if level<=self.last_extension:return ()
        self.last_extension=level
        self.raw_generated+=1
        high=max(completed_h4.high_raw,completed_h1.high_raw)/SCALE
        low=min(completed_h4.low_raw,completed_h1.low_raw)/SCALE
        return (GridOpportunity(now,d,max(1,level//self.settings.step_raw),
            (self.anchor+d*level)/SCALE,tick.ask_raw/SCALE,tick.bid_raw/SCALE,
            high,low,self.settings.step_raw/SCALE,geometry,
            now-minute*MIN_MS,source='APR136A_NATIVE_CAUSAL_MINUTE_EXTENSION_V1'),)

    def stats(self):
        return dict(native_136a_raw=self.raw_generated,spread_denied=self.spread_denied,
            htf_unresolved=self.htf_unresolved,stale_htf=self.stale_htf,
            session_inactive=self.session_inactive,
            reanchors=self.reanchors,hiatus_resets=self.hiatus_resets)

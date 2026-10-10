"""Delta-A-alpha V1 clean-room vertical tick+session+MTF kernel.

Owner authority: unmodified V1 whitepaper and 2026-10-10 session/risk addendum.
NEVER imports deleted Jan/Feb implementations. Zero trading signals/orders until
all L0-L7 contracts are implemented and verified. Research-only, no profit claim.
Session desk windows are CONFIGURABLE RESEARCH HYPOTHESES, not broker hours.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone, time
from zoneinfo import ZoneInfo
from typing import Optional

UTC = timezone.utc
SCALE = 1000  # Dukascopy raw quote units observed in Jan/Feb sample, not P&L units
TF_MS = {"H4": 14_400_000, "H1": 3_600_000, "M15": 900_000, "M5": 300_000}

# Research-only conventional FX desk windows, interpreted in each zone's
# local civil time with automatic per-zone DST; not a promise about XAUUSD hours.
DESKS = {
    "SYDNEY": ("Australia/Sydney", time(8), time(17)),
    "TOKYO": ("Asia/Tokyo", time(9), time(18)),
    "LONDON": ("Europe/London", time(8), time(17)),
    "NEW_YORK": ("America/New_York", time(8), time(17)),
}

@dataclass(frozen=True)
class Quote:
    time_ms_utc: int
    bid_raw: int
    ask_raw: int
    @property
    def spread_raw(self) -> int:
        return self.ask_raw - self.bid_raw

@dataclass(frozen=True)
class SessionFrame:
    utc: datetime
    local_clocks: dict[str, datetime]
    open_desks: tuple[str, ...]
    overlap: tuple[str, ...]
    suggested_geometry: str
    weekday: int
    status: str                 # OBSERVED_QUOTE/STALE/NON_EXECUTABLE
    broker_trading_confirmed: bool
    regional_holiday_labels: tuple[str, ...] # supplied as-of known records, never invented


def _time_in_window(t:time, begin:time, end:time)->bool:
    return begin<=t<end if begin<=end else (t>=begin or t<end)


def session_frame(utc_ms:int, *, quote_observed:bool=True,
                  broker_trading_confirmed:bool=False,
                  holiday_labels:tuple[str,...]=())->SessionFrame:
    if utc_ms<0:raise ValueError("negative timestamp")
    dt=datetime.fromtimestamp(utc_ms/1000, tz=UTC)
    clocks={name: dt.astimezone(ZoneInfo(zone)) for name,(zone,_,_) in DESKS.items()}
    opens=tuple(name for name,(_,start,end) in DESKS.items()
                if clocks[name].weekday()<5 and _time_in_window(clocks[name].time(),start,end))
    if "LONDON" in opens and "NEW_YORK" in opens:
        geom="LONDON_NEW_YORK_OVERLAP"
    elif "SYDNEY" in opens and "TOKYO" in opens:
        geom="SYDNEY_TOKYO_OVERLAP"
    elif "TOKYO" in opens or "SYDNEY" in opens:
        geom="ASIA_PACIFIC"
    elif "LONDON" in opens:
        geom="LONDON"
    elif "NEW_YORK" in opens:
        geom="NEW_YORK"
    else:
        geom="TRANSITION_OR_CLOSED"
    return SessionFrame(dt,clocks,opens,opens if len(opens)>1 else (),geom,
                        dt.weekday(),"OBSERVED_QUOTE" if quote_observed else "NO_QUOTE",
                        broker_trading_confirmed,tuple(holiday_labels))

@dataclass(frozen=True)
class ClosedBar:
    timeframe: str
    start_ms: int
    end_ms: int
    open_raw: int
    high_raw: int
    low_raw: int
    close_raw: int
    quote_count: int

@dataclass
class _AccumBar:
    start:int
    open:int
    high:int
    low:int
    close:int
    count:int

class CompletedBars:
    """Only completed bars are ever exposed to the strategy frame."""
    def __init__(self):
        self.live:dict[str,_AccumBar]={}
        self.completed:dict[str,ClosedBar]={}
    def on_quote(self,q:Quote):
        for name,width in TF_MS.items():
            start=(q.time_ms_utc//width)*width
            old=self.live.get(name)
            if old is None:
                self.live[name]=_AccumBar(start,q.bid_raw,q.bid_raw,q.bid_raw,q.bid_raw,1)
            elif old.start==start:
                old.high=max(old.high,q.bid_raw)
                old.low=min(old.low,q.bid_raw)
                old.close=q.bid_raw
                old.count+=1
            else:
                if start<=old.start:raise ValueError("non-monotonic bar key")
                self.completed[name]=ClosedBar(name,old.start,old.start+width,
                                               old.open,old.high,old.low,old.close,old.count)
                self.live[name]=_AccumBar(start,q.bid_raw,q.bid_raw,q.bid_raw,q.bid_raw,1)
    def snapshot(self,q:Quote)->dict[str,Optional[ClosedBar]]:
        ret={k:self.completed.get(k) for k in TF_MS}
        if any(b and b.end_ms>q.time_ms_utc for b in ret.values()):
            raise AssertionError("future bar exposure")
        return ret

@dataclass(frozen=True)
class VerticalFrame:
    quote:Quote
    l1_session:SessionFrame
    l2_completed_bars:dict[str,Optional[ClosedBar]]
    l3_geometry:str
    l4_regime_state:str
    l5_native_route:str
    l6_recovery_state:str
    l7_governor_state:str
    broker_order_count:int

class CleanV1Engine:
    """One vertical program, no specialist islands and no funded actions.

    Stages L3-L7 are explicit fail-closed interfaces, not fake strategies.
    Market event input is still processed across the same vertical frame.
    """
    def __init__(self):
        self.latest_ms:int|None=None
        self.bars=CompletedBars()
        self.num_quotes=0
        self.funded_orders=0
    def on_tick(self,q:Quote, *, broker_trading_confirmed:bool=False,
                known_holidays:tuple[str,...]=())->VerticalFrame:
        if self.latest_ms is not None and q.time_ms_utc<self.latest_ms:
            raise ValueError("L0 out-of-order executable tick")
        if q.ask_raw<q.bid_raw or q.bid_raw<=0:
            raise ValueError("L0 invalid bid/ask")
        self.latest_ms=q.time_ms_utc
        self.num_quotes+=1
        session=session_frame(q.time_ms_utc,
                            broker_trading_confirmed=broker_trading_confirmed,
                            holiday_labels=known_holidays)
        self.bars.on_quote(q)
        completed=self.bars.snapshot(q)
        # All L2/L3/L4/L5/L6 source strategies absent by owner reset.
        # No leakage of unverified prior implementations or fictional orders.
        return VerticalFrame(q,session,completed,session.suggested_geometry,
                             "NOT_YET_RESEARCHED", "NO_CERTIFIED_ROUTE",
                             "NO_FUNDED_INVENTORY", "DENY_ALL_NEW_RISK",
                             self.funded_orders)

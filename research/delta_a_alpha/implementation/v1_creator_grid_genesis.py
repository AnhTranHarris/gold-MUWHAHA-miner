"""Delta-A-alpha V1 / creator-derived, NON-TRADING original grid genesis.

Provenance: OmegaFX grid_bot.py, original code blob
1d5efa140b363941e7360bd0ae85ac7e04d0ecaa. This reconstructs the
creator's rolling 48 COMPLETED H1 highs/lows and successive same-side
previous-entry grid spacing, replacing physical averaging with virtual rungs.

Every output is only an opportunity. L1-L7 have sole authority to qualify,
fund and execute a physical 0.01-lot trade. No Martingale, no hidden order,
no future/unfinished candle, no calendar-month strategy selectors.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Optional
import math

SCALE = 1000
HOUR_MS = 3_600_000

@dataclass(frozen=True)
class GenesisSettings:
    h1_window: int = 48
    # These are predeclared RESEARCH hypotheses, not broker-optimized settings.
    liquid_gap_floor_usd: float = 0.80
    asia_gap_floor_usd: float = 1.80
    transition_gap_floor_usd: float = 1.40
    spread_multiple: float = 4.0
    h1_range_fraction_liquid: float = .18
    h1_range_fraction_asia: float = .34
    h1_range_fraction_other: float = .25
    max_gap_usd: float = 12.0
    max_virtual_rungs_per_direction: int = 32
    max_campaign_hours: int = 8
    # Independent lower-lattice research GENESIS. It is not a standalone EA.
    enable_m5_child_lattice: bool = True
    m5_liquid_gap_floor_usd: float = 0.75
    m5_asia_gap_floor_usd: float = 1.35
    m5_other_gap_floor_usd: float = 1.10
    m5_spread_multiple: float = 1.5
    m5_completed_range_fraction: float = 0.10
    # Profit-taking itself is NOT performed by this genesis layer.

    def __post_init__(self):
        if self.h1_window < 2 or self.max_virtual_rungs_per_direction < 1:
            raise ValueError('invalid grid windows or rung limit')
        if min(self.liquid_gap_floor_usd,self.asia_gap_floor_usd,
               self.transition_gap_floor_usd,self.spread_multiple,
               self.h1_range_fraction_liquid,self.h1_range_fraction_asia,
               self.h1_range_fraction_other,self.max_gap_usd) <= 0:
            raise ValueError('nonpositive grid geometry')

@dataclass(frozen=True)
class GridOpportunity:
    timestamp_ms: int
    side: int  # +1 creator-derived buy crossing; -1 creator-derived sell crossing
    rung: int
    crossing_level_usd: float
    observed_ask_usd: float
    bid_usd: float
    rolling_high_usd: float
    rolling_low_usd: float
    active_gap_usd: float
    session_geometry: str
    campaign_age_ms: int
    source: str = 'OMEGAFX_CAUSAL_VIRTUAL_RUNG'

@dataclass
class _VirtualCampaign:
    anchor_usd: Optional[float] = None
    depth: int = 0
    birth_ms: int = 0

class CreatorGridGenesis:
    """Executable-quote-aware virtual grid, but NEVER generates physical orders.

    The creator tested thresholds with Ask for BOTH signs, so this preserves
    that aspect for comparable opportunity GENESIS, while recording Bid/Ask
    for subsequent economically realistic L7 execution.

    Input to `on_tick` is a tick and the ONE latest COMPLETED H1 bar exposed
    by the V1 bar kernel. It must satisfy end_ms <= tick_ms.
    """
    def __init__(self, settings: GenesisSettings | None = None):
        self.settings = settings or GenesisSettings()
        self.h1 = deque(maxlen=self.settings.h1_window)
        self.last_h1_start: Optional[int] = None
        self.cached_high = None
        self.cached_low = None
        self.cached_last_range = None
        self.last_timestamp_ms: Optional[int] = None
        self.previous_ask: Optional[float] = None
        self.buy = _VirtualCampaign()
        self.sell = _VirtualCampaign()
        self.last_event_ms: Optional[int] = None
        self.last_m5_start: Optional[int] = None
        self.child_reference_usd: Optional[float] = None
        self.child_gap_usd: Optional[float] = None
        self.child_geometry: Optional[str] = None
        self.child_previous_ask: Optional[float] = None
        self.child_bars_reset = 0
        self.child_seen_crossings = set()
        self.m5_child_events = 0
        self.parent_events = 0
        self.total_events = 0
        self.total_by_side = {1:0,-1:0}
        self.rejected_nontradable = 0

    @property
    def ready(self) -> bool:
        return len(self.h1) == self.settings.h1_window

    def _closed_h1(self, bar, now: int):
        if bar is None:
            return
        if bar.end_ms > now:
            raise AssertionError('unfinished/future H1 bar delivered to grid genesis')
        if self.last_h1_start is None or bar.start_ms > self.last_h1_start:
            if self.last_h1_start is not None and bar.start_ms < self.last_h1_start:
                raise ValueError('backward completed-bar sequence')
            self.h1.append(bar)
            self.last_h1_start = bar.start_ms
            self.cached_high = max(x.high_raw for x in self.h1) / SCALE
            self.cached_low = min(x.low_raw for x in self.h1) / SCALE
            self.cached_last_range = (bar.high_raw-bar.low_raw) / SCALE
        elif bar.start_ms < self.last_h1_start:
            raise ValueError('stale/backward completed bar')

    def _geometry(self, geometry: str, spread: float, h1_span: float) -> float:
        liquid = geometry in ('LONDON_NEW_YORK_OVERLAP','LONDON','NEW_YORK')
        asia = geometry in ('ASIA_PACIFIC','SYDNEY_TOKYO_OVERLAP')
        floor = (self.settings.liquid_gap_floor_usd if liquid else
                 self.settings.asia_gap_floor_usd if asia else
                 self.settings.transition_gap_floor_usd)
        fraction = (self.settings.h1_range_fraction_liquid if liquid else
                    self.settings.h1_range_fraction_asia if asia else
                    self.settings.h1_range_fraction_other)
        raw = max(floor,spread*self.settings.spread_multiple,h1_span*fraction)
        # If even our maximum grid is inside the current spread burden,
        # no "affordable" opportunity may be manufactured.
        return round(raw,3)

    def _expire_or_reset(self, camp: _VirtualCampaign, side: int,
                         ask: float, gap: float, now: int) -> None:
        if camp.anchor_usd is None: return
        expiry = now-camp.birth_ms > self.settings.max_campaign_hours*HOUR_MS
        cap = camp.depth >= self.settings.max_virtual_rungs_per_direction
        # A completed favorable reversal closes a VIRTUAL campaign: it never
        # implies a funded P/L or frees a funded real-world slot.
        reversal = ((ask >= camp.anchor_usd+gap) if side==1
                    else (ask <= camp.anchor_usd-gap))
        if expiry or cap or reversal:
            camp.anchor_usd = None
            camp.depth = 0
            camp.birth_ms = 0

    def on_tick(self, tick, last_completed_h1,
                session_geometry: str, *, last_completed_m5=None,
                broker_tradable: bool = True) -> tuple[GridOpportunity,...]:
        now = tick.time_ms_utc
        if self.last_timestamp_ms is not None and now < self.last_timestamp_ms:
            raise ValueError('unordered tick input')
        if tick.ask_raw < tick.bid_raw or tick.bid_raw <= 0:
            raise ValueError('invalid executable quote')
        self._closed_h1(last_completed_h1,now)
        ask=tick.ask_raw / SCALE
        bid=tick.bid_raw / SCALE
        spread=ask-bid
        prior=self.previous_ask
        self.previous_ask=ask
        self.last_timestamp_ms=now
        if not self.ready or prior is None:
            return ()
        high=self.cached_high
        low=self.cached_low
        last_range=self.cached_last_range
        gap=self._geometry(session_geometry,spread,last_range)
        if not broker_tradable or gap > self.settings.max_gap_usd:
            self.rejected_nontradable+=1
            return ()
        # Recompute thresholds using PREVIOUS observed tick and completed
        # H1 extrema. Cannot treat sitting below a level as repeated crossing.
        events=[]
        for side,camp,origin in ((1,self.buy,high),(-1,self.sell,low)):
            self._expire_or_reset(camp,side,ask,gap,now)
            anchor=origin if camp.anchor_usd is None else camp.anchor_usd
            level=anchor-side*gap
            if side==1:
                crossed=(prior>level and ask<=level)
            else:
                crossed=(prior<level and ask>=level)
            if not crossed:continue
            if camp.anchor_usd is None:
                camp.birth_ms=now
            camp.depth+=1
            camp.anchor_usd=ask
            # At most one physical EVENT per input quote, although both
            # *directional research hypotheses* can be scored downstream.
            event=GridOpportunity(now,side,camp.depth,level,ask,bid,
                                  high,low,gap,session_geometry,now-camp.birth_ms)
            events.append(event)
            self.total_by_side[side]+=1
            self.total_events+=1
            self.parent_events+=1
        # The lower M5 lattice only reanchors at a COMPLETED M5 bar's
        # observable close. Its thresholds remain CONSTANT until the next
        # completed bar, so transient spread/volatility cannot slide lines
        # through price and manufacture noncausal "crossings".
        if self.settings.enable_m5_child_lattice and last_completed_m5 is not None:
            m5=last_completed_m5
            if m5.end_ms > now:
                raise AssertionError('future/unfinished M5 bar to child lattice')
            if self.last_m5_start is not None and m5.start_ms < self.last_m5_start:
                raise ValueError('stale child-lattice M5 bar')
            if self.last_m5_start is None or m5.start_ms > self.last_m5_start or session_geometry!=self.child_geometry:
                self.last_m5_start=m5.start_ms
                self.child_geometry=session_geometry
                self.child_reference_usd=m5.close_raw / SCALE
                liquid=session_geometry in ('LONDON','NEW_YORK','LONDON_NEW_YORK_OVERLAP')
                asia=session_geometry in ('ASIA_PACIFIC','SYDNEY_TOKYO_OVERLAP')
                floor=(self.settings.m5_liquid_gap_floor_usd if liquid else
                       self.settings.m5_asia_gap_floor_usd if asia else
                       self.settings.m5_other_gap_floor_usd)
                span=(m5.high_raw-m5.low_raw)/SCALE
                self.child_gap_usd=round(max(floor,spread*self.settings.m5_spread_multiple,
                                              span*self.settings.m5_completed_range_fraction),3)
                self.child_previous_ask=ask
                self.child_bars_reset+=1
                self.child_seen_crossings.clear()
            elif self.child_reference_usd is not None and self.child_gap_usd is not None:
                previous=self.child_previous_ask
                self.child_previous_ask=ask
                if previous is not None and self.child_gap_usd<=self.settings.max_gap_usd:
                    # a positive index crossing is a creator-style SELL / fade
                    # opportunity; negative is a BUY / fade opportunity.
                    # The native Vertical route may instead select breakout
                    # CONTINUATION; genesis never decides funded direction.
                    old_index=math.floor((previous-self.child_reference_usd)/self.child_gap_usd)
                    new_index=math.floor((ask-self.child_reference_usd)/self.child_gap_usd)
                    if old_index!=new_index:
                        side=1 if new_index<old_index else -1
                        crossed_index=new_index+1 if side==1 else old_index+1
                        crossed_level=self.child_reference_usd+crossed_index*self.child_gap_usd
                        key=(side,crossed_index)
                        # One rung hypothesis per direction per completed-M5
                        # auction state. Quote micro-jitter cannot repeatedly
                        # manufacture "new opportunities" around one level.
                        if key not in self.child_seen_crossings:
                            self.child_seen_crossings.add(key)
                            if not events:
                                events.append(GridOpportunity(now,side,abs(crossed_index),
                                    crossed_level,ask,bid,high,low,self.child_gap_usd,
                                    session_geometry,now-m5.end_ms,
                                    source='OMEGAFX_M5_COMPLETED_VIRTUAL_CHILD'))
                                self.m5_child_events+=1
                                self.total_by_side[side]+=1
                                self.total_events+=1
        # One distinct primary virtual opportunity per true market tick.
        # The journal retains separate parent/child source counters.
        return tuple(events[:1])

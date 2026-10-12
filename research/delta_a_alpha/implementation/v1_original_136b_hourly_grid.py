"""Causal opportunity-only reconstruction of original April 136B hour/Asia grids.

Original: apr_session_grid_discovery_136b.py:build_grid_events.  This is
only its deterministic event manufacturing, NOT April-selected profitable
cell masks, hindsight modes, take-profit, stop-loss or broker execution.

Original 136B time windows: 07:00..20:59 UTC HIGHVOL, 23:00..06:59 UTC
ASIA; original anchor is FIRST observed midpoint in each UTC hour / Asia
23:00-to-07:00 session, with first touch of each cell boundary/direction.
Six ORIGINAL research gaps are generated as parallel virtual hypotheses;
one market quote can generate at most ONE forwarded candidate downstream.
"""
from __future__ import annotations
from dataclasses import dataclass
from collections import Counter
from typing import Optional

from v1_creator_grid_genesis import GridOpportunity

HOUR_MS = 3_600_000
DAY_MS = 86_400_000
SCALE = 1000
ORIGINAL_GAPS_RAW = (250, 500, 750, 1000, 1500, 2000)


@dataclass(frozen=True)
class Hourly136BSettings:
    gaps_raw: tuple[int, ...] = ORIGINAL_GAPS_RAW
    max_quote_gap_ms: int = 60_000
    max_spread_raw: int = 650

    def __post_init__(self):
        if (not self.gaps_raw or any(not isinstance(g, int) or g <= 0 for g in self.gaps_raw)
                or len(set(self.gaps_raw)) != len(self.gaps_raw)
                or self.max_quote_gap_ms <= 0 or self.max_spread_raw <= 0):
            raise ValueError('invalid original-136B virtual-grid bounds')


class _RungCampaign:
    def __init__(self, gap_raw: int, kind: str):
        self.gap_raw = gap_raw
        self.kind = kind
        self.owner: Optional[int] = None
        self.anchor: Optional[int] = None
        self.prev_cell = 0
        self.seen: set[tuple[int, int]] = set()
        self.generated = 0
        self.duplicate = 0
        self.reset_count = 0

    def advance(self, *, now: int, midpoint_raw: int, owner: int,
                hiatus: bool, tradable: bool):
        # Every campaign is reset by its own original auction owner, or by an
        # observed market closure. The latter is an explicit fail-closed
        # deviation from original 136B's continuous-market assumption.
        if not tradable:
            # A bad-spread or broker-halted quote is NOT an executable anchor.
            # Arm reinitialization on the NEXT good quote; otherwise the
            # resumed quote would manufacture a giant false crossing.
            self.owner = None
            self.anchor = None
            self.prev_cell = 0
            self.seen.clear()
            self.reset_count += 1
            return None
        if self.owner != owner or hiatus or self.anchor is None:
            self.owner = owner
            self.anchor = midpoint_raw
            self.prev_cell = 0
            self.seen.clear()
            self.reset_count += 1
            return None
        cell = (midpoint_raw - self.anchor) // self.gap_raw
        if cell == self.prev_cell:
            return None
        cross = 1 if cell > self.prev_cell else -1
        # EXACT original 136B boundary key: destination cell on upward
        # crossing; previous cell on downward crossing. Side is MOM direction.
        boundary_cell = cell if cross > 0 else self.prev_cell
        key = (boundary_cell, cross)
        self.prev_cell = cell
        if key in self.seen:
            self.duplicate += 1
            return None
        self.seen.add(key)
        self.generated += 1
        return cross, self.anchor + boundary_cell * self.gap_raw, boundary_cell


class Original136BHourlyGrid:
    """One raw 136B G0 event per quote; never decides funded direction.

    The *first* original gap in configured order wins when several gaps
    cross on the same tick. All gaps remain independently journaled. The
    deterministic priority is not selected using any historical P&L.
    """
    def __init__(self, settings: Hourly136BSettings | None = None):
        self.settings = settings or Hourly136BSettings()
        self.campaigns = {
            (kind, gap): _RungCampaign(gap, kind)
            for kind in ('HIGHVOL', 'ASIA') for gap in self.settings.gaps_raw
        }
        self.last_ms: Optional[int] = None
        self.raw_by_kind = Counter()
        self.raw_by_gap = Counter()
        self.forwarded = 0
        self.collisions = 0
        self.spread_denied = 0
        self.quote_halt_denied = 0
        self.rung_unaffordable = 0

    @staticmethod
    def _owner(now: int):
        hour = (now // HOUR_MS) % 24
        if 7 <= hour <= 20:
            return 'HIGHVOL', now // HOUR_MS
        if hour >= 23 or hour < 7:
            return 'ASIA', (now - 23 * HOUR_MS) // DAY_MS
        return None, None

    def on_tick(self, tick, *, ready: bool, broker_tradable: bool = True,
                rolling_high: Optional[float] = None,
                rolling_low: Optional[float] = None,
                geometry: str = 'UNKNOWN') -> tuple[GridOpportunity, ...]:
        now = tick.time_ms_utc
        if self.last_ms is not None and now < self.last_ms:
            raise ValueError('nonmonotonic original-136B quote')
        if tick.ask_raw < tick.bid_raw or tick.bid_raw <= 0:
            raise ValueError('invalid original-136B Bid/Ask quote')
        hiatus = self.last_ms is not None and now - self.last_ms > self.settings.max_quote_gap_ms
        self.last_ms = now
        kind, owner = self._owner(now)
        if kind is None:
            return ()
        spread = tick.ask_raw - tick.bid_raw
        midpoint = (tick.bid_raw + tick.ask_raw) // 2
        tradable = broker_tradable and spread <= self.settings.max_spread_raw
        if not tradable:
            self.spread_denied += int(spread > self.settings.max_spread_raw)
            self.quote_halt_denied += int(not broker_tradable)
        matches = []
        for gap in self.settings.gaps_raw:
            campaign = self.campaigns[(kind, gap)]
            affordable = spread < gap
            if not affordable:
                self.rung_unaffordable += 1
            crossed = campaign.advance(now=now, midpoint_raw=midpoint,
                                       owner=owner, hiatus=hiatus,
                                       tradable=tradable and affordable)
            if crossed is not None:
                self.raw_by_kind[kind] += 1
                self.raw_by_gap[(kind, gap)] += 1
                matches.append((gap, *crossed))
        if not ready or not tradable or not matches:
            return ()
        # G0 has no physical orders. The existing L2-L7 funnel must choose
        # whether momentum or reversal is appropriate from completed context.
        gap, cross, level_raw, cell = matches[0]
        self.collisions += len(matches) - 1
        self.forwarded += 1
        return (GridOpportunity(now, cross, max(1, abs(cell)), level_raw / SCALE,
                tick.ask_raw / SCALE, tick.bid_raw / SCALE,
                rolling_high if rolling_high is not None else level_raw / SCALE,
                rolling_low if rolling_low is not None else level_raw / SCALE,
                gap / SCALE, geometry, 0,
                source=f'APR136B_{kind}_ORIGINAL_HOURLY_MOM_VIRTUAL'),)

    def stats(self):
        return {'136b_forwarded': self.forwarded,
                '136b_raw_by_kind': dict(self.raw_by_kind),
                '136b_raw_by_gap': {f'{k}:{g}': v for (k, g), v in self.raw_by_gap.items()},
                '136b_same_quote_gap_collisions': self.collisions,
                '136b_spread_denied': self.spread_denied,
                '136b_rung_unaffordable': self.rung_unaffordable,
                '136b_quote_halt_denied': self.quote_halt_denied,
                '136b_campaign_resets': sum(x.reset_count for x in self.campaigns.values())}

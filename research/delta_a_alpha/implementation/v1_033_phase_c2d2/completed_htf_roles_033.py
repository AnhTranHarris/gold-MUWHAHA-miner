"""DAA V1 L2: causal completed Bid/Ask OHLC transport with four DISTINCT role ports.

Owner whitepaper L2 and Jan-1 hardlock031. This component does not invent
unpublished optimized structural classifiers. It transports genuine completed
H4 ENVIRONMENT, H1 PARENT_LOCATION, M15 PHASE and M5 TRANSFER bars. Each
role's classifier must come from independently recovered original source.

It is NOT original JAN039/FEB045/FEB047 full strategy parity by itself.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Mapping
from v1_funded_core_033c import Quote, Structure

PERIODS_MS = {'H4': 14_400_000, 'H1': 3_600_000,
              'M15': 900_000, 'M5': 300_000}
ROLE_NAMES = {'H4': 'environment', 'H1': 'parent_location',
              'M15': 'phase', 'M5': 'transfer'}


@dataclass(frozen=True)
class CompletedBar:
    timeframe: str
    role: str
    interval_start_ms: int
    interval_end_ms: int
    first_quote_ms: int
    last_quote_ms: int
    open_bid: int
    high_bid: int
    low_bid: int
    close_bid: int
    open_ask: int
    high_ask: int
    low_ask: int
    close_ask: int
    observed_ticks: int
    observed_from_bucket_start: bool


@dataclass(frozen=True)
class RoleSnapshot:
    asof_quote_ms: int
    h4_environment: CompletedBar
    h1_parent_location: CompletedBar
    m15_phase: CompletedBar
    m5_transfer: CompletedBar

    def bars(self) -> dict[str, CompletedBar]:
        return {'H4': self.h4_environment, 'H1': self.h1_parent_location,
                'M15': self.m15_phase, 'M5': self.m5_transfer}


class CompletedHTFRoles:
    """Incremental as-of-only bar construction; never invent missing intervals.

    Caller MUST feed pre-T0 genuine historical quote ticks (when available)
    before first live quote; otherwise history readiness fails closed. A bar
    from the first arbitrarily cut bucket is marked partial, never complete.
    Months, dates, future prices, and EMA-sign voting play no role here.
    """
    def __init__(self):
        self._forming: dict[str, dict] = {}
        self._completed: dict[str, CompletedBar] = {}
        self._last_quote_ms = -1
        self.first_quote_ms: int | None = None
        self.total_quotes = 0
        self.missing_intervals = {name: 0 for name in PERIODS_MS}

    def on_quote(self, q: Quote) -> None:
        if q.time_ms < self._last_quote_ms:
            raise ValueError('Out-of-order Bid/Ask quote in original V1 L2')
        if self.first_quote_ms is None:
            self.first_quote_ms = q.time_ms
        for tf, width in PERIODS_MS.items():
            start = (q.time_ms // width) * width
            prev = self._forming.get(tf)
            if prev is None or prev['start'] != start:
                if prev is not None:
                    # Only actual observed bars are published, no empty bars.
                    previous_start = prev['start']
                    if start < previous_start:
                        raise ValueError('Non-monotonic source interval')
                    self.missing_intervals[tf] += max(0, (start - previous_start) // width - 1)
                    self._completed[tf] = CompletedBar(
                        tf, ROLE_NAMES[tf], previous_start, previous_start + width,
                        prev['first'], prev['last'],
                        prev['ob'], prev['hb'], prev['lb'], prev['cb'],
                        prev['oa'], prev['ha'], prev['la'], prev['ca'],
                        prev['count'], prev['start_known'])
                self._forming[tf] = dict(start=start, first=q.time_ms,
                    last=q.time_ms, ob=q.bid_raw, hb=q.bid_raw, lb=q.bid_raw,
                    cb=q.bid_raw, oa=q.ask_raw, ha=q.ask_raw, la=q.ask_raw,
                    ca=q.ask_raw, count=1,
                    # Initial bucket may begin before data begins. Only a
                    # genuine observed boundary after quote history can mark
                    # the next bucket complete as a provenance source.
                    start_known=prev is not None)
            else:
                prev['last'] = q.time_ms
                prev['hb'] = max(prev['hb'], q.bid_raw)
                prev['lb'] = min(prev['lb'], q.bid_raw)
                prev['cb'] = q.bid_raw
                prev['ha'] = max(prev['ha'], q.ask_raw)
                prev['la'] = min(prev['la'], q.ask_raw)
                prev['ca'] = q.ask_raw
                prev['count'] += 1
        self._last_quote_ms = q.time_ms
        self.total_quotes += 1

    def snapshot(self, time_ms: int) -> RoleSnapshot | None:
        if time_ms != self._last_quote_ms:
            # Returning for an unobserved future timestamp is forbidden.
            raise ValueError('L2 snapshot must be requested at latest actual quote')
        if len(self._completed) != 4:
            return None
        if any(not bar.observed_from_bucket_start or
               bar.interval_end_ms >= time_ms or
               bar.last_quote_ms >= time_ms
               for bar in self._completed.values()):
            return None
        return RoleSnapshot(time_ms, self._completed['H4'],
            self._completed['H1'], self._completed['M15'], self._completed['M5'])

    def as_structure(self, *, session: str, grid_key: str,
                     classify: Mapping[str, Callable[[CompletedBar], int]]) -> Structure | None:
        """Requires all FOUR role-specific original classifiers; no proxy fallback.

        We deliberately do not assign directions/phase from raw close-to-open
        or majority EMA votes. Such mappings would change the owner's design.
        """
        snap = self.snapshot(self._last_quote_ms)
        if snap is None:
            return None
        bars = snap.bars()
        if set(classify) != set(PERIODS_MS):
            raise ValueError('Each distinct V1 L2 role classifier must be supplied')
        states = {}
        for tf in ('H4', 'H1', 'M15', 'M5'):
            state = classify[tf](bars[tf])
            if type(state) is not int or state not in (-1, 0, 1):
                raise ValueError(f'Original {tf} role classifier returned invalid state')
            states[tf] = state
        ends = tuple(bars[tf].interval_end_ms for tf in ('H4', 'H1', 'M15', 'M5'))
        completed = max(ends)
        out = Structure(session, states['H4'], states['H1'], states['M15'],
                        states['M5'], completed, grid_key,
                        completed_bar_end_ms=ends)
        if not out.valid_at(self._last_quote_ms):
            raise AssertionError('Structural role contract violated')
        return out

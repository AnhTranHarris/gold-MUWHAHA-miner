"""C2D3-I: exact-source STMR 032 H4/H1/M15/M5 completed EMA-state port.

AUTHORITIES, *not summaries*:
  JAN032/source/stmr_base.py::bar_states, sess_fixed, choose_sleeve
  JAN032/source/stmr_janjul.py::bar_states_span, sleeve_state, make_states

bar_states_span uses source BID supplied by stmr_base.materialize, not
broker-actual Bid. This is source-research classification parity ONLY; live
fills ALWAYS require original real executable Bid/Ask in the existing L7.

Specialist states/sleeves here belong to this archived STMR strategy FAMILY,
not all optimized JAN039/FEB045/FEB047 or arbitrary rolling regimes. No
calendar month/day/week is consulted to choose or tune a strategy.
"""
from __future__ import annotations
from dataclasses import dataclass

TF_WIDTH_MS = (14_400_000, 3_600_000, 900_000, 300_000)
TF_LABELS = ('H4', 'H1', 'M15', 'M5')


@dataclass(frozen=True)
class STMRState:
    time_ms: int
    h4: int
    h1: int
    m15: int
    m5: int
    ends_ms: tuple[int | None, int | None, int | None, int | None]
    # Under original research, first observed bucket may be truncated.
    # This stricter provenance flag is solely a V1 funding safety gate.
    fully_observed: bool

    def source_states(self) -> tuple[int, int, int, int]:
        return self.h4, self.h1, self.m15, self.m5


class _OriginalCompletedEMA:
    """As-of port of bar_states_span: closes of observed bars, EMA8/EMA21.

    Original function maps all ticks in bucket k to state of observed bar k-1,
    including when wall-clock buckets are missing. The first observed close
    seeds *both* EMAs and its state is precisely 0. First bucket is potentially
    incomplete for physical startup even though research state mapping is 0.
    """
    __slots__=('width', 'bucket', 'last_price', 'last_time', 'ema_fast',
               'ema_slow', 'current_state', 'completed_end', 'last_full',
               'forming_full', 'seen', 'skipped')

    def __init__(self, width_ms: int):
        if width_ms <= 0: raise ValueError('Timeframe width must be positive')
        self.width = int(width_ms)
        self.bucket: int | None = None
        self.last_price: int | None = None
        self.last_time = -1
        self.ema_fast: float | None = None
        self.ema_slow: float | None = None
        self.current_state = 0
        self.completed_end: int | None = None
        self.last_full = False
        self.forming_full = False
        self.seen = 0
        self.skipped = 0

    def on_quote(self, time_ms: int, bid_source_raw: int) -> int:
        if time_ms < self.last_time:
            raise ValueError('Out-of-order original STMR source quote')
        if bid_source_raw <= 0:
            raise ValueError('Invalid STMR source Bid')
        bucket = time_ms // self.width
        if self.bucket is None:
            self.bucket = bucket
            self.forming_full = False  # no real prior starting boundary
        elif bucket != self.bucket:
            if bucket < self.bucket: raise ValueError('Reversed source bucket')
            self.skipped += bucket - self.bucket - 1
            cl = float(self.last_price)
            if self.ema_fast is None:
                self.ema_fast = self.ema_slow = cl
            else:
                self.ema_fast = 2 / 9 * cl + (1 - 2 / 9) * self.ema_fast
                self.ema_slow = 2 / 22 * cl + (1 - 2 / 22) * self.ema_slow
            self.current_state = int(self.ema_fast > self.ema_slow) - int(self.ema_fast < self.ema_slow)
            self.completed_end = self.bucket * self.width + self.width
            self.last_full = self.forming_full
            self.bucket = bucket
            self.forming_full = True
        self.last_price = int(bid_source_raw)
        self.last_time = int(time_ms)
        self.seen += 1
        return self.current_state


class SourceSTMRCompletedStack:
    """Four independent completed source EMA periods; never HTF majority vote.

    Input price must be the actual declared source *feature price*; to
    reproduce STMR 032 source, compute per-quote original materialized Bid.
    This module must not supply synthetic quotes to the physical L7 kernel.
    """
    def __init__(self):
        self._bars = tuple(_OriginalCompletedEMA(w) for w in TF_WIDTH_MS)
        self._last = -1

    def on_quote(self, time_ms: int, *, source_bid_raw: int) -> STMRState:
        if time_ms < self._last: raise ValueError('Out-of-order source quote')
        states = tuple(bar.on_quote(time_ms, source_bid_raw) for bar in self._bars)
        self._last = int(time_ms)
        ends = tuple(bar.completed_end for bar in self._bars)
        # The original STMR state can be tested even when funding must fail
        # closed due to incomplete as-of prehistory or exact-boundary timing.
        full = all(bar.last_full and bar.completed_end is not None
                   and bar.completed_end < time_ms for bar in self._bars)
        return STMRState(int(time_ms), *states, ends, full)


def source_sleeve_state(session: int, h4: int, h1: int, m15: int, m5: int) -> tuple[int, int]:
    """Literal pure-Python port of JAN032 stmr_janjul.py::sleeve_state.

    This original classifier takes *distinct H4/H1/M15/M5 states* and an
    already-known session. The source's own L0 direction filter remains with
    the source event generator; the tuple is (sleeve, intended direction).
    """
    macro = h4 != 0 and h4 == h1
    if session == 0:
        if macro and m15 == m5 and m15 == -h1: return 0, m5
        if macro and m15 == -h1 and m5 == h1: return 1, m5
    elif session == 2:
        if macro and m15 == h1 and m5 == -h1: return 2, m5
        if macro and m15 == -h1 and m5 == h1: return 3, m5
    elif session == 3:
        if macro and m15 == m5 and m15 == -h1: return 4, m5
        if macro and m15 == m5 and m15 == h1: return 5, -m5
    elif session == 4:
        if h4 != 0 and h1 != 0 and h4 != h1:
            if m15 != 0 and m5 == -m15: return 6, m5
            if m15 == m5 and m15 != 0: return 7, -m5
    elif session == 5:
        if h4 == h1 and h1 == m15 and m15 == m5 and h4 != 0: return 8, m5
        if h4 != 0 and h1 != 0 and h4 != h1 and m15 != 0 and m5 == -m15: return 9, m5
        if macro and m15 == h1 and m5 == -h1: return 10, -m5
        if macro and m15 == m5 and m15 == -h1: return 11, m5
    return -1, 0
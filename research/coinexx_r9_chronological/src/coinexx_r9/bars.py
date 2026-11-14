from __future__ import annotations
from dataclasses import dataclass
from typing import Iterator, Iterable
from .models import Tick, SecondBar

class SecondBarBuilder:
    """Observed-second bars. Missing seconds are not synthesized."""
    def __init__(self) -> None:
        self._second: int | None = None
        self._first_msc = self._last_msc = 0
        self._count = 0
        self._bo = self._bh = self._bl = self._bc = 0
        self._ao = self._ah = self._al = self._ac = 0
        self._so = self._sh = self._sl = self._sc = 0

    def _finish(self) -> SecondBar | None:
        if self._second is None:
            return None
        return SecondBar(
            second=self._second,
            first_time_msc=self._first_msc,
            last_time_msc=self._last_msc,
            tick_count=self._count,
            bid_open_u=self._bo,
            bid_high_u=self._bh,
            bid_low_u=self._bl,
            bid_close_u=self._bc,
            ask_open_u=self._ao,
            ask_high_u=self._ah,
            ask_low_u=self._al,
            ask_close_u=self._ac,
            spread_open=self._so,
            spread_high=self._sh,
            spread_low=self._sl,
            spread_close=self._sc,
        )

    def update(self, t: Tick) -> SecondBar | None:
        spread = t.spread_points
        if self._second is None:
            self._second = t.time_s
            self._first_msc = self._last_msc = t.time_msc
            self._count = 1
            self._bo = self._bh = self._bl = self._bc = t.bid_u
            self._ao = self._ah = self._al = self._ac = t.ask_u
            self._so = self._sh = self._sl = self._sc = spread
            return None
        if t.time_s == self._second:
            self._last_msc = t.time_msc
            self._count += 1
            self._bh = max(self._bh, t.bid_u); self._bl = min(self._bl, t.bid_u); self._bc = t.bid_u
            self._ah = max(self._ah, t.ask_u); self._al = min(self._al, t.ask_u); self._ac = t.ask_u
            self._sh = max(self._sh, spread); self._sl = min(self._sl, spread); self._sc = spread
            return None
        completed = self._finish()
        self._second = t.time_s
        self._first_msc = self._last_msc = t.time_msc
        self._count = 1
        self._bo = self._bh = self._bl = self._bc = t.bid_u
        self._ao = self._ah = self._al = self._ac = t.ask_u
        self._so = self._sh = self._sl = self._sc = spread
        return completed

    def flush(self) -> SecondBar | None:
        out = self._finish()
        self._second = None
        return out


def iter_second_bars(ticks: Iterable[Tick]) -> Iterator[SecondBar]:
    b = SecondBarBuilder()
    for t in ticks:
        x = b.update(t)
        if x is not None:
            yield x
    x = b.flush()
    if x is not None:
        yield x


@dataclass(slots=True)
class CompletedM5Atr:
    period: int = 14
    _bar: int | None = None
    _high_u: int = 0
    _low_u: int = 0
    _close_u: int = 0
    _prev_close_u: int | None = None
    _seed: list[int] = None  # type: ignore[assignment]
    atr_u: float | None = None
    completed_bars: int = 0

    def __post_init__(self) -> None:
        self._seed = []

    def update(self, t: Tick) -> None:
        bar = (t.time_s // 300) * 300
        if self._bar is None:
            self._bar = bar
            self._high_u = self._low_u = self._close_u = t.bid_u
            return
        if bar == self._bar:
            self._high_u = max(self._high_u, t.bid_u)
            self._low_u = min(self._low_u, t.bid_u)
            self._close_u = t.bid_u
            return

        if self._prev_close_u is not None:
            tr = max(
                self._high_u - self._low_u,
                abs(self._high_u - self._prev_close_u),
                abs(self._low_u - self._prev_close_u),
            )
            if self.atr_u is None:
                self._seed.append(tr)
                if len(self._seed) == self.period:
                    self.atr_u = sum(self._seed) / self.period
            else:
                self.atr_u = (self.atr_u * (self.period - 1) + tr) / self.period
        self.completed_bars += 1
        self._prev_close_u = self._close_u
        self._bar = bar
        self._high_u = self._low_u = self._close_u = t.bid_u

    @property
    def ready(self) -> bool:
        return self.atr_u is not None and self.completed_bars >= self.period + 2

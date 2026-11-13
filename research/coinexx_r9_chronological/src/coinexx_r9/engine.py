from __future__ import annotations
from typing import Iterable, Protocol
from .models import Tick

class TickStrategy(Protocol):
    def on_tick(self, tick: Tick) -> None: ...

class ChronologicalEngine:
    """Minimal event loop: one call per source row, in source order, no resampling."""
    def __init__(self, strategy: TickStrategy) -> None:
        self.strategy = strategy
        self.ticks_processed = 0
        self.first_time_msc: int | None = None
        self.last_time_msc: int | None = None

    def run(self, ticks: Iterable[Tick]) -> None:
        for tick in ticks:
            if self.first_time_msc is None:
                self.first_time_msc = tick.time_msc
            self.last_time_msc = tick.time_msc
            self.strategy.on_tick(tick)
            self.ticks_processed += 1

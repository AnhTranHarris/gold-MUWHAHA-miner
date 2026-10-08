from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import math

ROOT = Path(__file__).resolve().parents[3]
EA = ROOT / "Experts/GoldMuwahahaMiner_DeltaAAlpha_V1.mq5"

src = EA.read_text(encoding="utf-8")

required = [
    "struct DAAV1GridCycle",
    "struct DAAV1GridEventRecord",
    "DAAV1TouchKey g_touch_keys[]",
    "DAAV1GridEventRecord g_event_records[]",
    "void UpdateSessionGridCycle",
    "void ManufactureFirstTouchEvent",
    "bool RecordGenealogyEvent",
    "bool TouchAlreadyOwned",
    "void ResetGenealogyMemory",
    "input int InpMaxCycleAgeMinutes=720",
    "input int InpMaxTouchKeys=8192",
    "input int InpMaxEventRecords=8192",
]
for token in required:
    assert token in src, token

body = src[src.index("void OrchestrateV1"):src.index("bool InitMtfHandles")]
order = [
    "TickToUtcMs",
    "ApplySessionGeometry",
    "UpdateSessionGridCycle",
    "RefreshCompletedMTF",
    "ManufactureFirstTouchEvent",
    "ApplyHourlyHarvest",
    "ApplyWatchdogRegime",
    "ApplyTrendWithinTrend",
    "ApplyWrongDirectionRecovery",
    "ApplyCapitalGovernor",
    "WriteDiagnostic",
]
pos = [body.index(x) for x in order]
assert pos == sorted(pos), pos

# Unit 002 remains observe-only.
for forbidden in (
    "g_trade.Buy(",
    "g_trade.Sell(",
    "g_trade.PositionOpen(",
    "trade.Buy(",
    "trade.Sell(",
):
    assert forbidden not in src, forbidden

assert "One session-grid event maximum per market tick" in src
assert "the event represents the FIRST crossed boundary" in src
assert "Snapshot the original completed MTF/session context at birth" in src
assert "CopyBuffer(fast_handle,0,1,1" in src
assert "CopyBuffer(slow_handle,0,1,1" in src


@dataclass
class Event:
    event_id: int
    generation: int
    birth_ms: int
    session: str
    from_cell: int
    to_cell: int
    landing_cell: int
    direction: int
    boundary: float
    mtf: tuple[int, int, int, int]


@dataclass
class Cycle:
    generation: int = 0
    initialized: bool = False
    active: bool = False
    start_ms: int = 0
    session: str = ""
    anchor: float = 0.0
    gap: float = 0.0
    last_cell: int = 0
    touches: set[tuple[int, int]] = field(default_factory=set)
    events: list[Event] = field(default_factory=list)
    seq: int = 0

    def restart(self, now_ms: int, session: str, mid: float, gap: float) -> None:
        self.generation += 1
        self.initialized = True
        self.active = gap > 0.0
        self.start_ms = now_ms
        self.session = session
        self.anchor = mid
        self.gap = gap
        self.last_cell = 0
        self.touches.clear()
        self.events.clear()

    def cell(self, mid: float) -> int:
        if not self.active or self.gap <= 0:
            return 0
        return math.floor((mid - self.anchor) / self.gap)

    def tick(self, now_ms: int, mid: float, mtf=(1, 1, 1, 1)) -> Event | None:
        if not self.active:
            return None
        landing = self.cell(mid)
        prior = self.last_cell
        if landing == prior:
            return None
        direction = 1 if landing > prior else -1
        target = prior + direction
        boundary = (
            self.anchor + target * self.gap
            if direction > 0
            else self.anchor + prior * self.gap
        )
        self.last_cell = landing
        key = (target, direction)
        if key in self.touches:
            return None
        self.touches.add(key)
        self.seq += 1
        e = Event(
            self.seq,
            self.generation,
            now_ms,
            self.session,
            prior,
            target,
            landing,
            direction,
            boundary,
            mtf,
        )
        self.events.append(e)
        return e


# Deterministic synthetic behavior contract.
c = Cycle()
c.restart(0, "ASIA", 100.0, 0.75)
assert c.tick(1, 100.10) is None

e1 = c.tick(2, 100.80, (1, 1, -1, -1))
assert e1 is not None
assert (e1.from_cell, e1.to_cell, e1.landing_cell, e1.direction) == (0, 1, 1, 1)
assert e1.mtf == (1, 1, -1, -1)

e2 = c.tick(3, 100.70, (1, 1, 1, -1))
assert e2 is not None
assert (e2.from_cell, e2.to_cell, e2.landing_cell, e2.direction) == (1, 0, 0, -1)

# Same upward cell ownership is duplicate within the cycle.
assert c.tick(4, 100.80) is None

# A multi-cell jump creates exactly one event: first crossed boundary only.
e3 = c.tick(5, 103.20)
assert e3 is not None
assert e3.to_cell == 2
assert e3.landing_cell == 4
assert len(c.events) == 3

# Session handoff creates fresh ownership.
old_generation = c.generation
c.restart(6, "LONDON_OPEN", 103.20, 0.0)
assert c.generation == old_generation + 1
assert not c.active
assert c.events == []
assert c.tick(7, 104.0) is None

c.restart(8, "LONDON", 103.20, 1.0)
e4 = c.tick(9, 104.25, (-1, -1, -1, 1))
assert e4 is not None
assert e4.session == "LONDON"
assert e4.generation == c.generation
assert e4.mtf == (-1, -1, -1, 1)

print("DAA V1 MT5 unit 002 session/genealogy QA: PASS")

from __future__ import annotations

import csv
from bisect import bisect_right
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from delta_b_grid_kernel import (
    CalendarEvent,
    EventPhase,
    GridConfig,
    Importance,
    Session,
    classify_session,
)


_EVENT_RANK = {
    EventPhase.NORMAL: 0,
    EventPhase.STABILIZATION_MEDIUM: 1,
    EventPhase.PRE_MEDIUM: 2,
    EventPhase.DISCOVERY_MEDIUM: 3,
    EventPhase.RELEASE_MEDIUM: 4,
    EventPhase.STABILIZATION_HIGH: 5,
    EventPhase.PRE_HIGH: 6,
    EventPhase.DISCOVERY_HIGH: 7,
    EventPhase.RELEASE_HIGH: 8,
}


@dataclass(frozen=True)
class EventTransition:
    time_ms: int
    phase: EventPhase


def _dt_to_ms(ts: datetime) -> int:
    if ts.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return int(round(ts.astimezone(timezone.utc).timestamp() * 1000.0))


def load_ff_usd_medium_high(path: str | Path) -> list[CalendarEvent]:
    """Load the frozen DELTA-B compact cache.

    The cache is intentionally tiny: timestamp, USD, Medium/High, event name.
    Actual/forecast/previous values are not carried into the hot-path context.
    """
    events: list[CalendarEvent] = []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        required = {"date_gmt", "time_gmt", "currency", "impact", "event"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError("event cache schema mismatch")
        for row in reader:
            if (row.get("currency") or "").upper() != "USD":
                continue
            impact_raw = (row.get("impact") or "").upper()
            if impact_raw not in {"MEDIUM", "HIGH"}:
                continue
            dt = datetime.strptime(
                f"{row['date_gmt']} {row['time_gmt']}",
                "%a %b %d %Y %H:%M",
            ).replace(tzinfo=timezone.utc)
            events.append(
                CalendarEvent(
                    time_utc=dt,
                    importance=Importance[impact_raw],
                    currency="USD",
                    name=row.get("event") or "",
                )
            )
    events.sort(key=lambda e: e.time_utc)
    return events


def _phase_for_event(ms: int, event: CalendarEvent, cfg: GridConfig) -> EventPhase:
    t0 = _dt_to_ms(event.time_utc)
    window = cfg.high_window if event.importance is Importance.HIGH else cfg.medium_window
    minute = 60_000
    pre_start = t0 - window.pre_min * minute
    release_end = t0 + window.release_min * minute
    discovery_end = release_end + window.discovery_min * minute
    stabilization_end = discovery_end + window.stabilization_min * minute

    if pre_start <= ms < t0:
        return EventPhase.PRE_HIGH if event.importance is Importance.HIGH else EventPhase.PRE_MEDIUM
    if t0 <= ms < release_end:
        return EventPhase.RELEASE_HIGH if event.importance is Importance.HIGH else EventPhase.RELEASE_MEDIUM
    if release_end <= ms < discovery_end:
        return EventPhase.DISCOVERY_HIGH if event.importance is Importance.HIGH else EventPhase.DISCOVERY_MEDIUM
    if discovery_end <= ms < stabilization_end:
        return (
            EventPhase.STABILIZATION_HIGH
            if event.importance is Importance.HIGH
            else EventPhase.STABILIZATION_MEDIUM
        )
    return EventPhase.NORMAL


def compile_event_transitions(
    events: Iterable[CalendarEvent],
    cfg: GridConfig,
) -> list[EventTransition]:
    """Compile overlapping events into a minimal piecewise-constant phase schedule.

    Work is done once before replay. The tick loop then advances a pointer through
    this small transition vector instead of scanning the event calendar.
    """
    evs = list(events)
    minute = 60_000
    boundaries: set[int] = set()
    for event in evs:
        t0 = _dt_to_ms(event.time_utc)
        window = cfg.high_window if event.importance is Importance.HIGH else cfg.medium_window
        boundaries.update(
            {
                t0 - window.pre_min * minute,
                t0,
                t0 + window.release_min * minute,
                t0 + (window.release_min + window.discovery_min) * minute,
                t0
                + (
                    window.release_min
                    + window.discovery_min
                    + window.stabilization_min
                )
                * minute,
            }
        )

    out: list[EventTransition] = []
    current = EventPhase.NORMAL
    for ms in sorted(boundaries):
        best = EventPhase.NORMAL
        for event in evs:
            phase = _phase_for_event(ms, event, cfg)
            if _EVENT_RANK[phase] > _EVENT_RANK[best]:
                best = phase
        if best is not current:
            out.append(EventTransition(ms, best))
            current = best
    return out


class EventPhaseCursor:
    """Amortized O(1) phase lookup for monotonic tick streams.

    On a rewind/restart, lookup falls back to one binary search.
    """

    def __init__(self, transitions: Iterable[EventTransition]) -> None:
        self.transitions = list(transitions)
        self.times = [x.time_ms for x in self.transitions]
        self.phases = [x.phase for x in self.transitions]
        self._next = 0
        self._phase = EventPhase.NORMAL
        self._last_ms: int | None = None

    def phase_at_ms(self, ms: int) -> EventPhase:
        if self._last_ms is not None and ms < self._last_ms:
            pos = bisect_right(self.times, ms)
            self._next = pos
            self._phase = self.phases[pos - 1] if pos else EventPhase.NORMAL
            self._last_ms = ms
            return self._phase

        while self._next < len(self.times) and ms >= self.times[self._next]:
            self._phase = self.phases[self._next]
            self._next += 1
        self._last_ms = ms
        return self._phase


class FastContextClock:
    """Very small hot-path context engine.

    Session timezone conversion is performed at most once per UTC minute.
    Event phase is a pointer advance through precompiled boundaries.
    """

    def __init__(self, event_cursor: EventPhaseCursor) -> None:
        self.events = event_cursor
        self._minute_key: int | None = None
        self._session = Session.ROLLOVER
        self.session_recomputes = 0

    def state_at_ms(self, ms: int) -> tuple[Session, EventPhase]:
        minute_key = ms // 60_000
        if minute_key != self._minute_key:
            ts = datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc)
            self._session = classify_session(ts)
            self._minute_key = minute_key
            self.session_recomputes += 1
        return self._session, self.events.phase_at_ms(ms)


def build_context_clock(
    cache_path: str | Path,
    cfg: GridConfig | None = None,
) -> tuple[FastContextClock, list[CalendarEvent], list[EventTransition]]:
    cfg = cfg or GridConfig()
    events = load_ff_usd_medium_high(cache_path)
    transitions = compile_event_transitions(events, cfg)
    return FastContextClock(EventPhaseCursor(transitions)), events, transitions

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from delta_b_context_clock import (
    EventPhaseCursor,
    FastContextClock,
    build_context_clock,
    compile_event_transitions,
    load_ff_usd_medium_high,
)
from delta_b_grid_kernel import CalendarEvent, EventPhase, GridConfig, Importance, Session


class ContextClockTests(unittest.TestCase):
    def test_compact_cache_load(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "events.csv"
            p.write_text(
                "date_gmt,time_gmt,currency,impact,event\n"
                "Mon Jan 5 2026,15:00,USD,High,ISM Manufacturing PMI\n"
                "Tue Jan 6 2026,19:00,USD,Medium,President Speaks\n"
                "Tue Jan 6 2026,20:00,EUR,High,Ignored EUR\n",
                encoding="utf-8",
            )
            events = load_ff_usd_medium_high(p)
            self.assertEqual(len(events), 2)
            self.assertEqual(events[0].importance, Importance.HIGH)

    def test_transition_boundaries(self):
        cfg = GridConfig()
        t0 = datetime(2026, 1, 5, 15, 0, tzinfo=timezone.utc)
        transitions = compile_event_transitions(
            [CalendarEvent(t0, Importance.HIGH)],
            cfg,
        )
        cursor = EventPhaseCursor(transitions)
        ms = lambda dt: int(dt.timestamp() * 1000)
        self.assertEqual(
            cursor.phase_at_ms(ms(t0 - timedelta(minutes=46))),
            EventPhase.NORMAL,
        )
        self.assertEqual(
            cursor.phase_at_ms(ms(t0 - timedelta(minutes=45))),
            EventPhase.PRE_HIGH,
        )
        self.assertEqual(cursor.phase_at_ms(ms(t0)), EventPhase.RELEASE_HIGH)
        self.assertEqual(
            cursor.phase_at_ms(ms(t0 + timedelta(minutes=10))),
            EventPhase.DISCOVERY_HIGH,
        )
        self.assertEqual(
            cursor.phase_at_ms(ms(t0 + timedelta(minutes=40))),
            EventPhase.STABILIZATION_HIGH,
        )
        self.assertEqual(
            cursor.phase_at_ms(ms(t0 + timedelta(minutes=100))),
            EventPhase.NORMAL,
        )

    def test_high_priority_wins_overlap(self):
        cfg = GridConfig()
        base = datetime(2026, 1, 5, 15, 0, tzinfo=timezone.utc)
        events = [
            CalendarEvent(base, Importance.MEDIUM),
            CalendarEvent(base + timedelta(minutes=2), Importance.HIGH),
        ]
        cursor = EventPhaseCursor(compile_event_transitions(events, cfg))
        at = int((base + timedelta(minutes=2)).timestamp() * 1000)
        self.assertEqual(cursor.phase_at_ms(at), EventPhase.RELEASE_HIGH)

    def test_rewind_binary_search(self):
        cfg = GridConfig()
        base = datetime(2026, 1, 5, 15, 0, tzinfo=timezone.utc)
        cursor = EventPhaseCursor(
            compile_event_transitions([CalendarEvent(base, Importance.HIGH)], cfg)
        )
        after = int((base + timedelta(minutes=20)).timestamp() * 1000)
        before = int((base - timedelta(minutes=20)).timestamp() * 1000)
        self.assertEqual(cursor.phase_at_ms(after), EventPhase.DISCOVERY_HIGH)
        self.assertEqual(cursor.phase_at_ms(before), EventPhase.PRE_HIGH)

    def test_session_timezone_work_only_once_per_minute(self):
        cursor = EventPhaseCursor([])
        clock = FastContextClock(cursor)
        base = datetime(2026, 7, 15, 7, 30, tzinfo=timezone.utc)
        ms0 = int(base.timestamp() * 1000)
        for i in range(1000):
            session, phase = clock.state_at_ms(ms0 + i)
            self.assertEqual(session, Session.LONDON)
            self.assertEqual(phase, EventPhase.NORMAL)
        self.assertEqual(clock.session_recomputes, 1)

    def test_build_context_clock(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "events.csv"
            p.write_text(
                "date_gmt,time_gmt,currency,impact,event\n"
                "Mon Jan 5 2026,15:00,USD,High,ISM Manufacturing PMI\n",
                encoding="utf-8",
            )
            clock, events, transitions = build_context_clock(p)
            self.assertEqual(len(events), 1)
            self.assertGreaterEqual(len(transitions), 5)
            ms = int(datetime(2026, 1, 5, 15, 0, tzinfo=timezone.utc).timestamp() * 1000)
            _, phase = clock.state_at_ms(ms)
            self.assertEqual(phase, EventPhase.RELEASE_HIGH)


if __name__ == "__main__":
    unittest.main()

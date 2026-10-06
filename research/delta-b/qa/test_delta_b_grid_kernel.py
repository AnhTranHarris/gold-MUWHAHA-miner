from datetime import datetime, timedelta, timezone
import unittest

from delta_b_grid_kernel import (
    AdaptiveQEstimator,
    CalendarEvent,
    DirectionalChangeTracker,
    EventPhase,
    GridConfig,
    GridState,
    Importance,
    IntrinsicGridKernel,
    Session,
    classify_event_phase,
    classify_session,
)


class GridKernelTests(unittest.TestCase):
    def test_london_dst(self):
        self.assertEqual(
            classify_session(datetime(2026, 1, 15, 8, 30, tzinfo=timezone.utc)),
            Session.LONDON,
        )
        self.assertEqual(
            classify_session(datetime(2026, 7, 15, 7, 30, tzinfo=timezone.utc)),
            Session.LONDON,
        )

    def test_high_event_beats_medium(self):
        now = datetime(2026, 1, 8, 13, 30, tzinfo=timezone.utc)
        cfg = GridConfig()
        events = [
            CalendarEvent(now + timedelta(minutes=10), Importance.MEDIUM),
            CalendarEvent(now + timedelta(minutes=20), Importance.HIGH),
        ]
        self.assertEqual(classify_event_phase(now, events, cfg), EventPhase.PRE_HIGH)

    def test_non_usd_ignored(self):
        now = datetime(2026, 1, 8, 13, 30, tzinfo=timezone.utc)
        self.assertEqual(
            classify_event_phase(
                now,
                [CalendarEvent(now, Importance.HIGH, "EUR")],
                GridConfig(),
            ),
            EventPhase.NORMAL,
        )

    def test_q_rises_with_cost(self):
        cfg = GridConfig(q_floor=0.01, cost_mult=2.0, noise_mult=1.0)
        q = AdaptiveQEstimator(cfg)
        t = datetime(2026, 1, 1, tzinfo=timezone.utc)
        a = q.update(ts_utc=t, bid=100.0, ask=100.1)
        b = q.update(
            ts_utc=t + timedelta(milliseconds=10),
            bid=100.0,
            ask=100.5,
        )
        self.assertGreater(b.q_base, a.q_base)

    def test_high_release_expands_q_and_reduces_authority(self):
        cfg = GridConfig(q_floor=0.01, cost_mult=1.0, noise_mult=1.0)
        q = AdaptiveQEstimator(cfg)
        t = datetime(2026, 1, 1, 13, 0, tzinfo=timezone.utc)
        normal = q.update(
            ts_utc=t,
            bid=100.0,
            ask=100.1,
            event_phase=EventPhase.NORMAL,
        )
        high = q.update(
            ts_utc=t + timedelta(seconds=1),
            bid=100.0,
            ask=100.1,
            event_phase=EventPhase.RELEASE_HIGH,
        )
        self.assertGreater(high.q_context, high.q_base)
        self.assertLess(
            high.adjustment.entry_authority,
            normal.adjustment.entry_authority,
        )

    def test_threshold_does_not_shrink_mid_leg(self):
        tracker = DirectionalChangeTracker(1.0)
        t = datetime(2026, 1, 1, tzinfo=timezone.utc)
        tracker.update(t, 100.0, 1.0)
        tracker.update(t + timedelta(seconds=1), 100.2, 2.0)
        before = tracker.active_threshold
        tracker.update(t + timedelta(seconds=2), 100.3, 0.2)
        self.assertEqual(tracker.active_threshold, before)

    def test_directional_event(self):
        tracker = DirectionalChangeTracker(1.0)
        t = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.assertIsNone(tracker.update(t, 100.0, 1.0))
        event = tracker.update(t + timedelta(seconds=1), 101.1, 1.0)
        self.assertIsNotNone(event)
        self.assertEqual(event.direction, 1)

    def test_shock_state(self):
        cfg = GridConfig(
            q_floor=0.01,
            cost_mult=1.0,
            noise_mult=1.0,
            shock_min_components=1,
            noise_window=16,
            path_window=16,
            spread_window=32,
            interval_window=32,
        )
        kernel = IntrinsicGridKernel(cfg)
        t = datetime(2026, 1, 1, tzinfo=timezone.utc)
        for i in range(24):
            kernel.update(
                ts_utc=t + timedelta(milliseconds=100 * i),
                bid=100.0 + 0.001 * i,
                ask=100.02 + 0.001 * i,
            )
        snap = kernel.update(
            ts_utc=t + timedelta(milliseconds=2500),
            bid=99.5,
            ask=100.5,
        )
        self.assertEqual(snap.state, GridState.CHURN_SHOCK)


if __name__ == "__main__":
    unittest.main()

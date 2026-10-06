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

    def test_flat_spread_midrank_does_not_fake_tail_stress(self):
        cfg = GridConfig(
            q_floor=0.01,
            q_ceiling=100.0,
            cost_mult=1.0,
            noise_mult=1.0,
            noise_window=16,
            path_window=16,
            spread_window=32,
            interval_window=32,
        )
        q = AdaptiveQEstimator(cfg)
        t = datetime(2026, 1, 1, 13, 0, tzinfo=timezone.utc)
        snap = None
        for i in range(24):
            snap = q.update(
                ts_utc=t + timedelta(milliseconds=100 * i),
                bid=100.0 + 0.001 * i,
                ask=100.1 + 0.001 * i,
            )
        self.assertAlmostEqual(snap.spread_percentile, 0.5, places=12)
        self.assertLess(snap.observed_stress, 0.5)

    def test_calm_high_release_uses_partial_not_max_envelope(self):
        cfg = GridConfig(
            q_floor=0.01,
            q_ceiling=100.0,
            cost_mult=1.0,
            noise_mult=1.0,
            shock_min_components=4,
            noise_window=16,
            path_window=16,
            spread_window=32,
            interval_window=32,
        )
        q = AdaptiveQEstimator(cfg)
        t = datetime(2026, 1, 1, 13, 0, tzinfo=timezone.utc)
        snap = None
        for i in range(24):
            snap = q.update(
                ts_utc=t + timedelta(milliseconds=100 * i),
                bid=100.0 + 0.001 * i,
                ask=100.1 + 0.001 * i,
                event_phase=EventPhase.RELEASE_HIGH,
            )
        ratio = snap.q_context / snap.q_base
        self.assertGreaterEqual(snap.event_activation, 0.40)
        self.assertLess(snap.event_activation, 1.0)
        self.assertGreater(ratio, 1.0)
        self.assertLess(ratio, 1.80)
        self.assertGreater(snap.adjustment.entry_authority, 0.20)

    def test_scheduled_shock_never_exceeds_high_release_cap(self):
        cfg = GridConfig(
            q_floor=0.01,
            q_ceiling=100.0,
            cost_mult=1.0,
            noise_mult=1.0,
            shock_min_components=1,
            noise_window=16,
            path_window=16,
            spread_window=32,
            interval_window=32,
        )
        q = AdaptiveQEstimator(cfg)
        t = datetime(2026, 1, 1, 13, 0, tzinfo=timezone.utc)
        for i in range(24):
            q.update(
                ts_utc=t + timedelta(milliseconds=100 * i),
                bid=100.0 + 0.001 * i,
                ask=100.1 + 0.001 * i,
                event_phase=EventPhase.RELEASE_HIGH,
            )
        snap = q.update(
            ts_utc=t + timedelta(milliseconds=2450),
            bid=99.5,
            ask=100.7,
            event_phase=EventPhase.RELEASE_HIGH,
        )
        self.assertTrue(snap.shock_active)
        ratio = snap.q_context / snap.q_base
        self.assertLessEqual(ratio, 1.80 + 1e-12)
        self.assertGreaterEqual(snap.adjustment.entry_authority, 0.20 - 1e-12)
        self.assertGreaterEqual(snap.observed_stress, 0.0)
        self.assertLessEqual(snap.observed_stress, 1.0)
        self.assertGreaterEqual(snap.event_activation, 0.0)
        self.assertLessEqual(snap.event_activation, 1.0)

    def test_normal_unscheduled_shock_retains_defensive_multiplier(self):
        cfg = GridConfig(
            q_floor=0.01,
            q_ceiling=100.0,
            cost_mult=1.0,
            noise_mult=1.0,
            shock_min_components=1,
            noise_window=16,
            path_window=16,
            spread_window=32,
            interval_window=32,
        )
        q = AdaptiveQEstimator(cfg)
        t = datetime(2026, 1, 1, 13, 0, tzinfo=timezone.utc)
        for i in range(24):
            q.update(
                ts_utc=t + timedelta(milliseconds=100 * i),
                bid=100.0 + 0.001 * i,
                ask=100.1 + 0.001 * i,
                event_phase=EventPhase.NORMAL,
            )
        snap = q.update(
            ts_utc=t + timedelta(milliseconds=2450),
            bid=99.5,
            ask=100.7,
            event_phase=EventPhase.NORMAL,
        )
        self.assertTrue(snap.shock_active)
        self.assertAlmostEqual(snap.q_context / snap.q_base, 1.35, places=12)
        self.assertAlmostEqual(snap.adjustment.entry_authority, 0.50, places=12)
        self.assertEqual(snap.event_activation, 0.0)

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

    def test_reclaim_is_event_driven_not_persistent(self):
        cfg = GridConfig(
            q_floor=1.0,
            q_ceiling=10.0,
            cost_mult=0.1,
            noise_mult=0.1,
            shock_min_components=4,
            noise_window=8,
            path_window=8,
            spread_window=8,
            interval_window=8,
        )
        kernel = IntrinsicGridKernel(cfg)
        t = datetime(2026, 1, 1, tzinfo=timezone.utc)
        # Establish higher-scale UP, let L0 diverge DOWN without flipping L1,
        # then require a new L0 UP event to realign with the higher owner.
        prices = [100.0, 102.2, 101.1, 102.2]
        snaps = []
        for i, price in enumerate(prices):
            snaps.append(
                kernel.update(
                    ts_utc=t + timedelta(seconds=i),
                    bid=price,
                    ask=price,
                )
            )
        self.assertNotEqual(snaps[2].state, GridState.RECLAIM)
        self.assertEqual(snaps[3].state, GridState.RECLAIM)
        next_snap = kernel.update(
            ts_utc=t + timedelta(seconds=4),
            bid=102.3,
            ask=102.3,
        )
        self.assertNotEqual(next_snap.state, GridState.RECLAIM)

    def test_flip_away_from_higher_owner_is_not_reclaim(self):
        cfg = GridConfig(
            q_floor=1.0,
            q_ceiling=10.0,
            cost_mult=0.1,
            noise_mult=0.1,
            shock_min_components=4,
            noise_window=8,
            path_window=8,
            spread_window=8,
            interval_window=8,
        )
        kernel = IntrinsicGridKernel(cfg)
        t = datetime(2026, 1, 1, tzinfo=timezone.utc)
        for i, price in enumerate([100.0, 102.2]):
            kernel.update(
                ts_utc=t + timedelta(seconds=i),
                bid=price,
                ask=price,
            )
        snap = kernel.update(
            ts_utc=t + timedelta(seconds=2),
            bid=101.1,
            ask=101.1,
        )
        self.assertNotEqual(snap.state, GridState.RECLAIM)

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

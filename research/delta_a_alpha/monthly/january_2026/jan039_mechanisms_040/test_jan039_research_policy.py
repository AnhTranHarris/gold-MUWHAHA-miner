"""Offline invariants for isolated, non-promoted JAN039 research adapter."""
import unittest
from dataclasses import replace
from jan039_research_policy import (
    AdmissionSnapshot, BootstrapContext, CompletedBar, Params,
    admission, bootstrap_status, first_executable_profit_take,
    january_like_adaptation_approved, phase_of_utc_hour,
    quote_start_deadline_exceeded,
)


class TestJan039ResearchPolicy(unittest.TestCase):
    def setUp(self):
        self.s = AdmissionSnapshot(
            timestamp_ms=0, source_id=26, direction=-1,
            spread_usd=0.6, signed_impulse_20s=-0.7,
            v1_completed_htf_permission=True, v1_session_and_geometry_permission=True,
            broker_can_accept_order=True, global_open=200, direction_open=200,
            per_tick_submitted=0, per_second_submitted=0, watchdog_open=0,
            watchdog_same_cell_side_open=0, s26_open=12, s27_open_in_entry_phase=0,
        )

    def test_phase_clock_not_month_id(self):
        self.assertEqual(phase_of_utc_hour(0), 0)
        self.assertEqual(phase_of_utc_hour(5 * 600000), 5)
        self.assertEqual(phase_of_utc_hour(6 * 600000), 0)
        self.assertEqual(first_executable_profit_take(27, 0, True), 60.)
        self.assertEqual(first_executable_profit_take(27, 2 * 600000, True), 50.)
        self.assertEqual(first_executable_profit_take(27, 4 * 600000, True), 35.)
        self.assertIsNone(first_executable_profit_take(27, 1 * 600000, True))
        self.assertIsNone(first_executable_profit_take(27, 2 * 600000, False))
        self.assertEqual(first_executable_profit_take(26, 0, True), 35.)

    def test_source_caps_and_quote_rate(self):
        self.assertEqual(admission(replace(self.s, s26_open=432))[1], 'S26_CAP')
        self.assertEqual(admission(replace(self.s, per_second_submitted=3))[1], 'ORDER_RATE')
        self.assertEqual(admission(replace(self.s, global_open=512))[1], 'GLOBAL_OR_SIDE_CAP')
        self.assertEqual(admission(replace(self.s, broker_can_accept_order=False))[1],
                         'BROKER_MARGIN_EXECUTION_GATE')
        self.assertEqual(admission(replace(self.s, v1_completed_htf_permission=False))[1],
                         'V1_STRUCTURAL_PERMISSION')

    def test_source27_phase_limit(self):
        s = replace(self.s, source_id=27, timestamp_ms=0,
                    s27_open_in_entry_phase=224)
        self.assertEqual(admission(s)[1], 'S27_PHASE_0_CAP')
        self.assertEqual(admission(replace(s, timestamp_ms=5*600000,
                                           s27_open_in_entry_phase=128))[1], 'S27_PHASE_5_CAP')

    def test_frozen_upstream_source_mask(self):
        self.assertEqual(admission(replace(self.s, source_id=17))[1],
                         'JAN037_SOURCE_EXCLUSION')

    def test_watchdog_and_exclusion(self):
        self.assertEqual(admission(replace(self.s, source_id=0, watchdog_open=8))[1],
                         'WATCHDOG_CAP')
        s = replace(self.s, source_id=27, timestamp_ms=600000)
        self.assertEqual(admission(s)[1], 'JAN039_EXPERIMENTAL_PHASE_MASK')

    def test_missing_htf_history_blocks_trading(self):
        bars = {name: CompletedBar(end_ms=1000, close=1, high=2, low=0)
                for name in ('H4', 'H1', 'M15', 'M5')}
        state = BootstrapContext(quote_ms=2000, first_valid_quote_ms=1000,
                                 quote_valid=True, broker_connected=True,
                                 complete_htf=bars, session_known=True,
                                 grid_anchor_initialized=True,
                                 risk_broker_verified=True)
        self.assertTrue(bootstrap_status(state)[0])
        self.assertFalse(quote_start_deadline_exceeded(state))
        self.assertFalse(bootstrap_status(replace(state,
                    complete_htf={**bars, 'H4': CompletedBar(end_ms=3000,
                                                             close=1, high=2, low=0)}))[0])
        self.assertTrue(quote_start_deadline_exceeded(replace(state, quote_ms=302000)))

    def test_non_calibrated_january_mode_fails_closed(self):
        self.assertFalse(january_like_adaptation_approved(correlation_calibrated=True,
                         prior_month_regression_passed=True,
                         forward_validation_passed=False))
        self.assertTrue(january_like_adaptation_approved(correlation_calibrated=True,
                        prior_month_regression_passed=True,
                        forward_validation_passed=True))


if __name__ == '__main__':
    unittest.main()
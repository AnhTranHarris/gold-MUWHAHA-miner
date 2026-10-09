import unittest
import sys
from pathlib import Path
_runtime = Path(__file__).resolve().parents[1] / "runtime"
if _runtime.is_dir():
    sys.path.insert(0, str(_runtime))
from v1_startup_contract_031 import (
    CONTRACTS, TIMEFRAMES, FIVE_MIN_MS, CompletedBarEvidence, StartupFrame,
    StartupGate, Phase, MaturedOutcome, ObservationLedger,
)
T0 = 1767225600000  # January 1, 2026 at 00:00 UTC
FIRST_QUOTE = T0 + 23 * 3600000  # historical market re-opening example, not first-tick certification


def f(now, *, with_history=True, market_open=True, signal=False, admitted=False,
      spread=True, broker=True):
    return StartupFrame(
        now_ms=now, executable_quote=market_open, market_open=market_open,
        broker_ready=broker, margin_checked=True, spread_acceptable=spread,
        completed_bars=tuple(CompletedBarEvidence(tf, FIRST_QUOTE - 10000, True)
                             for tf in TIMEFRAMES) if with_history else (),
        active_layer_contracts=CONTRACTS, original_v1_signal=signal,
        governor_admits=admitted,
    )

class TestStartup(unittest.TestCase):
    def test_closed_market_does_not_start_deadline(self):
        g=StartupGate(T0)
        self.assertEqual(g.observe(f(T0,market_open=False)), Phase.MARKET_CLOSED)
        self.assertEqual(g.state.five_minute_readiness,"NOT_EVALUABLE_MARKET_NOT_YET_TRADABLE")
        self.assertEqual(g.observe(f(FIRST_QUOTE)), Phase.READY_NO_SIGNAL)
        self.assertEqual(g.state.five_minute_readiness,"PASS")
        self.assertIsNone(g.state.first_funded_ms)

    def test_ready_immediately_not_waiting_for_online_history(self):
        g=StartupGate(T0)
        self.assertEqual(g.observe(f(FIRST_QUOTE)),Phase.READY_NO_SIGNAL)
        self.assertEqual(g.observe(f(FIRST_QUOTE+4000,signal=True,admitted=True)),Phase.SIGNAL_ELIGIBLE)
        self.assertEqual(g.state.first_eligible_ms,FIRST_QUOTE+4000)
        self.assertEqual(g.state.five_minute_readiness,"PASS")
        g.record_funded(FIRST_QUOTE+4000)
        self.assertEqual(g.state.first_funded_ms,FIRST_QUOTE+4000)

    def test_missing_real_history_is_honest_fail(self):
        g=StartupGate(T0)
        self.assertEqual(g.observe(f(FIRST_QUOTE,with_history=False)),Phase.HISTORY_REQUIRED)
        self.assertEqual(g.observe(f(FIRST_QUOTE+FIVE_MIN_MS,with_history=False)),Phase.HISTORY_REQUIRED)
        self.assertEqual(g.state.five_minute_readiness,"FAIL_INCOMPLETE_INITIALIZATION")
        self.assertIsNone(g.state.first_eligible_ms)

    def test_no_forced_fill_because_timer_elapsed(self):
        g=StartupGate(T0)
        g.observe(f(FIRST_QUOTE))
        g.observe(f(FIRST_QUOTE+FIVE_MIN_MS+1))
        self.assertIsNone(g.state.first_funded_ms)
        self.assertEqual(g.state.five_minute_readiness,"PASS")
        with self.assertRaises(ValueError):g.record_funded(FIRST_QUOTE+FIVE_MIN_MS+1)

    def test_no_future_bars(self):
        g=StartupGate(T0)
        e=tuple(CompletedBarEvidence(tf,FIRST_QUOTE+60000,True) for tf in TIMEFRAMES)
        frame=f(FIRST_QUOTE)
        frame=StartupFrame(**{**frame.__dict__,"completed_bars":e})
        self.assertEqual(g.observe(frame),Phase.HISTORY_REQUIRED)

    def test_quotes_technically_tradable_but_spread_not_ok(self):
        g=StartupGate(T0)
        self.assertEqual(g.observe(f(FIRST_QUOTE,spread=False,signal=True,admitted=True)),Phase.INFRASTRUCTURE_REQUIRED)
        self.assertIsNone(g.state.first_ready_ms)

    def test_missing_layer_blocks_complete_v1(self):
        g=StartupGate(T0)
        base=f(FIRST_QUOTE,signal=True,admitted=True)
        frame=StartupFrame(**{**base.__dict__,"active_layer_contracts":CONTRACTS[:-1]})
        self.assertEqual(g.observe(frame),Phase.INFRASTRUCTURE_REQUIRED)
        self.assertIn("UNAVAILABLE_L7",g.state.blockers)

    def test_outcome_future_duplicate_and_shadow_isolation(self):
        ledger=ObservationLedger(lookback=32,min_adaptive_samples=2)
        with self.assertRaises(ValueError):
            ledger.record(MaturedOutcome("WATCHDOG",100,130,120,5,True,"future"))
        ledger.record(MaturedOutcome("WATCHDOG",100,130,130,5,False,"shadow1"))
        self.assertEqual(ledger.snapshot()["funded_closed_count"],0)
        ledger.record(MaturedOutcome("SESSION",120,150,151,5,True,"real1"))
        self.assertFalse(ledger.snapshot()["adaptive_observation_mature"])
        ledger.record(MaturedOutcome("NATIVE",150,170,171,-1,True,"real2"))
        self.assertTrue(ledger.snapshot()["adaptive_observation_mature"])
        self.assertTrue(ledger.snapshot()["original_v1_default_does_not_wait_for_this_ledger"])
        self.assertFalse(ledger.snapshot()["watchdog_unlock_from_shadow"])
        self.assertAlmostEqual(ledger.snapshot()["recent_funded_expectancy"],2.)
        with self.assertRaises(ValueError):
            ledger.record(MaturedOutcome("SESSION",120,150,171,5,True,"real1"))

    def test_predeployment_quote_and_backdated_updates_rejected(self):
        g=StartupGate(T0)
        with self.assertRaises(ValueError):g.observe(f(T0-1,market_open=False))
        g.observe(f(FIRST_QUOTE))
        with self.assertRaises(ValueError):g.observe(f(FIRST_QUOTE-1))

if __name__=="__main__":unittest.main()
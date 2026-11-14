"""Synthetic ORIGINAL R9 lifecycle parity / competing account-cash research tests."""
import math
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
REPO=ROOT.parents[0]
sys.path.insert(0,str(REPO/"src"))
sys.path.insert(0,str(ROOT/"src"))

from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config,R9HybridGateBaseline
from cash_risk_overlay import (
    CashAssumptions,R9CashRiskOverlay,run_stream,
    CAUSE_TARGET,CAUSE_STOP,CAUSE_TIMEOUT,CAUSE_GAP,CAUSE_EOF,
)


def easy():
    return R9Config(use_regime_gate=False,velocity_lookback_sec=2,
                    range_lookback_sec=2,min_velocity_pips=0,
                    min_directional_eff=0.0,min_range_pips=0,
                    max_turns=99,stop_loss_pips=30)


def t(n,s,bid,ask=None,ms_offset=None):
    if ask is None:ask=bid+2
    if ms_offset is None:ms_offset=n
    return Tick(n,s,s*1000+ms_offset,bid,ask)


def prefix():
    return [t(1,120,1000),t(2,121,1005),t(3,122,1010),
            t(4,123,1030)]


class MonetaryOverlayTests(unittest.TestCase):
    def setUp(self):
        self.cash=CashAssumptions("USD",1.0,0.20,1.75)

    def test_exact_quote_side_cash_target_no_double_spread(self):
        self.assertEqual(self.cash.required_favorable_cents,195)
        self.assertAlmostEqual(self.cash.net_cash(-2),-.22)
        self.assertAlmostEqual(self.cash.net_cash(195),1.75)
        self.assertEqual(CashAssumptions("USD",2.0,.2,1.75).required_favorable_cents,98)

    def test_never_assume_account_conversion_or_fees(self):
        for args in [
            ("USD",0.,.2,1.75),("USD",1.,-0.1,1.75),
            ("",1.,0.2,1.75),("USD",1.,0.2,-1.75),
            ("USD",float("inf"),0.2,1.75),
        ]:
            with self.assertRaises(ValueError):
                CashAssumptions(*args)

    def test_r9_trade_path_unchanged_by_observer(self):
        seq=prefix()+[t(5,124,1231),t(6,125,1227),t(7,126,1200)]
        plain=R9HybridGateBaseline(easy())
        for tick in seq:plain.on_tick(tick)
        research=run_stream(seq,self.cash,easy())
        self.assertEqual(plain.trades,research.base.trades)
        self.assertEqual(plain.entries,research.base.entries)
        self.assertEqual(plain.config_dict(),research.base.config_dict())

    def test_target_first_before_trailing_stop(self):
        # BUY entry Ask=1032. Later Bid=1231 -> +199c >=195.
        # Afterwards Bid=1227 triggers original R9 trailing/protective stop.
        seq=prefix()+[t(5,124,1231),t(6,125,1227)]
        sim=run_stream(seq,self.cash,easy())
        self.assertEqual(len(sim.completed),1)
        e=sim.completed[0]
        self.assertEqual(e.cause,CAUSE_TARGET)
        self.assertEqual(e.event_time_ms,1001)
        self.assertAlmostEqual(e.observed_goal_cash,1.79)
        self.assertEqual(e.exit_reason,"stop")
        self.assertIsNotNone(e.baseline_net_cash)
        self.assertGreater(e.overlay_net_cash,0.0)

    def test_stop_first_and_cash_loss(self):
        seq=prefix()+[t(5,124,998)]
        sim=run_stream(seq,self.cash,easy())
        self.assertEqual(sim.completed[0].cause,CAUSE_STOP)
        self.assertLess(sim.completed[0].baseline_net_cash,0.)
        self.assertEqual(sim.completed[0].baseline_net_cash,sim.completed[0].overlay_net_cash)

    def test_stop_labeled_stop_even_when_trailing_profit(self):
        seq=prefix()+[t(5,124,1070),t(6,125,1067)]
        sim=run_stream(seq,self.cash,easy())
        e=sim.completed[0]
        self.assertEqual(e.cause,CAUSE_STOP)
        self.assertGreater(e.baseline_net_cash,0.0)
        self.assertEqual(e.exit_reason,"stop")

    def test_timeout_first_with_fresh_quotes(self):
        seq=prefix()
        for j,s in enumerate((128,133,138,143,148,153,154),start=5):
            seq.append(t(j,s,1040))
        sim=run_stream(seq,self.cash,easy())
        e=sim.completed[0]
        self.assertEqual(e.cause,CAUSE_TIMEOUT)
        self.assertEqual(e.exit_reason,"timeout")
        self.assertEqual(e.event_time_ms,30000)
        self.assertGreater(e.exit_time_msc-e.entry_time_msc,30000)

    def test_quote_gap_censors_before_new_unobserved_market(self):
        seq=prefix()+[t(5,140,998)]
        sim=run_stream(seq,self.cash,easy())
        e=sim.completed[0]
        self.assertEqual(e.cause,CAUSE_GAP)
        self.assertEqual(e.event_time_ms,0)
        self.assertIsNone(e.overlay_net_cash)
        self.assertIsNotNone(e.baseline_net_cash)

    def test_eof_censors_instead_of_making_up_fills(self):
        sim=run_stream(prefix(),self.cash,easy())
        e=sim.completed[0]
        self.assertEqual(e.cause,CAUSE_EOF)
        self.assertIsNone(e.baseline_net_cash)
        self.assertIsNone(e.overlay_net_cash)

    def test_duplicate_millisecond_preserves_ordinals(self):
        seq=prefix()
        # Two source quotes have exact same milliseconds, distinct ordinals.
        seq.append(t(5,123,1230,1232,ms_offset=4))
        sim=run_stream(seq,self.cash,easy())
        self.assertEqual(sim.completed[0].cause,CAUSE_TARGET)
        self.assertEqual(sim.completed[0].event_time_ms,0)

    def test_backwards_source_ordinal_fails_closed(self):
        sim=R9CashRiskOverlay(self.cash,easy())
        sim.on_tick(t(1,120,1000))
        with self.assertRaises(ValueError):
            sim.on_tick(t(1,120,1000))


if __name__=="__main__":
    unittest.main()

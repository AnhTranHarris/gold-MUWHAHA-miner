"""Synthetic price paths verify ON-POLICY lifecycle; no fake market results."""
from __future__ import annotations

import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
PROJECT=ROOT.parent
sys.path.insert(0,str(PROJECT/"src"))
sys.path.insert(0,str(PROJECT/"account_cash_competing_risks"/"src"))
sys.path.insert(0,str(ROOT/"src"))

from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config,R9HybridGateBaseline
from cash_risk_overlay import CashAssumptions
from adaptive_policy import (AdaptiveR9,ExitPolicy,QuoteContext,
                             summarize_account_cash)


def t(ordinal,seconds,bid,spread=2):
    return Tick(ordinal=ordinal,time_s=seconds,
                time_msc=seconds*1000+ordinal,bid_u=bid,ask_u=bid+spread)


def test_config():
    return R9Config(use_regime_gate=False,velocity_lookback_sec=2,
                    range_lookback_sec=2,min_velocity_pips=0,
                    min_directional_eff=0,min_range_pips=0,
                    max_turns=99,max_hold_seconds=30)


def entry():
    return [t(1,120,1000),t(2,121,1005),t(3,122,1010),t(4,123,1030)]


class AdaptivePolicyTests(unittest.TestCase):
    def setUp(self):
        self.cash=CashAssumptions("USD",1.0,0.20,1.75)

    def test_baseline_mode_source_exact_parity(self):
        ticks=entry()+[t(5,124,1045),t(6,125,1040),
                       t(7,126,1050),t(8,127,980),
                       t(9,128,976),t(10,129,1100),
                       t(11,130,1120)]
        original=R9HybridGateBaseline(test_config())
        unchanged=AdaptiveR9(test_config(),self.cash,ExitPolicy(mode="baseline"))
        for tick in ticks:
            original.on_tick(tick)
            unchanged.on_tick(tick)
        self.assertEqual(original.trades,unchanged.trades)
        self.assertEqual(original.entries,unchanged.entries)
        self.assertEqual(original.stats,unchanged.stats)
        self.assertEqual(original.position,unchanged.position)

    def test_adaptive_trail_changes_real_exit_and_future_rearm(self):
        ticks=entry()+[t(5,124,1045),t(6,125,1040)]
        original=R9HybridGateBaseline(test_config())
        adaptive=AdaptiveR9(test_config(),self.cash,ExitPolicy(mode="cost_trail"))
        for tick in ticks:
            original.on_tick(tick)
            adaptive.on_tick(tick)
        self.assertEqual(len(original.trades),1)
        self.assertEqual(original.trades[0].reason,"stop")
        self.assertIsNotNone(adaptive.position)
        self.assertNotEqual(original.rearms,adaptive.rearms)
        self.assertNotEqual(original.pending_mode,adaptive.pending_mode)
        # Source-exact full replay automatically changes the following
        # opposite-side opportunity without splicing a frozen entry list.

    def test_adaptive_stop_never_worsens_after_raising(self):
        sim=AdaptiveR9(test_config(),self.cash,ExitPolicy(mode="cost_trail"))
        for row in entry()+[t(5,124,1070)]:
            sim.on_tick(row)
        self.assertIsNotNone(sim.position)
        first_sl=sim.position.sl_u
        self.assertGreater(first_sl,sim.position.initial_sl_u)
        sim.on_tick(t(6,125,1080))
        self.assertIsNotNone(sim.position)
        second_sl=sim.position.sl_u
        self.assertGreaterEqual(second_sl,first_sl)
        sim.on_tick(t(7,126,max(second_sl+1,1070)))
        self.assertIsNotNone(sim.position)
        self.assertGreaterEqual(sim.position.sl_u,second_sl)

    def test_harvest_occurs_only_with_real_positive_net_and_adverse_context(self):
        policy=ExitPolicy(mode="staged_harvest",harvest_after_seconds=1,
                          minimum_harvest_cash=0.10)
        sim=AdaptiveR9(test_config(),self.cash,policy)
        for tick in entry():
            sim.on_tick(tick)
        # Synthetic quote-state unit fixture: forced adverse CONTINUATION
        # INDEX only, not a claim that live M1 ADX implies this signal.
        sim._noise=lambda tick: 10.0
        sim.quotes.continuation_index=lambda side,tick:-1.0
        sim.on_tick(t(5,124,1070))
        self.assertEqual(len(sim.trades),1)
        self.assertEqual(sim.trades[0].reason,"adaptive_harvest")
        self.assertGreater(self.cash.net_cash(sim.trades[0].net_price_u),0)

    def test_negative_net_never_harvested(self):
        policy=ExitPolicy(mode="staged_harvest",harvest_after_seconds=1)
        sim=AdaptiveR9(test_config(),self.cash,policy)
        for tick in entry():
            sim.on_tick(tick)
        sim._noise=lambda tick:10.0
        sim.quotes.continuation_index=lambda side,tick:-1.0
        sim.on_tick(t(5,124,1040)) # net cash negative after cost
        self.assertEqual(len(sim.trades),0)

    def test_completed_bar_only_m1_indicator_context(self):
        quotes=QuoteContext()
        for i in range(11):
            quotes.update(t(i+1,120+60*i,1000+i*5))
        self.assertEqual(len(quotes.m1_closed_bid),10)
        before=list(quotes.m1_closed_bid)
        quotes.update(t(20,120+60*10+3,9999))
        self.assertEqual(list(quotes.m1_closed_bid),before)
        self.assertIsNotNone(quotes.diagnostics(t(20,120+60*10+3,9999))[
                             "completed_m1_std_cents"])

    def test_short_quote_proxy_abstains_on_long_gap(self):
        ctx=QuoteContext()
        for k in range(4):
            ctx.update(t(k+1,120+k,1000+5*k))
        quote=t(5,300,2000)
        ctx.update(quote)
        self.assertFalse(ctx.diagnostics(quote)["quote_fresh"])
        self.assertIsNone(ctx.continuation_index(1,quote))

    def test_cash_conversions_include_spread_once(self):
        sim=AdaptiveR9(test_config(),self.cash,ExitPolicy(mode="baseline"))
        for tick in entry():
            sim.on_tick(tick)
        self.assertEqual(sim.position.entry_price_u,1032)
        self.assertAlmostEqual(self.cash.net_cash(-2),-0.22)

    def test_forbidden_policy_or_nonfinite_fails(self):
        for kwargs in (dict(mode="unknown"),
                       dict(alpha_spread=float("nan")),
                       dict(beta_noise=float("inf")),
                       dict(max_quote_gap_ms=0)):
            with self.assertRaises(ValueError):
                ExitPolicy(**kwargs)

    def test_closed_trade_summary_explicitly_not_broker_account(self):
        sim=AdaptiveR9(test_config(),self.cash,ExitPolicy(mode="baseline"))
        for tick in entry()+[t(5,124,1045),t(6,125,1040)]:
            sim.on_tick(tick)
        result=summarize_account_cash(sim,self.cash)
        self.assertEqual(result["trades"],1)
        self.assertFalse(result["account_governor_simulated"])
        self.assertTrue(result["no_actual_order_fills"])
        self.assertEqual(result["completed_entry_hour_cells"],1)
        self.assertLess(result["total_net_cash"],0)


if __name__=="__main__":
    unittest.main()

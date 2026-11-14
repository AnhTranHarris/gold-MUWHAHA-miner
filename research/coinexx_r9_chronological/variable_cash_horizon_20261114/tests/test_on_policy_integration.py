"""Small source-exact state, causal market, risk-envelope & rearm tests.

Historical January full ledger parity is independently verified at runtime
before any performance number is admissible, rather than in this tiny fixture.
"""
from __future__ import annotations
import unittest, pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'variable_cash_horizon_20261114'))
from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config,R9HybridGateBaseline
from on_policy_cash_replay import ResearchCash,CashAccount,QuoteRegime,ManagedR9
from run_coinexx import reuse_only_identical_market_context

def tick(n,sec,bid,spread=20):
    return Tick(ordinal=n,time_s=sec,time_msc=sec*1000+n,bid_u=bid,ask_u=bid+spread)

class SourceExactPolicyTests(unittest.TestCase):
    def test_original_market_context_sharing_preserves_trades(self):
        config=R9Config(use_regime_gate=False,velocity_lookback_sec=2,range_lookback_sec=2,
                        min_velocity_pips=0,min_directional_eff=0,min_range_pips=0,max_turns=99)
        a=R9HybridGateBaseline(config)
        b=R9HybridGateBaseline(config)
        # b is the same exact stock R9 core but shares common price context.
        reuse_only_identical_market_context(a,b)
        for n,(sec,bid) in enumerate([(120,1000),(121,1005),(122,1010),
                                      (123,1030),(124,1055),(125,1040),
                                      (126,980),(127,975)],start=1):
            t=tick(n,sec,bid)
            a.on_tick(t);b.on_tick(t)
        self.assertEqual(a.trades,b.trades)
        self.assertEqual(a.entries,b.entries)
        self.assertEqual(a.position,b.position)

    def test_governor_10_percent_not_weakened_to_25_percent(self):
        cash=ResearchCash(initial_capital=100.,governor=True)
        account=CashAccount(cash)
        account.begin_tick(tick(1,100,10000))
        account.equity=89.
        account.begin_tick(tick(2,101,10000))
        self.assertTrue(account.permanent_lock)
        self.assertEqual(account.halts['10pct_peak'],1)
        self.assertEqual(account.halts['25pct_absolute'],0)

    def test_daily_gross_consumes_fees_even_on_profitable_trades(self):
        acc=CashAccount(ResearchCash(initial_capital=100.,governor=True))
        acc.begin_tick(tick(1,100,10000))
        acc.day_charges=4.01
        acc.begin_tick(tick(2,101,10000))
        self.assertTrue(acc.day_lock)

    def test_new_entry_respects_abs_position_risk_even_when_governor_off(self):
        config=R9Config(use_regime_gate=False,velocity_lookback_sec=2,range_lookback_sec=2,
                        min_velocity_pips=0,min_directional_eff=0,min_range_pips=0,max_turns=99)
        sim=ManagedR9(config,ResearchCash(),mode='cash_harvest')
        sim._open_trade(tick(1,100,10000,spread=300),1)
        self.assertIsNone(sim.position)
        self.assertEqual(sim.reasons['blocked_initial_stop_over_2cash'],1)

    def test_quote_regime_does_not_future_fill_gaps_or_claim_real_volume(self):
        ctx=QuoteRegime()
        for n in range(1,300):
            ctx.update(tick(n,1000+n,10000+n))
        now=tick(300,1300,10300)
        ctx.update(now)
        state=ctx.state(1,now)
        self.assertTrue(state['available'])
        self.assertTrue(state['liquidity_proxy_only'])
        gap=tick(301,1700,10700)
        ctx.update(gap)
        self.assertFalse(ctx.state(1,gap)['available'])

    def test_model_runner_remains_unvalidated_without_exact_positive_utility(self):
        sim=ManagedR9(R9Config(),ResearchCash(),mode='regime_probe')
        self.assertEqual(sim.conditional_runner_eligible,0)
        self.assertEqual(sim.score_covered,0)

if __name__=='__main__':
    unittest.main()
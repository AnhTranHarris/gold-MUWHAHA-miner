"""Deterministic V6 first-passage causality and cash-unit tests."""
import unittest
from dataclasses import replace
from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config
from on_policy_cash_replay import ResearchCash
from micro180 import RollingThreeMinute,Micro180Spec
from v5_path_lifecycle import V5Spec
from v6_past_only_utility import (
    V6Spec,past_cash_first_passage,incremental_hold_prior,PastOnlyCashMicroV6)


def quote(sec,bid,ask=None,ms_remainder=30,ordinal=0):
    return Tick(ordinal,sec,sec*1000+ms_remainder,bid,
                bid+10 if ask is None else ask)


def ring(prices,base=1_000):
    r=RollingThreeMinute()
    for i,bid in enumerate(prices):r.update(quote(base+i,bid,ordinal=i))
    return r


class V6CausalContract(unittest.TestCase):
    def test_parameters_validate(self):
        for kw in ({'window_ms':90_000},{'horizon_seconds':16},
                   {'stride_seconds':3},{'min_observations':1},
                   {'uncertainty_scale':-1},{'min_buy_cash_edge':3},
                   {'min_hold_increment':2}):
            with self.assertRaises(ValueError):V6Spec(**kw)

    def test_past_only_ignores_current_incomplete_bar(self):
        r=ring([10_000+i for i in range(120)])
        now=1_120_500
        buy=past_cash_first_passage(r,now,1,spec=V6Spec())
        sell=past_cash_first_passage(r,now,-1,spec=V6Spec())
        self.assertGreater(buy.sample_count,8)
        self.assertGreater(buy.historical_mean_net,sell.historical_mean_net)
        r.update(quote(1_120,999_999,ms_remainder=800))
        self.assertEqual(buy,past_cash_first_passage(r,now,1,spec=V6Spec()))
        self.assertEqual(sell,past_cash_first_passage(r,now,-1,spec=V6Spec()))

    def test_buy_uses_bid_sell_uses_ask_and_cost_once(self):
        r=ring([10_000+i*10 for i in range(150)])
        buy=past_cash_first_passage(r,1_150_001,1)
        sell=past_cash_first_passage(r,1_150_001,-1)
        self.assertGreater(buy.first_profit_fraction,0.0)
        self.assertAlmostEqual(sell.first_profit_fraction,0.0)
        self.assertLess(sell.historical_mean_net,0.0)
        # Executable Buy starts at ask=bid+10, not bid alone.
        r2=RollingThreeMinute()
        for i in range(150):
            r2.update(quote(2000+i,10_000+i*10,10_100+i*10))
        buy2=past_cash_first_passage(r2,2_150_001,1)
        self.assertLess(buy2.historical_mean_net,buy.historical_mean_net)

    def test_gap_cannot_be_imputed_as_candle(self):
        r=RollingThreeMinute()
        for i in range(140):
            sec=3000+i+10*(i//20)
            r.update(quote(sec,12_000+i))
        z=past_cash_first_passage(r,(3000+140+70)*1000,1)
        self.assertGreater(z.count_quote_gaps,0)
        self.assertLess(z.sample_count,16)

    def test_no_old_155_feature_dependency_and_governor_unmodified(self):
        model=PastOnlyCashMicroV6(
            R9Config(use_regime_gate=False),
            ResearchCash(governor=True,initial_capital=500),
            Micro180Spec(),v5=V5Spec(),v6=V6Spec())
        self.assertTrue(model.cash.governor)
        self.assertFalse(model.v6.enable_holding_utility)
        self.assertTrue(model.report()['v6_past_cash']['separate_buy_sell_cash_estimates'])

    def test_incremental_hold_has_no_second_commission(self):
        r=ring([10_000+i*6 for i in range(120)])
        h=incremental_hold_prior(r,1_120_002,1)
        k=incremental_hold_prior(r,1_120_002,-1)
        self.assertIsNotNone(h)
        self.assertGreater(h,0.)
        self.assertLess(k,0.)


    def test_v6_highwater_buy_stop_tightens_never_widens(self):
        from coinexx_r9.r9_baseline import _Position
        cfg=R9Config(use_regime_gate=False)
        m=PastOnlyCashMicroV6(cfg,ResearchCash(governor=False),
                 replace(Micro180Spec(),experimental_runner=True),
                 v5=V5Spec(enable_protected_continuation=True))
        m.position=_Position(1,7,1_000_000,1000,10_000,9_940,9_940,0)
        m._current_peak_cash=1.15
        m._v6_ratchet(quote(1_002,10_135,10_145),m.position,1.15)
        self.assertEqual(m.position.sl_u,10_110)
        m._v6_ratchet(quote(1_003,10_120,10_130),m.position,1.00)
        self.assertEqual(m.position.sl_u,10_110)

    def test_v6_highwater_sell_stop_uses_ask(self):
        from coinexx_r9.r9_baseline import _Position
        m=PastOnlyCashMicroV6(R9Config(use_regime_gate=False),
                 ResearchCash(governor=False),
                 replace(Micro180Spec(),experimental_runner=True),
                 v5=V5Spec(enable_protected_continuation=True))
        m.position=_Position(-1,8,1_000_000,1000,10_000,10_060,10_060,0)
        m._current_peak_cash=1.15
        m._v6_ratchet(quote(1_002,9_855,9_865),m.position,1.15)
        self.assertEqual(m.position.sl_u,9_890)
        m._v6_ratchet(quote(1_003,9_870,9_880),m.position,1.00)
        self.assertEqual(m.position.sl_u,9_890)



if __name__=='__main__':unittest.main()

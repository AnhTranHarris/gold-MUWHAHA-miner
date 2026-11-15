"""No-file synthetic tests for the opt-in asymmetric quote formula."""
import sys, unittest
from dataclasses import replace
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
for p in (ROOT/'src',ROOT/'variable_cash_horizon_20261114',ROOT/'micro180_20261114'):
    sys.path.insert(0,str(p))

from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config
from on_policy_cash_replay import ResearchCash
from micro180 import Micro180Spec,RollingThreeMinute
from asymmetric_v3 import AsymSpec,signature,AsymmetricMicroR9


def q(ms,bid,spread=10,ordinal=1):
    return Tick(ordinal,ms//1000,ms,bid,bid+spread)


def window(direction=1):
    ring=RollingThreeMinute()
    for second in range(0,190):
        ring.update(q(second*1000+100,1200+direction*second,ordinal=second+1))
    return ring


class V3Tests(unittest.TestCase):
    def test_unavailable_history_abstains(self):
        r=RollingThreeMinute()
        r.update(q(120000,1000))
        self.assertIsNone(signature(r,q(120100,1100),1))

    def test_monotone_healthy_bid_and_ask_buy(self):
        ring=window(1)
        e=signature(ring,q(189500,1395),1)
        self.assertIsNotNone(e)
        self.assertGreater(e.score,0.15)
        self.assertGreater(e.eff15,0.0)
        self.assertGreater(e.joint_quote_fraction,0.90)

    def test_monotone_healthy_bid_and_ask_sell(self):
        ring=window(-1)
        e=signature(ring,q(189500,1005),-1)
        self.assertIsNotNone(e)
        self.assertGreater(e.score,0.15)
        self.assertGreater(e.eff15,0.0)
        self.assertGreater(e.joint_quote_fraction,0.90)

    def test_widening_ask_alone_is_not_buy_evidence(self):
        ring=RollingThreeMinute()
        for sec in range(190):
            ring.update(q(sec*1000+100,1000))
        e=signature(ring,q(189500,1000,300),1)
        self.assertIsNotNone(e)
        self.assertLess(e.score,0.15)
        self.assertEqual(e.joint_quote_fraction,0.0)

    def test_no_real_volume_claim_from_quote_counts(self):
        ring=window(1)
        e=signature(ring,q(189500,1395),1)
        self.assertGreater(e.quote_intensity_ratio,0)
        e2=signature(ring,q(189500,1395),-1)
        self.assertEqual(e2.side,-1)

    def test_bad_contract_fails_closed(self):
        for kw in ({'min_buy_score':3},{'min_sell_score':-3},
                   {'minimum_history_seconds':10},{'min_coincident_quote_fraction':2}):
            with self.subTest(kw),self.assertRaises(ValueError):AsymSpec(**kw)
        with self.assertRaises(ValueError):signature(window(),q(189500,1400),0)

    def test_existing_base_controls_and_default_score_are_not_overwritten(self):
        s=Micro180Spec()
        self.assertEqual(s.min_net_cash,.10)
        self.assertEqual(s.preferred_max_net_cash,1.75)
        self.assertEqual(s.hard_risk_cash,2.0)
        sim=AsymmetricMicroR9(R9Config(use_regime_gate=False),
                              ResearchCash(governor=True,initial_capital=1000),s)
        sim.on_tick(q(120000,1000))
        sim._open_trade(q(120100,1100),1)
        self.assertIsNone(sim.position)
        self.assertEqual(sim.stats["asym_missing_completed_history"],1)
        self.assertFalse(s.experimental_runner)
        self.assertFalse(sim.report()["asymmetric_v3"]["uses_real_traded_volume"])


if __name__=="__main__":unittest.main()

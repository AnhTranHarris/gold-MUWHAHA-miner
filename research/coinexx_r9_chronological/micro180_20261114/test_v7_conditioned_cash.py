"""V7 tests: strict past-only labels, scale, asymmetric economics, safe controls."""
import unittest
from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config
from on_policy_cash_replay import ResearchCash
from micro180 import RollingThreeMinute,Micro180Spec
from v5_path_lifecycle import V5Spec
from v7_conditioned_cash import V7Spec,conditioned_cash_first_passage,conditioned_incremental_hold,SetupConditionedMicroV7


def q(i,bid,ask=None,origin=1000):
    return Tick(i,origin+i,(origin+i)*1000+55,bid,bid+10 if ask is None else ask)


def ring(prices,spread=10):
    r=RollingThreeMinute()
    for i,p in enumerate(prices):r.update(q(i,p,p+spread))
    return r


class TestV7(unittest.TestCase):
    def test_invalid_specs(self):
        for x in ({'min_effective_samples':0},{'anchor_stride_seconds':3},
                  {'similarity_width':0},{'uncertainty_multiplier':5},
                  {'min_buy_penalized_cash':float('nan')},
                  {'hold_horizon_seconds':0}):
            with self.assertRaises(ValueError):V7Spec(**x)

    def test_buy_and_sell_cash_profit_are_not_swapped(self):
        prices=[10_000+10*i for i in range(160)]
        r=ring(prices)
        t=q(160,11_600)
        b=conditioned_cash_first_passage(r,t,+1,spec=V7Spec(min_effective_samples=2))
        s=conditioned_cash_first_passage(r,t,-1,spec=V7Spec(min_effective_samples=2))
        self.assertTrue(b.usable)
        self.assertGreater(b.mean_cash,0.)
        self.assertLess(s.mean_cash,0.)
        self.assertGreater(b.profit_first_weight,s.profit_first_weight)

    def test_executable_spread_is_charged_not_midpoint(self):
        prices=[10_000+8*i for i in range(160)]
        t=q(160,11_280,11_380)
        b=conditioned_cash_first_passage(ring(prices,10),q(160,11_280),+1,
                      spec=V7Spec(min_effective_samples=2))
        worse=conditioned_cash_first_passage(ring(prices,100),t,+1,
                      spec=V7Spec(min_effective_samples=2))
        self.assertLess(worse.mean_cash,b.mean_cash)

    def test_incomplete_current_second_is_never_a_label(self):
        prices=[10_000+6*i for i in range(160)]
        r=ring(prices)
        now=q(160,10_960)
        initial=conditioned_cash_first_passage(r,now,+1)
        r.update(Tick(161,1160,1160_700,200_000,200_010))
        self.assertEqual(initial,conditioned_cash_first_passage(r,now,+1))

    def test_gaps_invalidate_samples(self):
        r=RollingThreeMinute()
        for i in range(160):
            second=1_000+i+8*(i//20)
            r.update(Tick(i,second,second*1000+5,10_000+i,10_010+i))
        z=conditioned_cash_first_passage(r,
              Tick(999,1224,1224_010,10_200,10_210),+1)
        self.assertFalse(z.usable)

    def test_hold_increment_is_directional_and_no_repeated_commission(self):
        r=ring([10_000+i*6 for i in range(160)])
        t=q(160,10_960)
        b=conditioned_incremental_hold(r,t,+1,spec=V7Spec(min_effective_samples=2))
        s=conditioned_incremental_hold(r,t,-1,spec=V7Spec(min_effective_samples=2))
        self.assertIsNotNone(b)
        self.assertGreater(b,0.0)
        self.assertIsNotNone(s)
        self.assertLess(s,0.0)

    def test_reject_unprotected_v7_holding(self):
        with self.assertRaises(ValueError):
            SetupConditionedMicroV7(R9Config(),ResearchCash(governor=False),
              Micro180Spec(),v7=V7Spec(enable_conditioned_holding=True))

    def test_full_previous_v6_governor_and_cash_constraints_remain(self):
        m=SetupConditionedMicroV7(R9Config(),ResearchCash(governor=True,
              initial_capital=500.),Micro180Spec(),v5=V5Spec(),
              v7=V7Spec(enable_cash_gate=False))
        self.assertTrue(m.cash.governor)
        self.assertFalse(m.v7.enable_cash_gate)
        self.assertTrue(m.v6.audit_only)
        self.assertEqual(m.micro_spec.hard_risk_cash,2.0)
        self.assertEqual(m.micro_spec.min_net_cash,.10)
        self.assertEqual(m.micro_spec.preferred_max_net_cash,1.75)
        self.assertFalse(m.v7.enable_conditioned_holding)


if __name__=='__main__':unittest.main()

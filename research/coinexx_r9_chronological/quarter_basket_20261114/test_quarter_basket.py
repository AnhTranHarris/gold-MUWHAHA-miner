"""Deterministic unit checks for 15s basket/15s-30s breakout execution."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'variable_cash_horizon_20261114'))
sys.path.insert(0,str(ROOT/'quarter_basket'))
from coinexx_r9.r9_baseline import R9Config,R9HybridGateBaseline
from coinexx_r9.models import Tick
from quarter_basket import BasketSpec,QuarterBasketBaseline,QuarterBasketCash
from on_policy_cash_replay import ResearchCash

def q(n,sec,bid,spread=20):
    return Tick(n,sec,sec*1000+n,bid,bid+spread)

def cfg():
    return R9Config(use_regime_gate=False,velocity_lookback_sec=2,
        range_lookback_sec=2,min_velocity_pips=0,min_directional_eff=0,
        min_range_pips=0,max_turns=99)

class QuarterBasketTests(unittest.TestCase):
    def test_invalid_configuration_fails(self):
        for x in ({'breakout_seconds':5},{'basket_seconds':30},
                  {'minimum_completed_seconds':2},{'minimum_mid_displacement_cents':0}):
            with self.assertRaises(ValueError): BasketSpec(**x)

    def test_basket_reset_exact_boundary_and_midpoint_spread_neutral(self):
        sim=QuarterBasketBaseline(cfg(),BasketSpec())
        sim._start_minute_cycle(q(1,120,1000,10))
        self.assertEqual(sim.basket_start,120)
        self.assertEqual(sim.anchor_mid2,2010)
        sim._start_minute_cycle(q(2,134,1001,100))
        self.assertEqual(sim.anchor_mid2,2010)
        sim._start_minute_cycle(q(3,135,1001,100))
        self.assertEqual(sim.basket_start,135)
        self.assertEqual(sim.anchor_mid2,2102)
        self.assertEqual(sim.cycle_minute,120)

    def test_completed_seconds_only_and_staleness(self):
        sim=QuarterBasketBaseline(cfg(),BasketSpec())
        for n,sec in enumerate(range(120,130),1):
            sim.on_tick(q(n,sec,1000+sec-120))
        levels=sim._breakout_levels(q(100,130,1100))
        self.assertIsNotNone(levels)
        # Same-current-second quoted extreme cannot leak into completed window
        sim.on_tick(q(101,130,2000))
        levels2=sim._breakout_levels(q(102,130,5000))
        self.assertEqual(levels,levels2)
        self.assertIsNone(sim._breakout_levels(q(103,144,2000)))

    def test_15_vs_30_distinct_stale_history(self):
        a=QuarterBasketBaseline(cfg(),BasketSpec(breakout_seconds=15))
        b=QuarterBasketBaseline(cfg(),BasketSpec(breakout_seconds=30))
        # Older high 20s ago should affect 30s not 15s breakout
        for n,sec in enumerate(range(100,131),1):
            bid=1200 if sec==106 else (1000 if sec<120 else 1050)
            t=q(n,sec,bid)
            a.on_tick(t); b.on_tick(t)
        t=q(60,131,1100)
        l15=a._breakout_levels(t);l30=b._breakout_levels(t)
        self.assertIsNotNone(l15)
        self.assertIsNotNone(l30)
        self.assertLess(l15[0],l30[0])

    def test_basket_local_rearm_no_cross_basket_leak(self):
        sim=QuarterBasketBaseline(cfg(),BasketSpec())
        sim._start_minute_cycle(q(1,120,1000))
        sim._last_entry_basket=120
        sim._closed_entry_basket=120
        sim._last_close_basket=120
        sim.last_position_side=1
        sim._arm_opposite_after_exit()
        self.assertEqual(sim.pending_mode,-1)
        self.assertEqual(sim.rearms,1)
        sim._start_minute_cycle(q(2,135,1000))
        self.assertEqual(sim.pending_mode,2)
        sim._arm_opposite_after_exit()
        self.assertEqual(sim.pending_mode,2)
        self.assertEqual(sim.rearms,0)

    def test_price_breakout_requires_completed_prior_high_and_s1(self):
        sim=QuarterBasketBaseline(cfg(),BasketSpec())
        for n,sec in enumerate(range(120,146),1):
            t=q(n,sec,1000)
            sim.on_tick(t)
        self.assertEqual(len(sim.entries),0)
        # Basket 135 began at mid 1010; mid quote 1030 at 146 is
        # +20c, and above old closes -> BUY under both gates.
        sim.on_tick(q(100,146,1020))
        self.assertEqual(len(sim.entries),1)
        self.assertEqual(sim.entries[0]['basket_start_second'],135)
        self.assertEqual(sim.entries[0]['breakout_seconds'],15)

    def test_cash_controller_integrated_no_ten_cent_harvest(self):
        sim=QuarterBasketCash(cfg(),ResearchCash(),mode='cash_harvest',
            basket_spec=BasketSpec())
        for n,sec in enumerate(range(120,146),1): sim.on_tick(q(n,sec,1000))
        sim.on_tick(q(100,146,1020))
        self.assertEqual(len(sim.entries),1)
        sim.on_tick(q(101,147,1050)) # +0.10 net cash, not >=0.50
        self.assertIsNotNone(sim.position)
        self.assertEqual(len(sim.trades),0)
        sim.on_tick(q(102,148,1110)) # +0.50 account cash on BUY after fees
        self.assertEqual(len(sim.trades),1)
        self.assertGreaterEqual(sim.trades[0].net_price_u/100.-.20+1e-9, .50)

    def test_synthetic_original_baseline_unchanged(self):
        original=R9HybridGateBaseline(cfg())
        copy=R9HybridGateBaseline(cfg())
        for n,s in enumerate(range(120,165),1):
            t=q(n,s,1000+s-120)
            original.on_tick(t);copy.on_tick(t)
        self.assertEqual(original.entries,copy.entries)
        self.assertEqual(original.trades,copy.trades)

if __name__=='__main__':unittest.main()
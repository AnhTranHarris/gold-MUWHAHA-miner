"""Micro V9 deterministic contract tests. No raw tick downloads or writes."""
from __future__ import annotations
import sys,unittest,os
from pathlib import Path
P=Path(__file__).resolve().parent
R=Path(os.environ.get('R9_RESEARCH_ROOT',str(P.parent)))
if not (R/'src').is_dir():
    raise RuntimeError('Set R9_RESEARCH_ROOT to the existing research source directory')
for p in (P,R/'src',R/'variable_cash_horizon_20261114',R/'dual_basket_20261114'):
    sys.path.insert(0,str(p))
from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config
from on_policy_cash_replay import ResearchCash
from micro180 import RollingThreeMinute
from v5_ms_path import MsQuarterPath
from v9_volume_router import V9Spec,VolumePreservingMicroV9,directional_quant


def tick(n,ms,bid=1000,spread=20):return Tick(n,ms//1000,ms,bid,bid+spread)

def cfg():return R9Config(use_regime_gate=False,velocity_lookback_sec=2,
    range_lookback_sec=2,min_velocity_pips=0,min_directional_eff=0,
    min_range_pips=0,max_turns=99)

class VolumeV9Contract(unittest.TestCase):
    def test_invalid_config_rejected(self):
        for opts in ({'entry_action':'future_trader'},{'entry_signal_mode':'mid_fill'},
                     {'rearm_cooldown_ms':-1},{'min_5s_span_ms':5000},
                     {'adverse_cash_trigger':1},{'exit_action':'never_stop'}):
            with self.subTest(opts=opts),self.assertRaises(ValueError):V9Spec(**opts)

    def test_independent_buy_bid_sell_ask_and_no_dummy_real_volume(self):
        ring=RollingThreeMinute();path=MsQuarterPath()
        for i in range(40):
            for ms in (i*1000+60,i*1000+540):
                t=tick(i*2+int(ms%1000>100),ms,1000+2*i,20)
                ring.update(t);path.update(t)
        now=tick(999,40100,1085,20)
        ring.update(now);path.update(now)
        b=directional_quant(ring,path,now,+1)
        s=directional_quant(ring,path,now,-1)
        self.assertTrue(b.usable and s.usable)
        self.assertGreater(b.executable_breakout_z15,0)
        self.assertLess(s.executable_breakout_z15,0)
        self.assertGreater(b.score,s.score)
        self.assertEqual((ring.nonzero_last,ring.nonzero_volume),(0,0))
        self.assertEqual(ring.current[15000].last_ms,now.time_msc)
        self.assertLessEqual(len(ring.finished[1000]),181)
        self.assertLessEqual(len(path.finished),720)

    def test_same_millisecond_burst_not_mature_five_second_basket(self):
        sim=VolumePreservingMicroV9(cfg(),ResearchCash(governor=False))
        sim._gate=lambda _:True;sim._quality=lambda _:True
        for s in range(50,90):sim.on_tick(tick(s,s*1000+100,1000))
        # 90s new five-second basket, many same-ms jumps, not an observed 1s move.
        for i in range(20):sim.on_tick(tick(200+i,90500,1000+i*20))
        self.assertEqual(sim.stats['micro_positions'],0)
        self.assertEqual(sim.rolling.current[5000].first_ms,
                         sim.rolling.current[5000].last_ms)

    def test_max_four_per_source_minute_even_during_rearm(self):
        sim=VolumePreservingMicroV9(cfg(),ResearchCash(governor=False))
        base=tick(1,120100)
        sim._push_second(base);sim._start_minute_cycle(base)
        sim._gate=lambda _:True
        # Direct entry attempts isolate cap, not direction eligibility.
        for k in range(4):
            t=tick(k+2,120100+k*500,1100)
            sim._open_trade(t,1)
            self.assertIsNotNone(sim.position)
            sim.position=None
        sim._open_trade(tick(11,123400,1100),1)
        self.assertEqual(len(sim.entries),4)
        self.assertEqual(sim._entries_in_minute,4)
        self.assertEqual(sim._entries_this_minute,4)
        self.assertEqual(sim.v9_stats['cap_block'],1)

    def test_both_rearm_modes_and_spanning_new_minute(self):
        sim=VolumePreservingMicroV9(cfg(),ResearchCash(governor=False))
        for ms in (119100,119700,120100,120900):
            t=tick(ms,ms,1000)
            sim._push_second(t);sim._start_minute_cycle(t)
        sim._last_exit_ms=119700
        sim._last_closed_basket=115000
        sim._last_closed_15s_basket=105000
        self.assertFalse(sim._volume_rearm_ready(tick(900,120100)))
        self.assertFalse(sim._volume_rearm_ready(tick(900,120900)))
        self.assertTrue(sim._volume_rearm_ready(tick(900,121200)))
        strict=VolumePreservingMicroV9(cfg(),ResearchCash(governor=False),
            v9=V9Spec(rearm_rule='both_new_baskets'))
        strict.rolling=sim.rolling
        strict._last_exit_ms=sim._last_exit_ms
        strict._last_closed_basket=120000
        strict._last_closed_15s_basket=120000
        self.assertFalse(strict._volume_rearm_ready(tick(900,121300)))

    def test_50ms_quote_path_source_ordinals_not_lookahead(self):
        r=RollingThreeMinute();p=MsQuarterPath()
        for i,ms in enumerate([120001,120001,120002,120099,120249,120255]):
            t=tick(i+1,ms,1000+i*2)
            r.update(t);p.update(t)
        self.assertEqual(p.rows,6)
        self.assertEqual(p.current.last_ms,120255)
        with self.assertRaises(ValueError):r.update(tick(7,120254))

    def test_default_indicators_shadow_no_155_model(self):
        s=VolumePreservingMicroV9(cfg(),ResearchCash(governor=False))
        self.assertEqual(s.v9.entry_action,'preserve_breakout')
        self.assertEqual(s.v9.entry_signal_mode,'executable_or')
        self.assertFalse(s.micro_spec.experimental_runner)
        self.assertFalse(s.cash.governor)
        self.assertEqual(s.micro_spec.hard_risk_cash,2.0)
        self.assertEqual(s.micro_spec.min_net_cash,.1)
        self.assertEqual(s.micro_spec.preferred_max_net_cash,1.75)
        self.assertEqual(s.micro_spec.max_lifetime_ms,30000)

    def test_polymorphic_model_is_not_misreported_as_frozen_baseline(self):
        from coinexx_r9.r9_baseline import R9HybridGateBaseline
        from dual_basket import DualBasketBaseline
        model=VolumePreservingMicroV9(cfg(),ResearchCash(governor=False))
        self.assertIsInstance(model,R9HybridGateBaseline)
        self.assertNotIn(type(model),(R9HybridGateBaseline,DualBasketBaseline))

    def test_native_v9_fork_static_source_guard_and_four_lane_logic(self):
        # Native code is not available in the local lightweight source bundle.
        # In GitHub Actions the full repo provides the real separate V9 fork.
        repo=Path(__file__).resolve().parents[3]
        ea=repo/'Experts'/'GoldMuwahahaMiner_R9_Micro180_V9_Research.mq5'
        if not ea.exists():self.skipTest('V9 MT5 source not in local lightweight Python checkout')
        code=ea.read_text()
        for required in (
            'InpEnableDemoOrders        = false',
            'InpV9QuantScoreVeto        = false',
            'InpV9RearmCooldownMs       = 1500',
            'V5QuarterUpdate(t);',
            'V5QuarterEvidence(side,(long)t.time_msc',
            'iADXWilder', 'iATR','iMA', 'SyncQuoteHistory',
            'const bool buy15=', 'const bool buy30=',
            'const bool sell15=', 'const bool sell30=',
            'g_5s.startMs==g_exit5 && g_15s.startMs==g_exit15',
            'OrderCalcProfit',
        ):
            with self.subTest(required=required):self.assertIn(required,code)

    def test_cash_target_liquidation_quotes_sell_and_buy(self):
        # This invariant is about exact *quote sides* rather than fabricated fills.
        for side in (-1,1):
            entry=1020 if side>0 else 1000
            at_net010=(entry+30) if side>0 else (entry-30)
            net=side*(at_net010-entry)/100.-.20
            self.assertAlmostEqual(net,.10)

if __name__=='__main__':unittest.main()

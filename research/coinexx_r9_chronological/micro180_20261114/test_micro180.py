"""Deterministic causality, risk and execution-side tests. No external data needed."""
from __future__ import annotations

import sys
import unittest
from dataclasses import replace
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for p in (ROOT/'src',ROOT/'variable_cash_horizon_20261114',ROOT/'micro180_20261114'):
    sys.path.insert(0,str(p))
from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config
from on_policy_cash_replay import ResearchCash
from micro180 import Candle, RollingThreeMinute, Micro180Spec, Micro180R9


def q(n:int,ms:int,bid:int=1000,sp:int=10,volume:int=0,last:int=0)->Tick:
    return Tick(n,ms//1000,ms,bid,bid+sp,last_u=last,volume=volume)


def cfg()->R9Config:
    return R9Config(use_regime_gate=False,velocity_lookback_sec=2,
                    range_lookback_sec=2,min_velocity_pips=0,
                    min_directional_eff=0,min_range_pips=0,max_turns=99)


class Micro180Tests(unittest.TestCase):
    def test_fixed_grid_and_cash_contract_reject_invalid_inputs(self):
        for invalid in ({'window_ms':120000},{'basket5_ms':6000},
                        {'hard_risk_cash':.10},{'max_entries_per_source_minute':5},
                        {'min_efficiency_15s':1.1}):
            with self.subTest(invalid=invalid),self.assertRaises(ValueError):
                Micro180Spec(**invalid)

    def test_subminute_candles_are_millisecond_anchored_and_source_ordered(self):
        r=RollingThreeMinute()
        for t in (q(1,4999,1000),q(2,5000,1100),q(3,5000,1200),
                  q(4,14999,900),q(5,15000,910),q(6,30000,920)):
            r.update(t)
        b5=r.finished[5000]
        self.assertEqual(b5[0].start_ms,0)
        self.assertEqual(b5[0].bid_close,1000)
        self.assertEqual(b5[1].start_ms,5000)
        self.assertEqual(b5[1].bid_hi,1200)
        self.assertEqual(b5[1].n,2)
        self.assertEqual(r.finished[15000][0].bid_lo,900)
        self.assertEqual(r.finished[30000][0].n,5)
        self.assertEqual(len(r.finished[1000]),4) # Four completed observed seconds before second 30

    def test_sparse_seconds_never_filled_and_history_bounded(self):
        r=RollingThreeMinute()
        r.update(q(1,0)); r.update(q(2,30000));r.update(q(3,180000))
        self.assertEqual([v.start_ms for v in r.finished[1000]],[0,30000])
        for i in range(400):r.update(q(i+4,181000+i*1000))
        self.assertLessEqual(len(r.finished[1000]),181)
        self.assertLessEqual(len(r.finished[5000]),37)
        self.assertLessEqual(len(r.finished[15000]),13)
        self.assertLessEqual(len(r.finished[30000]),7)

    def test_out_of_order_time_rejected_but_equal_millisecond_allowed(self):
        r=RollingThreeMinute()
        r.update(q(1,1234));r.update(q(2,1234))
        self.assertEqual(r.current[1000].n,2)
        with self.assertRaisesRegex(ValueError,'chronology'):
            r.update(q(3,1233))

    def test_breakout_uses_completed_bid_and_ask_seconds_only(self):
        r=RollingThreeMinute()
        for sec in range(40):r.update(q(sec+1,sec*1000+5,1000+sec))
        p15,p30=r.price_levels(39005,10,18,2500)
        self.assertEqual(p15[0],1038)
        self.assertEqual(p30[1],1019) # ask = bid+10, earliest eligible sec9
        r.update(q(45,39099,6000,200))
        p15a,p30a=r.price_levels(39099,10,18,2500)
        self.assertEqual(p15a[0],p15[0])
        self.assertEqual(p30a[1],p30[1])

    def test_no_unearned_auto_reentry_on_single_five_second_reset(self):
        sim=Micro180R9(cfg(),ResearchCash(governor=True))
        for sec in range(90,137):sim.on_tick(q(sec,sec*1000+100,1000+sec))
        sim._open_trade(q(900,137500,1100),1)
        self.assertIsNotNone(sim.position)
        sim._record_close(q(901,138100,1100),'manual',1100)
        sim._arm_opposite_after_exit()
        sim.rolling.update(q(902,140100,1000))
        sim._start_minute_cycle(q(902,140100,1000))
        self.assertEqual(sim.pending_mode,0)  # both clocks have NOT reset
        sim.rolling.update(q(903,150100,1000))
        sim._start_minute_cycle(q(903,150100,1000))
        self.assertEqual(sim.pending_mode,2)  # after both clocks and cooldown

    def test_15s_completed_directional_structure_and_both_breakouts_required(self):
        sim=Micro180R9(cfg(),ResearchCash(governor=True),Micro180Spec(use_m1_directional_veto=False))
        sim._gate=lambda t:True
        sim._quality=lambda side:True
        for sec in range(90,136):
            # Past last completed 15s candle is up 14 points; entry at sec136 jumps 60.
            t=q(sec,sec*1000+100,1000+(sec-90)*2)
            sim.on_tick(t)
        # sec136 is in same 5s basket as 135, but close price not changed by a single
        # earlier period; current bid +30 should exceed the last completed Bid 30s high.
        sim.on_tick(q(1000,136100,1100))
        # New 5s age repair: one-second burst is not a mature basket.
        self.assertEqual(sim.stats['micro_positions'],0)
        sim.on_tick(q(1001,137900,1120))
        self.assertEqual(sim.stats['micro_positions'],1)
        self.assertEqual(sim.entries[-1]['side'],1)

    def test_entry_side_bid_ask_not_mid_spread_only(self):
        sim=Micro180R9(cfg(),ResearchCash(governor=True),Micro180Spec(use_m1_directional_veto=False))
        sim._gate=lambda t:True; sim._quality=lambda side:True
        for sec in range(90,136):sim.on_tick(q(sec,sec*1000+100,1000+(sec-90)*2))
        # MID jumps +70 units exclusively on Ask widening, Bid does not break out.
        sim.on_tick(q(1000,136100,1080,160))
        self.assertEqual(sim.stats['micro_positions'],0)

    def test_cash_010_harvest_buy_and_sell_executable_side(self):
        for side in (1,-1):
            sim=Micro180R9(cfg(),ResearchCash(governor=True))
            init=q(1,120000,1000,10)
            sim.on_tick(init)
            sim._open_trade(init,side)
            self.assertIsNotNone(sim.position)
            entry=sim.position.entry_price_u
            if side==1: take=q(2,120100,entry+30,10)
            else:take=q(2,120100,entry-40,10) # SELL closes at Ask = entry-30
            sim.on_tick(take)
            self.assertEqual(sim.stats['closed_cash_010_harvest'],1)
            self.assertGreaterEqual(sim._net_values[-1],.10-1e-6)

    def test_hard_cash_loss_and_account_lock_fail_closed(self):
        sim=Micro180R9(cfg(),ResearchCash(governor=True,initial_capital=100))
        sim.on_tick(q(1,120000,1000,20))
        sim._open_trade(q(2,120100,1000,20),1)
        self.assertIsNotNone(sim.position)
        # A gap exceeds the intended $2; first available quote closes with worse loss.
        sim.on_tick(q(3,120200,720,20))
        self.assertIsNone(sim.position)
        self.assertTrue(sim.account.permanent_lock is False or sim.account.day_lock)
        sim.account.permanent_lock=True
        sim._open_trade(q(4,121100,1000,20),1)
        self.assertIsNone(sim.position)

    def test_30s_window_is_stable_throughout_current_partial_second(self):
        r=RollingThreeMinute()
        for sec in range(45):r.update(q(sec,sec*1000+800,1000+sec))
        before=r.price_levels(44801,10,18,2500)
        after=r.price_levels(44999,10,18,2500)
        self.assertEqual(before[1][0],after[1][0])
        self.assertEqual(before[1][1],after[1][1])
        self.assertEqual(before[1][2],after[1][2])

    def test_protected_runner_tightens_cash_sl_for_buy_and_sell(self):
        for side in (1,-1):
            sim=Micro180R9(cfg(),ResearchCash(governor=True),
                           Micro180Spec(experimental_runner=True))
            first=q(1,120000,1000,10)
            sim.on_tick(first)
            sim._open_trade(first,side)
            self.assertIsNotNone(sim.position)
            old_sl=sim.position.sl_u
            sim._signed_trend_score=lambda direction,t:1.0
            entry=sim.position.entry_price_u
            more=q(2,120100,entry+70 if side==1 else entry-80,10)
            sim.on_tick(more)
            self.assertIsNotNone(sim.position)
            new_sl=sim.position.sl_u
            self.assertGreater((new_sl-old_sl)*side,0)
            protected_cash=side*(new_sl-entry)*sim.cash.k/100-sim.cash.cost
            self.assertGreaterEqual(protected_cash,.10-1e-8)
            self.assertEqual(sim.stats['micro_protected_runner_hold'],1)

    def test_capital_loss_gov_locks_at_25_percent_even_between_days(self):
        sim=Micro180R9(cfg(),ResearchCash(governor=True,initial_capital=100))
        t=q(1,120000,1000,10)
        sim.on_tick(t)
        sim.account.equity=74.9
        later=q(2,86400100,1000,10)
        sim.account.begin_tick(later,0)
        self.assertTrue(sim.account.permanent_lock)
        sim._open_trade(later,1)
        self.assertIsNone(sim.position)

    def test_strict_default_and_experimental_router_inputs_guarded(self):
        d=Micro180Spec()
        self.assertEqual((d.breakout_router,d.s1_mode,d.structural_confirmation),
                         ('strict_30s','strict_r9','completed_only'))
        self.assertFalse(d.experimental_runner)
        self.assertEqual((d.min_net_cash,d.preferred_max_net_cash,d.hard_risk_cash),(.10,1.75,2.))
        for invalid in ({'breakout_router':'random'},{'s1_mode':'skip_all'},
                        {'structural_confirmation':'future_bar'},
                        {'min_buy_strong_15s_z':-1.},
                        {'min_sell_strong_15s_z':-1.},
                        {'max_adverse_30s_z':-1.}):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                Micro180Spec(**invalid)

    def test_explicit_active_15s_causal_reversal_does_not_leak_to_strict_control(self):
        active=Micro180Spec(breakout_router='balanced_30s_veto',
                            s1_mode='micro_only',
                            structural_confirmation='causal_active_or_completed',
                            use_m1_directional_veto=False)
        strict=Micro180Spec(use_m1_directional_veto=False)
        def run(spec):
            sim=Micro180R9(cfg(),ResearchCash(governor=False),spec)
            sim._gate=lambda t:True
            for sec in range(90,140):
                bid=(1000 if sec<120 else 1000-(sec-120)*3) if sec<135 else 1000+(sec-135)*20
                t=q(sec,sec*1000+100,bid)
                sim._push_second(t);sim.atr.update(t);sim._start_minute_cycle(t)
            t=q(140,140100,1120)
            sim._push_second(t);sim._start_minute_cycle(t)
            interim=q(141,141100,1180)
            sim._push_second(interim);sim._start_minute_cycle(interim)
            now=q(142,142100,1200)
            sim._push_second(now);sim._start_minute_cycle(now)
            sim._process_entries(now)
            return sim
        original=run(strict)
        candidate=run(active)
        self.assertEqual(len(original.entries),0)
        self.assertEqual(len(candidate.entries),1)
        self.assertEqual(candidate.entries[-1]['side'],1)
        self.assertEqual(candidate.entries[-1]['structure_source'],'active_causal')
        self.assertGreaterEqual(candidate.entries[-1]['z15'],0.)

    def test_quote_arrivals_are_not_treated_as_traded_volume(self):
        r=RollingThreeMinute()
        r.update(q(1,1000,1000,10,volume=0,last=0))
        r.update(q(2,1000,1001,10,volume=0,last=0))
        r.update(q(3,1100,1003,10,volume=0,last=0))
        self.assertEqual((r.nonzero_last,r.nonzero_volume),(0,0))
        self.assertEqual((r.current[1000].n,r.current[5000].n),(3,3))

    def test_unvalidated_runner_never_automatically_activated(self):
        self.assertFalse(Micro180Spec().experimental_runner)
        self.assertTrue(Micro180Spec(experimental_runner=True).experimental_runner)


if __name__=='__main__':unittest.main()

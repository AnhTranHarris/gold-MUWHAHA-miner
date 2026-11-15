"""V8 measurement/contract regressions; no market-data downloads.

Native-source checks are STATIC only, not a MetaEditor compile or MT5 execution.
"""
import unittest
from pathlib import Path
from unittest.mock import patch
from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config
from on_policy_cash_replay import ResearchCash
from micro180 import RollingThreeMinute, Micro180Spec, Micro180R9
from v7_conditioned_cash import (
    _setup, ConditionedCashEvidence, V7Spec, SetupConditionedMicroV7)


def q(n,ms,bid=1000,sp=10):
    return Tick(n,ms//1000,ms,bid,bid+sp)


def cfg():
    return R9Config(use_regime_gate=False,velocity_lookback_sec=2,
        range_lookback_sec=2,min_velocity_pips=0,min_directional_eff=0,
        min_range_pips=0,max_turns=99)


class MeasurementParityV8(unittest.TestCase):
    def test_minute_rollover_does_not_erase_cooldown(self):
        m=Micro180R9(cfg(),ResearchCash(governor=False))
        for sec in range(100,119):
            t=q(sec,sec*1000+100,1000+sec)
            m._push_second(t);m._start_minute_cycle(t)
        m.pending_mode=0
        m._last_exit_ms=119500
        m._last_closed_basket=115000
        m._last_closed_15s_basket=105000
        for ms in (120100,121900):
            t=q(ms,ms,1200)
            m._push_second(t);m._start_minute_cycle(t)
            self.assertEqual(m.pending_mode,0)
        t=q(122600,122600,1200)
        m._push_second(t);m._start_minute_cycle(t)
        self.assertEqual(m.pending_mode,2)

    def test_same_millisecond_spike_not_a_5s_basket(self):
        m=Micro180R9(cfg(),ResearchCash(governor=False),
                     Micro180Spec(use_m1_directional_veto=False))
        m._gate=lambda t:True;m._quality=lambda side:True
        for sec in range(90,136):
            m.on_tick(q(sec,sec*1000+100,1000+(sec-90)*2))
        for k in range(15):
            m.on_tick(q(1000+k,135500,1100+10*k))
        self.assertEqual(m.stats['micro_positions'],0)
        self.assertGreater(m.stats['micro_5s_effective_age_reject'],0)

    def test_sparse_completed_15s_cannot_authorize_entry(self):
        m=Micro180R9(cfg(),ResearchCash(governor=False),
                     Micro180Spec(use_m1_directional_veto=False))
        m._gate=lambda t:True;m._quality=lambda side:True
        for sec in range(90,136):
            if 124<=sec<=133:continue
            m.on_tick(q(sec,sec*1000+100,1000+(sec-90)*2))
        m.on_tick(q(2001,136100,1150))
        m.on_tick(q(2002,137900,1160))
        self.assertEqual(m.stats['micro_positions'],0)
        self.assertGreater(m.stats['micro_15s_structure_reject'],0)

    def test_candle_gap_is_real_millisecond_not_bucket_name(self):
        r=RollingThreeMinute()
        for t in (q(1,120100),q(2,120100),q(3,121900),q(4,124700)):
            r.update(t)
        b=r.current[5000]
        self.assertEqual(b.last_ms-b.first_ms,4600)
        self.assertEqual((b.n,b.max_gap_ms),(4,2800))

    def test_historical_anchor_gap_detected_across_boundary(self):
        r=RollingThreeMinute()
        for i in range(110):r.update(q(i,(1000+i)*1000+55,10000+i*4))
        bars=r.closes(1110000,180000)
        ix=55;anchor=bars[ix]
        anchor.start_ms+=5000;anchor.first_ms+=5000;anchor.last_ms+=5000
        self.assertIsNone(_setup(bars,ix,+1,anchor.bid_close,
                                 anchor.ask_close,anchor.n))

    def test_live_candidate_forecast_refreshes_within_same_ms(self):
        m=SetupConditionedMicroV7(R9Config(use_regime_gate=False),
                 ResearchCash(governor=False),Micro180Spec(),
                 v7=V7Spec(enable_cash_gate=True))
        for i in range(160):
            m.rolling.update(q(i,(1000+i)*1000+55,10000+i*3))
        unavailable=ConditionedCashEvidence(1,0,0.,0.,float('-inf'),0.,0.,0,False)
        with patch('v7_conditioned_cash.conditioned_cash_first_passage',
                   return_value=unavailable) as calc:
            t1=q(900,1160100,11000)
            t2=q(901,1160101,11050)
            t3=q(902,1160101,11060)
            m._open_trade(t1,+1)
            m._open_trade(t1,+1)
            self.assertEqual(calc.call_count,2)
            m._open_trade(t2,+1);m._open_trade(t3,+1)
            self.assertEqual(calc.call_count,6)

    def test_mt5_native_repair_default_and_expression_contract(self):
        repo=Path(__file__).resolve().parents[3]
        ea=repo/'Experts'/'GoldMuwahahaMiner_R9_Micro180_V8_Research.mq5'
        inc=repo/'Experts'/'GoldMuwahahaR9V7ConditionedCash.mqh'
        if not ea.exists() or not inc.exists():
            self.skipTest('native files not present in local code-only checkout; CI verifies')
        text=ea.read_text()
        for token in (
            'InpEnableDemoOrders        = false',
            'InpV7ConditionalGateResearch   = false',
            'InpMin5sObservedSpanMs    = 1500',
            'InpMinCompleted15SpanMs  = 9000',
            'InpMinActive15SpanMs     = 3000',
            'InpMaxCompleted15TailMs  = 2500',
            'InpAllowCausalActive15   = false',
            'InpMicroOnlyS1           = false',
            'InpBalanced30sVeto       = false',
            'InpV5PathResearch           = true',
            'g_5s.lastMs-g_5s.firstMs<InpMin5sObservedSpanMs',
            'g_closed15.maxGapMs<=InpMaxQuoteGapMs',
            'g_v7LastComputeMs!=ms',
            'g_v7LastComputeQuoteN!=g_second.n',
            'g_exitMs>0',
            'iADXWilder','iATR','iMA'):
            with self.subTest(token=token):self.assertIn(token,text)
        header=inc.read_text()
        self.assertIn('q[i].firstMs-q[i-1].lastMs>2000',header)
        self.assertIn('ArrayResize(history,n)',header)
        self.assertIn('i<ArraySize(q)?i:i-1',header)


if __name__=='__main__':unittest.main()

import unittest
from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config,R9HybridGateBaseline,session_code

def T(o,s,bid,ask):return Tick(o,s,s*1000+o,bid,ask)

class R9Tests(unittest.TestCase):
    def easy(self):
        return R9Config(use_regime_gate=False,velocity_lookback_sec=2,range_lookback_sec=2,min_velocity_pips=0,min_directional_eff=0.0,min_range_pips=0,max_turns=99,stop_loss_pips=30)
    def test_cycle_rounding_matches_mql_half_up(self):
        r=R9HybridGateBaseline(self.easy())
        t=T(1,120,1000,1003);r.on_tick(t)
        self.assertEqual(r.cycle_buy_u,1017);self.assertEqual(r.cycle_sell_u,987)
    def test_no_future_tick_can_change_prior_entry_history(self):
        prefix=[T(i,120+i,1000+i*10,1002+i*10) for i in range(1,8)]
        a=R9HybridGateBaseline(self.easy())
        for t in prefix:a.on_tick(t)
        before=list(a.entries)
        for i in range(8,20):a.on_tick(T(i,120+i,900-i,902-i))
        self.assertEqual(before,a.entries[:len(before)])
    def test_entry_tick_does_not_immediately_mark_had_position(self):
        r=R9HybridGateBaseline(self.easy())
        seq=[T(1,120,1000,1002),T(2,121,1005,1007),T(3,122,1010,1012),T(4,123,1030,1032)]
        for t in seq:r.on_tick(t)
        self.assertIsNotNone(r.position);self.assertFalse(r.had_position)
        p=r.position
        stop_bid=p.sl_u-1
        r.on_tick(T(5,124,stop_bid,stop_bid+2))
        self.assertIsNone(r.position);self.assertFalse(r.had_position);self.assertEqual(r.rearms,0)
    def test_session_is_source_native_with_configured_offset_only(self):
        self.assertIn(session_code(1767315600,0),(0,1,2,3))

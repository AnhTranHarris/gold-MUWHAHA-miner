import unittest
from coinexx_r9.bars import SecondBarBuilder, CompletedM5Atr
from coinexx_r9.models import Tick

def T(o,s,ms,b,a):return Tick(o,s,ms,b,a)

class BarTests(unittest.TestCase):
    def test_second_bar_preserves_full_observed_second(self):
        b=SecondBarBuilder()
        self.assertIsNone(b.update(T(1,100,100001,1000,1003)))
        self.assertIsNone(b.update(T(2,100,100999,1005,1008)))
        x=b.update(T(3,101,101001,999,1004))
        self.assertEqual((x.tick_count,x.bid_open_u,x.bid_high_u,x.bid_low_u,x.bid_close_u),(2,1000,1005,1000,1005))
        self.assertEqual((x.ask_open_u,x.ask_high_u,x.ask_low_u,x.ask_close_u),(1003,1008,1003,1008))
        self.assertEqual((x.spread_open,x.spread_high,x.spread_low,x.spread_close),(3,3,3,3))
    def test_missing_seconds_are_not_synthesized(self):
        b=SecondBarBuilder();b.update(T(1,100,100001,1000,1002));x=b.update(T(2,105,105001,1001,1003))
        self.assertEqual(x.second,100);self.assertEqual(b.flush().second,105)
    def test_atr_uses_completed_m5_only(self):
        a=CompletedM5Atr(period=2)
        for sec,bid in [(0,1000),(299,1010),(300,1005),(599,1020),(600,1010),(899,1030),(900,1020),(1199,1040),(1200,1030)]:
            a.update(T(sec+1,sec,sec*1000,bid,bid+2))
        self.assertTrue(a.ready);self.assertIsNotNone(a.atr_u)

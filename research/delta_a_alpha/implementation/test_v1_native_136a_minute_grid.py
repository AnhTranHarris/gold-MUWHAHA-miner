"""Original 136A native minute extension source semantics, no future/P&L."""
import unittest
from dataclasses import dataclass
from v1_native_136a_minute_grid import Native136AMinuteGrid
from v1_vertical_grid import Quote,ClosedBar
H=3600000;M=60000;T=1775055600000 # 2026-04-01 15:00 UTC

def b(tf,side=1,end=T):
    o=4400000;c=o+side*1000
    return ClosedBar(tf,end-3600000,end,o,max(o,c)+1000,min(o,c)-1000,c,100)
def q(dt,mid,spread=200):
    return Quote(T+dt,mid-spread//2,mid+spread//2)

class Native136ATests(unittest.TestCase):
    def test_native_50_raw_first_advance_not_repeat(self):
        g=Native136AMinuteGrid()
        self.assertFalse(g.on_tick(q(0,4400000),b('H4'),b('H1'),'LONDON'))
        e=g.on_tick(q(100,4400060),b('H4'),b('H1'),'LONDON')
        self.assertEqual(len(e),1)
        self.assertEqual((e[0].side,e[0].rung),(1,1))
        self.assertFalse(g.on_tick(q(200,4400061),b('H4'),b('H1'),'LONDON'))
        self.assertEqual(g.on_tick(q(300,4400120),b('H4'),b('H1'),'LONDON')[0].rung,2)
    def test_no_opposite_or_unresolved_h1(self):
        g=Native136AMinuteGrid()
        self.assertFalse(g.on_tick(q(0,4400000),b('H4',1),b('H1',-1),'LONDON'))
        self.assertFalse(g.on_tick(q(100,4400300),b('H4',1),b('H1',-1),'LONDON'))
        self.assertEqual(g.raw_generated,0)
    def test_negative_native_direction(self):
        g=Native136AMinuteGrid()
        g.on_tick(q(0,4400000),b('H4',-1),b('H1',-1),'LONDON')
        e=g.on_tick(q(100,4399940),b('H4',-1),b('H1',-1),'LONDON')
        self.assertEqual((e[0].side,e[0].rung),(-1,1))
    def test_minute_reset_cannot_fabricate_cross(self):
        g=Native136AMinuteGrid()
        g.on_tick(q(0,4400000),b('H4'),b('H1'),'LONDON')
        self.assertFalse(g.on_tick(q(M,4401000),b('H4'),b('H1'),'LONDON'))
        self.assertFalse(g.on_tick(q(M+100,4401010),b('H4'),b('H1'),'LONDON'))
    def test_halt_and_spread_reanchor(self):
        g=Native136AMinuteGrid()
        g.on_tick(q(0,4400000),b('H4'),b('H1'),'LONDON')
        self.assertFalse(g.on_tick(q(100,4401000,2000),b('H4'),b('H1'),'LONDON'))
        self.assertFalse(g.on_tick(q(200,4401100),b('H4'),b('H1'),'LONDON'))
        self.assertGreater(g.spread_denied,0)
    def test_quote_gap_reanchors(self):
        g=Native136AMinuteGrid()
        g.on_tick(q(0,4400000),b('H4'),b('H1'),'LONDON')
        self.assertFalse(g.on_tick(q(61000,4405000),b('H4'),b('H1'),'LONDON'))
        self.assertGreater(g.hiatus_resets,0)
    def test_future_htf_refused(self):
        g=Native136AMinuteGrid()
        with self.assertRaises(AssertionError):g.on_tick(q(0,4400000),b('H4',end=T+100),b('H1'),'LONDON')
    def test_stale_completed_htf_cannot_reuse_weekend_state(self):
        g=Native136AMinuteGrid()
        old=b('H4',end=T-9*H)
        self.assertFalse(g.on_tick(q(0,4400000),old,b('H1'),'LONDON'))
        self.assertGreater(g.stale_htf,0)
    def test_no_cash_or_order_inventory(self):
        g=Native136AMinuteGrid()
        self.assertFalse(hasattr(g,'positions'))
        self.assertFalse(hasattr(g,'cash'))
        self.assertFalse(hasattr(g,'order_send'))

if __name__=='__main__':unittest.main()

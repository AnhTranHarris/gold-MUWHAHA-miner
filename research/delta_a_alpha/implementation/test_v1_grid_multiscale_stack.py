"""Focused canonical-grid compatibility and strictly causal S1/M1 first-touch QA."""
import unittest
from dataclasses import dataclass
from v1_grid_multiscale_stack import MultiSpeedGridGenesis
from v1_creator_grid_genesis import GridOpportunity

@dataclass(frozen=True)
class Quote:
    time_ms_utc:int
    ask_raw:int
    bid_raw:int

def q(ms,p,spread=.1):
    return Quote(ms,round(p*1000),round((p-spread)*1000))

class CreatorStub:
    ready=True
    cached_high=110.0
    cached_low=90.0

class GridReadyStub:
    def __init__(self):
        self.parent=CreatorStub()
        self.ready=True
        self.emits={}
    def on_tick(self,tick,*args,**kwargs):
        return self.emits.get(tick.time_ms_utc,())
    def stats(self):
        return {}

class MultiSpeedRegression(unittest.TestCase):
    def setUp(self):
        self.parent=GridReadyStub()
        self.g=MultiSpeedGridGenesis(parent=self.parent)
    def x(self,t,p,spread=.1,geometry='LONDON',tradable=True):
        return self.g.on_tick(q(t,p,spread),None,geometry,
                              broker_tradable=tradable)
    def test_s1_previous_closed_bar_not_new_quote(self):
        self.x(100,100);self.x(600,100.1)
        self.assertFalse(self.x(1000,100.1))
        x=self.x(1100,99.7)
        self.assertEqual((len(x),x[0].side,x[0].source),
                         (1,1,'OMEGAFX_S1_COMPLETED_FIRST_TOUCH_V1'))
    def test_distinct_m1_grid(self):
        self.x(100,100);self.x(59000,100.05)
        self.assertFalse(self.x(60000,100.05))
        self.assertEqual(self.x(60100,100.6)[0].source,
                         'OMEGAFX_M1_COMPLETED_FIRST_TOUCH_V1')
    def test_no_first_quote_phantom(self):
        self.x(500,101)
        self.assertEqual(self.x(1000,95),())
    def test_duplicate_level_direction_suppression(self):
        self.x(100,100);self.x(1000,100)
        self.x(1100,100.35);self.x(1200,100.12)
        self.assertEqual(self.x(1300,100.35),())
    def test_no_market_halt_gap_cross(self):
        self.x(100,100);self.x(1000,100)
        self.assertEqual(self.x(120000,95),())
    def test_wide_spread_does_not_invent_cross(self):
        self.x(100,100);self.x(1000,100)
        self.assertFalse(self.x(1100,100,10))
        self.assertFalse(self.x(1200,99.6,10))
    def test_raw_source_backward_time_denied(self):
        self.x(1010,100)
        with self.assertRaises(ValueError):self.x(1000,100)
    def test_source_bad_bidask_denied(self):
        with self.assertRaises(ValueError):
            self.g.on_tick(Quote(1,99000,100000),None,'LONDON')
    def test_one_event_even_with_parent_same_tick(self):
        self.x(100,100);self.x(1000,100)
        self.parent.emits[1100]=(
            GridOpportunity(1100,1,1,99.8,99.6,99.5,110,90,.25,'LONDON',100),)
        self.assertEqual(len(self.x(1100,99.6)),1)
        self.assertEqual(self.g.parent_handoff,1)
        self.assertEqual(self.g.collisions_deduped,1)
    def test_nontradable_never_emits(self):
        self.x(100,100);self.x(1000,100)
        self.assertFalse(self.x(1100,99.6,tradable=False))
    def test_no_execution_inventory_or_sizing(self):
        for n in ('cash','positions','lot_multiplier','trades','margin','order_send'):
            self.assertFalse(hasattr(self.g,n))
    def test_month_label_not_used_for_grid_selection(self):
        a=MultiSpeedGridGenesis(parent=GridReadyStub())
        b=MultiSpeedGridGenesis(parent=GridReadyStub())
        p=[(100,100),(1000,100),(1100,99.6)]
        x=[len(a.on_tick(q(t,v),None,'LONDON')) for t,v in p]
        y=[len(b.on_tick(q(t+30*86400000,v),None,'LONDON')) for t,v in p]
        self.assertEqual(x,y)

if __name__=='__main__':
    unittest.main()

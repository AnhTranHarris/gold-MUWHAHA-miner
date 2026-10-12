"""Grid prototype tests against the REAL committed creator and V1 imports."""
import unittest
from dataclasses import dataclass
from v1_grid_ready_prototype import GridReadyPrototype,MicroGridSettings
from v1_creator_grid_genesis import GridOpportunity
from v1_four_session_architecture import FourSessionV1
from v1_vertical_grid import Quote

@dataclass(frozen=True)
class Q:
    time_ms_utc:int
    ask_raw:int
    bid_raw:int
@dataclass(frozen=True)
class B:
    start_ms:int
    end_ms:int
    open_raw:int
    high_raw:int
    low_raw:int
    close_raw:int
class StubCreator:
    ready=True
    cached_high=105.0
    cached_low=95.0
    total_events=0
    def __init__(self):self.events=();self.count=0
    def on_tick(self,*a,**kw):
        self.count+=1
        result=self.events
        self.events=()
        return result
def q(t,a,spread=.12):
    return Q(t,round(a*1000),round((a-spread)*1000))
def b(i=0):
    return B(i*300000,(i+1)*300000,100000,102000,98000,100000)

class GridReadyTests(unittest.TestCase):
    def make(self):
        return GridReadyPrototype(parent=StubCreator())
    def test_fine_completed_m5_cross(self):
        g=self.make()
        self.assertEqual(g.on_tick(q(300001,100),None,'LONDON',last_completed_m5=b()),())
        z=g.on_tick(q(300002,100.51),None,'LONDON',last_completed_m5=b())
        self.assertEqual(len(z),1)
        self.assertEqual((z[0].side,z[0].source),(-1,'OMEGAFX_M5_FINE_FIRST_TOUCH_V1'))
    def test_rung_quote_jitter_not_repeated(self):
        g=self.make()
        for t,a in [(300001,100),(300002,100.51),(300003,100),(300004,100.51)]:
            v=g.on_tick(q(t,a),None,'LONDON',last_completed_m5=b())
            if t==300004:self.assertEqual(v,())
        self.assertEqual(g.stats()['micro_events_generated'],2)
    def test_new_completed_m5_rearms(self):
        g=self.make()
        g.on_tick(q(300001,100),None,'LONDON',last_completed_m5=b())
        g.on_tick(q(300002,100.51),None,'LONDON',last_completed_m5=b())
        self.assertEqual(g.on_tick(q(600001,100),None,'LONDON',last_completed_m5=b(1)),())
        self.assertTrue(g.on_tick(q(600002,100.51),None,'LONDON',last_completed_m5=b(1)))
    def test_tick_gap_no_ghost_cross(self):
        g=self.make()
        g.on_tick(q(300001,100),None,'LONDON',last_completed_m5=b())
        self.assertEqual(g.on_tick(q(370002,110),None,'LONDON',last_completed_m5=b()),())
    def test_wide_spread_cannot_set_next_cross(self):
        g=self.make()
        g.on_tick(q(300001,100),None,'LONDON',last_completed_m5=b())
        self.assertEqual(g.on_tick(q(300002,110,20),None,'LONDON',last_completed_m5=b()),())
        self.assertEqual(g.on_tick(q(300003,100),None,'LONDON',last_completed_m5=b()),())
    def test_skipped_rungs_are_not_multiple_orders(self):
        g=self.make()
        g.on_tick(q(300001,100),None,'LONDON',last_completed_m5=b())
        self.assertEqual(len(g.on_tick(q(300002,105),None,'LONDON',last_completed_m5=b())),1)
        self.assertGreater(g.stats()['skipped_quote_jump_levels_not_filled'],1)
    def test_original_creator_events_take_precedence(self):
        g=self.make()
        g.on_tick(q(300001,100),None,'LONDON',last_completed_m5=b())
        e=GridOpportunity(300002,1,1,101,100,99.9,105,95,1,'LONDON',0)
        g.parent.events=(e,)
        z=g.on_tick(q(300002,100.51),None,'LONDON',last_completed_m5=b())
        self.assertEqual(z,(e,))
        self.assertEqual(g.stats()['micro_events_generated'],1)
    def test_future_bar_refused(self):
        g=self.make()
        with self.assertRaises(AssertionError):
            g.on_tick(q(299999,100),None,'LONDON',last_completed_m5=b())
    def test_backwards_tick_refused(self):
        g=self.make()
        g.on_tick(q(300001,100),None,'LONDON',last_completed_m5=b())
        with self.assertRaises(ValueError):
            g.on_tick(q(300000,100),None,'LONDON',last_completed_m5=b())
    def test_halt_has_no_grid_orders(self):
        g=self.make()
        g.on_tick(q(300001,100),None,'LONDON',last_completed_m5=b())
        self.assertEqual(g.on_tick(q(300002,101),None,'LONDON',last_completed_m5=b(),broker_tradable=False),())
        for name in ('cash','positions','lot_multiplier','send_order','equity'):
            self.assertFalse(hasattr(g,name))
    def test_bad_settings_rejected(self):
        with self.assertRaises(ValueError):MicroGridSettings(min_gap_usd=20,maximum_gap_usd=1)
    def test_real_engine_uses_new_source_and_stays_disabled(self):
        engine=FourSessionV1()
        self.assertIsInstance(engine.creator_genesis,GridReadyPrototype)
        self.assertEqual(engine.root.funded_orders,0)
        result=engine.result()
        self.assertIn('grid_genesis_stats',result)
        self.assertEqual(result['closed'],0)
    def test_no_month_strategy_selector(self):
        self.assertNotIn('month',str(GridReadyPrototype.on_tick.__code__.co_varnames))

if __name__=='__main__':unittest.main()

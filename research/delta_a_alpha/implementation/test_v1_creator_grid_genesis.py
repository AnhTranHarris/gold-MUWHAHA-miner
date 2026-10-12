import unittest
from dataclasses import dataclass
from v1_creator_grid_genesis import CreatorGridGenesis, GenesisSettings

@dataclass(frozen=True)
class Q:
    time_ms_utc:int
    bid_raw:int
    ask_raw:int

@dataclass(frozen=True)
class B:
    start_ms:int
    end_ms:int
    open_raw:int
    high_raw:int
    low_raw:int
    close_raw:int

H=3_600_000

def q(t,ask,bid=None):
    bid=ask-.1 if bid is None else bid
    return Q(t,round(bid*1000),round(ask*1000))

def b(i,low=99.0,high=111.0):
    return B(i*H,(i+1)*H,100000,round(high*1000),round(low*1000),100000)

class GenesisTests(unittest.TestCase):
    def make(self,geometry='LONDON'):
        g=CreatorGridGenesis(GenesisSettings(h1_window=2,liquid_gap_floor_usd=1.0,
              asia_gap_floor_usd=3.0,transition_gap_floor_usd=2.0,
              spread_multiple=2.0,h1_range_fraction_liquid=.1,
              h1_range_fraction_asia=.1,h1_range_fraction_other=.1,
              max_virtual_rungs_per_direction=8))
        g.on_tick(q(2*H+1,110),b(0),geometry)
        g.on_tick(q(2*H+2,109.9),b(1),geometry)
        return g

    def test_first_creator_buy_uses_cross_from_rolling_high(self):
        g=self.make()
        # high=111, gap=1.2 -> threshold 109.8
        e=g.on_tick(q(2*H+3,109.7),b(1),'LONDON')
        self.assertEqual(len(e),1)
        self.assertEqual((e[0].side,e[0].rung),(1,1))
        self.assertAlmostEqual(e[0].crossing_level_usd,109.8,2)

    def test_staying_below_does_not_repeat(self):
        g=self.make();g.on_tick(q(2*H+3,109.7),b(1),'LONDON')
        self.assertEqual(g.on_tick(q(2*H+4,109.6),b(1),'LONDON'),())

    def test_successive_virtual_rung(self):
        g=self.make();g.on_tick(q(2*H+3,109.7),b(1),'LONDON')
        e=g.on_tick(q(2*H+4,108.4),b(1),'LONDON')
        self.assertEqual((e[0].side,e[0].rung),(1,2))
        self.assertEqual(g.total_events,2)

    def test_quiet_geometry_has_wider_gap(self):
        a=self.make('ASIA_PACIFIC')
        self.assertEqual(a.on_tick(q(2*H+3,109.5),b(1),'ASIA_PACIFIC'),())
        self.assertEqual(a.on_tick(q(2*H+4,107.9),b(1),'ASIA_PACIFIC')[0].side,1)

    def test_spread_affordability_without_promoting(self):
        g=self.make();e=g.on_tick(q(2*H+3,100,90),b(1),'LONDON')
        self.assertEqual(e,())  # spread 10 forces gap=20 above configured risk maximum
        self.assertEqual(g.total_events,0)

    def test_future_bar_refused(self):
        g=self.make()
        with self.assertRaises(AssertionError):g.on_tick(q(3*H+1,109),b(3),'LONDON')

    def test_reverse_time_refused(self):
        g=self.make()
        with self.assertRaises(ValueError):g.on_tick(q(2*H-1,109),b(1),'LONDON')

    def test_disabled_broker_no_physical_actions(self):
        g=self.make()
        self.assertEqual(g.on_tick(q(2*H+3,109.7),b(1),'LONDON',broker_tradable=False),())
        self.assertEqual(g.total_events,0)

    def test_no_physical_order_side_effects_or_scaling(self):
        g=self.make();g.on_tick(q(2*H+3,109.7),b(1),'LONDON')
        self.assertFalse(hasattr(g,'cash'))
        self.assertFalse(hasattr(g,'positions'))
        self.assertFalse(hasattr(g,'lot_multiplier'))

    def test_m5_child_is_single_entry_per_rung_per_completed_bar(self):
        g=self.make()
        g.cached_high=120  # isolate child from simultaneous parent crossing
        m=B(2*H-300000,2*H,110000,110500,109500,110000)
        # First observed quote after bar completion binds one fixed grid.
        self.assertFalse(g.on_tick(q(2*H+3,110.4),b(1),'LONDON',last_completed_m5=m))
        e=g.on_tick(q(2*H+4,109.2),b(1),'LONDON',last_completed_m5=m)
        self.assertEqual(len(e),1)
        self.assertEqual(e[0].source,'OMEGAFX_M5_COMPLETED_VIRTUAL_CHILD')
        self.assertEqual(e[0].side,1)
        self.assertAlmostEqual(e[0].crossing_level_usd,109.25,places=2)
        # No second BUY for the same crossed rung, even after price churn.
        g.on_tick(q(2*H+5,110.0),b(1),'LONDON',last_completed_m5=m)
        e=g.on_tick(q(2*H+6,109.2),b(1),'LONDON',last_completed_m5=m)
        self.assertFalse(any(z.side==1 and abs(z.crossing_level_usd-109.25)<.01 for z in e))

    def test_child_refuses_future_m5(self):
        g=self.make()
        m=B(2*H+4,2*H+300004,110000,110500,109500,110000)
        with self.assertRaises(AssertionError):
            g.on_tick(q(2*H+3,110.4),b(1),'LONDON',last_completed_m5=m)

    def test_session_transition_reanchors_child_without_phantom_event(self):
        g=self.make()
        m=B(2*H-300000,2*H,110000,110500,109500,110000)
        g.on_tick(q(2*H+3,110.4),b(1),'LONDON',last_completed_m5=m)
        g.on_tick(q(2*H+4,109.2),b(1),'LONDON',last_completed_m5=m)
        e=g.on_tick(q(2*H+5,108.0),b(1),'ASIA_PACIFIC',last_completed_m5=m)
        self.assertEqual(e,())  # no M5 child quote-trigger at session-change reset
        self.assertEqual(g.child_geometry,'ASIA_PACIFIC')

    def test_stale_completed_bar_refused(self):
        g=self.make()
        g.on_tick(q(3*H+1,110),b(2),'LONDON')
        with self.assertRaises(ValueError):g.on_tick(q(3*H+2,110),b(1),'LONDON')

if __name__=='__main__':unittest.main()

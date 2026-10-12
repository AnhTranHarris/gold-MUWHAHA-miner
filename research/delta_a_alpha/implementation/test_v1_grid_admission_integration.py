"""Test the *existing* FourSessionV1 L2→L7 admission boundary, no synthetic P&L."""
import unittest
from collections import deque
from datetime import datetime, timezone
from types import SimpleNamespace
from v1_vertical_grid import Quote, ClosedBar
from v1_creator_grid_genesis import GridOpportunity
from v1_four_session_architecture import FourSessionV1


class VerticalAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.t = int(datetime(2026, 6, 2, 13, tzinfo=timezone.utc).timestamp() * 1000)

    def engine(self, *, leverage=500):
        e = FourSessionV1(leverage=leverage, broker_session_confirmed=True)
        t = self.t
        def b(tf):
            return ClosedBar(tf, t-3600000, t, 4400000, 4403000, 4397000, 4400000, 100)
        frame = SimpleNamespace(
            l1_session=SimpleNamespace(open_desks=('LONDON', 'NEW_YORK'),
                                       suggested_geometry='LONDON_NEW_YORK_OVERLAP'),
            l2_completed_bars={tf: b(tf) for tf in ('H4', 'H1', 'M15', 'M5')})
        e.root.on_tick = lambda *args, **kw: frame
        e.creator_genesis.on_tick = lambda q, *args, **kw: (
            GridOpportunity(q.time_ms_utc, 1, 1, 4399.5, q.ask_raw/1000,
                            q.bid_raw/1000, 4403, 4397, .5,
                            'LONDON_NEW_YORK_OVERLAP', 100,
                            'TEST_CHRONOLOGICAL_GRID'),)
        e._structure = lambda *args: (1, 'TEST_COMPLETED_HTF')
        e.last_mid_by_desk = {'LONDON': 4400., 'NEW_YORK': 4400.}
        e.tick_rate = deque([t-20+i for i in range(12)])
        return e

    def quote(self, delta=0):
        return Quote(self.t+delta, 4400000, 4400200)

    def test_l4_rejection_then_valid_next_quote_not_suppressed(self):
        e = self.engine()
        e.on_tick(self.quote(), regional_holidays=('KNOWN_EVENT',),
                  simulate_broker=True, broker_tradable=True)
        self.assertEqual(e.grid_arbiter.eligible_requests, 0)
        self.assertEqual(len(e.pending), 0)
        e.on_tick(self.quote(1), simulate_broker=True, broker_tradable=True)
        self.assertEqual(e.grid_arbiter.eligible_requests, 1)
        self.assertEqual(len(e.pending), 1)
        self.assertEqual(e.pending[0].opportunity.desk, 'LONDON')
        e.on_tick(self.quote(2), simulate_broker=True, broker_tradable=True)
        self.assertEqual(e.grid_arbiter.eligible_requests, 2)
        self.assertEqual(e.pending[1].opportunity.desk, 'NEW_YORK')

    def test_unconfigured_margin_does_not_consume_6s_cooldown(self):
        e = self.engine(leverage=None)
        e.on_tick(self.quote(), simulate_broker=True, broker_tradable=True)
        self.assertEqual(e.grid_arbiter.eligible_requests, 0)
        e.leverage = 500
        e.on_tick(self.quote(1), simulate_broker=True, broker_tradable=True)
        self.assertEqual(e.grid_arbiter.eligible_requests, 1)

    def test_shadow_only_does_not_consume_request_cooldown(self):
        e = self.engine()
        e.on_tick(self.quote(), simulate_broker=False, broker_tradable=True)
        self.assertEqual(e.grid_arbiter.eligible_requests, 0)
        e.on_tick(self.quote(1), simulate_broker=True, broker_tradable=True)
        self.assertEqual(e.grid_arbiter.eligible_requests, 1)

    def test_one_request_per_quote_with_overlapping_desks(self):
        e = self.engine()
        e.on_tick(self.quote(), simulate_broker=True, broker_tradable=True)
        self.assertEqual(len(e.pending), 1)
        self.assertEqual(e.events['l7_risk_eligible_requests'], 1)
        self.assertEqual(e.grid_arbiter.eligible_requests, 1)


if __name__ == '__main__':
    unittest.main()

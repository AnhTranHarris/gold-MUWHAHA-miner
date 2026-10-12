"""True FourSessionV1 prequeue integration: no phantom capacity or margin."""
import unittest
from datetime import datetime,timezone
from types import SimpleNamespace
from collections import deque
from v1_four_session_architecture import FourSessionV1
from v1_vertical_grid import Quote,ClosedBar
from v1_creator_grid_genesis import GridOpportunity

T=int(datetime(2026,6,2,13,tzinfo=timezone.utc).timestamp()*1000)
def q(dt):return Quote(T+dt,4400000,4400200)
def engine(*,cash=300.,cap=2,leverage=500):
    e=FourSessionV1(starting_cash=cash,leverage=leverage,global_max_open=cap,broker_session_confirmed=True)
    def b(tf):return ClosedBar(tf,T-3600000,T,4400000,4403000,4397000,4400000,100)
    fr=SimpleNamespace(l1_session=SimpleNamespace(open_desks=('LONDON','NEW_YORK'),suggested_geometry='LONDON_NEW_YORK_OVERLAP'),l2_completed_bars={tf:b(tf) for tf in ('H4','H1','M15','M5')})
    e.root.on_tick=lambda *args,**kwargs:fr
    e.creator_genesis.on_tick=lambda quote,*args,**kwargs:(GridOpportunity(quote.time_ms_utc,1,1,4399.5,quote.ask_raw/1000,quote.bid_raw/1000,4403,4397,.5,'LONDON_NEW_YORK_OVERLAP',100,'CAUSAL_TEST'),)
    e._structure=lambda *args:(1,'TEST_CAUSAL_HTF')
    e.last_mid_by_desk={'LONDON':4400.,'NEW_YORK':4400.}
    e.tick_rate=deque([T-20+i for i in range(12)])
    return e

class PrequeueTests(unittest.TestCase):
    def test_no_margin_does_not_steal_cooldown(self):
        e=engine(cash=10.)
        e.on_tick(q(0),simulate_broker=True,broker_tradable=True)
        self.assertEqual(len(e.pending),0)
        self.assertEqual(e.grid_arbiter.eligible_requests,0)
        self.assertGreater(e.events['l7_prequeue_margin_denied'],0)
        e.cash=300.
        e.on_tick(q(1),simulate_broker=True,broker_tradable=True)
        self.assertEqual(len(e.pending),1)
        self.assertEqual(e.grid_arbiter.eligible_requests,1)

    def test_pending_global_capacity_reserved_before_quote_claim(self):
        e=engine(cap=1)
        e.on_tick(q(0),simulate_broker=True,broker_tradable=True)
        self.assertEqual(len(e.pending),1)
        e.on_tick(q(1),simulate_broker=True,broker_tradable=True)
        self.assertEqual(len(e.pending),1)
        self.assertEqual(e.grid_arbiter.eligible_requests,1)
        self.assertGreater(e.events['l7_prequeue_global_capacity_denied'],0)

    def test_zero_or_negative_leverage_never_consumes_request(self):
        for leverage in (0,-1):
            e=engine(leverage=leverage)
            e.on_tick(q(0),simulate_broker=True,broker_tradable=True)
            self.assertEqual(len(e.pending),0)
            self.assertEqual(e.grid_arbiter.eligible_requests,0)
            self.assertGreater(e.events['l7_no_margin_config'],0)

    def test_two_different_desk_requests_when_capacity_allows(self):
        e=engine(cap=2)
        e.on_tick(q(0),simulate_broker=True,broker_tradable=True)
        e.on_tick(q(1),simulate_broker=True,broker_tradable=True)
        self.assertEqual(len(e.pending),2)
        self.assertEqual([p.opportunity.desk for p in e.pending],['LONDON','NEW_YORK'])

if __name__=='__main__':unittest.main()

"""Actual FourSessionV1 integration tests. Run only in canonical patched checkout."""
import unittest
from datetime import datetime,timezone
from v1_four_session_architecture import FourSessionV1,Opportunity,Pending,Position
from v1_vertical_grid import Quote


def now():return int(datetime(2026,6,2,13,tzinfo=timezone.utc).timestamp()*1000)
def q(t,price=4400.):return Quote(t,int(price*1000),int((price+.20)*1000))
def pend(t,desk,side=1):
    o=Opportunity(t,desk,side,4400.,4400.2,'GRID0246_TEST',t+5000,desk,4400.)
    return Pending(o,t,t+2000)

class QuoteTransactionTests(unittest.TestCase):
    def test_simulation_disabled_cannot_close_or_earn_watchdog(self):
        e=FourSessionV1(leverage=500,broker_session_confirmed=True)
        t=now()
        e.positions.append(Position(1,'LONDON',4400.,t,4398.,4404.))
        e.on_tick(q(t+1000,4390.),simulate_broker=False,broker_tradable=True)
        self.assertEqual(len(e.positions),1)
        self.assertEqual(e.events['closed'],0)
        self.assertEqual(len(e.watchdog_closed['LONDON']),0)
        self.assertEqual(e.events['l7_position_lifecycle_deferred_permission_loss'],1)
        self.assertLess(e.equity,e.cash)

    def test_two_pending_different_quotes_fills_both_fifo(self):
        e=FourSessionV1(leverage=500,broker_session_confirmed=True,global_max_open=3)
        t=now();e.pending.extend((pend(t,'LONDON'),pend(t,'NEW_YORK')))
        e.on_tick(q(t),simulate_broker=True,broker_tradable=True)
        self.assertEqual(e.events['filled'],1)
        self.assertEqual(len(e.pending),1)
        self.assertEqual(e.events['l7_pending_deferred_next_quote'],1)
        e.on_tick(q(t+1),simulate_broker=True,broker_tradable=True)
        self.assertEqual(e.events['filled'],2)
        self.assertEqual(len(e.pending),0)
        self.assertEqual(e.positions[0].desk,'LONDON')
        self.assertEqual(e.positions[1].desk,'NEW_YORK')

    def test_exit_has_priority_over_pending_entry_same_quote(self):
        e=FourSessionV1(leverage=500,broker_session_confirmed=True,global_max_open=3)
        t=now();e.positions.append(Position(1,'LONDON',4400.,t-1000,4398.,4404.))
        e.pending.append(pend(t,'NEW_YORK'))
        e.on_tick(q(t,4390.),simulate_broker=True,broker_tradable=True)
        self.assertEqual(e.events['closed'],1)
        self.assertEqual(e.events['filled'],0)
        self.assertEqual(len(e.pending),1)
        self.assertEqual(e.events['l7_pending_deferred_next_quote'],1)

    def test_multiple_stops_deferred_to_next_quote(self):
        e=FourSessionV1(leverage=500,broker_session_confirmed=True,global_max_open=3)
        t=now()
        for desk in ('LONDON','NEW_YORK'):
            e.positions.append(Position(1,desk,4400.,t-1000,4398.,4404.))
        e.on_tick(q(t,4390.),simulate_broker=True,broker_tradable=True)
        self.assertEqual(e.events['closed'],1)
        self.assertEqual(len(e.positions),1)
        self.assertGreaterEqual(e.events['l7_exit_deferred_quote_budget'],1)
        e.on_tick(q(t+1,4390.),simulate_broker=True,broker_tradable=True)
        self.assertEqual(e.events['closed'],2)
        self.assertEqual(len(e.positions),0)

    def test_expired_deferred_order_never_fills(self):
        e=FourSessionV1(leverage=500,broker_session_confirmed=True,global_max_open=3)
        t=now();e.pending.extend((pend(t,'LONDON'),pend(t,'NEW_YORK')))
        e.on_tick(q(t),simulate_broker=True,broker_tradable=True)
        e.on_tick(q(t+3000),simulate_broker=True,broker_tradable=True)
        self.assertEqual(e.events['filled'],1)
        self.assertEqual(e.events['expired_latency'],1)
        self.assertEqual(len(e.pending),0)

if __name__=='__main__':unittest.main()

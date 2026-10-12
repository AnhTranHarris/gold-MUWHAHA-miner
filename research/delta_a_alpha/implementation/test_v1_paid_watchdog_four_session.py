"""No simulation-only P&L may impersonate an acknowledged broker-paid parent."""
import unittest
from datetime import datetime,timezone
from collections import deque
from types import SimpleNamespace
from v1_four_session_architecture import FourSessionV1,Position
from v1_vertical_grid import Quote,ClosedBar
from v1_creator_grid_genesis import GridOpportunity
T=int(datetime(2026,6,2,13,tzinfo=timezone.utc).timestamp()*1000)
def q(dt):return Quote(T+dt,4400000,4400200)
def engine():
    e=FourSessionV1(leverage=500,broker_session_confirmed=True)
    def b(tf):return ClosedBar(tf,T-3600000,T,4400000,4403000,4397000,4400000,100)
    fr=SimpleNamespace(l1_session=SimpleNamespace(open_desks=('LONDON',),suggested_geometry='LONDON'),
        l2_completed_bars={tf:b(tf) for tf in ('H4','H1','M15','M5')})
    e.root.on_tick=lambda *args,**kwargs:fr
    e.creator_genesis.on_tick=lambda quote,*args,**kwargs:(GridOpportunity(
        quote.time_ms_utc,1,1,4399.5,quote.ask_raw/1000,quote.bid_raw/1000,
        4403,4397,.5,'LONDON',100,'TEST_SOURCE'),)
    e._structure=lambda *args:(1,'TEST_COMPLETED_HTF')
    e.last_mid_by_desk={'LONDON':4400.}
    e.tick_rate=deque([T-20+i for i in range(12)])
    return e
class FourSessionPaidWatchdogTests(unittest.TestCase):
    def test_simulated_positive_parent_never_mints_broker_permit(self):
        e=engine()
        e.positions.append(Position(1,'LONDON',4395.,T-1000,4390.,4400.))
        e.on_tick(q(0),simulate_broker=True,broker_tradable=True)
        self.assertEqual(e.events['closed'],1)
        self.assertFalse(e.paid_watchdog.permit_ready('LONDON',T+1))
        self.assertEqual(e.events['l4_broker_paid_parent_context'],0)
    def test_actual_ack_settlement_is_distinct_and_later(self):
        e=engine()
        e.on_broker_parent_intent(11,'LONDON',T)
        e.on_broker_deal_add(deal_id=101,position_id=11,entry_kind='IN',
            volume=.01,commission=-.10,observed_ms=T+1)
        e.on_broker_deal_add(deal_id=102,position_id=11,entry_kind='OUT',
            volume=.01,profit=2.,commission=-.10,observed_ms=T+2)
        self.assertEqual(e.events['l4_broker_paid_parent_context'],0)
        e.on_broker_settlement(11,observed_ms=T+3,verified_broker_history=True,
                               confirmed_net_cash=1.8)
        e.on_tick(q(4),simulate_broker=False,broker_tradable=True)
        self.assertEqual(e.events['l4_broker_paid_parent_context'],1)
        self.assertEqual(e.events['filled'],0)
        self.assertEqual(e.paid_watchdog.stats()['consumed_permits'],0)

if __name__=='__main__':unittest.main()

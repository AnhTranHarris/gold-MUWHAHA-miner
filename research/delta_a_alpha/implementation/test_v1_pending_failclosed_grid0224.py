"""GRID0224: regression for pending orders after broker/simulation permission loss.

Tests are research-only, do not invoke MT5 or live trading.
"""
import unittest
from datetime import datetime
from v1_vertical_grid import Quote
from v1_four_session_architecture import FourSessionV1, Opportunity, Pending

def ms(s):
    return int(datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()*1000)

class PendingFailClosed(unittest.TestCase):
    def make(self):
        e=FourSessionV1(leverage=500,broker_session_confirmed=True)
        t=ms("2026-04-07T12:00:00Z")
        o=Opportunity(t,"LONDON",1,4400,4400.2,"TEST_GRID",t+3000,"LONDON",4400)
        e.pending.append(Pending(o,t,t+3000))
        return e,t
    def test_pending_cancelled_when_broker_closed(self):
        e,t=self.make()
        e.on_tick(Quote(t,4400000,4400200),simulate_broker=True,broker_tradable=False)
        self.assertEqual(e.events["filled"],0)
        self.assertFalse(e.pending)
    def test_pending_cancelled_when_simulation_off(self):
        e,t=self.make()
        e.on_tick(Quote(t,4400000,4400200),simulate_broker=False,broker_tradable=True)
        self.assertEqual(e.events["filled"],0)
        self.assertFalse(e.pending)
    def test_confirmed_research_simulation_still_fills(self):
        e,t=self.make()
        e.on_tick(Quote(t,4400000,4400200),simulate_broker=True,broker_tradable=True)
        self.assertEqual(e.events["filled"],1)

if __name__=="__main__":
    unittest.main()

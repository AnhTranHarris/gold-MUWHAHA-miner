"""Run ONLY on a patched, actual FourSessionV1 checkout; never mocks P/L."""
import unittest
from datetime import datetime, timezone
from v1_four_session_architecture import FourSessionV1, Opportunity, Pending, Position
from v1_vertical_grid import Quote


def t0():
    return int(datetime(2026, 6, 2, 13, tzinfo=timezone.utc).timestamp()*1000)


def pending(t):
    o=Opportunity(t,'LONDON',1,4400.,4400.2,'TEST',t+5000,'LONDON',4400.)
    return Pending(o,t,t+5000)


class PermissionSafetyTests(unittest.TestCase):
    def test_pending_cancelled_if_broker_halted(self):
        e=FourSessionV1(leverage=500,broker_session_confirmed=True)
        t=t0();e.pending.append(pending(t))
        e.on_tick(Quote(t,4400000,4400200),simulate_broker=True,broker_tradable=False)
        self.assertEqual(e.events['filled'],0)
        self.assertEqual(len(e.pending),0)
        self.assertEqual(e.events['l7_pending_cancelled_permission_loss'],1)

    def test_pending_cancelled_if_simulation_disabled(self):
        e=FourSessionV1(leverage=500,broker_session_confirmed=True)
        t=t0();e.pending.append(pending(t))
        e.on_tick(Quote(t,4400000,4400200),simulate_broker=False,broker_tradable=True)
        self.assertEqual(e.events['filled'],0)
        self.assertEqual(len(e.pending),0)
        self.assertEqual(e.events['l7_pending_cancelled_permission_loss'],1)

    def test_existing_position_not_falsely_closed_during_halt(self):
        e=FourSessionV1(leverage=500,broker_session_confirmed=True)
        t=t0()
        e.positions.append(Position(1,'LONDON',4400.,t,4398.,4404.))
        e.on_tick(Quote(t+1000,4390000,4390200),simulate_broker=True,broker_tradable=False)
        self.assertEqual(e.events['closed'],0)
        self.assertEqual(len(e.positions),1)
        self.assertEqual(e.events['l7_position_lifecycle_deferred_permission_loss'],1)

    def test_pending_fills_only_when_simulation_and_broker_both_confirmed(self):
        e=FourSessionV1(leverage=500,broker_session_confirmed=True)
        t=t0();e.pending.append(pending(t))
        e.on_tick(Quote(t,4400000,4400200),simulate_broker=True,broker_tradable=True)
        self.assertEqual(e.events['filled'],1)
        self.assertEqual(len(e.pending),0)

if __name__=='__main__':unittest.main()

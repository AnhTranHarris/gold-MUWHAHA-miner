import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from r9_replay import *

class TestReplay(unittest.TestCase):
    def test_price_rounding(self):
        self.assertEqual(mql_round_price(4321.236,.01),4321.24)
    def test_clock(self):
        self.assertEqual(offset_minutes_for_coinexx_ms(1767315600480),120)
        self.assertEqual(offset_minutes_for_coinexx_ms(int(dt.datetime(2026,7,1,tzinfo=dt.timezone.utc).timestamp()*1000)),180)
    def test_no_future_information(self):
        sim=Replay(Config(fail_closed_atr=True))
        for i in range(100):sim.on_tick(Tick(1767315600000+i*1000,1767308400000+i*1000,4300+i*.001,4300.20+i*.001))
        self.assertEqual(len(sim.entries),0)
        self.assertGreater(sim.stats['gate_no_atr'],0)
    def test_replay_state_machine_lifecycle(self):
        sim=Replay(Config(fail_closed_atr=False, max_spread_points=500, min_eff=0.,min_vel_pips=0,min_range_pips=0))
        s=1767315600
        for i in range(20):sim.on_tick(Tick((s+i)*1000,(s+i)*1000,4300.0+i*.03,4300.2+i*.03))
        self.assertGreaterEqual(sim.stats['entries'],1)
        self.assertEqual(sim.cycle_min,(s+19)//60*60)

if __name__=='__main__':unittest.main()

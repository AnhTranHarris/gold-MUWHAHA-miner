"""V2 research contract tests: no broker/real-capital performance claims."""
import sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P))
sys.path.insert(0,'/mnt/data/jan_current_integrated_engine_20261015')
from v2_performance_chassis import (Quote,Proposal,V2OrderPolicy,FundedGovernor,
                                  R9MinuteCycle,MultiTimeframeOwner,V2PerformanceChassis)
from v1_vertical_grid import ClosedBar

def q(ms,bid,spread=0.15):return Quote(ms,int(round(bid*1000)),int(round((bid+spread)*1000)))

class TestV2Contract(unittest.TestCase):
 def test_latency_not_zero_and_single_funded_slot(self):
  a=FundedGovernor(100);p=Proposal(1000,1,'R9_M1_BRACKET_S1','R9','TEST','LONDON',3100,3100,3100.1)
  self.assertTrue(a.request(p,q(1000,3100,.1)))
  self.assertFalse(a.execute(q(1249,3100,.1)))
  self.assertTrue(a.execute(q(1251,3100,.1)))
  self.assertFalse(a.request(p,q(1251,3100,.1)))
  self.assertEqual(a.pos.proposal,p)
 def test_exact_original_ask_bid_and_fee(self):
  a=FundedGovernor(100);p=Proposal(0,1,'R9_M1_BRACKET_S1','R9','TREND','LONDON',3100,3100,3100.1)
  a.request(p,q(0,3100,.1));self.assertTrue(a.execute(q(300,3100,.1)))
  # 3100.10 entry Ask, 3099.70 exit Bid -> -0.40 before $0.20 cost
  x=a.funded(q(600,3099.70,.1));self.assertIsNotNone(x)
  self.assertAlmostEqual(x[2],-.60)
  self.assertAlmostEqual(a.cash,99.4)
 def test_short_side_bid_ask_and_spread_cost(self):
  a=FundedGovernor(100);p=Proposal(0,-1,'R9_M1_BRACKET_S1','R9','RANGE','ASIA',3100,3100,3100.1)
  a.request(p,q(0,3100,.1));self.assertTrue(a.execute(q(300,3100,.1)))
  # -0.40 before commission from 3100 bid to 3100.40 ask
  x=a.funded(q(600,3100.3,.1));self.assertAlmostEqual(x[2],-.60)
 def test_rearm_requires_actual_funded_close(self):
  r=R9MinuteCycle();r.observe(q(0,3100));r.offered();self.assertEqual(r.mode,0)
  self.assertEqual(r.rearms,0)
  p=Proposal(0,1,'R9_M1_BRACKET_S1','R9','TREND','LONDON',3100,3100,3100.15)
  r.funded_close(p,23000);self.assertEqual(r.mode,-1);self.assertEqual(r.rearms,1)
  r.funded_close(p,80000);self.assertEqual(r.mode,0)
 def test_no_future_or_stale_HTF(self):
  def bar(tf,end,o,c):return ClosedBar(tf,end-300000,end,o,max(o,c),min(o,c),c,30)
  bars={'H4':bar('H4',1_000_000,200,201),'H1':bar('H1',1_000_000,200,201),'M15':bar('M15',1_000_000,200,199),'M5':bar('M5',1_000_000,200,199)}
  s=MultiTimeframeOwner();self.assertEqual(s.classify(bars,999999),('STALE',False))
  self.assertEqual(s.classify(bars,1_000_000),('OPPOSED_HTF_TRANSITION',True))
 def test_cannot_evaluate_calendar_month(self):
  c=V2PerformanceChassis(enable_native=False)
  for i in range(50):c.on_tick(q(i*1000,3100+i*.01))
  self.assertEqual(c.result()['events']['ticks'],50)
  self.assertEqual(c.result()['trades'],0)
  self.assertGreater(c.result()['events']['regime_WARMUP'],0)
 def test_policy_enforces_protected_risk(self):
  with self.assertRaises(ValueError):V2OrderPolicy(physical_max_open=10)
  with self.assertRaises(ValueError):V2OrderPolicy(latency_ms=0)
  with self.assertRaises(ValueError):V2OrderPolicy(lot=0.1)
 def test_validates_out_of_order(self):
  c=V2PerformanceChassis(enable_native=False);c.on_tick(q(3000,3100))
  with self.assertRaises(ValueError):c.on_tick(q(2000,3100))

if __name__=='__main__':unittest.main(verbosity=2)

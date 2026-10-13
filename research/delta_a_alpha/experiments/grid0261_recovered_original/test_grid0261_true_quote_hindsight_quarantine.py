"""Test exact quote direction/latency oracle API; oracle never a runtime feature."""
import unittest
import numpy as np
from grid0261_60pct_r9_oracle_reachability import oracle_events,summary
class FutureOracleQuarantineTests(unittest.TestCase):
 def test_no_same_tick_future_exit_and_true_bid_ask(self):
  t=np.array([0,100,300,600,1000,1600,2500,4500,6000,6300,7000],dtype=np.int64)
  bid=np.array([10000,10000,10000,10000,10500,10550,10800,11200,11500,11900,11800],dtype=np.int64)
  ask=bid+500
  arr,counts=oracle_events(t,ask,bid,step_ms=5000,horizon_ms=3000,latency_ms=250,fee_raw=520,spreadcap_raw=800)
  self.assertTrue(len(arr)>=1)
  # Event at t0, first delayed entry 300ms ask=10500, actual future max Bid=11200 t4500 outside 3s.
  # Within 3s from 300, best Bid=10800 -> 10800-10500-520=-220.
  self.assertEqual(int(arr[0,2]),-220)
 def test_hindsight_columns_are_honestly_two_sided(self):
  t=np.array([0,250,500,750,1000,1250,1500,1750,2000,2250,2500],np.int64)
  b=np.array([10000,10000,10000,9900,9750,9500,9000,8900,8700,8500,8300],np.int64)
  ask=b+300
  x,_=oracle_events(t,ask,b,step_ms=5000,horizon_ms=2000,latency_ms=250,fee_raw=520)
  self.assertEqual(len(x),1)
  self.assertGreater(x[0,3],x[0,2])
 def test_observed_delayed_quote_without_250ms_is_rejected(self):
  t=np.array([0,3000,6000,9000],np.int64);a=np.array([10000]*4,np.int64);b=a-200
  x,_=oracle_events(t,a,b,step_ms=5000,horizon_ms=30000,latency_ms=250)
  self.assertEqual(len(x),0)
 def test_no_future_data_in_output_is_tradable_proof(self):
  t=np.array([0,300,700,1000,1500,2000,3000,4000],np.int64)
  b=np.array([10000,10000,10000,10000,10500,10600,10700,11000],np.int64);a=b+400
  x,_=oracle_events(t,a,b,step_ms=5000,horizon_ms=3000,latency_ms=250)
  stat=summary(x)
  self.assertIn('retrospective_best_net_usd_oz',stat)
  self.assertNotIn('broker_profit',stat)
if __name__=='__main__':unittest.main()

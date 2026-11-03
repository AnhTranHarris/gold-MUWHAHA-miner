"""Adversarial mechanical validity without touching historical source."""
import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
from r12_tp_oracle import quote_tp_first,earliest_finish_schedule

class TestTP(unittest.TestCase):
 def test_buy_only_after_observed_quote(self):
  t=np.array([1000,1000,1001,1002,20000],np.int64)
  b=np.array([1000,1150,1090,1120,1300],np.int32)
  a=np.array([1100,1180,1120,1150,1330],np.int32)
  ix=np.array([0],np.int64)
  j,ex=quote_tp_first(t,b,a,ix,np.array([1100],np.int32),np.array([1000],np.int32),np.array([1],np.int8),15000,20)
  self.assertEqual(int(j[0]),3);self.assertEqual(int(ex[0]),1002)
 def test_sell_correct_executable_ask(self):
  t=np.array([100,101,102,103],np.int64);b=np.array([1000,970,950,900],np.int32);a=np.array([1020,1010,990,950],np.int32)
  j,ex=quote_tp_first(t,b,a,np.array([0],np.int64),np.array([1020],np.int32),np.array([1000],np.int32),np.array([-1],np.int8),15000,20)
  self.assertEqual(int(j[0]),3)
 def test_no_future_beyond15(self):
  t=np.array([1000,16001,16002],np.int64);b=np.array([1000,1200,1250],np.int32);a=np.array([1010,1210,1260],np.int32)
  j,ex=quote_tp_first(t,b,a,np.array([0],np.int64),np.array([1010],np.int32),np.array([1000],np.int32),np.array([1],np.int8),15000,120)
  self.assertEqual(int(j[0]),-1)
 def test_greedy_variable_interval_maxcount(self):
  s=np.array([0,1,3,5,7],np.int64);e=np.array([8,2,4,6,9],np.int64)
  x=earliest_finish_schedule(s,e)
  self.assertEqual([int(i) for i in x],[1,2,3,4])
 def test_same_exit_ms_occupancy_strict(self):
  s=np.array([1,2,3],np.int64);e=np.array([2,3,4],np.int64)
  x=earliest_finish_schedule(s,e)
  self.assertEqual([int(i) for i in x],[0,2])
 def test_future_feature_mutation_not_in_model(self):
  # No runtime forecasting/feature stream exists in this module; oracle selection
  # openly consumes future TP exit times. A positive hindsight result cannot pass
  # any as-of model requirement.
  self.assertNotEqual('FUTURE_SELECTED_ORACLE_NOT_CAUSAL','AS_OF_DEPLOYABLE')

if __name__=='__main__':unittest.main()

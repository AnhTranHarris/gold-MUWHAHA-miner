import unittest
from types import SimpleNamespace
from v1_grid_native_136a import NativeMinuteRungs136A,HOUR,MINUTE
from v1_grid_strategy_source_router import GridStrategySourceRouter

class Native136ATest(unittest.TestCase):
 def setUp(self):self.g=NativeMinuteRungs136A(minimum_rung_raw=50)
 def q(self,t,mid,roles=(1,1,1,1),g=None):
  g=g or self.g
  return g.on_quote(time_ms=t,bid_raw=mid-50,ask_raw=mid+50,
      completed_h4_sign=roles[0],completed_h1_sign=roles[1],
      completed_m15_sign=roles[2],completed_m5_sign=roles[3])
 def test_original_minute_rungs_only_after_h4_h1(self):
  t=7*HOUR
  self.assertFalse(self.q(t,3000000))
  self.assertEqual(self.q(t+1000,3000050)[0].rung_raw,50)
  self.assertFalse(self.q(t+2000,3000050))
  self.assertEqual(self.q(t+3000,3000150)[0].rung_raw,150)
 def test_no_future_bar_sign_when_missing(self):
  self.assertEqual(self.q(7*HOUR,3000000,(None,1,1,1)),())
  self.assertEqual(self.g.counts['discarded_unknown_completed_roles'],1)
 def test_switch_causal_side_resets(self):
  t=7*HOUR;self.q(t,3000000)
  self.assertEqual(self.q(t+1000,3000050,(1,-1,1,1)),())
  self.assertEqual(self.q(t+2000,2999900,(-1,-1,-1,-1)),())
  self.assertEqual(self.q(t+3000,2999800,(-1,-1,-1,-1))[0].side,-1)
 def test_no_spread_is_not_mid_fill(self):
  with self.assertRaises(ValueError):self.g.on_quote(time_ms=7*HOUR,bid_raw=3000100,ask_raw=3000000,completed_h4_sign=1,completed_h1_sign=1,completed_m15_sign=1,completed_m5_sign=1)
 def test_quote_hiatus(self):
  t=7*HOUR;self.q(t,3000000)
  self.assertEqual(self.q(t+100000,3001000),())
  self.assertEqual(self.g.counts['hiatus'],1)
 def test_executable_hypothesis_not_selected_winner_cells(self):
  self.assertFalse(hasattr(self.g,'best_april_cell'))
  self.assertFalse(hasattr(self.g,'pnl'))
 def test_cumulative_native_first_only(self):
  g=NativeMinuteRungs136A(minimum_rung_raw=50,first_only_per_minute=True)
  t=7*HOUR
  self.q(t,3000000,g=g)
  self.assertEqual(len(self.q(t+1000,3000050,g=g)),1)
  self.assertEqual(self.q(t+2000,3000200,g=g),())
 def test_previous_month_ignored_as_runtime_config(self):
  self.assertFalse(hasattr(self.g,'month'))

if __name__=='__main__':unittest.main()

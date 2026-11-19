"""Small independent invariant tests (unit fixtures, not real-price evidence)."""
import unittest
import numpy as np
from ar1_january_integrated_policy import HistoricalR9BookObserver,TradeRiskObservation,frozen_gap_cents
class TestHistoricalAR1Contract(unittest.TestCase):
 def test_frozen_tiers_unchanged(self):
  for b,g in [(10000,400),(69999,400),(70000,500),(110000,900),(1620000,1100),(1990000,1400),(2750000,1500),(2930000,2300),(3320000,2400),(3330000,3000),(34010000,7400),(90000000,7400)]:
   self.assertEqual(frozen_gap_cents(b),g)
 def test_book_updates_only_on_original_close(self):
  b=HistoricalR9BookObserver();self.assertEqual(b.start(10000,400),0)
  self.assertEqual(b.book_cents,10000)
  b.record_original_fixed_exit(926,10926)
  self.assertEqual(b.start(10926,400),0)
  b.record_original_fixed_exit(-200,10726)
  self.assertEqual(b.start(10726,400),200)
  self.assertEqual(b.book_cents,10726)
 def test_quote_side_giveback_buy_exact_transition(self):
  p=TradeRiskObservation(1,'buy',1000,2000,4000,400,0,0,0.0,None)
  tm=np.array([2000,2100,2500,3100],np.int64)
  bid=np.array([10000,10200,10090,9800],np.int64)
  ask=bid+20
  p.observe_exact_window_quote_sequence(tm,bid,ask)
  self.assertEqual(p.observed_peak_dd_cents,400)
  self.assertEqual(p.first_u25_ms,2500)
  self.assertEqual(p.first_u50_ms,3100)
  self.assertEqual(p.first_full_touch_ms,3100)
  self.assertEqual(p.state_at_end(True,False)['trade_action'],'NONE_OBSERVATIONAL_ONLY')
 def test_quote_side_sell_ask_and_no_inside_quote(self):
  p=TradeRiskObservation(2,'sell',1000,1000,2000,400,0,0,0.0,.2)
  bid=np.array([10000,10100,10250],np.int64);ask=bid+30
  p.observe_exact_window_quote_sequence(np.array([1000,1500,2000]),bid,ask)
  self.assertEqual(p.observed_peak_dd_cents,250)
  self.assertEqual(p.first_u25_ms,1500)
  self.assertEqual(p.first_u50_ms,2000)
  p2=TradeRiskObservation(3,'buy',1000,1000,2000,400,0,0,0.0,None)
  p2.observe_exact_window_quote_sequence(np.array([],np.int64),np.array([],np.int64),np.array([],np.int64))
  self.assertIsNone(p2.observed_peak_dd_cents)
  self.assertEqual(p2.state_at_end(False,True)['real_tick_quality'],'NO_INSIDE_TICK')
 def test_illegal_out_of_window_quote_raises(self):
  p=TradeRiskObservation(4,'buy',1000,1000,2000,400,0,0,0.0,None)
  with self.assertRaises(AssertionError):
   p.observe_exact_window_quote_sequence(np.array([2001]),np.array([10000]),np.array([10020]))
 def test_source_month_exact_booked_HWM(self):
  import pandas as pd
  d=pd.read_csv('/mnt/data/AR1_JAN_R6_ACCOUNT_RISK_INTEGRATED_20261118/JAN_R6_ALL_27980_INTEGRATED_ACCOUNT_RISK_OBSERVER.csv.gz',usecols=['original_R9_book_after_cents'])
  a=np.r_[10000,d.original_R9_book_after_cents.to_numpy(int)]
  self.assertEqual(int((np.maximum.accumulate(a)-a).max()),340)
if __name__=='__main__':unittest.main(verbosity=2)

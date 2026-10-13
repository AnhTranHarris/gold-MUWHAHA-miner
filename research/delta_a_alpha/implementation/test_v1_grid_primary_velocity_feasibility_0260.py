import unittest
from v1_grid_primary_velocity_feasibility_0260 import *
class Velocity(unittest.TestCase):
 def test_immutable_r9_benchmark(self):
  self.assertEqual(R9_SYNTH_COMPLETED_JAN_JUL,219342)
  self.assertEqual(R9_SYNTH_MT5_TRADING_DAYS,149)
  self.assertEqual(R9_SYNTH_BROKER_NET_USD_JAN_JUL,309122.85)
 def test_10pct_is_21935_completed(self):
  r=ceiling_for_source('H4 asof first touch',2864,inherited_completed_quote_research_tickets=1228)
  self.assertEqual(r.target_ten_pct_completed,21935)
  self.assertEqual(r.max_possible_total_research_tickets,4092)
  self.assertFalse(r.source_can_supply_ten_pct_upper_bound)
  self.assertEqual(r.min_paid_cycles_per_source_for_10pct,8)
  self.assertEqual(r.min_paid_cycles_per_source_for_full_r9,77)
 def test_high_raw_event_count_only_upper_bound_not_trades(self):
  r=ceiling_for_source('H4',30000)
  self.assertTrue(r.source_can_supply_ten_pct_upper_bound)
  self.assertFalse(r.broker_cash_achieved)
 def test_paid_child_finite_and_bounded(self):
  r=ceiling_for_source('H4',2864,inherited_completed_quote_research_tickets=1228,max_distinct_children_per_source_event=8)
  self.assertTrue(r.source_can_supply_ten_pct_upper_bound)
 def test_no_server_clock_no_daily_cash_comparison(self):
  r=ceiling_for_source('H4',30000,verified_broker_cash=True)
  self.assertFalse(r.daily_cash_comparison_authorized)
 def test_no_broker_cash_no_daily_cash_comparison(self):
  r=ceiling_for_source('H4',30000,verified_mt5_server_utc_clock=True)
  self.assertFalse(r.daily_cash_comparison_authorized)
 def test_empty_events_reports_unreachable(self):
  r=ceiling_for_source('H4',0)
  self.assertEqual(r.min_paid_cycles_per_source_for_10pct,-1)
 def test_prevent_unbounded_and_negative_event_count(self):
  with self.assertRaises(ValueError):ceiling_for_source('H4',-1)
  with self.assertRaises(ValueError):ceiling_for_source('H4',100,max_distinct_children_per_source_event=-1)
if __name__=='__main__':unittest.main()

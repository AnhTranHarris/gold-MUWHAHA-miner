import unittest
import pandas as pd
from v1_grid_daily_r9_scoreboard_0259 import *

class R9DailyAuditTests(unittest.TestCase):
 def setUp(self):
  self.s=pd.DataFrame({'entry':[1,30_000,60_000,86_400_000],
     'exit':[10_000,35_000,120_000,86_410_000],
     'direction':[1,-1,1,-1],
     'net':[10.0,-1.0,2.0,4.0],
     'cohort':['H1','H4','H1','X']})
  self.r=pd.DataFrame({'mt5_server_day':['1970-01-01','1970-01-02'],
   'closed_positions':[10,14],'net_usd':[100,150],
   'gross_profit_usd':[101,151], 'gross_loss_usd':[-1,-1]})
 def test_all_closes_and_gross(self):
  d=summarize_source(self.s,level='day');self.assertEqual(d.completed.sum(),4)
  self.assertAlmostEqual(d.gross_loss_quote_usd_oz.sum(),-1)
  self.assertAlmostEqual(d.gross_profit_quote_usd_oz.sum(),16)
 def test_no_r9_cash_conversion(self):
  out=audit_report(self.s,self.r)
  self.assertFalse(out['cross_feed_net_cash_comparable'])
  self.assertTrue(out['not_promoted'])
 def test_reject_unapproved_time_domain(self):
  c=ClockCertification(0,False,False)
  with self.assertRaises(ValueError):daily_r9_comparison(self.s,self.r,clock=c)
 def test_explicit_approved_mapping_separates_broker_net(self):
  c=ClockCertification(0,True,True)
  z=daily_r9_comparison(self.s,self.r,clock=c)
  self.assertEqual(len(z),2)
  self.assertFalse(z.broker_net_parity_certified.any())
  self.assertEqual(z.completed.sum(),4)
 def test_benchmark_full_and_half_target_not_fabricated(self):
  q=benchmark_r9_daily(self.r)
  self.assertEqual(q.target_trades_r9_50pct.tolist(),[5,7])
  self.assertEqual(q.target_net_r9_100pct_usd.tolist(),[100,150])
 def test_negative_source_settlement_valid_and_visible(self):
  s=self.s.copy();s.loc[0,'net']=-100
  d=summarize_source(s,level='day');self.assertFalse(d.iloc[0].net_positive)
 def test_incomplete_source_fails_closed(self):
  with self.assertRaises(ValueError):summarize_source(self.s.drop(columns='exit'),level='day')
 def test_future_source_exit_before_entry_fails(self):
  s=self.s.copy();s.loc[0,'exit']=-1
  with self.assertRaises(ValueError):audit_report(s,self.r)
 def test_time_domain_period_is_utc_unless_explicit(self):
  c=ClockCertification(60,True,True)
  self.assertNotEqual(summarize_source(self.s,level='hour',clock=c).iloc[0].period,
                      summarize_source(self.s,level='hour').iloc[0].period)
 def test_unpaired_r9_calendar_day_has_zero_not_hidden(self):
  s=self.s.iloc[:1]
  d=daily_r9_comparison(s,self.r,clock=ClockCertification(0,True,True))
  self.assertEqual(d.completed.tolist(),[1,0])
 def test_duplicate_r9_target_dates_fails(self):
  with self.assertRaises(ValueError):benchmark_r9_daily(pd.concat([self.r,self.r.iloc[:1]]))
 def test_no_arbitrary_period(self):
  with self.assertRaises(ValueError):summarize_source(self.s,level='minute')
if __name__=='__main__': unittest.main()

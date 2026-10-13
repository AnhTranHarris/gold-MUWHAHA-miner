import unittest
from v1_grid_r9_60pct_economic_gate_0261 import *
class TestSixtyPercentAcceptance(unittest.TestCase):
 def make(self):
  return {g.month:BrokerPeriod(g.month,g.required_mt5_cash_usd+1,g.required_completed_deals,True)
          for g in goals()}
 def test_goals_exact(self):
  t=goals();self.assertEqual(len(t),7)
  self.assertEqual(t[0].required_completed_deals,16788)
  self.assertEqual(t[-1].required_completed_deals,14630)
 def test_missing_clock_fails_closed(self):
  self.assertFalse(assess_60pct_monthly(self.make(),verified_broker_contract_fees_margin=True)['science_promotion_accepted'])
 def test_missing_broker_funding_fails_closed(self):
  self.assertFalse(assess_60pct_monthly(self.make(),verified_mt5_to_utc_calendar=True)['science_promotion_accepted'])
 def test_oracle_labels_fails_closed_even_if_everything_else_passes(self):
  self.assertFalse(assess_60pct_monthly(self.make(),verified_mt5_to_utc_calendar=True,
     verified_broker_contract_fees_margin=True,hindsight_labels_present=True)['science_promotion_accepted'])
 def test_unmapped_utc_quote_proxy_never_passes(self):
  x=self.make();x['2026-01']=BrokerPeriod('2026-01',1e9,100000,True,source='DUKAS_QUOTES_USD_PER_OZ')
  self.assertFalse(assess_60pct_monthly(x,verified_mt5_to_utc_calendar=True,
             verified_broker_contract_fees_margin=True)['science_promotion_accepted'])
 def test_all_week_constraint(self):
  x=self.make();x['2026-03']=BrokerPeriod('2026-03',1e6,100000,False)
  self.assertFalse(assess_60pct_monthly(x,verified_mt5_to_utc_calendar=True,
             verified_broker_contract_fees_margin=True)['science_promotion_accepted'])
 def test_incomplete_months_not_promoted(self):
  x=self.make();del x['2026-07'];a=assess_60pct_monthly(x,verified_mt5_to_utc_calendar=True,
             verified_broker_contract_fees_margin=True)
  self.assertFalse(a['science_promotion_accepted']);self.assertEqual(a['missing_months'],['2026-07'])
 def test_hypothetically_valid_broker_cash_can_pass(self):
  x=assess_60pct_monthly(self.make(),verified_mt5_to_utc_calendar=True,
             verified_broker_contract_fees_margin=True)
  self.assertTrue(x['science_promotion_accepted'])
 def test_oracle_capacity_never_certifies_cash(self):
  counts={g.month:g.required_completed_deals+1000 for g in goals()}
  z=oracle_density_is_evidence_only(counts,slots=16)
  self.assertTrue(z['retrospective_eligibility_can_supply_count_in_each_month'])
  self.assertFalse(z['causally_executable_deal_count_certified']);self.assertTrue(z['cannot_be_promoted'])
 def test_source_empty_fails(self):
  z=oracle_density_is_evidence_only({},slots=8)
  self.assertFalse(z['retrospective_eligibility_can_supply_count_in_each_month'])
if __name__=='__main__':unittest.main()

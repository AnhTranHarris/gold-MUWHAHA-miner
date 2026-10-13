import unittest
from v1_grid0185_multiscale_permission_0256 import *
class TestOriginalStrictRole(unittest.TestCase):
 def q(self,**k):
  d=dict(t1_ms=10000,source_t1_verified=True,observed_t2_ms=12000,kind=0,h4=1,h1=1,m15=1,m5=-1,
      h1_structural_location=.12,bid_raw=4000000,ask_raw=4000300,completed_m5_tr_raw=1000)
  d.update(k);return StrictJ179FObservedT2(**d)
 def runq(self,x,**q):
  return x.evaluate(self.q(**q),current_j179f_reserved=0,current_global_reserved=0,
                prior_completed_hourly_pnl_raw={},prior_completed_hourly_close_count={})
 def test_original_base(self):
  o=self.runq(OriginalJ179FStrictPermission0256())
  self.assertEqual((o.direction,o.role,o.research_horizon_ms),(1,'BASE',5400000))
 def test_ignition(self):
  o=self.runq(OriginalJ179FStrictPermission0256(),m5=1)
  self.assertEqual(o.role,'IGNITION')
 def test_h4_source_role(self):
  o=self.runq(OriginalJ179FStrictPermission0256(),kind=1,h1_structural_location=.8)
  self.assertEqual(o.role,'STRICT_H4')
 def test_paid_prior_close_must_exist(self):
  x=OriginalJ179FStrictPermission0256()
  q=self.q(h1=-1,m5=-1,h1_structural_location=.5)
  self.assertIsNone(x.evaluate(q,current_j179f_reserved=0,current_global_reserved=0,
                        prior_completed_hourly_pnl_raw={},prior_completed_hourly_close_count={}))
  h=q.observed_t2_ms//3600000
  o=x.evaluate(q,current_j179f_reserved=0,current_global_reserved=0,
               prior_completed_hourly_pnl_raw={h-1:-20000},prior_completed_hourly_close_count={h-1:1})
  self.assertEqual((o.role,o.direction),('PAID_PRIOR_4H_TRANSITION',-1))
 def test_quote_spread_and_time_gap_fail_closed(self):
  x=OriginalJ179FStrictPermission0256()
  self.assertIsNone(self.runq(x,ask_raw=4002000))
  self.assertIsNone(self.runq(x,observed_t2_ms=29000))
 def test_wrong_h4_alignment_abstains(self):
  x=OriginalJ179FStrictPermission0256()
  self.assertIsNone(self.runq(x,m15=-1))
 def test_12_source_and_16_global_limits(self):
  x=OriginalJ179FStrictPermission0256();q=self.q()
  self.assertIsNone(x.evaluate(q,current_j179f_reserved=12,current_global_reserved=12,
                            prior_completed_hourly_pnl_raw={},prior_completed_hourly_close_count={}))
  self.assertIsNone(x.evaluate(q,current_j179f_reserved=11,current_global_reserved=16,
                            prior_completed_hourly_pnl_raw={},prior_completed_hourly_close_count={}))
 def test_source_unverified_cannot_enter(self):
  x=OriginalJ179FStrictPermission0256()
  self.assertIsNone(self.runq(x,source_t1_verified=False))
 def test_no_multiple_same_tick(self):
  x=OriginalJ179FStrictPermission0256()
  self.assertIsNotNone(self.runq(x))
  self.assertIsNone(self.runq(x))
 def test_no_calendar_month_feature_or_overfit_or_trade_sender(self):
  x=OriginalJ179FStrictPermission0256()
  self.assertFalse(any(hasattr(x,k) for k in ('overfit','month','future_label','positions','send_order','cash')))
 def test_risk_pilot_one_per_hour_after_realized_losses(self):
  x=OriginalJ179FStrictPermission0256();q=self.q(finished_day_loss_raw=50000)
  a=x.evaluate(q,current_j179f_reserved=0,current_global_reserved=0,prior_completed_hourly_pnl_raw={},prior_completed_hourly_close_count={})
  self.assertIsNotNone(a)
  b=x.evaluate(self.q(t1_ms=15000,observed_t2_ms=17000,finished_day_loss_raw=50000),current_j179f_reserved=0,current_global_reserved=0,prior_completed_hourly_pnl_raw={},prior_completed_hourly_close_count={})
  self.assertIsNone(b)
if __name__=='__main__':unittest.main()


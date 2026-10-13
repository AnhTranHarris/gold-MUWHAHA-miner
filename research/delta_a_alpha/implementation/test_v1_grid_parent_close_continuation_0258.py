import unittest
from v1_grid_parent_close_continuation_0258 import SettledSourceParent,EarnedMultigeometryRenewal0258

class PaidParentStrictMicroRenewal(unittest.TestCase):
 def parent(self,id=1,close=1000,side=1,net=2000,prev5=1500,continuous=True,quote=True):
  return SettledSourceParent(id,close,side,net,prev5,continuous,quote)
 def quote(self,mod,t=1250,bid=4000000,ask=4000500,capacity=5,tradable=True):
  return mod.on_observed_quote(time_ms=t,bid_raw=bid,ask_raw=ask,tradable=tradable,global_active_positions=capacity)
 def test_quote_after_250ms_first_observation(self):
  x=EarnedMultigeometryRenewal0258();x.observe_parent_close(self.parent())
  self.assertEqual(self.quote(x,1249),())
  p=self.quote(x,1251);self.assertEqual(len(p),1);self.assertEqual(p[0].fixed_research_qty_oz,1)
 def test_one_g0_per_same_quote(self):
  x=EarnedMultigeometryRenewal0258();x.observe_parent_close(self.parent());x.observe_parent_close(self.parent(id=2))
  self.assertEqual(len(self.quote(x,1260)),1)
  self.assertEqual(x.stats()['accepted'],1)
 def test_no_costless_child_if_prior_loss(self):
  x=EarnedMultigeometryRenewal0258();x.observe_parent_close(self.parent(net=-1))
  self.assertEqual(self.quote(x,1300),())
 def test_displacement_must_be_aligned_and_completed(self):
  for prev,continuous in [(999,True),(1000,False)]:
   x=EarnedMultigeometryRenewal0258();x.observe_parent_close(self.parent(prev5=prev,continuous=continuous))
   self.assertEqual(self.quote(x,1300),())
 def test_executable_bidask_spread_bound(self):
  x=EarnedMultigeometryRenewal0258();x.observe_parent_close(self.parent())
  self.assertEqual(self.quote(x,1300,ask=4000700),())
 def test_global_full_16_fails_closed(self):
  x=EarnedMultigeometryRenewal0258();x.observe_parent_close(self.parent())
  self.assertEqual(self.quote(x,1300,capacity=16),())
 def test_chronology_and_duplicate_parent(self):
  x=EarnedMultigeometryRenewal0258();x.observe_parent_close(self.parent())
  with self.assertRaises(ValueError):x.observe_parent_close(self.parent())
  self.quote(x,1300)
  with self.assertRaises(ValueError):self.quote(x,1200)
 def test_expired_quote_not_retried(self):
  x=EarnedMultigeometryRenewal0258();x.observe_parent_close(self.parent())
  self.assertEqual(self.quote(x,3001),());self.assertEqual(x.expired,1)
 def test_closed_session_abstains(self):
  x=EarnedMultigeometryRenewal0258();x.observe_parent_close(self.parent())
  self.assertEqual(self.quote(x,1260,tradable=False),())
 def test_horizon_only_not_order(self):
  x=EarnedMultigeometryRenewal0258();x.observe_parent_close(self.parent())
  q=self.quote(x,1250)[0]
  self.assertEqual(q.horizon_ms,600000)
  self.assertFalse(x.stats()['trading_enabled'])
  self.assertFalse(x.stats()['funded_broker_cash_verified'])
  self.assertFalse(hasattr(x,'broker_order_send'))
 def test_quote_order_monotone(self):
  x=EarnedMultigeometryRenewal0258();self.quote(x,1500)
  with self.assertRaises(ValueError):self.quote(x,1499)
if __name__=='__main__':unittest.main()
import unittest
from v1_grid_earned_h4_extension_0257 import *
class EarnedH4Tests(unittest.TestCase):
 def paid(self,engine,values):
  for i,amt in enumerate(values):
   engine.record_base_close(ConfirmedBaseClose(100+i,i,1000+i*100,amt,actually_paid=True,quote_reconciled=True))
 def ask(self,e,**v):
  d=dict(source_owner=10,source_invite_id=25,source_time_ms=4000,
     direction=1,active_base_positions=2,active_h4_positions=2,
     active_global_positions=10,source_verified=True,observed_tradable_quote_ms=4050)
  d.update(v);return e.request(**d)
 def test_positive_prior_five_paid_base_confirms_extra_one_ounce(self):
  e=H4EarnedExtensionPermission0257();self.paid(e,[100,-300,100,200,600]);p=self.ask(e)
  self.assertEqual(p.previous_five_paid_base_net_raw,700)
  self.assertEqual(e.stats()['max_h4_slots'],4)
 def test_never_size_multiply_or_approve_paid_cash_without_ack(self):
  e=H4EarnedExtensionPermission0257()
  with self.assertRaises(ValueError):e.record_base_close(ConfirmedBaseClose(1,1,100,200,actually_paid=False,quote_reconciled=True))
  self.assertFalse(e.stats()['broker_cash_verified'])
 def test_negative_or_zero_last_five_abstains(self):
  e=H4EarnedExtensionPermission0257();self.paid(e,[100,100,-300,0,100]);self.assertIsNone(self.ask(e))
 def test_minimum_five_realized_closes(self):
  e=H4EarnedExtensionPermission0257();self.paid(e,[1000]*4);self.assertIsNone(self.ask(e))
 def test_duplicate_invite_id_is_denied(self):
  e=H4EarnedExtensionPermission0257();self.paid(e,[1000]*5)
  self.assertIsNotNone(self.ask(e));self.assertIsNone(self.ask(e))
 def test_global_and_source_capacity_preserved(self):
  e=H4EarnedExtensionPermission0257();self.paid(e,[1000]*5)
  self.assertIsNone(self.ask(e,active_global_positions=16))
  self.assertIsNone(self.ask(e,active_h4_positions=4))
  self.assertIsNone(self.ask(e,active_base_positions=1))
  self.assertIsNotNone(self.ask(e))
 def test_delayed_or_backdated_quote_denied(self):
  e=H4EarnedExtensionPermission0257();self.paid(e,[1000]*5)
  self.assertIsNone(self.ask(e,observed_tradable_quote_ms=3999))
  self.assertIsNone(self.ask(e,observed_tradable_quote_ms=5001))
  self.assertIsNotNone(self.ask(e,observed_tradable_quote_ms=4000))
 def test_no_future_paid_close_credit(self):
  e=H4EarnedExtensionPermission0257();self.paid(e,[1000]*5)
  self.assertIsNone(self.ask(e,observed_tradable_quote_ms=1300,source_time_ms=1300))
 def test_only_actual_base_realized_not_child_profit(self):
  e=H4EarnedExtensionPermission0257()
  with self.assertRaises(ValueError):e.record_base_close(ConfirmedBaseClose(1,1,100,10000,
    source='GRID0257_H4_EARNED_EXTENSION_RESEARCH_ONLY',actually_paid=True,quote_reconciled=True))
 def test_distinct_owner_can_have_own_invitation(self):
  e=H4EarnedExtensionPermission0257();self.paid(e,[1000]*5)
  self.assertIsNotNone(self.ask(e))
  self.assertIsNotNone(self.ask(e,source_owner=11))
 def test_paid_close_duplicate_forbidden(self):
  e=H4EarnedExtensionPermission0257();self.paid(e,[1000]*5)
  with self.assertRaises(ValueError):e.record_base_close(ConfirmedBaseClose(10,2,2000,10,actually_paid=True,quote_reconciled=True))
if __name__=='__main__':unittest.main()

import unittest
from types import SimpleNamespace
from v1_grid_renewal_signature import (ORIGINAL_SOURCE_UNIT,RenewalSignature,
     source_profit_bucket,hold_bucket,signature_from_original,broker_cash_context)
class SignatureTest(unittest.TestCase):
 def test_original_profit_boundaries(self):
  vals=[(None,-1),(-1,0),(0,0),(.01,1),(.499,1),(.5,2),(.999,2),(1,3),(1.999,3),(2,4),(40,4)]
  self.assertEqual([(v,source_profit_bucket(v,unit=ORIGINAL_SOURCE_UNIT)) for v,_ in vals],[(v,b) for v,b in vals])
 def test_original_hold_boundaries(self):
  vals=[(None,-1),(0,0),(30,0),(30.01,1),(60,1),(60.01,2),(120,2),(180,3),(300,4),(300.01,5)]
  self.assertEqual([hold_bucket(v) for v,_ in vals],[b for v,b in vals])
 def test_never_reinterpret_broker_cash_as_archive_p(self):
  with self.assertRaises(ValueError):source_profit_bucket(5,unit='BROKER_USD_CASH')
 def test_no_ghost_parent(self):
  with self.assertRaises(ValueError):signature_from_original(rule_index=2,depth=2,previous_source_p=3,previous_h_seconds=15,parent_ticket_id=None)
 def test_archived_signature_exact(self):
  s=signature_from_original(rule_index=3,depth=7,previous_source_p=.75,previous_h_seconds=61,parent_ticket_id=777)
  self.assertEqual((s.rule_index,s.depth,s.prior_profit_bucket,s.prior_hold_bucket),(3,7,2,2))
 def test_broker_paid_context_preserves_unit_separation(self):
  paid=SimpleNamespace(ticket_id=7,close_ms=4,realized_net_cash=3.,duration_ms=50000)
  campaign=SimpleNamespace(last_paid_close={1:paid,-1:None})
  proposal=SimpleNamespace(side=1,quote_ms=5,prior_paid_close_id=7)
  c=broker_cash_context(proposal,campaign)
  self.assertEqual(c['prior_hold_bucket'],1)
  self.assertIsNone(c['april_136_source_profit_bucket'])
 def test_nonfinite_rejection(self):
  with self.assertRaises(ValueError):source_profit_bucket(float('nan'),unit=ORIGINAL_SOURCE_UNIT)
if __name__=='__main__':unittest.main()

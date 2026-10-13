import unittest
from decimal import Decimal
from v1_grid_mt5_transaction_contract_0263 import *
class BrokerEvidenceTests(unittest.TestCase):
 def ledger(self,verified=True):
  l=MT5EventContractResearchOnly(account_mode='HEDGING',verified_symbol=verified)
  l.submit(BrokerOrder('source:1','order:1',1000,1250,1,Decimal('.02'),4000000,600000))
  return l
 def approve(self,l):l.check('order:1',approved=True);l.send('order:1',accepted=True)
 def deal(self,ident,amount='.01',tm=1500):return BrokerDeal('order:1',ident,tm,Decimal(amount),4000100)
 def test_check_is_not_fill(self):
  l=self.ledger();l.check('order:1',approved=True)
  self.assertEqual(l.summary()['broker_filled_entries'],0)
  with self.assertRaises(ValueError):l.fill(self.deal('d'))
 def test_send_accepted_is_not_fill(self):
  l=self.ledger();self.approve(l);self.assertEqual(l.summary()['broker_filled_entries'],0)
 def test_partial_fill_is_explicit(self):
  l=self.ledger();self.approve(l)
  l.fill(self.deal('d1'))
  self.assertEqual(l.orders['order:1'].entry_lots,Decimal('.01'))
  l.fill(self.deal('d2',tm=1600));self.assertEqual(l.orders['order:1'].entry_lots,Decimal('.02'))
 def test_reject_overfill(self):
  l=self.ledger();self.approve(l);l.fill(self.deal('d1',amount='.02'))
  with self.assertRaises(ValueError):l.fill(self.deal('d2',tm=1600))
 def test_reject_duplicate_id(self):
  l=self.ledger();self.approve(l);l.fill(self.deal('d1'))
  with self.assertRaises(ValueError):l.fill(self.deal('d1',tm=1600))
 def test_unverified_broker_mode_fails_closed(self):
  l=self.ledger(verified=False);self.approve(l)
  with self.assertRaises(ValueError):l.fill(self.deal('d1'))
 def test_rejected_stop_modify_does_not_change_state(self):
  l=self.ledger();self.approve(l);l.fill(self.deal('d1'))
  self.assertIsNone(l.modify_stop('order:1',modify_id='m',at_ms=1550,proposed_stop_raw=4001000,broker_accepted=False,freeze_clear=True))
 def test_accepted_stop_modify_requires_freeze_clear(self):
  l=self.ledger();self.approve(l);l.fill(self.deal('d1'))
  self.assertIsNone(l.modify_stop('order:1',modify_id='m',at_ms=1550,proposed_stop_raw=4001000,broker_accepted=True,freeze_clear=False))
  self.assertEqual(l.modify_stop('order:1',modify_id='m2',at_ms=1600,proposed_stop_raw=4001000,broker_accepted=True,freeze_clear=True),4001000)
 def test_stop_reject_duplicate_modify(self):
  l=self.ledger();self.approve(l);l.fill(self.deal('d1'));l.modify_stop('order:1',modify_id='m',at_ms=1600,proposed_stop_raw=4001000,broker_accepted=False,freeze_clear=True)
  with self.assertRaises(ValueError):l.modify_stop('order:1',modify_id='m',at_ms=1700,proposed_stop_raw=4001000,broker_accepted=True,freeze_clear=True)
 def test_no_over_close(self):
  l=self.ledger();self.approve(l);l.fill(self.deal('d1'))
  with self.assertRaises(ValueError):l.close(self.deal('cx',amount='.02',tm=1600))
 def test_close_net_from_broker_not_quotation(self):
  l=self.ledger();self.approve(l);l.fill(self.deal('d1',tm=1600))
  l.close(BrokerDeal('order:1','cx',1700,Decimal('.01'),4000900,Decimal('3.4'),Decimal('-.2')))
  self.assertEqual(l.confirmed_net_cash,Decimal('3.2'))
  self.assertEqual(l.summary()['open_lots'],'0.00')
 def test_order_source_must_precede_request(self):
  with self.assertRaises(ValueError):BrokerOrder('src','o',2000,1000,1,Decimal('.01'),200,3000)
 def test_entry_fee_reconciles_before_first_close(self):
  l=self.ledger();self.approve(l)
  l.fill(BrokerDeal('order:1','entfee',1600,Decimal('.01'),4000100,Decimal('0'),Decimal('-.10')))
  self.assertEqual(l.confirmed_net_cash,Decimal('-.10'))
  l.close(BrokerDeal('order:1','exfee',1700,Decimal('.01'),4000900,Decimal('3.4'),Decimal('-.2')))
  self.assertEqual(l.confirmed_net_cash,Decimal('3.10'))
 def test_rejected_check_cannot_send(self):
  l=self.ledger();l.check('order:1',approved=False)
  with self.assertRaises(ValueError):l.send('order:1',accepted=True)
 def test_reject_nonfinite_cash(self):
  with self.assertRaises(ValueError):BrokerDeal('o','d',1000,Decimal('.01'),3000000,Decimal('NaN'))
if __name__=='__main__':unittest.main()

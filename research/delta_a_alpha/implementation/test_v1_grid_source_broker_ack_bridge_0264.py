import unittest
from decimal import Decimal
from v1_grid_source_broker_ack_bridge_0264 import GridSourceBrokerAckBridge0264,PaidSourceBinding
from v1_grid_mt5_transaction_contract_0263 import MT5EventContractResearchOnly,BrokerOrder,BrokerDeal
from v1_grid_funded_campaign import FundedGridCampaign,SourceProposal
from types import SimpleNamespace as NS

class AcknowledgementTests(unittest.TestCase):
 def setUp(self):
  self.c=MT5EventContractResearchOnly(account_mode='HEDGING',verified_symbol=True)
  self.r=NS(funded=FundedGridCampaign())
  self.r.funded.proposals[7]=SourceProposal(7,1000,1,1,4000000,3999800,4000000,None)
  self.c.submit(BrokerOrder('g0:7','order7',1000,1100,1,Decimal('.01'),3990000,300000))
  self.a=GridSourceBrokerAckBridge0264(router=self.r,contract=self.c)
  self.a.bind(PaidSourceBinding(7,'order7',88,'g0:7'))
 def fill(self):
  self.c.check('order7',approved=True);self.c.send('order7',accepted=True)
  self.c.fill(BrokerDeal('order7','d1',1400,Decimal('.01'),4000100,fee_cash=Decimal('-.10')))
 def test_order_send_is_not_paid_fill(self):
  self.c.check('order7',approved=True);self.c.send('order7',accepted=True)
  with self.assertRaises(ValueError):self.a.ack_full_entry(88)
  self.assertFalse(self.r.funded.open_tickets)
 def test_broker_confirmed_paid_anchor(self):
  self.fill();self.a.ack_full_entry(88)
  self.assertIn(88,self.r.funded.open_tickets)
  self.assertEqual(self.r.funded.last_filled_price_raw[1],4000100)
 def test_broker_close_fee_and_cash(self):
  self.fill();self.a.ack_full_entry(88)
  self.c.close(BrokerDeal('order7','close1',1800,Decimal('.01'),4001500,Decimal('3.50'),Decimal('-.20')))
  net=self.a.ack_complete_close(88)
  self.assertEqual(net,Decimal('3.20'))
  self.assertEqual(self.r.funded.last_paid_close[1].realized_net_cash,3.2)
 def test_partial_fill_never_acknowledged_full(self):
  self.c.check('order7',approved=True);self.c.send('order7',accepted=True)
  self.c.fill(BrokerDeal('order7','small',1500,Decimal('.005'),4000100))
  with self.assertRaises(ValueError):self.a.ack_full_entry(88)
 def test_duplicate_fill_rejected(self):
  self.fill();self.a.ack_full_entry(88)
  with self.assertRaises(ValueError):self.a.ack_full_entry(88)
 def test_unknown_contract_deny(self):
  self.fill();self.c.verified_symbol=False
  with self.assertRaises(ValueError):self.a.ack_full_entry(88)
 def test_close_partially_open_rejected(self):
  self.fill();self.a.ack_full_entry(88)
  with self.assertRaises(ValueError):self.a.ack_complete_close(88)

if __name__=='__main__':unittest.main()

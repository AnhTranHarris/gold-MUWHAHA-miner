import unittest
from dataclasses import replace
from decimal import Decimal as D
from v1_grid_mt5_position_ledger_0264 import VerifiedMT5PositionLedger0264, OrderRequest, ObservedDeal
from v1_grid_mt5_stop_ack_0264 import BrokerAcknowledgedStops0264,ObservedStopModify
class Stops(unittest.TestCase):
 def setUp(self):
  self.l=VerifiedMT5PositionLedger0264(account_mode='HEDGING',symbol_verified=True)
  self.l.add_request(OrderRequest('o1',1000,1,D('.01'),'g0:p','IN'))
  self.l.acknowledge_check('o1',True);self.l.acknowledge_send('o1',True)
  self.l.stage_history_deal(ObservedDeal('d1','o1',44,1400,'IN',1,D('.01'),4000000,history_verified=True))
  self.stops=BrokerAcknowledgedStops0264(self.l)
 def evidence(self,**kw):
  x=dict(modify_id='m1',position_id=44,request_ms=1600,reply_ms=1700,
    proposed_stop_raw=3997000,reported_position_stop_raw=3997000,
    current_broker_bid_raw=4000000,current_broker_ask_raw=4000200,
    stops_distance_raw=1200,freeze_distance_raw=300,tick_size_raw=50,
    accepted=True,server_quote_verified=True,position_readback_verified=True)
  x.update(kw);return ObservedStopModify(**x)
 def test_success_only_after_broker_ack_and_readback(self):
  self.assertNotIn(44,self.stops.confirmed_stop_raw)
  self.assertEqual(self.stops.on_observed_stop_response(self.evidence()),3997000)
 def test_refused_is_not_changed(self):
  self.stops.on_observed_stop_response(self.evidence(accepted=False,reported_position_stop_raw=None))
  self.assertNotIn(44,self.stops.confirmed_stop_raw)
 def test_rejects_unverified_broker_quote(self):
  with self.assertRaises(ValueError):self.stops.on_observed_stop_response(self.evidence(server_quote_verified=False))
 def test_rejects_unverified_readback(self):
  with self.assertRaises(ValueError):self.stops.on_observed_stop_response(self.evidence(position_readback_verified=False))
 def test_rejects_wrong_ack_sl(self):
  with self.assertRaises(ValueError):self.stops.on_observed_stop_response(self.evidence(reported_position_stop_raw=3998000))
 def test_rejects_min_stop_violation(self):
  with self.assertRaises(ValueError):self.stops.on_observed_stop_response(self.evidence(proposed_stop_raw=3999500,reported_position_stop_raw=3999500))
 def test_rejects_off_tick_grid(self):
  with self.assertRaises(ValueError):self.stops.on_observed_stop_response(self.evidence(proposed_stop_raw=3997021))
 def test_duplicate_confirmation_rejected(self):
  self.stops.on_observed_stop_response(self.evidence())
  with self.assertRaises(ValueError):self.stops.on_observed_stop_response(self.evidence())
 def test_unverified_hedging_denied(self):
  self.l.symbol_verified=False
  with self.assertRaises(ValueError):self.stops.on_observed_stop_response(self.evidence())
 def test_rejected_stop_cannot_silently_change_old_confirmed(self):
  self.stops.on_observed_stop_response(self.evidence())
  with self.assertRaises(ValueError):self.stops.on_observed_stop_response(self.evidence(modify_id='m2',accepted=False,reported_position_stop_raw=3996000))
 def test_sell_protective_sl_checked_ask_not_bid(self):
  L=VerifiedMT5PositionLedger0264(account_mode='HEDGING',symbol_verified=True)
  L.add_request(OrderRequest('so',1000,-1,D('.01'),'g0:s','IN'))
  L.acknowledge_check('so',True);L.acknowledge_send('so',True)
  L.stage_history_deal(ObservedDeal('sd','so',55,1400,'IN',-1,D('.01'),4000000,history_verified=True))
  b=BrokerAcknowledgedStops0264(L)
  x=self.evidence(position_id=55,proposed_stop_raw=4001500,reported_position_stop_raw=4001500)
  self.assertEqual(b.on_observed_stop_response(x),4001500)
if __name__=='__main__':unittest.main()

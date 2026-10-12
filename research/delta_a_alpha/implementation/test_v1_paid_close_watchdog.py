"""Broker DEAL_ADD and verified settlement invariants, no simulated wins."""
import unittest
from v1_paid_close_watchdog import PaidCloseWatchdog

class PaidCloseTests(unittest.TestCase):
    def make(self):
        w=PaidCloseWatchdog();w.register_parent(11,'LONDON',.01,1000);return w
    def open(self,w,ms=1001,deal=101,fee=-.10):
        return w.on_deal_add(deal_id=deal,position_id=11,entry_kind='IN',volume=.01,
                             commission=fee,observed_ms=ms)
    def close(self,w,ms=1002,deal=102,profit=2.,fee=-.10):
        return w.on_deal_add(deal_id=deal,position_id=11,entry_kind='OUT',volume=.01,
                             profit=profit,commission=fee,observed_ms=ms)
    def test_no_permit_without_verified_history(self):
        w=self.make();self.open(w);self.close(w)
        self.assertFalse(w.permit_ready('LONDON',1004))
        self.assertIsNone(w.confirm_settlement(11,observed_ms=1003,
                              verified_broker_history=False,confirmed_net_cash=1.8))
        self.assertFalse(w.permit_ready('LONDON',1004))
    def test_broker_ack_and_paid_close_one_time_later_quote(self):
        w=self.make();self.open(w);self.close(w)
        p=w.confirm_settlement(11,observed_ms=1003,verified_broker_history=True,
                               confirmed_net_cash=1.8)
        self.assertIsNotNone(p)
        self.assertFalse(w.permit_ready('LONDON',1003))
        self.assertFalse(w.permit_ready('NEW_YORK',1004))
        self.assertTrue(w.permit_ready('LONDON',1004))
        self.assertIsNone(w.consume('LONDON',1004,broker_tradable=False))
        self.assertEqual(w.consume('LONDON',1004).position_id,11)
        self.assertIsNone(w.consume('LONDON',1005))
    def test_expiry(self):
        w=PaidCloseWatchdog(permit_ttl_ms=10);w.register_parent(11,'LONDON',.01,1000)
        self.open(w);self.close(w)
        w.confirm_settlement(11,observed_ms=1003,verified_broker_history=True,
                             confirmed_net_cash=1.8)
        self.assertFalse(w.permit_ready('LONDON',1014))
    def test_out_of_order_deal_types_no_future_approval(self):
        w=self.make();self.close(w,ms=1001);self.open(w,ms=1002)
        self.assertFalse(w.permit_ready('LONDON',1003))
        self.assertIsNotNone(w.confirm_settlement(11,observed_ms=1003,
            verified_broker_history=True,confirmed_net_cash=1.8))
    def test_orphan_close_before_parent_intent(self):
        w=PaidCloseWatchdog()
        w.on_deal_add(deal_id=102,position_id=11,entry_kind='OUT',volume=.01,
                      profit=2,commission=-.1,observed_ms=1000)
        w.register_parent(11,'LONDON',.01,1001)
        self.open(w,ms=1002)
        self.assertIsNotNone(w.confirm_settlement(11,observed_ms=1003,
            verified_broker_history=True,confirmed_net_cash=1.8))
    def test_duplicate_deal_id_never_double_counts(self):
        w=self.make();self.open(w)
        self.assertFalse(self.open(w,ms=1002))
        self.assertEqual(w.parents[11].opened,w.expected_lot)
        self.assertEqual(w.duplicates,1)
    def test_partial_close_never_renews(self):
        w=self.make();self.open(w)
        w.on_deal_add(deal_id=102,position_id=11,entry_kind='OUT',volume=.005,
                      profit=1.,observed_ms=1002)
        self.assertIsNone(w.confirm_settlement(11,observed_ms=1003,
            verified_broker_history=True,confirmed_net_cash=.9))
    def test_losing_after_fees_no_permit(self):
        w=self.make();self.open(w);self.close(w,profit=.1)
        self.assertIsNone(w.confirm_settlement(11,observed_ms=1003,
            verified_broker_history=True,confirmed_net_cash=-.1))
        self.assertEqual(w.denied_nonprofit,1)
    def test_unmatched_cash_history_never_renews(self):
        w=self.make();self.open(w);self.close(w)
        self.assertIsNone(w.confirm_settlement(11,observed_ms=1003,
            verified_broker_history=True,confirmed_net_cash=999))
    def test_cancel_removes_permit(self):
        w=self.make();self.open(w);self.close(w)
        w.confirm_settlement(11,observed_ms=1003,verified_broker_history=True,
                             confirmed_net_cash=1.8)
        w.cancel_parent(11)
        self.assertFalse(w.permit_ready('LONDON',1004))
    def test_fixed_lot_policy(self):
        w=PaidCloseWatchdog()
        with self.assertRaises(ValueError):w.register_parent(11,'LONDON',.02,1000)
    def test_out_of_order_observation_refused(self):
        w=self.make()
        with self.assertRaises(ValueError):self.open(w,ms=999)
    def test_duplicate_parent_refused(self):
        w=self.make()
        with self.assertRaises(ValueError):w.register_parent(11,'LONDON',.01,1001)
    def test_overfilled_position_refused(self):
        w=self.make();self.open(w)
        with self.assertRaises(ValueError):w.on_deal_add(
            deal_id=103,position_id=11,entry_kind='IN',volume=.01,observed_ms=1002)

if __name__=='__main__':unittest.main()

"""No market-data downloads; exact ordinal + fill-side lifecycle contracts."""
import unittest
import numpy as np
from micro180_exactms_v12 import trace_one, SHA_2026,EXPECTED_2026,FIELDS

class Micro180ExactMSContracts(unittest.TestCase):
    def _rec(self,**overrides):
        r={'entry_ordinal':1,'entry_time_msc':1000,'side':1,
           'entry_execution_u':10004,'entry_liquidation_u':10000,
           'entry_spread_u':4,'exit_ordinal':3,'exit_time_msc':1000,
           'exit_price_u':9980,'exit_reason':'stop'}
        r.update(overrides)
        return r
    def test_same_millisecond_postentry_quotes_resolve_by_source_ordinal(self):
        ts=np.array([1000,1000,1000,1100,1500],dtype=np.int64)
        bids=np.array([10000,10020,9980,9990,10005],dtype=np.int32)
        asks=bids+4
        p=trace_one(self._rec(),ts,bids,asks)
        self.assertEqual(p['hold_ms'],0)
        self.assertEqual(p['actual_quote_updates'],2)
        self.assertEqual(p['actual_same_ms_updates'],2)
        self.assertEqual(p['actual_first_favorable_10ms'],0)
        self.assertEqual(p['actual_first_favorable_10_ordinal'],2)
        self.assertEqual(p['actual_first_adverse_10ms'],0)
        self.assertEqual(p['actual_first_adverse_10_ordinal'],3)
        self.assertEqual(p['first_drift_pos_25_ms'],None)
        self.assertEqual(p['first_drift_pos_10_ordinal'],2)
        self.assertEqual(p['first_drift_neg_10_ordinal'],3)
    def test_gap_censor_prevents_lookahead_after_unobserved_interval(self):
        ts=np.array([1000,1020,5100,5200,6000],dtype=np.int64)
        bids=np.array([10000,9998,10090,10120,10150],dtype=np.int32)
        p=trace_one(self._rec(exit_ordinal=2,exit_time_msc=1020,exit_price_u=9998),ts,bids,bids+4)
        self.assertEqual(p['forward_censored_gap'],1)
        self.assertIsNone(p['forward_5000ms_liq_mark_u'])
        self.assertIsNone(p['first_drift_pos_50_ordinal'])
        self.assertEqual(p['actual_quote_updates'],1)
    def test_executable_liquidation_is_bid_for_buy_and_ask_for_sell(self):
        ts=np.array([1000,1100],dtype=np.int64)
        bid=np.array([10000,10020],dtype=np.int32)
        ask=np.array([10004,10060],dtype=np.int32)
        p=trace_one(self._rec(exit_ordinal=2,exit_time_msc=1100,exit_price_u=10020),ts,bid,ask)
        self.assertEqual(p['actual_mfe_execution_u'],16)
        rec=self._rec(side=-1,entry_execution_u=10000,
                      entry_liquidation_u=10004,exit_ordinal=2,
                      exit_time_msc=1100,exit_price_u=10060)
        p=trace_one(rec,ts,bid,ask)
        self.assertEqual(p['actual_mae_execution_u'],-60)
    def test_nonexecutable_exit_is_hard_failure(self):
        ts=np.array([1000,1100],dtype=np.int64)
        bid=np.array([10000,10020],dtype=np.int32)
        with self.assertRaises(AssertionError):
            trace_one(self._rec(exit_ordinal=2,exit_time_msc=1100,
                                exit_price_u=10021),ts,bid,bid+4)
    def test_all_month_source_hashes_and_expected_counts_are_frozen(self):
        self.assertEqual(len(SHA_2026),9)
        self.assertEqual(sum(v[0] for v in EXPECTED_2026.values()),72129347)
        self.assertEqual(sum(v[1] for v in EXPECTED_2026.values()),338065)
        self.assertEqual(sum(v[2] for v in EXPECTED_2026.values()),338064)
        self.assertEqual(SHA_2026['03'],
                         '3e9a03d97c6403036c4f5731e2e9eff43b8c4c9b25ac61adc6cc2147e3e79112')
        self.assertEqual(len(FIELDS),len(set(FIELDS)))

if __name__=='__main__':unittest.main()

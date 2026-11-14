"""No-trading lifecycle monitor: source-ordinal and quote-side parity tests."""
from __future__ import annotations
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from trade_lifecycle_shadow import R9LifecycleShadow

class LifecycleShadowTests(unittest.TestCase):
    def test_buy_p5_immutable_marks_and_exit(self):
        p=R9LifecycleShadow(entry_ordinal=50,entry_time_msc=5000,
            side=1,entry_price_cents=460020,cash_per_xau_quote_dollar=1.,
            extra_roundtrip_cash=.20,frozen_entry_p5=.81,
            calibrated_original_exit_cash_win_probability=.22)
        self.assertAlmostEqual(p.observe(51,5200,460000,460020),-.40)
        self.assertAlmostEqual(p.observe(52,5600,460050,460070),.10)
        x=p.close(53,5900,460040)
        self.assertEqual(x["frozen_original_entry_p5"],.81)
        self.assertAlmostEqual(x["original_exit_cash_assumed"],0.)
        self.assertEqual(x["observed_quote_count"],2)
        self.assertFalse(x["original_exit_net_positive"])
        self.assertFalse(p.active)
        with self.assertRaises(ValueError):
            p.observe(54,6000,460050,460070)

    def test_sell_bid_entry_ask_liquidation(self):
        p=R9LifecycleShadow(100,10000,-1,462800,1.0,.20,None,None)
        self.assertAlmostEqual(p.observe(101,10100,462760,462770),.10)
        x=p.close(102,10300,462750)
        self.assertAlmostEqual(x["original_exit_cash_assumed"],.30)
        self.assertIsNone(x["frozen_original_entry_p5"])

    def test_reject_future_score_fabrication_and_out_of_order(self):
        for bad in (-.01,1.01,float("nan")):
            with self.assertRaises(ValueError):
                R9LifecycleShadow(1,10,1,100,1.0,.20,bad,None)
        p=R9LifecycleShadow(100,10000,1,10000,1.0,.20,.5)
        with self.assertRaises(ValueError):
            p.observe(99,10100,9999,10001)
        with self.assertRaises(ValueError):
            p.observe(102,9999,9999,10001)
        with self.assertRaises(ValueError):
            p.observe(101,10100,10002,10000)
        self.assertTrue(p.active)
        with self.assertRaises(ValueError):
            p.close(99,10001,10100)

if __name__ == "__main__":
    unittest.main()

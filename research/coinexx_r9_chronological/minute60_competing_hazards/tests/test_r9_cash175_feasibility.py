"""Synthetic tests ONLY: the original Coinexx raw months are not uploaded here."""
import pathlib
import sys
import unittest

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from r9_cash175_feasibility import evaluate, target_units


class Cash175ResearchAdapterTests(unittest.TestCase):
    def test_target_uses_quote_side_cash_value(self):
        self.assertEqual(target_units(1.75, 0.20, 1.0), 195)
        self.assertEqual(target_units(1.75, 0.20, 2.0), 98)
        with self.assertRaises(ValueError):
            target_units(1.75, 0.20, 0.0)

    def test_buy_target_before_initial_stop(self):
        t=np.array([0,1000,2000,3000],dtype=np.int64)
        bid=np.array([200000,199995,200120,200250],dtype=np.int32)
        ask=bid+20
        v=evaluate(t,bid,ask,np.array([0]),np.array([1]),30,195)
        self.assertEqual(v["target_first_count"],1)
        self.assertEqual(v["stop_first_count"],0)
        self.assertEqual(v["median_target_hit_seconds"],3.0)

    def test_buy_adverse_before_future_target(self):
        t=np.array([0,1000,2000],dtype=np.int64)
        bid=np.array([200000,199960,200250],dtype=np.int32)
        v=evaluate(t,bid,bid+20,np.array([0]),np.array([1]),30,195)
        self.assertEqual(v["stop_first_count"],1)

    def test_same_millisecond_source_order_cannot_be_sorted_away(self):
        t=np.array([0,0,1000],dtype=np.int64)
        bid=np.array([200000,200260,199940],dtype=np.int32)
        v=evaluate(t,bid,bid+20,np.array([0]),np.array([1]),30,195)
        self.assertEqual(v["target_first_count"],1)
        self.assertEqual(v["median_target_hit_seconds"],0.0)

    def test_horizon_no_event(self):
        t=np.array([0,30000],dtype=np.int64)
        bid=np.array([200000,200002],dtype=np.int32)
        v=evaluate(t,bid,bid+20,np.array([0]),np.array([-1]),30,195)
        self.assertEqual(v["no_event_count"],1)

    def test_bad_quote_sequence_fails_closed(self):
        with self.assertRaises(ValueError):
            evaluate(np.array([5,4]),np.array([200000,200001]),
                     np.array([200020,200021]),np.array([0]),
                     np.array([1]),30,195)


if __name__ == "__main__":
    unittest.main()

"""Exact quote sequencing contracts for the independent, on-policy pilot."""
import unittest
import numpy as np
from types import SimpleNamespace
from independent_pilot import quote_exit,Rules

class ClosedLoopPilotTests(unittest.TestCase):
    def test_buy_observed_bid_target_after_entry(self):
        t=SimpleNamespace(ms=np.array([1000,1100,1200],dtype=np.int64),
                          bid=np.array([10000,10040,10225],dtype=np.int32),
                          ask=np.array([10004,10044,10229],dtype=np.int32))
        j,net,reason=quote_exit(t,0,1,Rules('test',target_cash=2.0))
        self.assertEqual((j,reason),(2,'target'))
        self.assertAlmostEqual(net,2.01)

    def test_sell_stop_precedes_favorable_equal_millisecond(self):
        t=SimpleNamespace(ms=np.array([1000,1000,1000],dtype=np.int64),
                          bid=np.array([10000,9890,10100],dtype=np.int32),
                          ask=np.array([10004,10110,10104],dtype=np.int32))
        j,net,reason=quote_exit(t,0,-1,Rules('test',stop_c=100,target_cash=2))
        self.assertEqual((j,reason),(1,'stop'))
        self.assertLess(net,0)

    def test_quote_gap_is_not_claimed_as_a_profitable_target(self):
        t=SimpleNamespace(ms=np.array([1000,5000],dtype=np.int64),
                          bid=np.array([10000,10500],dtype=np.int32),
                          ask=np.array([10004,10504],dtype=np.int32))
        j,net,reason=quote_exit(t,0,1,Rules('test',target_cash=1.))
        self.assertEqual((j,reason),(1,'quote_gap'))

if __name__=='__main__':unittest.main()

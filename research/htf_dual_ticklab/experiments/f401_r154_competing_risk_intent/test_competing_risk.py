"""Deterministic, synthetic contract tests; NOT source-native validation."""
import unittest
from competing_risk import Quote, Intent, fit_hazard_from_matured_training_counts, first_touch_probabilities, side_aware_first_touch, validate_prefix

class Contract(unittest.TestCase):
    def setUp(self):
        self.q = [Quote(100, 2000.0, 2000.2)]
        self.buy = Intent(200, 1)
    def test_prefix_excludes_t0(self):
        with self.assertRaises(ValueError):
            validate_prefix(self.buy, self.q + [Quote(200,2000,2000.2)])
    def test_filled_immutable(self):
        with self.assertRaises(ValueError):
            validate_prefix(Intent(200,1,True),self.q)
    def test_hazard_mass(self):
        p = first_touch_probabilities(fit_hazard_from_matured_training_counts(2,1,100,30))
        self.assertAlmostEqual(sum(p),1)
        self.assertGreater(p[0],p[1])
    def test_buy_exit_bid(self):
        self.assertEqual(side_aware_first_touch(self.buy,self.q,[Quote(210,2001.3,2001.5)],1,1),"favorable")
    def test_sell_exit_ask(self):
        self.assertEqual(side_aware_first_touch(Intent(200,-1),self.q,[Quote(210,1998.5,1998.7)],1,1),"favorable")
    def test_buy_spread_cost(self):
        self.assertEqual(side_aware_first_touch(self.buy,self.q,[Quote(210,1999.0,1999.2)],1,1),"adverse")
    def test_first_touch_not_last(self):
        self.assertEqual(side_aware_first_touch(self.buy,self.q,[Quote(210,2001.3,2001.5),Quote(220,1998,1998.2)],1,1),"favorable")
    def test_no_future_in_policy(self):
        p=first_touch_probabilities(fit_hazard_from_matured_training_counts(2,1,100,30))
        self.assertEqual(p,first_touch_probabilities(fit_hazard_from_matured_training_counts(2,1,100,30)))
if __name__ == "__main__":
    unittest.main()

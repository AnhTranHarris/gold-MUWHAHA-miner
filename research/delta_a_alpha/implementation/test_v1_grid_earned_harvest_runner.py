import unittest
from v1_grid_earned_harvest_runner import AsOfM5EnergyHarvestRunner
class EarnedSourceTest(unittest.TestCase):
 def setUp(self):self.g=AsOfM5EnergyHarvestRunner()
 def call(self,tr,spread=500):return self.g.select(quote_ms=60001,bid_raw=3000000,ask_raw=3000000+spread,completed_m5_tr_raw=tr,asof_ms=59999)
 def test_original_low_energy_30min(self):self.assertEqual(self.call(1000).horizon_ms,30*60000)
 def test_original_high_energy_90min(self):self.assertEqual(self.call(3000).horizon_ms,90*60000)
 def test_exact_threshold(self):self.assertEqual(self.call(2040).horizon_ms,30*60000)
 def test_missing_historical_m5_never_guessed(self):self.assertIsNone(self.g.select(quote_ms=60001,bid_raw=3000000,ask_raw=3000100,completed_m5_tr_raw=None,asof_ms=None))
 def test_future_completed_bar_rejected(self):
  with self.assertRaises(ValueError):self.g.select(quote_ms=60000,bid_raw=3000000,ask_raw=3000100,completed_m5_tr_raw=4000,asof_ms=60000)
 def test_spread_and_cost_as_original(self):self.assertAlmostEqual(self.call(3000).m5_energy,3000/1020)
if __name__=='__main__':unittest.main()

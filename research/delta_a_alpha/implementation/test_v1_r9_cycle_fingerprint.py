import unittest
from v1_r9_cycle_fingerprint import R9CycleFingerprintResearch

class R9CycleFingerprintTests(unittest.TestCase):
 def test_quote_spread_greater_than_r9_stop_is_just_context_not_order(self):
  f=R9CycleFingerprintResearch();s=f.observe(time_ms=0,bid_raw=3100000,ask_raw=3100630)
  self.assertTrue(s.spread_over_nominal_stop)
  self.assertEqual(s.nominal_r9_stop_raw,300)
  self.assertFalse(hasattr(f,'positions'))
 def test_causal_5s_path_and_turns(self):
  f=R9CycleFingerprintResearch();seq=[(0,3100000),(2000,3100100),(4000,3100050),(5000,3100200)]
  for tm,m in seq: s=f.observe(time_ms=tm,bid_raw=m-200,ask_raw=m+200)
  self.assertAlmostEqual(s.preentry_efficiency_5s,200/300)
  self.assertEqual(s.preentry_directional_turns_5s,2)
  self.assertEqual(s.preentry_range_raw_15s,None)
 def test_no_lookahead_before_observed_5s(self):
  f=R9CycleFingerprintResearch()
  s=f.observe(time_ms=4000,bid_raw=3100000,ask_raw=3100100)
  self.assertIsNone(s.preentry_efficiency_5s)
  s=f.observe(time_ms=5000,bid_raw=3099000,ask_raw=3099100)
  self.assertIsNone(s.preentry_efficiency_5s)
 def test_hiatus_resets_replayed_path(self):
  f=R9CycleFingerprintResearch(hiatus_ms=6000)
  for tm in (0,3000,5000):f.observe(time_ms=tm,bid_raw=3100000,ask_raw=3100100)
  x=f.observe(time_ms=80000,bid_raw=3120000,ask_raw=3120100)
  self.assertIsNone(x.preentry_efficiency_5s)
 def test_time_monotonic_fails(self):
  f=R9CycleFingerprintResearch();f.observe(time_ms=5000,bid_raw=1,ask_raw=2)
  with self.assertRaises(ValueError):f.observe(time_ms=4000,bid_raw=1,ask_raw=2)
 def test_same_ms_replay_allowed_without_new_future(self):
  f=R9CycleFingerprintResearch();a=f.observe(time_ms=1000,bid_raw=100,ask_raw=200)
  b=f.observe(time_ms=1000,bid_raw=120,ask_raw=250)
  self.assertEqual((a.available_ms,b.available_ms),(1000,1000))
if __name__=='__main__':unittest.main()

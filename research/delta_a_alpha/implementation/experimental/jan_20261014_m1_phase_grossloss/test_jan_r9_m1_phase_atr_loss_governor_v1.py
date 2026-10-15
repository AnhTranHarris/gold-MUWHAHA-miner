import unittest
from jan_r9_m1_phase_atr_loss_governor_v1 import event_permission, observable_quote_permission,BASE,HIGH
S='COMPLETED_S15_BB_KELTNER_SQUEEZE'
class TestGrossLossShield(unittest.TestCase):
 def test_m1_open_suppressed(self):
  r=event_permission(signal_utc_ms=0,side=1,source=S,completed_m5_atr_usd=10)
  self.assertFalse(r.approved);self.assertIn('PHASE',r.reason)
 def test_completed_atr_state(self):
  low=event_permission(signal_utc_ms=15000,side=1,source=S,completed_m5_atr_usd=7.769)
  high=event_permission(signal_utc_ms=30000,side=-1,source=S,completed_m5_atr_usd=7.77)
  self.assertEqual(low.lifecycle,BASE);self.assertEqual(high.lifecycle,HIGH)
 def test_no_unknown_source(self):
  self.assertFalse(event_permission(signal_utc_ms=15000,side=1,source='OTHER',completed_m5_atr_usd=10).approved)
 def test_no_missing_atr(self):
  self.assertFalse(event_permission(signal_utc_ms=15000,side=1,source=S,completed_m5_atr_usd=float('nan')).approved)
 def test_first_real_delayed_quote(self):
  r=dict(signal_utc_ms=15000,fill_quote_utc_ms=15250,signal_side_quote=4400.1,candidate_side_quote=4400.6,bid=4400.2,ask=4400.6)
  self.assertTrue(observable_quote_permission(**r))
  self.assertFalse(observable_quote_permission(**(r|{'fill_quote_utc_ms':15249})))
  self.assertFalse(observable_quote_permission(**(r|{'ask':4401.2})))
  self.assertFalse(observable_quote_permission(**(r|{'candidate_side_quote':4403.2})))
if __name__=='__main__':unittest.main()

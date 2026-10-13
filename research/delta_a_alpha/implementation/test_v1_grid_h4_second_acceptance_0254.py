import unittest
from v1_grid_h4_second_acceptance_0254 import H4SecondAcceptanceSource,H4AsOfBoundary,H4_MS
M=60000
REF=H4AsOfBoundary(0,1000000,980000,20000,1.1)
class AsOfTests(unittest.TestCase):
 def test_three_completed_prices_second_confirm(self):
  s=H4SecondAcceptanceSource()
  self.assertIsNone(s.on_completed_m1(end_ms=M,close_raw=999000,h4=REF))
  self.assertIsNone(s.on_completed_m1(end_ms=2*M,close_raw=1000500,h4=REF))
  e=s.on_completed_m1(end_ms=3*M,close_raw=1002000,h4=REF)
  self.assertEqual((e.side,e.signal_known_at_ms,e.structural_boundary_raw),(1,3*M,1000000))
 def test_negative_two_minute_confirmation(self):
  s=H4SecondAcceptanceSource()
  for i,px in enumerate((981000,979300,978100),1):
   e=s.on_completed_m1(end_ms=i*M,close_raw=px,h4=REF)
  self.assertEqual(e.side,-1)
 def test_no_second_per_owner(self):
  s=H4SecondAcceptanceSource()
  for i,px in enumerate((999000,1000500,1002000,1004000,1006000),1):
   e=s.on_completed_m1(end_ms=i*M,close_raw=px,h4=REF)
   if i==3:self.assertIsNotNone(e)
   if i>3:self.assertIsNone(e)
 def test_weak_second_acceptance_consumes_owner(self):
  s=H4SecondAcceptanceSource()
  for i,px in enumerate((999000,1000500,1000950,1003000,1005000),1):
   e=s.on_completed_m1(end_ms=i*M,close_raw=px,h4=REF)
   self.assertIsNone(e)
  self.assertEqual(s.n_invites,0)
 def test_halt_no_fake_confirmation(self):
  s=H4SecondAcceptanceSource()
  s.on_completed_m1(end_ms=M,close_raw=999000,h4=REF)
  s.on_completed_m1(end_ms=2*M,close_raw=1000500,h4=REF)
  self.assertIsNone(s.on_completed_m1(end_ms=9*M,close_raw=1002000,h4=REF))
 def test_h4_owner_wrap_no_cross_bar_fake(self):
  s=H4SecondAcceptanceSource()
  s.on_completed_m1(end_ms=H4_MS-M,close_raw=999000,h4=REF)
  s.on_completed_m1(end_ms=H4_MS,close_raw=1000500,h4=REF)
  self.assertIsNone(s.on_completed_m1(end_ms=H4_MS+M,close_raw=1002000,h4=H4AsOfBoundary(H4_MS,1000000,980000,20000,1.1)))
 def test_not_know_current_H4(self):
  s=H4SecondAcceptanceSource()
  with self.assertRaises(ValueError):s.on_completed_m1(end_ms=M,close_raw=1000500,h4=H4AsOfBoundary(50000,1000000,980000,20000,1.1))
 def test_no_broker_and_no_hindsight(self):
  s=H4SecondAcceptanceSource()
  self.assertFalse(any(hasattr(s,x) for x in ('balance','positions','overfit_score','trade','martingale')))
if __name__=='__main__':unittest.main()

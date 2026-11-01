"""Fast deterministic research invariants. No IO to broker or future data."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from four_month_train import Hypo, Quote, DAYS,ROLES,ENTRY_FEE
from nonlinear_student import np_threshold

class FourMonthTests(unittest.TestCase):
 def test_development_calendar_pins(self):
  self.assertEqual(set(DAYS),{'01','02','06','07'})
  self.assertEqual(ROLES,('fit','fit','np_calibration','development_check'))
  self.assertEqual(len({d for days in DAYS.values() for d in days}),16)
 def hypo(self,side,sp=.20):
  q=Quote(1000,100.,100.+sp,1000)
  cand={'source':'coinexx','month':'01','role':'fit','bins':(2,)*11,'features':dict(enumerate([0]*11))}
  return Hypo(q,side,cand,99.70 if side==1 else 100.+sp+.30,q.ask if side==1 else q.bid,1000,0,sp,0,'2026-01-06')
 def test_does_not_exit_on_entry_event(self):
  h=self.hypo(1)
  self.assertIsNone(h.update(Quote(1010,100.,100.2,1010)))
 def test_buy_stop_price_is_bid_and_spread_included(self):
  h=self.hypo(1);r=h.update(Quote(1050,99.69,99.89,1050))
  self.assertEqual(r['exit_type'],'SL');self.assertAlmostEqual(r['net'],99.69-100.2-ENTRY_FEE)
 def test_sell_stop_price_is_ask(self):
  h=self.hypo(-1);r=h.update(Quote(1050,100.31,100.51,1050))
  self.assertEqual(r['exit_type'],'SL');self.assertAlmostEqual(r['net'],100.-100.51-ENTRY_FEE)
 def test_trail_is_monotone_then_stop(self):
  h=self.hypo(1)
  self.assertIsNone(h.update(Quote(1010,100.35,100.55,1010)))
  self.assertGreater(h.sl,99.7)
  sl=h.sl
  self.assertIsNone(h.update(Quote(1020,100.34,100.54,1020)))
  self.assertEqual(h.sl,sl)
  r=h.update(Quote(1030,sl-.01,sl+.19,1030))
  self.assertEqual(r['exit_type'],'SL')
 def test_timeout_only_after_30_seconds(self):
  h=self.hypo(1)
  self.assertIsNone(h.update(Quote(30999,100.10,100.3,30999)))
  r=h.update(Quote(31000,100.10,100.3,31000));self.assertEqual(r['exit_type'],'TIMEOUT')
 def test_np_threshold_no_fake_guarantee(self):
  self.assertIsNone(np_threshold([0]*50,.1))
  x=np_threshold([i/1000 for i in range(2000)],.10)
  self.assertIsNotNone(x)
  self.assertGreater(x,1.7)
if __name__=='__main__':unittest.main()

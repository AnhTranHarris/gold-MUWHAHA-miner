import math
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from entry_model import (Quote, Clock, Hawkes2, CausalEntryFeatures,
                         BNPModel, CLOCK_MS, FEATURES, bins5, binomial_tail)

class TestEntryModel(unittest.TestCase):
    def test_requested_clocks(self):
        self.assertEqual(CLOCK_MS,(250,500,1000,5000,15000,30000,45000))
        self.assertEqual(len(FEATURES),11)
    def test_only_completed_clock_bars(self):
        c=Clock(250)
        c.add(100,100.); c.add(249,101.)
        self.assertEqual(len(c.bars),0)
        c.add(250,102.)
        self.assertEqual(len(c.bars),1)
        self.assertEqual(c.bars[-1][4],101.)
        self.assertEqual(c.bars[-1][5],2)
    def test_gap_reset(self):
        m=CausalEntryFeatures()
        m.add(Quote(0,100,100.1));m.add(Quote(1,101,101.1))
        self.assertGreater(m.hawkes.exc_up,0)
        m.add(Quote(15002,102,102.1))
        self.assertEqual(m.gap_resets,1)
        self.assertEqual(m.hawkes.exc_up,0.)
        self.assertEqual(len(m.clocks[0].bars),0)
    def test_no_future_timestamps(self):
        e=CausalEntryFeatures();e.add(Quote(100,100,100.2))
        with self.assertRaises(ValueError):e.add(Quote(99,100,100.2))
        with self.assertRaises(ValueError):e.add(Quote(101,100.3,100.2))
    def test_hawkes_stable_and_directional(self):
        h=Hawkes2()
        self.assertLess((h.alpha_same+h.alpha_cross)/h.beta,1.)
        h.add(0,100.);h.add(10,100.1)
        self.assertGreater(h.pressure()[0],0)
        h.add(5010,100.1)
        self.assertLess(abs(h.pressure()[0]),1e-5)
    def test_model_fails_closed_until_frozen(self):
        p=BNPModel()
        self.assertEqual(p.decision({'bins':(2,)*11})[0], 'SHADOW_UNTRAINED')
        with self.assertRaises(ValueError):p.score((2,)*11)
        self.assertFalse(p.export()['probability_calibrated'])
    def test_policy_export_requires_validation(self):
        p=BNPModel(min_neg=20,alpha=.2,delta=.05)
        p.fit([((0,)*11,0)]*200+[((4,)*11,1)]*200)
        p.calibrate([-2+i*.01 for i in range(100)])
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d)/'policy.csv'
            with self.assertRaises(ValueError):p.write_mt5_policy(dest)
            p.write_mt5_policy(dest,real_validated=True)
            rows=dest.read_text()
            self.assertIn('real_validated,1',rows)
            self.assertEqual(sum(line.startswith('w') for line in rows.splitlines()),55)
    def test_binomial_tail(self):
        self.assertAlmostEqual(binomial_tail(10,.5,8),56/1024,places=8)
        self.assertEqual(binomial_tail(5,.5,6),0)
    def test_np_frozen_and_strictly_greater_than_ties(self):
        p=BNPModel(min_neg=20,alpha=.2,delta=.05)
        train=[((0,)*len(FEATURES),0)]*200+[((4,)*len(FEATURES),1)]*200
        p.fit(train)
        self.assertTrue(p.calibrate([-2+i*.01 for i in range(80)]))
        self.assertTrue(p.ready)
        s=p.threshold
        p.score=lambda _:s
        self.assertEqual(p.decision({'bins':(0,)*11})[0], 'ABSTAIN_NP')
    def test_np_no_fake_low_sample_guarantees(self):
        p=BNPModel(min_neg=200)
        p.fit([((0,)*11,0)]*30+[((4,)*11,1)]*30)
        self.assertFalse(p.calibrate([0]*100))
        self.assertFalse(p.ready)
    def test_past_feature_immutability(self):
        m=CausalEntryFeatures();total=26*60*4+16
        captured=None
        for i in range(total):
            ms=i*250
            mid=4000+.002*i+.05*math.sin(i*.1)
            q=Quote(ms,mid-.06,mid+.06)
            m.add(q)
            if i==total-16:
                captured=m.candidate(q)
        self.assertIsNotNone(captured)
        oldbins=captured['bins']
        for i in range(total,total+400):
            ms=i*250
            m.add(Quote(ms,3900.,3900.12))
        self.assertEqual(captured['bins'],oldbins)
if __name__=='__main__':unittest.main()
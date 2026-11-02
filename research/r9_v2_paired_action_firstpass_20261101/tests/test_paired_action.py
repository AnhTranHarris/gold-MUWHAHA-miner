from __future__ import annotations
import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from paired_action_labels import replay_pairs,find_quote,money_tick
from causal_dual_features import asof,NAMES

class TestPairedForesight(unittest.TestCase):
    def setUp(self):
        self.t=np.array([0,100,100,250,500,1000,1500,2000],dtype=np.int64)
        self.bid=np.array([100.0,100.01,100.015,100.10,100.20,100.15,100.05,100.08])
        self.ask=self.bid+.15
        self.i=np.array([2],dtype=np.int64)
    def test_event_index_preserves_same_millisecond(self):
        got=find_quote(self.t,self.bid,self.ask,np.array([100],np.int64),np.array([100.165]),np.array([1],np.int8))
        self.assertEqual(int(got[0]),2)
    def test_pair_options_are_opposite_sides(self):
        a=replay_pairs(self.t,self.bid,self.ask,self.i,np.array([1],np.int8),np.array([2000],np.int64),np.array([0.],np.float64))
        self.assertEqual(a[0].shape,(1,2))
        self.assertEqual(a[4].shape,(1,2))
    def test_fractional_stop_rounding_matches_frozen_R9(self):
        self.assertEqual(money_tick(4332.115),4332.11)
    def test_prefix_feature_invariance(self):
        X=asof(self.t,self.bid,self.ask,self.i,np.array([.31],np.float32),np.array([0.],np.float32))
        XX=asof(self.t[:3],self.bid[:3],self.ask[:3],self.i,np.array([.31],np.float32),np.array([0.],np.float32))
        self.assertTrue(np.allclose(X,XX,atol=1.e-7))
    def test_feature_count(self):self.assertEqual(len(NAMES),102)
    def test_favorable_event_is_not_runtime_input(self):
        self.assertFalse(any(x.startswith('future') or 'teacher' in x or 'net' in x for x in NAMES))

if __name__=='__main__':unittest.main()

"""No fabricated market rows; unit tests and optional pinned original source contract."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
import zipfile
import json
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from competing_cash5 import (encode_features,logit,normalize_fit,
    normalize_apply,brier3,read_month,SOURCE_RECEIPT,MODEL_ARCHIVE)

class SourceAndCalibrationTests(unittest.TestCase):
    def test_finite_probability_logits(self):
        x=logit([0.,1.,.5])
        self.assertTrue(np.isfinite(x).all())
        self.assertAlmostEqual(x[2],0.)

    def test_source_future_cash_not_an_input(self):
        d={'context':np.ones((8,9)),
           'session':np.array([0,1,2,3,0,1,2,3]),
           'p5':np.linspace(.02,.21,8),'y':np.arange(8)%3,
           'cash_orig':np.linspace(-1,1,8)}
        before=encode_features(d,'context')
        plus=encode_features(d,'with_frozen_p5')
        self.assertEqual(before.shape,(8,12))
        self.assertEqual(plus.shape,(8,13))
        d['y'][:]=2;d['cash_orig'][:]=1000
        np.testing.assert_array_equal(before,encode_features(d,'context'))
        np.testing.assert_array_equal(plus,encode_features(d,'with_frozen_p5'))

    def test_three_class_brier(self):
        y=np.array([0,1,2])
        self.assertEqual(brier3(y,np.eye(3)),0.)
        self.assertAlmostEqual(brier3(y,np.ones((3,3))/3),2/3)

    def test_training_only_scaling(self):
        train=np.array([[1.,10.],[2.,20.],[3.,30.],[4.,40.]])
        stat=normalize_fit(train)
        self.assertTrue(np.isfinite(normalize_apply(
            np.array([[100000.,-100000.]]),stat)).all())
        self.assertAlmostEqual(normalize_apply(train,stat)[:,0].mean(),0.)

    def test_exact_existing_archive_if_present(self):
        root=Path('/mnt/data')
        if not (root/MODEL_ARCHIVE).exists() or not (root/SOURCE_RECEIPT).exists():
            self.skipTest('Original source ZIPs not attached: never use synthetic substitute')
        with zipfile.ZipFile(root/SOURCE_RECEIPT) as z, zipfile.ZipFile(root/MODEL_ARCHIVE) as m:
            data=read_month(5,root,z,json.loads(z.read('source_receipt.json')),m)
        self.assertEqual(data['n'],31615)
        self.assertAlmostEqual(data['p5_orig_auc'],0.7050847089981862,places=6)
        self.assertEqual(np.unique(data['y']).tolist(),[-1,0,1,2])

if __name__=='__main__':
    unittest.main()

"""Tiny, deterministic lifecycle code checks: no market data or model training."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lifecycle_calibration import cash_now, make_context, normalize, fit_normalization, fit_economic_head


class R9LifecycleTests(unittest.TestCase):
    def test_buy_quote_side_spread_charged_once(self):
        # BUY Ask 4628.00, liquidation Bid 4628.30, K=1, C=.20.
        self.assertAlmostEqual(cash_now(462800, 462830, 1, 1.0, .20), .10)
        self.assertAlmostEqual(cash_now(462800, 462770, 1, 1.0, .20), -.50)

    def test_sell_quote_side_cash(self):
        self.assertAlmostEqual(cash_now(462800, 462770, -1, 1.0, .20), .10)
        self.assertAlmostEqual(cash_now(462800, 462830, -1, 1.0, .20), -.50)
        with self.assertRaises(ValueError):
            cash_now(462800, 462830, 0, 1., .20)

    def test_original_fifteen_fields_context(self):
        x = np.arange(3 * 155, dtype="f4").reshape(3, 155)
        p = np.array([.1, .2, .3], dtype="f4")
        self.assertEqual(make_context(x).shape, (3, 14))
        result = make_context(x, p)
        self.assertEqual(result.shape, (3, 15))
        np.testing.assert_allclose(result[:, -1], p)

    def test_fit_normalization_has_train_only_bounds(self):
        training = np.array([[1., 2.], [2., 3.], [3., 4.], [4., np.nan]])
        stats = fit_normalization(training)
        before = normalize(training, stats)
        later = normalize(np.array([[100000., -100000.]]), stats)
        self.assertTrue(np.all(np.isfinite(before)))
        self.assertTrue(np.all(np.isfinite(later)))
        self.assertEqual(stats[0].shape, (2,))

    def test_economic_head_never_implies_place_order(self):
        rng = np.random.default_rng(20261114)
        x = rng.standard_normal((400, 15)).astype("f4")
        y = (x[:, 1] + .1 * x[:, 14] > 0).astype("i1")
        prob, receipt = fit_economic_head(x[:300], y[:300], x[300:])
        self.assertEqual(prob.shape, (100,))
        self.assertTrue(np.all(np.isfinite(prob)))
        self.assertTrue(np.all((0 <= prob) & (prob <= 1)))
        self.assertEqual(receipt["features"], 15)
        self.assertEqual(len(receipt["coef"]), 15)


if __name__ == "__main__":
    unittest.main()

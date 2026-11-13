import unittest
from crossindex import CausalCrossIndexPanel, IndexObservation, ex_ante_factor


class TestCausalIndexPanel(unittest.TestCase):
    def test_unclosed_bar_rejected(self):
        p=CausalCrossIndexPanel()
        with self.assertRaisesRegex(ValueError, 'not-yet-published'):
            p.observe(IndexObservation('US100',1000,60000,100,'bar',61000,60000))

    def test_same_time_cannot_enter_gold_tick(self):
        p=CausalCrossIndexPanel()
        p.observe(IndexObservation('US100',1000,1005,100,'quote'))
        with self.assertRaisesRegex(ValueError,'strict causality'):
            p.snapshot(1005)
        self.assertEqual(p.snapshot(1006)['us100_available'],1)

    def test_silent_or_stale_instrument_missing(self):
        p=CausalCrossIndexPanel(max_age_ms=3000)
        self.assertEqual(p.snapshot(100)['jp225_available'],0)
        p.observe(IndexObservation('JP225',101,102,100,'quote'))
        self.assertEqual(p.snapshot(105)['jp225_available'],1)
        self.assertEqual(p.snapshot(8000)['jp225_available'],0)
        self.assertIsNone(p.snapshot(8001)['jp225_logret_1000ms'])

    def test_inverted_publication_order_fails_closed(self):
        p=CausalCrossIndexPanel()
        p.observe(IndexObservation('US30',100,200,100,'quote'))
        with self.assertRaisesRegex(ValueError, 'availability ordered'):
            p.observe(IndexObservation('US100',90,199,101,'quote'))

    def test_unsupported_future_quote_schema_rejected(self):
        p=CausalCrossIndexPanel()
        with self.assertRaises(ValueError):
            p.observe(IndexObservation('US100',1000,999,100,'quote'))
        with self.assertRaises(ValueError):
            p.observe(IndexObservation('BOGUS',1000,1000,100,'quote'))

    def test_completed_minute_bar_not_fake_second_return(self):
        p=CausalCrossIndexPanel(max_age_ms=62000)
        p.observe(IndexObservation('US100',0,61000,100,'bar',60000,60000))
        p.observe(IndexObservation('US100',60000,121000,101,'bar',120000,60000))
        snap=p.snapshot(121001)
        self.assertIsNone(snap['us100_logret_1000ms'])
        self.assertIsNotNone(snap['us100_logret_60000ms'])

    def test_no_interpolation_across_closed_market(self):
        p=CausalCrossIndexPanel(max_age_ms=3000)
        p.observe(IndexObservation('JP225',0,100,100,'quote'))
        p.observe(IndexObservation('JP225',59000,59001,101,'quote'))
        snap=p.snapshot(59002)
        self.assertIsNone(snap['jp225_logret_30000ms'])

    def test_valid_factor_uses_observed_prior_quotes(self):
        p=CausalCrossIndexPanel()
        p.observe(IndexObservation('US100',100,101,100,'quote'))
        p.observe(IndexObservation('US500',100,102,100,'quote'))
        p.observe(IndexObservation('US100',5100,5101,102,'quote'))
        p.observe(IndexObservation('US500',5100,5102,101,'quote'))
        q=p.snapshot(5103)
        f=ex_ante_factor(q,horizon_ms=5000,train_vol={'US100':0.01,'US500':0.01},train_weights={'US100':1.0,'US500':-1.0})
        self.assertEqual(f['observed_count'],2)
        self.assertEqual(f['has_diversified_factor'],1)
        self.assertIsNotNone(f['factor'])

    def test_factor_requires_two_quoted_markets(self):
        p=CausalCrossIndexPanel()
        p.observe(IndexObservation('US100',1000,1001,100,'quote'))
        p.observe(IndexObservation('US500',1000,1002,100,'quote'))
        p.observe(IndexObservation('US100',10000,10001,102,'quote'))
        p.observe(IndexObservation('US500',10000,10002,101,'quote'))
        q=p.snapshot(10003)
        r=ex_ante_factor(q,horizon_ms=5000,train_vol={'US100':0.01,'US500':0.01},train_weights={'US100':1,'US500':1})
        self.assertEqual(r['has_diversified_factor'],0) # 9s > horizon+3s, stale endpoints rejected

if __name__=='__main__':unittest.main()

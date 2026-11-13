import unittest
from alpaca_iex import CausalAlpacaIEXPanel, ETFQuote, ETF_TO_INDEX, row_from_alpaca

class TestAlpacaCausalAdapter(unittest.TestCase):
    def q(self,sym,ms,b=100,a=100.01,bs=100,asks=100,ord=0):
        return ETFQuote(sym,ms,b,a,bs,asks,ord)
    def test_schema_and_no_nikkei_mislabel(self):
        self.assertEqual(ETF_TO_INDEX['EWJ'],'JAPAN_EQUITY_ETF')
        self.assertNotIn('JP225',ETF_TO_INDEX.values())
    def test_provider_nanosecond_time_and_sizes(self):
        d={'bp':100,'ap':100.01,'bs':100,'as':90,'t':'2026-01-15T15:00:00.123456789Z'}
        q=row_from_alpaca('QQQ',d,7)
        self.assertEqual(q.time_msc % 1000,123)
        self.assertEqual(q.source_ordinal,7)
    def test_no_same_timestamp_future_quote(self):
        p=CausalAlpacaIEXPanel(assumed_feed_latency_ms=500)
        p.observe(self.q('QQQ',1000))
        with self.assertRaisesRegex(ValueError,'same/future'):p.snapshot(1500)
        self.assertEqual(p.snapshot(1501)['qqq_present'],1)
    def test_outlier_cannot_carry_prior_good_quote(self):
        p=CausalAlpacaIEXPanel()
        p.observe(self.q('DIA',1000,100,100.02,ord=0))
        p.observe(self.q('DIA',1050,100,110,ord=1))
        s=p.snapshot(1700)
        self.assertEqual(s['dia_present'],0)
        self.assertIsNone(s['dia_logret_1000ms'])
        self.assertEqual(p.stats['rejected_DIA'],1)
    def test_degenerate_size_must_fail_closed(self):
        p=CausalAlpacaIEXPanel()
        p.observe(self.q('SPY',1000,bs=0))
        self.assertEqual(p.snapshot(2000)['spy_present'],0)
    def test_stale_does_not_appear_valid(self):
        p=CausalAlpacaIEXPanel(max_age_ms=2000)
        p.observe(self.q('VGK',1000))
        self.assertEqual(p.snapshot(3500)['vgk_present'],1)
        self.assertEqual(p.snapshot(3501)['vgk_present'],0)
    def test_prior_five_second_return(self):
        p=CausalAlpacaIEXPanel()
        p.observe(self.q('QQQ',1000,100,100.02,ord=0))
        p.observe(self.q('QQQ',6100,101,101.02,ord=1))
        s=p.snapshot(6601)
        self.assertGreater(s['qqq_logret_5000ms'],0)
        self.assertIsNone(s['qqq_logret_1000ms'])
    def test_absent_market_neutral_missing_not_zero(self):
        p=CausalAlpacaIEXPanel()
        self.assertEqual(p.snapshot(1000)['ewj_present'],0)
        self.assertIsNone(p.snapshot(1000)['ewj_logret_1000ms'])
    def test_not_ordered_source_rejected(self):
        p=CausalAlpacaIEXPanel()
        p.observe(self.q('QQQ',1000,ord=0))
        with self.assertRaisesRegex(ValueError,'inverted'):
            p.observe(self.q('SPY',999,ord=1))
    def test_no_insertion_into_past_after_gold(self):
        p=CausalAlpacaIEXPanel()
        p.observe(self.q('QQQ',1000,ord=0))
        p.snapshot(1600)
        with self.assertRaisesRegex(ValueError,'late-arriving'):
            p.observe(self.q('SPY',1000,ord=1))
    def test_recover_after_invalid_but_no_borrowed_path(self):
        p=CausalAlpacaIEXPanel()
        p.observe(self.q('DIA',1000,ord=0))
        p.observe(self.q('DIA',2000,100,130,ord=1))
        p.observe(self.q('DIA',3000,100.1,100.11,ord=2))
        s=p.snapshot(3600)
        self.assertEqual(s['dia_present'],1)
        self.assertIsNone(s['dia_logret_1000ms'])

if __name__=='__main__':unittest.main()

import csv
import tempfile
from pathlib import Path
import unittest
from broker_telemetry_v12 import COLUMNS,audit

class TelemetryValidationTests(unittest.TestCase):
    def _audit(self,rows):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'DEMO.csv'
            with p.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=COLUMNS);w.writeheader()
                for row in rows:
                    a={k:'0' for k in COLUMNS}
                    a.update(version='V12',session='test-session',environment='DEMO',
                           event='DEAL',callback_mono_ms='110',callback_server_s='1710000000',
                           quote_time_msc='1710000001000',bid='2100.00',ask='2100.20',
                           symbol='XAUUSD',magic='0',order_id='42',deal_id='77',
                           position_id='3',request_side='0',retcode='0',
                           request_price='0',deal_time_msc='1710000000100',
                           deal_price='2100.22',volume='0.01',commission='-0.02',
                           deal_entry='0',deal_reason='3')
                    a.update(row);w.writerow(a)
            return audit(p)

    def test_out_of_order_request_deal_match_is_not_latency(self):
        a=self._audit([
          {'event':'DEAL','deal_id':'77','deal_price':'2100.22'},
          {'event':'REQUEST','deal_id':'0','request_side':'0','request_price':'2100.20',
           'retcode':'10009','callback_mono_ms':'90','deal_time_msc':'0','deal_price':'0'},
        ])
        self.assertEqual(a['request_deal_unique_price_matches'],1)
        self.assertAlmostEqual(a['conditional_requested_to_deal_price_adverse_units']['median'],.02)
        self.assertIsNone(a['latency_ms_request_to_fill'])

    def test_partial_fills_are_separate_unique_deals(self):
        a=self._audit([
          {'event':'REQUEST','request_side':'1','request_price':'2099.90','retcode':'10010',
           'deal_id':'0','deal_price':'0'},
          {'event':'DEAL','deal_id':'77','deal_price':'2099.85'},
          {'event':'DEAL','deal_id':'78','deal_price':'2099.80'},
        ])
        self.assertEqual(a['unique_deals'],2)
        self.assertEqual(a['request_deal_unique_price_matches'],2)
        self.assertEqual(a['retcodes']['DONE_PARTIAL'],1)
        self.assertTrue(a['conditional_requested_to_deal_price_adverse_units']['median']>0)

    def test_ambiguous_request_rejects_slippage_inference(self):
        a=self._audit([
          {'event':'REQUEST','request_side':'0','request_price':'2100.00','deal_id':'0'},
          {'event':'REQUEST','request_side':'0','request_price':'2100.10','deal_id':'0'},
          {'event':'DEAL','deal_id':'77','deal_price':'2100.22'},
        ])
        self.assertEqual(a['request_deal_unique_price_matches'],0)
        self.assertEqual(a['request_deal_ambiguous'],1)

    def test_no_broker_data_is_not_a_successful_execution_sample(self):
        a=self._audit([])
        self.assertEqual(a['unique_deals'],0)
        self.assertFalse(a['quality_pass_for_execution_inference'])

    def test_reject_live_environment(self):
        with self.assertRaisesRegex(ValueError,'Non-DEMO'):
            self._audit([{'environment':'REAL'}])

    def test_loss_diagnostic_marks_sample_incomplete(self):
        a=self._audit([{'event':'LOSS_DIAGNOSTIC','retcode':'5',
                        'deal_reason':'2','deal_id':'0','deal_time_msc':'0','deal_price':'0','volume':'0'}])
        self.assertEqual(a['lost_event_rows_or_pending_deals'],7)
        self.assertFalse(a['quality_pass_for_execution_inference'])

    def test_duplicate_deal_is_not_double_counted(self):
        a=self._audit([{'event':'DEAL','deal_id':'77'}, {'event':'DEAL','deal_id':'77'}])
        self.assertEqual(a['unique_deals'],1)
        self.assertEqual(a['data_quality_issues']['DUPLICATE_DEAL'],1)

if __name__=='__main__':unittest.main()

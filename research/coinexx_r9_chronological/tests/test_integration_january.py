import os, unittest
from coinexx_r9.ticks import iter_coinexx_ticks

RAW=os.environ.get('COINEXX_JAN_TICKS')

@unittest.skipUnless(RAW and os.path.exists(RAW), 'set COINEXX_JAN_TICKS for raw-file integration')
class JanuaryIntegration(unittest.TestCase):
    def test_first_100k_rows_strict_chronology(self):
        first=None;last=None;n=0
        for t in iter_coinexx_ticks(RAW):
            if first is None:first=t.time_msc
            last=t.time_msc;n+=1
            if n==100000:break
        self.assertEqual(n,100000);self.assertLessEqual(first,last)

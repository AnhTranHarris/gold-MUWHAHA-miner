import unittest,tempfile,gzip
from pathlib import Path
from v1_grid_original_tick_stream_0262 import stream_original_ticks
class OriginalTickStreamChecks(unittest.TestCase):
    def data(self,lines):
        tmp=tempfile.TemporaryDirectory();p=Path(tmp.name)/'XAUUSD_DUKAS_2026_01_ticks.csv.gz'
        with gzip.open(p,'wt') as f:
            f.write('timestamp_ms_utc,ask_raw,bid_raw,ask_volume,bid_volume\n')
            f.write(lines)
        return tmp,p
    def test_original_order_duplicate_milliseconds_preserved(self):
        tmp,p=self.data('1000,100200,100000,1,2\n1000,100300,100100,2,3\n1001,100400,100200,2,3\n')
        try:
            x=list(stream_original_ticks(p,permission=lambda ms,b,a:False))
            self.assertEqual([(q.ordinal,q.quote.utc_ms,q.quote.bid_raw) for q in x],[(0,1000,100000),(1,1000,100100),(2,1001,100200)])
        finally:tmp.cleanup()
    def test_reversed_timestamp_rejected(self):
        tmp,p=self.data('1001,100200,100000,1,2\n1000,100300,100100,2,3\n')
        try:
            with self.assertRaises(ValueError):list(stream_original_ticks(p,permission=lambda ms,b,a:False))
        finally:tmp.cleanup()
    def test_permission_cannot_be_guessed(self):
        tmp,p=self.data('1000,100200,100000,1,2\n')
        try:
            with self.assertRaises(TypeError):list(stream_original_ticks(p,permission=None))
        finally:tmp.cleanup()
    def test_noncanonical_input_rejected(self):
        tmp,p=self.data('1000,100200,100000,1,2\n')
        with gzip.open(p,'wt') as f:f.write('timestamp,ask,bid\n1000,100200,100000\n')
        try:
            with self.assertRaises(ValueError):list(stream_original_ticks(p,permission=lambda ms,b,a:False))
        finally:tmp.cleanup()
    def test_2026_august_seal(self):
        with self.assertRaises(PermissionError):list(stream_original_ticks('XAUUSD_DUKAS_2026_08_ticks.csv.gz',permission=lambda ms,b,a:False))
    def test_no_quote_volume_as_signed_flow(self):
        tmp,p=self.data('1000,100200,100000,0.001,0.002\n')
        try:
            obs=next(stream_original_ticks(p,permission=lambda ms,b,a:False))
            self.assertEqual(obs.ask_volume,.001);self.assertEqual(obs.bid_volume,.002)
            self.assertFalse(hasattr(obs,'executed_buy_volume'))
        finally:tmp.cleanup()
if __name__=='__main__':unittest.main()

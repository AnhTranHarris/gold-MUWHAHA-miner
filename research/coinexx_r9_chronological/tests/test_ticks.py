import csv, gzip, tempfile, unittest
from pathlib import Path
from coinexx_r9.models import parse_price_units
from coinexx_r9.ticks import DataIntegrityError, iter_coinexx_ticks, verify_coinexx_tick_file

class TickTests(unittest.TestCase):
    def _write(self, rows, logger=False):
        td=tempfile.TemporaryDirectory();p=Path(td.name)/'ticks.csv.gz'
        fields=(['run_label','time_msc','time','bid','ask','last','tick_volume','volume_real','flags','event']
                if logger else ['time','time_msc','bid','ask','last','volume','volume_real','flags'])
        with gzip.open(p,'wt',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
        self.addCleanup(td.cleanup);return p
    def test_exact_price_units(self):
        self.assertEqual(parse_price_units('4324.37'),432437)
    def test_nonrepresentable_price_precision_fails_closed(self):
        with self.assertRaises(ValueError):
            parse_price_units('4324.371')
        self.assertEqual(parse_price_units('4324.370'),432437)

    def test_equal_millisecond_rows_preserve_file_order(self):
        rows=[
          {'time':'1000','time_msc':'1000001','bid':'10.00','ask':'10.02','last':'0','volume':'0','volume_real':'0','flags':'134'},
          {'time':'1000','time_msc':'1000001','bid':'10.01','ask':'10.03','last':'0','volume':'0','volume_real':'0','flags':'134'},
        ]
        out=list(iter_coinexx_ticks(self._write(rows)))
        self.assertEqual([x.ordinal for x in out],[1,2]);self.assertEqual([x.bid_u for x in out],[1000,1001])
    def test_backward_time_fails(self):
        rows=[
          {'time':'1000','time_msc':'1000002','bid':'10.00','ask':'10.02','last':'0','volume':'0','volume_real':'0','flags':'134'},
          {'time':'1000','time_msc':'1000001','bid':'10.01','ask':'10.03','last':'0','volume':'0','volume_real':'0','flags':'134'},
        ]
        with self.assertRaises(DataIntegrityError):list(iter_coinexx_ticks(self._write(rows)))

    def test_fast_verifier_preserves_duplicate_count(self):
        rows=[
          {'time':'1000','time_msc':'1000001','bid':'10.00','ask':'10.02','last':'0','volume':'0','volume_real':'0','flags':'134'},
          {'time':'1000','time_msc':'1000001','bid':'10.01','ask':'10.03','last':'0','volume':'0','volume_real':'0','flags':'134'},
          {'time':'1000','time_msc':'1000999','bid':'10.02','ask':'10.04','last':'0','volume':'0','volume_real':'0','flags':'134'},
        ]
        v=verify_coinexx_tick_file(self._write(rows))
        self.assertEqual(v.schema,'broker_export')
        self.assertEqual(v.rows,3)
        self.assertEqual(v.same_millisecond_adjacent_rows,1)
        self.assertEqual(v.first_time_msc,1000001)
        self.assertEqual(v.last_time_msc,1000999)

    def test_ordinal_offset_supports_exact_chunk_continuation(self):
        rows=[{'time':'1000','time_msc':'1000001','bid':'10.00','ask':'10.02','last':'0','volume':'0','volume_real':'0','flags':'134'}]
        out=list(iter_coinexx_ticks(self._write(rows),ordinal_offset=3_000_000))
        self.assertEqual(out[0].ordinal,3_000_001)

    def test_logger_schema_keeps_market_columns_and_optional_telemetry(self):
        rows=[{'run_label':'REAL','time_msc':'1000001','time':'1000','bid':'10.00','ask':'10.02','last':'0','tick_volume':'5','volume_real':'0','flags':'134','event':'NONE'}]
        out=list(iter_coinexx_ticks(self._write(rows,True),preserve_logger_extras=True))
        self.assertEqual(out[0].volume,5);self.assertEqual(out[0].volume_real,'0');self.assertEqual(out[0].source_extras['event'],'NONE')

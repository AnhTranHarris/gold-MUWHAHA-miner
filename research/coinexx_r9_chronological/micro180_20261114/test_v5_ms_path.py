import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not (ROOT/'src').is_dir(): ROOT=ROOT/'r9_runner'
sys.path.insert(0,str(ROOT/'src'))
from coinexx_r9.models import Tick
from v5_ms_path import MsQuarterPath

def quote(ms,bid,ask=None,ordinal=1):
    return Tick(ordinal,ms//1000,ms,bid,bid+10 if ask is None else ask)

class MsPathTests(unittest.TestCase):
    def test_equal_ms_source_events_count_as_different_path_steps(self):
        p=MsQuarterPath()
        p.update(quote(100000,1000,1010,1))
        p.update(quote(100000,1010,1020,2))
        p.update(quote(100000,1005,1015,3))
        p.update(quote(100250,1015,1025,4))
        e=p.signature(100250,1)
        self.assertIsNotNone(e)
        self.assertEqual(p.rows,4)
        self.assertEqual(e.updates,3)
        self.assertGreater(e.coherence,.5)
        self.assertGreater(p.finished[0].path_bid,10)
    def test_no_fabricated_missing_quarter_bins(self):
        p=MsQuarterPath();p.update(quote(100000,1000));p.update(quote(104000,1010))
        self.assertEqual(len(p.finished),1)
        self.assertIsNone(p.signature(104000,1))  # only one active + one stale bin
        self.assertEqual(p.current.observed_deltas,0)
    def test_disordered_timestamp_fails_closed(self):
        p=MsQuarterPath();p.update(quote(5000,1000))
        with self.assertRaises(ValueError):p.update(quote(4999,1001))
    def test_bound_memory(self):
        p=MsQuarterPath()
        for i in range(1300):p.update(quote(i*250,1000+i))
        self.assertLessEqual(len(p.finished),720)
        self.assertEqual(p.current.start_ms,1299*250)
if __name__=='__main__':unittest.main()

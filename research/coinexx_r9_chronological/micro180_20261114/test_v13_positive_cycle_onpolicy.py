"""Fixture tests for a source-only Micro180 V13 on-policy entry controller."""
from __future__ import annotations
import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from v13_positive_cycle_onpolicy_coinexx import CausalTwoHead
MODELS=ROOT/'positive_cycle_model'

def fixture(start_sec=1767315600, count=40, sign=1):
    # Both paths share the first 20 seconds, then diverge; no teacher events.
    for i in range(count):
        price=432500+(min(i,20)*3 if i<20 else (20*3+(i-20)*5*sign))
        ms=(start_sec+i)*1000+100
        yield ms,price,price+19,370.

class V13SourceOnlyContract(unittest.TestCase):
    def test_different_future_cannot_change_previous_quote_entries(self):
        left=CausalTwoHead(MODELS);right=CausalTwoHead(MODELS)
        a=list(fixture(sign=1));b=list(fixture(sign=-1))
        for x,y in zip(a,b):
            if x[0] <= a[19][0]:self.assertEqual(x,y)
            left.on_quote(*x);right.on_quote(*y)
        cut=a[19][0]
        first=[x for x in left.entries if x['time_msc']<=cut]
        other=[x for x in right.entries if x['time_msc']<=cut]
        self.assertEqual(first,other)
    def test_no_second_leg_without_own_first_close(self):
        sim=CausalTwoHead(MODELS,first_threshold=.0,second_threshold=.0)
        for q in fixture(count=90):sim.on_quote(*q)
        for e in sim.entries:
            if e['leg']==2:
                self.assertTrue(any(
                    c['entry_ms']<e['time_msc'] and c['exit_ms']<=e['entry_signal_msc']
                    and c['minute']==e['minute']
                    for c in sim.close_records))
    def test_quote_timestamp_chronology_enforced(self):
        s=CausalTwoHead(MODELS)
        s.on_quote(1000100,10000,10019,300)
        with self.assertRaises(ValueError):s.on_quote(1000000,10001,10020,300)
    def test_no_r9_teacher_row_is_required_at_runtime(self):
        sim=CausalTwoHead(MODELS,first_threshold=.0,second_threshold=.0)
        for q in fixture(count=20):sim.on_quote(*q)
        for e in sim.entries:
            self.assertIn(e['side'],(1,-1))
            self.assertIn(e['leg'],(1,2))
            self.assertEqual(e['time_msc']%1000,100)
            self.assertGreaterEqual(e['signal_to_entry_ms'],1000)
            self.assertLessEqual(e['signal_to_entry_ms'],3000)

if __name__=='__main__':unittest.main(verbosity=2)

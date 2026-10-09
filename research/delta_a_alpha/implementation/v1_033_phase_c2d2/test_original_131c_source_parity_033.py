"""Original 131C frozen JAN032 grid-first-touch source vs ONLINE L1 adapter.

No fabricated source outcomes, no future bars, no synthetic profitable fills.
Does not assert full original V1/Jan/Feb economics; only L1 event genealogy.
"""
import unittest
from pathlib import Path
import numpy as np
from v1_funded_core_033c import Quote
from original_online_sources_033c import Original131CSessionGridL1
from audit_original_131c_full_month_033 import (load_verified_original_build_events,
                                                 SOURCE_SHA256, digest)

SOURCE = Path(__file__).parent / 'verified_original_sources' / 'general_session_state_discovery_131c.py'


class Original131CFirstTouchSourceParity(unittest.TestCase):
    def setUp(self):
        self.assertEqual(digest(SOURCE), SOURCE_SHA256)
        self.ref = load_verified_original_build_events(SOURCE.parent)

    def compare(self, mid, timestamps, step):
        t = np.asarray(timestamps, np.int64)
        m = np.asarray(mid, np.int64)
        reference_indices, directions = self.ref(t, m, step)
        engine = Original131CSessionGridL1(step_raw=step)
        idx, dr = [], []
        for i, (time_ms, p) in enumerate(zip(t, m)):
            # Zero spread is valid here to isolate the literal first-touch formula.
            for x in engine.on_tick(Quote(int(time_ms), int(p), int(p))):
                idx.append(i); dr.append(x.direction)
        self.assertEqual(idx, reference_indices.tolist())
        self.assertEqual(dr, directions.tolist())

    def test_both_directions_touches_and_skipped_rungs(self):
        self.compare([100000,100075,100150,100700,100500,99900,99800,100000],
                     [60000,60100,60200,60300,60400,60500,60600,60700],75)

    def test_minute_reset_and_duplicate_millisecond_ticks(self):
        self.compare([200000,200500,199450,199300,201000,201300,201200,201000],
                     [120000,120000,120010,120500,180000,180020,180020,180050],250)

    def test_real_bidask_mid_rounding(self):
        q = [Quote(120000,200004,200001),Quote(120010,200261,200260),
             Quote(120010,199540,199538),Quote(180000,200000,199997),
             Quote(180005,200800,200799)]
        t=np.asarray([x.time_ms for x in q],np.int64)
        m=np.asarray([(x.ask_raw+x.bid_raw)//2 for x in q],np.int64)
        ei,ed=self.ref(t,m,250)
        o=Original131CSessionGridL1(250)
        got=[(i,y.direction) for i,x in enumerate(q) for y in o.on_tick(x)]
        self.assertEqual(got,list(zip(ei.tolist(),ed.tolist())))

    def test_session_boundary_preserves_l1_ordinal(self):
        self.compare([300000,300260,300790,300310,299700,299100,301000,301300],
                     [23*3600000+59900,23*3600000+59910,
                      24*3600000,24*3600000+100,
                      24*3600000+150,24*3600000+180,
                      24*3600000+190,24*3600000+210],250)

    def test_mirror_checksum_tamper_fails_closed(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as x:
            p=Path(x)/SOURCE.name
            p.write_bytes(SOURCE.read_bytes()+b'\n# unapproved source change\n')
            with self.assertRaises(ValueError):
                load_verified_original_build_events(Path(x))


if __name__=='__main__':unittest.main()
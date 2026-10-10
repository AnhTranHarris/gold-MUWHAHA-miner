"""Test exact preserved JAN038/FEB042 original logic, not a handoff summary."""
import unittest
from pathlib import Path
from source_jan038_feb042_online_033 import OriginalJAN038FEB042Online, TEN_MIN_MS
ORIGINAL = Path(__file__).parent / 'verified_original_sources/JAN038/JAN038_SELECTED_EXACT.json'

class JAN038FEB042SourceContracts(unittest.TestCase):
    def src(self): return OriginalJAN038FEB042Online(ORIGINAL)

    def test_unseen_market_rejected(self):
        with self.assertRaises(ValueError):self.src().context_for(26)

    def test_ordering_rejected(self):
        s=self.src();s.on_quote(600_000,1200,1100)
        with self.assertRaises(ValueError):s.on_quote(599999,1200,1100)

    def test_invalid_executable_quotes_rejected(self):
        s=self.src()
        with self.assertRaises(ValueError):s.on_quote(1234,1000,1200)
        with self.assertRaises(ValueError):s.on_quote(1234,1,0)

    def test_original_searchsorted_left_exact_twenty_second_boundary(self):
        s=self.src();s.on_quote(10000,120000,119000)
        s.on_quote(10001,130000,129000)
        s.on_quote(30000,150000,149000)
        v=s.context_for(27)
        self.assertEqual(v.prior_observation_ms,10000)
        self.assertEqual(v.raw_impulse20_usd,30)
        s.on_quote(30001,151000,150000)
        v=s.context_for(27)
        self.assertEqual(v.prior_observation_ms,10001)
        self.assertEqual(v.raw_impulse20_usd,21)

    def test_multiple_same_tick_proposals_do_not_mutate_quote_history(self):
        s=self.src();s.on_quote(601000,130000,129000)
        a=s.context_for(25);b=s.context_for(26)
        self.assertEqual(a.raw_impulse20_usd,b.raw_impulse20_usd)
        self.assertEqual(a.timestamp_ms,b.timestamp_ms)
        self.assertNotEqual(a.source_id,b.source_id)
        self.assertEqual(s.observed_quotes,1)

    def test_original_source_phase_gate_is_exact(self):
        s=self.src()
        for phase in range(6):
            s.on_quote(phase*TEN_MIN_MS+10,130000,129000)
            for source in (0,3,4,5,6,17,19,21,22,23,24,25,26,27,28):
                self.assertEqual(s.context_for(source).excluded_by_jan038,
                    (source,phase) in s.excluded_pairs)

    def test_month_blind_identical_market_conditions(self):
        snapshots=[]
        for when in (1768000000000, 1770500000000, 1780500000000):
            s=self.src();t=when//3600000*3600000
            s.on_quote(t,2500200,2500000)
            s.on_quote(t+1000,2502200,2502000)
            a=s.context_for(26)
            snapshots.append((a.phase10,a.spread_usd,a.raw_impulse20_usd,a.excluded_by_jan038))
        self.assertEqual(snapshots[0],snapshots[1]);self.assertEqual(snapshots[1],snapshots[2])

if __name__=='__main__':unittest.main()

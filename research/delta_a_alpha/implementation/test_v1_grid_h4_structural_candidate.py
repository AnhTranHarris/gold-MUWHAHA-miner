"""GRID0252 H4 source as-of tests. Does not assert funded profitability."""
import unittest
from v1_grid_h4_structural_candidate import (
    CompletedH4GridSource, CompletedH4StructuralSource, H4_MS,
)
class CompletedH4Tests(unittest.TestCase):
    def context(self,asof=0,hi=4700000,lo=4650000,atr=6000,ratio=1.2):
        return CompletedH4StructuralSource(asof,hi,lo,atr,ratio)
    def test_true_observed_close_breaks_frozen_six_bar_high(self):
        s=CompletedH4GridSource()
        e=s.on_completed_m1(completed_m1_end_ms=60_000,
            prior_m1_close_raw=4699000,latest_m1_close_raw=4700300,
            h4=self.context())
        self.assertEqual((e.side,e.boundary_raw,e.signal_known_at_ms),
                         (1,4700000,60000))
        self.assertEqual(e.source,"GRID0252_CAUSAL_COMPLETED_H4_DONCHIAN6")
    def test_no_multiple_same_h4_owner(self):
        s=CompletedH4GridSource()
        s.on_completed_m1(completed_m1_end_ms=60_000,
            prior_m1_close_raw=4699000,latest_m1_close_raw=4701000,h4=self.context())
        self.assertIsNone(s.on_completed_m1(completed_m1_end_ms=120_000,
            prior_m1_close_raw=4651000,latest_m1_close_raw=4649000,h4=self.context()))
    def test_fails_closed_if_current_incomplete_h4_is_mislabeled(self):
        s=CompletedH4GridSource()
        with self.assertRaises(ValueError):
            s.on_completed_m1(completed_m1_end_ms=60_000,
                prior_m1_close_raw=4699000,latest_m1_close_raw=4701000,
                h4=self.context(asof=30_000))
    def test_completed_prior_h4_available_next_owner(self):
        s=CompletedH4GridSource()
        e=s.on_completed_m1(completed_m1_end_ms=H4_MS+60_000,
            prior_m1_close_raw=4699000,latest_m1_close_raw=4701000,
            h4=self.context(asof=H4_MS))
        self.assertEqual(e.completed_h4_owner,1)
    def test_preentry_no_break_or_excess_energy(self):
        s=CompletedH4GridSource()
        self.assertIsNone(s.on_completed_m1(completed_m1_end_ms=60_000,
            prior_m1_close_raw=4680000,latest_m1_close_raw=4690000,h4=self.context()))
        self.assertIsNone(s.on_completed_m1(completed_m1_end_ms=120_000,
            prior_m1_close_raw=4699000,latest_m1_close_raw=4702000,
            h4=self.context(ratio=2.2)))
    def test_old_minute_cannot_replay(self):
        s=CompletedH4GridSource()
        s.on_completed_m1(completed_m1_end_ms=60_000,
            prior_m1_close_raw=4680000,latest_m1_close_raw=4681000,h4=self.context())
        with self.assertRaises(ValueError):
            s.on_completed_m1(completed_m1_end_ms=60_000,
                prior_m1_close_raw=4699000,latest_m1_close_raw=4702000,h4=self.context())
    def test_no_order_cash_or_oracle_import(self):
        self.assertFalse(any(hasattr(CompletedH4GridSource(),x)
                     for x in ("trade","cash","positions","overfit_score")))
if __name__=="__main__":unittest.main()

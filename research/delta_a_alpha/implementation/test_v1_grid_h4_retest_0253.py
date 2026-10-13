"""Source-only completed H4 causal grid-retest invariants."""
import unittest
from v1_grid_h4_retest_0253 import FinishedH4Rung,CompletedH4RetestGrid,H4_MS,M1_MS
def r(asof=0,hi=1000000,lo=980000,atr=4800,vol=1.1):
    return FinishedH4Rung(asof,hi,lo,atr,vol)
class TestAsOfRetest(unittest.TestCase):
    def test_three_distinct_finished_minute_events(self):
        s=CompletedH4RetestGrid()
        self.assertIsNone(s.on_completed_m1(end_ms=M1_MS,prev_close_raw=999000,close_raw=1001000,h4=r()))
        self.assertEqual(s.state,'BROKEN')
        self.assertIsNone(s.on_completed_m1(end_ms=M1_MS*2,prev_close_raw=1001000,close_raw=998900,h4=r()))
        self.assertEqual(s.state,'PULLED_BACK')
        v=s.on_completed_m1(end_ms=M1_MS*3,prev_close_raw=998900,close_raw=1001100,h4=r())
        self.assertEqual((v.side,v.signal_known_at_ms,v.prior_breakout_level_raw),(1,3*M1_MS,1000000))
    def test_no_signal_without_actual_retest(self):
        s=CompletedH4RetestGrid()
        for k,p,c in ((1,999000,1001000),(2,1001000,1000400),(3,1000400,1002300)):
            self.assertIsNone(s.on_completed_m1(end_ms=k*M1_MS,prev_close_raw=p,close_raw=c,h4=r()))
    def test_prior_completed_h4_required(self):
        s=CompletedH4RetestGrid()
        with self.assertRaises(ValueError):
            s.on_completed_m1(end_ms=60000,prev_close_raw=999000,close_raw=1001000,h4=r(asof=50000))
    def test_single_owner(self):
        s=CompletedH4RetestGrid()
        for i,(p,c) in enumerate(((999000,1001000),(1001000,998900),(998900,1001100)),1):
            v=s.on_completed_m1(end_ms=i*M1_MS,prev_close_raw=p,close_raw=c,h4=r())
        self.assertIsNotNone(v)
        self.assertIsNone(s.on_completed_m1(end_ms=4*M1_MS,prev_close_raw=999000,close_raw=1002000,h4=r()))
        self.assertEqual(s.state,'IDLE')
    def test_quote_gap_resets(self):
        s=CompletedH4RetestGrid()
        s.on_completed_m1(end_ms=M1_MS,prev_close_raw=999000,close_raw=1001000,h4=r())
        self.assertIsNone(s.on_completed_m1(end_ms=H4_MS+M1_MS,prev_close_raw=1001000,close_raw=998900,h4=r(asof=H4_MS)))
        self.assertEqual(s.state,'IDLE')
    def test_expiration(self):
        s=CompletedH4RetestGrid(max_age_minutes=2)
        s.on_completed_m1(end_ms=M1_MS,prev_close_raw=999000,close_raw=1001000,h4=r())
        s.on_completed_m1(end_ms=2*M1_MS,prev_close_raw=1001000,close_raw=998900,h4=r())
        self.assertIsNone(s.on_completed_m1(end_ms=4*M1_MS,prev_close_raw=998900,close_raw=1001300,h4=r()))
    def test_downside(self):
        s=CompletedH4RetestGrid()
        s.on_completed_m1(end_ms=M1_MS,prev_close_raw=981000,close_raw=979000,h4=r())
        s.on_completed_m1(end_ms=2*M1_MS,prev_close_raw=979000,close_raw=982000,h4=r())
        v=s.on_completed_m1(end_ms=3*M1_MS,prev_close_raw=982000,close_raw=978000,h4=r())
        self.assertEqual(v.side,-1)
    def test_no_cash_trade_or_oracle(self):
        s=CompletedH4RetestGrid()
        self.assertFalse(any(hasattr(s,k) for k in ('buy','sell','cash','positions','oracle_score')))
if __name__=='__main__':unittest.main()

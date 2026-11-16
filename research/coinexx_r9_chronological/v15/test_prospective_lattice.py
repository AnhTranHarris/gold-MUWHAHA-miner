"""V15 causality and executable Bid/Ask research contracts, no market downloads."""
from __future__ import annotations
import unittest
from types import SimpleNamespace
import numpy as np
from prospective_lattice_locked import Mechanism,execute,candidate_events

class QuoteOrderTests(unittest.TestCase):
    def test_same_millisecond_adverse_first_stops_before_later_target(self):
        tape=SimpleNamespace(ms=np.array([1000,1000,1000]),
            bid=np.array([10000,9800,10300],dtype=np.int32),
            ask=np.array([10004,9804,10304],dtype=np.int32))
        result=execute(tape,0,1,Mechanism('buy','C',stop_c=150,target_cash=1.5))
        self.assertEqual(result[0],1)
        self.assertEqual(result[2],'STOP')
        self.assertAlmostEqual(result[1],-2.24)

    def test_source_gap_takes_precedence_over_favorable_quote(self):
        tape=SimpleNamespace(ms=np.array([1000,5000]),
            bid=np.array([10000,10300],dtype=np.int32),
            ask=np.array([10004,10304],dtype=np.int32))
        result=execute(tape,0,1,Mechanism('gap','C',target_cash=1.5))
        self.assertEqual(result[2],'GAP')

    def test_short_fills_bid_and_covers_ask(self):
        tape=SimpleNamespace(ms=np.array([1000,1001,1002]),
            bid=np.array([10000,9900,9800],dtype=np.int32),
            ask=np.array([10004,9904,9804],dtype=np.int32))
        res=execute(tape,0,-1,Mechanism('sell','R2',target_cash=1.5))
        self.assertEqual(res[2],'TARGET')
        self.assertEqual(res[0],2)
        self.assertAlmostEqual(res[1],1.76)

    def test_sweep_determines_side_without_ema_or_winner_hindsight(self):
        # Frozen previous support at 10000; a completed 5-second bar sweeps
        # below 10000 and closes above. Sign of EMA is opposed on purpose.
        n=42;starts=np.arange(n)*5;ends=starts+4
        ms=np.repeat(np.arange(n)*5000,5)+np.tile(np.array([0,1200,2400,3600,4800]),n)
        bid=np.full(n*5,10028,dtype=np.int32)
        ask=bid+4
        p=dict(starts=starts,ends=ends,bucket=np.arange(n),
          valid_span=np.ones(n,dtype=bool),
          maxima=np.zeros(n,dtype=np.int64),
          prior_hi=np.full(n,10500.,dtype=float),
          prior_lo=np.full(n,10000.,dtype=float),
          close=np.full(n,10200.,dtype=float),
          low=np.full(n,10100.,dtype=float),
          high=np.full(n,10300.,dtype=float),
          trend=np.full(n-1,-1,dtype=np.int8),
          parent=np.full(n-1,-1,dtype=np.int8),
          available_ms=ms[starts[1:]])
        k=36;p['low'][k]=9970.;p['high'][k]=10100.;p['close'][k]=10030.
        tape=SimpleNamespace(ms=ms,bid=bid,ask=ask,
           mid=(bid+ask)/2.,total_weight=np.arange(n*3,dtype=float),
           total_quote_value=np.cumsum((bid+ask)/2.))
        rule=Mechanism('sweep','R2',require_parent=False)
        fi,side,rail,stops,counters=candidate_events(tape,p,rule)
        self.assertEqual(fi.tolist(),[int(starts[k+1]+1)])
        self.assertEqual(side.tolist(),[1]);self.assertEqual(rail.tolist(),[10000.])
        self.assertEqual(counters['potential'],1)
        # A quote that arrives AFTER the entry has no right to change the
        # earlier bar's signal, even if its price is extreme.
        tape.bid[starts[k+1]+2]=9900
        again=candidate_events(tape,p,rule)[0]
        self.assertEqual(again.tolist(),fi.tolist())

    def test_strong_250ms_confirmation_abstains_on_unobserved_gap(self):
        # A 4s silence cannot be called a confirming 250ms microquote move.
        tape=SimpleNamespace(ms=np.array([1000,5000],dtype=np.int64),
            bid=np.array([10000,10200],dtype=np.int32),
            ask=np.array([10004,10204],dtype=np.int32))
        self.assertEqual(execute(tape,0,1,Mechanism('x','C'))[2],'GAP')

if __name__=='__main__':unittest.main()

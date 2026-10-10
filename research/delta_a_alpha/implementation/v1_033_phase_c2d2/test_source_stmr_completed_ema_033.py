"""Executable original, full-source JAN032 STMR role + session classification parity.

Reference comes via direct Python AST extraction from the unedited exact original
archived code. It does not consult source notes, handoffs, summary claims, or
any original future-outcome ledger.
"""
from __future__ import annotations
import ast
import hashlib
import itertools
import sys
import unittest
from pathlib import Path
import numpy as np
from source_stmr_completed_ema_033 import SourceSTMRCompletedStack, source_sleeve_state, TF_WIDTH_MS

SRC_DIR = Path(__file__).parent / 'verified_original_sources' / 'STMR_JAN032'
SRC_BASE = SRC_DIR / 'stmr_base.py'
SRC_MULTI = SRC_DIR / 'stmr_janjul.py'
SHA_BASE = '5c0a2802d8c883d0612ba7549ac7c146836d93907d6b3182fc7857d2f2bc08f1'
SHA_MULTI = 'f89e85ade7aaeb7ccffec19215795876f5d811af2ba8a7a6c1f646aef030ec08'


def original_source_function(p: Path, name: str):
    """Execute the entire EXACT original function AST, unchanged body."""
    tree = ast.parse(p.read_bytes(), filename=str(p))
    fn = next(x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) and x.name==name)
    fn.decorator_list = []  # original @njit only; test reference is still original BODY
    scope = {'np':np}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),str(p),'exec'),scope)
    return scope[name]


class OriginalSTMRTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref_ema=staticmethod(original_source_function(SRC_MULTI,'bar_states_span'))
        cls.ref_sleeve=staticmethod(original_source_function(SRC_MULTI,'sleeve_state'))

    def test_source_hashes_exact_full_jan032_files(self):
        self.assertEqual(hashlib.sha256(SRC_BASE.read_bytes()).hexdigest(),SHA_BASE)
        self.assertEqual(hashlib.sha256(SRC_MULTI.read_bytes()).hexdigest(),SHA_MULTI)

    def test_all_567_role_session_states_match_original_exact_ast(self):
        observed=set()
        for vals in itertools.product(range(-1,2),repeat=4):
            for sess in range(7):
                want=self.ref_sleeve(sess,*vals)
                got=source_sleeve_state(sess,*vals)
                self.assertEqual(want,got,(sess,vals))
                if want[0]>=0:observed.add(want[0])
        self.assertEqual(observed,set(range(12)))

    def test_every_source_tick_matches_original_completed_ema_all_four_periods(self):
        # ~1,000 ticks including bucket-boundary duplicates, gap and daylight hour.
        t=np.array([0,1,1,500,299999,300000,300000,350000,900000,
              1_200_000,3_600_000,4_100_000,14_400_000,16_000_000,
              28_800_000,43_200_000,48_600_000,50_400_000,70_000_000,
              72_000_000,100_000_000],dtype=np.int64)
        t=np.sort(np.concatenate([t, np.arange(100_000,100_150,dtype=np.int64)*1200]))
        b=(np.arange(t.size,dtype=np.int32)%47)*113+4000000
        roll=SourceSTMRCompletedStack()
        actual=np.empty((4,t.size),dtype=np.int8)
        full=[]
        for i,(time,px) in enumerate(zip(t,b)):
            x=roll.on_quote(int(time),source_bid_raw=int(px))
            actual[:,i]=x.source_states()
            full.append(x.fully_observed)
        for j,w in enumerate(TF_WIDTH_MS):
            want=self.ref_ema(t,b,w,8,21)
            self.assertTrue(np.array_equal(want,actual[j]),(w,np.flatnonzero(want!=actual[j])[:3]))
        self.assertFalse(full[0]); self.assertTrue(full[-1])

    def test_initial_partial_bucket_is_source_state_but_not_physical_ready(self):
        r=SourceSTMRCompletedStack()
        for ts in (1,100_000,300_000,900_000,3_600_000,14_400_000):
            state=r.on_quote(ts,source_bid_raw=4_000_000+ts//10_000)
            self.assertFalse(state.fully_observed)
        # completed H4 starting at true observed second boundary 14.4m,
        # first quote of next H4 boundary itself is not before the quote.
        self.assertFalse(r.on_quote(28_800_000,source_bid_raw=4_001_000).fully_observed)
        self.assertTrue(r.on_quote(28_800_001,source_bid_raw=4_001_100).fully_observed)

    def test_identical_causal_market_inputs_across_different_calendar_months(self):
        patterns=(0,300000,900000,3600000,14400000,28800000,43200000)
        out=[]
        for offset in (0,31*86400000,90*86400000):
            x=SourceSTMRCompletedStack()
            # All shifts are exact multiples of every tf width (H4 too).
            out.append([x.on_quote(offset+t,source_bid_raw=4_000_000+j*100).source_states()
                        for j,t in enumerate(patterns)])
        self.assertEqual(out[0],out[1]);self.assertEqual(out[1],out[2])

    def test_gaps_never_generate_nonexistent_completed_bars(self):
        a=SourceSTMRCompletedStack()
        a.on_quote(0,source_bid_raw=4_000_000)
        a.on_quote(100*14_400_000,source_bid_raw=4_005_000)
        self.assertEqual(a._bars[0].skipped,99)
        self.assertEqual(a._bars[0].ema_fast,4_000_000.0)
        self.assertEqual(a._bars[0].completed_end,14_400_000)

    def test_source_bid_is_not_reinterpreted_as_executable_bid(self):
        # L2 returns structural states and timestamps ONLY, no price/fills.
        x=SourceSTMRCompletedStack().on_quote(0,source_bid_raw=4_000_000)
        self.assertFalse(hasattr(x,'entry_raw'))
        self.assertFalse(hasattr(x,'ask_raw'))

    def test_reverse_quote_chronology_denied(self):
        a=SourceSTMRCompletedStack();a.on_quote(5,source_bid_raw=100)
        with self.assertRaises(ValueError):a.on_quote(4,source_bid_raw=100)

if __name__=='__main__':unittest.main()

"""FEB045 original January-independent 234698 source-proposal quality-mask gate.

No synthetic profitable events; fixture proposals are explicit and cannot be
mistaken for archive FEB045 in-sample PnL. Preserve prior funded V1 L7 code.
"""
from __future__ import annotations
from datetime import datetime,timezone
import unittest
from v1_funded_core_033c import Quote, Structure, Proposal, FundedEngine, Limits
from feb045_source_native_context_033 import (TEN_MIN_MS,CompletedFEB045Features,
    CausalFeatures045,FEB045NativeQualityL3,original_quality_allows)

class FixtureSource:
    def __init__(self, sources=('ORIGINAL_F045_S22',), side=1):
        self.sources=sources
        self.side=side
        self.ordinal=0
        self.closes=[]

    def propose(self,q,s,e):
        self.ordinal+=1
        return tuple(Proposal('L3',src,s.grid_key,self.side,0.0,0.0,600000,
                source_event_key=f'FIXTURE:{src}:{self.ordinal}') for src in self.sources)

    def on_funded_close(self,c,e): self.closes.append(c)


def valid_structure(t:int):
    return Structure('LONDON',1,1,1,1,t-1,'ORIG_F045',completed_bar_end_ms=(t-1,)*4)


class OriginalFebSourceTests(unittest.TestCase):
    def test_last_completed_range_is_not_live_incomplete_bucket(self):
        f=CompletedFEB045Features()
        t0=600000
        f.on_market_quote(Quote(t0+1,100050,100000))
        self.assertIsNone(f.current)
        f.on_market_quote(Quote(t0+599990,128050,128000))
        self.assertIsNone(f.current)
        f.on_market_quote(Quote(t0+600001,130050,130000))
        self.assertIsNone(f.current) # first arbitrary cut bucket excluded
        f.on_market_quote(Quote(t0+600050,149050,149000))
        f.on_market_quote(Quote(t0+1200000,150050,150000))
        self.assertTrue(f.current.valid_for(Quote(t0+1200000,150050,150000)))
        self.assertEqual(f.current.completed_prior_10m_end_ms,t0+1200000)
        self.assertEqual(f.current.prior_10m_range_usd,19.0)
        self.assertEqual(f.current.prior_bucket_observed_quotes,2)
        self.assertGreaterEqual(f.current.directional_impulse_20s_usd,0)

    def test_gap_does_not_fabricate_completed_buckets(self):
        f=CompletedFEB045Features()
        for t in [600005,1200010,2400015]:
            f.on_market_quote(Quote(t,100050,100000))
        self.assertEqual(f.gaps,1)
        self.assertEqual(f.current.completed_prior_10m_end_ms,1800000)

    def test_source_selected_without_calendar_month(self):
        pairs=[(22,3,30,1),(25,5,30,1),(26,3,10,-1),(17,3,12,1),
               (17,3,7,1),(19,3,3,1.5),(24,0,6,1),(27,3,20,1)]
        targets=[True,True,True,True,False,False,True,False]
        for features,accept in zip(pairs,targets):
            self.assertEqual(original_quality_allows(*features),accept,features)

    def test_real_january_february_june_same_causal_state_same_rule(self):
        results=[]
        for month in (1,2,6):
            ms=int(datetime(2026,month,9,10,10,tzinfo=timezone.utc).timestamp()*1000)
            phase=(ms//TEN_MIN_MS)%6
            results.append(original_quality_allows(22,phase,30.0,0.25,cut=9))
        self.assertEqual(results,[True,True,True])

    def test_explicit_first_nine_pockets_preserved_exact(self):
        self.assertTrue(original_quality_allows(25,4,22,0,cut=9))
        self.assertFalse(original_quality_allows(25,4,22,0,cut=10))
        self.assertFalse(original_quality_allows(25,2,9,0,cut=9))
        self.assertTrue(original_quality_allows(25,2,9,0,cut=0))
        self.assertFalse(original_quality_allows(25,3,18,0,cut=9))
        self.assertFalse(original_quality_allows(23,2,18,0,cut=9))

    def test_incomplete_context_fails_closed_not_forwarded(self):
        upstream=FixtureSource()
        gate=FEB045NativeQualityL3(upstream)
        t=1800000
        e=FundedEngine(Limits(max_spread_usd=1,max_orders_per_second=10),[gate],broker_contract_verified=True)
        e.process_quote(Quote(t,100050,100000),valid_structure(t))
        self.assertEqual(len(e.positions),0)
        self.assertEqual(gate.denials.get('MISSING_COMPLETED_CAUSAL_FEB042_CONTEXT'),1)
        self.assertEqual(gate.shadow_candidates,1)
        self.assertEqual(gate.admitted_candidates,0)

    def test_native_source_cap_uses_only_actual_funded_account(self):
        upstream=FixtureSource()
        gate=FEB045NativeQualityL3(upstream,source22_cap=1)
        t0=1800000
        # Inject exactly one authenticated source observation as a deterministic
        # independent fixture (not an upstream original 10m-source claim).
        class Features:
            def __init__(self):self.current=None
            def on_market_quote(self,q,engine):
                self.current=CausalFeatures045(q.time_ms,q.time_ms-600000,30.,0.,20)
        gate.features=Features()
        e=FundedEngine(Limits(max_spread_usd=1,max_orders_per_second=10),[gate],broker_contract_verified=True)
        for t in (t0,t0+100):
            e.process_quote(Quote(t,100050,100000),valid_structure(t))
        self.assertEqual(len(e.positions),1)
        self.assertEqual(gate.shadow_candidates,2)
        self.assertEqual(gate.admitted_candidates,1)
        self.assertEqual(gate.denials.get('ORIGINAL_FEB045_SOURCE_FUNDED_CAP'),1)

    def test_non_target_january_and_watchdog_owner_passthrough(self):
        upstream=FixtureSource(('ORIGINAL_131D_ASIA','ORIGINAL_F045_S22'))
        class F:
            def __init__(self):self.current=None
            def on_market_quote(self,q,e):self.current=None
        gate=FEB045NativeQualityL3(upstream,features=F())
        e=FundedEngine(Limits(),[gate],broker_contract_verified=True)
        t=1800000
        result=list(gate.propose(Quote(t,100050,100000),valid_structure(t),e))
        self.assertEqual([p.source for p in result],['ORIGINAL_131D_ASIA'])

if __name__=='__main__': unittest.main()
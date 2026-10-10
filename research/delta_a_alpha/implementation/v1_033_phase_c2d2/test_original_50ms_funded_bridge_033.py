"""Source-to-physical counterfactual tests; no historical future outcome tape."""
import unittest
from pathlib import Path
from v1_funded_core_033c import Quote,Structure,Limits,FundedEngine,Proposal
from original_50ms_funded_bridge_033 import OriginalJAN037L3QuoteBridge,OriginalSourceFeed033
from source_stmr_completed_ema_033 import SourceSTMRCompletedStack
from feb045_source_native_context_033 import FEB045NativeQualityL3,CausalFeatures045

SOURCE=Path(__file__).parent/'verified_original_sources'/'JAN038'/'JAN038_SELECTED_EXACT.json'


def struct(t,h4=1,h1=1,m15=-1,m5=-1):
    return Structure('LONDON',h4,h1,m15,m5,t-1,'REAL_SOURCE_L3',
        completed_bar_end_ms=(t-1,)*4)

class NativePhysicalBridgeTests(unittest.TestCase):
    def make(self,*,jan038=False,feb=False):
        src=OriginalJAN037L3QuoteBridge(SOURCE,apply_jan038=jan038,
                   label_family='F045' if feb else 'JAN037')
        adapters=[FEB045NativeQualityL3(src) if feb else src]
        e=FundedEngine(Limits(max_orders_per_second=10,max_orders_per_tick=1,
                      max_spread_usd=1,max_per_cell_side=10),adapters,broker_contract_verified=True)
        return src,e

    def test_london_zero_tp_sl_are_disabled_and_true_ttl(self):
        a,e=self.make()
        t=7*3600000
        for i,(delta,price) in enumerate([(0,100000),(1,101000)]):
            q=Quote(t+delta,price+50,price)
            a.observe_raw_bidask(i,q,(1,1,-1,-1))
            e.process_quote(q,struct(q.time_ms))
        self.assertEqual(len(e.positions),1)
        p=next(iter(e.positions.values()))
        self.assertEqual((p.tp_raw,p.sl_raw),(0,0))
        self.assertEqual(p.expiry_ms,t+1+1800000)
        self.assertEqual((a.source_events,a.physical_callbacks),(1,1))
        self.assertAlmostEqual(p.entry_raw/1000,101.05)

    def test_no_funding_without_real_provenance_still_observes_source(self):
        a,e=self.make()
        t=7*3600000
        for i,v in enumerate((100000,101000)):
            q=Quote(t+i,v+50,v)
            a.observe_raw_bidask(i,q,(1,1,-1,-1))
            e.process_quote(q,None)
        self.assertEqual(a.source_events,1)
        self.assertEqual(len(e.positions),0)
        self.assertEqual(e.history_missing,2)

    def test_no_shadow_credit_if_funded_l7_rejects(self):
        a,e=self.make()
        e.broker_contract_verified=False
        t=7*3600000
        for i,v in enumerate((100000,101000)):
            q=Quote(t+i,v+50,v)
            a.observe_raw_bidask(i,q,(1,1,-1,-1))
            e.process_quote(q,struct(q.time_ms))
        self.assertEqual(a.source_events,1)
        self.assertEqual(a.physical_callbacks,0)
        self.assertEqual(e.reject_counts['BROKER_CONTRACT_UNKNOWN'],1)

    def test_original_source_ordinal_cannot_duplicate_from_repeated_propose(self):
        a,e=self.make()
        t=7*3600000
        for i,v in enumerate((100000,101000)):
            q=Quote(t+i,v+50,v);s=struct(q.time_ms)
            a.observe_raw_bidask(i,q,(1,1,-1,-1))
            e.process_quote(q,s)
            self.assertEqual(a.propose(q,s,e),())
        self.assertEqual(len(e.positions),1)
        self.assertEqual(len(e._seen_events),1)

    def test_completed_state_mismatch_fails_closed(self):
        a,e=self.make()
        t=7*3600000
        q=Quote(t,100050,100000)
        a.observe_raw_bidask(0,q,(1,1,-1,-1))
        q=Quote(t+1,101050,101000)
        a.observe_raw_bidask(1,q,(1,1,-1,-1))
        with self.assertRaisesRegex(ValueError,'Source event and L7 structure differ'):
            e.process_quote(q,struct(t+1,1,1,1,1))
        self.assertEqual(len(e.positions),0)

    def test_no_refiring_source_at_same_quote_or_month_time_field(self):
        a,e=self.make()
        t=7*3600000
        a.observe_raw_bidask(0,Quote(t,100050,100000),(1,1,-1,-1))
        a.observe_raw_bidask(1,Quote(t+1,101050,101000),(1,1,-1,-1))
        self.assertEqual(a.manufacturer.events,1)
        self.assertNotIn('month',vars(a))
        with self.assertRaises(ValueError):
            a.observe_raw_bidask(1,Quote(t+1,101050,101000),(1,1,-1,-1))

    def test_original_structural_zero_history_fail_closed(self):
        a,e=self.make()
        feed=OriginalSourceFeed033(a,SourceSTMRCompletedStack())
        t=7*3600000
        s=feed.on_quote(Quote(t,100050,100000))
        self.assertIsNone(s)
        s=feed.on_quote(Quote(t+1,101050,101000))
        self.assertIsNone(s)

    def test_february_quality_is_separate_physical_mask(self):
        a,e=self.make(feb=True)
        t=7*3600000
        for i,v in enumerate((100000,101000)):
            q=Quote(t+i,v+50,v)
            a.observe_raw_bidask(i,q,(1,1,-1,-1))
            e.process_quote(q,struct(q.time_ms))
        self.assertEqual(a.source_events,1)
        self.assertEqual(a.physical_callbacks,0)
        self.assertEqual(len(e.positions),0)
        self.assertGreaterEqual(e.adapters[0].denials.get('MISSING_COMPLETED_CAUSAL_FEB042_CONTEXT',0),1)

    def test_derived_profile_matches_direct_original_source_lifecycle(self):
        a,e=self.make()
        t=16*3600000
        # Original 16: h4=+1 h1=+1 m15=+1 m5=-1; hour16 b10=0 -> NY BUY;
        # close targets TP16[0]=40000 raw, SL16[0]=20000 raw, hold 1200000ms.
        for i,raw in enumerate((100000,101000)):
            q=Quote(t+i,raw+50,raw)
            a.observe_raw_bidask(i,q,(1,1,1,-1))
            e.process_quote(q,struct(q.time_ms,1,1,1,-1))
        self.assertEqual(len(e.positions),1)
        p=next(iter(e.positions.values()))
        self.assertEqual((p.side,p.tp_raw,p.sl_raw,p.expiry_ms-t-1),(1,40000,20000,1200000))

    def test_no_exits_from_original_shadow_results(self):
        a,e=self.make()
        t=7*3600000
        for i,v in enumerate((100000,101000)):
            q=Quote(t+i,v+50,v);a.observe_raw_bidask(i,q,(1,1,-1,-1));e.process_quote(q,struct(q.time_ms))
        q=Quote(t+1800001,101050,101000)
        a.observe_raw_bidask(2,q,(0,0,0,0))
        e.process_quote(q,None)
        self.assertEqual(len(e.closed),1)
        self.assertEqual(e.closed[0].reason,'TIME')
        self.assertEqual(e.closed[0].time_ms,q.time_ms)
        self.assertEqual(len(e.positions),0)

if __name__=='__main__': unittest.main()

class SourcePolicyContractTests(unittest.TestCase):
    def test_source_phase_26_original_jan038_rejection_before_physical(self):
        t=16*3600000+10*60000 # UTC hour16 phase1; source26 phase1 excluded JAN038
        src=OriginalJAN037L3QuoteBridge(SOURCE,apply_jan038=True)
        e=FundedEngine(Limits(max_spread_usd=1,max_orders_per_second=10),[src],broker_contract_verified=True)
        for i,v in enumerate((100000,101000)):
            q=Quote(t+i,v+50,v)
            src.observe_raw_bidask(i,q,(1,1,1,-1))
            e.process_quote(q,struct(q.time_ms,1,1,1,-1))
        self.assertEqual(src.source_events,1)
        self.assertEqual(src.excluded_by_jan038,1)
        self.assertEqual(len(e.positions),0)

    def test_original_jan038_source_deny_not_applied_when_fixed_ab_control_off(self):
        t=16*3600000+10*60000
        src=OriginalJAN037L3QuoteBridge(SOURCE,apply_jan038=False)
        e=FundedEngine(Limits(max_spread_usd=1,max_orders_per_second=10),[src],broker_contract_verified=True)
        for i,v in enumerate((100000,101000)):
            q=Quote(t+i,v+50,v)
            src.observe_raw_bidask(i,q,(1,1,1,-1))
            e.process_quote(q,struct(q.time_ms,1,1,1,-1))
        self.assertEqual(src.excluded_by_jan038,0)
        self.assertEqual(len(e.positions),1)

    def test_both_months_same_observed_state_same_physical_policy(self):
        from datetime import datetime,timezone
        results=[]
        for month in (1,2):
            t=int(datetime(2026,month,13,16,0,0,tzinfo=timezone.utc).timestamp()*1000)
            src=OriginalJAN037L3QuoteBridge(SOURCE,apply_jan038=False)
            e=FundedEngine(Limits(max_spread_usd=1,max_orders_per_second=10),[src],broker_contract_verified=True)
            for i,v in enumerate((100000,101000)):
                q=Quote(t+i,v+50,v)
                src.observe_raw_bidask(i,q,(1,1,1,-1))
                e.process_quote(q,struct(q.time_ms,1,1,1,-1))
            results.append((len(e.positions), next(iter(e.positions.values())).tp_raw,
                           next(iter(e.positions.values())).sl_raw))
        self.assertEqual(results,[(1,40000,20000)]*2)

import unittest
from pathlib import Path
from v1_funded_core_033c import Quote,Structure,FundedEngine,Limits,Proposal
from source_native_s26_s27_033 import S26,S27
from original_50ms_funded_bridge_033 import OriginalJAN037L3QuoteBridge
from original_jan039_source_owner_adapter_033 import OriginalJAN039OwnerIdentity,exact_jan039_l3_chain

P=Path(__file__).parent/'verified_original_sources/JAN038/JAN038_SELECTED_EXACT.json'

def struct(t,h4=1,h1=1,m15=1,m5=-1):
    return Structure('NY',h4,h1,m15,m5,t-1,'ORIGINAL_JAN037_L3_SOURCE_HOUR_16',
      completed_bar_end_ms=(t-1,)*4)

class JAN039Integration(unittest.TestCase):
    def test_source_id26_live_original_event_gets_existing_source_target(self):
        src=OriginalJAN037L3QuoteBridge(P,apply_jan038=False)
        full=exact_jan039_l3_chain(src)
        e=FundedEngine(Limits(max_spread_usd=1,max_orders_per_second=10),[full],broker_contract_verified=True)
        t=16*3600000
        for i,v in enumerate((100000,101000)):
            q=Quote(t+i,v+50,v)
            src.observe_raw_bidask(i,q,(1,1,1,-1))
            e.process_quote(q,struct(q.time_ms))
        self.assertEqual(len(e.positions),1)
        p=next(iter(e.positions.values()))
        self.assertEqual(p.source,S26)
        self.assertEqual(p.tp_raw,35020) # $35 net + $0.02 actual modeled broker fee
        self.assertEqual(p.sl_raw,20000)
        self.assertEqual(p.expiry_ms,t+1+1200000)
        self.assertEqual(full.upstream.remapped,1)
        self.assertEqual(src.physical_callbacks,1)
        self.assertTrue(p.source_event_key.startswith('JAN037_HEARTBEAT:'))

    def test_original_jan038_exclusion_precedes_jan039_name_relay(self):
        src=OriginalJAN037L3QuoteBridge(P,apply_jan038=True)
        chain=exact_jan039_l3_chain(src)
        e=FundedEngine(Limits(max_spread_usd=1,max_orders_per_second=10),[chain],broker_contract_verified=True)
        t=16*3600000+10*60000 # S26 phase1 denied by original JAN038
        for i,v in enumerate((100000,101000)):
            q=Quote(t+i,v+50,v)
            src.observe_raw_bidask(i,q,(1,1,1,-1));e.process_quote(q,struct(q.time_ms))
        self.assertEqual(src.source_events,1)
        self.assertEqual(src.excluded_by_jan038,1)
        self.assertEqual(chain.upstream.remapped,0)
        self.assertEqual(len(e.positions),0)

    def test_month_blind_jan039_s26_owner_changes_no_month_input(self):
        from datetime import datetime,timezone
        results=[]
        for month in (1,2,6):
            t=int(datetime(2026,month,15,16,tzinfo=timezone.utc).timestamp()*1000)
            src=OriginalJAN037L3QuoteBridge(P,apply_jan038=False)
            policy=exact_jan039_l3_chain(src)
            e=FundedEngine(Limits(max_spread_usd=1,max_orders_per_second=10),[policy],broker_contract_verified=True)
            for i,v in enumerate((100000,101000)):
                q=Quote(t+i,v+50,v)
                src.observe_raw_bidask(i,q,(1,1,1,-1));e.process_quote(q,struct(q.time_ms))
            results.append((next(iter(e.positions.values())).source,next(iter(e.positions.values())).tp_raw))
        self.assertEqual(results,[(S26,35020)]*3)

    def test_fixed_physical_source_deny_no_fictional_l7_callbacks(self):
        src=OriginalJAN037L3QuoteBridge(P,apply_jan038=False)
        policy=exact_jan039_l3_chain(src)
        e=FundedEngine(Limits(max_spread_usd=1,max_orders_per_second=10),[policy],broker_contract_verified=False)
        t=16*3600000
        for i,v in enumerate((100000,101000)):
            q=Quote(t+i,v+50,v);src.observe_raw_bidask(i,q,(1,1,1,-1));e.process_quote(q,struct(q.time_ms))
        self.assertEqual(len(e.positions),0)
        self.assertEqual(src.physical_callbacks,0)
        self.assertEqual(policy.upstream.entry_events,[])
        self.assertEqual(e.reject_counts.get('BROKER_CONTRACT_UNKNOWN'),1)

    def test_alias_rejects_other_family_even_matching_source_suffix(self):
        class Fake:
            def propose(self,q,s,e):
                return (Proposal('L3','ORIGINAL_F045_S26','x',1,0,0,60000,
                       source_event_key='original_feb_source_event'),)
            def on_funded_close(self,c,e):pass
        alias=OriginalJAN039OwnerIdentity(Fake())
        q=Quote(100,100050,100000)
        e=FundedEngine(Limits(),[],broker_contract_verified=True)
        z=tuple(alias.propose(q,struct(100),e))
        self.assertEqual(z[0].source,'ORIGINAL_F045_S26')
        self.assertEqual(alias.remapped,0)

if __name__=='__main__':unittest.main()

class S27OriginalPhaseContracts(unittest.TestCase):
    def test_original_short_source27_phase0_net_target_is_frozen(self):
        from source_native_s26_s27_033 import S27
        src=OriginalJAN037L3QuoteBridge(P,apply_jan038=True)
        policy=exact_jan039_l3_chain(src)
        e=FundedEngine(Limits(max_spread_usd=1,max_orders_per_second=10),[policy],broker_contract_verified=True)
        t=17*3600000
        for i,v in enumerate((100000,91000)):
            q=Quote(t+i,v+50,v)
            src.observe_raw_bidask(i,q,(-1,-1,-1,-1))
            e.process_quote(q,struct(q.time_ms,-1,-1,-1,-1))
        self.assertEqual(src.source_events,1)
        self.assertEqual(src.excluded_by_jan038,0)
        self.assertEqual(len(e.positions),1)
        p=next(iter(e.positions.values()))
        self.assertEqual(p.source,S27)
        self.assertEqual((p.side,p.tp_raw,p.sl_raw,p.expiry_ms-t-1),(-1,60020,40000,1800000))
        self.assertEqual(policy._phase_by_funded_id[p.id],0)

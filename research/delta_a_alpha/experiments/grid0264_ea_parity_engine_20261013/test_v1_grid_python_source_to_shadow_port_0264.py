import unittest
from types import SimpleNamespace as NS
from v1_grid_python_source_to_shadow_port_0264 import Grid0264ResearchRuntime, SourceLifecyclePolicy
from v1_grid_funded_quote_gate_0262_hardened import HardenedBrokerPhysics
from v1_grid_cumulative_source_adapter_0264 import CumulativeCreatorAdapter
from v1_grid_strategy_source_router import SourceCandidate

class StaticRouter:
    def __init__(self):self.funded=NS(counts={'ack_fills':0});self.num=0
    def on_tick(self,q,*args,**kw):
        self.num+=1
        if self.num==1:return (SourceCandidate(q.time_ms_utc,1,'PREDECLARED',1,4000000,q.bid_raw,q.ask_raw),)
        return ()
    def stats(self):return {}
    def on_completed_m1(self,**kwargs):pass
    def on_completed_m1_second(self,**kwargs):pass

def physics():return HardenedBrokerPhysics(100,500,0.01,0.01,100,0.20)
def mk(policy=True):
    r=StaticRouter();adapter=CumulativeCreatorAdapter(r)
    return Grid0264ResearchRuntime(physics=physics(),starting_cash_usd=100,
        policies=(SourceLifecyclePolicy('PREDECLARED',600,2000,250,1500),) if policy else
        (SourceLifecyclePolicy('OTHER',600,2000,250,1500),),source_adapter=adapter)
class RuntimeTests(unittest.TestCase):
    def test_no_broker_deal_can_be_claimed_by_shadow(self):
        e=mk();e.on_original_tick(time_ms=1000,bid_raw=4_000_000,ask_raw=4_000_200,h1_completed=None,m5_completed=None,geometry='LONDON',hypothetical_research_tradable=True)
        for t in (1300,1800,2400,3200,4000):
            e.on_original_tick(time_ms=t,bid_raw=4_002_000,ask_raw=4_002_200,h1_completed=None,m5_completed=None,geometry='LONDON',hypothetical_research_tradable=True)
        self.assertEqual(e.summary()['MT5_broker_fills_claimed'],0)
        self.assertEqual(e.sources.router.funded.counts['ack_fills'],0)
        self.assertEqual(e.summary()['shadow']['closed_count'],1)
    def test_tradability_denial_no_fill(self):
        e=mk();e.on_original_tick(time_ms=1000,bid_raw=4_000_000,ask_raw=4_000_200,h1_completed=None,m5_completed=None,geometry='LONDON',hypothetical_research_tradable=False)
        e.on_original_tick(time_ms=1500,bid_raw=4_004_000,ask_raw=4_004_200,h1_completed=None,m5_completed=None,geometry='LONDON',hypothetical_research_tradable=True)
        self.assertEqual(e.summary()['shadow']['closed_count'],0)
    def test_unknown_lifecycle_rejected(self):
        e=mk(False);e.on_original_tick(time_ms=1000,bid_raw=4_000_000,ask_raw=4_000_200,h1_completed=None,m5_completed=None,geometry='LONDON',hypothetical_research_tradable=True)
        self.assertEqual(e.summary()['counters']['unconfigured_quality_or_lifecycle'],1)
    def test_broker_verified_scenario_rejected_for_shadow(self):
        from dataclasses import replace
        with self.assertRaises(ValueError):Grid0264ResearchRuntime(physics=replace(physics(),specs_broker_verified=True),starting_cash_usd=100,policies=(SourceLifecyclePolicy('PREDECLARED',600,2000),))
    def test_explicit_permission_required(self):
        e=mk()
        with self.assertRaises(TypeError):e.on_original_tick(time_ms=1000,bid_raw=4_000_000,ask_raw=4_000_200,h1_completed=None,m5_completed=None,geometry='LONDON',hypothetical_research_tradable=1)
    def test_no_same_tick_entry_even_with_two_quotes(self):
        e=mk();e.on_original_tick(time_ms=1000,bid_raw=4_000_000,ask_raw=4_000_200,h1_completed=None,m5_completed=None,geometry='TOKYO',hypothetical_research_tradable=True)
        e.on_original_tick(time_ms=1000,bid_raw=4_000_050,ask_raw=4_000_250,h1_completed=None,m5_completed=None,geometry='TOKYO',hypothetical_research_tradable=True)
        self.assertEqual(e.summary()['shadow']['open_count'],0)
    def test_mark_reserves_unpaid_roundtrip_fee(self):
        from v1_grid_ea_parity_shadow_risk_0264 import CostReservedObservedFundingEngine0264
        from v1_grid_observed_lifecycle_0262_hardened import HardenedExitPolicy
        from v1_grid_funded_quote_gate_0262_hardened import StrictExecutionQuote
        from v1_grid_funded_quote_gate_0259 import ResearchIntent
        p=HardenedBrokerPhysics(100,500,.01,.01,100,52)
        e=CostReservedObservedFundingEngine0264(starting_cash_usd=300,physics=p,exit_policies=(HardenedExitPolicy('test',999999,999999),))
        e.on_observed_quote(StrictExecutionQuote(1000,4000000,4000200,True))
        e.offer(ResearchIntent('id','test',1000,1,1000,60000,min_latency_ms=250,ttl_ms=2000))
        e.on_observed_quote(StrictExecutionQuote(1300,4000000,4000200,True))
        self.assertEqual(len(e.open),1)
        q=StrictExecutionQuote(1400,4000000,4000200,True)
        self.assertAlmostEqual(e._mark(q),300-.2-.52,places=7)
        self.assertEqual(e.summary()['reserved_expected_exit_fees_for_open_usd'],.52)
    def test_invalid_geometry_rejected(self):
        e=mk()
        with self.assertRaises(ValueError):e.on_original_tick(time_ms=1000,bid_raw=4_000_000,ask_raw=4_000_200,h1_completed=None,m5_completed=None,geometry='',hypothetical_research_tradable=True)
if __name__=='__main__':unittest.main()

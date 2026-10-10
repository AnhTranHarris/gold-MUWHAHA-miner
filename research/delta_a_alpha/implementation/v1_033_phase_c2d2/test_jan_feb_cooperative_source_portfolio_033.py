"""Deterministic cooperative Jan/Feb source-policy and single L7 tests.

Synthetic quote fixtures validate integration mechanics ONLY; not frozen
January/February excellence performance or real-broker certification.
"""
from __future__ import annotations
import unittest
from datetime import datetime, timezone

from v1_funded_core_033c import Quote, Structure, Proposal, Limits, FundedEngine
from source_native_s26_s27_033 import S26
from jan_feb_cooperative_source_portfolio_033 import (
    JanFebCausalPortfolioL3, create_jan_feb_combined_engine
)

class _OriginalFixtureSource:
    def __init__(self, events):
        self.events = events
        self.entrants = []
        self.closes = []
    def propose(self, q, s, e):
        src = self.events.get(q.time_ms)
        if src is None:
            return ()
        return (Proposal("L3", f"ORIGINAL_J037_S{src}", "source-shared-grid",
                         1, 3.0, 100.0, 1_800_000,
                         source_event_key=f"JAN037_HEARTBEAT:{q.time_ms}:{src}"),)
    def on_funded_entry(self, p, q, s, e):
        self.entrants.append((p.id,p.source))
    def on_funded_close(self, c, e):
        self.closes.append(c.position_id)


def _ms(month, hour, minute=0, second=0):
    return int(datetime(2026,month,15,hour,minute,second,tzinfo=timezone.utc).timestamp()*1000)

def _q(t,bid=100000):
    return Quote(t,bid+50,bid)

def _s(t):
    return Structure("NY",1,1,1,-1,t-1,"source-shared-grid",
                     completed_bar_end_ms=(t-1,)*4)

def _process(eng,t,bid=100000):
    eng.process_quote(_q(t,bid),_s(t))

class IntegratedAccountContracts(unittest.TestCase):
    def _engine(self,events,broker=True):
        origin=_OriginalFixtureSource(events)
        owner=JanFebCausalPortfolioL3(origin)
        eng=FundedEngine(Limits(balance_usd=100000, max_orders_per_second=10,
                                max_orders_per_tick=1, max_spread_usd=1.0,
                                max_per_cell_side=32),[owner],
                         broker_contract_verified=broker)
        return origin,owner,eng

    def _warm_completed_10m(self,e,month):
        for h,m in ((14,40),(14,50),(15,0),(15,10)):
            _process(e,_ms(month,h,m))

    def test_jan039_s26_uses_original_frozen_native_tp_in_one_account(self):
        t=_ms(1,16,5)
        origin,owner,e=self._engine({t:26})
        _process(e,t)
        self.assertEqual(len(e.positions),1)
        self.assertEqual(next(iter(e.positions.values())).source,S26)
        self.assertEqual(next(iter(e.positions.values())).tp_raw,35020)
        self.assertEqual(owner.routed_jan,1)
        self.assertEqual(owner.routed_feb,0)
        self.assertEqual(len(origin.entrants),1)

    def test_feb045_causal_quality_uses_identical_upstream_proposal(self):
        t=_ms(2,15,10,1)
        origin,owner,e=self._engine({t:25})
        self._warm_completed_10m(e,2)
        _process(e,t)
        self.assertEqual(len(e.positions),1)
        self.assertEqual(next(iter(e.positions.values())).source,"ORIGINAL_F045_S25")
        self.assertEqual(owner.routed_feb,1)
        self.assertEqual(owner.both_source_policies_eligible,1)
        self.assertEqual(len(origin.entrants),1)

    def test_jan_mechanism_is_not_removed_when_feb_context_unavailable(self):
        t=_ms(1,15,10,1)
        origin,owner,e=self._engine({t:25})
        _process(e,t)
        self.assertEqual(next(iter(e.positions.values())).source,"ORIGINAL_J037_S25")
        self.assertEqual(owner.routed_jan,1)
        self.assertEqual(owner.routed_feb,0)

    def test_broker_fail_closed_preserves_no_shadow_funded_callbacks(self):
        t=_ms(2,16,5)
        origin,owner,e=self._engine({t:26},broker=False)
        _process(e,t)
        self.assertEqual(len(e.positions),0)
        self.assertEqual(len(origin.entrants),0)
        self.assertEqual(owner.funded_entries,0)
        self.assertEqual(e.reject_counts["BROKER_CONTRACT_UNKNOWN"],1)

    def test_january_and_february_both_use_same_condition_without_month_lookup(self):
        outcome=[]
        for month in (1,2,6):
            t=_ms(month,16,5)
            _,owner,e=self._engine({t:26})
            _process(e,t)
            p=next(iter(e.positions.values()))
            outcome.append((p.source,p.tp_raw,owner.routed_jan))
        self.assertEqual(outcome,[(S26,35020,1)]*3)

    def test_combined_jan_and_feb_source_owners_share_one_funded_ledger(self):
        tf=_ms(1,15,10,1)
        tj=_ms(1,16,5)
        origin,owner,e=self._engine({tf:25,tj:26})
        self._warm_completed_10m(e,1)
        _process(e,tf)
        self.assertEqual(next(iter(e.positions.values())).source,"ORIGINAL_F045_S25")
        # Close a timed-out FEB position on a separate observed quote.
        # Combined protective exits share the original one-order-per-quote L7.
        _process(e,tj-1)
        _process(e,tj)
        self.assertEqual(next(iter(e.positions.values())).source,S26)
        _process(e,tj+1_900_000)
        self.assertEqual(owner.funded_entries,2)
        self.assertEqual(owner.funded_closes,2)
        self.assertEqual(len(e.closed),2)
        self.assertEqual(len(origin.entrants),2)
        self.assertEqual(len(origin.closes),2)
        self.assertAlmostEqual(e.score()["net"],sum(c.net_usd for c in e.closed))
        self.assertEqual(owner.routed_feb,1)
        self.assertEqual(owner.routed_jan,1)
        self.assertLessEqual(e.score()["combined_max_orders_sec"],10)

    def test_jan039_source_owned_three_admissions_per_second_preserved(self):
        t=_ms(1,16,5)
        origin,owner,e=self._engine({t+i:26 for i in range(5)})
        for i in range(5):
            _process(e,t+i)
        self.assertEqual(len(e.positions),3)
        self.assertEqual(owner.jan_source_rate_denials,2)
        self.assertEqual(len(origin.entrants),3)
        # Physical L7 is shared and allows up to 10 orders/s for original
        # FEB045, without letting JAN039 exceed its original 3/s owner.
        self.assertEqual(e.limits.max_orders_per_second,10)

    def test_feb_ceiling_is_not_forced_to_jan_global_512(self):
        from pathlib import Path
        rule=Path(__file__).parent/"verified_original_sources/JAN038/JAN038_SELECTED_EXACT.json"
        feed,e,owner=create_jan_feb_combined_engine(rule)
        self.assertEqual(e.limits.max_open,1536)
        self.assertEqual(owner.JAN_MAX_FUNDED_SOURCE_POSITIONS,512)
        self.assertEqual(e.limits.max_orders_per_second,10)

    def test_existing_original_source_feed_can_be_constructed_without_rewrite(self):
        from pathlib import Path
        rule=Path(__file__).parent/"verified_original_sources/JAN038/JAN038_SELECTED_EXACT.json"
        feed,e,owner=create_jan_feb_combined_engine(rule)
        self.assertEqual(feed.bridge,owner.source)
        self.assertEqual(len(e.adapters),1)
        self.assertFalse(e.broker_contract_verified)

if __name__=="__main__":
    unittest.main()

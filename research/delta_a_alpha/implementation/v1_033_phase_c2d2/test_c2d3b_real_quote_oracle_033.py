"""Offline/no-archive deterministic C2D3-B independent book and exit-ablation tests."""
import unittest
from pathlib import Path
from v1_funded_core_033c import Quote,Structure,Limits,FundedEngine,Proposal
from c2d3b_feb_funded_replay_033 import IndependentPhysicalOracle,ExitAblation049


def context(ms):
 return Structure('DIAGNOSTIC',1,1,-1,-1,ms-1,'GRID',0,(ms-100,ms-90,ms-80,ms-70))

class RealQuoteOracleContracts(unittest.TestCase):
 def test_independent_long_delay_real_close_marks_every_quote(self):
  l=Limits(max_orders_per_second=1,max_orders_per_tick=1,max_spread_usd=1)
  e=FundedEngine(l,broker_contract_verified=True);o=IndependentPhysicalOracle(l)
  stream=[(100000000,200100,200000),(100000050,200400,200300),
          (100001000,200450,200350)]
  for i,(t,a,b) in enumerate(stream):
   q=Quote(t,a,b);k=len(e.events)
   ps=[Proposal('L3','TEST','GRID',1,.10,0.,2000,source_event_key='entry')] if i==0 else ()
   e.process_quote(q,context(t),proposals=ps)
   o.ingest(q,e.events[k:],e)
   if i==1:self.assertEqual(len(e.positions),1)
  self.assertEqual(o.close_count,1)
  self.assertEqual(o.mismatch_count,0)
  self.assertEqual(e.combined_order_rate_max,1)
  self.assertAlmostEqual(o.last_post,e.equity)
  self.assertAlmostEqual(o.total_net, .23,places=6)
 def test_independent_short_book_and_fee(self):
  l=Limits(max_orders_per_second=3,max_orders_per_tick=1,max_spread_usd=1)
  e=FundedEngine(l,broker_contract_verified=True);o=IndependentPhysicalOracle(l)
  for i,(t,a,b) in enumerate(((100000000,200100,200000),(100001000,199900,199800))):
   q=Quote(t,a,b);k=len(e.events)
   ps=[Proposal('L3','TEST','GRID',-1,.10,0.,2000,source_event_key='short')] if i==0 else ()
   e.process_quote(q,context(t),proposals=ps);o.ingest(q,e.events[k:],e)
  self.assertEqual(o.mismatch_count,0)
  self.assertEqual(o.close_count,1)
  self.assertAlmostEqual(o.total_net,.08,places=6)
 def test_oracle_detects_corrupted_engine_cash(self):
  l=Limits();e=FundedEngine(l,broker_contract_verified=True);o=IndependentPhysicalOracle(l)
  q=Quote(100000000,200100,200000);k=len(e.events)
  e.process_quote(q,context(q.time_ms));e.balance+=1;e.equity+=1
  o.ingest(q,e.events[k:],e)
  self.assertGreater(o.mismatch_count,0)
 def test_source_exit_ablation_has_identity_when_scales_one(self):
  # An as-of 049 producer must use the same class and source event counters;
  # physical exit variants are attached only to emitted proposals.
  from original_funded_lineage_033c2 import Original049FundedCapacity
  a=ExitAblation049(Original049FundedCapacity(),1.,1.)
  self.assertEqual(a.ttl_scale,1.)
  self.assertEqual(a.tp_scale,1.)
  self.assertEqual(a.total_source_events,0)

if __name__=='__main__':unittest.main()

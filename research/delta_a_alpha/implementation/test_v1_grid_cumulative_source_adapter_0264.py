import unittest
from types import SimpleNamespace as NS
from dataclasses import replace
from v1_grid_cumulative_source_adapter_0264 import CumulativeCreatorAdapter,CompletedM1H4Observations
from v1_grid_strategy_source_router import SourceCandidate

class Router:
 def __init__(self,seq):self.seq=list(seq);self.kw=[];self.m1=[];self.m1second=[]
 def on_tick(self,q,*args,**kw):
  self.kw.append(kw)
  return self.seq.pop(0) if self.seq else ()
 def on_completed_m1(self,**kw):self.m1.append(kw)
 def on_completed_m1_second(self,**kw):self.m1second.append(kw)
 def stats(self):return {'tested':True}

def quote(ms=1,bid=3000000,ask=3000200):return NS(time_ms_utc=ms,bid_raw=bid,ask_raw=ask)
def candidate(ms=1,side=1,available=None):return SourceCandidate(ms,side,'TEST_ORIGINAL_ROUTER',1,3000000,3000000,3000200,available_ms=available)

class ContractTests(unittest.TestCase):
 def test_source_is_never_order(self):
  r=Router([(candidate(),)]);a=CumulativeCreatorAdapter(r)
  y=a.on_tick(quote(),None,'TEST',broker_tradable=True)
  self.assertEqual(y[0].crossing_level_usd,3000)
  self.assertEqual(y[0].side,1)
  self.assertFalse(hasattr(a,'cash'))
 def test_explicit_no_broker_permission(self):
  r=Router([(candidate(),)]);a=CumulativeCreatorAdapter(r)
  self.assertEqual(a.on_tick(quote(),None,'TEST',broker_tradable=False),())
 def test_unsigned_auction_not_guessed(self):
  r=Router([(candidate(side=0),)]);a=CumulativeCreatorAdapter(r)
  self.assertEqual(a.on_tick(quote(),None,'TEST',broker_tradable=True),())
 def test_stale_prior_event_suppressed(self):
  r=Router([(candidate(ms=1,available=4000),)]);a=CumulativeCreatorAdapter(r)
  self.assertEqual(a.on_tick(quote(4000),None,'TEST',broker_tradable=True),())
 def test_delayed_source_not_backdated(self):
  r=Router([(candidate(ms=1000,available=1300),)]);a=CumulativeCreatorAdapter(r)
  self.assertEqual(a.on_tick(quote(1300),None,'TEST',broker_tradable=True)[0].available_ms,1300)
 def test_future_source_rejected(self):
  r=Router([(candidate(ms=2000,available=1000),)]);a=CumulativeCreatorAdapter(r)
  with self.assertRaises(AssertionError):a.on_tick(quote(1000),None,'TEST',broker_tradable=True)
 def test_availability_mismatch_rejected(self):
  r=Router([(candidate(ms=500,available=500),)]);a=CumulativeCreatorAdapter(r)
  with self.assertRaises(AssertionError):a.on_tick(quote(1000),None,'TEST',broker_tradable=True)
 def test_one_source_per_millisecond(self):
  r=Router([(candidate(1),),(candidate(1),)]);a=CumulativeCreatorAdapter(r)
  a.on_tick(quote(1),None,'TEST',broker_tradable=True)
  self.assertEqual(a.on_tick(quote(1),None,'TEST',broker_tradable=True),())
 def test_quote_reverse_rejected(self):
  a=CumulativeCreatorAdapter(Router([]));a.on_tick(quote(2000),None,'TEST')
  with self.assertRaises(ValueError):a.on_tick(quote(1999),None,'TEST')
 def test_h4_requires_fourteen_consecutive_completed(self):
  a=CompletedM1H4Observations()
  for i in range(15):a.observe(quote(i*14_400_000+1))
  self.assertEqual(len(a.h4_completed),14)
  # first minute observed after 14 H4; all past data and no invented bars.
  f=a.observe(quote(14*14_400_000+60_001))
  self.assertIsNotNone(f)
  self.assertLessEqual(f[3].reference_asof_ms,f[0])
 def test_gap_cannot_fake_missing_h4(self):
  a=CompletedM1H4Observations()
  a.observe(quote(1));a.observe(quote(30*14_400_000+1))
  self.assertEqual(len(a.h4_completed),1)
 def test_broker_flag_requires_bool(self):
  with self.assertRaises(TypeError):CumulativeCreatorAdapter(Router([])).on_tick(quote(),None,'TEST',broker_tradable=1)

if __name__=='__main__':unittest.main()

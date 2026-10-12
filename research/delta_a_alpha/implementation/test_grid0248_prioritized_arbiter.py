import unittest
from types import SimpleNamespace
from v1_grid_strategy_source_router import GridStrategySourceRouter

class ExistingBase:
 def __init__(self):
  self.ready=True;self.output=set()
  self.parent=SimpleNamespace(parent=SimpleNamespace(cached_high=3100.,cached_low=3090.,parent_gap_usd=1.2))
 def on_tick(self,q,h1,geometry,*,last_completed_m5=None,broker_tradable=True):
  if q.time_ms_utc in self.output and broker_tradable:
   return (SimpleNamespace(side=1,source='PRESERVED_S1',rung=1,crossing_level_usd=3099.),)
  return ()
 def stats(self):return {}

class Arbiter(unittest.TestCase):
 def setUp(self):
  self.base=ExistingBase();self.r=GridStrategySourceRouter(multiscale=self.base)
  self.h=SimpleNamespace(start_ms=1,end_ms=1)
  self.t=7*3600000
 def q(self,t,p,signs=(1,1,1,1)):
  qq=SimpleNamespace(time_ms_utc=t,bid_raw=p-100,ask_raw=p)
  return self.r.on_tick(qq,self.h,'NO_L1',completed_grid_signs=signs)
 def test_native_delayed_one_timestamp(self):
  self.assertEqual(self.q(self.t,3099500),())
  self.assertEqual(self.q(self.t+1000,3099800),())
  x=self.q(self.t+2000,3099900)
  self.assertEqual(len(x),1)
  self.assertEqual(x[0].time_ms,self.t+1000)
  self.assertEqual(x[0].source,'APRIL136A_CAUSAL_NATIVE_MINUTE_RUNG')
 def test_old_base_from_later_quote_same_millisecond_wins(self):
  self.q(self.t,3099500)
  self.assertEqual(self.q(self.t+1000,3099800),())
  self.base.output.add(self.t+1000)
  got=self.q(self.t+1000,3099800)
  self.assertEqual([e.source for e in got],['PRESERVED_S1'])
  self.assertGreaterEqual(self.r.counts['provisional_suppressed_by_original_grid'],1)
  more=self.q(self.t+2000,3099900)
  self.assertNotIn('APRIL136A_CAUSAL_NATIVE_MINUTE_RUNG',[e.source for e in more])
 def test_release_prior_ms_supplemental_even_if_old_base_arrives_now(self):
  self.q(self.t,3099500)
  self.q(self.t+1000,3099800)
  self.base.output.add(self.t+2000)
  out=self.q(self.t+2000,3099900)
  self.assertEqual([e.source for e in out],
    ['APRIL136A_CAUSAL_NATIVE_MINUTE_RUNG','PRESERVED_S1'])
  self.assertEqual([e.time_ms for e in out],[self.t+1000,self.t+2000])
  self.assertEqual([e.available_ms for e in out],[self.t+2000,self.t+2000])
 def test_supplemental_never_returns_a_fake_paid_child(self):
  self.q(self.t,3099500)
  self.q(self.t+1000,3099800)
  items=self.q(self.t+2000,3099900)
  self.assertTrue(all(x.paid_prior_close_id is None for x in items))
if __name__=='__main__':unittest.main()

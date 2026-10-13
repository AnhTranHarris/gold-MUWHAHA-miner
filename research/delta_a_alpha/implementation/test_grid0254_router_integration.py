"""Research G0 optional H4 second acceptance never displaces original base."""
import unittest
from types import SimpleNamespace
from v1_grid_h4_second_acceptance_0254 import H4AsOfBoundary,H4_MS
from v1_grid_strategy_source_router import GridStrategySourceRouter
from test_v1_grid_strategy_source_router import Base
M=60_000
class TestOptionalSource(unittest.TestCase):
 def setUp(self):
  self.base=Base();self.r=GridStrategySourceRouter(multiscale=self.base)
  self.end=8*H4_MS+3*M
  ctx=H4AsOfBoundary(8*H4_MS,3100000,3090000,20000,1.)
  for off,c in enumerate((3099000,3100500,3102000),1):
   self.inv=self.r.on_completed_m1_second(end_ms=8*H4_MS+off*M,close_raw=c,h4=ctx)
  self.assertIsNotNone(self.inv)
 def tick(self,ms,tradable=True):
  q=SimpleNamespace(time_ms_utc=ms,bid_raw=3100300,ask_raw=3100400)
  return self.r.on_tick(q,SimpleNamespace(start_ms=1,end_ms=1),'G0_TEST',broker_tradable=tradable)
 def test_next_observed_quote_h4_sniper(self):
  x=self.tick(self.end+111)
  self.assertEqual([(a.source,a.side,a.available_ms) for a in x],
    [('GRID0254_H4_TWO_COMPLETED_M1_ACCEPTANCE',1,self.end+111)])
  self.assertIsNone(x[0].paid_prior_close_id)
 def test_creator_priority_then_releases_on_new_millisecond(self):
  ms=self.end+111;self.base.output[ms]=True
  x=self.tick(ms);self.assertEqual([r.source for r in x],['S1_BASE'])
  y=self.tick(ms+3)
  self.assertEqual([r.source for r in y],['GRID0254_H4_TWO_COMPLETED_M1_ACCEPTANCE'])
 def test_never_emit_from_closed_quote_or_stale(self):
  self.assertEqual(self.tick(self.end+500,False),())
  self.assertEqual(self.tick(self.end+1501),())
  self.assertEqual(self.r.counts['h4_second_expired'],1)
 def test_no_cash_positions_overfit(self):
  self.assertFalse(any(hasattr(self.r,k) for k in ('cash','positions','teacher_score')))
if __name__=='__main__':unittest.main()

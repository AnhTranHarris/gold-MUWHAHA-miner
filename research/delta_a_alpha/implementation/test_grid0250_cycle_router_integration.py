"""GRID0250: research-only R9 cycle fingerprint is attached to real G0 events."""
import unittest
from types import SimpleNamespace
from v1_grid_strategy_source_router import GridStrategySourceRouter
from test_v1_grid_strategy_source_router import Base

class R9GridCycleRouterIntegration(unittest.TestCase):
 def test_observed_asof_context_attached_without_future_teacher(self):
  base=Base();base.output[5000]=True
  router=GridStrategySourceRouter(multiscale=base)
  h=SimpleNamespace(start_ms=0,end_ms=0)
  for ms,price in [(0,3099500),(2000,3099600),(4500,3099400)]:
   router.on_tick(SimpleNamespace(time_ms_utc=ms,ask_raw=price,bid_raw=price-400),h,'RESEARCH_ONLY')
  out=router.on_tick(SimpleNamespace(time_ms_utc=5000,ask_raw=3099700,bid_raw=3099300),h,'RESEARCH_ONLY')
  self.assertTrue(out)
  x=next(y for y in out if y.source=='S1_BASE')
  self.assertEqual(x.cycle_fingerprint.available_ms,5000)
  self.assertTrue(x.cycle_fingerprint.spread_over_nominal_stop)
  self.assertFalse(hasattr(x.cycle_fingerprint,'overfit_score'))
  self.assertEqual(router.cycle_research.snapshots,1)
if __name__=='__main__':unittest.main()

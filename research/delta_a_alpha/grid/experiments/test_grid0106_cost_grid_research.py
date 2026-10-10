"""Deterministic causal contract tests, independent of 2026 market outcomes."""
import unittest
import numpy as np
from cost_grid_research import scan_grid,evaluate
class TestPreVerticalCostGrid(unittest.TestCase):
    def mk(self,mids,spreads=None,sec_step=1):
        if spreads is None:spreads=[200]*len(mids)
        t=np.arange(len(mids),dtype='int64')*sec_step*1000+1767308400000
        m=np.array(mids,dtype='int64');s=np.array(spreads,dtype='int32');return t,(m-s//2).astype('int32'),(m+s//2).astype('int32')
    def test_crossing_direction_down_is_reversion_buy(self):
        t,b,a=self.mk([10000,9600,9200,9000]);ix,s,r,g=scan_grid(t,b,a,750,125,0,0,0);self.assertEqual(s.tolist(),[1]);self.assertEqual(ix.tolist(),[2])
    def test_crossing_up_is_reversion_sell(self):
        t,b,a=self.mk([10000,10400,10800,11000]);ix,s,r,g=scan_grid(t,b,a,750,125,0,0,0);self.assertEqual(s.tolist(),[-1]);self.assertEqual(ix.tolist(),[2])
    def test_gap_never_below_125pct_spread(self):
        t,b,a=self.mk([10000,9000,8100,7100,6100],[500,1200,1800,800,1600]);ix,s,r,g=scan_grid(t,b,a,750,125,0,0,0);self.assertTrue(np.all(g*100 >=(a[ix]-b[ix])*125 -100))
    def test_no_events_on_unchanged_quotes(self):
        t,b,a=self.mk([10000]*30);self.assertEqual(len(scan_grid(t,b,a,750,125,0,0,0)[0]),0)
    def test_cooldown_not_ignored(self):
        t,b,a=self.mk([10000,9000,10000,9000,10000,9000],sec_step=1);ix,s,r,g=scan_grid(t,b,a,750,125,3000,0,0);self.assertTrue(np.all(np.diff(t[ix])>=3000))
    def test_bounce_event_occurs_after_crossing(self):
        t,b,a=self.mk([10000,9000,8000,8050,8300,8700]);ix,s,r,g=scan_grid(t,b,a,750,125,0,1,25);self.assertTrue(len(ix)>0);self.assertGreater(ix[0],1);self.assertEqual(int(s[0]),1)
    def test_no_retroactive_bounce(self):
        t,b,a=self.mk([10000,9000,8100,7900,8050,8200,8300]);ix,s,r,g=scan_grid(t,b,a,750,125,0,1,25);self.assertTrue(all(t[i]>=t[4] for i in ix))
    def test_continuation_event_opposite_reversion_side(self):
        t,b,a=self.mk([10000,9000,8700,8500,8200]);ix,s,r,g=scan_grid(t,b,a,750,125,0,2,25);self.assertTrue(len(ix)>0);self.assertEqual(int(s[0]),-1)
    def test_no_source_account_or_session_dependencies(self):
        import inspect,cost_grid_research as x
        source=inspect.getsource(x.scan_grid)
        for text in ['capital','order_send','volume','session','timezone','lot_multiplier','OnTrade']:
            self.assertNotIn(text,source)
    def test_determinism(self):
        t,b,a=self.mk([10000,9000,8000,9000,10000,9500,8700,8000]);r1=scan_grid(t,b,a,750,125,1000,1,25);r2=scan_grid(t,b,a,750,125,1000,1,25)
        for x,y in zip(r1,r2):np.testing.assert_array_equal(x,y)
    def test_no_more_than_one_event_per_tick(self):
        t,b,a=self.mk([10000,7000,4000,10000,2000,15000,3000]);ix,s,r,g=scan_grid(t,b,a,750,125,0,0,0);self.assertEqual(len(ix),len(np.unique(ix)))
if __name__=='__main__':unittest.main(verbosity=2)

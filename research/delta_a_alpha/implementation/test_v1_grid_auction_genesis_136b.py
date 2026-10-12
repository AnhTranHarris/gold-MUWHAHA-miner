"""GRID0247 event-only source regressions. No broker or V1 engine writes."""
import unittest
from v1_grid_auction_genesis_136b import NativeAuctionGrid136B,HOUR_MS,DAY_MS

BASE=1775001600000
def ms(hour,minute=0,day=0):return BASE+day*DAY_MS+hour*HOUR_MS+minute*60000
def q(g,hour,mid,minute=0,day=0,tradable=True):
    return g.on_quote(time_ms=ms(hour,minute,day),
                      bid_raw=mid-50,ask_raw=mid+50,tradable=tradable)

class Test136B(unittest.TestCase):
    def test_highvol_frozen_hour_first_touch(self):
        g=NativeAuctionGrid136B(highvol_gap_raw=1000)
        self.assertEqual(q(g,7,3100000),())
        x=q(g,7,3101000,1)
        self.assertEqual((x[0].family,x[0].cross_sign,x[0].boundary_cell),('HIGHVOL',1,1))
        q(g,7,3100500,2)
        self.assertEqual(q(g,7,3101050,3),())
        self.assertEqual(g.counts['repeat_rejections'],1)
        self.assertEqual(q(g,8,3102000),())
    def test_original_asia_23_to_early_morning_owner(self):
        g=NativeAuctionGrid136B(asia_gap_raw=1000)
        self.assertEqual(q(g,23,3100000,59),())
        x=q(g,0,3102000,day=1)
        self.assertEqual((x[0].family,x[0].cross_sign),('ASIA',1))
        self.assertEqual(x[0].owner_id,ms(23)//DAY_MS)
        self.assertEqual(q(g,7,3103000,day=1),())
    def test_downward_boundary_is_previous_cell(self):
        g=NativeAuctionGrid136B();q(g,7,3100000)
        x=q(g,7,3098800,1)
        self.assertEqual((x[0].boundary_cell,x[0].cross_sign),(0,-1))
    def test_quote_hiatus_cannot_manufacture_cross(self):
        g=NativeAuctionGrid136B(max_quote_gap_ms=60000)
        q(g,7,3100000)
        self.assertEqual(q(g,7,3105000,5),())
        self.assertEqual(g.counts['hiatus_resets'],1)
    def test_new_owner_no_stale_day_anchor(self):
        g=NativeAuctionGrid136B()
        q(g,7,3100000,day=0)
        self.assertEqual(q(g,7,3101100,day=1),())
    def test_nontradable_resets_continuity(self):
        g=NativeAuctionGrid136B()
        q(g,7,3100000)
        q(g,7,3100500,1,tradable=False)
        self.assertEqual(q(g,7,3102000,2),())
    def test_backward_quotes_rejected(self):
        g=NativeAuctionGrid136B();q(g,7,3100000,1)
        with self.assertRaises(ValueError):q(g,7,3100000)
    def test_no_funded_trade_impersonation(self):
        g=NativeAuctionGrid136B()
        self.assertFalse(any(hasattr(g,x) for x in ('cash','positions','lot','martingale')))
if __name__=='__main__':unittest.main()

import sys, tempfile,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).parent))
from research import Tape,Config,candidate_trajectory,exit_trajectory
class ChronologicalLatticeTests(unittest.TestCase):
    def tape(self,quotes):
        t=tempfile.TemporaryDirectory();p=Path(t.name)/'synthetic.csv'
        pd.DataFrame(quotes,columns=['time_msc','bid','ask']).to_csv(p,index=False)
        return t,Tape(p)
    def test_same_ms_rebound_requires_250ms_and_subsequent_ordinal(self):
        t,x=self.tape([(1000,100.00,100.04),(1001,99.80,99.84),(1001,99.81,99.85),(1100,99.86,99.90),(1252,100.00,100.04)])
        try:
            cfg=Config('test',expiry_ms=1000,rebound_c=10,max_zone_width_c=30)
            idx,status=candidate_trajectory(x,0,1,{'rail':9985},cfg)
            self.assertEqual(idx,4)
            self.assertEqual(status,'confirmed_market')
        finally:t.cleanup()
    def test_exit_buy_uses_bid_not_ask(self):
        t,x=self.tape([(1000,100.00,100.20),(1100,99.70,100.00)])
        try:
            idx,net,status=exit_trajectory(x,0,1,Config('t'))
            self.assertEqual((idx,status),(1,'stop'))
            self.assertAlmostEqual(net,-.70)
        finally:t.cleanup()
    def test_exit_sell_uses_ask_not_bid(self):
        t,x=self.tape([(1000,100.00,100.20),(1100,100.20,100.50)])
        try:
            idx,net,status=exit_trajectory(x,0,-1,Config('t'))
            self.assertEqual((idx,status),(1,'stop'))
            self.assertAlmostEqual(net,-.70)
        finally:t.cleanup()
    def test_original_timestamp_order_is_not_sorted(self):
        with self.assertRaises(AssertionError):
            t,x=self.tape([(1001,100.00,100.20),(1000,100.10,100.30)])
            t.cleanup()
    def test_twap_at_signal_does_not_see_later_quote(self):
        a=[(1000+1000*i,100+i*.001,100.2+i*.001) for i in range(402)]
        t,x=self.tape(a)
        try:
            self.assertTrue(np.isfinite(x.twap[-1]))
            value=x.twap[-1]
        finally:t.cleanup()
        t,y=self.tape(a+[(500000,1000,1000.2)])
        try:self.assertEqual(value,y.twap[len(a)-1])
        finally:t.cleanup()
if __name__=='__main__':unittest.main()

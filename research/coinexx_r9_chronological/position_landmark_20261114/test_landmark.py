"""Small deterministic causal-landmark and account-cash validation fixtures."""
import sys
from pathlib import Path
import unittest
import numpy as np
import pandas as pd

sys.path.insert(0,str(Path(__file__).parent))
from continuation_landmarks import calculate_snapshot, month_rows, FEATURE_COLS
from train_continuation_value import cvar_by_predicted_bucket, fit_predict


class LandmarkTests(unittest.TestCase):
    def test_buy_quote_marking_stop_and_closed_path_no_future(self):
        ms=np.array([100,500,900,1100,1500,2000,3100,3300],dtype='int64')
        bid=np.array([1000,1002,1009,1014,1008,1006,1018,1012],dtype='int32')
        ask=bid+2
        x=calculate_snapshot(ms,bid,ask,0,3,1,1002,970,1.,.2)
        self.assertAlmostEqual(x[0],-.08) # (1014-1002)/100-.2
        self.assertAlmostEqual(x[1],3.) # latest trailing stop at 1011
        self.assertEqual(x[2],2.)
        self.assertEqual(x[8],3.) # all post-entry quotes in last 1s
        # Future quote after landmark MUST NOT influence stop, MFE or market proxy
        bid[4:]=100000
        y=calculate_snapshot(ms,bid,ask,0,3,1,1002,970,1.,.2)
        self.assertEqual(x,y)

    def test_sell_quote_side_and_stop(self):
        ms=np.array([100,600,1100],dtype='int64')
        bid=np.array([1000,993,980],dtype='int32')
        ask=bid+4
        x=calculate_snapshot(ms,bid,ask,0,2,-1,1000,1034,1.,.2)
        self.assertAlmostEqual(x[0],-.04) # selling 1000, buy back at 984 => +.16-.20
        self.assertEqual(x[1],3.)  # favorable ask minimum 984, trail 987

    def test_snapshot_only_when_original_position_open(self):
        # Position 1 entry ord 1 exits ord 4; 1s at row3 eligible,
        # 3s after closing ineligible; second trade 1s missing.
        times=np.array([0,500,1100,1500,1600,1700,1800,1900],dtype='int64')
        bid=np.array([1000,1002,1005,1000,998,999,995,992],dtype='int32')
        ask=bid+2
        led=pd.DataFrame(dict(entry_ordinal=[1,5],exit_ordinal=[4,8],
            entry_time_msc=[0,1600],exit_time_msc=[1500,1900],
            side=[1,-1],entry_price_u=[1002,998],exit_price_u=[1000,994],
            net_price_u=[-2,4],r9_atr_u=[200.,200.],r9_eff=[.8,.8],
            spread_u=[2,2],session=[0,1],rearm=[0,1]))
        r=month_rows(5,led,times,bid,ask,np.array([.4,.7]),1,1.,.2,500,2500)
        self.assertEqual(r[1]['available'],1)
        self.assertEqual(r[3]['available'],0)
        self.assertEqual(int(r[1]['source_ordinal'][0]),3)
        self.assertAlmostEqual(float(r[1]['now'][0]),-.17)
        self.assertEqual(r[1]['X'].shape[1],len(FEATURE_COLS))

    def test_cash_loss_tail_cv_a_r_is_train_only(self):
        predtrain=np.array([0.,0.1,0.2,0.3]*600)
        deltas=np.array([-.7,-.5,.3,.5]*600)
        x=np.array([0.02,.18,.21])
        cvar,buckets=cvar_by_predicted_bucket(predtrain,deltas,x,levels=4)
        self.assertEqual(len(cvar),len(x))
        self.assertTrue(np.all(cvar>=0))
        self.assertEqual(len(buckets),4)

    def test_no_high_auc_feature_leakage_when_context_ablated(self):
        rng=np.random.default_rng(123)
        X=rng.standard_normal((1000,len(FEATURE_COLS)))
        y=rng.standard_normal(1000)
        p1,_=fit_predict(X[:700],y[:700],X[700:],False)
        X2=X.copy();X2[:,-1]=99999
        p2,_=fit_predict(X2[:700],y[:700],X2[700:],False)
        np.testing.assert_array_equal(p1,p2)


if __name__=='__main__':unittest.main()

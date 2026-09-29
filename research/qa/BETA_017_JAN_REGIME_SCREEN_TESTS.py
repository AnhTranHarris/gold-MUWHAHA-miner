"""BETA017 independent causal-feature and accounting tests.  Does not claim entry edge."""
import json, unittest
from pathlib import Path
import numpy as np
import BETA_017_JAN_REGIME_SCREEN as study
from BETA_009_JAN_JUL_ENTRY_CANDIDATE_VALIDATION import build_m5

ROOT=Path('/mnt/data')
R=json.loads((ROOT/'BETA_017_JAN_REGIME_SCREEN.json').read_text())

class Check(unittest.TestCase):
    def test_no_august(self):self.assertIs(R['sources']['august_read'],False)
    def test_source(self):
        self.assertEqual(R['sources']['ticks'],9135062)
        self.assertEqual(R['sources']['january_source_compressed_sha256'],'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5')
    def test_control_exact_b014(self):
        b=json.loads((ROOT/'BETA_014_PROP_001LOT_FUNDED_RERUN.json').read_text())['strategy_results']['R09_BETA_001_ADAPTIVE_IGNITION_ENTRY']
        x=R['experiments']['R09_BETA_001_UNFILTERED']
        for a,bname in [('trade_count','trade_count'),('winning_trades','winning_trades'),('net_profit_usd','net_profit_usd'),('gross_loss_usd','gross_loss_usd'),('overall_floor_breach_utc','overall_floor_breach_utc')]:
            self.assertEqual(x[a],b[bname])
    def test_pl_integrity(self):
        for n,x in R['experiments'].items():
            with self.subTest(n=n):
                self.assertAlmostEqual(x['gross_profit_usd']+x['gross_loss_usd'],x['net_profit_usd'],delta=.025)
                self.assertAlmostEqual(100000+x['net_profit_usd'],x['end_balance_usd'],delta=.025)
                self.assertLessEqual(x['winning_trades'],x['trade_count'])
                self.assertLessEqual(x['max_floating_equity_drawdown_usd'],10500)
                self.assertIsNone(x['overall_floor_breach_utc'] if not x['terminal_stop'] else None)
    def test_every_filter_loses(self):
        for x in R['experiments'].values():self.assertLess(x['net_profit_usd'],0)
    def test_causal_feature_prefix_invariance(self):
        # Deterministic one quote per complete M5 bucket; changing future cannot alter prior known state.
        t=(1767308400000+np.arange(110,dtype=np.int64)*300000+1500)
        price=(4200000+(np.sin(np.arange(110)*.37)*500).astype(np.int64)+np.arange(110)*3).astype(np.int64)
        t0=t[:99].copy();p0=price[:99].copy()
        mids,a=build_m5(t0,p0)
        eff,vr,hd,hids=study.completed_regime_features(t0,p0,mids,a)
        distorted=price.copy();distorted[99:]+=200000
        mids2,a2=build_m5(t,distorted)
        eff2,vr2,hd2,hids2=study.completed_regime_features(t,distorted,mids2,a2)
        np.testing.assert_allclose(eff,eff2[:99],equal_nan=True)
        np.testing.assert_allclose(vr,vr2[:99],equal_nan=True)
        # Last H1 bar in a truncated prefix is not necessarily closed: exclude it.
        # The simulator accesses last hour with id < the current hour only.
        np.testing.assert_array_equal(hd[:-1],hd2[:len(hd)-1])
    def test_decision_bars_must_be_completed(self):
        # Explicit source-code invariants: M5 p chosen by strictly earlier bucket and H1 search 'left'-1.
        src=(ROOT/'BETA_017_JAN_REGIME_SCREEN.py').read_text()
        self.assertIn("if m5ids[p]>=mb:p-=1",src)
        self.assertIn("np.searchsorted(h1_ids,hcur,side='left')-1",src)

if __name__=='__main__':unittest.main(verbosity=2)
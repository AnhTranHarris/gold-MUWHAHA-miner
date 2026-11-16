"""Source-clock causal and quote-side assertions, no broker/data downloads."""
import unittest
import numpy as np
from causal_lifecycle_v16 import intervention
from harvest_extension_v16 import first_extension_exit
from source_1s_specialists import exit_trade

class ProspectiveCausalUnitTests(unittest.TestCase):
    def test_adverse_first_cut_uses_next_quote(self):
        ms=np.array([1000,1100,1300,1310,2010,2020,3000,3100],dtype='int64')
        bi=np.array([10000,9992,9985,9983,9980,9978,9970,9960],dtype='int32')
        ask=bi+4
        rec=dict(entry_ordinal=1,exit_ordinal=8,side=1,entry_liquidation_u=10000)
        self.assertEqual(intervention(ms,bi,ask,rec,'C250_CUT_ADVERSE_ONLY'),
                         (3,'ADVERSE_FIRST_250MS_CUT'))
        self.assertEqual(intervention(ms,bi,ask,rec,'R1000_ALLOW_RECOVERY'),
                         (5,'ADVERSE_FIRST_UNRECOVERED_1S_CUT'))

    def test_favorable_first_not_misclassified_recovery(self):
        ms=np.array([1000,1100,1300,1310,2010,2020,3000,3100],dtype='int64')
        bi=np.array([10000,10020,9985,9983,9980,9978,9970,9960],dtype='int32')
        rec=dict(entry_ordinal=1,exit_ordinal=8,side=1,entry_liquidation_u=10000)
        self.assertIsNone(intervention(ms,bi,bi+4,rec,'C250_CUT_ADVERSE_ONLY'))

    def test_exit_before_landmark_must_remain_frozen(self):
        ms=np.array([1000,1100,1200,1300,1310,1510],dtype='int64')
        bi=np.array([10000,9990,9970,9960,9960,9950],dtype='int32')
        rec=dict(entry_ordinal=1,exit_ordinal=3,side=1,entry_liquidation_u=10000)
        self.assertIsNone(intervention(ms,bi,bi+4,rec,'C250_CUT_ADVERSE_ONLY'))

    def test_source_gap_abstains_from_outdated_landmark(self):
        ms=np.array([1000,1100,5000,5010,6000,6010,7000],dtype='int64')
        bid=np.array([10000,9990,9980,9980,9970,9960,9950],dtype='int32')
        rec=dict(entry_ordinal=1,exit_ordinal=7,side=1,entry_liquidation_u=10000)
        self.assertIsNone(intervention(ms,bid,bid+4,rec,'R1000_ALLOW_RECOVERY'))

    def test_harvest_extension_first_crossing_source_order(self):
        ms=np.array([1000,1000,1001,1100,1300],dtype='int64')
        bid=np.array([10030,10055,10070,9980,9990],dtype='int32');ask=bid+4
        # Entry at Ask=10004 (prior), profit at +0.6 reached at source ordinal3.
        j,net=first_extension_exit(ms,bid,ask,0,10004,10000,1,.40,.05,1000)
        self.assertEqual(j,2)
        self.assertAlmostEqual(net,.46)

    def test_sell_liquidation_is_ask(self):
        ms=np.array([1000,1100,1200,1300],dtype='int64')
        bi=np.array([10000,9950,9920,9900],dtype='int32');ask=bi+20
        j,net=first_extension_exit(ms,bi,ask,0,10000,10020,-1,.30,-.50,1000)
        self.assertEqual(j,2)
        self.assertAlmostEqual(net,.40)

    def test_market_trade_1s_source_quote_side(self):
        ms=np.array([1000,1100,1200,1300,1400,1500],dtype='int64')
        bi=np.array([10000,10010,10080,10090,10040,10030],dtype='int32');ask=bi+20
        config=('C',15,30,0,.35,40,5000)
        j,net,reason=exit_trade(ms,bi,ask,0,1,config)
        self.assertEqual(j,2)
        self.assertEqual(reason,'TARGET')
        self.assertAlmostEqual(net,.40)

if __name__=='__main__':unittest.main()

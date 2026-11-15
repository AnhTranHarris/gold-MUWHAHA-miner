"""Source-level causal contract tests, no futures and no trading account."""
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not (ROOT/'src').is_dir(): ROOT=ROOT/'r9_runner'
for p in ('src','variable_cash_horizon_20261114','micro180_20261114'):
    sys.path.insert(0,str(ROOT/p))
if (ROOT.parent/'micro180_v3_exact').is_dir():
    sys.path.insert(0,str(ROOT.parent/'micro180_v3_exact'))
from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config
from on_policy_cash_replay import ResearchCash
from micro180 import Micro180Spec,RollingThreeMinute
from v5_path_lifecycle import V5Spec,path_evidence,PathLifecycleV5

def tick(ms,bu,ask=None,ordinal=1):
    return Tick(ordinal,ms//1000,ms,bu,bu+10 if ask is None else ask)

class PathV5Contract(unittest.TestCase):
    def test_inputs_fail_closed(self):
        for bad in ({'min_buy_path':3},{'min_history':5},{'min_coherence':1.1},
                    {'max_spread_relative':.2},{'hold_sell_path':3},{'protect_cost_cash':-1}):
            with self.assertRaises(ValueError):V5Spec(**bad)
    def test_source_ms_equal_preserved_no_candle_hindsight(self):
        r=RollingThreeMinute()
        r.update(tick(101_001,1000));r.update(tick(101_001,1001))
        self.assertEqual(r.current[1000].n,2)
        self.assertEqual(r.closes(101_100,5000),[])
        r.update(tick(102_001,1002))
        self.assertEqual(len(r.closes(102_001,5000)),1)
        self.assertEqual(r.closes(102_001,5000)[0].bid_close,1001)
    def test_order_sensitive_signatures(self):
        a=RollingThreeMinute();b=RollingThreeMinute()
        # Same last close and price extrema but different ordered path.
        p1=[1000]*66+[1020,1000,1020,1020]
        p2=[1000]*66+[1000,1020,1000,1020]
        for i in range(70):
            a.update(tick(100_000+i*1000,p1[i],ordinal=i+1))
            b.update(tick(100_000+i*1000,p2[i],ordinal=i+1))
        e1=path_evidence(a,tick(170_001,1020),1)
        e2=path_evidence(b,tick(170_001,1020),1)
        self.assertIsNotNone(e1);self.assertIsNotNone(e2)
        self.assertNotEqual(e1.tail_persistence,e2.tail_persistence)
    def test_sell_uses_ask_liquidation(self):
        r=RollingThreeMinute()
        for i in range(80):r.update(tick(100_000+i*1000,2000-i,2010-i,i+1))
        e1=path_evidence(r,tick(180_001,1920,1930),-1)
        e2=path_evidence(r,tick(180_001,1920,1960),-1)
        self.assertIsNotNone(e1);self.assertIsNotNone(e2)
        self.assertNotEqual(e1.score,e2.score)
    def test_hold_off_and_cash_target(self):
        m=PathLifecycleV5(R9Config(use_regime_gate=False),ResearchCash(governor=False),Micro180Spec(),v5=V5Spec())
        self.assertFalse(m.v5.enable_protected_continuation)
        self.assertEqual(m.report()['v5_lifecycle']['cash_first_harvest'],.1)
        self.assertFalse(m.report()['v5_lifecycle']['no_AUC'] is False)
if __name__=='__main__':unittest.main()

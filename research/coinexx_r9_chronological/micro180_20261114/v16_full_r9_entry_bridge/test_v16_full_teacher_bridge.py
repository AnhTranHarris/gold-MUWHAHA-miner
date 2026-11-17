"""Causal source-contract tests for V16 independent entry redesign."""
from __future__ import annotations
from pathlib import Path
import math, os, unittest
from v16_full_teacher_bridge import Quote,V16CausalBridge,all_teacher_targets,clock_priors,FEATURE_NAMES
from v16_train_and_replay import OwnPosition,session_floor

MERGED=Path(os.environ.get('R9_MERGED_PATH','/mnt/data/r9_synthetic_teacher_to_original_REAL_TickLogger_9m_trade_marks.csv.gz'))

class ScoreModel:
    def __init__(self,score):self.value=score
    def predict(self,x,num_threads=1):return [self.value]

class V16Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.targets=all_teacher_targets(MERGED) if MERGED.is_file() else {}
        cls.prior=clock_priors(cls.targets,train_months=('2026-02','2026-03','2026-04'))

    def quote(self,age,mid=432700,spread=10,minute=30000000,off=20,atr=600):
        return Quote((minute*60+age)*1000+off,mid-spread//2,mid+spread//2,atr,175.)

    @unittest.skipUnless(MERGED.is_file(), 'Original merged reference not attached to CI')
    def test_complete_teacher_population_not_positive_only(self):
        self.assertEqual(len(self.targets),272352)
        self.assertEqual(sum(k[1]==1 for k in self.targets),192487)
        self.assertEqual(sum(k[1]==2 for k in self.targets),79865)

    def test_model_has_exact_feature_contract_and_causal_state(self):
        b=V16CausalBridge(self.prior)
        for i in range(310):b.observe(self.quote(i%60,432700+i,minute=30000000+i//60))
        x=b.features(self.quote(10,433020,minute=30000006),1,1)
        self.assertEqual(len(x),len(FEATURE_NAMES))
        self.assertTrue(all(map(math.isfinite,x)))

    def test_no_future_quote_used_and_fill_on_next_actual_quote(self):
        b=V16CausalBridge(self.prior,ScoreModel(1.),ScoreModel(1.),threshold=.5)
        a=b.observe(self.quote(0))
        self.assertEqual(a,[])
        a=b.observe(self.quote(1,432725))
        self.assertEqual(len(a),1)
        self.assertEqual(a[0].price_cents,432730) # BUY Ask
        self.assertEqual(a[0].origin_time_msc,self.quote(0).time_msc)
        self.assertEqual(a[0].time_msc,self.quote(1,432725).time_msc)
        self.assertEqual(b.observe(self.quote(2,432730)),[])

    def test_rearm_after_own_exit_only(self):
        b=V16CausalBridge(self.prior,ScoreModel(1.),ScoreModel(1.),threshold=.5)
        b.observe(self.quote(0))
        a=b.observe(self.quote(1))
        self.assertEqual(len(a),1)
        self.assertEqual(b.observe(self.quote(2)),[])
        b.notify_closed(self.quote(2).time_msc,a[0].side)
        self.assertEqual(b.rearm_side,-a[0].side)
        self.assertEqual(b.observe(self.quote(3)),[])
        a2=b.observe(self.quote(4))
        self.assertEqual(len(a2),1)
        self.assertEqual(a2[0].side,-a[0].side)
        self.assertEqual(b.observe(self.quote(5)),[])

    def test_spread_and_atr_gates(self):
        b=V16CausalBridge(self.prior,ScoreModel(1.),ScoreModel(1.),threshold=.5)
        self.assertFalse(b.observe(self.quote(0,spread=26)))
        self.assertFalse(b.observe(self.quote(1,atr=100)))
        self.assertFalse(b.observe(self.quote(2,spread=30)))

    def test_frozen_position_not_exit_research(self):
        q=self.quote(1)
        p=OwnPosition(1,q.ask_cents,q.time_msc,q.bid_cents-30,q.bid_cents-30)
        self.assertFalse(p.manage(self.quote(2,mid=432715)))
        self.assertTrue(p.manage(self.quote(3,mid=432650)))

if __name__=='__main__':unittest.main()

"""Non-negotiable invariants for owner-accepted MICRO180 V28 entry checkpoint.
No claim of native MetaEditor compilation or order-fill equivalence.
"""
import hashlib
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EA = ROOT / "GoldMuwahahaMiner_MICRO180_V28_FrozenEntry.mq5"
WEIGHTS = ROOT / "MICRO180_Jan_through_07_merged_weights.tsv"
CPP = ROOT / "v28_forward_frozen.cpp"
EXPECTED_SHA256 = "92719ae1edd78c91e63f151da7d2f3607c7d5f42119b07613b8b20a7cce3997b"
ROLES = {"A_EARLY", "A_LATE", "B_FIRST", "C_FIRST", "D_FIRST", "B_SECOND", "C_SECOND", "D_SECOND"}
STATES = {"trend", "nested_trend", "reversal", "consolidation", "breakout", "transition", "ANY"}

class FrozenPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = EA.read_text()
        cls.cpp = CPP.read_text()
        cls.lines = WEIGHTS.read_text().splitlines()

    def test_source_weights_exact_sha256(self):
        self.assertEqual(hashlib.sha256(WEIGHTS.read_bytes()).hexdigest(), EXPECTED_SHA256)
        self.assertIn(EXPECTED_SHA256, self.src)

    def test_all_role_heads_and_all_2658_experts_present(self):
        experts = [line.split() for line in self.lines if line.startswith("G ")]
        self.assertEqual(len(experts), 2658)
        self.assertEqual({x[1] for x in experts}, ROLES)
        self.assertEqual({int(x[2]) for x in experts}, {-1, 1})
        self.assertTrue({x[3] for x in experts}.issubset(STATES))
        self.assertTrue(all(len(x) == 56 for x in experts))
        self.assertIn("gProtoN!=2658", self.src)
        self.assertIn("MAX_PROTOS 8192", self.src)

    def test_all_phase_hourly_rates_and_priors(self):
        phase = [x.split() for x in self.lines if x.startswith("P ")]
        self.assertEqual(len(phase), 16)
        self.assertTrue(all(len(x) == 63 for x in phase))
        self.assertEqual(len([x for x in self.lines if x.startswith("PHASEMIN ")]), 16)
        rates = [x.split() for x in self.lines if x.startswith("RATE ")]
        self.assertEqual(len(rates), 8 * 24)
        self.assertEqual(len([x for x in self.lines if x.startswith("PRIOR ")]), 8)
        for role in ROLES:
            self.assertEqual({int(x[2]) for x in rates if x[1] == role}, set(range(24)))

    def test_precise_normalization_feature_contract(self):
        ix = [3,4,5,6,7,8,9,10,11,12,13,17,18,20,21,22,24,25,26,27,30,31,32,33,36]
        a = re.search(r"FEATURE_MAP\[NFEAT\]=\{([^}]+)\}", self.src)
        b = re.search(r"static const int ix\[\]=\{([^}]+)\}", self.cpp)
        self.assertEqual([int(n) for n in a.group(1).split(',')], ix)
        self.assertEqual([int(n) for n in b.group(1).split(',')], ix)
        self.assertEqual(self.src.count('v[37]='), 1)
        self.assertIn('CopyBuffer(gAtrHandle,0,1,1', self.src)
        self.assertIn('q.time_msc/60000', self.src)

    def test_reproduce_cpp_last_prototype_quasi_bug(self):
        # Frozen C++ Candidate.score is not assigned until AFTER its prototype
        # loop, so c.score==-1e9 stays true for all prototypes. The last
        # matching model is selected (not the best-distance prototype).
        self.assertIn('den>c.density||c.score==-1e9', self.cpp)
        self.assertIn('found=true;best=density;bestThresh=', self.src)
        self.assertNotIn('if(!found||density>best)', self.src)

    def test_dual_basket_model_and_complete_hourly_budgets(self):
        self.assertIn('r!=gFirstRole+3', self.src)
        self.assertIn('side!=-gFirstSide', self.src)
        self.assertIn('gToken[r]=MathMin(3.,gToken[r]+gRate[r][h])', self.src)
        self.assertIn('gModelCalendarMonth!=monthKey', self.src)
        self.assertIn('gHaveFirst=true', self.src)
        self.assertIn('gHaveSecond=true', self.src)

    def test_causal_minute_eval_order_and_gap_semantics(self):
        self.assertIn('evalBeforeMinuteReset', self.src)
        self.assertLess(self.src.index('bool evalBeforeMinuteReset'), self.src.index('UpdateQuote(q);'))
        self.assertLess(self.src.index('bool evalBeforeMinuteReset'), self.src.index('if(newMinute){', self.src.index('void OnTick(){')))
        self.assertIn('if(x==EMPTY_VALUE)return 0.;', self.src)
        self.assertIn('bool eval=sec!=prevsec', self.cpp)
        self.assertIn('if(!isfinite(x))return 0.;', self.cpp)

    def test_entry_only_and_teacher_blind(self):
        executable = self.src[self.src.index('int OnInit(){'):]
        self.assertFalse(re.search(r'\bOrderSend\s*\(|\bCTrade\b|trade\s*\.\s*(Buy|Sell|PositionClose|PositionModify)\s*\(', executable))
        self.assertFalse(re.search(r'\bquote_net\b|\bteacher\b|\bprofit\b', executable, re.I))
        self.assertIn('conditional_on_flat', self.src)
        self.assertIn('FileWriteString(gIntentFile,out)', self.src)

if __name__ == '__main__':
    unittest.main(verbosity=2)
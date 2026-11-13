"""R9 checkpoint repository tests. No raw Coinexx data or retraining."""
from pathlib import Path
import re
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[2]
sys.path.insert(0,str(ROOT))
from lineage_audit import verify_local_lineage, CONTRACT_COUNTS, MODEL_SHA


class CheckpointLineage(unittest.TestCase):
    def test_original_source_sha1_blobs(self):
        result=verify_local_lineage()
        self.assertEqual(result["model_input_dimensions"],155)
        self.assertEqual(len(result["original_source_git_blobs"]),3)
        self.assertEqual(
            CONTRACT_COUNTS,
            {"r9_context":14, "hft_selected":25, "event_time":77,
             "cusum_and_quote_intensity":23, "brownian_geometry":11,
             "action_metadata":5},
        )

    def test_all_original_direct_model_hashes_pinned(self):
        self.assertEqual(len(MODEL_SHA),6)
        self.assertTrue(all(re.fullmatch("[0-9a-f]{64}",s)
                            for s in MODEL_SHA.values()))

    def test_ea_version_includes_and_safe_default(self):
        ea=(REPO/"Experts"/"GoldMuwahahaMiner_R9_HybridGate.mq5").read_text()
        for name in (
            "GoldMuwahahaR9PortfolioGovernor.mqh",
            "GoldMuwahahaR9M1IndicatorContext.mqh",
            "GoldMuwahahaR9CashGeometry.mqh",
            "GoldMuwahahaR9M60ModelBridge.mqh",
        ):
            self.assertIn('#include "'+name+'"',ea)
        self.assertIn('#property version   "1.94"',ea)
        self.assertIn("InpR9M60Mode                     = 1",ea)
        self.assertIn("InpR9M60ExperimentalFilterUnlock = false",ea)
        self.assertIn("InpR9GovEnabled                  = true",ea)
        self.assertIn("InpR9M1RescueEnabled             = false",ea)
        self.assertIn("if(originalQualified && !R9M60PermitOriginalEntry(tick,side)) return;",ea)
        self.assertIn("InpR9M60MinProbability<=0.0",ea)

    def test_score_hash_is_frozen_jan_sep_model(self):
        ea=(REPO/"Experts"/"GoldMuwahahaMiner_R9_HybridGate.mq5").read_text()
        self.assertIn(MODEL_SHA["direct_all_JanSep_IS_ONLY.joblib"],ea)

    def test_project_protects_untrained_rescue_universe(self):
        ea=(REPO/"Experts"/"GoldMuwahahaMiner_R9_HybridGate.mq5").read_text()
        self.assertIn("if(InpR9M60Mode==2) return;",ea)
        self.assertIn("if(!R9IndicatorRescue(side,tick.time,indicatorScore)) return;",ea)


if __name__=="__main__":
    unittest.main()

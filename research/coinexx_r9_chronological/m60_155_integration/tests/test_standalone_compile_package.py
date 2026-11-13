"""MT5 single-file checkpoint: exact source equivalence and include audit.

No MQL5 compiler is available in GitHub's Python runners. These tests verify
the original four embedded MQH sources are byte-for-byte unchanged and every
reference to the local MQH files is removed. Real MetaEditor compilation
remains required to certify the EX5.
"""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[2]
EA=REPO/"Experts"/"GoldMuwahahaMiner_R9_HybridGate.mq5"
STANDALONE=REPO/"Experts"/"Advisors"/"GWM_EA"/"r9_v1_94.mq5"
DEPENDENCIES=(
    "GoldMuwahahaR9PortfolioGovernor.mqh",
    "GoldMuwahahaR9M1IndicatorContext.mqh",
    "GoldMuwahahaR9CashGeometry.mqh",
    "GoldMuwahahaR9M60ModelBridge.mqh",
)


class SourceExactStandalone(unittest.TestCase):
    def test_standalone_is_exactly_modular_ea_with_only_four_includes_inlined(self):
        main=EA.read_text(encoding="utf-8")
        expected=main
        for name in DEPENDENCIES:
            marker='#include "'+name+'"'
            self.assertEqual(expected.count(marker),1,name)
            body=(EA.parent/name).read_text(encoding="utf-8").rstrip("\n")
            expected=expected.replace(marker,
                "// R9_STANDALONE_BEGIN "+name+"\n"+
                body+"\n"+
                "// R9_STANDALONE_END "+name)
        self.assertEqual(STANDALONE.read_text(encoding="utf-8"),expected)

    def test_only_standard_mt5_trade_header_remains(self):
        single=STANDALONE.read_text(encoding="utf-8")
        directives=re.findall(r'(?m)^\s*#include\s*(.*)$',single)
        self.assertEqual(directives,["<Trade/Trade.mqh>"])
        for name in DEPENDENCIES:
            self.assertIn("// R9_STANDALONE_BEGIN "+name,single)
            self.assertIn("// R9_STANDALONE_END "+name,single)
        self.assertIn('#property version   "1.94"',single)

    def test_entry_hold_exit_governor_and_model_bridge_all_preserved(self):
        t=STANDALONE.read_text(encoding="utf-8")
        for token in ("void OnTick()", "void OnTimer()",
                      "void OnTradeTransaction(", "R9GovAllowsOrder(",
                      "R9GovCloseOurPositions(", "R9M60PermitOriginalEntry(",
                      "R9IndicatorConfluence(", "R9CashScenario(",
                      "InpR9M60Mode                     = 1",
                      "InpR9M60ExperimentalFilterUnlock = false",
                      "InpR9M1RescueEnabled             = false"):
            self.assertIn(token,t)
        for handler in ("void OnTick()", "void OnTimer()",
                        "void OnTradeTransaction("):
            self.assertEqual(t.count(handler),1,handler)


if __name__=="__main__":
    unittest.main()

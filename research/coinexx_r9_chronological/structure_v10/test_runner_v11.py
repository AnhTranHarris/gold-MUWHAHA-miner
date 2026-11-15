"""Test single-pass frozen V9/V10/V11 source-exact replay without market data."""
import csv
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_structure_refinement_v11 import run


class FullPathV11Tests(unittest.TestCase):
    def test_full_existing_schema_unchanged_and_accounting(self):
        with tempfile.TemporaryDirectory() as folder:
            ticks=Path(folder)/"synthetic_Coinexx_schema.csv"
            with ticks.open("w",newline="") as f:
                out=csv.writer(f)
                out.writerow(["time","time_msc","bid","ask","last",
                              "volume","volume_real","flags"])
                for sec in range(190):
                    for sub in (0,400,800):
                        bid=2000.+.07*sec+.02*(sub//400)
                        out.writerow([sec,sec*1000+sub,
                                      f"{bid:.2f}",f"{bid+.04:.2f}",
                                      "0","0","0","0"])
            report=run(ticks,570)
            self.assertEqual(report["quotes"],570)
            self.assertTrue(report["v9_v10_v11_exact_trade_decision_parity"])
            # Default historical V9 regime gate can correctly reject this
            # deliberately simple synthetic schema fixture. The independent
            # model-level test exercises >0 real entry events.
            self.assertEqual(sum(report["structure_v11"]["v11_entry_subtypes"].values()),
                             report["entries"])
            self.assertEqual(report["structure_v11"]["original_v9_decisions_modified"],False)
            self.assertFalse(report["profits_evaluated"])


if __name__=="__main__":unittest.main()

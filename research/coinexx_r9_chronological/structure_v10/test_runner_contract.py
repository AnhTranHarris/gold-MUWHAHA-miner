"""Bounded original-reader integration: 570 tiny synthetic rows, no downloads."""
import csv
import sys
import tempfile
import unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from run_structure_audit import run


class RunnerTests(unittest.TestCase):
    def test_existing_coinexx_schema_and_v9_ordinal_fidelity(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"synthetic_existing_schema.csv"
            with p.open("w",newline="") as f:
                w=csv.writer(f)
                w.writerow(["time","time_msc","bid","ask","last",
                            "volume","volume_real","flags"])
                for sec in range(190):
                    for fraction in (0,400,800):
                        bid=2000.+.07*sec+.02*(fraction//400)
                        w.writerow([sec,sec*1000+fraction,
                                    f"{bid:.2f}",f"{bid+.04:.2f}",
                                    "0","0","0","0"])
            data=run(p,570)
            self.assertTrue(data["same_entry_exit_quote_ordinals"])
            self.assertTrue(data["trade_decisions_unchanged"])
            self.assertFalse(data["native_parity_verified"])
            self.assertEqual(data["observed_quotes"],570)
            self.assertIn("structure",data)
            self.assertGreater(data["structure"]["event_counters"]["quotes"],0)


if __name__=="__main__":unittest.main()

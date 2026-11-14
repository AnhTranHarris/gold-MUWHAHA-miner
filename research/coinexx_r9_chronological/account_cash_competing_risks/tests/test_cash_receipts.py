"""Reject unsafe longitudinal training merges of different monetary scenarios."""
import contextlib
import csv
from dataclasses import asdict,fields
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[0]
sys.path.insert(0,str(REPO/"src"))
sys.path.insert(0,str(ROOT/"src"))
from cash_risk_overlay import Episode,CAUSE_TARGET,CAUSE_STOP
from cli import train_evaluate


def fixture(root,name,at,fee=0.20,currency="USD",config=None):
    out=root/f"{name}.csv"
    e=Episode(entry_ordinal=int(at//1000),entry_time_msc=at,
              source_hour=3,session=1,side=1,entry_price_cents=400000,
              entry_spread_cents=20,cause=CAUSE_TARGET if name.startswith("train") else CAUSE_STOP,
              event_time_ms=1000,overlay_net_cash=1.8 if name.startswith("train") else -.5)
    with out.open("w",newline="",encoding="utf8") as fh:
        w=csv.DictWriter(fh,fieldnames=[v.name for v in fields(Episode)])
        w.writeheader();w.writerow(asdict(e))
    receipt={
        "schema":"R9_CASH_EPISODES_V1",
        "cash_assumptions":{"account_currency":currency,
                            "round_trip_cost_cash":fee,
                            "cash_per_one_xau_price_dollar":1.0,
                            "goal_net_cash":1.75,
                            "max_hold_ms":30000,
                            "max_quote_gap_ms":10000},
        "r9_config":config if config is not None else {"lots":.01},
        "source_receipts":[{"compressed_sha256":"f"*64,"source_sha_verified":True}],
        "simulation_truncated":False,
        "source_rows_processed":10,
    }
    Path(str(out)+".receipt.json").write_text(json.dumps(receipt),encoding="utf8")
    return out


class Receipts(unittest.TestCase):
    def args(self,train,test):
        return SimpleNamespace(train_episodes=[train],test_episodes=[test],
                               by="global",min_group_count=1,
                               cvar_penalty=.0,max_censor_fraction=.1,out=None)

    def test_same_cash_and_chronological_receipt_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            tr=fixture(p,"train_1",1_000_000)
            te=fixture(p,"test_1",2_000_000)
            with contextlib.redirect_stdout(io.StringIO()) as out:
                train_evaluate(self.args(tr,te))
            val=json.loads(out.getvalue())
            self.assertTrue(val["all_original_source_hashes_verified"])
            self.assertEqual(val["account_currency"],"USD")

    def test_different_cost_or_currency_is_never_silently_merged(self):
        for fee,cur in ((.30,"USD"),(.2,"EUR")):
            with tempfile.TemporaryDirectory() as td:
                p=Path(td)
                tr=fixture(p,"train_a",1_000_000)
                te=fixture(p,"test_a",2_000_000,fee=fee,currency=cur)
                with self.assertRaises(ValueError):
                    train_evaluate(self.args(tr,te))

    def test_training_must_precede_eval(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            tr=fixture(p,"train_a",3_000_000)
            te=fixture(p,"test_a",2_000_000)
            with self.assertRaises(ValueError):
                train_evaluate(self.args(tr,te))

    def test_missing_source_receipt_fails(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            tr=fixture(p,"train_a",1_000_000)
            te=fixture(p,"test_a",2_000_000)
            Path(str(tr)+".receipt.json").unlink()
            with self.assertRaises(ValueError):
                train_evaluate(self.args(tr,te))


if __name__=="__main__":
    unittest.main()

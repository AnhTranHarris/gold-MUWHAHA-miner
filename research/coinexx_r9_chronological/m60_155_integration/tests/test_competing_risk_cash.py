"""Pinned model competing-risk mathematics; synthetic input, no tick rebuild."""
import csv
import pathlib
import sys
import tempfile
import unittest

import numpy as np

HERE=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
from competing_risk_cash import (
    cumulative_risks,scenario_ev,snapshot_geometry,score_packet,
    packet_filename,publish_packet,MODEL_BYTES,
)
from score_snapshot import SCHEMA as SNAPSHOT_SCHEMA


class ControlledHazardModel:
    def __init__(self):
        # Conditional risk-set classes [none, favorable, adverse] for each bin.
        self.by_bin=np.array([
            [0.80,0.10,0.10],
            [0.50,0.10,0.40],
            [0.60,0.20,0.20],
            [0.60,0.20,0.20],
            [0.80,0.10,0.10]],dtype=float)

    def predict_proba(self,x):
        assert x.shape==(5,156)
        assert list(x[:,-1])==[0,1,2,3,4]
        return self.by_bin.copy()


def snapshot():
    import datetime as dt
    now=int(dt.datetime(2026,11,14,tzinfo=dt.timezone.utc).timestamp()*1000)
    vals=[0.0]*155
    vals[-5]=1.0
    vals[-4]=1.0
    vals[-3]=50.0
    vals[-2]=80.0
    vals[-1]=20.0
    return dict(
        schema_id=SNAPSHOT_SCHEMA,
        market_source="Coinexx",feature_origin="FROZEN_EXACT_ASOF",
        time_msc=now,feature_end_time_msc=now,source_ordinal=50200,
        account_login=98765,symbol="XAUUSD",magic=5559,
        bid_cents=400000,ask_cents=400020,side=1,features=vals,
    )


class CompetingRiskTests(unittest.TestCase):
    def test_real_archive_model_hash_manifest(self):
        self.assertEqual(len(MODEL_BYTES),6)
        self.assertEqual(MODEL_BYTES["final_is"],
                         "717829da94b15af27f244b51ea22458319470052471b9f3ca65dd51501daa1a3")

    def test_cumulative_survival_is_conditional_at_each_bin(self):
        results=cumulative_risks(ControlledHazardModel(),np.zeros((1,155),np.float32))
        self.assertAlmostEqual(results[5000]["p_fav"],0.1+0.8*.1+0.4*.2+0.24*.2)
        self.assertAlmostEqual(results[5000]["p_adv"],0.1+0.8*.4+0.4*.2+0.24*.2)
        self.assertAlmostEqual(results[5000]["p_alive"],0.144)
        self.assertAlmostEqual(results[15000]["p_fav"],results[5000]["p_fav"]+0.144*.1)
        self.assertAlmostEqual(results[15000]["p_adv"],results[5000]["p_adv"]+0.144*.1)
        self.assertAlmostEqual(results[15000]["p_alive"],0.1152)
        self.assertAlmostEqual(sum(results[15000].values()),1.0)

    def test_cash_ev_pays_fee_once_even_on_survival(self):
        x=scenario_ev(.3,.4,.3,3.0,1.0,.2,0)
        # +$3 gross, -$1 gross, $0 surviving gross, all pay -$0.20.
        self.assertAlmostEqual(x["expected_net_account_cash"],.3*3-.4*1-.2)
        self.assertAlmostEqual(x["loss_cvar95_account_cash"],1.2)
        self.assertAlmostEqual(x["risk_adjusted_net_account_cash"],
                               x["expected_net_account_cash"])

    def test_cvar_exact_when_rare_worst_case_is_below_five_percent(self):
        x=scenario_ev(.9,.01,.09,4.0,3.0,.2,0,risk_weight=.5)
        # worst 1% at loss 3.20, next 4% from surviving loss 0.20.
        self.assertAlmostEqual(x["loss_cvar95_account_cash"],
                               (.01*3.2+.04*.2)/.05)
        self.assertAlmostEqual(x["risk_adjusted_net_account_cash"],
                               x["expected_net_account_cash"]-
                               .5*x["loss_cvar95_account_cash"])

    def test_bounds_are_valid_for_range_of_unresolved_payoff(self):
        x=scenario_ev(.2,.3,.5,2.0,1.0,.2,0)
        self.assertLessEqual(x["lower_timeout_bound_account_cash"],
                             x["expected_net_account_cash"])
        self.assertGreaterEqual(x["upper_timeout_bound_account_cash"],
                                x["expected_net_account_cash"])

    def test_model_label_geometry_exact(self):
        s=snapshot()
        self.assertEqual(snapshot_geometry(s),(50,80))
        s["features"][-1]=19.
        with self.assertRaises(ValueError):
            snapshot_geometry(s)

    def test_bad_probabilities_refused(self):
        for probs in [(-.1,.4,.7),(.4,.4,.4),(float("nan"),.2,.8)]:
            with self.assertRaises(ValueError):
                scenario_ev(*probs,3,1,.2,0)

    def test_full_23_field_packet_roundtrip(self):
        s=snapshot()
        probs,row=score_packet(ControlledHazardModel(),MODEL_BYTES["final_is"],
                               "hazard_all_JanSep_IS_ONLY","final_is",s)
        self.assertEqual(len(row),23)
        self.assertEqual(row[0],"R9_CRISK155_V1")
        self.assertEqual(row[9],MODEL_BYTES["final_is"])
        self.assertEqual(row[13:15],["50","80"])
        self.assertEqual(row[21],"ASOF_PINNED")
        self.assertEqual(row[22],"R9_CRISK_155_20261113_V1")
        self.assertAlmostEqual(float(row[15]),probs[5000]["p_fav"])
        self.assertAlmostEqual(float(row[20]),probs[15000]["p_alive"])
        with tempfile.TemporaryDirectory() as d:
            name=packet_filename(s)
            publish_packet(pathlib.Path(d),name,row)
            with (pathlib.Path(d)/name).open(newline="") as f:
                result=list(csv.reader(f))
            self.assertEqual(result,[row])
            self.assertEqual(len(list(pathlib.Path(d).iterdir())),1)


if __name__=="__main__":
    unittest.main()

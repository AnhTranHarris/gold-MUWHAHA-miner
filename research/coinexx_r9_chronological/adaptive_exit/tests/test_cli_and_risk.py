"""Small original Coinexx-schema gzip tests and experimental stop risk caps."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve()
PROJECT=HERE.parents[2]
sys.path.insert(0,str(PROJECT/"src"))
sys.path.insert(0,str(PROJECT/"account_cash_competing_risks"/"src"))
sys.path.insert(0,str(HERE.parents[1]/"src"))

from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config
from cash_risk_overlay import CashAssumptions
from adaptive_policy import AdaptiveR9,ExitPolicy
from cli import run


def tick(i,second,bid,spread=20):
    return Tick(ordinal=i,time_s=second,time_msc=second*1000+i,
                bid_u=bid,ask_u=bid+spread)


def easy():
    return R9Config(use_regime_gate=False,velocity_lookback_sec=2,
                    range_lookback_sec=2,min_velocity_pips=0,
                    min_directional_eff=0,min_range_pips=0,max_turns=99)


class SmokeAndStops(unittest.TestCase):
    def test_original_coinexx_broker_gzip_one_pass_three_arms(self):
        rows=[
            (120,1000,1020),(121,1005,1025),(122,1010,1030),
            (123,1030,1050),(124,1075,1095),(125,1070,1090),
            (126,1060,1080),(127,1030,1050),(128,990,1010),
            (129,978,998),(130,990,1010),(131,1060,1080),
        ]
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            raw=root/"ORIGINAL_TINY_COINEXX.csv.gz"
            with gzip.open(raw,"wt",newline="",encoding="utf-8") as f:
                w=csv.writer(f)
                w.writerow(("time","time_msc","bid","ask","last",
                            "volume","volume_real","flags"))
                for n,(sec,bid,ask) in enumerate(rows,1):
                    w.writerow((sec,sec*1000+n,
                                f"{bid/100:.2f}",f"{ask/100:.2f}",
                                "0.00",0,0,134))
            source_hash=hashlib.sha256(raw.read_bytes()).hexdigest()
            cfg=root/"R9_config.json"
            # R9Config frozen/slotted? Use dataclasses.asdict for portability.
            from dataclasses import asdict
            cfg.write_text(json.dumps(asdict(easy())),encoding="utf-8")
            args=SimpleNamespace(
                policies=["baseline","cost_trail","staged_harvest"],
                allow_wider_initial_stop=False,max_ticks=0,
                expected_source_sha256=[source_hash],ticks=[raw],
                config_json=cfg,account_currency="USD",
                cash_per_one_xau_dollar=1.0,round_trip_cost_cash=0.2,
                alpha_spread=.75,beta_noise=1.25,
                m1_std_weight=.2,m1_ema_weight=.1,
                activation_cash_buffer=.06,minimum_harvest_cash=.1,
                maximum_initial_risk_cash=1.5,output=root/"tiny_result.json")
            result=run(args)
            self.assertEqual(result["source_rows"],len(rows))
            self.assertFalse(result["truncated"])
            self.assertEqual(len(result["stats_by_policy"]),3)
            self.assertTrue(result["source_receipts"][0]["source_sha256_verified"])
            self.assertTrue(args.output.is_file())
            for s in result["stats_by_policy"].values():
                self.assertFalse(s["account_governor_simulated"])
                self.assertTrue(s["no_actual_order_fills"])

    def test_original_source_hash_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            raw=Path(td)/"dummy.csv.gz"
            with gzip.open(raw,"wt") as out:out.write("broken")
            args=SimpleNamespace(
                policies=["baseline"],allow_wider_initial_stop=False,
                max_ticks=0,expected_source_sha256=["0"*64],ticks=[raw],
                config_json=None,account_currency="USD",
                cash_per_one_xau_dollar=1.,round_trip_cost_cash=.2,
                alpha_spread=.75,beta_noise=1.25,
                m1_std_weight=.20,m1_ema_weight=.10,
                activation_cash_buffer=.06,minimum_harvest_cash=.1,
                maximum_initial_risk_cash=1.5,output=None)
            with self.assertRaises(ValueError):
                run(args)

    def test_initial_stop_risk_cash_cap_never_overridden(self):
        cfg=easy()
        cash=CashAssumptions("USD",1.0,0.2)
        sim=AdaptiveR9(cfg,cash,ExitPolicy(
            mode="experimental_wide_stop", maximum_initial_risk_cash=0.55))
        sim._noise=lambda tick:20.0 # known synthetic pre-entry noise state for cap unit test
        for z in [
            tick(1,120,1000),tick(2,121,1005),
            tick(3,122,1010),tick(4,123,1030)
        ]:
            sim.on_tick(z)
        self.assertIsNotNone(sim.position)
        self.assertEqual(sim.position.initial_sl_u,1000)
        self.assertEqual(sim.stats["experimental_initial_risk_cap_refusals"],1)

    def test_explicit_unlock_required_for_wider_initial_sl(self):
        args=SimpleNamespace(
            policies=["baseline","experimental_wide_stop"],
            allow_wider_initial_stop=False,max_ticks=0,
            expected_source_sha256=None,ticks=[],config_json=None,
            account_currency="USD",cash_per_one_xau_dollar=1.,
            round_trip_cost_cash=.2,output=None)
        with self.assertRaises(ValueError):
            run(args)


if __name__=="__main__":
    unittest.main()

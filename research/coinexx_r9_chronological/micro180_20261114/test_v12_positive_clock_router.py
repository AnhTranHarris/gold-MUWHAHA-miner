"""Micro180 V12 positive-clock/no-hindsight deterministic source contracts."""
from __future__ import annotations

import csv
import gzip
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
PROJ = ROOT.parent
for p in (PROJ / "src", PROJ / "variable_cash_horizon_20261114",
          PROJ / "dual_basket_20261114", ROOT):
    sys.path.insert(0, str(p))

from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config, R9HybridGateBaseline
from v12_positive_clock_router import (
    CompletedMultiScaleClock, FIRST_FEATURES, SECOND_FEATURES,
    Micro180V12PositiveClock, V12PositiveClockSpec,
)
from v12_positive_cycle_targets import read_positive_targets


class FixedModel:
    def __init__(self, p: float = 1.0):
        self.p = p
        self.rows = []

    def score(self, row):
        self.rows.append(row)
        return self.p


def tick(i, sec, ms=5, bid=10000, spread=20):
    return Tick(i, sec, sec * 1000 + ms, bid, bid + spread)


def cfg():
    return R9Config(
        use_regime_gate=False, velocity_lookback_sec=2, range_lookback_sec=2,
        min_velocity_pips=0, min_directional_eff=0, min_range_pips=0,
        max_turns=99, max_same_minute_rearms=1,
    )


class PositiveRouter(unittest.TestCase):
    def test_research_only_guards(self):
        for kwargs in (
            {"live_orders_enabled": True},
            {"allow_historical_event_intervention": True},
            {"max_next_quote_delay_ms": 5000},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                V12PositiveClockSpec(**kwargs)

    def test_first_entry_is_at_a_later_real_source_quote(self):
        first = FixedModel()
        second = FixedModel()
        sim = Micro180V12PositiveClock(cfg(), first_model=first, second_model=second)
        with patch.object(R9HybridGateBaseline, "_process_entries",
                          side_effect=AssertionError("R9 entry driver must NOT execute")):
            sim.on_tick(tick(0, 60, ms=10, bid=10000))
            self.assertEqual(len(sim.entries), 0)
            sim.on_tick(tick(1, 61, ms=7, bid=10000))
        self.assertEqual(len(sim.entries), 1)
        entry = sim.entries[0]
        self.assertEqual(entry["time_msc"], 61007)
        self.assertEqual(entry["price_u"], 10020)
        self.assertEqual(entry["v12_signal_second"], 60)
        self.assertEqual(entry["v12_entry_authority"], "frozen_positive_cycle_clock")
        self.assertEqual(entry["v12_inherited_first_entry_family"], "UNKNOWN")
        self.assertEqual(len(first.rows), 2)
        self.assertEqual(len(first.rows[0]), len(FIRST_FEATURES))
        self.assertEqual(len(second.rows), 0)
        self.assertFalse(sim.concordance_summary()["future_trade_outcomes_available_to_router"])

    def test_frozen_two_second_entry_clock_uses_future_real_quote_only(self):
        sim = Micro180V12PositiveClock(
            cfg(), first_model=FixedModel(), second_model=FixedModel(),
            spec=V12PositiveClockSpec(first_execution_delay_seconds=2),
        )
        sim.on_tick(tick(0, 60, ms=15, bid=10000))
        self.assertEqual(len(sim.entries), 0)
        sim.on_tick(tick(1, 61, ms=23, bid=10010))
        self.assertEqual(len(sim.entries), 0)
        self.assertEqual(sim._pending[0], 60)
        sim.on_tick(tick(2, 62, ms=17, bid=10022))
        self.assertEqual(len(sim.entries), 1)
        self.assertEqual(sim.entries[0]["time_msc"], 62017)
        self.assertEqual(sim.entries[0]["price_u"], 10042)
        self.assertEqual(sim.entries[0]["v12_precommitted_delay_seconds"], 2)
        self.assertEqual(sim.entries[0]["v12_signal_second"], 60)

    def test_no_same_second_fill_or_stale_next_second_fill(self):
        sim = Micro180V12PositiveClock(cfg(), first_model=FixedModel(), second_model=FixedModel())
        sim.on_tick(tick(0, 60, ms=100))
        sim.on_tick(tick(1, 60, ms=400))
        self.assertEqual(len(sim.entries), 0)
        sim.on_tick(tick(2, 64, ms=15))
        self.assertEqual(len(sim.entries), 0)

    def test_new_minute_invalidates_old_intent(self):
        sim = Micro180V12PositiveClock(cfg(), first_model=FixedModel(), second_model=FixedModel())
        sim.on_tick(tick(0, 119, ms=700))
        sim.on_tick(tick(1, 120, ms=10))
        self.assertEqual(len(sim.entries), 0)
        self.assertEqual(sim.cycle_minute, 120)

    def test_completed_baskets_never_require_current_future_extrema(self):
        clock = CompletedMultiScaleClock()
        seq = [tick(i, s, ms=1, bid=10000 + s) for i, s in enumerate(range(100, 130))]
        for t in seq:
            clock.on_tick(t)
        r = clock.vector(seq[-1], 1, 250.0, False)
        self.assertEqual(len(r), len(FIRST_FEATURES))
        self.assertEqual(r[0], 9)
        self.assertEqual(r[1], 20)
        self.assertGreater(r[6], 0.9)
        self.assertGreater(r[12], 0)
        s = clock.vector(seq[-1], -1, 250.0, True)
        self.assertEqual(len(s), len(SECOND_FEATURES))
        self.assertLess(s[5], 0)
        self.assertEqual(s[-2], 0.0)

    def test_quote_stream_suffix_does_not_change_preceding_entry(self):
        a = Micro180V12PositiveClock(cfg(), first_model=FixedModel(), second_model=FixedModel())
        b = Micro180V12PositiveClock(cfg(), first_model=FixedModel(), second_model=FixedModel())
        for i,s in enumerate((60,61,62,63)):
            t=tick(i,s,bid=10000+i)
            a.on_tick(t);b.on_tick(t)
        expected=[dict(x) for x in a.entries]
        a.on_tick(tick(9,64,bid=10200))
        b.on_tick(tick(9,64,bid=9800))
        self.assertEqual(expected,a.entries[:len(expected)])
        self.assertEqual(expected,b.entries[:len(expected)])


class ChunkedOriginalREALSource(unittest.TestCase):
    def test_resume_uses_original_quote_rows_and_retains_single_inventory(self):
        from run_v12_positive_coinexx_chunks import run_one_batch
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            source=p/"existing_REAL_part01.csv.gz"
            fields=("run_label","time_msc","bid","ask","atr")
            rows=[
                ("REAL","60010","100.00","100.20","2.50"),
                ("REAL","61007","100.00","100.20","2.50"),
                ("REAL","62005","100.05","100.25","2.50"),
            ]
            with gzip.open(source,"wt",newline="") as f:
                writer=csv.writer(f);writer.writerow(fields);writer.writerows(rows)
            # FixedModel implements exactly the frozen-model score interface.
            sim=Micro180V12PositiveClock(cfg(),
                first_model=FixedModel(),second_model=FixedModel())
            dummy1=p/"frozen_first.txt";dummy2=p/"frozen_second.txt"
            dummy1.write_text("fixture");dummy2.write_text("fixture")
            work=p/"outputs"
            with patch(
                "run_v12_positive_coinexx_chunks._make_engine",
                return_value=sim,
            ):
                a=run_one_batch([source],dummy1,dummy2,work,1,resume=False)
            self.assertEqual(a["total_source_quotes"],1)
            self.assertEqual(a["total_entry_candidates"],0)
            b=run_one_batch([source],dummy1,dummy2,work,2,resume=True)
            self.assertEqual(b["total_source_quotes"],3)
            self.assertEqual(b["total_entry_candidates"],1)
            self.assertTrue(b["finished_all_parts"] is False or b["finished_all_parts"])
            path=work/"v12_independent_entries_chunk_00002.csv.gz"
            with gzip.open(path,"rt") as f:
                records=list(csv.DictReader(f))
            self.assertEqual(len(records),1)
            self.assertEqual(records[0]["entry_time_msc"],"61007")
            self.assertEqual(records[0]["executable_price_cents"],"10020")
            self.assertEqual(records[0]["source_quote_bid_ask"],"BUY_ASK")
            self.assertEqual(records[0]["original_R9_future_family_used"],"False")

    def test_SYNTH_log_is_never_accepted_as_REAL_Coinexx_quotes(self):
        from run_v12_positive_coinexx_chunks import run_one_batch
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            source=p/"source.csv.gz"
            with gzip.open(source,"wt",newline="") as f:
                writer=csv.writer(f)
                writer.writerow(["run_label","time_msc","bid","ask","atr"])
                writer.writerow(["SYNTH","60010","100.00","100.20","2.50"])
            first=p/"first.txt";second=p/"second.txt"
            first.write_text("fixture");second.write_text("fixture")
            with patch("run_v12_positive_coinexx_chunks._make_engine",
                       return_value=Micro180V12PositiveClock(
                           cfg(),first_model=FixedModel(),second_model=FixedModel())):
                with self.assertRaises(ValueError):
                    run_one_batch([source],first,second,p/"work",1,resume=False)


class PositiveSourceTargets(unittest.TestCase):
    def test_A_B_C_C_first_loss_positive_cycle_precursor(self):
        headers = ("entry_time_broker","leg","side","net_usd","quote_net",
                   "equote_ms","elag_ms","xlag_ms","q_entry_u")
        def record(minute, leg, net, quote, side):
            return {
                "entry_time_broker":f"2026-01-02 01:{minute:02d}:04",
                "leg":str(leg),"side":side,"net_usd":str(net),"quote_net":str(quote),
                "equote_ms":str(1767315605000 + minute * 60000),"elag_ms":"0",
                "xlag_ms":"0","q_entry_u":"432745",
            }
        rows=[
            record(0,1,1.1,0.8,"buy"),
            record(1,1,0.6,0.4,"buy"),record(1,2,0.7,0.3,"sell"),
            record(2,1,-0.5,-0.2,"sell"),record(2,2,1.6,1.1,"buy"),
            record(3,1,-0.3,0.2,"buy"),
        ]
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"existing.csv.gz"
            with gzip.open(path,"wt",newline="") as f:
                w=csv.DictWriter(f,fieldnames=headers);w.writeheader();w.writerows(rows)
            targets,summary=read_positive_targets(path)
        self.assertEqual(summary["original_rows"],6)
        self.assertEqual(summary["positive_complete_cycles_by_family"],{"A":1,"B":1,"C":1})
        self.assertEqual(summary["positive_first_leg_targets"],3)
        self.assertEqual(summary["positive_second_leg_targets"],2)
        self.assertEqual(summary["positive_target_legs"],5)
        self.assertTrue(summary["contains_C_initial_loss_as_recovery_precursor"])
        self.assertTrue(any(x.family=="C" and x.leg==1 and not x.positive_individual_exit for x in targets))


if __name__=="__main__":
    unittest.main()

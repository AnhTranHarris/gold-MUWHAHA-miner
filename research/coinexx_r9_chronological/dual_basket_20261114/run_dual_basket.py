"""One-pass R9 source-exact control versus four-lane dual-basket execution.

The nine-month Coinexx receipt and original .csv.gz remain READ-ONLY. No new
market data is generated. Full-month results require frozen original-trade parity.
This script has NOT established any profitable trading result.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for sub in ("src", "variable_cash_horizon_20261114",
            "dual_basket_20261114"):
    sys.path.insert(0, str(ROOT / sub))

from coinexx_r9.r9_baseline import R9Config, R9HybridGateBaseline
from coinexx_r9.ticks import iter_coinexx_ticks
from on_policy_cash_replay import ManagedR9, ResearchCash
from run_coinexx import (
    source_sha, summarize_original, verify_month, reuse_only_identical_market_context,
)
from dual_basket import DualBasketBaseline, DualBasketCash, DualBasketSpec


def summarize_dual(sim, cash):
    if isinstance(sim, DualBasketBaseline):
        r = summarize_original(sim, cash)
        r["target_ge_0_10"] = sum(
            (t.net_price_u / 100 * cash.k - cash.cost) >= .10 - 1e-9
            for t in sim.trades)
    else:
        r = sim.report()
    r["basket_5s_starts"] = sim.stats["basket_5s_starts"]
    r["basket_15s_starts"] = sim.stats["basket_15s_starts"]
    r["conflicts_wait"] = sim.stats["dual_conflicting_direction_wait"]
    r["cross_basket_rearms_blocked"] = sim.stats["dual_no_stale_cross_basket_rearm"]
    r["entries_per_source_minute_hard_cap"] = sim._cap()
    r["lane_confirmations"] = {
        f"{basket}s/{window}s": sim.stats[
            f"accepted_{basket}s_basket_{window}s_breakout"]
        for basket in (5, 15) for window in (15, 30)}
    return r


def research_run(args):
    cfg = R9Config()
    cash = ResearchCash(args.k, args.c, args.start_capital, args.governor)
    dual_spec = DualBasketSpec(
        minimum_mid_displacement_cents=args.mid_displacement_cents,
        max_entries_per_minute=args.max_entries_per_minute)
    original = R9HybridGateBaseline(cfg)
    governed_original = (ManagedR9(cfg, cash, "original") if args.governor else None)
    arms = {
        "dual_original_R9_exit": DualBasketBaseline(cfg, dual_spec),
        "dual_cash010_immediate_harvest": DualBasketCash(cfg, cash, False, dual_spec),
        "dual_cash010_protected_stretch175": DualBasketCash(cfg, cash, True, dual_spec),
    }
    peers = list(arms.values())
    if governed_original is not None:
        peers.append(governed_original)
    reuse_only_identical_market_context(original, *peers)

    result = {
        "classification": "RESEARCH_ONLY_QUOTE_SIDE_NOT_BROKER_FILLS",
        "owner_revision": "DUAL_5_15_BASKETS_DUAL_15_30_BREAKOUT_010_175",
        "entry": {
            "independent_basket_seconds": [5, 15],
            "completed_quote_breakout_seconds": [15, 30],
            "lane_combination": "same-side ANY, opposite-side conflicts WAIT",
            "minimum_midquote_displacement_cents": args.mid_displacement_cents,
            "max_entries_per_source_minute": min(
                args.max_entries_per_minute, cfg.max_same_minute_rearms + 1),
        },
        "exit": {
            "min_account_net": .10, "preferred_max_account_net": 1.75,
            "conservative_arm": "harvest on first observable net>=.10",
            "experimental_arm": "legally protect >=.10 before stretching toward 1.75",
            "original_R9_protective_stop_unchanged": True,
            "original_stricter_account_limits_unchanged": True,
        },
        "cash": {"k_unverified": cash.k, "extra_c_unverified": cash.cost,
                 "governor_approximation": cash.governor,
                 "initial_capital": cash.initial_capital},
        "no_155_feature_imputation": True,
        "no_tick_data_rebuild": True,
        "not_pristine_oos": True,
        "months": [],
        "arms": {},
    }
    start = 0
    offset = 0
    with zipfile.ZipFile(args.receipt) as z:
        receipt = json.loads(z.read("source_receipt.json"))
        for month in args.months:
            path = args.data / f"XAUUSD_MT5_BROKER_2026_{month}_ticks_ALL.csv.gz"
            got = source_sha(path)
            want = receipt["source_months"][month]["source_sha256"]
            if got != want:
                raise ValueError(f"Source SHA changed for {month}, STOP")
            count = 0
            t0 = time.monotonic()
            for tick in iter_coinexx_ticks(path, strict=True, ordinal_offset=offset):
                original.on_tick(tick)
                if governed_original is not None:
                    governed_original.on_tick(tick)
                for arm in arms.values():
                    arm.on_tick(tick)
                count += 1
                if args.max_rows and count >= args.max_rows:
                    break
            full = count == receipt["source_months"][month]["rows"]
            matched = verify_month(original, start, month, z, receipt) if full else None
            row = {
                "month": month, "rows": count, "source_sha": got,
                "original_full_ledger_parity": bool(full and matched is not None),
                "original_trade_count": len(original.trades) - start,
                "dual_trade_counts": {k: len(v.trades) for k, v in arms.items()},
                "elapsed_s": round(time.monotonic() - t0, 2),
            }
            result["months"].append(row)
            print("MONTH " + json.dumps(row, sort_keys=True), flush=True)
            start = len(original.trades)
            offset += count
            if not full:
                break

    # All aggregate financial statistics are exploratory, even with exact
    # original ledger parity. The broker deal/account economics are unverified.
    base = summarize_original(governed_original or original, cash)
    orig = summarize_original(original, cash)
    result["original_frozen_control"] = orig
    if governed_original is not None:
        result["same_governor_original_comparator"] = base
    result["arms"] = {}
    for name, arm in arms.items():
        r = summarize_dual(arm, cash)
        r["trade_retention_vs_same_governor"] = round(
            r["trades"] / base["trades"], 6) if base["trades"] else None
        r["net_delta_vs_same_governor"] = round(
            r["net_cash"] - base["net_cash"], 5)
        r["fraction_trades_net_ge_010"] = round(
            r["target_ge_0_10"] / r["trades"], 6) if r["trades"] else None
        r["fraction_trades_net_ge_175"] = round(
            r["target_ge_1_75"] / r["trades"], 6) if r["trades"] else None
        result["arms"][name] = r
    result["evaluation_complete"] = (
        len(result["months"]) == len(args.months) and
        all(r["original_full_ledger_parity"] for r in result["months"]))
    result["promoted_to_mt5"] = False
    result["broker_cost_contract_verified"] = False
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("FINAL " + json.dumps({
        "evaluation_complete": result["evaluation_complete"],
        "baseline": {"trades": base["trades"], "net": base["net_cash"]},
        "arms": {k: {"trades": v["trades"], "net": v["net_cash"],
                      "share_ge_010": v["fraction_trades_net_ge_010"]}
                 for k, v in result["arms"].items()},
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", type=Path, default=Path("/mnt/data"))
    p.add_argument("--receipt", type=Path, default=Path(
        "/mnt/data/R9_P1_Coinexx_9Month_SourceOrdinal_ASOF_CANDIDATE_CACHE_20261113.zip"))
    p.add_argument("--months", nargs="+", default=["01"])
    p.add_argument("--k", type=float, default=1.)
    p.add_argument("--c", type=float, default=.20)
    p.add_argument("--start-capital", type=float, default=100000.)
    p.add_argument("--mid-displacement-cents", type=int, default=10)
    p.add_argument("--max-entries-per-minute", type=int, default=4)
    p.add_argument("--governor", action="store_true")
    p.add_argument("--max-rows", type=int, default=0)
    p.add_argument("--output", type=Path, default=Path(
        "/mnt/data/R9_DUAL_5S15S_RESEARCH_SCORECARD.json"))
    research_run(p.parse_args())

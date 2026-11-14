"""One-pass ORIGINAL Coinexx tick stream, multiple independent R9 on-policy arms.

READS existing .csv.gz files directly. Writes a single small JSON receipt only
if explicitly requested. Never creates raw, bar, feature or tick duplicates.
Experiment is market-quote execution SCENARIO with explicit account cash K,C:
no real broker fills, multi-EA governor or production MQL5 modifications.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"account_cash_competing_risks"/"src"))
from coinexx_r9.r9_baseline import R9HybridGateBaseline,R9Config
from coinexx_r9.ticks import iter_coinexx_ticks
from cash_risk_overlay import CashAssumptions
from adaptive_policy import POLICIES,ExitPolicy,AdaptiveR9,summarize_account_cash


def source_sha256(path:Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as inp:
        for chunk in iter(lambda:inp.read(4*1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def run(args) -> dict:
    modes=tuple(args.policies)
    if len(set(modes))!=len(modes) or "baseline" not in modes:
        raise ValueError("Exactly one baseline control arm required; no duplicate modes")
    if "experimental_wide_stop" in modes and not args.allow_wider_initial_stop:
        raise ValueError("Wide initial stop is an explicit extra-risk research arm")
    if args.max_ticks<0:
        raise ValueError("max-ticks must be nonnegative")
    if args.expected_source_sha256 and len(args.expected_source_sha256)!=len(args.ticks):
        raise ValueError("Expected one original source SHA256 for each Coinexx gzip")
    cfg=(R9Config(**json.loads(args.config_json.read_text(encoding="utf-8")))
         if args.config_json else R9Config())
    cash=CashAssumptions(args.account_currency.upper(),
                         args.cash_per_one_xau_dollar,
                         args.round_trip_cost_cash,
                         max_hold_ms=cfg.max_hold_seconds*1000)
    # To avoid building separate tick engines: same exact Tick instance is
    # delivered to independent FULL original-R9 state machines in source order.
    models={m:(R9HybridGateBaseline(cfg) if m=="baseline"
               else AdaptiveR9(cfg,cash,ExitPolicy(mode=m,
                   alpha_spread=args.alpha_spread,
                   beta_noise=args.beta_noise,
                   m1_std_regime_weight=args.m1_std_weight,
                   m1_ema_trend_weight=args.m1_ema_weight,
                   activation_cash_buffer=args.activation_cash_buffer,
                   minimum_harvest_cash=args.minimum_harvest_cash,
                   maximum_initial_risk_cash=args.maximum_initial_risk_cash)))
            for m in modes}
    original_sources=[]
    row_count=0
    ordinal=0
    truncated=False
    for i,path in enumerate(args.ticks):
        if not path.is_file():
            raise FileNotFoundError(path)
        digest=(source_sha256(path) if args.expected_source_sha256 else None)
        if digest and digest.lower()!=args.expected_source_sha256[i].lower():
            raise ValueError(f"Source SHA256 mismatch: {path.name}")
        month_rows=0
        for tick in iter_coinexx_ticks(path,strict=True,ordinal_offset=ordinal):
            for policy in models.values():
                policy.on_tick(tick)
            row_count+=1
            month_rows+=1
            if args.max_ticks and row_count>=args.max_ticks:
                truncated=True
                break
        ordinal+=month_rows
        original_sources.append({
            "basename":path.name,"rows_used":month_rows,
            "source_sha256":digest,
            "source_sha256_verified":digest is not None,
        })
        if truncated:break
    stats={m:summarize_account_cash(s,cash) for m,s in models.items()}
    base=stats["baseline"]
    for m,one in stats.items():
        one["trade_retention_vs_baseline"]=(
            one["trades"]/base["trades"] if base["trades"] else None)
        one["whole_system_net_cash_delta_vs_baseline"]=(
            one["total_net_cash"]-base["total_net_cash"])
        one["average_cash_per_active_entry_hour"]=(
            one["total_net_cash"]/one["completed_entry_hour_cells"]
            if one["completed_entry_hour_cells"] else None)
    result={
        "classification":"COINEXX_ON_POLICY_QUOTE_SCENARIOS_NOT_MT5_EXECUTION_PNL",
        "source_rows":row_count,
        "source_receipts":original_sources,
        "truncated":truncated,
        "uses_exact_original_r9_baseline_engine":True,
        "independent_policy_reentry_and_occupancy":True,
        "source_clock_timezone":"UNVERIFIED_SOURCE_NATIVE",
        "cash_assumptions":asdict(cash),
        "r9_configuration":asdict(cfg),
        "trial_policy_parameters":{
            m:asdict(models[m].policy) for m in modes if m!="baseline"
        },
        "modeled":list(modes),
        "stats_by_policy":stats,
        "limitations":[
            "Only one R9 EA simulated; no account-wide cross-EA portfolio governor",
            "Broker fills/SL modification reject, fee/slippage draws and timer in quote gaps not observed",
            "Quote-side PnL converted with explicit externally calibrated K/C only",
            "Native M1 indicator historical parity, symbol quote timezone, and true out-of-sample not certified",
            "Historical Jan-Sep Coinexx source months already exposed in R9 research",
            "The prior high-AUC classifier is SHADOW only; no false cash hazard conversion",
            "Experimental initial-stop widening changes gross risk; do not promote without cap tests",
        ],
    }
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",
                               encoding="utf-8")
    return result


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--ticks",type=Path,nargs="+",required=True,
                   help="ORIGINAL Coinexx broker/ticklogger month .csv.gz, no conversion")
    a.add_argument("--expected-source-sha256",nargs="+",
                   help="Optional original pinned SHA256, one per original gzip")
    a.add_argument("--config-json",type=Path,help="Owner-approved R9 baseline parameters")
    a.add_argument("--account-currency",required=True)
    a.add_argument("--cash-per-one-xau-dollar",type=float,required=True,
                   help="MT5 OrderCalcProfit calibrated CASH per +1 XAUUSD quote at 0.01 lot")
    a.add_argument("--round-trip-cost-cash",type=float,required=True,
                   help="EXTRA full-trade commission/slippage, not already in Bid/Ask")
    a.add_argument("--policies",nargs="+",choices=POLICIES,
                   default=("baseline","cost_trail","staged_harvest"))
    a.add_argument("--allow-wider-initial-stop",action="store_true",
                   help="Explicit separate higher-risk research arm, NOT live")
    a.add_argument("--alpha-spread",type=float,default=.75)
    a.add_argument("--beta-noise",type=float,default=1.25)
    a.add_argument("--m1-std-weight",type=float,default=.20)
    a.add_argument("--m1-ema-weight",type=float,default=.10)
    a.add_argument("--activation-cash-buffer",type=float,default=.06)
    a.add_argument("--minimum-harvest-cash",type=float,default=.10)
    a.add_argument("--maximum-initial-risk-cash",type=float,default=1.5)
    a.add_argument("--max-ticks",type=int,default=0,
                   help="Optional bounded smoke sample; zero means FULL source")
    a.add_argument("--output",type=Path,help="Optional ONE compact JSON result")
    args=a.parse_args()
    output=run(args)
    print(json.dumps(output,indent=2,sort_keys=True))


if __name__=="__main__":
    main()

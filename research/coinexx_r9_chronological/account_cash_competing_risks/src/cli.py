"""Research CLI: original Coinexx quote stream -> small competing-risk evidence.

Default: stdout JSON summary ONLY. Optional per-trade CSV is small and requires
explicit --episodes-out; NO raw tick, second-bar, feature or model outputs.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, fields
import gzip
import hashlib
import json
import sys
from pathlib import Path

BASE_SRC = Path(__file__).resolve().parents[2] / "src"
sys.path.insert(0,str(BASE_SRC))

from coinexx_r9.r9_baseline import R9Config
from coinexx_r9.ticks import iter_coinexx_ticks
from cash_risk_overlay import CashAssumptions, Episode, R9CashRiskOverlay, summarize
from competing_hazards import fit_context_tables,evaluate_frozen_table


def file_sha256(path:Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for b in iter(lambda:fh.read(4*1024*1024),b""):
            h.update(b)
    return h.hexdigest()


def replay(args) -> None:
    if args.expected_source_sha256 and len(args.expected_source_sha256)!=len(args.ticks):
        raise ValueError("Supply one original source SHA256 for EVERY input month")
    cfg=(R9Config(**json.loads(args.r9_config.read_text(encoding="utf-8")))
         if args.r9_config else R9Config())
    cash=CashAssumptions(
        args.account_currency.upper(),args.cash_per_one_xau_dollar,
        args.round_trip_cost_cash,args.goal_net_cash,
        cfg.max_hold_seconds*1000,args.quote_gap_ms)
    sim=R9CashRiskOverlay(cash,cfg)
    source_receipts=[]
    source_rows=0
    prior_ordinal=0
    truncated=False
    for i,path in enumerate(args.ticks):
        if args.expected_source_sha256:
            sha=file_sha256(path)
            if sha!=args.expected_source_sha256[i]:
                raise ValueError(f"Original Coinexx compressed source hash mismatch: {path}")
        else:
            sha=None
        month_rows=0
        for t in iter_coinexx_ticks(path,strict=True,ordinal_offset=prior_ordinal):
            sim.on_tick(t)
            month_rows+=1
            source_rows+=1
            if args.max_ticks and source_rows>=args.max_ticks:
                truncated=True
                break
        prior_ordinal+=month_rows
        source_receipts.append({
            "source_file_name":path.name,
            "compressed_sha256":sha,
            "source_sha_verified":sha is not None,
            "rows_consumed":month_rows,
        })
        if truncated:
            break
    sim.finish()
    result={
        "classification":"EXACT_COINEXX_QUOTE_OVERLAY_NOT_ON_POLICY_ACCOUNT_BACKTEST",
        "research_basis":"unmodified chronological R9 v1.90 state machine",
        "r9_v194_ea": "UNCHANGED",
        "source_rows_processed":source_rows,
        "source_receipts":source_receipts,
        "simulation_truncated":truncated,
        "cash_assumptions":asdict(cash),
        "required_quote_side_favorable_price_cents":cash.required_favorable_cents,
        "r9_config":asdict(cfg),
        "summaries":summarize(sim.completed),
        "unmodeled":[
            "real broker fills/requotes/latency",
            "real trading fees/swaps if not covered by scenario cost",
            "MetaTrader tick callback coalescence",
            "v1.93/v1.94 account gross loss governor and margin",
            "early-target altered trade occupancy/re-arming",
            "live 155-feature model scoring and future OOS profitability",
        ],
    }
    if args.episodes_out:
        out=args.episodes_out
        out.parent.mkdir(parents=True,exist_ok=True)
        writer_open=(gzip.open if out.suffix==".gz" else open)
        with writer_open(out,"wt",newline="",encoding="utf-8") as fh:
            writer=csv.DictWriter(fh,fieldnames=[x.name for x in fields(Episode)])
            writer.writeheader()
            for episode in sim.completed:
                writer.writerow(episode.as_row())
        result["optional_episodes_out"]=str(out)
        result["optional_episode_rows"]=len(sim.completed)
    if args.summary_out:
        args.summary_out.parent.mkdir(parents=True,exist_ok=True)
        args.summary_out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))


def load_episode_file(path:Path) -> list[Episode]:
    def value(field,s):
        if s=="":
            return None
        if field in ("source_hour","session","side","entry_ordinal","entry_time_msc",
                     "entry_price_cents","entry_spread_cents","event_time_ms",
                     "exit_ordinal","exit_time_msc"):
            return int(s)
        if field in ("observed_goal_cash","baseline_net_cash","overlay_net_cash",
                     "max_favorable_net_cash","max_adverse_net_cash"):
            return float(s)
        return s
    result=[]
    op=(gzip.open if path.suffix==".gz" else open)
    with op(path,"rt",newline="",encoding="utf-8") as fh:
        r=csv.DictReader(fh)
        expected={x.name for x in fields(Episode)}
        if set(r.fieldnames or ())!=expected:
            raise ValueError("Episode schema mismatch: refuse silent repair")
        for row in r:
            e=Episode(**{key:value(key,v) for key,v in row.items()})
            result.append(e)
    return result


def train_evaluate(args) -> None:
    if set(args.train_episodes) & set(args.test_episodes):
        raise ValueError("Train and evaluation ledger files overlap")
    train=[]
    evaluate=[]
    for path in args.train_episodes:
        train.extend(load_episode_file(path))
    for path in args.test_episodes:
        evaluate.extend(load_episode_file(path))
    if not train or not evaluate:
        raise ValueError("Both chronological train and evaluation cohorts required")
    latest_train=max(x.entry_time_msc for x in train)
    earliest_test=min(x.entry_time_msc for x in evaluate)
    if latest_train>=earliest_test:
        raise ValueError("Train must END strictly before test begins; no future training leakage")
    table=fit_context_tables(train,by=args.by,
                             min_group_count=args.min_group_count,
                             risk_lambda=args.cvar_penalty,
                             max_censor_fraction=args.max_censor_fraction)
    out={
        "classification":"RETROSPECTIVE_DEVELOPMENT_EXPOSED_NOT_PRISTINE_OOS",
        "train_first_msc":min(x.entry_time_msc for x in train),
        "train_last_msc":latest_train,
        "test_first_msc":earliest_test,
        "test_last_msc":max(x.entry_time_msc for x in evaluate),
        "trained_incidence_and_cash_utility":table,
        "chronological_test_summary":evaluate_frozen_table(table,evaluate),
        "policy":"NO EA MODIFICATION, NO NEW TRAINED LIGHTGBM, NO ON_POLICY PAYOFF CLAIM",
    }
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    sub=ap.add_subparsers(dest="command",required=True)
    r=sub.add_parser("replay",help="Stream existing Coinexx months, no new raw caches")
    r.add_argument("--ticks",type=Path,nargs="+",required=True)
    r.add_argument("--expected-source-sha256",nargs="+",
                   help="optional original compressed hashes, one for each month")
    r.add_argument("--r9-config",type=Path,
                   help="original pinned R9 configuration JSON, defaults to repository baseline")
    r.add_argument("--account-currency",required=True,
                   help="MT5 account currency (e.g., USD); NOT assumed from ticklogger")
    r.add_argument("--cash-per-one-xau-dollar",type=float,required=True,
                   help="broker-calibrated account cash PnL per $1 XAU movement at configured lot")
    r.add_argument("--round-trip-cost-cash",type=float,required=True,
                   help="explicit scenario commission + slippage cost for whole position")
    r.add_argument("--goal-net-cash",type=float,default=1.75)
    r.add_argument("--quote-gap-ms",type=int,default=10000)
    r.add_argument("--max-ticks",type=int,default=0,
                   help="optional smoke cap; truncation and EOF censor reported; 0 means all")
    r.add_argument("--episodes-out",type=Path,
                   help="OPTIONAL small per-trade evidence CSV or CSV.GZ; no default file")
    r.add_argument("--summary-out",type=Path,
                   help="OPTIONAL small result JSON; default stdout only")
    r.set_defaults(func=replay)
    f=sub.add_parser("fit-evaluate",
                     help="training-month Aalen-Johansen incidence against later month ledgers")
    f.add_argument("--train-episodes",type=Path,nargs="+",required=True)
    f.add_argument("--test-episodes",type=Path,nargs="+",required=True)
    f.add_argument("--by",choices=["global","session","session_spread","hour"],
                   default="session_spread")
    f.add_argument("--min-group-count",type=int,default=100)
    f.add_argument("--cvar-penalty",type=float,default=0.25)
    f.add_argument("--max-censor-fraction",type=float,default=0.10,
                   help="abstain from training context if gap/EOF censoring exceeds this")
    f.add_argument("--out",type=Path,help="OPTIONAL small model receipt JSON")
    f.set_defaults(func=train_evaluate)
    args=ap.parse_args()
    if args.command=="replay" and args.max_ticks<0:
        ap.error("--max-ticks must be zero or positive")
    args.func(args)


if __name__=="__main__":
    main()

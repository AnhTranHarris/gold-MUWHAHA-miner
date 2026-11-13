from __future__ import annotations
import argparse
import json
from pathlib import Path
from .bars import iter_second_bars
from .engine import ChronologicalEngine
from .io import sha256_file, write_json, write_second_bars, write_trades
from .mt5_report import extract_trade_sections
from .r9_baseline import R9Config, R9HybridGateBaseline
from .ticks import iter_coinexx_ticks, verify_coinexx_tick_file


def _load_config(path: str | None) -> R9Config:
    if path is None:
        return R9Config()
    return R9Config(**json.loads(Path(path).read_text(encoding="utf-8")))


def cmd_verify(args: argparse.Namespace) -> None:
    v = verify_coinexx_tick_file(args.ticks, strict=True)
    print(json.dumps({
        "schema": v.schema,
        "sha256": sha256_file(args.ticks),
        "rows": v.rows,
        "first_time_msc": v.first_time_msc,
        "last_time_msc": v.last_time_msc,
        "same_millisecond_adjacent_rows": v.same_millisecond_adjacent_rows,
        "status": "strict_chronology_pass",
    }, indent=2))


def cmd_seconds(args: argparse.Namespace) -> None:
    ticks=iter_coinexx_ticks(args.ticks, strict=True)
    count=write_second_bars(args.out,iter_second_bars(ticks))
    print(json.dumps({"bars_written":count,"out":args.out,"source_sha256":sha256_file(args.ticks)},indent=2))


def cmd_replay(args: argparse.Namespace) -> None:
    cfg=_load_config(args.config)
    strategy=R9HybridGateBaseline(cfg)
    eng=ChronologicalEngine(strategy)
    eng.run(iter_coinexx_ticks(args.ticks, strict=True))
    trade_count=write_trades(args.trades_out,strategy.trades)
    receipt={
        "source_sha256":sha256_file(args.ticks),
        "ticks_processed":eng.ticks_processed,
        "first_time_msc":eng.first_time_msc,
        "last_time_msc":eng.last_time_msc,
        "entries":len(strategy.entries),
        "closed_trades":trade_count,
        "open_position_at_eof":strategy.position is not None,
        "config":strategy.config_dict(),
        "stats":dict(strategy.stats),
        "note":"Metadata receipt only; full tick source and full trade ledger remain authoritative.",
    }
    if args.receipt_out:write_json(args.receipt_out,receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k not in ("config","stats")},indent=2))


def cmd_extract_report(args: argparse.Namespace) -> None:
    oc,dc=extract_trade_sections(args.report,args.orders_out,args.deals_out)
    print(json.dumps({"orders_rows_written":oc,"deals_rows_written":dc,"report_sha256":sha256_file(args.report)},indent=2))


def build_parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(prog="coinexx-r9")
    sub=p.add_subparsers(dest="command",required=True)
    v=sub.add_parser("verify-ticks");v.add_argument("ticks");v.set_defaults(func=cmd_verify)
    s=sub.add_parser("emit-seconds");s.add_argument("ticks");s.add_argument("--out",required=True);s.set_defaults(func=cmd_seconds)
    r=sub.add_parser("replay-r9");r.add_argument("ticks");r.add_argument("--config");r.add_argument("--trades-out",required=True);r.add_argument("--receipt-out");r.set_defaults(func=cmd_replay)
    x=sub.add_parser("extract-mt5");x.add_argument("report");x.add_argument("--orders-out",required=True);x.add_argument("--deals-out",required=True);x.set_defaults(func=cmd_extract_report)
    return p


def main() -> None:
    a=build_parser().parse_args();a.func(a)

if __name__=="__main__":main()

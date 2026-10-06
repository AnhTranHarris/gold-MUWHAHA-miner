#!/usr/bin/env python3
"""Extract a compact monthly benchmark from an MT5 Strategy Tester XLSX report.

Designed for large MT5 report workbooks without loading the workbook into Excel/pandas.
Uses only Python stdlib, streams XLSX XML, and preserves MT5 deal-accounting parity.

Output metrics:
- tester-account net/gross profit/gross loss/PF from deal cashflows;
- closed trade count and winning trades from completed positions;
- balance max drawdown from exact deal balance sequence;
- trade velocity (closed trades per active trading day);
- holding-time survivability at selected horizons.

This helper is research infrastructure, not a trading strategy.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import re
import statistics
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

SI_RE = re.compile(r"<si><t(?: [^>]*)?>(.*?)</t></si>")
ROW_RE = re.compile(r'<row r="(\\d+)"')
CELL_RE = re.compile(r'<c r="([A-Z]+)\\d+"([^>]*)>(?:<v>(.*?)</v>)?</c>')
TIMESTAMP_RE = re.compile(r"^\\d{4}\\.\\d{2}\\.\\d{2} \\d{2}:\\d{2}:\\d{2}$")
TIME_FMT = "%Y.%m.%d %H:%M:%S"
SURVIVAL_HORIZONS = (1, 5, 10, 15, 20, 30)


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def load_relevant_shared_strings(zf: zipfile.ZipFile) -> dict[int, str]:
    """Map only timestamps and control tokens needed for the deal ledger."""
    relevant: dict[int, str] = {}
    with zf.open("xl/sharedStrings.xml") as raw:
        text = io.TextIOWrapper(raw, encoding="utf-16")
        idx = 0
        for line in text:
            m = SI_RE.search(line)
            if not m:
                continue
            value = html.unescape(m.group(1))
            if TIMESTAMP_RE.match(value) or value in {"Deals", "balance", "in", "out"}:
                relevant[idx] = value
            idx += 1
    return relevant


def new_bucket() -> dict[str, Any]:
    return {
        "deal_net": 0.0,
        "gross_profit": 0.0,
        "gross_loss": 0.0,
        "trades": 0,
        "wins": 0,
        "holds": [],
        "days": set(),
        "peak_balance": None,
        "max_balance_drawdown": 0.0,
        "start_balance": None,
        "end_balance": None,
    }


def update_balance(bucket: dict[str, Any], balance: float, prior_balance: float | None) -> None:
    if bucket["start_balance"] is None:
        bucket["start_balance"] = prior_balance if prior_balance is not None else balance
        bucket["peak_balance"] = bucket["start_balance"]
    bucket["peak_balance"] = max(bucket["peak_balance"], balance)
    bucket["max_balance_drawdown"] = max(
        bucket["max_balance_drawdown"], bucket["peak_balance"] - balance
    )
    bucket["end_balance"] = balance


def finalize(bucket: dict[str, Any]) -> dict[str, Any]:
    trades = int(bucket["trades"])
    holds = list(bucket["holds"])
    gl = float(bucket["gross_loss"])
    gp = float(bucket["gross_profit"])
    net = float(bucket["deal_net"])

    def survive(seconds: int) -> float | None:
        if not holds:
            return None
        return 100.0 * sum(h >= seconds for h in holds) / len(holds)

    return {
        "trades": trades,
        "wins": int(bucket["wins"]),
        "win_rate_pct": (100.0 * bucket["wins"] / trades) if trades else None,
        "net_profit": net,
        "gross_profit": gp,
        "gross_loss": gl,
        "profit_factor": (gp / abs(gl)) if gl else None,
        "expected_payoff": (net / trades) if trades else None,
        "balance_max_drawdown": float(bucket["max_balance_drawdown"]),
        "active_trading_days": len(bucket["days"]),
        "trades_per_active_day": (trades / len(bucket["days"])) if bucket["days"] else None,
        "average_hold_seconds": (sum(holds) / len(holds)) if holds else None,
        "median_hold_seconds": statistics.median(holds) if holds else None,
        "survival_pct": {str(s): survive(s) for s in SURVIVAL_HORIZONS},
        "start_balance": bucket["start_balance"],
        "end_balance": bucket["end_balance"],
    }


def extract(path: Path, label: str) -> dict[str, Any]:
    monthly: dict[str, dict[str, Any]] = defaultdict(new_bucket)
    aggregate = new_bucket()
    open_trade: dict[str, Any] | None = None
    prior_balance: float | None = None
    in_deals = False
    row: dict[str, Any] = {}

    with zipfile.ZipFile(path) as zf:
        strings = load_relevant_shared_strings(zf)
        with zf.open("xl/worksheets/sheet1.xml") as raw:
            text = io.TextIOWrapper(raw, encoding="utf-16")
            for line in text:
                if ROW_RE.search(line):
                    row = {}
                    continue

                cm = CELL_RE.search(line)
                if cm:
                    col, attrs, raw_value = cm.groups()
                    if raw_value is None:
                        row[col] = ""
                    elif 't="s"' in attrs:
                        row[col] = strings.get(int(raw_value), "")
                    else:
                        row[col] = raw_value
                    continue

                if "</row>" not in line:
                    continue

                if row.get("A") == "Deals":
                    in_deals = True
                    row = {}
                    continue
                if not in_deals:
                    row = {}
                    continue

                ts_text = row.get("A", "")
                if not TIMESTAMP_RE.match(ts_text):
                    row = {}
                    continue
                ts = datetime.strptime(ts_text, TIME_FMT)
                month = ts.strftime("%Y-%m")
                bucket = monthly[month]

                commission = float(row.get("I") or 0.0)
                swap = float(row.get("J") or 0.0)
                profit = float(row.get("K") or 0.0)
                balance = float(row.get("L") or prior_balance or 0.0)
                direction = row.get("E", "")
                deal_type = row.get("D", "")

                if deal_type == "balance":
                    prior_balance = balance
                    aggregate["start_balance"] = balance
                    aggregate["peak_balance"] = balance
                    row = {}
                    continue

                cashflow = commission + swap + profit
                for b in (bucket, aggregate):
                    b["deal_net"] += cashflow
                    if cashflow > 0:
                        b["gross_profit"] += cashflow
                    elif cashflow < 0:
                        b["gross_loss"] += cashflow
                    update_balance(b, balance, prior_balance)
                prior_balance = balance

                if direction == "in":
                    open_trade = {"time": ts, "swap": swap}
                elif direction == "out":
                    entry_time = open_trade["time"] if open_trade else ts
                    entry_swap = open_trade["swap"] if open_trade else 0.0
                    hold = (ts - entry_time).total_seconds()
                    winner_basis = profit + swap + entry_swap
                    for b in (bucket, aggregate):
                        b["trades"] += 1
                        b["wins"] += int(winner_basis > 0)
                        b["holds"].append(hold)
                        b["days"].add(ts.date())
                    open_trade = None

                row = {}

    return {
        "schema": "delta-a-alpha-r9-benchmark-v1",
        "label": label,
        "source_file": path.name,
        "source_sha256": sha256_file(path),
        "accounting": {
            "net_and_gross": "exact MT5 deal cashflows: commission + swap + profit",
            "winning_trade": "completed-position price profit + swap > 0; commission excluded for tester parity",
            "balance_drawdown": "exact deal-balance sequence",
            "survivability": "percentage of completed positions with holding time >= horizon seconds",
        },
        "aggregate": finalize(aggregate),
        "monthly": {m: finalize(monthly[m]) for m in sorted(monthly)},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("xlsx", type=Path)
    ap.add_argument("--label", required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    result = extract(args.xlsx, args.label)
    payload = json.dumps(result, indent=2, sort_keys=False)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()

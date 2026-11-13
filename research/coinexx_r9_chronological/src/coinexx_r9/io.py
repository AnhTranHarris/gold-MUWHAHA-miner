from __future__ import annotations
import csv
import gzip
import hashlib
import json
from pathlib import Path
from typing import Iterable
from .models import SecondBar, Trade, format_price_units


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_second_bars(path: str | Path, bars: Iterable[SecondBar]) -> int:
    p = Path(path)
    opener = gzip.open if p.suffix.lower() == ".gz" else open
    fields = [
        "second","first_time_msc","last_time_msc","tick_count",
        "bid_open","bid_high","bid_low","bid_close",
        "ask_open","ask_high","ask_low","ask_close",
        "spread_open_points","spread_high_points","spread_low_points","spread_close_points",
    ]
    n = 0
    with opener(p, "wt", newline="", encoding="utf-8") as f:  # type: ignore[arg-type]
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for b in bars:
            w.writerow({
                "second":b.second,"first_time_msc":b.first_time_msc,"last_time_msc":b.last_time_msc,"tick_count":b.tick_count,
                "bid_open":format_price_units(b.bid_open_u),"bid_high":format_price_units(b.bid_high_u),"bid_low":format_price_units(b.bid_low_u),"bid_close":format_price_units(b.bid_close_u),
                "ask_open":format_price_units(b.ask_open_u),"ask_high":format_price_units(b.ask_high_u),"ask_low":format_price_units(b.ask_low_u),"ask_close":format_price_units(b.ask_close_u),
                "spread_open_points":b.spread_open,"spread_high_points":b.spread_high,"spread_low_points":b.spread_low,"spread_close_points":b.spread_close,
            })
            n += 1
    return n


def write_trades(path: str | Path, trades: Iterable[Trade]) -> int:
    fields = [
        "entry_ordinal","entry_time_msc","side","entry_price","initial_sl",
        "exit_ordinal","exit_time_msc","exit_price","reason","net_price","rearm_number",
    ]
    n = 0
    with Path(path).open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for t in trades:
            w.writerow({
                "entry_ordinal":t.entry_ordinal,"entry_time_msc":t.entry_time_msc,"side":t.side,
                "entry_price":format_price_units(t.entry_price_u),"initial_sl":format_price_units(t.initial_sl_u),
                "exit_ordinal":t.exit_ordinal,"exit_time_msc":t.exit_time_msc,"exit_price":format_price_units(t.exit_price_u),
                "reason":t.reason,"net_price":format_price_units(t.net_price_u),"rearm_number":t.rearm_number,
            });n+=1
    return n


def write_json(path: str | Path, payload: dict) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

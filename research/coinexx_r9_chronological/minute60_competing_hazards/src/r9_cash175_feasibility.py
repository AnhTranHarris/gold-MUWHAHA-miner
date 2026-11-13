"""Coinexx-only, source-ordinal R9 net-cash-target reachability research.

THIN ADAPTER: reuses existing event_engine.first_passage_actions, the preexisting
monthly frozen entry ordinal cache, and preverified original source receipts.
No fresh tick engine, no feature cache, no saved per-trade files.
This is a STATIC-STOP first-passage scenario, NOT exact R9 trailing-stop replay
and NOT account P&L or a tradable classifier.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from event_engine import first_passage_actions


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def target_units(net_target_cash: float, cost_cash: float,
                 account_cash_per_xau_price_dollar: float) -> int:
    """Cent-XAU move from already-paid quote-side fill to opposite quote-side exit."""
    if not (net_target_cash > 0 and cost_cash >= 0
            and account_cash_per_xau_price_dollar > 0):
        raise ValueError("Positive net target and contract cash value required; cost cannot be negative")
    return int(math.ceil((net_target_cash + cost_cash) * 100
                         / account_cash_per_xau_price_dollar - 1e-10))


def evaluate(t: np.ndarray, bid: np.ndarray, ask: np.ndarray,
             entry_ix: np.ndarray, original_side: np.ndarray,
             stop_cents: int, target_cents: int,
             horizon_ms: int = 30000) -> dict:
    """Call ONLY the established exact-ordinal first-passage engine.

    Stop from original requested bid/ask initial stop geometry:
      initial BUY SL = bid_at_entry - stop_cents
      initial SELL SL = ask_at_entry + stop_cents
    Hence adverse move from filled Ask/Bid is spread + stop_cents.
    Real broker min stops, fill slippage and trailing moves are NOT represented.
    """
    t = np.asarray(t, dtype=np.int64)
    bid = np.asarray(bid, dtype=np.int32)
    ask = np.asarray(ask, dtype=np.int32)
    entry_ix = np.asarray(entry_ix, dtype=np.int64)
    original_side = np.asarray(original_side, dtype=np.int32)
    if not (len(t) == len(bid) == len(ask)):
        raise ValueError("Tick columns must have equal lengths")
    if len(t) == 0 or np.any(np.diff(t) < 0) or np.any(ask < bid):
        raise ValueError("Invalid source chronology or inverted spread")
    if np.any(bid <= 0) or np.any(ask <= 0):
        raise ValueError("Invalid quote values")
    if len(entry_ix) != len(original_side) or np.any((entry_ix < 0) | (entry_ix >= len(t))):
        raise ValueError("Invalid frozen entry ordinals")
    if np.any((original_side != 1) & (original_side != -1)):
        raise ValueError("Frozen original R9 side must be +/-1")
    if stop_cents <= 0 or target_cents <= 0 or horizon_ms <= 0:
        raise ValueError("Positive stop, target and horizon required")

    spreads = (ask[entry_ix] - bid[entry_ix]).astype(np.int32)
    stop = spreads + int(stop_cents)
    target = np.full(len(entry_ix),target_cents,dtype=np.int32)
    cause, hit_ms, _ = first_passage_actions(
        t, bid, ask, entry_ix, stop, target, horizon_ms
    )
    selected = np.where(original_side > 0, 0, 1)
    idx = np.arange(len(entry_ix))
    result = cause[idx, selected]
    hit = hit_ms[idx, selected]
    def frac(v: int) -> float | None:
        return None if len(entry_ix) == 0 else float(v / len(entry_ix))
    event_times = hit[(result == 1) & (hit >= 0)]
    return {
        "original_r9_candidates": int(len(entry_ix)),
        "target_first_count": int(np.sum(result == 1)),
        "stop_first_count": int(np.sum(result == 2)),
        "no_event_count": int(np.sum(result == 0)),
        "censored_count": int(np.sum(result == -1)),
        "target_first_fraction_all_candidates": frac(int(np.sum(result == 1))),
        "median_target_hit_seconds": (None if len(event_times) == 0
                                     else float(np.median(event_times) / 1000.0)),
        "hypothetical_stop_quote_cents_at_entry": {
            "min": None if not len(stop) else int(np.min(stop)),
            "median": None if not len(stop) else float(np.median(stop)),
            "max": None if not len(stop) else int(np.max(stop)),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True,
                        help="Original unchanged Coinexx monthly .csv.gz with time_msc,bid,ask")
    parser.add_argument("--frozen", type=Path, required=True,
                        help="Existing full_month_2026_MM.npz, DO NOT rebuild")
    parser.add_argument("--receipt", type=Path, required=True,
                        help="Existing original source_receipt.json")
    parser.add_argument("--month", choices=[f"{i:02}" for i in range(1, 10)], required=True)
    parser.add_argument("--account-cash-per-xau-price-dollar", type=float, required=True,
                        help="Broker-verified cash P&L for a $1 XAU quote move at FIXED volume, not assumed")
    parser.add_argument("--net-target-account-cash", type=float, default=1.75)
    parser.add_argument("--scenario-cost-account-cash", type=float, required=True,
                        help="Explicit roundtrip commission/slippage charge, not contained in ticklogger")
    parser.add_argument("--stop-xau-price", type=float, default=0.30)
    parser.add_argument("--horizon-ms", type=int, default=30000)
    parser.add_argument("--skip-source-sha", action="store_true",
                        help="EXPEDIENT but weakens source-integrity audit; chronology still checked")
    a = parser.parse_args()

    receipt = json.loads(a.receipt.read_text())
    source = receipt["source_months"][a.month]
    if not a.skip_source_sha and sha256_file(a.raw) != source["source_sha256"]:
        raise ValueError("Original Coinexx monthly file hash mismatch; cannot reuse frozen ordinals")
    source_start = sum(int(receipt["source_months"][f"{i:02}"]["rows"])
                       for i in range(1, int(a.month)))
    # Read only existing market columns; no cache or emitted full tick data.
    df = pd.read_csv(a.raw, usecols=["time_msc", "bid", "ask"],
                     dtype={"time_msc": "int64", "bid": "float64", "ask": "float64"})
    if len(df) != int(source["rows"]):
        raise ValueError("Raw market row count does not match pinned receipt")
    times = df["time_msc"].to_numpy(np.int64, copy=True)
    bids = np.rint(df["bid"].to_numpy(copy=True) * 100).astype(np.int32)
    asks = np.rint(df["ask"].to_numpy(copy=True) * 100).astype(np.int32)
    del df
    with np.load(a.frozen, allow_pickle=False) as frozen:
        original_ord = frozen["entry_ordinals"]
        entry_ix = (original_ord - source_start - 1).astype(np.int64)
        expected_time = frozen["entry_times"]
        original_side = frozen["side"]
    if np.any(entry_ix < 0) or np.any(entry_ix >= len(times)):
        raise ValueError("Frozen global ordinals are outside this monthly source")
    if not np.array_equal(times[entry_ix], expected_time):
        raise ValueError("Frozen entry timestamp/ordinal parity FAILED")
    target_cents = target_units(a.net_target_account_cash,
                               a.scenario_cost_account_cash,
                               a.account_cash_per_xau_price_dollar)
    stop_cents = int(round(100.0 * a.stop_xau_price))
    out = evaluate(times,bids,asks,entry_ix,original_side,
                   stop_cents,target_cents,a.horizon_ms)
    out.update({
        "month": a.month,
        "source_rows": int(len(times)),
        "static_stop_quote_cents": stop_cents,
        "required_favorable_quote_cents": target_cents,
        "net_target_account_cash": a.net_target_account_cash,
        "scenario_cost_account_cash": a.scenario_cost_account_cash,
        "account_cash_per_xau_price_dollar": a.account_cash_per_xau_price_dollar,
        "horizon_ms": a.horizon_ms,
        "original_source_sha_verified": not a.skip_source_sha,
        "classification": "RESEARCH_STATIC_STOP_QUOTE_SIDE_SCENARIO_NOT_ACTUAL_R9_EXITS_OR_LIVE_PNL",
        "caveats": [
            "No R9 dynamic trailing stop, broker min stop, order fills, slippage draws or account occupancy",
            "Contract cash value and execution charge externally provided; ticklogger cannot prove them",
            "No profitable strategy or deployment certification, no new model training",
            "Existing Jan-Sep months have already been used for development research",
        ],
    })
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__ == "__main__":
    main()

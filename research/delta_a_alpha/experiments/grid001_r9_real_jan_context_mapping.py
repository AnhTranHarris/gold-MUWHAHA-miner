from __future__ import annotations

import argparse
import html
import io
import json
import re
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from grid001_january_event_label_lab import load, materialize, PRICE_SCALE
from grid001_january_early_thesis_failure import m1_atr_gap, gen_events
from grid001_january_nested_trend_phase import state_age_series, map_state

SI_RE = re.compile(r"<si><t(?: [^>]*)?>(.*?)</t></si>")
CELL_RE = re.compile(r'<c r="([A-Z]+)\\d+"([^>]*)>(?:<v>(.*?)</v>)?</c>')
TS_RE = re.compile(r"^2026\\.01\\.\\d{2} \\d{2}:\\d{2}:\\d{2}$")
TIME_FMT = "%Y.%m.%d %H:%M:%S"
OFFSET_CANDIDATES = tuple(range(-12, 15))


def extract_trades(report: Path):
    relevant = {}
    with zipfile.ZipFile(report) as zf:
        with zf.open("xl/sharedStrings.xml") as raw:
            text = io.TextIOWrapper(raw, encoding="utf-16")
            idx = 0
            for line in text:
                m = SI_RE.search(line)
                if not m:
                    continue
                value = html.unescape(m.group(1))
                if TS_RE.match(value) or value in {"Deals", "buy", "sell", "in", "out", "balance"}:
                    relevant[idx] = value
                idx += 1

        trades = []
        row = {}
        in_deals = False
        current = None

        with zf.open("xl/worksheets/sheet1.xml") as raw:
            text = io.TextIOWrapper(raw, encoding="utf-16")
            for line in text:
                if "<row r=" in line:
                    row = {}
                    continue

                m = CELL_RE.search(line)
                if m:
                    col, attrs, raw_value = m.groups()
                    if raw_value is None:
                        row[col] = ""
                    elif 't="s"' in attrs:
                        row[col] = relevant.get(int(raw_value), "")
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

                ts = row.get("A", "")
                if not TS_RE.match(ts):
                    row = {}
                    continue

                deal_type = row.get("D", "")
                direction = row.get("E", "")

                if direction == "in" and deal_type in ("buy", "sell"):
                    current = {
                        "entry_report_time": ts,
                        "side": 1 if deal_type == "buy" else -1,
                        "entry_price": float(row.get("G") or 0.0),
                        "entry_commission": float(row.get("I") or 0.0),
                        "entry_swap": float(row.get("J") or 0.0),
                    }

                elif direction == "out" and current is not None:
                    current.update(
                        {
                            "exit_report_time": ts,
                            "exit_price": float(row.get("G") or 0.0),
                            "exit_commission": float(row.get("I") or 0.0),
                            "exit_swap": float(row.get("J") or 0.0),
                            "price_profit": float(row.get("K") or 0.0),
                        }
                    )
                    current["net_cashflow"] = (
                        current["entry_commission"]
                        + current["exit_commission"]
                        + current["entry_swap"]
                        + current["exit_swap"]
                        + current["price_profit"]
                    )
                    entry_dt = datetime.strptime(current["entry_report_time"], TIME_FMT)
                    exit_dt = datetime.strptime(current["exit_report_time"], TIME_FMT)
                    current["hold_seconds"] = (exit_dt - entry_dt).total_seconds()
                    trades.append(current)
                    current = None

                row = {}

    return trades


def report_ms_naive(value: str) -> int:
    dt = datetime.strptime(value, TIME_FMT).replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def infer_report_offset(t, ask, bid, trades):
    side = np.array([x["side"] for x in trades], np.int8)
    report_price = np.array([x["entry_price"] for x in trades], float)
    naive_ms = np.array([report_ms_naive(x["entry_report_time"]) for x in trades], np.int64)

    rows = []
    for offset_hours in OFFSET_CANDIDATES:
        shifted = naive_ms - offset_hours * 3_600_000
        idx = nearest_tick_indices(t, shifted)
        mapped_quote = np.where(side > 0, ask[idx], bid[idx]) / PRICE_SCALE
        price_error = np.abs(mapped_quote - report_price)
        time_error = np.abs(t[idx] - shifted)
        rows.append(
            {
                "offset_hours": int(offset_hours),
                "median_abs_price_error": float(np.median(price_error)),
                "p75_abs_price_error": float(np.quantile(price_error, 0.75)),
                "p90_abs_price_error": float(np.quantile(price_error, 0.90)),
                "mean_abs_price_error": float(price_error.mean()),
                "within_0_25usd_pct": float(100 * np.mean(price_error <= 0.25)),
                "within_0_50usd_pct": float(100 * np.mean(price_error <= 0.50)),
                "within_1usd_pct": float(100 * np.mean(price_error <= 1.0)),
                "median_tick_time_error_ms": float(np.median(time_error)),
                "p90_tick_time_error_ms": float(np.quantile(time_error, 0.90)),
            }
        )

    ranking = sorted(
        rows,
        key=lambda x: (
            x["median_abs_price_error"],
            x["p90_abs_price_error"],
            x["mean_abs_price_error"],
        ),
    )
    return naive_ms, rows, ranking


def nearest_tick_indices(t, timestamps_ms):
    out = np.empty(len(timestamps_ms), np.int64)
    for i, ms in enumerate(timestamps_ms):
        j = np.searchsorted(t, ms)
        if j <= 0:
            out[i] = 0
        elif j >= len(t):
            out[i] = len(t) - 1
        else:
            out[i] = j if abs(int(t[j]) - int(ms)) < abs(int(t[j - 1]) - int(ms)) else j - 1
    return out


def minute_vol_ratio(t, bid, query_idx):
    bucket = t // 60_000
    starts = np.r_[0, np.flatnonzero(bucket[1:] != bucket[:-1]) + 1]
    ends = np.r_[starts[1:] - 1, len(t) - 1]
    hi = np.maximum.reduceat(bid, starts).astype(np.int64)
    lo = np.minimum.reduceat(bid, starts).astype(np.int64)
    cl = bid[ends].astype(np.int64)
    prev = np.r_[cl[0], cl[:-1]]
    tr = np.maximum(hi - lo, np.maximum(np.abs(hi - prev), np.abs(lo - prev))).astype(float)

    cs = np.r_[0.0, np.cumsum(tr)]
    atr14 = np.full(len(tr), np.nan)
    atr240 = np.full(len(tr), np.nan)

    for k in range(14, len(tr)):
        atr14[k] = (cs[k] - cs[k - 14]) / 14.0
    for k in range(240, len(tr)):
        atr240[k] = (cs[k] - cs[k - 240]) / 240.0

    ratio = np.divide(
        atr14,
        atr240,
        out=np.full(len(tr), np.nan),
        where=np.isfinite(atr14) & np.isfinite(atr240) & (atr240 > 0),
    )

    minute_ids = bucket[starts]
    query_minutes = t[query_idx] // 60_000
    bi = np.searchsorted(minute_ids, query_minutes, side="left") - 1
    out = np.full(len(query_idx), np.nan)
    ok = bi >= 0
    out[ok] = ratio[bi[ok]]
    return out


def latest_event_context(t, trade_idx, trade_side, ei, ed, eg, prefix):
    j = np.searchsorted(ei, trade_idx, side="right") - 1
    valid = j >= 0

    event_dir = np.zeros(len(trade_idx), np.int8)
    event_relation = np.zeros(len(trade_idx), np.int8)
    event_age_s = np.full(len(trade_idx), np.nan)
    gap_usd = np.full(len(trade_idx), np.nan)

    if np.any(valid):
        jj = j[valid]
        event_dir[valid] = np.where(ed[jj] < 0, -1, 1)
        event_relation[valid] = np.where(event_dir[valid] == trade_side[valid], 1, -1)
        event_age_s[valid] = (t[trade_idx[valid]] - t[ei[jj]]) / 1000.0
        gap_usd[valid] = eg[jj] / PRICE_SCALE

    return {
        f"{prefix}_event_dir": event_dir,
        f"{prefix}_event_relation": event_relation,
        f"{prefix}_event_age_s": event_age_s,
        f"{prefix}_gap_usd": gap_usd,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report", type=Path)
    ap.add_argument("ticks", type=Path)
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--rows", type=Path, required=True)
    ap.add_argument("--offset-sweep", type=Path)
    args = ap.parse_args()

    trades = extract_trades(args.report)
    if len(trades) != 31915:
        raise RuntimeError(f"Expected 31915 January R9 REAL trades, found {len(trades)}")

    t, source_ask, source_bid = load(args.ticks)
    ask, bid, max_error2 = materialize(t, source_ask, source_bid)
    mid = (ask.astype(np.int64) + bid.astype(np.int64)) / 2.0

    side = np.array([x["side"] for x in trades], np.int8)
    report_price = np.array([x["entry_price"] for x in trades], float)

    naive_ms, offset_rows, offset_ranking = infer_report_offset(t, ask, bid, trades)
    winner = offset_ranking[0]
    runner_up = offset_ranking[1]
    report_offset_hours = int(winner["offset_hours"])
    report_ms = naive_ms - report_offset_hours * 3_600_000
    trade_idx = nearest_tick_indices(t, report_ms)

    mapped_quote = np.where(side > 0, ask[trade_idx], bid[trade_idx]) / PRICE_SCALE
    price_error = np.abs(mapped_quote - report_price)
    time_error = np.abs(t[trade_idx] - report_ms)

    bars5, state5, age5 = state_age_series(t, mid, 300000)
    bars15, state15, age15 = state_age_series(t, mid, 900000)
    st5, ag5 = map_state(t, trade_idx, bars5, state5, age5, 300000)
    st15, ag15 = map_state(t, trade_idx, bars15, state15, age15, 900000)

    owner_tf = np.zeros(len(trade_idx), np.int8)
    owner_dir = np.zeros(len(trade_idx), np.int8)
    owner_age = np.zeros(len(trade_idx), np.int32)
    relation = np.zeros(len(trade_idx), np.int8)

    same = (st15 != 0) & (st5 == st15)
    own15 = (st15 != 0) & ((st5 == 0) | same)
    own5 = (st5 != 0) & (st15 == 0)
    conflict = (st5 != 0) & (st15 != 0) & (st5 != st15)

    owner_tf[own15] = 15
    owner_dir[own15] = st15[own15]
    owner_age[own15] = ag15[own15]

    owner_tf[own5] = 5
    owner_dir[own5] = st5[own5]
    owner_age[own5] = ag5[own5]

    relation[(owner_dir != 0) & (owner_dir == side)] = 1
    relation[(owner_dir != 0) & (owner_dir == -side)] = -1
    relation[conflict] = 2

    phase = np.zeros(len(trade_idx), np.int8)
    phase[(owner_age >= 1) & (owner_age <= 2)] = 1
    phase[(owner_age >= 3) & (owner_age <= 6)] = 2
    phase[owner_age >= 7] = 3

    vol_ratio = minute_vol_ratio(t, bid, trade_idx)

    contexts = {}
    for multiplier, name in ((0.5, "A05"), (1.0, "A10"), (1.5, "A15")):
        gaps = m1_atr_gap(t, bid, multiplier)
        ei, ed, eg = gen_events(t, ask, bid, gaps)
        contexts.update(latest_event_context(t, trade_idx, side, ei, ed, eg, name))

    rows = pd.DataFrame(
        {
            "entry_report_time": [x["entry_report_time"] for x in trades],
            "exit_report_time": [x["exit_report_time"] for x in trades],
            "entry_utc_ms": report_ms,
            "mapped_tick_utc_ms": t[trade_idx],
            "mapped_time_error_ms": time_error,
            "side": side,
            "entry_price_report": report_price,
            "entry_price_mapped_quote": mapped_quote,
            "entry_price_abs_error": price_error,
            "price_profit": [x["price_profit"] for x in trades],
            "entry_commission": [x["entry_commission"] for x in trades],
            "exit_commission": [x["exit_commission"] for x in trades],
            "entry_swap": [x["entry_swap"] for x in trades],
            "exit_swap": [x["exit_swap"] for x in trades],
            "entry_deal_cashflow": [x["entry_commission"] + x["entry_swap"] for x in trades],
            "exit_deal_cashflow": [x["exit_commission"] + x["exit_swap"] + x["price_profit"] for x in trades],
            "net_cashflow": [x["net_cashflow"] for x in trades],
            "hold_seconds": [x["hold_seconds"] for x in trades],
            "state_5m": st5,
            "age_5m": ag5,
            "state_15m": st15,
            "age_15m": ag15,
            "owner_tf": owner_tf,
            "owner_dir": owner_dir,
            "owner_relation": relation,
            "owner_phase": phase,
            "vol_ratio_atr14_atr240": vol_ratio,
            **contexts,
        }
    )

    rows.to_csv(args.rows, index=False, compression="gzip")

    deal_cashflows = np.concatenate(
        [rows.entry_deal_cashflow.to_numpy(float), rows.exit_deal_cashflow.to_numpy(float)]
    )
    gp = float(deal_cashflows[deal_cashflows > 0].sum())
    gl = float(deal_cashflows[deal_cashflows < 0].sum())

    summary = {
        "schema": "delta-a-alpha-r9-real-jan-context-mapping-v1",
        "unit": "DAA_GRID_001_R9_REAL_JAN_CONTEXT_MAPPING_001",
        "status": "COMPLETE_MAPPING_VERIFIED",
        "trades": int(len(rows)),
        "accounting": {
            "net": float(rows.net_cashflow.sum()),
            "gross_profit": gp,
            "gross_loss": gl,
            "profit_factor": gp / abs(gl),
        },
        "alignment": {
            "offset_hours": report_offset_hours,
            "tested_offset_range_hours": [int(OFFSET_CANDIDATES[0]), int(OFFSET_CANDIDATES[-1])],
            "runner_up_offset_hours": int(runner_up["offset_hours"]),
            "runner_up_median_entry_price_abs_error": float(runner_up["median_abs_price_error"]),
            "winner_median_error_advantage_vs_runner_up_usd": float(runner_up["median_abs_price_error"] - winner["median_abs_price_error"]),
            "median_entry_price_abs_error": float(np.median(price_error)),
            "p75_entry_price_abs_error": float(np.quantile(price_error, 0.75)),
            "p90_entry_price_abs_error": float(np.quantile(price_error, 0.90)),
            "mean_entry_price_abs_error": float(price_error.mean()),
            "median_tick_time_error_ms": float(np.median(time_error)),
            "p90_tick_time_error_ms": float(np.quantile(time_error, 0.90)),
            "within_1usd_pct": float(100 * np.mean(price_error <= 1.0)),
            "max_midpoint_quantization_error_price": float(max_error2 / (2 * PRICE_SCALE)),
        },
        "context_population": {
            "owner_15m": int(np.sum(owner_tf == 15)),
            "owner_5m": int(np.sum(owner_tf == 5)),
            "owner_neutral": int(np.sum(relation == 0)),
            "owner_aligned": int(np.sum(relation == 1)),
            "owner_opposed": int(np.sum(relation == -1)),
            "owner_conflict": int(np.sum(relation == 2)),
            "phase_early": int(np.sum(phase == 1)),
            "phase_mature": int(np.sum(phase == 2)),
            "phase_extended": int(np.sum(phase == 3)),
            "vol_expansion_ge_1_75": int(np.sum(vol_ratio >= 1.75)),
            "vol_expansion_ge_2_00": int(np.sum(vol_ratio >= 2.0)),
        },
    }

    if args.offset_sweep is not None:
        offset_doc = {
            "schema": "delta-a-alpha-r9-real-jan-clock-offset-sweep-v1",
            "sample": len(trades),
            "candidate_offsets": offset_rows,
            "ranking": offset_ranking,
            "winner": winner,
            "runner_up": runner_up,
            "winner_median_error_advantage_vs_runner_up_usd": float(
                runner_up["median_abs_price_error"] - winner["median_abs_price_error"]
            ),
        }
        args.offset_sweep.write_text(json.dumps(offset_doc, indent=2) + "\n", encoding="utf-8")

    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

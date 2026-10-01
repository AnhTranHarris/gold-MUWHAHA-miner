#!/usr/bin/env python3
"""BETA078: self-contained M5 level-maturity first-retest x hold neighborhood.

Research-only human-QA candidate builder.

Causal contract
---------------
* Canonical Dukascopy Jan-Jul 2026 tick gzip files are verified by SHA-256.
* M1/M5 bars are UTC [left,right) buckets and become visible only at right edge.
* A left2/right2 M5 pivot centered at i becomes active only after i+2 closes.
* A break is observed on an M1 completed close beyond the active M5 level.
* The first accepted M1 retest within 10 M1 bars generates an event.
* Entry is the first source tick strictly after the event timestamp.
* Exit is the first source tick at/after the fixed hold from actual entry.
* BUY fills Ask and exits Bid; SELL fills Bid and exits Ask; fee=$0.02 roundtrip.
* August is never referenced or read.

Jan-Jul are historically inspected/nonblind; this unit is for engineering/human QA,
not independent alpha validation and not MQL5 authorization.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

UNIT = "BETA_078_M5_LEVEL_MATURITY_RETEST_HOLD_NEIGHBORHOOD"
MONTH_SPECS = [
    ("2026-01", "XAUUSD_DUKAS_2026_01_ticks.csv(3).gz", "d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"),
    ("2026-02", "XAUUSD_DUKAS_2026_02_ticks.csv(3).gz", "ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d"),
    ("2026-03", "XAUUSD_DUKAS_2026_03_ticks.csv(3).gz", "814ba35e72f219a58badd806ed5c0f30ef0fb4ffe56a48205d873706513bd177"),
    ("2026-04", "XAUUSD_DUKAS_2026_04_ticks.csv(3).gz", "30375098f62aed6cabc32ec6b67c57c20baec9b6d9be1ce0a204e09806c1ec0f"),
    ("2026-05", "XAUUSD_DUKAS_2026_05_ticks.csv(3).gz", "3a50e0f1eba3076154238290ec02842cf3744ab192e5c9a2acc1cc07367c6a0d"),
    ("2026-06", "XAUUSD_DUKAS_2026_06_ticks.csv(3).gz", "34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2"),
    ("2026-07", "XAUUSD_DUKAS_2026_07_ticks.csv(2).gz", "e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7"),
]
MONTHS = [m for m, _, _ in MONTH_SPECS]
MONTH_FILE = {m: f for m, f, _ in MONTH_SPECS}
MONTH_SHA = {m: h for m, _, h in MONTH_SPECS}
WINDOWS = {"AGE_7_9": (7, 9), "AGE_7_10": (7, 10), "AGE_8_9": (8, 9)}
WINDOW_NEIGHBORS = {"AGE_7_9": ["AGE_7_10", "AGE_8_9"], "AGE_7_10": ["AGE_7_9"], "AGE_8_9": ["AGE_7_9"]}
HOLDS = (600, 900, 1200, 1800)
RETEST_TOLERANCES = (0.10, 0.20, 0.30)
MAX_RETEST_AGE_M1 = 10
FEE = 0.02
MIN_TRADES = 200
MIN_POS_MONTHS = 4
NEIGHBOR_MIN_TRADES = 150
PNL_EPS = 1e-9


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(16 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_ticks(path: Path, expected_sha: str | None, head_only: bool = False):
    if expected_sha is not None:
        actual = sha256_file(path)
        if actual != expected_sha:
            raise RuntimeError(f"source SHA mismatch for {path.name}: {actual}")
    ts, asks, bids = [], [], []
    previous_last = None
    for df in pd.read_csv(
        path,
        compression="gzip",
        usecols=["timestamp_ms_utc", "ask_raw", "bid_raw"],
        chunksize=1_000_000,
        dtype={"timestamp_ms_utc": "int64", "ask_raw": "int64", "bid_raw": "int64"},
    ):
        t = df.timestamp_ms_utc.to_numpy(np.int64, copy=True)
        a = df.ask_raw.to_numpy(np.int32, copy=True)
        b = df.bid_raw.to_numpy(np.int32, copy=True)
        if len(t):
            if previous_last is not None and t[0] < previous_last:
                raise RuntimeError(f"timestamp descent across chunks in {path.name}")
            if np.any(np.diff(t) < 0):
                raise RuntimeError(f"timestamp descent inside {path.name}")
            if np.any(a < b):
                raise RuntimeError(f"crossed quote in {path.name}")
            previous_last = int(t[-1])
        ts.append(t)
        asks.append(a)
        bids.append(b)
        if head_only:
            break
    if not ts:
        raise RuntimeError(f"empty source {path.name}")
    t = np.concatenate(ts)
    ask = np.concatenate(asks).astype(np.float64) * 0.001
    bid = np.concatenate(bids).astype(np.float64) * 0.001
    return t, ask, bid


def raw_bars(t: np.ndarray, ask: np.ndarray, bid: np.ndarray, minutes: int) -> pd.DataFrame:
    bucket_ms = minutes * 60_000
    bucket = t // bucket_ms
    starts = np.r_[0, np.flatnonzero(bucket[1:] != bucket[:-1]) + 1]
    ends = np.r_[starts[1:], len(t)]
    ids = bucket[starts]
    mid = (ask + bid) * 0.5
    return pd.DataFrame(
        {
            "id": ids,
            "right": (ids + 1) * bucket_ms,
            "o": mid[starts],
            "h": np.maximum.reduceat(mid, starts),
            "l": np.minimum.reduceat(mid, starts),
            "c": mid[ends - 1],
        }
    )


def finish_bars(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("id").drop_duplicates("id").reset_index(drop=True)
    o, h, l, c = (df[x].to_numpy(float) for x in ("o", "h", "l", "c"))
    prev = np.r_[o[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(np.abs(h - prev), np.abs(l - prev)))
    df["atr"] = pd.Series(tr).rolling(14, min_periods=14).mean().to_numpy()
    return df


def confirmed_pivots(df: pd.DataFrame):
    h = df.h.to_numpy(float)
    l = df.l.to_numpy(float)
    n = len(df)
    pivot_h = np.full(n, np.nan)
    pivot_l = np.full(n, np.nan)
    for i in range(2, n - 2):
        if h[i] > h[i - 2] and h[i] > h[i - 1] and h[i] > h[i + 1] and h[i] > h[i + 2]:
            pivot_h[i + 2] = h[i]
        if l[i] < l[i - 2] and l[i] < l[i - 1] and l[i] < l[i + 1] and l[i] < l[i + 2]:
            pivot_l[i + 2] = l[i]
    active_h = np.full(n, np.nan)
    active_l = np.full(n, np.nan)
    age_h = np.full(n, -1, np.int32)
    age_l = np.full(n, -1, np.int32)
    hp = lp = np.nan
    hi = li = -1
    for j in range(n):
        if np.isfinite(pivot_h[j]):
            hp, hi = pivot_h[j], j
        if np.isfinite(pivot_l[j]):
            lp, li = pivot_l[j], j
        active_h[j], active_l[j] = hp, lp
        age_h[j] = j - hi if hi >= 0 else -1
        age_l[j] = j - li if li >= 0 else -1
    return active_h, active_l, age_h, age_l


def build_cumulative_bars(data_dir: Path):
    m1_parts, m5_parts, cert = [], [], []
    for month, filename, expected in MONTH_SPECS:
        path = data_dir / filename
        t, ask, bid = load_ticks(path, expected)
        m1_parts.append(raw_bars(t, ask, bid, 1))
        m5_parts.append(raw_bars(t, ask, bid, 5))
        cert.append({"month": month, "file": filename, "sha256": expected, "ticks": int(len(t))})
        print("BARS", month, len(t), flush=True)
    return finish_bars(pd.concat(m1_parts, ignore_index=True)), finish_bars(pd.concat(m5_parts, ignore_index=True)), cert


def generate_m5_first_retests(m1: pd.DataFrame, m5: pd.DataFrame) -> pd.DataFrame:
    active_h, active_l, age_h, age_l = confirmed_pivots(m5)
    m5_right = m5.right.to_numpy(np.int64)
    m1_right = m1.right.to_numpy(np.int64)
    m5_index = np.searchsorted(m5_right, m1_right, side="right") - 1
    m5_index = np.maximum(m5_index, 0)
    level_h, level_l = active_h[m5_index], active_l[m5_index]
    ageh, agel = age_h[m5_index], age_l[m5_index]
    close = m1.c.to_numpy(float)
    high = m1.h.to_numpy(float)
    low = m1.l.to_numpy(float)
    atr = m1.atr.to_numpy(float)
    states = {1: None, -1: None}
    rows = []
    for i in range(20, len(m1)):
        if not np.isfinite(atr[i]) or atr[i] <= 0:
            continue
        prev = close[i - 1]
        if np.isfinite(level_h[i]) and prev <= level_h[i] and close[i] > level_h[i]:
            states[1] = {"level": float(level_h[i]), "break_i": i, "level_age": int(ageh[i])}
        if np.isfinite(level_l[i]) and prev >= level_l[i] and close[i] < level_l[i]:
            states[-1] = {"level": float(level_l[i]), "break_i": i, "level_age": int(agel[i])}
        for side in (1, -1):
            st = states[side]
            if st is None:
                continue
            retest_age = i - st["break_i"]
            if retest_age <= 0 or retest_age > MAX_RETEST_AGE_M1:
                if retest_age > MAX_RETEST_AGE_M1:
                    states[side] = None
                continue
            level = st["level"]
            for tol in RETEST_TOLERANCES:
                used_key = f"used_{tol:.2f}"
                if st.get(used_key):
                    continue
                if side == 1:
                    touched = low[i] <= level + tol * atr[i]
                    accepted = close[i] > level
                else:
                    touched = high[i] >= level - tol * atr[i]
                    accepted = close[i] < level
                if touched and accepted:
                    rows.append(
                        {
                            "event_ms": int(m1_right[i]),
                            "side": int(side),
                            "level_tf": "M5",
                            "level_price": float(level),
                            "level_age_m5_bars": int(st["level_age"]),
                            "retest_age_m1_bars": int(retest_age),
                            "retest_tolerance_atr": float(tol),
                            "m1_atr14": float(atr[i]),
                        }
                    )
                    st[used_key] = True
    events = pd.DataFrame(rows)
    events["level_key"] = np.round(events.level_price, 4)
    events = (
        events.sort_values(["event_ms", "side", "level_key", "retest_tolerance_atr"])
        .drop_duplicates(["event_ms", "side", "level_key"], keep="first")
        .drop(columns="level_key")
        .reset_index(drop=True)
    )
    events["entry_month"] = pd.to_datetime(events.event_ms, unit="ms", utc=True).dt.strftime("%Y-%m")
    return events


def attach_multi_horizon_execution(events: pd.DataFrame, data_dir: Path, out_dir: Path) -> pd.DataFrame:
    parts = []
    for idx, (month, filename, expected) in enumerate(MONTH_SPECS):
        ev = events[(events.entry_month == month) & events.level_age_m5_bars.between(7, 10)].copy().reset_index(drop=True)
        if ev.empty:
            continue
        t, ask, bid = load_ticks(data_dir / filename, expected)
        if idx + 1 < len(MONTH_SPECS):
            _, next_file, _ = MONTH_SPECS[idx + 1]
            tn, an, bn = load_ticks(data_dir / next_file, None, head_only=True)
            t = np.r_[t, tn]
            ask = np.r_[ask, an]
            bid = np.r_[bid, bn]
        entry_index = np.searchsorted(t, ev.event_ms.to_numpy(np.int64), side="right")
        valid = entry_index < len(t)
        ev = ev.loc[valid].reset_index(drop=True)
        entry_index = entry_index[valid]
        sides = ev.side.to_numpy(np.int8)
        ev["entry_ms"] = t[entry_index]
        ev["entry_ask"] = ask[entry_index]
        ev["entry_bid"] = bid[entry_index]
        ev["entry_spread"] = ask[entry_index] - bid[entry_index]
        for hold_s in HOLDS:
            exit_index = np.searchsorted(t, t[entry_index] + hold_s * 1000, side="left")
            good = exit_index < len(t)
            exit_ms = np.full(len(ev), -1, np.int64)
            exit_ask = np.full(len(ev), np.nan)
            exit_bid = np.full(len(ev), np.nan)
            pnl = np.full(len(ev), np.nan)
            ii = np.flatnonzero(good)
            xx = exit_index[ii]
            ss = sides[ii]
            exit_ms[ii] = t[xx]
            exit_ask[ii] = ask[xx]
            exit_bid[ii] = bid[xx]
            pnl[ii] = np.where(ss == 1, bid[xx] - ev.entry_ask.to_numpy(float)[ii], ev.entry_bid.to_numpy(float)[ii] - ask[xx]) - FEE
            ev[f"exit_ms_{hold_s}s"] = exit_ms
            ev[f"exit_ask_{hold_s}s"] = exit_ask
            ev[f"exit_bid_{hold_s}s"] = exit_bid
            ev[f"pnl_{hold_s}s"] = pnl
        ev.to_csv(out_dir / f"BETA_078_EXEC_{month}.csv.gz", index=False, compression="gzip")
        parts.append(ev)
        print("EXEC", month, len(ev), flush=True)
    if not parts:
        raise RuntimeError("no executable events")
    return pd.concat(parts, ignore_index=True).sort_values(["entry_ms", "event_ms", "side", "level_price"]).reset_index(drop=True)


def schedule_one_position(df: pd.DataFrame, hold_s: int) -> pd.DataFrame:
    pnl_col = f"pnl_{hold_s}s"
    exit_col = f"exit_ms_{hold_s}s"
    df = df[np.isfinite(df[pnl_col])].sort_values(["entry_ms", "event_ms", "side", "level_price"]).reset_index(drop=True)
    keep = []
    free_ms = -1
    for row in df.itertuples():
        if row.entry_ms < free_ms:
            continue
        keep.append(row.Index)
        free_ms = int(getattr(row, exit_col))
    return df.loc[keep].copy().reset_index(drop=True)


def stats(df: pd.DataFrame, hold_s: int) -> dict:
    if len(df) == 0:
        return {"trades": 0, "wins": 0, "win_rate": 0.0, "net": 0.0, "gp": 0.0, "gl": 0.0, "pf": 0.0, "avg": 0.0, "max_dd": 0.0}
    pnl = df[f"pnl_{hold_s}s"].to_numpy(float)
    pnl = np.where(np.abs(pnl) <= PNL_EPS, 0.0, pnl)
    gp = float(pnl[pnl > PNL_EPS].sum())
    gl = float(pnl[pnl < -PNL_EPS].sum())
    wins = int((pnl > PNL_EPS).sum())
    equity = np.cumsum(pnl)
    peak = np.maximum.accumulate(np.r_[0.0, equity])[1:]
    dd = peak - equity
    return {
        "trades": int(len(pnl)),
        "wins": wins,
        "win_rate": wins / len(pnl),
        "net": float(pnl.sum()),
        "gp": gp,
        "gl": gl,
        "pf": gp / abs(gl) if gl < 0 else (math.inf if gp > 0 else 0.0),
        "avg": float(pnl.mean()),
        "max_dd": float(dd.max() if len(dd) else 0.0),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    data_dir = Path(args.data_dir)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    m1, m5, cert = build_cumulative_bars(data_dir)
    events = generate_m5_first_retests(m1, m5)
    events.to_csv(out / "BETA_078_M5_FIRST_RETEST_EVENTS.csv.gz", index=False, compression="gzip")
    surface = attach_multi_horizon_execution(events, data_dir, out)

    rows = []
    ledgers = {}
    for window_name, (age_lo, age_hi) in WINDOWS.items():
        sub = surface[surface.level_age_m5_bars.between(age_lo, age_hi)]
        for hold_s in HOLDS:
            ledger = schedule_one_position(sub, hold_s)
            ledgers[(window_name, hold_s)] = ledger
            total = stats(ledger, hold_s)
            monthly = {month: stats(ledger[ledger.entry_month == month], hold_s) for month in MONTHS}
            positive_months = sum(v["net"] > 0 for v in monthly.values())
            rows.append(
                {
                    "window": window_name,
                    "age_lo": age_lo,
                    "age_hi": age_hi,
                    "hold_s": hold_s,
                    **total,
                    "positive_months": positive_months,
                    "monthly_json": json.dumps(monthly, sort_keys=True),
                }
            )
    table = pd.DataFrame(rows)
    table.to_csv(out / "BETA_078_NEIGHBORHOOD_TABLE.csv", index=False)

    candidates = []
    for row in table.itertuples():
        if row.trades < MIN_TRADES or row.net <= 0 or row.pf <= 1 or row.avg <= 0 or row.positive_months < MIN_POS_MONTHS:
            continue
        neighbors = []
        hold_index = HOLDS.index(row.hold_s)
        if hold_index > 0:
            neighbors.append((row.window, HOLDS[hold_index - 1]))
        if hold_index + 1 < len(HOLDS):
            neighbors.append((row.window, HOLDS[hold_index + 1]))
        neighbors += [(w, row.hold_s) for w in WINDOW_NEIGHBORS[row.window]]
        support = []
        for w, h in neighbors:
            z = table[(table.window == w) & (table.hold_s == h)]
            if len(z):
                z = z.iloc[0]
                if int(z.trades) >= NEIGHBOR_MIN_TRADES and float(z.net) > 0 and float(z.pf) > 1 and float(z.avg) > 0:
                    support.append({"window": w, "hold_s": int(h), "trades": int(z.trades), "net": float(z.net), "pf": float(z.pf)})
        if support:
            candidates.append((row, support))

    selected = None
    if candidates:
        row, support = sorted(candidates, key=lambda x: (x[0].positive_months, x[0].net, x[0].pf), reverse=True)[0]
        selected = {"window": row.window, "age_lo": int(row.age_lo), "age_hi": int(row.age_hi), "hold_s": int(row.hold_s), "neighbor_support": support}
        ledger = ledgers[(row.window, row.hold_s)].copy()
        ledger.insert(0, "qa_trade_id", np.arange(1, len(ledger) + 1))
        ledger["selected_pnl"] = ledger[f"pnl_{row.hold_s}s"]
        ledger.to_csv(out / "BETA_078_SELECTED_LEDGER.csv.gz", index=False, compression="gzip")
        aggregate = stats(ledger, row.hold_s)
        monthly = {month: stats(ledger[ledger.entry_month == month], row.hold_s) for month in MONTHS}
    else:
        pd.DataFrame(columns=["qa_trade_id", "entry_ms", "selected_pnl"]).to_csv(out / "BETA_078_SELECTED_LEDGER.csv.gz", index=False, compression="gzip")
        aggregate = stats(pd.DataFrame(), 900)
        monthly = {}

    result = {
        "unit_id": UNIT,
        "status": "HUMAN_QA_RESEARCH_CANDIDATE_NONBLIND" if selected else "NO_STABLE_NEIGHBORHOOD_CANDIDATE",
        "selected": selected,
        "aggregate": aggregate,
        "monthly": monthly,
        "source_certification": cert,
        "preownership_events": int(len(events)),
        "age_7_10_executable_events": int(len(surface)),
        "human_qa_ready_for_inspection": bool(selected),
        "selection_data": "Jan-Jul historically inspected/nonblind",
        "august": "SEALED_NOT_READ",
        "warning": "Human QA readiness is engineering/research inspection only; not alpha validation or MT5 approval.",
    }
    (out / "BETA_078_RESULTS.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    if selected:
        packet = (
            "# BETA078 Human-Facing QA Review Packet\n\n"
            f"Status: **{result['status']}**  \nAugust: **SEALED**  \nMQL5: **NOT AUTHORIZED**\n\n"
            f"Candidate: **M5 FIRST_RETEST; level maturity {selected['age_lo']}–{selected['age_hi']} completed M5 bars; fixed {selected['hold_s']}s hold.**\n\n"
            f"Jan-Jul nonblind research score: **{aggregate['trades']} trades, ${aggregate['net']:.2f} net, PF {aggregate['pf']:.3f}, {aggregate['win_rate']:.1%} win rate, ${aggregate['avg']:.3f}/trade, max DD ${aggregate['max_dd']:.2f}.**\n\n"
            "Monthly:\n" + "\n".join(
                f"- {m}: {v['trades']} trades, ${v['net']:.2f}, PF {v['pf']:.3f}, avg ${v['avg']:.3f}" for m, v in monthly.items()
            ) + "\n\nNeighbor support:\n" + "\n".join(
                f"- {n['window']} @ {n['hold_s']}s: {n['trades']} trades, ${n['net']:.2f}, PF {n['pf']:.3f}" for n in selected['neighbor_support']
            ) + "\n\n**Interpretation:** suitable for human inspection of timing, state-machine logic, trade ledger and reconstruction. Jan-Jul were used in discovery/selection, so profitability is not independently validated. August remains the sealed blind gate.\n"
        )
    else:
        packet = "# BETA078 Human-Facing QA Review Packet\n\nNo stable maturity/hold neighborhood passed. August remains sealed.\n"
    (out / "BETA_078_HUMAN_QA_REVIEW_PACKET.md").write_text(packet)
    (out / "BETA_078_M5_LEVEL_MATURITY_RETEST_HOLD_NEIGHBORHOOD_REPORT.md").write_text(packet)

    np.savez_compressed(
        out / "BETA_078_MULTI_HORIZON_EXECUTION.npz",
        event_ms=surface.event_ms.to_numpy(np.int64),
        entry_ms=surface.entry_ms.to_numpy(np.int64),
        side=surface.side.to_numpy(np.int8),
        level_age_m5_bars=surface.level_age_m5_bars.to_numpy(np.int16),
        **{f"pnl_{h}s": surface[f"pnl_{h}s"].to_numpy(float) for h in HOLDS},
        **{f"exit_ms_{h}s": surface[f"exit_ms_{h}s"].to_numpy(np.int64) for h in HOLDS},
    )
    hashes = {p.name: sha256_file(p) for p in sorted(out.iterdir()) if p.is_file() and p.name != "BETA_078_HASHES.json"}
    (out / "BETA_078_HASHES.json").write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
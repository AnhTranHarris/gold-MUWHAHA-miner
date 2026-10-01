#!/usr/bin/env python3
"""Independent engineering QA for BETA078 human-review candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

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
HOLD_S = 1800
FEE_MILLS = 20
PNL_EPS = 1e-9


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(16 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_raw(path: Path, head_only: bool = False):
    ts, asks, bids = [], [], []
    prev = None
    for df in pd.read_csv(
        path,
        compression="gzip",
        usecols=["timestamp_ms_utc", "ask_raw", "bid_raw"],
        chunksize=1_000_000,
        dtype={"timestamp_ms_utc": "int64", "ask_raw": "int64", "bid_raw": "int64"},
    ):
        t = df.timestamp_ms_utc.to_numpy(np.int64, copy=True)
        a = df.ask_raw.to_numpy(np.int64, copy=True)
        b = df.bid_raw.to_numpy(np.int64, copy=True)
        if len(t):
            if prev is not None and t[0] < prev:
                raise RuntimeError(f"timestamp descent across chunks in {path.name}")
            if np.any(np.diff(t) < 0):
                raise RuntimeError(f"timestamp descent in {path.name}")
            if np.any(a < b):
                raise RuntimeError(f"crossed quote in {path.name}")
            prev = int(t[-1])
        ts.append(t); asks.append(a); bids.append(b)
        if head_only:
            break
    return np.concatenate(ts), np.concatenate(asks), np.concatenate(bids)


def calc_stats(df: pd.DataFrame):
    v = df.selected_pnl.to_numpy(float)
    v = np.where(np.abs(v) <= PNL_EPS, 0.0, v)
    gp = float(v[v > PNL_EPS].sum())
    gl = float(v[v < -PNL_EPS].sum())
    eq = np.cumsum(v)
    peak = np.maximum.accumulate(np.r_[0.0, eq])[1:] if len(v) else np.array([])
    return {
        "trades": int(len(v)),
        "wins": int((v > PNL_EPS).sum()),
        "flats": int((np.abs(v) <= PNL_EPS).sum()),
        "win_rate": float((v > PNL_EPS).mean()) if len(v) else 0.0,
        "net": float(v.sum()),
        "gp": gp,
        "gl": gl,
        "pf": gp / abs(gl) if gl < 0 else 0.0,
        "avg": float(v.mean()) if len(v) else 0.0,
        "max_dd": float((peak - eq).max()) if len(v) else 0.0,
    }


def iso(ms):
    if ms is None or ms == "" or (isinstance(ms, float) and np.isnan(ms)):
        return ""
    return pd.to_datetime(int(ms), unit="ms", utc=True).isoformat()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--data-dir", required=True)
    args = ap.parse_args()
    out = Path(args.out_dir)
    data = Path(args.data_dir)

    res = json.loads((out / "BETA_078_RESULTS.json").read_text())
    ledger = pd.read_csv(out / "BETA_078_SELECTED_LEDGER.csv.gz")
    checks = []

    def ck(name, cond, detail=""):
        checks.append({"name": name, "pass": bool(cond), "detail": str(detail)})
        if not cond:
            print("FAIL", name, detail)

    selected = res["selected"]
    ck("selected_policy_identity", selected["age_lo"] == 7 and selected["age_hi"] == 9 and selected["hold_s"] == HOLD_S)
    ck("trade_count_420", len(ledger) == 420, len(ledger))
    ck("qa_ids_sequential", np.array_equal(ledger.qa_trade_id.to_numpy(), np.arange(1, len(ledger) + 1)))
    ck("all_M5", set(ledger.level_tf) == {"M5"})
    ck("maturity_7_9", bool(ledger.level_age_m5_bars.between(7, 9).all()))
    ck("valid_retest_age", bool(ledger.retest_age_m1_bars.between(1, 10).all()))
    ck("valid_tolerance", set(np.round(ledger.retest_tolerance_atr, 2)).issubset({0.1, 0.2, 0.3}))
    ck("strict_entry_after_event", bool((ledger.entry_ms > ledger.event_ms).all()))
    ck("selected_pnl_identity", np.allclose(ledger.selected_pnl, ledger.pnl_1800s, atol=1e-12))
    ck("selected_hold_not_early", bool((ledger.exit_ms_1800s >= ledger.entry_ms + HOLD_S * 1000).all()))
    ck("no_position_overlap", bool(np.all(ledger.entry_ms.to_numpy()[1:] >= ledger.exit_ms_1800s.to_numpy()[:-1])))
    ck("months_only_jan_jul", set(ledger.entry_month).issubset(set(MONTHS)) and not ledger.entry_month.astype(str).str.contains("2026-08").any())

    # Event-ledger identity: every selected event must exist in the source-generated causal event ledger.
    events = pd.read_csv(out / "BETA_078_M5_FIRST_RETEST_EVENTS.csv.gz")
    ekeys = set(zip(events.event_ms.astype(int), events.side.astype(int), np.round(events.level_price, 4)))
    lkeys = list(zip(ledger.event_ms.astype(int), ledger.side.astype(int), np.round(ledger.level_price, 4)))
    ck("selected_events_exist_in_causal_event_ledger", all(k in ekeys for k in lkeys), f"{sum(k in ekeys for k in lkeys)}/{len(lkeys)}")

    # Result reconciliation with flat-tolerant classification.
    st = calc_stats(ledger)
    for key in ["trades", "wins", "net", "gp", "gl", "pf", "avg", "max_dd"]:
        rv, sv = res["aggregate"][key], st[key]
        ck("aggregate_" + key, abs(float(rv) - float(sv)) < 1e-8, f"{rv} vs {sv}")
    ck("one_flat_trade", st["flats"] == 1, st["flats"])

    for month in MONTHS:
        sm = calc_stats(ledger[ledger.entry_month == month])
        rm = res["monthly"][month]
        for key in ["trades", "wins", "net", "pf", "avg"]:
            rv = rm[key]
            sv = sm[key]
            ck(f"month_{month}_{key}", abs(float(rv) - float(sv)) < 1e-8, f"{rv} vs {sv}")

    # Verify every canonical source hash plus exact entry/exit quote/timestamp and integer-mill P&L.
    source_hashes = {}
    max_quote_error = 0.0
    max_pnl_error = 0.0
    for i, (month, filename, expected_sha) in enumerate(MONTH_SPECS):
        path = data / filename
        actual_sha = sha256_file(path)
        source_hashes[month] = actual_sha
        ck(f"{month}_source_sha", actual_sha == expected_sha, actual_sha)
        sub = ledger[ledger.entry_month == month]
        if sub.empty:
            continue
        t, ask_raw, bid_raw = load_raw(path)
        if i + 1 < len(MONTH_SPECS):
            _, next_file, _ = MONTH_SPECS[i + 1]
            tn, an, bn = load_raw(data / next_file, head_only=True)
            t = np.r_[t, tn]; ask_raw = np.r_[ask_raw, an]; bid_raw = np.r_[bid_raw, bn]
        entry_idx = np.searchsorted(t, sub.event_ms.to_numpy(np.int64), side="right")
        exit_idx = np.searchsorted(t, sub.entry_ms.to_numpy(np.int64) + HOLD_S * 1000, side="left")
        ck(f"{month}_entry_first_later_tick", np.array_equal(t[entry_idx], sub.entry_ms.to_numpy(np.int64)))
        ck(f"{month}_exit_first_at_after_1800s", np.array_equal(t[exit_idx], sub.exit_ms_1800s.to_numpy(np.int64)))
        entry_ask = ask_raw[entry_idx] / 1000.0
        entry_bid = bid_raw[entry_idx] / 1000.0
        exit_ask = ask_raw[exit_idx] / 1000.0
        exit_bid = bid_raw[exit_idx] / 1000.0
        max_quote_error = max(max_quote_error, float(np.max(np.abs(entry_ask - sub.entry_ask))), float(np.max(np.abs(entry_bid - sub.entry_bid))), float(np.max(np.abs(exit_ask - sub.exit_ask_1800s))), float(np.max(np.abs(exit_bid - sub.exit_bid_1800s))))
        ck(f"{month}_entry_quotes_source", np.allclose(entry_ask, sub.entry_ask, atol=1e-12) and np.allclose(entry_bid, sub.entry_bid, atol=1e-12))
        ck(f"{month}_exit_quotes_source", np.allclose(exit_ask, sub.exit_ask_1800s, atol=1e-12) and np.allclose(exit_bid, sub.exit_bid_1800s, atol=1e-12))
        sides = sub.side.to_numpy(np.int8)
        pnl_mills = np.where(sides == 1, bid_raw[exit_idx] - ask_raw[entry_idx], bid_raw[entry_idx] - ask_raw[exit_idx]) - FEE_MILLS
        exact_pnl = pnl_mills / 1000.0
        max_pnl_error = max(max_pnl_error, float(np.max(np.abs(exact_pnl - sub.selected_pnl))))
        ck(f"{month}_integer_mill_pnl", np.allclose(exact_pnl, sub.selected_pnl, atol=1e-9), max_pnl_error)
        print("RAW QA", month, len(sub), flush=True)

    # Neighborhood support required by preregistration.
    tab = pd.read_csv(out / "BETA_078_NEIGHBORHOOD_TABLE.csv")
    def cell(window, hold):
        return tab[(tab.window == window) & (tab.hold_s == hold)].iloc[0]
    for window, hold in [("AGE_7_9", 1200), ("AGE_7_10", 1800), ("AGE_8_9", 1800)]:
        z = cell(window, hold)
        ck(f"neighbor_{window}_{hold}", int(z.trades) >= 150 and z.net > 0 and z.pf > 1 and z.avg > 0)

    # Build human review cases with exact blocking relationships.
    cases = []
    def add_case(case_type, expected_decision, reason, row, blocking=None):
        case = {
            "case_type": case_type,
            "expected_decision": expected_decision,
            "reason": reason,
            "month": str(row.entry_month),
            "event_ms": int(row.event_ms),
            "event_utc": iso(row.event_ms),
            "entry_ms": int(row.entry_ms),
            "entry_utc": iso(row.entry_ms),
            "side": int(row.side),
            "side_name": "BUY" if int(row.side) == 1 else "SELL",
            "level_price": float(row.level_price),
            "level_age_m5_bars": int(row.level_age_m5_bars),
            "retest_age_m1_bars": int(row.retest_age_m1_bars),
            "retest_tolerance_atr": float(row.retest_tolerance_atr),
            "entry_spread": float(row.entry_spread),
            "expected_exit_ms": "",
            "expected_exit_utc": "",
            "expected_pnl": "",
            "pnl_formula": "",
            "blocking_trade_id": "",
            "blocking_entry_utc": "",
            "blocking_exit_utc": "",
        }
        if case_type == "ADMITTED":
            case["expected_exit_ms"] = int(row.exit_ms_1800s)
            case["expected_exit_utc"] = iso(row.exit_ms_1800s)
            case["expected_pnl"] = float(row.selected_pnl)
            case["pnl_formula"] = "exit_bid - entry_ask - 0.02" if int(row.side) == 1 else "entry_bid - exit_ask - 0.02"
        if blocking is not None:
            case["blocking_trade_id"] = int(blocking.qa_trade_id)
            case["blocking_entry_utc"] = iso(blocking.entry_ms)
            case["blocking_exit_utc"] = iso(blocking.exit_ms_1800s)
        cases.append(case)

    # Largest winners/losers plus the exact-flat example.
    for month in MONTHS:
        d = ledger[ledger.entry_month == month]
        sample = pd.concat([d.nlargest(2, "selected_pnl"), d.nsmallest(2, "selected_pnl")]).drop_duplicates("qa_trade_id")
        for r in sample.itertuples(index=False):
            add_case("ADMITTED", "ENTER", "M5_FIRST_RETEST_LEVEL_AGE_7_9_AND_FLAT", r)
    flat = ledger[np.abs(ledger.selected_pnl) <= PNL_EPS]
    for r in flat.itertuples(index=False):
        add_case("ADMITTED", "ENTER", "EXACT_FLAT_PNL_CASE__FLOATING_DUST_NORMALIZED_TO_ZERO", r)

    all_exec = pd.concat([pd.read_csv(out / f"BETA_078_EXEC_{m}.csv.gz") for m in MONTHS], ignore_index=True).sort_values("entry_ms")
    maturity_rejects = all_exec[all_exec.level_age_m5_bars.isin([6, 10])].groupby(["entry_month", "level_age_m5_bars"], as_index=False).head(1)
    for r in maturity_rejects.head(14).itertuples(index=False):
        add_case("REJECT_MATURITY", "SKIP", "M5_LEVEL_AGE_OUTSIDE_7_9", r)

    eligible = all_exec[all_exec.level_age_m5_bars.between(7, 9) & np.isfinite(all_exec.pnl_1800s)].sort_values(["entry_ms", "event_ms", "side", "level_price"]).reset_index(drop=True)
    admitted_by_key = {(int(r.event_ms), int(r.side), round(float(r.level_price), 4)): r for r in ledger.itertuples(index=False)}
    ownership_examples = []
    for r in eligible.itertuples(index=False):
        key = (int(r.event_ms), int(r.side), round(float(r.level_price), 4))
        if key in admitted_by_key:
            continue
        blockers = ledger[(ledger.entry_ms <= r.entry_ms) & (ledger.exit_ms_1800s > r.entry_ms)]
        if len(blockers):
            ownership_examples.append((r, next(blockers.itertuples(index=False))))
    for r, blocking in ownership_examples[:14]:
        add_case("REJECT_OWNERSHIP", "BLOCK", "POSITION_ALREADY_OPEN", r, blocking)

    cases_df = pd.DataFrame(cases)
    cases_df.insert(0, "qa_case_id", [f"B78-QA-{i:03d}" for i in range(1, len(cases_df) + 1)])
    cases_df.to_csv(out / "BETA_078_HUMAN_QA_CASES.csv", index=False)

    passed = sum(c["pass"] for c in checks)
    qa = {
        "unit_id": "BETA_078_HUMAN_QA_ENGINEERING_QA_V2",
        "assertions": len(checks),
        "passed": passed,
        "failed": len(checks) - passed,
        "all_pass": passed == len(checks),
        "checks": checks,
        "human_qa_cases": len(cases_df),
        "case_counts": {str(k): int(v) for k, v in cases_df.case_type.value_counts().to_dict().items()},
        "exact_flat_trades": st["flats"],
        "max_source_quote_error_usd": max_quote_error,
        "max_integer_pnl_error_usd": max_pnl_error,
        "source_sha256": source_hashes,
        "august": "SEALED_NOT_READ",
    }
    (out / "BETA_078_QA.json").write_text(json.dumps(qa, indent=2, sort_keys=True) + "\n")

    checklist = f'''# BETA078 Human QA Checklist\n\nEngineering QA: **{passed}/{len(checks)} assertions PASS**  \nCandidate: **M5 FIRST_RETEST / level age 7–9 M5 bars / 1800-second hold**  \nAugust: **SEALED**  \nMQL5: **NOT AUTHORIZED**\n\n## Manual review workflow\n\n1. Open `BETA_078_HUMAN_QA_CASES.csv`; review cases from **ADMITTED**, **REJECT_MATURITY**, and **REJECT_OWNERSHIP**.\n2. For an ADMITTED case, verify the displayed M5 level was confirmed before the break, the break precedes the retest, the retest is visible only at the completed M1 right edge, and the entry is the first later quote.\n3. Confirm maturity admission is inclusive only for level ages **7, 8, or 9 completed M5 bars**.\n4. For REJECT_OWNERSHIP, verify the referenced blocking trade was still open at the rejected entry timestamp.\n5. Recalculate BUY P&L as `exit_bid - entry_ask - 0.02`; SELL as `entry_bid - exit_ask - 0.02`. The QA suite also verifies the equivalent calculation in integer quote mills.\n6. Verify exit is the first source quote at or after **1800 seconds from actual entry**, not from signal time.\n7. Review largest winners and largest losers from every month, plus the explicit exact-flat case.\n8. Reconcile monthly totals with `BETA_078_RESULTS.json` and the complete selected ledger.\n\n## Accounting normalization\n\nOne July trade is exactly flat in integer quote units. Earlier floating arithmetic represented it as approximately ±1e-13 and could change the win count without changing economics. QA V2 normalizes `|PnL| <= 1e-9` to flat. This is an accounting classification correction, not a strategy change.\n\n## Research interpretation boundary\n\nThis is a **human-QA research candidate**, not independently validated alpha. The maturity window was discovered on Jan–Jul, which are historically inspected. Human QA evaluates causality, implementation, accounting, state transitions, explainability, and reproducibility. It does not convert Jan–Jul economics into out-of-sample evidence. **August remains sealed** for the blind gate after QA.\n'''
    (out / "BETA_078_HUMAN_QA_CHECKLIST.md").write_text(checklist)
    print(json.dumps({k: qa[k] for k in ["assertions", "passed", "failed", "all_pass", "human_qa_cases", "case_counts", "exact_flat_trades", "max_integer_pnl_error_usd", "august"]}, indent=2))


if __name__ == "__main__":
    main()
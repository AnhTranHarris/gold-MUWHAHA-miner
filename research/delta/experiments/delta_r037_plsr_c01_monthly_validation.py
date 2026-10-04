"""DELTA R037 PLSR C01 month-isolated surrogate validation — Checkpoint 16C.

Frozen candidate: R037-PLSR-C01_PDH_PDL_S5_RECLAIM.
Each invocation validates exactly one calendar month using the final seven UTC
calendar days of the immediately preceding canonical month as causal warmup.
Economic entries are prohibited before the current month start.
No month-specific tuning, no PDH/PDL split, no August.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

import delta_r037_sorb_c04_dual30_independent_validation as val
import delta_r037_plsr_stage_a as plsr

CANDIDATE_ID = "R037-PLSR-C01_PDH_PDL_S5_RECLAIM"
DAY_MS = 86_400_000
WARMUP_DAYS = 7
SOURCE_SHA = {
    "2026-01": "d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5",
    "2026-02": "ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d",
    "2026-03": "814ba35e72f219a58badd806ed5c0f30ef0fb4ffe56a48205d873706513bd177",
    "2026-04": "30375098f62aed6cabc32ec6b67c57c20baec9b6d9be1ce0a204e09806c1ec0f",
    "2026-05": "3a50e0f1eba3076154238290ec02842cf3744ab192e5c9a2acc1cc07367c6a0d",
    "2026-06": "34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2",
    "2026-07": "e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7",
}


def month_bounds(month: str) -> tuple[int, int, str]:
    y, m = map(int, month.split("-"))
    if y != 2026 or m < 2 or m > 7:
        raise SystemExit(f"16C supports only 2026-02..2026-07, got {month}")
    start = int(datetime(y, m, 1, tzinfo=timezone.utc).timestamp() * 1000)
    end = int(datetime(y, m + 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
    prev = f"{y:04d}-{m-1:02d}"
    return start, end, prev


def load_ticks(prev_path: Path, cur_path: Path, month: str):
    start, end, prev_month = month_bounds(month)
    prev_sha = val.base.sha256_file(prev_path)
    cur_sha = val.base.sha256_file(cur_path)
    if prev_sha != SOURCE_SHA[prev_month]:
        raise SystemExit(f"previous-month SHA mismatch {prev_month}: {prev_sha}")
    if cur_sha != SOURCE_SHA[month]:
        raise SystemExit(f"current-month SHA mismatch {month}: {cur_sha}")

    usecols = ["timestamp_ms_utc", "ask_raw", "bid_raw"]
    prev = pd.read_csv(prev_path, compression="gzip", usecols=usecols, dtype=np.int64)
    warmup_start = start - WARMUP_DAYS * DAY_MS
    prev = prev[(prev.timestamp_ms_utc >= warmup_start) & (prev.timestamp_ms_utc < start)]
    cur = pd.read_csv(cur_path, compression="gzip", usecols=usecols, dtype=np.int64)
    cur = cur[(cur.timestamp_ms_utc >= start) & (cur.timestamp_ms_utc < end)]
    df = pd.concat([prev, cur], ignore_index=True)
    t = df.timestamp_ms_utc.to_numpy(np.int64)
    if t.size == 0 or np.any(t[1:] < t[:-1]):
        raise SystemExit(f"16C chronology mismatch {month}: {t.size}")
    economic_ticks = int(np.sum((t >= start) & (t < end)))
    if economic_ticks <= 0:
        raise SystemExit(f"16C no economic ticks for {month}")
    return df, start, end, warmup_start, prev_sha, cur_sha, economic_ticks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prev", type=Path, required=True)
    ap.add_argument("--current", type=Path, required=True)
    ap.add_argument("--month", required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()

    df, month_start, month_end, warmup_start, prev_sha, cur_sha, economic_ticks = load_ticks(
        a.prev, a.current, a.month
    )
    t = df.timestamp_ms_utc.to_numpy(np.int64)
    ask, bid = val.base.p75(t, df.ask_raw.to_numpy(np.int64), df.bid_raw.to_numpy(np.int64))

    feat = val.parent.build_parent_features(t, ask, bid)
    streams = val.generate_streams(t, ask, bid)
    d3t, d3s = streams["DH03_S06"]
    d5t, d5s = streams["DH05_S06"]
    s11t, s11s = streams["DH02_S11"]
    s08t, s08s = streams["DH02_S08"]

    zi = np.empty(0, np.int64)
    zs = np.empty(0, np.int8)
    parent = val.pack_sorb(val.run_integrated_sorb(
        t, ask, bid, feat["impulse250"], feat["h1_netatr"], feat["m30_netatr"],
        d3t, d3s, d5t, d5s, s11t, s11s, s08t, s08s,
        zi, zs, zs, 1, 1, 1, 1, 1, month_start
    ))

    props_all = plsr.generate_proposals(t, ask, bid, CANDIDATE_ID)
    props = [
        x for x in props_all
        if x.decision_index < len(t) and month_start <= int(t[x.decision_index]) < month_end
    ]
    supply = plsr.supply(props)
    eligible = [x for x in props if x.eligible]
    ii = np.asarray([x.decision_index for x in eligible], np.int64)
    ss = np.asarray([x.side for x in eligible], np.int8)
    sk = np.asarray([1 if x.level_kind == "PDH" else 2 for x in eligible], np.int8)

    combined = val.pack_sorb(val.run_integrated_sorb(
        t, ask, bid, feat["impulse250"], feat["h1_netatr"], feat["m30_netatr"],
        d3t, d3s, d5t, d5s, s11t, s11s, s08t, s08s,
        ii, ss, sk, 1, 1, 1, 1, 1, month_start
    ))
    decision = val.decision(parent, combined, supply)

    contribution = combined.pop("sorb_session_contribution")
    combined["plsr_entries"] = combined.pop("sorb_entries")
    combined["plsr_net"] = combined.pop("sorb_net")
    combined["plsr_level_contribution"] = {
        "PDH": contribution["LONDON"],
        "PDL": contribution["COMEX_GOLD"],
    }
    decision["incremental_net_per_plsr_entry"] = decision.pop("incremental_net_per_sorb_entry")

    out = {
        "schema": "delta-r037-plsr-c01-month-isolated-validation-16c-v1",
        "status": "COMPLETE_MONTH_ISOLATED_VALIDATION",
        "unit": "R037_PLSR_C01_MONTH_BY_MONTH_SURROGATE_VALIDATION",
        "candidate": CANDIDATE_ID,
        "month": a.month,
        "surface": "DUKAS_COINEXX_LIKE_P75",
        "promotable": False,
        "warmup_days": WARMUP_DAYS,
        "warmup_start_ms": warmup_start,
        "month_start_ms": month_start,
        "month_end_ms_exclusive": month_end,
        "loaded_ticks": int(t.size),
        "economic_ticks": economic_ticks,
        "source_sha256": {"previous": prev_sha, "current": cur_sha},
        "candidate_retuned": False,
        "posthoc_level_split": False,
        "august_accessed": False,
        "parent_control": parent,
        "supply": supply,
        "combined": combined,
        "decision": decision,
        "mql5_authorized": False,
    }
    val.base.atomic_write_json(a.output, out)
    print(json.dumps({
        "month": a.month,
        "supply": supply,
        "parent": {"trades": parent["trades"], "official_wins": parent["official_wins"], "net_profit": parent["net_profit"], "max_equity_drawdown": parent["max_equity_drawdown"]},
        "combined": {"trades": combined["trades"], "official_wins": combined["official_wins"], "net_profit": combined["net_profit"], "max_equity_drawdown": combined["max_equity_drawdown"], "plsr_entries": combined["plsr_entries"], "plsr_net": combined["plsr_net"], "levels": combined["plsr_level_contribution"]},
        "decision": decision,
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()

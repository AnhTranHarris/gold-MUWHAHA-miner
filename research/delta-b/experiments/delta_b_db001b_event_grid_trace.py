#!/usr/bin/env python3
"""DELTA-B DB001B scheduled-event grid-state trace.

Research-only. This producer does not place trades and does not evaluate profit.
It replays canonical Dukascopy quotes only inside bounded event windows, with
per-event warmup, then measures Grid Layer 1 state/Q behavior by event phase and
session.

Key causal rules:
- ask = ask_raw / 1000; bid = bid_raw / 1000
- midpoint state, not midpoint fills
- calendar rows are scheduled state only; no actual/consensus surprise is used
- each event cluster receives an independent pre-event warmup kernel
- August is rejected
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
import tempfile
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from delta_b_grid_kernel import (
    CalendarEvent,
    GridConfig,
    Importance,
    IntrinsicGridKernel,
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False, suffix=".tmp"
    ) as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
        tmp = Path(f.name)
    os.replace(tmp, path)


def load_events(path: Path, start: str, end: str) -> tuple[list[CalendarEvent], list[dict[str, str]], str]:
    raw = path.read_bytes()
    cache_sha = hashlib.sha256(raw).hexdigest()
    rows: list[dict[str, str]] = []
    events: list[CalendarEvent] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["currency"] != "USD":
                continue
            if not (start <= row["date_et"] <= end):
                continue
            if row["date_et"] >= "2026-08-01":
                raise RuntimeError("August is sealed; event cache selection crossed into August")
            ts = datetime.fromisoformat(row["timestamp_utc"].replace("Z", "+00:00"))
            imp = Importance.HIGH if row["severity"] == "HIGH" else Importance.MEDIUM
            events.append(
                CalendarEvent(
                    time_utc=ts,
                    importance=imp,
                    currency="USD",
                    name=row["event_name"],
                    event_id=row["event_id"],
                )
            )
            rows.append(row)
    if not rows:
        raise RuntimeError("no event rows selected")
    return events, rows, cache_sha


def make_clusters(rows: list[dict[str, str]], warmup_min: int, pre_min: int, post_min: int) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["timestamp_utc"]].append(row)
    clusters: list[dict[str, Any]] = []
    for stamp, members in sorted(grouped.items()):
        t = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        sev = "HIGH" if any(m["severity"] == "HIGH" for m in members) else "MEDIUM"
        clusters.append(
            {
                "cluster_id": stamp,
                "time": t,
                "time_ms": int(t.timestamp() * 1000),
                "warm_start_ms": int((t - timedelta(minutes=warmup_min + pre_min)).timestamp() * 1000),
                "record_start_ms": int((t - timedelta(minutes=pre_min)).timestamp() * 1000),
                "record_end_ms": int((t + timedelta(minutes=post_min)).timestamp() * 1000),
                "severity": sev,
                "event_ids": [m["event_id"] for m in members],
                "families": [m["event_family"] for m in members],
                "names": [m["event_name"] for m in members],
            }
        )
    return clusters


def new_bucket() -> dict[str, Any]:
    return {
        "ticks": 0,
        "q_base_sum": 0.0,
        "q_context_sum": 0.0,
        "spread_sum": 0.0,
        "entry_authority_sum": 0.0,
        "shock_ticks": 0,
        "states": Counter(),
        "events_by_scale": Counter(),
    }


def update_bucket(bucket: dict[str, Any], snap, spread: float) -> None:
    bucket["ticks"] += 1
    bucket["q_base_sum"] += snap.q.q_base
    bucket["q_context_sum"] += snap.q.q_context
    bucket["spread_sum"] += spread
    bucket["entry_authority_sum"] += snap.q.adjustment.entry_authority
    bucket["shock_ticks"] += int(snap.q.shock_active)
    bucket["states"][snap.state.value] += 1
    for event in snap.events:
        bucket["events_by_scale"][f"{event.scale:g}Q"] += 1


def finalize_bucket(bucket: dict[str, Any]) -> dict[str, Any]:
    n = bucket["ticks"]
    if not n:
        return {
            "ticks": 0,
            "mean_q_base": None,
            "mean_q_context": None,
            "mean_q_context_ratio": None,
            "mean_spread": None,
            "mean_entry_authority": None,
            "shock_fraction": None,
            "states": {},
            "events_by_scale": {},
        }
    qbase = bucket["q_base_sum"] / n
    qctx = bucket["q_context_sum"] / n
    return {
        "ticks": n,
        "mean_q_base": qbase,
        "mean_q_context": qctx,
        "mean_q_context_ratio": (qctx / qbase) if qbase else None,
        "mean_spread": bucket["spread_sum"] / n,
        "mean_entry_authority": bucket["entry_authority_sum"] / n,
        "shock_fraction": bucket["shock_ticks"] / n,
        "states": dict(bucket["states"]),
        "events_by_scale": dict(bucket["events_by_scale"]),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticks", required=True)
    ap.add_argument("--events", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--start", default="2026-01-01")
    ap.add_argument("--end", default="2026-01-31")
    ap.add_argument("--warmup-min", type=int, default=60)
    ap.add_argument("--pre-min", type=int, default=60)
    ap.add_argument("--post-min", type=int, default=120)
    ap.add_argument("--commission-equiv", type=float, default=0.02)
    ap.add_argument("--slippage-buffer", type=float, default=0.0)
    ap.add_argument("--expected-source-sha256")
    ns = ap.parse_args()

    if ns.end >= "2026-08-01":
        raise RuntimeError("August 2026 is SEALED")
    tick_path = Path(ns.ticks)
    event_path = Path(ns.events)
    out_path = Path(ns.output)

    source_sha = sha256_file(tick_path)
    if ns.expected_source_sha256 and source_sha != ns.expected_source_sha256:
        raise RuntimeError(
            f"source SHA mismatch expected={ns.expected_source_sha256} actual={source_sha}"
        )

    events, event_rows, event_cache_sha = load_events(event_path, ns.start, ns.end)
    clusters = make_clusters(event_rows, ns.warmup_min, ns.pre_min, ns.post_min)
    first_ms = min(c["warm_start_ms"] for c in clusters)
    last_ms = max(c["record_end_ms"] for c in clusters)

    cfg = GridConfig()
    runtimes = []
    for c in clusters:
        runtimes.append(
            {
                **c,
                "kernel": IntrinsicGridKernel(cfg),
                "overall": new_bucket(),
                "by_phase": defaultdict(new_bucket),
                "by_session": defaultdict(new_bucket),
                "processed": 0,
            }
        )

    source_rows = 0
    active_rows = 0
    with gzip.open(tick_path, "rt", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        idx = {name: i for i, name in enumerate(header)}
        required = {"timestamp_ms_utc", "ask_raw", "bid_raw"}
        if not required.issubset(idx):
            raise RuntimeError(f"tick schema missing {sorted(required - set(idx))}")

        for row in reader:
            source_rows += 1
            ts_ms = int(row[idx["timestamp_ms_utc"]])
            if ts_ms < first_ms:
                continue
            if ts_ms > last_ms:
                break

            targets = [
                rt for rt in runtimes
                if rt["warm_start_ms"] <= ts_ms <= rt["record_end_ms"]
            ]
            if not targets:
                continue
            active_rows += 1
            ts = datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc)
            ask = int(row[idx["ask_raw"]]) / 1000.0
            bid = int(row[idx["bid_raw"]]) / 1000.0
            if ask < bid:
                raise RuntimeError("invalid quote ask < bid")
            spread = ask - bid

            for rt in targets:
                snap = rt["kernel"].update(
                    ts_utc=ts,
                    bid=bid,
                    ask=ask,
                    events=events,
                    commission_equiv=ns.commission_equiv,
                    slippage_buffer=ns.slippage_buffer,
                )
                rt["processed"] += 1
                if ts_ms < rt["record_start_ms"]:
                    continue
                update_bucket(rt["overall"], snap, spread)
                update_bucket(rt["by_phase"][snap.q.event_phase.value], snap, spread)
                update_bucket(rt["by_session"][snap.q.session.value], snap, spread)

    cluster_results = []
    phase_all: dict[str, dict[str, Any]] = defaultdict(new_bucket)
    session_all: dict[str, dict[str, Any]] = defaultdict(new_bucket)
    overall_all = new_bucket()

    for rt in runtimes:
        # Aggregate by replaying bucket sums, avoiding trade/economic interpretation.
        def merge(dst, src):
            dst["ticks"] += src["ticks"]
            dst["q_base_sum"] += src["q_base_sum"]
            dst["q_context_sum"] += src["q_context_sum"]
            dst["spread_sum"] += src["spread_sum"]
            dst["entry_authority_sum"] += src["entry_authority_sum"]
            dst["shock_ticks"] += src["shock_ticks"]
            dst["states"].update(src["states"])
            dst["events_by_scale"].update(src["events_by_scale"])

        merge(overall_all, rt["overall"])
        for key, bucket in rt["by_phase"].items():
            merge(phase_all[key], bucket)
        for key, bucket in rt["by_session"].items():
            merge(session_all[key], bucket)

        cluster_results.append(
            {
                "cluster_id": rt["cluster_id"],
                "severity": rt["severity"],
                "event_ids": rt["event_ids"],
                "families": rt["families"],
                "names": rt["names"],
                "warmup_ticks": rt["processed"] - rt["overall"]["ticks"],
                "record": finalize_bucket(rt["overall"]),
                "by_phase": {k: finalize_bucket(v) for k, v in rt["by_phase"].items()},
                "by_session": {k: finalize_bucket(v) for k, v in rt["by_session"].items()},
            }
        )

    payload = {
        "schema": "delta-b-db001b-event-grid-trace-v1",
        "status": "MECHANICS_DIAGNOSTIC_NO_PROFIT_CLAIM",
        "source": {
            "tick_path_name": tick_path.name,
            "tick_sha256": source_sha,
            "event_cache_name": event_path.name,
            "event_cache_sha256": event_cache_sha,
            "date_start": ns.start,
            "date_end": ns.end,
            "source_rows_scanned": source_rows,
            "rows_processed_inside_any_window": active_rows,
        },
        "config": {
            "warmup_min": ns.warmup_min,
            "pre_min": ns.pre_min,
            "post_min": ns.post_min,
            "commission_equiv": ns.commission_equiv,
            "slippage_buffer": ns.slippage_buffer,
            "grid_config": {
                "q_floor": cfg.q_floor,
                "q_ceiling": cfg.q_ceiling,
                "cost_mult": cfg.cost_mult,
                "noise_mult": cfg.noise_mult,
                "scales": list(cfg.scales),
                "medium_window": asdict(cfg.medium_window),
                "high_window": asdict(cfg.high_window),
            },
        },
        "calendar": {
            "selected_rows": len(event_rows),
            "unique_clusters": len(clusters),
        },
        "overall": finalize_bucket(overall_all),
        "by_phase": {k: finalize_bucket(v) for k, v in phase_all.items()},
        "by_session": {k: finalize_bucket(v) for k, v in session_all.items()},
        "clusters": cluster_results,
        "limitations": [
            "No trades or PnL are computed.",
            "Each event cluster has an independent warmup kernel; this is event-window diagnostics, not continuous-month state.",
            "V1 event cache is core official scheduled USD macro, not an exhaustive third-party Medium/High clone.",
            "Calendar severity is DELTA-B research taxonomy.",
        ],
    }
    atomic_json(out_path, payload)
    print(
        f"DELTA_B_DB001B_OK clusters={len(clusters)} selected_events={len(event_rows)} "
        f"rows_scanned={source_rows} active_rows={active_rows} output={out_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

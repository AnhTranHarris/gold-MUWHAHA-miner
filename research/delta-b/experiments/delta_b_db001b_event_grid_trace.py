#!/usr/bin/env python3
"""DELTA-B DB001 event/session grid-state trace.

Single-pass, research-only producer:
- one chronological intrinsic-grid kernel
- one compact medium/high USD event schedule
- one fast session/event context cursor
- no trade placement and no profitability claim
- August hard-sealed
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
import tempfile
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from delta_b_context_clock import build_context_clock
from delta_b_grid_kernel import GridConfig, IntrinsicGridKernel


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
        suffix=".tmp",
    ) as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
        tmp = Path(f.name)
    os.replace(tmp, path)


def parse_utc_ms(value: str) -> int:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc)
    if dt >= datetime(2026, 8, 1, tzinfo=timezone.utc):
        raise RuntimeError("August 2026 is SEALED")
    return int(round(dt.timestamp() * 1000.0))


def new_bucket() -> dict[str, Any]:
    return {
        "ticks": 0,
        "q_base_sum": 0.0,
        "q_context_sum": 0.0,
        "spread_sum": 0.0,
        "entry_authority_sum": 0.0,
        "observed_stress_sum": 0.0,
        "event_activation_sum": 0.0,
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
    bucket["observed_stress_sum"] += snap.q.observed_stress
    bucket["event_activation_sum"] += snap.q.event_activation
    bucket["shock_ticks"] += int(snap.q.shock_active)
    bucket["states"][snap.state.value] += 1
    for event in snap.events:
        bucket["events_by_scale"][f"{event.scale:g}Q"] += 1


def finalize(bucket: dict[str, Any]) -> dict[str, Any]:
    n = bucket["ticks"]
    if n == 0:
        return {
            "ticks": 0,
            "mean_q_base": None,
            "mean_q_context": None,
            "mean_q_context_ratio": None,
            "mean_spread": None,
            "mean_entry_authority": None,
            "mean_observed_stress": None,
            "mean_event_activation": None,
            "shock_fraction": None,
            "states": {},
            "events_by_scale": {},
        }
    qb = bucket["q_base_sum"] / n
    qc = bucket["q_context_sum"] / n
    return {
        "ticks": n,
        "mean_q_base": qb,
        "mean_q_context": qc,
        "mean_q_context_ratio": qc / qb if qb else None,
        "mean_spread": bucket["spread_sum"] / n,
        "mean_entry_authority": bucket["entry_authority_sum"] / n,
        "mean_observed_stress": bucket["observed_stress_sum"] / n,
        "mean_event_activation": bucket["event_activation_sum"] / n,
        "shock_fraction": bucket["shock_ticks"] / n,
        "states": dict(bucket["states"]),
        "events_by_scale": dict(bucket["events_by_scale"]),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticks", required=True)
    ap.add_argument("--events", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--start", required=True, help="UTC ISO timestamp")
    ap.add_argument("--end", required=True, help="UTC ISO timestamp exclusive")
    ap.add_argument("--commission-equiv", type=float, default=0.02)
    ap.add_argument("--slippage-buffer", type=float, default=0.0)
    ap.add_argument("--expected-source-sha256")
    ap.add_argument("--max-active-rows", type=int, default=0)
    ns = ap.parse_args()

    start_ms = parse_utc_ms(ns.start)
    end_ms = parse_utc_ms(ns.end)
    if end_ms <= start_ms:
        raise RuntimeError("end must be after start")
    if end_ms > int(datetime(2026, 8, 1, tzinfo=timezone.utc).timestamp() * 1000):
        raise RuntimeError("August 2026 is SEALED")

    tick_path = Path(ns.ticks)
    event_path = Path(ns.events)
    out_path = Path(ns.output)

    source_sha = sha256_file(tick_path)
    event_sha = sha256_file(event_path)
    if ns.expected_source_sha256 and source_sha != ns.expected_source_sha256:
        raise RuntimeError(
            f"source SHA mismatch expected={ns.expected_source_sha256} actual={source_sha}"
        )

    cfg = GridConfig()
    clock, events, transitions = build_context_clock(event_path, cfg)
    kernel = IntrinsicGridKernel(cfg)

    overall = new_bucket()
    by_phase: dict[str, dict[str, Any]] = defaultdict(new_bucket)
    by_session: dict[str, dict[str, Any]] = defaultdict(new_bucket)
    by_state: dict[str, dict[str, Any]] = defaultdict(new_bucket)
    by_phase_session: dict[str, dict[str, Any]] = defaultdict(new_bucket)

    source_rows = 0
    active_rows = 0
    started = time.perf_counter()

    with gzip.open(tick_path, "rt", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        idx = {name: i for i, name in enumerate(header)}
        required = {"timestamp_ms_utc", "ask_raw", "bid_raw"}
        if not required.issubset(idx):
            raise RuntimeError(
                f"tick schema missing {sorted(required - set(idx))}"
            )

        for row in reader:
            source_rows += 1
            ts_ms = int(row[idx["timestamp_ms_utc"]])
            if ts_ms < start_ms:
                continue
            if ts_ms >= end_ms:
                break

            ask = int(row[idx["ask_raw"]]) / 1000.0
            bid = int(row[idx["bid_raw"]]) / 1000.0
            if ask < bid:
                raise RuntimeError("invalid quote ask < bid")

            session, phase = clock.state_at_ms(ts_ms)
            snap = kernel.update_ms(
                time_ms=ts_ms,
                bid=bid,
                ask=ask,
                session=session,
                event_phase=phase,
                commission_equiv=ns.commission_equiv,
                slippage_buffer=ns.slippage_buffer,
            )
            spread = ask - bid
            update_bucket(overall, snap, spread)
            update_bucket(by_phase[phase.value], snap, spread)
            update_bucket(by_session[session.value], snap, spread)
            update_bucket(by_state[snap.state.value], snap, spread)
            update_bucket(
                by_phase_session[f"{phase.value}|{session.value}"],
                snap,
                spread,
            )

            active_rows += 1
            if ns.max_active_rows and active_rows >= ns.max_active_rows:
                break

    elapsed = time.perf_counter() - started
    result = {
        "schema": "delta-b-db001-event-grid-trace-v2",
        "claim_boundary": (
            "Grid/context mechanics only. No orders, fills, profit or candidate promotion."
        ),
        "source": {
            "ticks": str(tick_path),
            "ticks_sha256": source_sha,
            "event_cache": str(event_path),
            "event_cache_sha256": event_sha,
            "event_rows": len(events),
            "event_transitions": len(transitions),
        },
        "range": {
            "start_ms": start_ms,
            "end_ms": end_ms,
            "active_rows": active_rows,
            "source_rows_read": source_rows,
            "max_active_rows": ns.max_active_rows,
        },
        "runtime": {
            "elapsed_seconds": elapsed,
            "ticks_per_second": active_rows / elapsed if elapsed else None,
            "session_recomputes": clock.session_recomputes,
            "q_noise_refreshes": kernel.q.noise_refreshes,
            "q_quantile_refreshes": kernel.q.quantile_refreshes,
        },
        "overall": finalize(overall),
        "by_phase": {k: finalize(v) for k, v in sorted(by_phase.items())},
        "by_session": {k: finalize(v) for k, v in sorted(by_session.items())},
        "by_state": {k: finalize(v) for k, v in sorted(by_state.items())},
        "by_phase_session": {
            k: finalize(v) for k, v in sorted(by_phase_session.items())
        },
    }
    atomic_json(out_path, result)
    print(
        json.dumps(
            {
                "active_rows": active_rows,
                "elapsed_seconds": elapsed,
                "ticks_per_second": result["runtime"]["ticks_per_second"],
                "event_rows": len(events),
                "event_transitions": len(transitions),
                "output": str(out_path),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

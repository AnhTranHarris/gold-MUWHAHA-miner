"""V12: fixed-model first-leg entry evaluation on later original Coinexx ticks.

No retraining or tuning: use an existing frozen LightGBM research model,
read only the original TickLogger, and compare autonomous signals against
R9 SYNTH -> Coinexx merged teacher target AFTER the decisions are fixed.
The intended market entry is a newly observed quote at/after next second,
not the historical teacher fill or an invented quote. Compact JSON only.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from train_v12_coinexx_event_hazard import (
    read_teacher, load_existing_ticklogger, choose_online_entries,
    next_real_second, score,
)

RESEARCH_MODEL_SHA256 = "7e52f85d0af8222cfd0b1b92be9647a210affe5226a1f12dd2de7cda5d5f8b3a"


def read_family_labels(path: Path, clock_offset_minutes: int):
    """Outcomes used ONLY after all entry decisions are fixed."""
    rows = defaultdict(dict)
    with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as h:
        for item in csv.DictReader(h):
            stamp = datetime.fromisoformat(item["entry_time_broker"])
            if stamp.tzinfo is None:
                stamp = stamp.replace(tzinfo=timezone.utc)
            minute = (int(stamp.timestamp()) + clock_offset_minutes * 60) // 60
            rows[minute][int(item["leg"])] = float(item["net_usd"])
    families = {}
    for minute, legs in rows.items():
        if 2 not in legs:
            families[minute] = "A_single_leg"
        elif legs[1] > 0 and legs[2] > 0:
            families[minute] = "B_favorable_first_then_opposite"
        elif legs[1] <= 0 and legs[2] > 0:
            families[minute] = "C_adverse_first_then_opposite"
        else:
            families[minute] = "other_two_leg_outcomes"
    return families


def run(tick_paths, merged, model_path, *, after_epoch_ms: int,
        offset_minutes: int, max_quotes: int | None, threshold: float):
    import numpy as np
    import lightgbm as lgb

    blob_hash = hashlib.sha256(model_path.read_bytes()).hexdigest()
    if blob_hash != RESEARCH_MODEL_SHA256:
        raise AssertionError("Research model has changed: frozen-weight test rejected")
    X, minutes, time_ms, sides, prices, first_ms, first_buy, first_sell, source_rows = (
        load_existing_ticklogger(tick_paths, max_quotes=max_quotes)
    )
    eval_minutes = np.unique(minutes[minutes > after_epoch_ms // 60000])
    if len(eval_minutes) == 0:
        raise ValueError("No independent future Coinexx minutes after frozen cutoff")
    mask = minutes > after_epoch_ms // 60000
    model = lgb.Booster(model_file=str(model_path), params={"num_threads": 4})
    probs = model.predict(X[mask], num_threads=4)
    autonomous = choose_online_entries(
        mask, probs, threshold, minutes, time_ms, sides, prices
    )
    next_second = next_real_second(autonomous, first_ms, first_buy, first_sell)
    teacher = read_teacher(merged, offset_minutes)
    families = read_family_labels(merged, offset_minutes)

    report = {
        "source": "existing_original_REAL_TickLogger_ordered_quotes",
        "teacher": "existing_r9_synth_to_Coinexx_merged_reference",
        "model_sha256": blob_hash,
        "model_weights_or_threshold_modified": False,
        "threshold": threshold,
        "eval_after_epoch_ms": after_epoch_ms,
        "quote_rows_read_from_original_source": source_rows,
        "quote_input_files": [x.name for x in tick_paths],
        "first_leg_only": True,
        "entry_decisions_do_not_use_teacher_or_future_labels": True,
        "no_synthetic_or_future_quote_execution": True,
        "immediate": score(autonomous, teacher, eval_minutes),
        "next_second": score(next_second, teacher, eval_minutes),
    }
    by_family = {}
    for family in sorted(set(families.values())):
        subset = {m: r for m, r in teacher.items() if families[m] == family}
        by_family[family] = score(
            {m: v for m, v in next_second.items() if m in subset},
            subset, eval_minutes,
        )
    report["next_second_by_original_historical_family"] = by_family
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ticks", nargs="+", required=True, type=Path)
    p.add_argument("--merged", required=True, type=Path)
    p.add_argument("--frozen-model", required=True, type=Path)
    p.add_argument("--after", required=True,
                   help="strict chronology cutoff, ISO e.g. 2026-01-07T19:42:00+00:00")
    p.add_argument("--clock-offset-minutes", required=True, type=int)
    p.add_argument("--max-quotes", type=int, default=1900000)
    p.add_argument("--threshold", type=float, default=.70)
    p.add_argument("--out-json", required=True, type=Path)
    a = p.parse_args()
    time = datetime.fromisoformat(a.after.replace("Z", "+00:00"))
    if time.tzinfo is None:
        p.error("--after must include a timezone offset")
    if a.max_quotes is not None and a.max_quotes <= 0:
        p.error("--max-quotes must be positive")
    if not 0 < a.threshold <= 1:
        p.error("--threshold out of range")
    report = run(
        a.ticks, a.merged, a.frozen_model,
        after_epoch_ms=int(time.timestamp() * 1000),
        offset_minutes=a.clock_offset_minutes,
        max_quotes=a.max_quotes, threshold=a.threshold,
    )
    a.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["next_second"], sort_keys=True))


if __name__ == "__main__":
    main()

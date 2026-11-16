"""Train/validate Micro180 V12 entry hazard from EXISTING REAL TickLogger + merged R9 teacher.

Only the first original 0.01-lot entry opportunity of each minute is modeled
in this phase. No R9 synthetic event or post-entry quote is fed into features.
Every feature is calculated at the first ACTUAL source quote of its second using
CompletedSecondHorizon (including the previous five minutes of observed quotes)
and the as-of completed M5 ATR already recorded by the source TickLogger.

Validation and test splits are chronological and never used to fit the model.
Timestamps and price of the mapped Coinexx quote are scoring targets only.
This command produces ONE small model and ONE compact metrics JSON; neither
raw source nor expanded tick tables are copied or created.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from coinexx_r9.models import Tick
from v12_coinexx_virtualclock_entry import (
    CompletedSecondHorizon,
    FEATURE_NAMES,
)


def read_teacher(path: Path, offset_minutes: int):
    first = {}
    legs = defaultdict(dict)
    with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"entry_time_broker", "leg", "side", "net_usd",
                    "q_entry_u", "equote_ms"}
        if not required.issubset(reader.fieldnames or ()):
            raise ValueError("Unexpected original merged R9-Coinexx schema")
        for row in reader:
            stamp = datetime.fromisoformat(row["entry_time_broker"])
            if stamp.tzinfo is None:
                stamp = stamp.replace(tzinfo=timezone.utc)
            ts = int(stamp.timestamp()) + offset_minutes * 60
            minute = ts // 60
            side = 1 if row["side"].lower() == "buy" else -1
            leg = int(row["leg"])
            legs[minute][leg] = (
                ts, side, int(row["q_entry_u"]), float(row["net_usd"]),
                int(row["equote_ms"]),
            )
    for minute, minute_legs in legs.items():
        if 1 in minute_legs:
            first[minute] = minute_legs[1]
    return first


def load_existing_ticklogger(paths: list[Path], *, max_quotes: int | None):
    import numpy as np

    clock = CompletedSecondHorizon()
    features, labels, minutes, times, sides, prices = [], [], [], [], [], []
    # One chronological real quote per observed SECOND for event-hazard
    # evaluation. The full underlying feed still advances the state.
    first_buy, first_sell, first_times = [], [], []
    source_rows = 0
    prior_ms = -1
    for part in paths:
        opener = gzip.open if part.suffix == ".gz" else open
        with opener(part, "rt", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader)
            positions = {name: i for i, name in enumerate(header)}
            for required in ("time_msc", "bid", "ask", "atr"):
                if required not in positions:
                    raise ValueError(f"Original REAL TickLogger missing {required}")
            for row in reader:
                source_rows += 1
                if max_quotes is not None and source_rows > max_quotes:
                    break
                tms = int(row[positions["time_msc"]])
                if tms < prior_ms:
                    raise ValueError("Original Coinexx quotes must be chronologically ordered")
                prior_ms = tms
                bid = int(round(float(row[positions["bid"]]) * 100))
                ask = int(round(float(row[positions["ask"]]) * 100))
                if bid <= 0 or ask < bid:
                    raise ValueError("Malformed original Coinexx Bid/Ask")
                tick = Tick(source_rows, tms // 1000, tms, bid, ask)
                clock.update(tick)
                if not clock.first_tick_this_second:
                    continue
                first_times.append(tms)
                first_buy.append(ask)
                first_sell.append(bid)
                atr_u = float(row[positions["atr"]]) * 100
                for side in (1, -1):
                    minutes.append(tick.time_s // 60)
                    times.append(tms)
                    sides.append(side)
                    prices.append(ask if side > 0 else bid)
                    features.append(clock.features(tick, side, atr_u))
        if max_quotes is not None and source_rows > max_quotes:
            source_rows = max_quotes
            break
    return (
        np.asarray(features, dtype=np.float32),
        np.asarray(minutes, dtype=np.int64),
        np.asarray(times, dtype=np.int64),
        np.asarray(sides, dtype=np.int8),
        np.asarray(prices, dtype=np.int32),
        np.asarray(first_times, dtype=np.int64),
        np.asarray(first_buy, dtype=np.int32),
        np.asarray(first_sell, dtype=np.int32),
        source_rows,
    )


def choose_online_entries(mask, prob, threshold, mins, tms, sides, prices):
    import numpy as np

    decisions = {}
    idx = np.flatnonzero(mask)
    # Data are strictly in time order and use BUY before SELL on a tied quote.
    # Choose FIRST threshold crossing, NEVER hindsight max within a minute.
    for index, value in zip(idx, prob):
        minute = int(mins[index])
        if minute in decisions or value < threshold:
            continue
        decisions[minute] = (
            int(tms[index]), int(sides[index]), int(prices[index]),
        )
    return decisions


def next_real_second(decisions, first_times, first_buy, first_sell):
    import numpy as np

    executed = {}
    for minute, (signal_time, side, _) in decisions.items():
        target_ms = (signal_time // 1000 + 1) * 1000
        idx = int(np.searchsorted(first_times, target_ms, side="left"))
        if idx >= len(first_times) or first_times[idx] > target_ms + 2000:
            continue
        actual_price = first_buy[idx] if side == 1 else first_sell[idx]
        executed[minute] = (int(first_times[idx]), side, int(actual_price))
    return executed


def score(decisions, refs, valid_minutes):
    from collections import Counter
    import numpy as np

    stats = Counter()
    deltas, prices = [], []
    per_family = defaultdict(Counter)
    valid_set = set(int(x) for x in valid_minutes)
    source_refs = {m: data for m, data in refs.items() if m in valid_set}
    for minute, reference in source_refs.items():
        stats["teacher"] += 1
        # Family is intentionally excluded from this first-leg scoring stage.
        found = decisions.get(minute)
        if found is None:
            continue
        stats["same_minute"] += 1
        actual_ms, side, price = found
        original_s, original_side, quote_price, _, mapped_ms = reference
        if side != original_side:
            continue
        stats["same_direction"] += 1
        elapsed = int(actual_ms // 1000 - original_s)
        price_diff = int(price - quote_price)
        deltas.append(abs(elapsed))
        prices.append(abs(price_diff))
        if abs(elapsed) <= 2:
            stats["signal_second_plus_minus_2"] += 1
        if abs(price_diff) <= 5:
            stats["quote_price_within_5c"] += 1
        if actual_ms == mapped_ms and price_diff == 0:
            stats["exact_mapped_quote_time_and_price"] += 1
        if abs(actual_ms - mapped_ms) <= 2000 and abs(price_diff) <= 5:
            stats["mapped_2s_and_5c"] += 1
    stats["candidate_minutes"] = len(decisions)
    stats["extra_minutes"] = sum(m not in source_refs for m in decisions)
    return {
        **stats,
        "same_direction_recall": round(stats["same_direction"] / max(1, stats["teacher"]), 6),
        "same_direction_precision": round(
            stats["same_direction"] / max(1, len(decisions)), 6
        ),
        "median_absolute_original_second_error_s": (
            float(np.median(deltas)) if deltas else None
        ),
        "median_absolute_mapped_quote_price_error_cents": (
            float(np.median(prices)) if prices else None
        ),
    }


def execute(tick_paths, merged_path, offset_minutes, model_output, report_output, max_quotes):
    import numpy as np
    from lightgbm import LGBMClassifier

    refs = read_teacher(merged_path, offset_minutes)
    X, mins, tms, sides, prices, first_times, first_buy, first_sell, n = (
        load_existing_ticklogger(tick_paths, max_quotes=max_quotes)
    )
    if len(mins) == 0:
        raise ValueError("No original Coinexx quotes found")
    y = np.asarray([
        int(refs.get(int(m), (-1, -1))[0] == int(ms) // 1000
            and refs[int(m)][1] == int(side))
        for m, ms, side in zip(mins, tms, sides)
    ], dtype=np.uint8)

    active_minutes = np.unique(mins)
    if len(active_minutes) < 100:
        raise ValueError("Insufficient chronological minutes for three-way study")
    train_last = active_minutes[int(len(active_minutes) * .58) - 1]
    valid_last = active_minutes[int(len(active_minutes) * .78) - 1]
    train = mins <= train_last
    valid = (mins > train_last) & (mins <= valid_last)
    test = mins > valid_last
    positives = int(y[train].sum())
    if positives < 25:
        raise ValueError("Not enough original reference labels in training period")

    model = LGBMClassifier(
        n_estimators=170, learning_rate=.045, num_leaves=11,
        min_child_samples=130, subsample=.9, colsample_bytree=.85,
        reg_lambda=8.0, verbosity=-1,
        scale_pos_weight=min(60, max(1, float((train.sum() - positives) / positives) / 4)),
    )
    model.fit(X[train], y[train], feature_name=list(FEATURE_NAMES))
    p_valid = model.predict_proba(X[valid])[:, 1]
    p_test = model.predict_proba(X[test])[:, 1]

    thresholds = (.03, .05, .075, .10, .15, .20, .30, .40, .50, .60, .70, .80)
    validation = []
    for threshold in thresholds:
        proposals = choose_online_entries(valid, p_valid, threshold, mins, tms, sides, prices)
        executed = next_real_second(proposals, first_times, first_buy, first_sell)
        outcome = score(executed, refs, active_minutes[
            (active_minutes > train_last) & (active_minutes <= valid_last)
        ])
        utility = (4 * outcome.get("exact_mapped_quote_time_and_price", 0)
                   + 2 * outcome.get("mapped_2s_and_5c", 0)
                   + .5 * outcome.get("same_direction", 0)
                   - .7 * outcome.get("extra_minutes", 0))
        validation.append((threshold, utility, outcome))
    selected = max(validation, key=lambda x: x[1])[0]
    initial_test = choose_online_entries(test, p_test, selected, mins, tms, sides, prices)
    scheduled_test = next_real_second(initial_test, first_times, first_buy, first_sell)
    test_minutes = active_minutes[active_minutes > valid_last]
    report = {
        "source": "existing_original_Coinexx_REAL_TickLogger_only",
        "teacher": "existing_original_R9_to_Coinexx_merged_CSV",
        "source_quotes_seen": n,
        "feature_order": FEATURE_NAMES,
        "full_2026_JanSep_coverage_claimed": False,
        "first_leg_only": True,
        "model_features_use_only_past_and_current_tick": True,
        "no_future_teacher_entry_in_online_decision": True,
        "never_fills_at_synthetic_teacher_price": True,
        "historical_original_net_repricing": False,
        "train_valid_test_breaks": (int(train_last), int(valid_last)),
        "train_valid_test_positive_labels": (
            positives, int(y[valid].sum()), int(y[test].sum()),
        ),
        "threshold_fixed_from_validation": selected,
        "validation_score_curve": [
            {"threshold": th, "utility": round(utility, 4),
             "exact_mapped": stats.get("exact_mapped_quote_time_and_price", 0),
             "mapped_2s_5c": stats.get("mapped_2s_and_5c", 0)}
            for th, utility, stats in validation
        ],
        "heldout_immediate": score(initial_test, refs, test_minutes),
        "heldout_next_second_real_quote": score(scheduled_test, refs, test_minutes),
        "model_feature_importances": sorted(
            zip(FEATURE_NAMES, model.feature_importances_.tolist()),
            key=lambda z: -z[1]
        ),
    }
    model.booster_.save_model(str(model_output))
    report_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--ticks", nargs="+", required=True, type=Path,
                   help="EXISTING original REAL TickLogger monthly gzip files in time order")
    p.add_argument("--merged", required=True, type=Path)
    p.add_argument("--clock-offset-minutes", required=True, type=int)
    p.add_argument("--max-quotes", type=int, default=1400000,
                   help="Bound the first experiment; large sources require chunked training")
    p.add_argument("--model-out", required=True, type=Path)
    p.add_argument("--report-out", required=True, type=Path)
    args = p.parse_args()
    report = execute(args.ticks, args.merged, args.clock_offset_minutes,
                     args.model_out, args.report_out, args.max_quotes)
    print(json.dumps({
        "quote_rows": report["source_quotes_seen"],
        "validation_threshold": report["threshold_fixed_from_validation"],
        "test": report["heldout_next_second_real_quote"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

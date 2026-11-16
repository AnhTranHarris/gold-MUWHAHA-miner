"""Offline, read-only R9-Coinexx merged-entry concordance.

This module compares V10's independent causal quote entries with the EXISTING
R9-SYNTH-to-Coinexx merged reference: it never imports teacher timestamps as
trading signals. "Exact price" means matched original Coinexx executable-side
quote CENTS at the entry, not the synthetic MT5 deal fill.

No P&L repricing, commission adjustment, data rebuild or per-tick export.
"""
from __future__ import annotations

import csv
import gzip
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable


def read_merged_rows(path: Path) -> Iterable[dict[str, str]]:
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {
            "entry_time_broker", "side", "leg", "equote_ms",
            "q_entry_u", "net_usd",
        }
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"Merged reference missing columns: {sorted(required-set(reader.fieldnames or []))}")
        yield from reader


def _minute_from_teacher_stamp(stamp: str, clock_offset_minutes: int) -> int:
    dt = datetime.fromisoformat(stamp.strip().replace("Z", "+00:00"))
    # The archive uses broker/server seconds. No timezone is inferred: the
    # caller supplies the documented clock offset to source epoch time.
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return ((int(dt.timestamp()) + clock_offset_minutes * 60) // 60) * 60


def compare_merged_entries(
    teacher_rows: Iterable[dict[str, str]],
    causal_entries: Iterable[dict[str, Any]],
    *,
    clock_offset_minutes: int = 0,
    max_anchor_distance_ms: int = 3000,
    expected_teacher_rows: int | None = None,
    expected_teacher_net_usd: Decimal | None = None,
) -> dict[str, Any]:
    """Complete-population matching with no teacher-to-strategy leakage.

    Identity is source-native minute, numbered leg, side. Timing and executable
    price agreement are INDEPENDENT metrics, never combined into an inflated
    "matched" label. The timestamp equality gate is exact (0 ms); a ±tolerance\n    gate is reported separately. Zero recovered quote references remain in the teacher
    denominator. No candidate may match twice.
    """
    if not isinstance(clock_offset_minutes, int):
        raise ValueError("Clock offset must be an explicitly specified integer")
    if max_anchor_distance_ms < 0:
        raise ValueError("Negative entry matching tolerance")
    index: dict[tuple[int, int, int], dict[str, Any]] = {}
    duplicates: list[tuple[int, int, int]] = []
    candidate_count = 0
    for entry in causal_entries:
        candidate_count += 1
        minute = int(entry["cycle_minute"])
        leg = int(entry["rearm_number"]) + 1
        side = int(entry["side"])
        if side not in (-1, 1):
            raise ValueError("Invalid causal candidate side")
        key = (minute, leg, side)
        if key in index:
            duplicates.append(key)
            continue
        index[key] = entry
    if duplicates:
        raise ValueError(f"Duplicate causal candidate keys, first={duplicates[0]}")
    counters: Counter[str] = Counter()
    source_net = Decimal("0")
    price_errors: list[int] = []
    timing_errors: list[int] = []
    misses: list[dict[str, Any]] = []
    used: set[tuple[int, int, int]] = set()
    for row in teacher_rows:
        counters["original_teacher_rows"] += 1
        source_net += Decimal(row["net_usd"])
        side_name = row["side"].strip().lower()
        if side_name not in ("buy", "sell"):
            raise ValueError(f"Invalid merged reference side: {side_name!r}")
        side = 1 if side_name == "buy" else -1
        key = (
            _minute_from_teacher_stamp(row["entry_time_broker"], clock_offset_minutes),
            int(row["leg"]),
            side,
        )
        q_ms = int(Decimal(row["equote_ms"]))
        q_entry = int(Decimal(row["q_entry_u"]))
        if q_ms < 0 or q_entry <= 0:
            counters["source_quote_missing"] += 1
        else:
            counters["source_quote_available"] += 1
        candidate = index.get(key)
        if candidate is None:
            counters["no_candidate_same_minute_leg_side"] += 1
            if len(misses) < 12:
                misses.append({"kind": "no_causal_candidate", "minute_leg_side": key})
            continue
        if key in used:
            raise ValueError("One causal candidate reused across two teacher references")
        used.add(key)
        counters["same_minute_leg_side"] += 1
        if q_ms < 0 or q_entry <= 0:
            continue
        diff_ms = int(candidate["time_msc"]) - q_ms
        delta_price = int(candidate["price_u"]) - q_entry
        timing_errors.append(abs(diff_ms))
        price_errors.append(abs(delta_price))
        if diff_ms == 0:
            counters["exact_millisecond_timestamp"] += 1
            if delta_price == 0:
                counters["exact_executable_quote_price_and_clock"] += 1
        if abs(diff_ms) <= max_anchor_distance_ms:
            counters["anchor_time_within_tolerance"] += 1
            if delta_price == 0:
                counters["exact_price_within_clock_tolerance"] += 1
            else:
                counters["clock_match_quote_price_differs"] += 1
        if delta_price == 0:
            counters["exact_executable_quote_price_regardless_of_clock"] += 1
        if len(misses) < 12 and (abs(diff_ms) > max_anchor_distance_ms or delta_price != 0):
            misses.append({
                "kind": "clock_or_quote_difference",
                "minute_leg_side": key,
                "candidate_minus_merged_ms": diff_ms,
                "candidate_minus_merged_price_cents": delta_price,
            })
    if expected_teacher_rows is not None and counters["original_teacher_rows"] != expected_teacher_rows:
        raise AssertionError("Reference population is incomplete; no subset passes")
    if expected_teacher_net_usd is not None and source_net != expected_teacher_net_usd:
        raise AssertionError("Original R9 economic total differs; no repricing or replacement permitted")
    original_economics_present = (counters["original_teacher_rows"] > 0)
    denominator = counters["source_quote_available"]
    def percentile(data: list[int], numerator: int, denominator: int = 100) -> int | None:
        if not data:
            return None
        x = sorted(data)
        return x[((len(x)-1)*numerator)//denominator]
    return {
        "source": "preexisting_r9_coinexx_merged_reference_only",
        "candidate_mode": "causal_R9_v190_quote_entry_plus_dual_basket_evidence",
        "merged_label_leakage_into_candidate": False,
        "original_fee_or_swap_changes": False,
        "clock_offset_minutes_explicit": clock_offset_minutes,
        "max_anchor_distance_ms": max_anchor_distance_ms,
        "counts": dict(counters),
        "candidate_total": candidate_count,
        "unmatched_candidate_entries": candidate_count - len(used),
        "original_r9_net_usd_unchanged": str(source_net),
        "original_economics_present": original_economics_present,
        "median_absolute_price_difference_cents": percentile(price_errors, 50),
        "p95_absolute_price_difference_cents": percentile(price_errors, 95),
        "median_absolute_time_difference_ms": percentile(timing_errors, 50),
        "p95_absolute_time_difference_ms": percentile(timing_errors, 95),
        "exact_price_same_millisecond_fraction_of_quote_eligible": round(
            counters["exact_executable_quote_price_and_clock"] / max(1, denominator), 6
        ),
        "price_equal_within_tolerance_fraction_of_quote_eligible": round(
            counters["exact_price_within_clock_tolerance"] / max(1, denominator), 6
        ),
        "same_cycle_entry_coverage": round(
            counters["same_minute_leg_side"] / max(1, counters["original_teacher_rows"]), 6
        ),
        "quote_exact_and_time_coverage": round(
            counters["exact_executable_quote_price_and_clock"] / max(1, denominator), 6
        ),
        "limited_mismatch_examples": misses,
        "reference_event_time_is_not_injected_into_candidate": True,
        "certified_exact_replication": (
            original_economics_present
            and counters["original_teacher_rows"] == candidate_count
            and counters["source_quote_missing"] == 0
            and counters["exact_executable_quote_price_and_clock"] == candidate_count
        ),
    }

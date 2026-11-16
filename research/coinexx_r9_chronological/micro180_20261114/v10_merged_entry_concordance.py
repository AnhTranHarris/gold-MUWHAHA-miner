"""Read-only, full-population R9-SYNTH -> Coinexx quote-mark concordance.

The existing merged CSV is a teacher-labelled reference, never a strategy input.
An entry's Coinexx quote is the first tick AFTER entry_time_broker + 1 second;
elag_ms is its latency beyond THAT boundary, not beyond the teacher event.
No historic synthetic fills or alternative fee assumptions are manufactured.
"""
from __future__ import annotations

import csv
import gzip
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable

REQUIRED_COLUMNS = frozenset({
    "entry_time_broker", "exit_time_broker", "month", "leg", "side", "net_usd",
    "equote_ms", "xquote_ms", "elag_ms", "xlag_ms", "q_entry_u", "q_exit_u",
})
MAPPING_MAX_LAG_MS = 2000


def read_merged_rows(path: Path) -> Iterable[dict[str, str]]:
    """Read the EXISTING gzip file; keep every original R9 row and source fee."""
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not REQUIRED_COLUMNS.issubset(reader.fieldnames or []):
            raise ValueError(
                "Unexpected R9-Coinexx merged source schema: missing "
                + repr(sorted(REQUIRED_COLUMNS - set(reader.fieldnames or [])))
            )
        yield from reader


def _stamp_epoch_ms(stamp: str, clock_offset_minutes: int) -> int:
    dt = datetime.fromisoformat(stamp.strip().replace("Z", "+00:00"))
    if dt.tzinfo is None:
        # Broker display times are interpreted only through the EXPLICIT offset.
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp()) * 1000 + clock_offset_minutes * 60_000


def _percentile(values: list[int], n: int) -> int | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[(len(ordered) - 1) * n // 100]


def compare_merged_entries(
    teacher_rows: Iterable[dict[str, str]],
    causal_entries: Iterable[dict[str, Any]],
    *,
    clock_offset_minutes: int = 0,
    max_anchor_distance_ms: int = 3000,
    expected_teacher_rows: int | None = None,
    expected_teacher_net_usd: Decimal | None = None,
    expected_fully_mapped_rows: int | None = None,
) -> dict[str, Any]:
    """Compare autonomous candidate entries to ALL original teacher rows.

    Entry identity: source-native minute, first/second leg, BUY/SELL.
    Metrics distinguish (1) teacher original second, (2) mapped Coinexx quote
    timestamp, (3) executable quote price. A candidate is never spawned from a
    teacher mark. Out-of-window quote marks still retain original R9 economics.
    """
    if not isinstance(clock_offset_minutes, int) or not isinstance(max_anchor_distance_ms, int):
        raise ValueError("Clock offset/tolerance must be integer milliseconds/minutes")
    if max_anchor_distance_ms < 0:
        raise ValueError("Negative timestamp tolerance")

    index: dict[tuple[int, int, int], dict[str, Any]] = {}
    by_minute: dict[int, list[tuple[int, int]]] = {}
    candidate_count = 0
    for entry in causal_entries:
        candidate_count += 1
        minute = int(entry["cycle_minute"])
        leg = int(entry["rearm_number"]) + 1
        side = int(entry["side"])
        if side not in (-1, 1) or leg < 1:
            raise ValueError("Invalid candidate side or leg")
        key = (minute, leg, side)
        if key in index:
            raise ValueError(f"Duplicate autonomous candidate minute/leg/side: {key}")
        index[key] = entry
        by_minute.setdefault(minute, []).append((leg, side))

    c: Counter[str] = Counter()
    source_net = Decimal("0")
    original_net_by_month: dict[str, Decimal] = {}
    used_keys: set[tuple[int, int, int]] = set()
    original_keys: set[tuple[int, int, int]] = set()
    mark_time_errors: list[int] = []
    teacher_time_errors: list[int] = []
    price_errors: list[int] = []
    sample_misses: list[dict[str, Any]] = []

    for row in teacher_rows:
        c["original_teacher_rows"] += 1
        original_net = Decimal(row["net_usd"])
        source_net += original_net
        month = row["month"]
        original_net_by_month[month] = original_net_by_month.get(month, Decimal(0)) + original_net
        s = row["side"].lower().strip()
        if s not in ("buy", "sell"):
            raise ValueError("Invalid teacher side")
        side = 1 if s == "buy" else -1
        leg = int(row["leg"])
        teacher_ms = _stamp_epoch_ms(row["entry_time_broker"], clock_offset_minutes)
        exit_ms = _stamp_epoch_ms(row["exit_time_broker"], clock_offset_minutes)
        minute = teacher_ms // 60_000 * 60
        key = (minute, leg, side)
        if key in original_keys:
            raise ValueError(f"Duplicate original teacher minute/leg/side: {key}")
        original_keys.add(key)

        e_mark = int(Decimal(row["equote_ms"]))
        x_mark = int(Decimal(row["xquote_ms"]))
        e_lag = int(Decimal(row["elag_ms"]))
        x_lag = int(Decimal(row["xlag_ms"]))
        q_entry = int(Decimal(row["q_entry_u"]))
        q_exit = int(Decimal(row["q_exit_u"]))

        if e_mark > 0 and e_mark != teacher_ms + 1000 + e_lag:
            raise ValueError(f"Corrupt entry quote alignment: {key}")
        if x_mark > 0 and x_mark != exit_ms + 1000 + x_lag:
            raise ValueError(f"Corrupt exit quote alignment: {key}")

        entry_mapped = (e_mark > 0 and q_entry > 0
                        and 0 <= e_lag <= MAPPING_MAX_LAG_MS)
        exit_mapped = (x_mark > 0 and q_exit > 0
                       and 0 <= x_lag <= MAPPING_MAX_LAG_MS)
        if entry_mapped:
            c["entry_quote_mapped_le_2s"] += 1
        else:
            c["entry_quote_outside_2s_or_missing"] += 1
        if exit_mapped:
            c["exit_quote_mapped_le_2s"] += 1
        else:
            c["exit_quote_outside_2s_or_missing"] += 1
        if entry_mapped and exit_mapped:
            c["fully_mapped_trade_window"] += 1
        else:
            c["trade_window_not_fully_mapped"] += 1

        candidate = index.get(key)
        if candidate is None:
            c["no_candidate_same_minute_leg_side"] += 1
            observed = by_minute.get(minute, [])
            if observed:
                c["candidate_other_side_or_leg_same_minute"] += 1
            if len(sample_misses) < 20:
                sample_misses.append({
                    "reason": "missing_causal_entry",
                    "teacher_time": row["entry_time_broker"],
                    "minute_leg_side": key,
                    "candidate_other_side_or_leg": observed[:4],
                })
            continue
        used_keys.add(key)
        c["same_minute_leg_side"] += 1
        candidate_time = int(candidate["time_msc"])
        candidate_price = int(candidate["price_u"])
        delta_teacher_ms = candidate_time - teacher_ms
        teacher_time_errors.append(abs(delta_teacher_ms))
        if candidate_time // 1000 == teacher_ms // 1000:
            c["same_original_teacher_second"] += 1
        if candidate_time == teacher_ms:
            c["exact_original_teacher_second_boundary_ms"] += 1

        # Eligibility is based on the archive's *existing* 2s matching rule.
        # A post-event quote may not have existed at the original entry time.
        if not entry_mapped:
            continue
        delta_mark_ms = candidate_time - e_mark
        delta_price = candidate_price - q_entry
        mark_time_errors.append(abs(delta_mark_ms))
        price_errors.append(abs(delta_price))
        if candidate_time == e_mark:
            c["exact_mapped_quote_millisecond"] += 1
        if candidate_price == q_entry:
            c["exact_mapped_quote_price_any_time"] += 1
        if abs(delta_mark_ms) <= max_anchor_distance_ms:
            c["within_mapped_quote_time_tolerance"] += 1
            if delta_price == 0:
                c["equal_quote_price_within_tolerance"] += 1
        if delta_mark_ms == 0 and delta_price == 0:
            c["exact_mapped_quote_time_and_price"] += 1
        if len(sample_misses) < 20 and (delta_mark_ms != 0 or delta_price != 0):
            sample_misses.append({
                "reason": "causal_entry_differs_from_post_second_quote_mark",
                "minute_leg_side": key,
                "candidate_minus_teacher_ms": delta_teacher_ms,
                "candidate_minus_mapped_quote_ms": delta_mark_ms,
                "candidate_minus_quote_price_cents": delta_price,
                "entry_mapping_lag_ms": e_lag,
            })

    if expected_teacher_rows is not None and c["original_teacher_rows"] != expected_teacher_rows:
        raise AssertionError("Incomplete teacher population")
    if expected_teacher_net_usd is not None and source_net != expected_teacher_net_usd:
        raise AssertionError("Original R9 net does not reconcile; never substitute costs")
    if (expected_fully_mapped_rows is not None
            and c["fully_mapped_trade_window"] != expected_fully_mapped_rows):
        raise AssertionError("Full-window source mapping count changed")
    total = c["original_teacher_rows"]
    eligible = c["entry_quote_mapped_le_2s"]
    exact = c["exact_mapped_quote_time_and_price"]
    return {
        "source": "original_r9_coinexx_merged_teacher_marks_only",
        "mapping_rule": "first_source_quote_after_next_full_second_boundary_with_2s_lag_limit",
        "teacher_labels_used_as_strategy_signals": False,
        "candidate_mode": "autonomous_R9_v190_on_real_quotes_plus_micro180_dual_evidence",
        "clock_offset_minutes_explicit": clock_offset_minutes,
        "mapped_mark_tolerance_ms": max_anchor_distance_ms,
        "counts": dict(c),
        "candidate_total": candidate_count,
        "unmatched_candidate_entries": candidate_count - len(used_keys),
        "original_r9_net_usd_unchanged": str(source_net),
        "original_net_by_month_unchanged": {
            k: str(v) for k, v in sorted(original_net_by_month.items())
        },
        "original_fee_or_swap_changes": False,
        "same_cycle_entry_coverage": round(c["same_minute_leg_side"] / max(1, total), 6),
        "same_original_teacher_second_coverage": round(
            c["same_original_teacher_second"] / max(1, total), 6
        ),
        "quote_exact_and_time_coverage": round(exact / max(1, eligible), 6),
        "exact_entry_quote_price_coverage": round(
            c["exact_mapped_quote_price_any_time"] / max(1, eligible), 6
        ),
        "median_abs_teacher_second_delta_ms": _percentile(teacher_time_errors, 50),
        "p95_abs_teacher_second_delta_ms": _percentile(teacher_time_errors, 95),
        "median_abs_mapped_quote_delta_ms": _percentile(mark_time_errors, 50),
        "p95_abs_mapped_quote_delta_ms": _percentile(mark_time_errors, 95),
        "median_abs_quote_price_difference_cents": _percentile(price_errors, 50),
        "p95_abs_quote_price_difference_cents": _percentile(price_errors, 95),
        "limited_mismatch_examples": sample_misses,
        "certified_exact_replication": bool(
            total > 0 and candidate_count == total
            and c["same_original_teacher_second"] == total
            and c["entry_quote_mapped_le_2s"] == total
            and exact == total
        ),
        "limitations": (
            "Event-marked merged CSV has no independent V10 candidate entries. "
            "Exact execution-value replication requires source-ordered real quotes. "
            "An entry can match the original R9 second yet differ from the "
            "later mapped quote price; never force a fill at a future price."
        ),
    }

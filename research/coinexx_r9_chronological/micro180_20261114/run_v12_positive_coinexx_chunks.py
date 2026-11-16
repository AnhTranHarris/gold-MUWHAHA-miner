"""Resumable REAL Coinexx TickLogger positive-clock backtest: NO DATA REBUILD.

Usage (original source parts in chronological order, no extra data copies):

  python run_v12_positive_coinexx_chunks.py \
    --ticks /original/GoldMuwahaha_REAL_part01.csv.gz ... \
    --first-model /frozen/micro180_positive_first_hazard_model.txt \
    --second-model /frozen/micro180_positive_second_hazard_model.txt \
    --merged /original/r9_synthetic_teacher_to_original_REAL_TickLogger_9m_trade_marks.csv.gz \
    --workdir /small_compact_research_results --max-quotes-per-call 200000

Repeat with identical arguments + --resume. Each call consumes one bounded
quote batch, writes only a small compressed candidate-entry ledger and one
checkpoint. No raw ticks/candles warehouse, no model retraining, no data
downloads, no future-family labels fed to entry decisions. All input order is
preserved including equal-ms original quote rows.

Do not use untrusted pickle checkpoints. The --resume flag is explicit, and
source/model identity is validated before loading the trusted own checkpoint.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
import pickle
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
for root in (
    PROJECT / "src", PROJECT / "variable_cash_horizon_20261114",
    PROJECT / "dual_basket_20261114", HERE,
):
    sys.path.insert(0, str(root))

from coinexx_r9.models import Tick, parse_price_units
from coinexx_r9.r9_baseline import R9Config
from v12_positive_clock_router import (
    FrozenLightGBM, Micro180V12PositiveClock, V12PositiveClockSpec,
)
from v12_positive_cycle_targets import read_positive_targets

HEADER = (
    "source_ordinal", "entry_time_msc", "source_minute", "leg",
    "side", "executable_price_cents", "source_quote_bid_ask",
    "original_R9_future_family_used", "model",
)


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for segment in iter(lambda: f.read(1024 * 1024), b""):
            h.update(segment)
    return h.hexdigest()


def _manifest(sources: list[Path], first: Path, second: Path) -> dict:
    return {
        "source_parts": [
            {"path": str(p.resolve()), "size": p.stat().st_size,
             "mtime_ns": p.stat().st_mtime_ns}
            for p in sources
        ],
        "first_model_sha256": _sha(first),
        "second_model_sha256": _sha(second),
        "first_threshold": 0.60,
        "second_threshold": 0.50,
        "model_signals_use_R9_teacher_event_times": False,
        "source_ticklogger_events_used_to_train_online": False,
    }


def _make_engine(first: Path, second: Path) -> Micro180V12PositiveClock:
    cfg = R9Config(
        use_regime_gate=False,
        max_same_minute_rearms=1,
        # Spread and completed M5 ATR remain as-of learned input features;
        # this is the source-entry research gate rather than live permission.
    )
    return Micro180V12PositiveClock(
        cfg, first_model=FrozenLightGBM(first),
        second_model=FrozenLightGBM(second),
        spec=V12PositiveClockSpec(
            first_threshold=0.60, second_threshold=0.50,
        ),
    )


def _read_original_tick_row(fields: dict[str, int], row: list[str], ordinal: int):
    """Original REAL logger 'time' is display text; derive sec from time_msc."""
    time_msc = int(row[fields["time_msc"]])
    bid = parse_price_units(row[fields["bid"]])
    ask = parse_price_units(row[fields["ask"]])
    if bid <= 0 or ask < bid:
        raise ValueError(f"Invalid Coinexx source Bid/Ask at quote {ordinal}")
    t = Tick(ordinal, time_msc // 1000, time_msc, bid, ask)
    atr = float(row[fields["atr"]]) * 100.0
    if atr < 0:
        raise ValueError("As-of prior-M5 ATR cannot be negative")
    return t, atr


def _emit_entries(workdir: Path, chunk_index: int, engine: Micro180V12PositiveClock):
    path = workdir / f"v12_independent_entries_chunk_{chunk_index:05d}.csv.gz"
    tmp = path.with_suffix(".tmp")
    count = len(engine.entries)
    with gzip.open(tmp, "wt", newline="", encoding="utf-8") as h:
        writer = csv.writer(h)
        writer.writerow(HEADER)
        for e in engine.entries:
            side = int(e["side"])
            writer.writerow((
                e["ordinal"], e["time_msc"], e["cycle_minute"],
                int(e["rearm_number"]) + 1, side, e["price_u"],
                "BUY_ASK" if side > 0 else "SELL_BID",
                False, "frozen_positive_cycle_hazard",
            ))
    os.replace(tmp, path)
    engine.entries.clear()
    engine.trades.clear()
    engine.close_observations.clear()
    return path, count


def _save_state(workdir: Path, payload: dict, engine: Micro180V12PositiveClock):
    # Own checkpoint, not market data. Users must not load foreign pickle data.
    tmp = workdir / "v12_state.pickle.gz.tmp"
    with gzip.open(tmp, "wb") as f:
        pickle.dump({"cursor": payload["cursor"], "engine": engine}, f, protocol=5)
    os.replace(tmp, workdir / "v12_state.pickle.gz")
    text_tmp = workdir / "v12_receipt.json.tmp"
    text_tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(text_tmp, workdir / "v12_receipt.json")


def run_one_batch(
    sources: list[Path], first_model: Path, second_model: Path,
    workdir: Path, max_quotes: int, *,
    resume: bool,
) -> dict:
    if max_quotes < 1 or max_quotes > 500_000:
        raise ValueError("Use bounded source batches of 1..500000 quotes")
    if not sources or any(not p.is_file() for p in sources):
        raise FileNotFoundError("Already-existing chronological REAL TickLogger source required")
    workdir.mkdir(parents=True, exist_ok=True)
    identity = _manifest(sources, first_model, second_model)
    receipt = workdir / "v12_receipt.json"
    if resume:
        if not receipt.is_file():
            raise FileNotFoundError("No prior own checkpoint; start without --resume")
        old = json.loads(receipt.read_text())
        if old["immutable_source_and_model"] != identity:
            raise ValueError("Source/model changed: cannot reuse an old checkpoint")
        with gzip.open(workdir / "v12_state.pickle.gz", "rb") as f:
            saved = pickle.load(f)  # Only our own explicitly trusted checkpoint.
        if saved["cursor"] != old["cursor"]:
            raise ValueError("Checkpoint state/receipt cursor mismatch")
        engine = saved["engine"]
        cursor = dict(old["cursor"])
        completed_chunks = list(old["completed_chunks"])
        running_count = int(old["total_entry_candidates"])
    else:
        if receipt.exists():
            raise FileExistsError("Existing checkpoint; use --resume or a new workdir")
        engine = _make_engine(first_model, second_model)
        cursor = {"part": 0, "row": 0, "source_ordinal": 0,
                  "last_time_msc": -1, "chunk_index": 0}
        completed_chunks = []
        running_count = 0

    part_index = int(cursor["part"])
    start_row = int(cursor["row"])
    consumed = 0
    first_ms: int | None = None
    last_ms: int | None = None
    while part_index < len(sources) and consumed < max_quotes:
        with gzip.open(sources[part_index], "rt", newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            try:
                header = next(reader)
            except StopIteration as exc:
                raise ValueError("Empty original source part") from exc
            fields = {name: pos for pos, name in enumerate(header)}
            need = {"time_msc", "bid", "ask", "atr", "run_label"}
            if not need.issubset(fields):
                raise ValueError("Expected ORIGINAL Coinexx REAL TickLogger schema")
            for _ in range(start_row):
                next(reader)  # Decompress-only skip; no redundant state replay.
            rowno = start_row
            for row in reader:
                if consumed == max_quotes:
                    break
                rowno += 1
                cursor["source_ordinal"] += 1
                if row[fields["run_label"]] != "REAL":
                    raise ValueError("Refusing SYNTH source: REAL TickLogger required")
                quote, completed_atr_u = _read_original_tick_row(
                    fields, row, cursor["source_ordinal"]
                )
                if quote.time_msc < cursor["last_time_msc"]:
                    raise ValueError("Source parts are out of chronological order")
                cursor["last_time_msc"] = quote.time_msc
                first_ms = quote.time_msc if first_ms is None else first_ms
                last_ms = quote.time_msc
                engine.asof_source_completed_m5_atr_u = completed_atr_u
                engine.on_tick(quote)
                consumed += 1
            cursor["row"] = rowno
            if consumed < max_quotes:
                # EOF: advance to next original source part, with all engine
                # history/cycle/active position/ATR state preserved.
                part_index += 1
                cursor["part"] = part_index
                cursor["row"] = 0
                start_row = 0

    cursor["chunk_index"] += 1
    chunk_path, new_entries = _emit_entries(workdir, cursor["chunk_index"], engine)
    running_count += new_entries
    completed_chunks.append({
        "chunk_index": cursor["chunk_index"], "processed_quotes": consumed,
        "first_time_msc": first_ms, "last_time_msc": last_ms,
        "new_causal_entries": new_entries, "entry_receipt_file": chunk_path.name,
        "receipt_sha256": _sha(chunk_path),
    })
    report = {
        "immutable_source_and_model": identity,
        "cursor": cursor,
        "completed_chunks": completed_chunks,
        "total_source_quotes": cursor["source_ordinal"],
        "total_entry_candidates": running_count,
        "finished_all_parts": part_index == len(sources),
        "sample_is_source_ordered": True,
        "execution_prices_are_REAL_BID_ASK": True,
        "fee_or_original_R9_teacher_net_altered": False,
        "future_positive_target_labels_used_to_enter": False,
        "position_inventory_is_own_simulated_state": True,
        "input_source_timestamp_schema": "REAL TickLogger time_msc; time display ignored",
        "note": "Full A/B/C precision/recall must be computed against the existing "
                "merged positive-cycle labels after complete source coverage; "
                "a subset checkpoint does not prove whole-population results.",
    }
    _save_state(workdir, report, engine)
    return report


def score_existing_chunks(workdir: Path, merged: Path):
    """Offline scored positive A/B/C targets, never called inside on-tick path."""
    targets, target_report = read_positive_targets(merged)
    target_by_key = {(t.minute * 60, t.leg, t.side): t for t in targets}
    by_family = {
        f: {"matched_side_and_minute": 0, "within_2sec_5c": 0,
            "exact_mapped_quote": 0}
        for f in ("A", "B", "C")
    }
    seen: set[tuple[int,int,int]] = set()
    totals = {"candidate_entries": 0, "matching_target_side_and_minute": 0,
              "entries_without_positive_target": 0}
    for path in sorted(workdir.glob("v12_independent_entries_chunk_*.csv.gz")):
        with gzip.open(path, "rt", newline="") as f:
            for e in csv.DictReader(f):
                totals["candidate_entries"] += 1
                key = (int(e["source_minute"]), int(e["leg"]), int(e["side"]))
                t = target_by_key.get(key)
                if t is None:
                    totals["entries_without_positive_target"] += 1
                    continue
                if key in seen:
                    raise ValueError("One target matched by two separate quote entries")
                seen.add(key)
                totals["matching_target_side_and_minute"] += 1
                row = by_family[t.family]
                row["matched_side_and_minute"] += 1
                delta_time = abs(int(e["entry_time_msc"]) - t.mapped_quote_ms)
                delta_price = abs(int(e["executable_price_cents"])
                                  - t.mapped_bid_ask_entry_cents)
                if delta_time <= 2000 and delta_price <= 5:
                    row["within_2sec_5c"] += 1
                if delta_time == 0 and delta_price == 0:
                    row["exact_mapped_quote"] += 1
    return {
        "teacher_target": target_report,
        "entry_receipts_scored": totals,
        "by_historical_family_posthoc": by_family,
        "family_outcome_known_only_after_execution": True,
        "caveat": "Use full target denominators only after all source parts are complete.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticks", nargs="+", type=Path, required=True)
    parser.add_argument("--first-model", type=Path, required=True)
    parser.add_argument("--second-model", type=Path, required=True)
    parser.add_argument("--merged", type=Path)
    parser.add_argument("--workdir", type=Path, required=True)
    parser.add_argument("--max-quotes-per-call", type=int, default=200000)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--score", action="store_true")
    a = parser.parse_args()
    if a.score:
        if a.merged is None:
            parser.error("--merged required when --score is specified")
        result = score_existing_chunks(a.workdir, a.merged)
    else:
        result = run_one_batch(
            a.ticks, a.first_model, a.second_model, a.workdir,
            a.max_quotes_per_call, resume=a.resume,
        )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

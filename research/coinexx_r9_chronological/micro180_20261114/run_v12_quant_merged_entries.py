"""V12 original-Coinexx executable entry-concordance runner.

Reads each pre-existing REAL TickLogger part ONCE; never caches/sorts/writes
original quotes or injects R9-SYNTH teacher timestamps. The 19-factor entry
model is frozen before replay, with observable 5s/15s baskets and completed
M5 ATR. Output is a single compact JSON receipt.

The entire teacher is passed to compare_merged_entries only AFTER independent
V12 execution finishes. Full historical recall and exact quote-side price
matching are results, never entry triggers.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from decimal import Decimal

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
for p in (PROJECT / "src", PROJECT / "variable_cash_horizon_20261114",
          PROJECT / "dual_basket_20261114", HERE):
    sys.path.insert(0, str(p))

from coinexx_r9.ticks import iter_coinexx_ticks
from v10_merged_entry_concordance import compare_merged_entries, read_merged_rows
from v12_micro180_quant_entry import Micro180V12QuantEntry

EXPECTED_TEACHER_ROWS = 272352
EXPECTED_TEACHER_NET_USD = Decimal("360693.05")
EXPECTED_FULLY_MAPPED_WINDOWS = 270776
EXPECTED_RAW_QUOTE_ROWS = 71794750


def run(
    source_parts: list[Path],
    merged: Path,
    clock_offset_minutes: int,
    *,
    max_ticks: int | None = None,
    certify_full_population: bool = False,
) -> dict:
    if not source_parts or any(not p.is_file() for p in source_parts):
        raise FileNotFoundError("Pre-existing source REAL TickLogger parts required")
    if not merged.is_file():
        raise FileNotFoundError("Pre-existing verified merged R9 reference required")
    if certify_full_population and max_ticks is not None:
        raise ValueError("Bounded sample may not certify full population")
    engine = Micro180V12QuantEntry()
    n = 0
    last_ms = -1
    last_entry_ms = -1
    for part in source_parts:
        # R9 REAL TickLogger's M5 ATR field is an as-of MT5 indicator reading.
        # Retain it for prototype MQL5/iATR proxy concordance, not as an order.
        for tick in iter_coinexx_ticks(
            part, preserve_logger_extras=True, ordinal_offset=n, strict=True
        ):
            if tick.time_msc < last_ms:
                raise ValueError("Out-of-order original source parts")
            last_ms = tick.time_msc
            n += 1
            before = len(engine.entries)
            engine.on_tick(tick)
            if len(engine.entries) > before:
                receipt = engine.entries[-1]
                if receipt["time_msc"] < last_entry_ms:
                    raise ValueError("Noncausal entry ordering")
                last_entry_ms = receipt["time_msc"]
                if receipt["v12_executable_quote_u"] != (
                    tick.ask_u if receipt["side"] > 0 else tick.bid_u
                ):
                    raise AssertionError("Entry value differs from observed source Bid/Ask")
            if max_ticks is not None and n >= max_ticks:
                break
        if max_ticks is not None and n >= max_ticks:
            break
    if certify_full_population and n != EXPECTED_RAW_QUOTE_ROWS:
        raise AssertionError("Source replay is incomplete; cannot certify nine months")
    result = compare_merged_entries(
        read_merged_rows(merged),
        engine.entries,
        clock_offset_minutes=clock_offset_minutes,
        expected_teacher_rows=EXPECTED_TEACHER_ROWS if certify_full_population else None,
        expected_teacher_net_usd=EXPECTED_TEACHER_NET_USD if certify_full_population else None,
        expected_fully_mapped_rows=(
            EXPECTED_FULLY_MAPPED_WINDOWS if certify_full_population else None
        ),
    )
    result.update({
        "source_quote_rows_replayed": n,
        "independent_V12_model": True,
        "V12_trading_entries": len(engine.entries),
        "V12_closed_quotes": len(engine.trades),
        "source_file_parts_used": [p.name for p in source_parts],
        "complete_nine_month_replay": certify_full_population,
        "no_hindsight_teacher_features_at_entry": True,
        "no_broker_orders": True,
        "no_original_coinexx_tick_data_rebuilt": True,
        "v12_frozen_model_context": engine.concordance_summary(),
    })
    return result


def main() -> None:
    a = argparse.ArgumentParser()
    a.add_argument("--ticks", nargs="+", type=Path, required=True)
    a.add_argument("--merged", type=Path, required=True)
    a.add_argument("--clock-offset-minutes", type=int, required=True)
    a.add_argument("--max-ticks", type=int)
    a.add_argument("--full-nine-months", action="store_true")
    a.add_argument("--out-json", type=Path, required=True)
    args = a.parse_args()
    result = run(args.ticks, args.merged, args.clock_offset_minutes,
                 max_ticks=args.max_ticks,
                 certify_full_population=args.full_nine_months)
    args.out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "matched_minute_leg_side":result["counts"].get("same_minute_leg_side",0),
        "matched_original_teacher_second":result["counts"].get("same_original_teacher_second",0),
        "mapped_quote_price_within_5c":result["counts"].get("mapped_quote_price_within_5c",0),
        "extra_V12_entries":result["unmatched_candidate_entries"],
        "v12_total_entries":result["V12_trading_entries"],
        "original_teacher_count":result["counts"]["original_teacher_rows"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

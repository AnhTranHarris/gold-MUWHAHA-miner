"""V10 read-only original-Coinexx parity and existing-merge concordance runner.

Use ORIGINAL existing quote files in chronological order, not rebuilt tick
libraries. The merged R9 file is read only AFTER autonomous entries exist.
Only compact JSON metrics are emitted, never duplicate tick or trade archives.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
for path in (
    PROJECT / "src",
    PROJECT / "variable_cash_horizon_20261114",
    PROJECT / "dual_basket_20261114",
    HERE,
):
    sys.path.insert(0, str(path))

from coinexx_r9.r9_baseline import R9Config, R9HybridGateBaseline
from coinexx_r9.ticks import iter_coinexx_ticks
from v10_r9_dual_concordance import Micro180V10R9Causal
from v10_merged_entry_concordance import compare_merged_entries, read_merged_rows


ENTRY_PARITY_KEYS = (
    "ordinal", "time_msc", "side", "price_u",
    "sl_u", "cycle_minute", "rearm_number",
)


def run(
    quote_paths: list[Path],
    merged_path: Path,
    *,
    clock_offset_minutes: int,
    max_ticks: int | None = None,
    require_full_272352: bool = False,
) -> dict:
    if not quote_paths:
        raise ValueError("Existing Coinexx quote source path(s) required")
    if not merged_path.exists():
        raise FileNotFoundError(f"Existing merged R9-Coinexx file inaccessible: {merged_path}")
    if any(not file.exists() for file in quote_paths):
        raise FileNotFoundError("One or more original quote files are not accessible")
    reference = R9HybridGateBaseline(R9Config())
    candidate = Micro180V10R9Causal(R9Config())
    n = 0
    previous_ms = -1
    for source in quote_paths:
        for tick in iter_coinexx_ticks(source, strict=True):
            if tick.time_msc < previous_ms:
                raise ValueError("Original source files are out of chronological order")
            previous_ms = tick.time_msc
            # Per-file ordinal can restart. Source quote order is still stable.
            tick = replace(tick, ordinal=n)
            n += 1
            reference.on_tick(tick)
            candidate.on_tick(tick)
            if len(reference.entries) != len(candidate.entries):
                raise AssertionError(f"R9 entry count parity failed at tick {n}")
            if len(reference.trades) != len(candidate.trades):
                raise AssertionError(f"R9 exit/rearm count parity failed at tick {n}")
            if reference.entries and any(
                reference.entries[-1][key] != candidate.entries[-1][key]
                for key in ENTRY_PARITY_KEYS
            ):
                raise AssertionError(f"R9 executable entry or side diverged at quote {n}")
            if reference.trades and reference.trades[-1] != candidate.trades[-1]:
                raise AssertionError(f"R9 exit reason/price/order diverged at quote {n}")
            if max_ticks is not None and n >= max_ticks:
                break
        if max_ticks is not None and n >= max_ticks:
            break
    expected = 272352 if require_full_272352 else None
    result = compare_merged_entries(
        read_merged_rows(merged_path),
        candidate.entries,
        clock_offset_minutes=clock_offset_minutes,
        expected_teacher_rows=expected,
    )
    result.update({
        "source_ticks_processed": n,
        "source_quote_files_read": len(quote_paths),
        "original_R9_source_parity": True,
        "original_R9_entries_on_same_quote_sequence": len(reference.entries),
        "v10_entries_on_same_quote_sequence": len(candidate.entries),
        "completed_quote_trade_parity": len(reference.trades),
        "v10_entry_context": candidate.concordance_summary(),
        "run_scope": (
            "full_reference_covered_if_quote_paths_cover_same_9months"
            if require_full_272352 and max_ticks is None
            else "partial_or_bounded_research_no_full_coverage_claim"
        ),
        "no_merged_labels_used_for_entry": True,
        "original_R9_accounting_immutable": True,
        "original_0p01_entry_0p01_exit_commission_preserved_not_recomputed": True,
        "native_MT5_fill_parity_verified": False,
    })
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticks", type=Path, nargs="+", required=True,
                        help="Existing original Coinexx source files in chronological order")
    parser.add_argument("--merged", type=Path, required=True,
                        help="Existing merged r9_synthetic_teacher_to_original_REAL_TickLogger_9m_trade_marks.csv.gz")
    parser.add_argument("--clock-offset-minutes", type=int, required=True,
                        help="Verified source-epoch minus teacher broker-server offset; do not guess")
    parser.add_argument("--max-ticks", type=int)
    parser.add_argument("--require-full-272352", action="store_true")
    parser.add_argument("--out-json", type=Path)
    args = parser.parse_args()
    if args.max_ticks is not None and args.max_ticks < 1:
        parser.error("--max-ticks must be positive")
    report = run(
        args.ticks,
        args.merged,
        clock_offset_minutes=args.clock_offset_minutes,
        max_ticks=args.max_ticks,
        require_full_272352=args.require_full_272352,
    )
    output = json.dumps(report, indent=2, sort_keys=True)
    if args.out_json:
        args.out_json.write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()

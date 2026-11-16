"""Single-pass original Coinexx quote replay for independent Micro180 V11.

No copied ticks, no rebuilt 1s files, no teacher timestamp injected at decision.
Compare independent V11 with source-equivalent two-leg R9 control, THEN score
both against the existing merged 272,352-row R9 SYNTH->Coinexx quote marks.
Write one bounded summary JSON. Requires original source tick files to be
available locally; no automatic download or temporary data archive.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
for p in (PROJECT / "src", PROJECT / "variable_cash_horizon_20261114",
          PROJECT / "dual_basket_20261114", HERE):
    sys.path.insert(0, str(p))

from coinexx_r9.r9_baseline import R9Config, R9HybridGateBaseline
from coinexx_r9.ticks import iter_coinexx_ticks
from v11_micro180_independent_dual_entry import Micro180V11DualEntry
from v10_merged_entry_concordance import compare_merged_entries, read_merged_rows


ENTRY_KEYS = ("ordinal", "time_msc", "side", "price_u", "sl_u",
              "cycle_minute", "rearm_number")
ORIGINAL_FULL_TRADES = 272352
ORIGINAL_FULL_NET = Decimal("360693.05")
ORIGINAL_FULL_MAPPED_WINDOWS = 270776
ORIGINAL_FULL_QUOTE_ROWS = 71794750


def execute(
    quote_paths: list[Path],
    merged_path: Path,
    clock_offset_minutes: int,
    *,
    max_ticks: int | None = None,
    full_nine_months: bool = False,
) -> dict:
    if not quote_paths or not merged_path.is_file():
        raise FileNotFoundError("Supply the already-existing merged and original Coinexx sources")
    if any(not p.is_file() for p in quote_paths):
        raise FileNotFoundError("At least one original source quote part is unavailable")
    if full_nine_months and max_ticks is not None:
        raise ValueError("A bounded replay cannot claim full 9-month verification")
    if max_ticks is not None and max_ticks <= 0:
        raise ValueError("max_ticks must be positive")

    cfg = replace(R9Config(), max_same_minute_rearms=1)
    source_r9 = R9HybridGateBaseline(cfg)
    micro = Micro180V11DualEntry(cfg)

    n = 0
    prior_ms = -1
    for part in quote_paths:
        # Each part is supplied IN order. Source internal equal-ms row order
        # remains unmodified. The iterator manages monotonic original ordinals.
        for t in iter_coinexx_ticks(part, ordinal_offset=n, strict=True):
            if t.time_msc < prior_ms:
                raise ValueError("Original source parts must be chronologically ordered")
            prior_ms = t.time_msc
            n += 1
            n_entry = len(source_r9.entries)
            n_close = len(source_r9.trades)
            source_r9.on_tick(t)
            micro.on_tick(t)
            if len(source_r9.entries) != len(micro.entries):
                raise AssertionError(f"Independent V11 count diverges from source R9 at quote {n}")
            if len(source_r9.trades) != len(micro.trades):
                raise AssertionError(f"Independent V11 close/rearm diverges at quote {n}")
            if len(source_r9.entries) > n_entry:
                a, b = source_r9.entries[-1], micro.entries[-1]
                if any(a[k] != b[k] for k in ENTRY_KEYS):
                    raise AssertionError(
                        f"Independent V11 quote-side/time/leg mismatch at quote {n}: "
                        f"ref={tuple(a[k] for k in ENTRY_KEYS)}, "
                        f"dual={tuple(b[k] for k in ENTRY_KEYS)}"
                    )
            if len(source_r9.trades) > n_close and source_r9.trades[-1] != micro.trades[-1]:
                raise AssertionError(f"Independent V11 closed trade mismatch at quote {n}")
            if max_ticks is not None and n >= max_ticks:
                break
        if max_ticks is not None and n >= max_ticks:
            break

    if full_nine_months and n != ORIGINAL_FULL_QUOTE_ROWS:
        raise AssertionError("Incomplete 71,794,750-row original Coinexx logger source")
    merged_report = compare_merged_entries(
        read_merged_rows(merged_path), micro.entries,
        clock_offset_minutes=clock_offset_minutes,
        expected_teacher_rows=ORIGINAL_FULL_TRADES if full_nine_months else None,
        expected_teacher_net_usd=ORIGINAL_FULL_NET if full_nine_months else None,
        expected_fully_mapped_rows=ORIGINAL_FULL_MAPPED_WINDOWS if full_nine_months else None,
    )
    merged_report.update({
        "micro180_v11_independent_candidate_source": "causal_coinexx_source_quotes",
        "reference_source_exact_r9_two_leg_parity": True,
        "micro180_independent_router_used": True,
        "r9_baseline_entry_method_used_to_trigger_v11": False,
        "quote_rows_processed": n,
        "source_parts_read": [p.name for p in quote_paths],
        "full_nine_months_attempted": full_nine_months,
        "full_nine_months_certified": bool(full_nine_months and n == ORIGINAL_FULL_QUOTE_ROWS),
        "v11_summary": micro.concordance_summary(),
        "source_equivalent_r9_entries": len(source_r9.entries),
        "v11_autonomous_entries": len(micro.entries),
        "source_equivalent_r9_closed_positions": len(source_r9.trades),
        "v11_closed_positions": len(micro.trades),
        "original_R9_synthetic_net_is_not_real_quote_execution_pnl": True,
        "native_mt5_ea_compilation_or_fills_certified": False,
    })
    return merged_report


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--ticks", nargs="+", type=Path, required=True,
                   help="Existing original REAL TickLogger CSV.gz parts in chronological order")
    p.add_argument("--merged", type=Path, required=True,
                   help="Existing verified R9-Coinexx merged teacher CSV.gz")
    p.add_argument("--clock-offset-minutes", type=int, required=True,
                   help="Verified source epoch minus server clock, never inferred")
    p.add_argument("--max-ticks", type=int)
    p.add_argument("--full-nine-months", action="store_true")
    p.add_argument("--out-json", type=Path, required=True)
    args = p.parse_args()
    result = execute(args.ticks, args.merged, args.clock_offset_minutes,
                     max_ticks=args.max_ticks, full_nine_months=args.full_nine_months)
    args.out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "full_nine_months": result["full_nine_months_certified"],
        "source_quote_rows": result["quote_rows_processed"],
        "independent_v11_trades": result["v11_autonomous_entries"],
        "teacher_rows": result["counts"]["original_teacher_rows"],
        "teacher_entry_recall": result["same_cycle_entry_coverage"],
        "exact_mapped_quote_time_and_price": result["counts"].get(
            "exact_mapped_quote_time_and_price", 0
        ),
    }, sort_keys=True))


if __name__ == "__main__":
    main()

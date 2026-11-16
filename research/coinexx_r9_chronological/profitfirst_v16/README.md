# R9 V16 — Winner-first causal execution research

This is **research only**. The original R9/V8/V9/V10/V11/V12/V13 trading and broker-execution code is frozen and not modified.

## Goal and release gates
We are targeting: (1) **positive complete-system net cash after executable Bid/Ask and costs**, (2) **a majority of trades profitable**, (3) at least **95% of the original 338,064-trade volume** without increasing broker risk or martingale. A result with negative total net is **NOT** a successful trading policy regardless of positive incremental improvement.

Historical V14 **128,203 positive V9 lifecycles** motivated two causal online states:
- Clean continuation: already-observed entry-to-harvest path contains no adverse 10-cent liquidation-side move.
- Recovery: adverse-first movement has been seen by the current 250ms/1s quote clock, without consulting final trade outcome.

## Tested research modules

- `causal_lifecycle_v16.py`: conservative causal source-ordinal 250ms/1s early-exit observations, only actionable before existing original exit.
- `harvest_extension_v16.py`: after an **already observable** cash-harvest event, a proposed bounded 1s/3s/5s clean-momentum continuation or shorter fast-protected continuation. Uses original source quote order, next-quote side execution, fixed 30-cent observed liquidation stop and quote-gap handling. Comparison includes original-entry overlap suppression.
- `recovery_salvage_v16.py`: smaller positive cash harvest on adverse-first observations at 250ms/1s. Three development months studied; not released.
- `source_1s_specialists.py` and `source_1s_reversal.py`: independent completed-one-second breakout and sweep/reclaim source-quote specialists, their contrarian controls. These have not qualified for positive complete-system cash.
- `aggregate_v16.py`: combines only existing compact derived month results; never re-reads or downloads raw tick files.
- `test_v16_profitfirst.py`: source ordinal and same-ms ordering, next-quote action, Bid/Ask, no after-exit decisions, and gap abstention.

All quote inputs are the **preexisting** Jan–Sep 2026 original Coinexx `.csv.gz` files under `COINEXX_DATA_ROOT`, independently SHA-matched to the original `V12_MONTHLY_SOURCE_PROOF.csv`. No new tick library is generated.

## How to reproduce locally

Provide Python 3.11+, numpy and pandas plus the **already existing** source files and V12 exact-ms event ledgers. For a sample:

```bash
export COINEXX_DATA_ROOT=/path/to/existing/coinexx/months
export V12_EVENT_LEDGER_ROOT=/path/to/existing/v12/derived_events
export V16_RESEARCH_OUT=/path/to/small/derived/results
python research/coinexx_r9_chronological/profitfirst_v16/harvest_extension_v16.py 01 05 09
python research/coinexx_r9_chronological/profitfirst_v16/causal_lifecycle_v16.py 01 05 09
# Run the SAME commands for the other six months before aggregation:
# python research/coinexx_r9_chronological/profitfirst_v16/aggregate_v16.py
```

For full nine-month aggregation, repeat the **same frozen code** for months `01` through `09` before calling aggregate. Note that the aggregate currently also expects small independent 1s development artifacts from Jan/May/Sep. Complete exact nine-month full-period result is preserved in the local downloadable V16 evidence package; **no original tick rows are placed in GitHub**.

## Latest nine-month V16 qualification status

| Candidate | Retained matched V9 opportunities | Modeled incremental cash | New total net | Positive-trade rate | Result |
|---|---:|---:|---:|---:|---|
| Clean 5s harvest extension | 332,218 / 338,064 (98.271%) | +$3,825.26 | −$131,492.37 | 32.383% | **Not qualified** |
| Fast protected 1.5s extension | 338,064 / 338,064 (100%) | +$509.20 | −$134,808.43 | 37.043% | **Not qualified** |
| Original V9 baseline | 338,064 (100%) | $0 | −$135,317.63 | 37.923% | Existing research control |

The 5s result has **nine positive incremental monthly comparisons**, but a fixed-entry replay yields only **+$1,545.90**. The remainder of its +$3,825.26 relative matched-calendar difference occurs because longer holds block some original trades; this is not full dynamic V9 rearming. Report it precisely as a *collision-aware matched-original-signal experiment*, **not certified complete-system profit or prediction accuracy**.

## Scientific qualification still missing

- Recompute V9 signal state after every changed exit; do not rely only on the frozen original signal schedule.
- Demonstrate restored profitable-trade rate ≥50%, net above zero and ≥95% volume under full-system account governor and stress-spread/slippage assumptions.
- Freeze one causal rule using early development dates and validate on genuinely untouched later data. Jan–Sep has repeatedly been reused for research, so its monthly slices are not untouched OOS.
- MetaEditor compile, MT5 native-Python parity, and real DEMO fill/commission behavior before any native trading policy change.
- **No EA rebuilt, no order permissions enabled, no broker stop changed, no martingale or averaging down**.

See `V14_POSITIVE_WINNER_BASELINE_20261115.md` for exact positive-lifecycle definitions and `V16_POSITIVE_CAPTURE_REPORT_20261115.md` for the full chronological study and limitations.

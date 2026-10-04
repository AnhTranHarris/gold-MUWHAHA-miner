# DELTA R037 — PLSR C01 Month-by-Month Surrogate Validation — Checkpoint 16C

**Status:** COMPLETE MONTHLY ROBUSTNESS FAIL / ACTIVE PROMOTION RETIRED  
**Unit:** R037_PLSR_C01_MONTH_BY_MONTH_SURROGATE_VALIDATION  
**Parent:** R037_PLSR_C01_INDEPENDENT_VALIDATION_CHECKPOINT_16B  
**Candidate:** R037-PLSR-C01_PDH_PDL_S5_RECLAIM  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**Months:** 2026-02 through 2026-07  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Purpose

Test whether the unchanged PLSR-C01 previous-day-high/low sweep-and-S5-reclaim entry source survives month-isolated February-July validation after its Stage-A and later-January independent passes.

No month-specific tuning, no PDH-only/PDL-only rescue, no timeframe changes, and no lifecycle retuning were allowed.

## Timeout-safe execution

Each month was executed as a separate bounded job using the committed producer:

`research/delta/experiments/delta_r037_plsr_c01_monthly_validation.py`

Producer commit: `e8ab95ddee0ac07cc8b223e6b16ca56dd890bf0d`  
Blob: `46d01ab6800eabb3c2f0a87d71ee999ac03eeba6`  
SHA-256: `7405e85cb693ebbaa4a163e9d4d86c45606649139771a8fef68ef108d99860e6`

The project recovery runner constrained each process, isolated Numba cache state, enabled faulthandler/unbuffered execution, and preserved outputs month-by-month before the next month began.

ChatGPT message-delivery timeouts were treated as transport/session interruptions only. No completed monthly result was rerun solely because a message timed out.

## Monthly results

| Month | Trade Δ | Official-win Δ | Net Δ | PLSR entries | Direct PLSR net | Monthly screen |
|---|---:|---:|---:|---:|---:|---|
| 2026-02 | +17 | +6 | -$4.08 | 17 | -$5.01 | FAIL |
| 2026-03 | +23 | +9 | -$6.20 | 23 | -$6.21 | FAIL |
| 2026-04 | +21 | +8 | -$6.78 | 21 | -$6.78 | FAIL |
| 2026-05 | +20 | +8 | -$6.34 | 20 | -$6.34 | FAIL |
| 2026-06 | +18 | +8 | -$2.78 | 18 | -$2.78 | FAIL |
| 2026-07 | +22 | +10 | -$0.92 | 22 | -$1.88 | PASS loose monthly screen only |

## Aggregate

- Incremental trades: **+121**
- Official-win delta: **+49**
- Aggregate incremental net: **-$27.10**
- Direct PLSR net: **-$29.00**
- Incremental net per added trade: **-$0.224**
- Nonnegative-net months: **0 / 6**
- Months within the preregistered -$2 single-month tolerance: **1 / 6**
- Worst month: **April, -$6.78**
- Combined trade count non-lower: **6 / 6**

## Robustness-gate decision

The candidate fails the preregistered monthly robustness gate.

It preserves activity and adds official winners, but the added entries have negative aggregate economics. The failure is broad rather than isolated to one month, so the correct action is not threshold retuning or a post-hoc PDH/PDL split.

**Decision:** retire PLSR-C01 from the active promotion path and retain it only as forensic/reserve evidence.

## Next bounded unit

`R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`

Goal: harvest a new causally independent entry source, preregister its mechanism and bounded candidate set, then run tick-rooted Stage-A screening. Existing PLSR monthly results must not be used to engineer a post-hoc rescue.

Compact checkpoint:
`research/delta/reference/DELTA_R037_PLSR_C01_MONTHLY_VALIDATION_CHECKPOINT_16C.json`

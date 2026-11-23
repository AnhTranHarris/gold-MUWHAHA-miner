# R9 HybridGate — MERGED-PRIMARY RECONSTRUCTION, source-exact restart 2026-11-23

## GOVERNING SOURCE CONTRACT — DO NOT SUBSTITUTE EARLIER V7–V11 ENTRY STREAMS

The owner's **NEW January–September 2026 R9+Coinexx merged trade dataset** is the sole PRIMARY historical trade ledger for reconstruction. Use its exact mapped Coinexx entry and exit **source quote ordinals**, not independently regenerated R9 minute entries, as the first replay baseline. Replay original Coinexx MT5 TickLogger gzip quotes in ordinal order. The user has authorized heavy in-sample development over ALL nine months.

**Complete executable C++17/Python source and reproducible tests:** [MT5_EXPAND source-only V1](https://drive.google.com/file/d/1eFFh6Ip6_ITx7RcP5qdPO1sIRcrO2uMa/view). ZIP SHA256: `6d39cbdd2016b66673d072daa49b9cff3e952ba33c2294894ed80f8bfc94e386`; 533,609 bytes, 32 members. This branch is source-contract/rollback checkpoint; the compiled engine, exact source loader, nine-month receipts, model scripts and fitted exploratory artifacts are inside that ZIP, not embedded in this GitHub README.

### Exact input identities

1. PRIMARY merged January archive: `R9_JAN_COINEXX_HYPOTHETICAL_OUTCOME_OVERLAY_V1_20261122.zip` (27,980 trades).
2. PRIMARY merged February–September archive: `R9_FEB_SEP_COINEXX_244372_OUTCOME_ALIGNED_MERGE_V1_20261122.zip` (244,372 trades).
3. Original Coinexx MT5 TickLogger `XAUUSD_MT5_BROKER_2026_MM_ticks_ALL.csv.gz` monthly January–September (72,129,347 ordered quotes).
4. Historical original R9 source `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5`, Git blob SHA `7eecb5f1947017a01ce85b2520725de54749e523` (UNCHANGED).

### Exact nine-month execution readback (completed)

| Month | Source quotes | Merged trades | Source-quote fee-inclusive matched net |
|---|---:|---:|---:|
| January | 7,699,274 | 27,980 | +$41,520.82 |
| February | 7,102,818 | 33,523 | +$66,213.65 |
| March | 8,859,103 | 40,985 | +$75,698.63 |
| April | 7,831,685 | 31,758 | +$38,353.96 |
| May | 8,011,360 | 28,913 | +$29,545.35 |
| June | 9,347,508 | 31,801 | +$35,348.30 |
| July | 8,075,197 | 25,277 | +$23,085.85 |
| August | 7,468,061 | 25,663 | +$25,682.83 |
| September | 7,734,341 | 26,452 | +$25,243.66 |
| **Total** | **72,129,347** | **272,352** | **+$360,693.05** |

Every mapped quote ordinal/timestamp/bid/ask and two-cent roundtrip fee mathematical trade net independently verified against gzip sources in C++17. Source-prefix test 1,200,000 January quotes and 3,884 fully contained trades: all 31 output market-state/path columns match full month exactly. No new tick libraries generated or uploaded.

The baseline is an **exact reconstruction of the owner's merged historical trade ledger**, **NOT** a proven self-directed live EA: the recorded pairs were outcome-matched when the merge was created. Future knowledge is allowed in research labels but NEVER in inference state. This distinction does **not** demote the merged dataset as controlling research data.

### Current implementation

- `prepare_merge_ledger.py`: reads original ZIP members, pins original trade order, original sides/legs/results, maps quote entry and exit.
- `merged_ledger_tick_replay.cpp`: C++17/zlib streaming tick exact source-quote ordinal fill/exit engine; completed 250ms, 1s, 5s, 15s, 30s, M1, M5, M15 and H1 as-of candle states; in-trade excursion and chronological account diagnostics.
- `qa_reconciled.py`, `qa_causal_prefix.py`: exact nine-month book and non-anticipation checks.
- `analyze_primary_ledger.py`: original mapped-trade family, path and entry-condition comparisons.
- `train_adverse_state.py`: prototype **heavy in-sample** adverse-excursion model on pre-entry Coinexx state; fitted training AUC approximately 0.687 (NOT future performance).
- `train_merged_entry_policy.py`: negative-control mean-payoff regressors; a model that only learns cohort averages is not an advanced executable opportunity policy.

### Mandatory next mechanism work

Within the original R9 minute-bracket/S1/M5 ATR/opposite-rearm architecture, derive quote-tick **live exit/hold and recovery** decisions from *these mapped entries and their observed real-tick paths*. Fit a full-cycle WAIT/ENTER/HOLD/HARVEST/ABORT/REARM controller with as-of completed candles and observed MAE/MFE, no source-future leakage; grade independent quote-by-quote real-tick replay and capital survival against **each** of nine frozen 90%-net floors. Preserve high frequency. Never restart by substituting the V7–V11 independently generated R9 entry schedule, stop at a summary or rebuild raw tick libraries.

**No production/approved EA changes, no native MT5 compilation, and no broker-execution certification in this checkpoint.**

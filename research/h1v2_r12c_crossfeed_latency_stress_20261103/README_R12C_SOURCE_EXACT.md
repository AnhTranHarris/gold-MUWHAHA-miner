# R12C — FROZEN-ORACLE CROSS-SOURCE EXECUTABLE-LATENCY / SPREAD STRESS

2026-11-03. **Independent add-only research branch.** Source parent: `carson/h1v2-r12bn-native-quarter-source-verification-20261103` commit `638974629c434efd8360b03db2e274e361b81479`. This is **neither** a prospective causal entry model, nor an actual Coinexx trade-fill receipt, nor a modification to MT5 EA.

## 0. Mandatory source lineage and continuation

Original unabridged previous R12 append-only Google Doc https://docs.google.com/document/d/1v0X5Vkif81qV784Ja6FVe5DfyQLx7RoEw-yjC4m7D1Y/edit and 47-object R11 master forensic package https://drive.google.com/file/d/1hsUSUyF3GJbtRSFR1c9mtDo-44EK_Rap/view are immutable. Also keep R11 251k original ledger https://docs.google.com/document/d/1eGC-vxRDzu7FxQOY-3PPUfWzoVRrOZU5jaDozuuv0xI/edit, R12D and R12BN full original source/traces. Supplementary R12C recovery ledger in MT5_EXPAND https://docs.google.com/document/d/1iVv1tAmJlBWhNfXMcw2N50VEVIFrawMObGOzyfUGWmI/edit . Preserve original source log hashes, failed experiments and all quote ordinal traces.

## 1. Distinct scientific hypothesis and falsification

**R12C-H01** The original observed first-250ms, future-informed strict full30 SAFE + first15 net favorable teacher max-count signals may be heavily vulnerable to fill latency and even small spread/extra friction. Two separate exercises are necessary: (A) a *frozen-signal* on-quote execution stress, without reselection; (B) a later distinct counterfactual latency-aware reoptimization as an upper bound. **R12C implements only A.** It is not a new hyperparameter fit or a causal inference that a model can know those signal timestamps.

Null: each quote source's frozen hindsight signal count, precision and quarter/hour parity are invariant under delayed executable quote and supplemental roundtrip friction. Falsify by exact bid/ask quote-replayed counters. Positive controls: reproduce the independent historical original R12BR isolated-hour BUY+SELL baseline firstTP selection exactly on **each** of three sources. Negative controls: future quote gaps, source end and invalid or delayed broker spread reject, wrong side price, skip while busy, no free immediate retry after failed execution; both-side entry/exit slippage. True high frequency execution viability remains not established without broker order/fill data.

## 2. Sources and exact hour

Original MT5 Strategy Tester ticklogger archived `R9_REAL_2026-02-02_ticks.csv.gz` SHA256 `24e4b31935ead7b0eb039fe84dc8972c59500b362cac21721739f1b0c050b3d7`, original `R9_SYNTH_2026-02-02_ticks.csv.gz` SHA256 `dcedb28f7453c80d2dec5ffe5d386dad1661134ba61765337155fbbaeb6213a2`, and original Dukascopy full Feb `XAUUSD_DUKAS_2026_02_ticks.csv.gz` SHA256 `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d`. All three original GZIP full byte SHA independently verified by executable source. R9 tester timestamp source aligns UTC after -2hr February correction, Dukas native timestamp already UTC. Raw integer `0.001 USD` quote price units; fees $0.02 research nominal. Tested 2026-02-02T06:00:00Z through 06:59:59.999Z with 6min past warmup and +45s future quote halo; original R9 SYNTH source exact benchmark **104** entries in this hour. This is a deliberately acute problem hour, not an out-of-sample performance estimate.

## 3. Source eligibility and original future-known baseline

No stale admission: source >15s quote drought reset, 300s warmed past-only bid/ask history, nonnegative spread <= $1.50, first actually observed quote of each occupied 250ms bin (no end-of-bin future). Independently label executable BUY entry at Ask + close Bid and SELL entry Bid + close Ask with source fee $0.02, +$0.10 nominal executable net by 15s AND no future >$0.10 opening-liquidation-side adverse through entire 30s. Quote gaps/source end censor. Original early first observed future favorable quote is TP *exit event*, and next chosen future-known signal strictly after last TP exit ordinal/time. Original source handoff exact baseline first250 strict candidate / nonoverlap expected: R9 REAL MT5 tester 1,520 / **705**, R9 SYNTH MT5 tester 6,247 / **1,853**, Dukas raw six / **six**, matching previous independently authored R12BR SHA-verified witness. Hindsight opportunity quality is by design selected using FUTURE prices; no claim of accuracy 100% under live signal decisions.

## 4. New delayed quote experiment, frozen original signals

For each originally selected nominal source signal, delay hypothetical order time by zero, 50, 100, 250, 500 or 1,000 ms. Execute **only** on first later real observed quote at or after specified delay; reject if >1,000ms beyond requested fill target, spread >$1.50, or fill moves outside original hour. At zero ms, reproduce original ideal quote benchmark. Do not consult future for fill eligibility except the observation at actual fill. Apply optional fixed extra positive adverse slippage of 0, $0.020, or $0.050 **at both entry AND exit**; the extra roundtrip cost is 2x the stated per-side number. Recompute +$0.10 net first favorable *after delayed fill* within 15s and full30 zero -$0.10 adverse relative executable opening liquidation; missing quotes/gaps censor. Each successful position is occupied until first observed favorable TP quote; a failed executed position is conservatively occupied for full30s. This failure default is **not** the R9 live stop/trail/timeout; because the failed path economics are not executed, R12C does **NOT** compute true expected profit/portfolio equity. Crucially, future outcome information is never used to *replace* failing nominal signals. Every source/scenario records skipped-busy, fill reject, completed-good, completed-bad, source-censored counts separately.

**Critical mathematical restriction:** 100% strict correct at ZERO simulated delay remains pure oracle hindsight tautology. After delay, quote transitions are path dependent; a failure is not merely a late quote. Passing trade count from a future-informed signal under one historical feed does not establish a usable training policy or viable execution. Source `REAL` is MT5 tester recorded REAL tick mode, **not** Coinexx historical live quote or broker trade fill certification. Source SYNTH is model-generated Strategy Tester tick mode; the two should not be merged or called two independent brokers. Only Dukascopy is the independent raw vendor historical feed here.

## 5. Complete output and reproduction

- `R12C_ALL_54_SOURCE_LATENCY_SLIPPAGE_SCENARIOS.csv`: 3 original source domains x6 lag clocks x3 per-side slippage conditions, with full raw counts and 104 benchmark; all 54 rows, no omitted negatives. Correct strict performance must use *completed fill* count, not count all oracle signals or silently drop rejected/busy actions.
- `R12C_SOURCE_AND_RESULT_RECEIPT.json`: full original source SHA, first-250 good and frozen teacher selected count plus source price spread median, research limitations and scenario file SHA.
- `*FROZEN_ORACLE_SIGNAL_STRESS.npz` (24 files): all original baseline source quote ordinals and times and source sides, every corresponding stress fill/exit quote ordinal, per-signal outcome code, net **only for good closing TP**, sentinel for failure; coverage for lag 0/100/500/1000, slippage 0/50. Missing other 30 scenarios have exact aggregate CSV rows; future work may emit all 54 per-signal when needed.
- `R12C_SHA_MANIFEST.json`: exact bytes and SHA for every saved file except self. `unit_test_final.log`: 10 passing tests. `execution_final.log` preserves original receipts.
- `source/r12c_latency_and_execution_stress.py` and `tests/test_r12c_latency_contract.py`: exact original executable, never a rewrite of R9 v2 or R12D source.

Command using the original source environment, Python 3.11, numpy, pandas, numba:

```
PYTHONPATH=<R12_ENGINE_DIR>:<R11S1_UPSTREAM_DIR> python source/r12c_latency_and_execution_stress.py \
  --real R9_REAL_2026-02-02_ticks.csv.gz \
  --synth R9_SYNTH_2026-02-02_ticks.csv.gz \
  --dukas XAUUSD_DUKAS_2026_02_ticks.csv.gz \
  --engine-dir <R12_ENGINE_DIR> --out <NEW_RESULTS_DIR>
PYTHONPATH=source pytest -q tests/test_r12c_latency_contract.py
```

Failure log: first local check had 9/10 tests because one synthetic fixture was only 40s long and tested a 31s entry's full30 horizon. This is correct missing-source censor, not source algorithm failure. Extended the test fixture to 80s; 10/10 PASS. During code review, fixed a boundary-horizon coverage condition to honor the original S1 straddling-quote condition and observation exactly at horizon; no historical source modification. All original three-source zero-lag baseline parity checks then passed.

## 6. Data accounting and limits

For every scenario distinguish lost due quote rejection, lost to earlier stressed position occupancy, true failed fills, censored fills, and strict successful quote-based outcomes. Do NOT pool source failures or report native on one stream as executable on another. Trial is one acute historical hour, explicitly in-sample and already research exposed. No train/test split is claimed, no live-account risk, no MQL5 compile, no portfolio/net on losses, no actual order-market latency, no prop firm broker permission proof, no commission/mark-to-market conversion to 0.01 lot verified. Subsequent research must fit a **causal** observed-quote side+WAIT admission and validate execution with broker-native fills and unseen chronological windows, then re-evaluate all source months and quarters. Maintain the original strict 15/30 survival contract, source SHA, and R11/R12 negative studies as frozen.

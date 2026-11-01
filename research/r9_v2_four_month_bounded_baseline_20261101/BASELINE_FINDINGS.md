# Gold MUWHAHA Miner R9 Router v2 — Frozen Default Entry Baseline

**Run date:** 2026-11-01  
**Authoritative entry source:** `carson/r9-probabilistic-entry-router-v2-20261101` commit `35056fa38c11a7b2e9b9d6bab984af3368e905be`  
**Status:** BOUNDED RESEARCH EVALUATION. **NOT a full-month entry-performance baseline; NOT approved for MT5/demo/live.**

## Direct result

The unchanged v2 Bayesian first-passage/NP BUY/SELL/WAIT policy was fitted with original defaults on earlier source-labelled samples, NP-calibrated on subsequent samples, and scored on four later development-check dates, one per research month, independently for Coinexx and Dukascopy real quote streams. Selected trade paths were enforced nonoverlapping by source. No hyperparameter tuning, filter weakening, indicator or trade exit alteration took place.

| Dev-check date | Coinexx trades | Coinexx net | Coinexx win % | Dukascopy trades | Dukascopy net |
|---|---:|---:|---:|---:|---:|
| 2026-01-27 | 18 | -$2.18 | 55.56% | 0 | $0.00 |
| 2026-02-26 | 13 | -$3.23 | 38.46% | 0 | $0.00 |
| 2026-06-25 | 0 | $0.00 | N/A | 0 | $0.00 |
| 2026-07-28 | 4 | -$1.00 | 50.00% | 0 | $0.00 |
| **Total** | **35** | **-$6.41** | **48.57%** | **0** | **$0.00** |

Aggregate selected-trade performance: gross wins +$3.01, gross losses -$9.42, profit factor **0.3195**, mean **-$0.1831/trade**, observed peak-to-trough closed-trade cumulative loss **$6.97**, average spread at entry **$0.1929**. With an *additional* $0.18/trade fee as a transparent sensitivity (i.e. total fee $0.20 vs built-in $0.02), Coinexx net would be **-$12.71**. This fee stress is not a broker commission confirmation.

All **64,515,445 quotes across eight monthly archives** were parsed to maintain historical minute geometry. On each of the four predetermined development days/month/source, only the fixed UTC windows starting 00:00, 06:00, 12:00 and 18:00 were evaluated for entry decisions. Each window contained a 5-minute local warm-up followed by at most 100 500ms decision-point snapshots. The collector produced **25,536 independently simulated hypothetical BUY/SELL action paths** across the fit/calibration/dev windows. **These are NOT trades.** Only 35 actually selected nonoverlapping development-check actions were counted as trades.

### Unselected hypothetical opportunity economics (dev-check windows only)

- Coinexx Jan/Feb/June/July: 800 BUY/SELL paths per month; approximate mean net per hypothetical path **-$0.205, -$0.210, -$0.223, -$0.219**, respectively; observed win fractions **43.75%, 43.63%, 43.88%, 47.00%**.
- Dukascopy: 800 paths per month; approximate mean net **-$0.661, -$0.781, -$0.670, -$0.702**, with win fractions **26.88%, 27.00%, 27.63%, 18.50%**.
- Dukascopy dev-window average spread approximately **$0.63–$0.77** versus Coinexx **$0.19–$0.21**. The same policy selected **zero Dukascopy trades**; that is abstention, not a $0-profit cross-broker success.

### Four frozen chronological folds

| Fold | Fit observations | NP calibration paths | Scored date | Status |
|---|---:|---:|---|---|
| Jan | 3,200 | 1,600 | 2026-01-27 | completed |
| Feb | 9,536 | 1,600 | 2026-02-26 | completed |
| June | 15,936 | 1,600 | 2026-06-25 | completed |
| July | 22,336 | 1,600 | 2026-07-28 | completed |

Fitting/calibration never uses labels from a future scored day. The synthetic R9 annotation weights only already-favorable real labeled examples by up to 10%; it is not a runtime input.

## Why this is bounded, not a full-month baseline

The unmodified full 500ms chronological collector was attempted on January Coinexx. It accumulated all overlapping counterfactual paths and full Python feature dictionaries in memory, and updated every path on every future tick. During the attempt, the process reached ~1.45GB resident memory with only ~10% of the ~61MB gzip input consumed. It was stopped deliberately to avoid 4GB container-memory exhaustion. No completed whole-month performance report resulted.

A separate `bounded_trace_v2.py` diagnostic harness preserves the exact frozen feature/label/model functions and the 500ms evaluation clock **inside its predefined sampling windows**, but caps candidate generation to 100 snapshots per 9min window and locally warms up for 5min. HTF one-minute context is updated from all raw quote records between windows. Because the sampling windows and memory-bounded cap reduce effective participation and locally restart state, the resulting 35 selected trades CANNOT be extrapolated to whole-month frequency, expectancy, or account drawdown.

## Execution-model restrictions

- Immediate bid/ask quote-fill approximation; no actual order acceptance, latency or broker execution requests.
- Fixed $0.02/trade round-trip fee from the frozen `ActivePath`; no verified historical broker commission or actual slippage.
- R9-style initial stop based on opposite quote, monotonic trailing after +$0.10 excursion, nominal 30sec OnTick-evaluated timeout; no historical broker stops/freeze constraints, margin, or partial fills.
- The frozen `ActivePath` skips all subsequent quote events sharing the same `utc_ms` as the entry. This is inherited from v2 and differs from source-sequence handling in the original R9 replay. Do not silently fix it mid-baseline.
- The experimental feature and Hawkes intensity parameters are engineered, not statistically fitted production Hawkes kernels. No production probability calibration/live Neyman-Pearson guarantee.
- The score dates are declared development days that have appeared in earlier R9 research. Not pristine blind OOS.

## Verdict and required next engineering step

The bounded default v2 mechanism fails to demonstrate positive entry economics or useful dual-source trade participation. **Do not promote the policy or begin optimizing v2 on this sample alone.** The current evidence isolates two blockers: adverse payoff asymmetry on Coinexx and execution cost/spread toxicity on Dukascopy. To obtain the *requested full research-day or full-month baseline*, the underlying hypothesis labeler needs an exactly equivalent but memory-bounded method (streamed paths and an optimized concurrent-outcome evaluator) validated on a common raw-tick fixture against the frozen `ActivePath` state machine. This is an **infrastructure performance improvement**, not permission to change signals or exit rules.

## Preservation

The archive contains the raw counterfactual outcome tables, exact policy exports for four folds, selected-trade ledger, scorecard JSON/CSV, all Python helpers, original frozen v2 source and tests, original design contract, logs, source SHA-256 checks, and validation receipt. Large raw monthly ticks are separately pinned in the existing `gold_mt5_tick_all` and Dukascopy Drive folders, not duplicated in the recovery ZIP. No tests on March/April/May/August/September were performed.

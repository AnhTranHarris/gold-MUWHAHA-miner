# DELTA R005 — Immutable Multivariate Vector Library and Stage-A Selection Protocol

**Status:** PREREGISTERED DESIGN / NO REPLAY EXECUTED  
**Active parent:** `DELTA_004_COINEXX_LIKE_DUKASCOPY_RESEARCH_SURFACE`  
**Scope:** ENTRY + INITIAL-HOLD  
**Library version:** `R005-v1`

## Purpose

Freeze a broad multivariate vector library before seeing candidate performance.

R005 deliberately optimizes **design quality**, not expected profit. It is intended to improve the probability of discovering a genuine useful region of the preregistered search space while reducing overfit risk.

## Immutable vector library

Families:
- DH-01 Nested Direction State
- DH-02 Breakout Retest Rebreak
- DH-03 Pullback Continuation
- DH-06 Quote-Pressure Initial-Hold
- DH-07 Specialist-Aware Initial Hold

Counts:
- DH-01: 12
- DH-02: 20
- DH-03: 20
- DH-06: 12
- DH-07: 12

Total: **76 immutable vectors**

Full library SHA-256:

`9dfcdcd83bae9452291b2b249d41ac4f19751e23f1ff91ae6e1d581707528b52`

## Design method

Each family contains four mechanism-driven theory anchors plus a scrambled Sobol space-filling set.

Power-of-two Sobol counts:
- DH-01: 8
- DH-02: 16
- DH-03: 16
- DH-06: 8
- DH-07: 8

Seeds were selected from the fixed candidate pool 1..256 using geometry only:
- 55% centered-discrepancy percentile rank, lower is better
- 45% minimum normalized pairwise-distance percentile rank including theory anchors, higher is better

Chosen seeds:
- DH-01: 11
- DH-02: 84
- DH-03: 8
- DH-06: 72
- DH-07: 42

No XAUUSD performance result was used in seed choice.

## Mixed-factor mapping

- continuous factors: linear map across frozen R004 bounds
- categorical factors: rank-balanced assignment across declared levels
- integer factors: rank-balanced assignment across allowed integer levels

## Coverage order

Vectors are ordered with farthest-first traversal in normalized parameter space, starting from the balanced theory anchor.

This produces crash-safe partial coverage: early completed vectors should span broad parameter space rather than cluster.

## Core and extension

DH-02 / DH-03:
- first 12 coverage vectors = CORE
- remaining 8 = preregistered EXTENSION

DH-01 / DH-06 / DH-07:
- first 8 = CORE
- remaining 4 = preregistered EXTENSION

Extensions are already frozen and hashed. They cannot be invented after results.

## Stage-A queue

Exact window:

`[2026-01-01T00:00:00Z, 2026-01-18T12:00:00Z)`

Default surface:

`DELTA_004_P75`

Queue composition:
- 1 R9 control
- 1 primitive causal-feature harvest
- 76 immutable vector jobs

Total: **78 jobs**

Run-sheet SHA-256:

`3e2728bb1a0db7e2423892d4756591e246ddb646c9f2a2a0a82618e983e5275a`

All jobs are queued only. No replay has been executed.

## Wave structure

### Wave 0
- exact R9 control
- primitive causal feature harvest
- DH-01 context labeling
- DH-06 observer evaluation
- DH-07 observer state evaluation

Observer jobs do not change R9 trades.

### Wave 1
- DH-02 raw-tick entry-specialist replay
- DH-03 raw-tick entry-specialist replay
- DH01-A02 fixed as base context implementation
- R9 downstream lifecycle frozen for entry attribution

Extension vectors remain conditional.

## Selection protocol

R005 forbids “highest net profit wins.”

Selection should first preserve:
- winners
- net profit
- gross-loss reduction
- max-drawdown reduction
- activity / opportunity retention

Leading configurations are evaluated on a multi-objective Pareto surface.

A result is also checked against its three nearest preregistered vectors within its family. A large isolated spike without nearby support is flagged as fragile.

Temporal stability is later checked by day, session, and month.

The full tested universe must remain in the ledger.

## Multiple-testing controls

Preregistered for later use when data support them:
- White Reality Check / Hansen-style SPA logic
- Probability of Backtest Overfitting / CSCV
- Deflated Sharpe Ratio only if Sharpe is later reported as a secondary statistic

These do not replace DELTA primary governance metrics.

Adaptive Bayesian optimization is **not authorized inside R005**. A future adaptive search requires a new documented research unit with frozen acquisition function, bounds, stopping rule, and holdout policy.

## Drive artifacts

R005 Google Doc:

https://docs.google.com/document/d/14uay-Q_xvHakpIoMZKiqds67B3HetoVDlfNa5dM5umU/edit

Working workbook:

https://docs.google.com/spreadsheets/d/1C2EOJ2WDZgVMcGG8s1WPY46-Q4U8QQXUhZytqPJVsY0/edit

Canonical tabs:
- `15 Immutable Vectors`
- `16 Stage-A Run Sheet`
- `17 Design QA`

Stage folder:

https://drive.google.com/drive/folders/1iCg7Ptl8zRQ-5QUFGSuB7sPTqsNKzxiX

## Reference methods

NIST fractional-factorial guidance:
https://www.itl.nist.gov/div898/handbook/pri/section3/pri3345.htm

NIST D-optimal design guidance:
https://www.itl.nist.gov/div898/handbook/pri/section5/pri521.htm

SciPy Sobol:
https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.qmc.Sobol.html

SciPy Latin hypercube:
https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.qmc.LatinHypercube.html

Bailey et al., Probability of Backtest Overfitting:
https://papers.ssrn.com/sol3/Papers.cfm?abstract_id=2326253

Bailey & López de Prado, Deflated Sharpe Ratio:
https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551

## Current gate

- immutable vector library: FROZEN
- Stage-A run sheet: FROZEN
- replay: NOT STARTED
- active promoted candidate: NONE
- August: SEALED
- GOV-018: DORMANT
- MQL5: NOT AUTHORIZED

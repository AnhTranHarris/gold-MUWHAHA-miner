# GRID-001 R9 REAL January Proof-Admission Retention 001 — Preregistration

**Unit:** `DAA_GRID_001_R9_REAL_JAN_PROOF_ADMISSION_RETENTION_001`  
**Status:** FROZEN BEFORE COMPUTE  
**Role:** first direct admission-layer intervention on the actual R9 REAL signal stream

## Question

Can the already-promoted A15 proof-before-entry mechanism selectively preserve profitable R9 REAL January opportunities while refusing enough weak signals to remove roughly 20% or more of canonical gross loss?

This is a **retention diagnostic**, not yet a delayed-entry PnL backtest.

## Parent architecture

Preserve:
- actual R9 REAL January BUY/SELL signals;
- frozen nested 5m/15m state underneath the system;
- fixed 0.01 policy;
- A15 completed-M1 ATR adaptive gap;
- proof-before-entry as the admission primitive.

No state family is vetoed by label.

Every R9 signal faces the same frozen causal proof test.

## A15 admission gap

At the mapped R9 signal tick compute the existing A15 adaptive gap:

- completed-M1 ATR(14);
- gap = 1.50 × ATR;
- clamp $0.75–$5.00;
- quantize to $0.10.

The gap is frozen for that signal.

## Shadow admission state

At the original R9 signal:
- no new grid-owned physical trade is assumed;
- reference executable quote:
  - BUY -> modeled Ask;
  - SELL -> modeled Bid.

Frozen proof/failure distances:
- favorable proof = **+0.25 A15 gap**
- adverse failure = **-0.50 A15 gap**

Use executable liquidation-side quotes while observing:
- BUY path measured on Bid;
- SELL path measured on Ask.

First boundary wins.

## Decision horizon

The proof race ends at the earliest of:
1. original R9 trade exit time;
2. original signal time + 5 minutes;
3. end of January tick data.

This prevents the admission layer from resurrecting an opportunity after the original specialist lifecycle ended.

Outcomes:
- PROOF -> retain opportunity;
- FAIL -> abstain;
- NO_DECISION -> abstain.

No reversal or recovery flip is authorized here.

## Retention proxy accounting

For diagnostic selectivity only:

If PROOF:
- retain the **original R9 MT5 deal cashflows** unchanged.

If FAIL / NO_DECISION:
- treat the original trade as not admitted and remove its original entry/exit cashflows.

This is **not** claimed as actual delayed-entry economics because the real entry price would be later.

The purpose is to measure whether proof-before-entry separates original winners from losers strongly enough to justify a full delayed-entry simulation.

## Required metrics

Full January plus frozen discovery/validation split:

- R9 signals;
- PROOF / FAIL / NO_DECISION counts and shares;
- median / p75 proof latency;
- retained trade count/share;
- retained original net / GP / GL / PF;
- removed net / GP / GL;
- gross-loss removed percentage;
- gross-profit sacrificed percentage;
- net improvement proxy;
- original positive-trade retention rate;
- original negative-trade retention rate;
- trade velocity proxy after admission.

Also report by frozen owner relation:
- ALIGNED
- OPPOSED
- NEUTRAL
- CONFLICT

These subgroup reports are diagnostic only; no subgroup-specific threshold is allowed.

## Preferred breakthrough gate

The proof-admission primitive is high-leverage if:

1. gross loss removed >= **$2,087.38** (20% of canonical January gross loss);
2. net improvement proxy >= **$1,330.32** (20% of canonical January net-loss magnitude), preferably much larger;
3. gross-profit sacrifice is materially smaller than gross-loss removal;
4. qualitative improvement survives both discovery and validation;
5. retained trade flow remains large enough to serve the system-wide specialist architecture.

If this gate passes, next unit must simulate the **actual delayed entry and executable economics**. The retention proxy alone cannot be promoted as trading performance.

## Anti-overfit rules

- A15 only; no A05/A10 comparison in this unit.
- no proof/failure distance sweep;
- no state-specific proof thresholds;
- no session/news/macroeconomic routing;
- no ML;
- no reroute/reversal;
- no MQL5.

August sealed. Main `delta` read-only. Fixed 0.01. No Martingale.

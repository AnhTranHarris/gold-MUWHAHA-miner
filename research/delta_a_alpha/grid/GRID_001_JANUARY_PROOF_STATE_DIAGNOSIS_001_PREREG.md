# GRID-001 January Proof-State Diagnosis 001 — Preregistration

**Unit:** `DAA_GRID_001_JANUARY_PROOF_STATE_DIAGNOSIS_001`  
**Status:** FROZEN BEFORE COMPUTE

## Question

Why does A15 proof-before-entry lose in the chronological discovery segment but become strongly positive in the final-third validation segment?

This unit is diagnostic. It does not authorize a new strategy or threshold optimizer.

## Parent contract

Use the exact A15 Proof-Before-Entry 001 contract:
- adaptive A15 lattice;
- completed-M1 ATR(14) spacing;
- gap clamp $0.75–$5.00;
- $0.10 quantization;
- +0.25 gap proof before physical entry;
- -0.50 gap failure before proof = no trade;
- post-proof ±1.00 event-gap TP/SL;
- original five-minute event horizon;
- fixed 0.01;
- $0.02 round-trip commission;
- no averaging or Martingale.

Only opened proof-before-entry trades are analyzed.

## Causal state variables

All values must be known at or before the physical proof-entry tick.

### V1 — volatility expansion ratio

`vol_ratio = completed_M1_ATR14 / completed_M1_ATR240`

Frozen coarse bins:
- < 0.75
- 0.75–1.00
- 1.00–1.25
- 1.25–1.50
- 1.50–2.00
- >= 2.00

No threshold fitting.

### V2 — gap-cap state

- A15 event gap < $5.00
- A15 event gap == $5.00 clamp

Purpose: determine whether the regime shift is simply caused by the A15 geometry reaching its cap.

### V3 — 5-minute directional efficiency at proof entry

Using modeled midpoint ticks up to the proof-entry timestamp:

`eff_5m = abs(net displacement) / path length`

Frozen coarse bins:
- < 0.10
- 0.10–0.25
- 0.25–0.50
- 0.50–0.75
- >= 0.75

Also record continuation-aligned signed displacement over the same 5-minute window in units of event gap.

### V4 — event pace

Elapsed time since the previous A15 virtual event:
- < 1 second
- 1–5 seconds
- 5–30 seconds
- 30–120 seconds
- >= 120 seconds

No minimum-sample filtering during computation; sample size must be displayed.

## Required outputs

For each state/bin and separately for discovery/validation:
- opened trades;
- net;
- gross profit/loss;
- PF;
- expectancy;
- win rate.

Also report:
- state population shift from discovery to validation;
- whether any mechanism shows the same qualitative economic sign in both chronological segments;
- whether validation success can be explained by one simple state or only by broad nonstationarity.

## Anti-overfit rule

No model training.
No threshold search.
No bin merging after seeing results.
No session/news categories.

A mechanism may inform the next unit only if:
- it has nontrivial sample size;
- its qualitative direction is not reversed between discovery and validation;
- it corresponds to a reconstructible causal state.

## Scratch-data rule

Any pre-existing local scratch experiment may suggest hypotheses but cannot count as evidence for this unit.

August sealed. Main `delta` read-only. MQL5 unauthorized.

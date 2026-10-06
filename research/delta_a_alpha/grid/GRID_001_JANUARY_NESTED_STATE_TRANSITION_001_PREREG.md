# GRID-001 January Nested State Transition 001 — Preregistration

**Unit:** `DAA_GRID_001_JANUARY_NESTED_STATE_TRANSITION_001`  
**Status:** FROZEN BEFORE COMPUTE  
**Category:** multi-timeframe trend-within-trend ownership

## Parent floor

Reuse exactly:
- A05 / A10 / A15 adaptive lattices;
- proof-before-entry;
- one 0.01 position per event;
- ±1 event-gap TP/SL;
- original five-minute horizon;
- signed-efficiency states from Nested Trend State 001.

No thresholds are changed.

## Two causal snapshots

For every proof-before-entry physical trade compute the same 5s / 15s / 1m / 5m / 15m Signed Efficiency Ratio states at:

1. the **original lattice event timestamp**;
2. the **proof-entry timestamp**.

Only completed bars may be used at each timestamp.

## State definitions

Unchanged:
- aligned with event: event_direction × SER >= +0.50
- opposed: event_direction × SER <= -0.50
- non-directional: abs(SER) < 0.50

Parent = 5m + 15m.
Child = 5s + 15s.
Middle = 1m.

Parent supportive means:
- at least one parent timeframe aligned;
- neither parent timeframe opposed.

Parent neutral means:
- neither parent aligned nor opposed.

## Frozen transition families

### S1 — STABLE_ALIGN

- parent supportive at event and proof;
- both child timeframes aligned at event and proof;
- middle not opposed at event or proof.

### S2 — CHILD_RECLAIM_IN_PARENT_TREND

- parent supportive at event and proof;
- child is **not both aligned** at event;
- both child timeframes aligned at proof;
- middle not opposed at proof.

Interpretation: local child pullback/noise resolves back into the existing parent trend.

### S3 — MIDDLE_RECLAIM_IN_PARENT_TREND

- parent supportive at event and proof;
- middle opposed at event;
- middle not opposed at proof;
- both child timeframes aligned at proof.

Interpretation: a 1-minute pullback inside a broader trend has stopped opposing before physical entry.

### S4 — DEEP_RECLAIM

- parent supportive at event and proof;
- middle opposed at event;
- child not both aligned at event;
- middle not opposed at proof;
- both child timeframes aligned at proof.

This is the strictest explicit trend-within-trend reclaim pattern.

### S5 — PARENT_RANGE_CHILD_RECLAIM

- parent neutral at event and proof;
- child not both aligned at event;
- both child timeframes aligned at proof;
- middle not opposed at proof.

Interpretation: local trend emerges inside parent equilibrium.

### S6 — PARENT_OPPOSED_AT_PROOF

- no parent timeframe aligned at proof;
- at least one parent timeframe opposed at proof.

### TRANSITION_ACCEPT

Predeclared union:

`S2 ∪ S3 ∪ S4 ∪ S5`

### RECLAIM_PARENT_ONLY

Predeclared union:

`S2 ∪ S3 ∪ S4`

No post-result recombination is allowed.

## Required outputs

For A05 / A10 / A15 and each family:
- trades;
- retention;
- net;
- gross profit/loss;
- PF;
- expectancy;
- win rate;
- trades/day;
- discovery and validation.

Compare with:
- ungated proof-before-entry;
- static Nested Trend State 001.

## Breakthrough discipline

A gross-loss reduction is not credited as a 50% breakthrough unless:
- trade retention remains meaningful;
- net/PF also improve;
- discovery/validation do not collapse.

R9 REAL January guiding targets remain:
- +$3,325.81 net-loss recovery;
- $5,218.45 gross-loss reduction;
- $3,329.58 drawdown reduction.

This unit seeks a reusable ownership mechanism, not necessarily the whole 50% bridge alone.

No session/news categories. No ML. No threshold tuning.

August sealed. Main `delta` read-only. MQL5 unauthorized.

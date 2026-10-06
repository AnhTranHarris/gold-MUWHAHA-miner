# GRID-001 January Nested Trend Phase 001 — Preregistration

**Unit:** `DAA_GRID_001_JANUARY_NESTED_TREND_PHASE_001`  
**Status:** FROZEN BEFORE COMPUTE  
**Category:** multi-timeframe trend-within-trend / market-state phase

## Purpose

Add **trend age/phase** to the already-tested independent timeframe states.

No entry-distance, proof-distance, TP, SL, or volatility threshold is changed.

## Base state

Reuse Signed Efficiency Ratio on completed bars:

- strong UP: SER >= +0.50
- strong DOWN: SER <= -0.50
- otherwise non-strong

Timeframes examined:
- 5m
- 15m

The 5s / 15s / 1m child/middle states remain available as context but are not re-thresholded.

## Trend age

For each completed 5m and 15m bar, calculate the consecutive number of completed bars that have remained in the same **strong directional state**.

Age resets to zero when:
- state becomes non-strong;
- direction changes.

Frozen phase bins:

- **EARLY:** age 1–2 bars
- **MATURE:** age 3–6 bars
- **EXTENDED:** age >= 7 bars

These bins are fixed before compute.

## Parent owner

At proof-entry time:

1. if 15m is strong and 5m is either same-direction or non-strong, 15m owns;
2. else if 5m is strong and 15m is non-strong, 5m owns;
3. if 5m and 15m are both strong in the same direction, 15m owns;
4. if 5m and 15m are strongly opposed to each other, classify **PARENT_CONFLICT**;
5. if neither is strong, classify **PARENT_NEUTRAL**.

For an owned parent trend, classify ownership relative to the child event:

- PARENT_ALIGNED
- PARENT_OPPOSED

## Two parent-floor mechanisms evaluated

### F1 — Proof-Before-Entry continuation

Use the existing A05/A10/A15 continuation PnL unchanged.

Report economics by:
- parent relation;
- owner timeframe;
- phase age.

### F2 — Parent-Opposed Reclaim Route

For parent-opposed events, reuse the already-frozen parent-reclaim route unchanged.

Report parent-reclaim economics by:
- owner timeframe;
- phase age.

No phase-based trade selection occurs inside the simulation. This unit is diagnostic first.

## Required outputs

For A05 / A10 / A15:

For each parent relation × owner timeframe × phase:
- trades;
- net;
- gross profit/loss;
- PF;
- expectancy;
- win rate;
- discovery and validation.

Also report population shifts.

## Advancement rule

A phase mechanism may advance only if:
- the same phase has qualitatively compatible economics in discovery and validation;
- sample size is nontrivial;
- it materially distinguishes good/bad ownership better than direction alone.

No age-bin optimization or merging after results.

If a robust phase is found, the next sandwich unit may use it as a routing/admission state.

If not, age remains descriptive only.

## R9 January discipline

The target is still a **system-level** >=50%-ish improvement in at least one R9 REAL January weakness metric, not a tiny leaf.

Guiding targets:
- +$3,325.81 net-loss recovery;
- $5,218.45 gross-loss reduction;
- $3,329.58 drawdown reduction.

No session/news categories. No ML.

August sealed. Main `delta` read-only. MQL5 unauthorized.

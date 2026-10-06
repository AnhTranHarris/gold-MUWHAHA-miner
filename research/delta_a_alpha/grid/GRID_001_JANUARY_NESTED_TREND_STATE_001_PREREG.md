# GRID-001 January Nested Trend State 001 — Preregistration

**Unit:** `DAA_GRID_001_JANUARY_NESTED_TREND_STATE_001`  
**Status:** FROZEN BEFORE COMPUTE  
**Category:** multi-timeframe trend-within-trend ownership

## Scientific question

Can independently classified trend states across multiple completed timeframes identify which proof-before-entry continuation events deserve ownership, especially distinguishing:

- aligned continuation;
- pullback-within-parent-trend continuation;
- child trend inside parent range;
- parent-opposed continuation;
- unresolved/mixed state?

## Parent floor

Do not regress architecture.

Reuse:
- A05 / A10 / A15 adaptive virtual lattices;
- proof-before-entry (+0.25 gap proof, -0.50 gap pre-proof failure);
- one physical 0.01 position maximum per event;
- ±1 event-gap post-proof TP/SL;
- original five-minute event horizon;
- no Martingale;
- no averaging.

The existing volatility-expansion route remains frozen and is not retuned in this unit.

## Timeframes

Build causal midpoint-close bars for:

- 5 seconds;
- 15 seconds;
- 1 minute;
- 5 minutes;
- 15 minutes.

At a proof-entry timestamp, use only **completed bars**.

## Local trend score

For each timeframe use the last 6 completed closes.

Signed Efficiency Ratio:

`SER = (close_last - close_6bars_ago) / sum(abs(close_i - close_(i-1)))`

Range: -1 to +1.

State:
- UP: SER >= +0.50
- DOWN: SER <= -0.50
- RANGE: abs(SER) <= 0.30
- MIXED: otherwise

These thresholds are frozen from public efficiency-ratio conventions; no threshold search is authorized.

## Event-aligned scores

For an event direction `d ∈ {-1,+1}`:

- child = mean(d*SER_5s, d*SER_15s)
- middle = d*SER_1m
- parent = mean(d*SER_5m, d*SER_15m)

Positive = trend state supports continuation direction.
Negative = trend state opposes continuation direction.

## Frozen ownership families

### T1 — FULL_ALIGN

- 5s and 15s states both match event direction;
- 1m matches event direction;
- neither 5m nor 15m is strongly opposite;
- at least one of 5m/15m matches event direction.

### T2 — PULLBACK_RECLAIM

Trend within trend:
- at least one parent 5m/15m state matches event direction;
- neither parent strongly opposes;
- 1m strongly opposes event direction;
- both 5s and 15s match event direction at proof.

Interpretation: local pullback inside broader trend has re-aligned at the child layer.

### T3 — PARENT_RANGE_CHILD_TREND

- 5m and 15m are RANGE/MIXED, not strongly directional;
- 5s and 15s both match event direction;
- 1m is not strongly opposite.

Interpretation: scalp-sized local trend inside parent equilibrium.

### T4 — PARENT_OPPOSED

- either 5m or 15m strongly opposes the event direction;
- no parent timeframe strongly supports it.

### T5 — OTHER

Everything else.

No family is assumed profitable before compute.

## Required outputs

For A05/A10/A15 and each T-family:

- events/opened trades;
- trade velocity;
- full net / gross profit / gross loss / PF / expectancy / win rate;
- discovery vs validation;
- contribution to total gross loss;
- contribution to total net;
- comparison with ungated proof-before-entry.

Also report a stacked candidate:

`NESTED_ACCEPT = T1 ∪ T2 ∪ T3`

and a strict candidate:

`TREND_OWNED = T1 ∪ T2`

No post-result family recombination is allowed in this unit.

## R9 REAL January bridge targets

These are **guiding-light system targets**, not claims that a standalone route directly rewrites R9 REAL history:

- 50% net-loss recovery: +$3,325.81 incremental value;
- 50% gross-loss reduction benchmark: $5,218.45;
- 50% drawdown reduction benchmark: $3,329.58.

A route that merely deletes most events is not considered a 50% breakthrough.

## Advancement

A nested-state mechanism advances if it:
- materially improves proof-before-entry economics;
- shows compatible discovery/validation behavior;
- retains useful velocity;
- reveals a reusable state/routing layer for future specialists.

A true January breakthrough should ideally recover >=50% of at least one R9 REAL weakness benchmark when stacked into the broader grid system. This unit may first identify the structural route that can support that later stack.

No session/news categories. No threshold tuning. No ML.

August sealed. Main `delta` read-only. MQL5 unauthorized.

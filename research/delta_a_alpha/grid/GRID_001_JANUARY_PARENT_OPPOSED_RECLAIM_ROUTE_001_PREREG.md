# GRID-001 January Parent-Opposed Reclaim Route 001 — Preregistration

**Unit:** `DAA_GRID_001_JANUARY_PARENT_OPPOSED_RECLAIM_ROUTE_001`  
**Status:** FROZEN BEFORE COMPUTE  
**Category:** nested multi-timeframe trend-within-trend ownership

## Parent floor

Reuse:
- A05 / A10 / A15 adaptive lattice events;
- proof-before-entry continuation event detection;
- nested 5m / 15m parent states from Signed Efficiency Ratio;
- fixed 0.01;
- original five-minute event horizon;
- no averaging;
- no Martingale.

The volatility-expansion route remains frozen and untouched.

## Eligible family

At the normal continuation proof timestamp:

`PARENT_OPPOSED`

means:
- neither 5m nor 15m parent state strongly supports the child continuation direction;
- at least one of 5m / 15m strongly opposes the child continuation direction.

This is the same large losing family already measured in Nested State 001 / Transition 001.

## Rerouting hypothesis

The child continuation proof may represent a countertrend pullback inside the parent trend.

Therefore do **not** enter the child continuation.

Instead:

1. mark the continuation proof price as the pullback extreme reference;
2. wait for price to move **0.25 event gap back in the parent direction**;
3. if that parent-direction reclaim occurs inside the remaining original event horizon, enter exactly one parent-direction trade;
4. otherwise abstain.

The parent direction is the opposite of the child continuation direction for this eligible family.

## Physical parent trade

At reclaim proof:
- fixed 0.01;
- entry at executable Ask for parent-long / Bid for parent-short;
- TP = +1.00 event gap;
- SL = -1.00 event gap;
- no horizon reset;
- no second flip;
- one event owner only.

## Comparisons

For A05 / A10 / A15 report:

### CHILD_CONT_BASELINE
Original proof-before-entry continuation PnL for eligible parent-opposed events.

### ABSTAIN
Zero PnL for the eligible family.

### PARENT_RECLAIM_ROUTE
Parent-direction trade after 0.25-gap reclaim.

Required:
- eligible events;
- reclaim-proven count/share;
- trades/day;
- net / gross profit / gross loss / PF / expectancy / win rate;
- discovery and validation;
- target / stop / timeout;
- net value recovered versus CHILD_CONT_BASELINE;
- gross-loss change versus CHILD_CONT_BASELINE.

## Breakthrough discipline

This route is structurally interesting if:
- parent-reclaim economics materially outperform child continuation;
- discovery and validation have compatible signs;
- trade count remains large enough to matter;
- recovered value is not merely the result of abstaining from almost everything.

For the broader sandwich system, the January guiding targets remain:
- +$3,325.81 net-loss recovery;
- $5,218.45 gross-loss reduction;
- $3,329.58 drawdown reduction.

This route may contribute part of that bridge rather than solve it alone.

No reclaim-distance tuning is authorized.

August sealed. Main `delta` read-only. MQL5 unauthorized.

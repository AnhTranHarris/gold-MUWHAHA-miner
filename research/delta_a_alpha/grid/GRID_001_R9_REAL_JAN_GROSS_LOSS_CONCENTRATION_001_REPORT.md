# GRID-001 R9 REAL January Gross-Loss Concentration 001

**Status:** COMPLETE / NO CLEAN 20% STATIC FAMILY

## Question

Can frozen Delta-A-alpha grid/nested states isolate a large R9 REAL January loss family that is obviously safe to veto?

## Result

Several states exceed the requested 20% scale, but mostly because they contain a very large share of all trades.

Examples:

- volatility ratio <1.00:
  - 17,306 trades / 54.23% of trades
  - 53.11% of gross loss
  - 49.67% of gross profit
  - net -$3,663.34

- mixed A05/A10/A15 lattice consensus:
  - 17,021 trades / 53.33%
  - 52.59% of gross loss
  - 50.22% of gross profit
  - net -$3,587.66

- nested owner neutral:
  - 13,327 trades / 41.76%
  - 41.59% of gross loss
  - 39.47% of gross profit
  - net -$2,846.75

- latest A15 event opposed to R9 direction:
  - 13,912 trades / 43.59%
  - 43.60% of gross loss
  - 42.58% of gross profit
  - net -$2,938.29

- latest A15 opposed event older than 120 seconds:
  - 8,599 trades / 26.94%
  - 26.84% of gross loss
  - 24.93% of gross profit
  - net -$1,858.18

All listed families remain net-negative in both chronological January partitions.

## Interpretation

The 20% scale exists, but static vetoing is not intelligent enough.

The broad states carry almost proportional amounts of both gross loss and gross profit. A perfect veto would improve the backtest largely by deleting huge portions of the system.

That is not the sandwich architecture we want.

The useful conclusion is different:

> R9 REAL January appears broadly overactive and insufficiently selective, rather than being ruined by one narrow static regime.

The next state variable should therefore describe the **behavior of the signal stream itself**, not add another price indicator.

## HFT/scalping mutation

Public HFT systems commonly treat event flow, intensity, imbalance, and event clocks as distinct from slower market state.

We do not have order-book depth in Dukascopy, so Delta-A-alpha will not invent it.

Instead, use the actual R9 BUY/SELL signal stream as **synthetic specialist flow**:

- same-direction run length;
- exponentially decayed signed signal pressure;
- alternating/chop rate;
- time since previous R9 signal;
- time since previous opposite signal;
- relation of signal pressure to 5m/15m nested state.

This is an original mutation inspired by HFT event-flow architecture.

## Decision

DO NOT:
- veto the broad static families yet;
- tune volatility thresholds;
- add session/news categories.

NEXT:
**R9 SIGNAL-FLOW STATE 001**.

Goal: identify whether rapid-fire signal pressure/alternation exposes a more selective wrong-direction family large enough to support a 20%+ intervention.

August sealed. Main `delta` read-only. MQL5 unauthorized.

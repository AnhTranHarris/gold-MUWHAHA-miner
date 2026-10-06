# GRID-001 January Nested Trend State 001

**Status:** COMPLETE / STATIC STATE PARTIAL NEGATIVE

## Question

Can independent trend states across 5s, 15s, 1m, 5m and 15m identify which proof-before-entry continuation events deserve ownership?

## Frozen state model

Each timeframe used a six-completed-bar Signed Efficiency Ratio:

`SER = net close displacement / sum(abs(close-to-close displacement))`

States:
- UP >= +0.50
- DOWN <= -0.50
- RANGE when abs(SER) <= 0.30
- MIXED otherwise

No threshold search was performed.

## Main result

Static multi-timeframe context improves selectivity, but **does not yet meet the 50%-ish breakthrough standard**.

Large apparent gross-loss reductions mostly come from retaining only a small fraction of trades. That is not counted as a system breakthrough.

### A15 — strongest useful families

Parent-range + child-trend:
- 760 trades
- **+$215.53**
- PF **1.1811**
- discovery **-$106.25 / PF 0.8164**
- validation **+$321.78 / PF 1.5263**

Nested accept = full alignment + pullback reclaim + parent-range child-trend:
- 1,097 trades / 16.72% retention
- **+$232.05 / PF 1.1254**
- discovery **-$174.29 / PF 0.7990**
- validation **+$406.34 / PF 1.4135**

Pullback-reclaim:
- only 15 trades
- **+$5.60 / PF 1.2472**
- discovery **+$4.71 / PF 1.6662**
- validation **+$0.89 / PF 1.0571**

The pullback pattern is directionally interesting but far too sparse.

Parent-opposed continuation remained poor:
- 1,957 trades
- **-$151.63 / PF 0.9663**

### A10

Parent-range + child-trend:
- 1,074 trades
- **+$71.99 / PF 1.0499**
- discovery negative
- validation strongly positive

Again the state family is useful but nonstationary.

## Interpretation

The new assumption is supported conceptually:

> each timeframe can carry its own trend, and cross-scale disagreement contains information.

But a static snapshot at proof entry is too crude.

The most promising clue is the tiny A15 pullback-reclaim family. It suggests the valuable event may not be "all timeframes aligned." It may be a **transition**:

1. parent trend already exists;
2. child/middle timeframe pulls against it;
3. child state turns back into the parent direction;
4. proof-before-entry confirms the reclaim.

That is a true trend-within-trend mechanism.

## R9 REAL January breakthrough check

Guiding-light 50%-ish targets:
- recover $3,325.81 of R9 REAL January net loss;
- reduce $5,218.45 of R9 REAL January gross loss;
- reduce drawdown by $3,329.58.

This screen does **not** satisfy those targets in a meaningful system-wide sense.

Do not claim an 85–95% gross-loss breakthrough from subsets retaining only 3–17% of the proof-before-entry trades.

## Decision

KEEP:
- independent per-timeframe state;
- parent-opposed context as a negative signal;
- parent-range + child-trend as a candidate context;
- pullback-within-trend concept.

DO NOT PROMOTE:
- static multi-timeframe gating;
- simple timeframe majority voting;
- strict full alignment.

NEXT:
**state-transition ownership** inside the same category.

Test whether a child timeframe changing from opposed/mixed at the event to aligned at proof, while parent direction remains supportive, is materially stronger than a static aligned snapshot.

The volatility-expansion route remains frozen and untouched.

August sealed. Main `delta` read-only. MQL5 unauthorized.

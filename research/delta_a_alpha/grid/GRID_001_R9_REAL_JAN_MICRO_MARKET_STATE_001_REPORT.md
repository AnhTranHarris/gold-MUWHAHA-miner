# GRID-001 R9 REAL January Micro-Market State 001

**Status:** COMPLETE / USEFUL CONTEXT / NO CLEAN 20% STATIC VETO

## Question

Can causal 250 ms / 1 s / 5 s quote-path state, legitimate Dukascopy top-of-book volume pressure, and quote-event intensity isolate a selective R9 REAL January loss family?

## Result

The micro-state exists, but the large negative families are still too broad for a static veto.

### Price path

`MIXED_FLAT`:
- 14,141 trades / 44.31% of R9 entries
- net **-$2,970.55**
- PF **0.3509**
- 43.85% of January gross loss
- 42.42% of January gross profit
- discovery **-$2,557.78**
- validation **-$412.77**

`FAST_OPPOSE_SLOW_SUPPORT`:
- 7,156 trades / 22.42%
- net **-$1,513.07**
- PF **0.3646**
- 22.81% of gross loss
- 22.93% of gross profit
- negative in both chronological segments

This is a legitimate trend-within-trend micro-state, but its loss share is approximately proportional to trade share.

### L1 top-of-book volume

`MIXED_OR_ZERO`:
- 22,456 trades / 70.36%
- net **-$4,748.53**
- PF **0.3480**
- 69.78% of gross loss
- 66.96% of gross profit

The combined `MIXED_FLAT × MIXED_OR_ZERO` state contains:
- 10,068 trades / 31.55%
- net **-$2,193.19**
- PF **0.3296**
- 31.34% of gross loss
- 28.48% of gross profit

It is negative in discovery and validation, but still too broad to justify amputating one-third of the trade stream.

### Quote intensity

`BURST`:
- 6,151 trades / 19.27%
- net **-$1,342.99**
- PF **0.3200**
- 18.92% of gross loss
- 16.70% of gross profit

Again, it is poor but not a selective 20% loss concentration.

## Timestamp caveat

The 250 ms component was retained because it was frozen in the preregistration. MT5 report timestamps are only second-resolution and the empirical mapping has a 90th-percentile nearest-tick error of roughly 359 ms.

Therefore no independent 250 ms finding is promotable. The reusable state is the 1 s / 5 s structure.

## Interpretation

The HFT/scalping cross-reference was still useful:

- quote-event state should remain separate from slower 5m/15m context;
- L1 pressure is legitimate input;
- event-time intensity is a valid state dimension.

But another static veto is the wrong intervention.

The next sandwich layer should use the already-promoted **proof-before-entry** primitive on actual R9 signals:

`R9 signal -> shadow candidate -> causal proof/failure -> retain/defer/abstain`

This can preserve recoverable opportunities instead of deleting a broad state.

## Decision

KEEP:
- 1s/5s quote-path trend-within-trend state;
- L1 imbalance;
- quote intensity as contextual fields.

REJECT:
- static micro-state veto;
- threshold tuning;
- treating 250 ms as reliable independent state.

NEXT:
**R9 REAL proof-admission retention diagnostic** before any delayed-execution simulation.

August remains sealed. Main `delta` read-only. Fixed 0.01. No Martingale. MQL5 unauthorized.

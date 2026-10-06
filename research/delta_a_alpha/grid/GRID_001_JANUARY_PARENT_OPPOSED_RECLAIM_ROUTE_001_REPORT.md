# GRID-001 January Parent-Opposed Reclaim Route 001

**Status:** COMPLETE / INCREMENTAL IMPROVEMENT / NOT BREAKTHROUGH

## Question

When child continuation proof conflicts with the 5m/15m parent trend, can the event be rerouted into the parent direction after a causal reclaim instead of being traded in the wrong direction or discarded?

## Frozen route

Eligible family:
- neither 5m nor 15m strongly supports child continuation;
- at least one strongly opposes it.

Action:
- do not enter child continuation;
- wait for 0.25 event-gap movement back in parent direction;
- enter one fixed 0.01 parent-direction trade;
- ±1 event-gap TP/SL;
- preserve original five-minute event horizon;
- no second flip.

## Results

### A15

Child-continuation baseline for parent-opposed family:
- 1,957 trades
- **-$151.63**
- PF **0.9663**
- gross loss **-$4,498.92**

Parent-reclaim route:
- 1,721 trades
- **+$110.14**
- PF **1.0287**
- gross loss **-$3,842.63**
- net value recovered versus child continuation: **+$261.77**
- gross-loss magnitude reduction: **14.59%**

Chronology:
- discovery: **-$108.27 / PF 0.8405**
- validation: **+$218.41 / PF 1.0690**

This proves the rerouting idea can reverse the sign of the family overall, but does not solve early January.

### A10

- child baseline: **-$315.41 / PF 0.9385**
- parent route: **-$260.02 / PF 0.9429**
- net recovered: **+$55.39**
- gross-loss reduction: **11.20%**

### A05

- child baseline: **-$844.40 / PF 0.8739**
- parent route: **-$581.05 / PF 0.9043**
- net recovered: **+$263.35**
- gross-loss reduction: **9.35%**

## Interpretation

Multi-timeframe state is adding value when used as **routing**, not merely as a veto.

The A15 result is particularly important:
- the original child direction loses;
- the parent-direction reclaim route becomes positive overall.

However, the discovery/validation asymmetry remains.

That implies direction alone is still incomplete.

A trend has a **phase/age**:
- newly established;
- mature;
- exhausting;
- transitioning.

A 15-minute downtrend that just emerged and a 15-minute downtrend that has persisted through many bars should not automatically own the same child event.

Public regime-transition implementations also track regime-block duration rather than only the current label. Delta-A-alpha will use that idea clean-room as a causal state variable, not copy source code.

## Decision

KEEP:
- parent-opposed family as a reusable wrong-direction detector;
- parent-direction reclaim rerouting;
- A15 as the strongest implementation so far.

DO NOT PROMOTE:
- the route as a final candidate;
- reclaim-distance tuning.

NEXT:
**multi-timeframe trend phase / age.**

The next unit will test whether parent and child state age explains the early-January weakness and whether route ownership should depend on trend phase.

August sealed. Main `delta` read-only. MQL5 unauthorized.

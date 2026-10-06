# GRID-001 January Elastic Spacing 001

**Status:** COMPLETE / STRUCTURAL GEOMETRY BREAKTHROUGH  
**Dataset:** full January 2026 canonical Dukascopy XAUUSD ordered ticks  
**Surface:** `DUKAS_COINEXX_LIKE_P75`

## Question

Can causal volatility-normalized spacing stop the fixed-$1 grid from exploding in high-volatility January while preserving enough event supply for the R9 Delta-A-alpha system?

## Contract

Completed-M1 ATR(14) controls new-event spacing:

`gap = max($1, alpha * ATR14_M1)`

Then:
- clamp $1–$8;
- quantize to $0.25;
- 10% hysteresis;
- update no more than once per completed M1 bar.

Existing virtual anchors retain the gap that created them.

The event clock remains virtual. No physical averaging positions exist.

Shadow direction diagnostics remain fixed at $1 TP / $1 adverse bound so spacing changes are evaluated as event-selection geometry rather than as changing the payoff contract.

## Fixed-$1 reference

The previous event clock produced:
- **130,133 events**
- **~5,915 events/active day**

This was far above the R9 SYNTH velocity target and became extremely unstable late in January.

## Results

| Alpha | Events | Events/day | Daily CV | Median gap | Validation CONT PF | Validation Oracle PF |
|---|---:|---:|---:|---:|---:|---:|
| 0.25 | 64,196 | 2,918 | 0.686 | $1.00 | 0.774 | 5.95 |
| **0.50** | **33,922** | **1,542** | **0.444** | **$1.25** | **0.779** | **5.97** |
| 1.00 | 12,981 | 590 | 0.551 | $2.50 | 0.835 | 6.51 |

R9 SYNTH Jan–Jul guiding-light velocity is ~1,472 trades/active day.

## Interpretation

The important result is not that alpha 0.50 is an optimized number.

The important result is that **elastic spacing changes the event clock from a volatility-amplifying firehose into a much more stable opportunity stream**.

Alpha 0.50 is the best research-clock knee in this deliberately tiny matrix because:
- ~1,542 events/day is near R9 SYNTH system velocity;
- its daily event-count coefficient of variation is the lowest of the three screened variants;
- the directional-oracle ceiling remains very strong;
- validation behavior remains qualitatively similar to discovery.

This is a geometry breakthrough, not an alpha breakthrough.

Always mean reversion and always continuation remain negative.

## New mutation enabled by this result

The failed physical grid's unresolved stack can now be repurposed as a **virtual pressure sensor**.

Instead of actually accumulating hundreds of positions:
- the lattice tracks how many unresolved same-direction virtual anchors would exist;
- deep virtual BUY pressure means repeated mean-reversion attempts would still be unresolved during a downward move;
- deep virtual SELL pressure means the corresponding upward condition.

This may encode trend persistence / failed reversion without risking inventory.

That is the next January test.

## Decision

KEEP:
- completed-M1 elastic spacing;
- alpha 0.50 as the current research-clock geometry;
- virtual stack state as information only.

DO NOT PROMOTE:
- any physical grid;
- any directional strategy yet.

NEXT:
**virtual pressure / stack-depth semantics + information-based re-arm on the elastic clock.**

August sealed. Main `delta` read-only. MQL5 unauthorized.

# GRID-001 January Adaptive Spacing Screen 001

**Status:** COMPLETE / STRUCTURAL BREAKTHROUGH

## Question

Does a causal volatility-normalized lattice improve the quality of grid events compared with the creator's fixed $1 geometry?

## Method

The virtual source-inspired event clock was retained, but new events used the **last completed M1 ATR(14)**:

- A05: 0.50 × ATR
- A10: 1.00 × ATR
- A15: 1.50 × ATR

All gaps were:
- clamped to $0.75–$5.00;
- quantized to $0.10;
- updated only from completed M1 information;
- frozen per existing event after creation.

Each event was again shadowed as mean reversion and continuation with TP/SL equal to its own event gap.

## Fixed-$1 reference

- events: **130,133**
- ~**5,915/day**
- continuation PF: **0.762**
- direction-oracle PF: **6.05**
- oracle expected payoff: **+$0.883/event**
- both directions negative: **16.18%**

## A05 — fast child-scale candidate

- events: **39,397**
- ~**1,791/day**
- median event gap: **$1.20**
- continuation PF: **0.845**
- oracle PF: **9.50**
- oracle expected payoff: **+$1.591/event**
- both directions negative: **14.47%**
- validation continuation PF: **0.977**

A05 retains **more event velocity than the Jan–Jul R9 SYNTH average** while materially improving event quality over fixed $1.

## A10 — slower structural-scale candidate

- events: **16,141**
- ~**734/day**
- median event gap: **$3.10**
- continuation PF: **0.938**
- oracle PF: **20.65**
- oracle expected payoff: **+$3.038/event**
- both directions negative: **7.87%**
- validation continuation: **+$596.98 / PF 1.033**
- validation oracle PF: **28.90**

## A15 — strongest event-quality candidate

- events: **11,133**
- ~**506/day**
- median event gap: **$5.00** due the preregistered clamp
- continuation PF: **0.978**
- oracle PF: **28.88**
- oracle expected payoff: **+$3.871/event**
- both directions negative: **5.61%**
- validation continuation: **+$594.65 / PF 1.034**
- validation oracle PF: **28.67**

## Interpretation

This is the first large architectural improvement.

The fixed $1 grid was dramatically over-sampling January XAUUSD movement. Normalizing event spacing to recent causal volatility:

1. removed a large amount of noisy event duplication;
2. reduced the percentage of events where **neither** direction could earn its own gap;
3. increased the economic value of correctly classified events;
4. made continuation nearly break-even overall at the larger scales and slightly positive in the held-out final third;
5. produced a natural multi-layer lattice.

The important result is **not** that A15 should become the trading strategy.

A15's discovery segment is still negative under automatic continuation. Direction classification remains necessary.

The breakthrough is that the lattice now has useful scale separation:

- **A05** can act as the fast child/opportunity clock: ~1,791 events/day.
- **A10/A15** can act as slower structural/parent lattices with much cleaner event geometry.

That directly matches the Delta-A-alpha parent/child lattice hypothesis.

## Decision

PROMOTE:
- causal ATR-normalized spacing;
- per-event frozen gap geometry;
- multi-scale child/parent lattice concept.

DO NOT PROMOTE:
- always-continuation;
- any standalone adaptive grid strategy yet.

NEXT:
test whether the slower A10/A15 lattice can provide directional/state authority for A05 child events, followed by event-age/re-arm and thesis-failure logic.

No Jan–Jul candidate promotion yet.

# GRID-001 January Causal Observation Gate 001

**Status:** COMPLETE / NEGATIVE

The event crossing was treated as an observation trigger rather than an immediate order.

Matrix:
- waits: 250 ms, 1 s, 3 s;
- confirmation: 0, 0.10, 0.25 grid gaps;
- fixed 0.01 economics;
- 1-gap TP / 1-gap adverse bound;
- 5-minute horizon;
- same January virtual event clock and P75 execution surface.

## Result

All 9 variants remained negative.

Best validation variant:
- wait: **250 ms**
- confirmation: **0.25 gap**
- acceptance: **44.07%**
- event throughput: **~2,607 accepted events/day**
- full net: **-$11,150.19**
- full PF: **0.749**
- validation net: **-$9,410.09**
- validation PF: **0.757**

Immediate continuation from Event-Label Lab 001 had validation PF **0.787**, so the observation gate did not improve the core directional problem.

## Interpretation

The grid event is rich in opportunity, but **simple signed displacement during the first 0.25–3 seconds after the crossing is still not enough information to classify direction profitably**.

This rules out another tempting micro-tuning loop.

Do not optimize these waits.

The next structural mutation should change the lattice geometry itself. January M1 true range is materially larger than the source's fixed $1 grid for much of the month, so the fixed lattice likely over-samples noise and produces too many low-information events.

## Decision

REJECT:
- fixed short post-crossing displacement as the direction classifier;
- further tuning of the 250ms–3s confirmation family.

ADVANCE:
- **causal adaptive/elastic grid spacing** with bounded updates and hysteresis/cooldown;
- re-run the same dual-shadow opportunity diagnostic on normalized events.

No physical single-owner promotion yet.

# GRID-001 January Recovery Admission 001

**Status:** COMPLETE / NOT PROMOTED

## Question

Can causal information available at EARLY_THESIS_FAILURE identify which failed continuation events deserve one opposite-direction recovery flip?

## Frozen microscope

Allowed information:
- time to failure;
- failure speed and overshoot;
- adaptive event gap;
- crossing direction;
- recovery-aligned displacement over 1s/5s/15s/30s/60s;
- path length and directional efficiency over the same windows.

One shallow decision tree per lattice:
- max depth 3;
- minimum leaf 100;
- trained only on the first two-thirds;
- fixed probability gates 0.55 / 0.60 / 0.65.

The tree was a discovery microscope only.

## A10

Early-failure events: **7,118**.

The discovery-selected 0.55 gate chose only **117 events total / 1.64%** of eligible failures.

Selected recovery:
- full recovery-leg net: about **+$66.64**
- validation: **12 recovery trades, +$9.06, PF 1.50**

Combined system:
- RETIRE: **-$1,445.11 / PF 0.9375**
- selected recovery: **-$1,378.47 / PF 0.9404**

Discovery:
- RETIRE: **-$1,989.22 / PF 0.7566**
- selected: **-$1,931.64 / PF 0.7636**

Validation:
- RETIRE: **+$544.11 / PF 1.0364**
- selected: **+$553.17 / PF 1.0370**

The signal survives directionally, but **12 validation flips are far too few** to call robust.

The tree mainly used path-length/choppiness features:
- 1s path length;
- 15s path length;
- 30s path length;
- 5s efficiency.

This is retained only as a clue.

## A15

Early-failure events: **4,553**.

The 0.55 gate selected **627 / 13.77%**.

Discovery improved:
- RETIRE: **-$1,030.86 / PF 0.8066**
- selected: **-$915.01 / PF 0.8294**

But validation failed:
- RETIRE: **+$356.89 / PF 1.0245**
- selected: **+$71.19 / PF 1.0047**
- selected recovery legs in validation: **-$285.70 / PF 0.7887**

This is a clear non-promotion result.

## Interpretation

The recoverable subset exists, but this compact failure-path classifier does not robustly isolate it.

Do not:
- tune tree depth;
- tune probability gates;
- add dozens of features to rescue this classifier.

The strongest architectural lesson from Early Thesis Failure 001 is more fundamental:

> If a continuation event must prove favorable movement before earning its full risk budget, there may be no reason to pay the provisional loss at all.

That motivates the next structural mutation.

## Next mutation — proof before entry

Instead of:

`EVENT -> ENTER -> wait for proof -> cut if proof fails`

test:

`EVENT -> SHADOW UNCONFIRMED -> proof arrives -> ENTER`

If -0.50 gap failure occurs before +0.25 favorable proof:
- no physical trade occurs;
- event retires or moves to later recovery research.

This attacks gross loss before it exists.

## Decision

REJECT:
- current recovery-admission tree as a candidate;
- additional classifier tuning.

KEEP:
- recovery oracle as evidence that opportunity remains;
- path-length/choppiness clue for later architecture;
- one-shot recovery concept as a future routed action.

NEXT:
**proof-before-entry continuation on adaptive A05/A10/A15 lattices.**

A05 is included next because confirmation gating may reduce its ~1,791 events/day toward the R9 SYNTH system-velocity region while retaining the fast child-lattice role.

August remains sealed. Main `delta` read-only. MQL5 unauthorized.

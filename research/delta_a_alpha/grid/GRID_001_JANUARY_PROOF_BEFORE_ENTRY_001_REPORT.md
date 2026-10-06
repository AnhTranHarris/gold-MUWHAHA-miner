# GRID-001 January Proof-Before-Entry 001

**Status:** COMPLETE / STRUCTURAL BREAKTHROUGH / NOT YET PROMOTED

## Question

Can the adaptive lattice reduce gross loss structurally by keeping continuation events virtual until favorable path evidence arrives, instead of paying provisional loss while waiting for confirmation?

## Frozen contract

Lattices:
- A05
- A10
- A15

At each lattice crossing:

`SHADOW_UNCONFIRMED`

No physical trade exists yet.

Decision:
- favorable proof = +0.25 event gap;
- failure = -0.50 event gap.

If failure arrives first:
- retire event;
- physical PnL = $0.

If proof arrives first:
- enter one continuation trade at the executable proof tick;
- TP = +1.00 event gap from actual proof-entry price;
- SL = -1.00 event gap from actual proof-entry price;
- trade must finish inside the original five-minute event horizon;
- no horizon reset.

Economics:
- fixed 0.01;
- $0.02 round-trip commission only when a physical trade opens;
- no averaging;
- no Martingale;
- one physical trade maximum per event.

## A05

- lattice events: **39,397**
- physical trades opened: **18,522 / 47.01%**
- opened velocity: **~842/day**
- gross-loss reduction versus immediate continuation: **47.77%**

Immediate continuation:
- **-$6,619.30 / PF 0.8447**

Proof-before-entry:
- **-$3,019.49 / PF 0.8643**

Validation:
- **-$392.10 / PF 0.9704**

A05 cuts almost half the gross loss, but remains negative.

## A10

- lattice events: **16,141**
- physical trades: **9,022 / 55.89%**
- opened velocity: **~410/day**
- gross-loss reduction: **42.17%**

Immediate continuation:
- **-$1,753.09 / PF 0.9383**

Proof-before-entry:
- **-$701.39 / PF 0.9573**

Discovery:
- **-$1,249.29 / PF 0.7687**

Validation:
- **+$547.90 / PF 1.0497**

A10 materially reduces gross loss and improves validation, but the discovery segment remains weak.

## A15

- lattice events: **11,133**
- physical trades: **6,560 / 58.92%**
- opened velocity: **~298/day**
- gross-loss reduction: **41.33%**

Immediate continuation:
- **-$514.19 / PF 0.9784**

Proof-before-entry:
- **+$142.77 / PF 1.0102**
- expected payoff: **+$0.0218/trade**

Discovery:
- **-$697.43 / PF 0.8004**

Validation:
- **+$840.20 / PF 1.0801**

This is the first adaptive-lattice continuation architecture in Delta-A-alpha to become positive for full January under a frozen structural rule.

## Why this matters

Early Thesis Failure 001 showed that conditional risk can cut gross loss after a trade is already open.

Proof-Before-Entry improves that concept:

> unproven events consume no physical loss budget.

That is a major architectural improvement because more than 40% of A10/A15 events fail before confirmation and can now be discarded without taking the provisional loss.

The improvement is not a threshold-tuning artifact; the +0.25 / -0.50 rule was frozen before compute.

## Limitation

A15's aggregate positivity is **not robust enough for promotion** because:
- discovery remains materially negative;
- validation is strongly positive;
- January is nonstationary.

The next problem is not to tune proof/failure thresholds.

The next problem is to identify the structural state difference between the weak discovery period and strong validation period.

## Decision

PROMOTE AS ARCHITECTURAL PRIMITIVE:
- virtual unconfirmed event state;
- proof-before-entry;
- no physical risk before proof;
- original-horizon preservation.

DO NOT PROMOTE:
- A15 as a final candidate;
- proof/failure threshold optimization;
- standalone continuation strategy.

NEXT:
**state/regime diagnosis of A15 proof-before-entry discovery vs validation divergence.**

The first pass should stay narrow:
- causal volatility/drift/range structure;
- lattice-scale state;
- event pace;
- finite-age path state.

No session/news/macroeconomic categories yet.

August remains sealed. Main `delta` remains read-only. MQL5 remains unauthorized.

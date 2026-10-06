# GRID-001 January Dual Proof Ownership 001 — Preregistration

**Unit:** `DAA_GRID_001_JANUARY_DUAL_PROOF_OWNERSHIP_001`  
**Status:** FROZEN BEFORE COMPUTE

## Question

Can an adaptive grid event become direction-neutral by allowing continuation and mean-reversion to compete for causal proof before any physical position exists?

## Lattices

- A05
- A10
- A15

Use the already-promoted completed-M1 ATR(14) adaptive geometry and frozen per-event gaps.

## Event semantics

At the lattice crossing:

`SHADOW_DIRECTION_NEUTRAL`

No physical trade exists.

Two hypotheses are created:

1. **CONT** — crossing direction.
2. **MR** — opposite direction.

Each hypothesis has its own executable event-reference price:
- hypothetical LONG uses event Ask;
- hypothetical SHORT uses event Bid.

## Proof race

Frozen proof distance:

`0.25 * event_gap`

A hypothesis proves itself when its executable mark-to-market path first reaches +0.25 event gap relative to its event-reference price.

- continuation proof first -> CONT owns the event;
- mean-reversion proof first -> MR owns the event;
- neither before the original five-minute horizon -> ABSTAIN;
- if both are detected on the same tick -> ABSTAIN as ambiguous.

No failure threshold is used in this unit.

## Physical entry

After one hypothesis wins:
- enter exactly one 0.01 position in the winning direction at the executable quote on the proof tick;
- TP = +1.00 event gap from actual entry;
- SL = -1.00 event gap from actual entry;
- exit must occur inside the remaining original five-minute event horizon;
- no horizon reset;
- no second trade or flip for the event.

## Economics

- fixed 0.01;
- $0.02 round-trip commission;
- no averaging;
- no Martingale;
- no overlapping-position/margin model in this mechanism screen.

## Required comparisons

For A05/A10/A15 report:
- lattice events;
- CONT-owned count/share;
- MR-owned count/share;
- abstain count/share;
- physical trade velocity;
- full net / gross profit / gross loss / PF / expectancy / win rate;
- discovery and validation;
- CONT-owned economics separately;
- MR-owned economics separately;
- comparison to continuation-only proof-before-entry.

## Advancement

Dual proof ownership is structurally interesting only if:
- it improves economics versus continuation-only proof-before-entry;
- discovery and validation do not show a catastrophic sign reversal;
- MR ownership adds genuine value rather than merely increasing trade count;
- gross loss remains materially below immediate-entry continuation baseline.

No proof-distance sweep is authorized.

August sealed. Main `delta` read-only. MQL5 unauthorized.

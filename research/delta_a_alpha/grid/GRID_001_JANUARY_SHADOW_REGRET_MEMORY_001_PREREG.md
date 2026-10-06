# GRID-001 January Shadow-Regret Memory 001 — Preregistration

**Unit:** `DAA_GRID_001_JANUARY_SHADOW_REGRET_MEMORY_001`  
**Status:** FROZEN BEFORE COMPUTE

## Question

Can the grid learn, causally and without paying for two positions, whether recent events of the same family have favored mean reversion or continuation?

## Lattice

Use A05 from Adaptive Spacing Screen 001 because it retains approximately **1,791 events/day**, above the Jan–Jul R9 SYNTH average trade velocity.

No physical averaging.

## Counterfactual shadow contract

Every A05 event already has two bounded shadow outcomes:
- MR PnL;
- CONT PnL.

Both use:
- event-specific adaptive gap;
- 1-gap TP / 1-gap adverse bound;
- 5-minute horizon;
- executable Bid/Ask;
- $0.02 round-trip commission.

To guarantee causality, an event's shadow result does **not** enter memory until **5 minutes after the event**, even if its shadow trade would have closed earlier.

## Event families

Family key is intentionally coarse:

`(cross_direction, gap_band)`

Cross direction:
- DOWN;
- UP.

Gap bands:
- SMALL: gap < $1.50;
- MEDIUM: $1.50 <= gap < $3.00;
- LARGE: gap >= $3.00.

Total families: 6.

No additional features are allowed in this unit.

## Regret signal

For every matured event:

`regret_delta = (CONT_PnL - MR_PnL) / gap_usd`

Positive regret favors continuation.  
Negative regret favors mean reversion.

At a new event, use only previously matured events from the same family.

## Three fixed memory horizons

- M30: prior 30 minutes;
- M120: prior 2 hours;
- M480: prior 8 hours.

No other windows.

Require at least 3 matured observations in the family/window. Otherwise ABSTAIN.

Decision:
- mean regret > 0 -> CONT;
- mean regret < 0 -> MR;
- exactly zero -> ABSTAIN.

No deadband optimization.

## Frozen split

First 2/3 of January ticks = discovery.  
Final 1/3 = validation.

The online memory itself runs continuously through January. The split is for reporting only; validation decisions may use only outcomes that matured causally before each validation event.

## Required metrics

- accepted events / acceptance %;
- accepted events/day;
- MR vs CONT share;
- net / gross profit / gross loss;
- PF;
- expected payoff;
- win rate;
- discovery / validation metrics;
- comparison with A05 always-CONT;
- comparison with impossible A05 direction oracle.

## Advancement rule

This mechanism is interesting only if the same memory horizon or neighboring horizons:
- materially improves A05 PF/gross loss;
- remains stable in validation;
- preserves substantial velocity;
- does not rely on future outcomes.

If negative, retire simple family-memory and move to explicit structural-break / thesis-failure logic rather than tuning more windows.

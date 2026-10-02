# DELTA 005J-001 — State-Conditioned Initial Protection

**Status:** PREREGISTERED
**Mode:** historical Python simulation only
**Focus:** ENTRY + INITIAL-HOLD
**Mature Holding-Trade + Exit + High-Profit:** frozen / out of scope
**Stage-A:** [2026-01-01T00:00:00Z, 2026-01-18T12:00:00Z)
**Surface:** DUKAS_COINEXX_LIKE_P75
**August:** SEALED

## Derivation

DELTA_005H established that delaying the original R9 trailing activation from +$0.10 toward +$0.30 materially increases first-seconds survival.

DELTA_005I showed that simply widening trail distance is much lower leverage.

DELTA_005E found a broad causal state in which an original entry has survived into accepted post-break consolidation: the original boundary remains accepted and completed-S1 range has cooled.

DELTA_005J tests whether the 005H breathing-room mechanic should be applied **only when that accepted-consolidation state is present**, instead of globally loosening early protection.

## Parent behavior

All original R9-style entries remain unchanged.

Hard stop remains $0.30.

Normal R9 trail remains:
- activation +$0.10;
- distance $0.03.

## State observation

For the first 1000ms after entry, protection remains at the baseline R9 behavior.

At approximately 1000ms, if the trade is still open, evaluate only causal state available at that time.

Accepted-consolidation state requires:
- current side-adjusted boundary acceptance >= min_boundary_acceptance;
- completed-S1 range <= s1_range_ceiling.

No future state or outcome may enter this decision.

## Conditioned protection

If accepted-consolidation state is present:
- use accepted_trail_activation_price until protection_end_ms from entry;
- trail distance remains $0.03.

If the state is not present:
- retain baseline +$0.10 / $0.03 R9 trailing.

After protection_end_ms:
- revert to baseline +$0.10 / $0.03 logic for all positions still open.

This isolates state-conditioned initial breathing room rather than globally changing trailing.

## Frozen grid

S1 range ceilings:
- $0.50
- $0.75
- $1.00

Minimum boundary acceptance:
- $0.00
- $0.05

Accepted-state trail activation:
- +$0.20
- +$0.30
- +$0.50

Protection end:
- 3000ms
- 5000ms
- 10000ms

Observation grace:
- fixed 1000ms

Total variants: 54.

## Required diagnostics

For every cell:
- trades;
- winners;
- gross profit/loss;
- net;
- max balance drawdown;
- average hold;
- accepted-state count;
- accepted-state winners;
- baseline-state count;
- trail moves;
- 1/3/5/10/15s survival;
- winner retention;
- gross-loss change;
- survival lift.

## Desired shape

A useful region should preserve the 005H survival breakthrough while avoiding the large winner/gross-loss deterioration of globally loosened protection.

A broad neighboring region matters more than one isolated best cell.

## Phase boundary

This unit changes only initial protective timing.

No mature-trade hold, harvest, profit target, or final exit optimization is permitted.

August remains sealed.

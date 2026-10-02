# DELTA 005G-001 — Dual-State Initial-Hold Validator

**Status:** PREREGISTERED
**Mode:** historical Python simulation only
**Focus:** ENTRY + INITIAL-HOLD
**Mature Holding-Trade + Exit + High-Profit:** frozen / out of scope
**Stage-A:** [2026-01-01T00:00:00Z, 2026-01-18T12:00:00Z)
**Surface:** DUKAS_COINEXX_LIKE_P75
**August:** SEALED

## Derivation

005E discovered that durable initial holds can be owned by either:
1. immediate directional continuation; or
2. accepted post-break consolidation/cooling.

005F showed that accepted consolidation should not be translated into a delayed fresh entry.

005G therefore applies the state to the role in which it was discovered: validation of an already-open original R9-style entry.

## Parent entry

All original R9-style entries remain available.

No entry opportunity is removed before execution.

## Direct-continuation ownership

Between entry and the validation horizon, a trade earns direct ownership if at any tick:
- BUY: 250ms tick flow >= 0 and 1000ms tick flow >= 0;
- SELL: both mirrored <= 0.

Once earned, direct ownership is latched for the validation decision.

## Accepted-consolidation ownership

At the validation horizon, a non-direct-owned trade may remain open if:
- the modeled regime/spread gate remains open;
- side-adjusted current boundary acceptance >= the preregistered minimum;
- completed-S1 range <= the preregistered ceiling;
- the selected boundary-history rule is satisfied.

Boundary-history modes:
- CURRENT_HELD: only current acceptance matters;
- NEVER_LOST: the original boundary may never have been lost since entry.

## Early invalidation

At the validation horizon, if neither direct ownership nor accepted-consolidation ownership is present, close at the current executable quote.

After a trade is validated, the downstream R9-style stop/trail/max-duration/rearm lifecycle remains unchanged.

No later mature-hold or exit optimization is permitted.

## Frozen grid

Validation horizons:
- 250 ms
- 500 ms
- 1000 ms
- 2000 ms

Completed-S1 range ceilings:
- $0.50
- $0.75
- $1.00

Minimum boundary acceptance:
- $0.00
- $0.05

Boundary-history modes:
- CURRENT_HELD
- NEVER_LOST

Total configurations: 48.

## Required diagnostics

For every configuration:
- original entries / completed trades;
- winners;
- direct-owned validations;
- accepted-consolidation validations;
- early invalidations;
- early-invalidation average P/L;
- gross profit/loss;
- net;
- balance max drawdown;
- winner retention vs parent;
- 1/3/5/10/15s survival;
- rearm count.

## Desired shape

A useful region should reduce gross loss/drawdown materially while retaining most winners and improving the quality of first-seconds persistence.

A cell is not considered promising merely because it exits many trades early.

## Scientific boundary

This unit tests only the initial-hold validator.

Holding-Trade + Exit + High-Profit remains deferred.

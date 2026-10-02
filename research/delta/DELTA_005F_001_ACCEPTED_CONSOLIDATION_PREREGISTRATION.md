# DELTA 005F-001 — Direct Continuation + Accepted-Consolidation Recovery

**Status:** PREREGISTERED
**Mode:** historical Python simulation only
**Focus:** ENTRY + INITIAL-HOLD
**Mature Holding-Trade + Exit + High-Profit:** frozen / out of scope
**Stage-A:** [2026-01-01T00:00:00Z, 2026-01-18T12:00:00Z)
**Surface:** DUKAS_COINEXX_LIKE_P75
**August:** SEALED

## Derivation

DELTA_005E found that many durable initial holds do not maintain high flow/efficiency after the original break.

A broad pattern was:
IMPULSE -> ACCEPTED BOUNDARY -> S1 RANGE COMPRESSION / COOLING.

At 1s, S1 range < $0.50 with the boundary never lost had 73.39% 5s survival and 48.25% 10s survival.
The broader $0.50-$0.75 state had 68.24% / 39.29% survival.

The same structure exists inside the pool that immediate 005A sign-flow would reject.

## Architecture

When an original R9-style opportunity appears:

### Owner A — direct continuation
For a short preregistered handoff period, the opportunity may enter immediately whenever 250ms and 1000ms tick-count flow both align with the R9 direction while original R9 entry quality remains valid.

### Owner B — accepted-consolidation recovery
If Owner A has not entered by the fallback horizon, Owner B may enter the same direction using only causal state available at that horizon.

Owner B does NOT require R9's original S1 range minimum to remain active, because the forensic discovery is explicitly a post-impulse cooling state.

Owner B requires:
- the original minute/opportunity is still alive;
- no opposite-side cycle invalidation;
- regime/spread eligibility still open;
- current boundary acceptance >= preregistered minimum;
- completed-S1 range <= preregistered ceiling;
- boundary-history mode satisfied.

## Frozen grid

Fallback horizons:
- 250 ms
- 500 ms
- 1000 ms
- 2000 ms

S1 range ceilings:
- $0.50
- $0.75
- $1.00

Minimum current boundary acceptance:
- $0.00
- $0.05

Boundary-history modes:
1. CURRENT_HELD — current quote remains accepted regardless of an earlier brief loss;
2. NEVER_LOST — boundary has never been lost during the handoff.

Total configurations: 48.

No additional threshold may be introduced before results are persisted and GOV-013 leverage analysis is completed.

## Direct-owner flow

Direct owner uses the mild sign-only context identified in 005A:
- 250ms aligned flow >= 0 and 1000ms aligned flow >= 0 for BUY;
- mirrored <= 0 for SELL.

No stronger flow threshold is used.

## Lifecycle

After either owner enters, downstream stop/trail/max-duration/rearm behavior is the unchanged parent R9-style lifecycle.

No mature hold, exit, harvest or profit-target optimization occurs in this unit.

## Required diagnostics

For every configuration:
- total trades and winners;
- direct-owner entries/wins;
- recovery-owner entries/wins;
- recovery-owner win rate;
- net/gross loss/drawdown;
- parent trade/winner retention;
- 1/3/5/10/15s survival;
- recovery entry acceptance geometry;
- handoff attempts/cancels;
- direct vs recovery contribution.

## Success shape

A useful 005F region should:
- recover a material fraction of activity lost by 005A;
- preserve or improve winning-trade count relative to 005A;
- show better initial-hold survival for the recovery sleeve than the rejected pool;
- avoid merely trading activity for lower gross loss.

The candidate is not promoted solely because one cell has the best net number.

## Scientific boundary

005F is a Stage-A screen. Any subsequent version or specialist router requires a new version ID.

Holding-Trade + Exit + High-Profit remains deferred.

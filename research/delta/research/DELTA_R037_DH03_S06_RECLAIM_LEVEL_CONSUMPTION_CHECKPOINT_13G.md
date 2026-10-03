# DELTA R037 — DH03-S06 Reclaim-Level Consumption / Pivot Reuse — Checkpoint 13G

**Status:** COMPLETE NEGATIVE LOCALIZATION / FULL HISTORICAL PARITY NOT ACHIEVED  
**Unit:** R037_DH03_S06_RECLAIM_LEVEL_CONSUMPTION_AND_PIVOT_REUSE_PARITY_RECONSTRUCTION  
**Parent:** R037_DH03_S06_EVENT_IDENTITY_REARM_CHECKPOINT_13F  
**Vector:** DH03-S06 / `a3a086b7344c`  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Bounded question

The canonical DH-03 white paper describes LOCAL_RECLAIM as a completed S5 close **back through** a causally known fast pivot/reclaim level. 13G tested whether the remaining historical mismatch was caused by:
1. interpreting “back through” as an actual completed-S5 edge crossing; and/or
2. consuming the exact S15 pivot identity after a successful reclaim/reacceleration attempt.

All numeric thresholds and the 13C same-pullback fresh-exhaustion lifecycle remained frozen.

## Crash-safe replay

Preregistration, engine and producer were committed before official compute. GitHub rebuild gate / recovery-snapshot run **37159942295** passed. The replay used that committed snapshot.

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**  
Runtime: **10.03 s**  
Peak RSS: **698,560 KB**  
Raw result SHA-256:
`25c685e579ab30728dbc2cd649ecc22fdb94000a0371813ef272aeb07da8cbdb`

The two frozen 13F controls reproduced:
- strict close-beyond: **1,586 signals / 1,513 trades / 674 raw-positive / net -339.14**
- inherited-first close-beyond: **1,683 signals / 1,610 trades / 716 raw-positive / net -362.29**

## Results

Historical target:
**1,563 trades / 690 raw-positive wins / net -338.93**

| Profile | Trades | Raw+ | Net | Diagnostic |
|---|---:|---:|---:|---|
| strict close-beyond control | 1,513 | 674 | -339.14 | frozen control |
| inherited-first close-beyond | 1,610 | 716 | -362.29 | 13F control |
| strict true S5 edge-cross | 1,081 | 484 | -240.34 | 1,101 edge reclaims |
| inherited-first true edge-cross | 1,170 | 524 | -260.09 | 94 inherited / 1,190 edge reclaims |
| strict consume-used-pivot | 992 | 451 | -214.03 | 5,710 reuse blocks |
| inherited-first consume-used-pivot | 1,092 | 494 | -238.26 | 5,692 reuse blocks |
| inherited + edge-cross + consume | 1,049 | 474 | -230.03 | both restrictions active |

## Interpretation

This is a strong falsification result.

A literal previous-S5-to-current-S5 crossing interpretation of “back through” is much too restrictive. It removes roughly 330–430 trades relative to the already-underproducing strict control.

Treating a pivot as consumed after one successful attempt is even more restrictive. Thousands of later reclaim opportunities reference the same causal pivot identity, and forbidding that reuse collapses the signal population.

Therefore the historical DH03-S06 implementation almost certainly allowed:
- a completed S5 close simply **beyond** the eligible reclaim level rather than requiring the immediately previous S5 close to be on the opposite side; and
- reuse of a still-current causal S15 reclaim pivot across more than one fresh-exhaustion attempt inside the same original pullback.

This eliminates two attractive but wrong explanations for the residual.

## Decision

**Checkpoint 13G = NEGATIVE QA PASS / LOCALIZATION IMPROVED / FULL PARITY FAIL.**

Reject as dominant residual:
- true S5 edge-cross requirement;
- one-use reclaim-pivot consumption;
- their combination.

Retain the 13C strict close-beyond control as the stronger economic anchor. Do not promote the 13F inherited-first profile.

No threshold retuning, pending-TTL fitting, exit optimization, SORB integration, August access, or MQL5 work occurred.

## Next bounded unit

`R037_DH03_S06_SIGNAL_GENERATOR_RESIDUAL_PROVENANCE_DECISION`

Purpose: use the now-narrowed evidence to decide which remaining source-grounded generator/state provenance question is still reconstructible and worth testing, rather than continuing blind semantic sweeps.

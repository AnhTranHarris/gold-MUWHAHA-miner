# DELTA R037 — DH03-S06 Reclaim-Level Consumption / Pivot Reuse — Checkpoint 13G

**Status:** COMPLETE STRONG NEGATIVE QA / FULL PARITY NOT ACHIEVED  
**Unit:** R037_DH03_S06_RECLAIM_LEVEL_CONSUMPTION_AND_PIVOT_REUSE_PARITY_RECONSTRUCTION  
**Parent:** R037_DH03_S06_EVENT_IDENTITY_REARM_CHECKPOINT_13F  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Question

Does the remaining DH03-S06 population mismatch come from interpreting the white-paper phrase “closes on S5 back through a causally known fast pivot/reclaim level” as either:

1. a literal completed-S5 adverse-to-parent-side edge crossing; or
2. an event-owned reclaim pivot that is consumed after one successful reclaim/reacceleration signal?

No threshold, TTL, pivot-age number, exit, lot, or execution rule was retuned.

## Crash-safe official replay

The exact preregistration, engine, and producer were committed before compute:

- evidence commit: `2fbd1a54f1ada8aaa0c2831ae9bcb5142cc2442f`
- engine commit: `4f0eea113cf039fed36a725a7c4de77f1ddbea2f`
- producer commit: `813ec9aba663f09225a6716890f049df53310edc`

The producer snapshot came from successful Actions recovery run `37159942295`. Local Git blob verification matched the committed evidence, engine, producer, and bounded runner before execution.

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**

Official raw result SHA-256:
`25c685e579ab30728dbc2cd649ecc22fdb94000a0371813ef272aeb07da8cbdb`

Runtime: **9.92 s**  
Peak RSS: **697,992 KB**  
Exit: **0**

## Controls reproduced

Historical target:
**1,563 trades / 690 raw-positive / GP +151.82 / GL -490.75 / net -338.93 / DD 339.25**

13F strict control:
**1,513 trades / 674 raw-positive / net -339.14**

13F inherited-first control:
**1,610 trades / 716 raw-positive / net -362.29**

Both exact control fingerprints reproduced before any new semantic interpretation was accepted.

## Candidate results

| Profile | Signals | Trades | Raw+ | Net |
|---|---:|---:|---:|---:|
| STRICT_TRUE_EDGE_CROSS | 1,084 | 1,081 | 484 | -240.34 |
| **INHERITED_FIRST_TRUE_EDGE_CROSS** | **1,173** | **1,170** | **524** | **-260.09** |
| STRICT_CONSUME_USED_PIVOT | 993 | 992 | 451 | -214.03 |
| INHERITED_FIRST_CONSUME_USED_PIVOT | 1,093 | 1,092 | 494 | -238.26 |
| INHERITED_FIRST_EDGE_CROSS_CONSUME | 1,049 | 1,049 | 474 | -230.03 |

The formal leading new candidate is INHERITED_FIRST_TRUE_EDGE_CROSS, but it is still **393 trades and 166 raw-positive winners below** the historical target.

Pivot consumption is even more restrictive: the strict consumption profile blocks 5,710 reclaim evaluations and falls to 992 trades.

## Interpretation

The historical DH03-S06 behavior is not explained by a conventional “one breakout/retest per level” state machine and is not requiring a literal prior-close/current-close S5 edge crossing.

This is a strong negative localization:

- simple close-beyond semantics are necessary to preserve the historical activity scale;
- unlimited reuse by itself is not enough to explain the remaining residual;
- literal edge crossing removes hundreds of valid historical-scale opportunities;
- consuming a reclaim pivot after one signal removes even more.

Therefore the remaining discrepancy should not be attacked with another threshold search or another reuse restriction.

## Decision

**Checkpoint 13G = STRONG NEGATIVE QA / FULL PARITY FAIL.**

Reject as the primary residual:
- literal completed-S5 edge-cross requirement;
- one-use event-local reclaim pivot consumption;
- their combination.

Preserve the 13F bounds:
- strict post-original-pullback close-beyond control;
- inherited-first close-beyond as a non-promoted diagnostic bound.

## Next bounded unit

`R037_DH03_S06_SIGNAL_GENERATOR_RESIDUAL_PROVENANCE_DECISION`

Purpose: determine whether the remaining DH03 historical gap can still be reconstructed from source-compatible semantics or must be frozen as a provenance-limited best reconstruction, as was done for DH05, DH02-S11, and DH02-S08.

No numeric retuning, August, SORB, or MQL5.

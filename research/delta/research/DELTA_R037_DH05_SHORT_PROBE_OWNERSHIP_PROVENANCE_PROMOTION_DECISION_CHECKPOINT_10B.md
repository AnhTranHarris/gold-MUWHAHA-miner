# DELTA R037 — Short-Probe Ownership Provenance / Promotion Decision — Checkpoint 10B

**Status:** COMPLETE / ROBUST CHALLENGER RETAINED / HISTORICAL SEMANTIC PROMOTION REJECTED  
**Unit:** R037_DH05_SHORT_PROBE_OWNERSHIP_PROVENANCE_PROMOTION_DECISION  
**Parent:** R037_DH05_SHORT_PROBE_OWNERSHIP_ANTI_OVERFIT_VALIDATION_CHECKPOINT_10A  
**Raw ticks:** NOT ACCESSED  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Decision question

Does the 09Z relative-duration ownership router now have enough independent evidence to be frozen as reconstructed historical DH05 semantics?

The candidate rule is:

`max_probe_age_s < acceptance_tf_seconds -> FAILURE_CANDIDATE generator release; otherwise SERIAL_POST_QUAL`.

## Evidence reviewed

Independent/pre-09Y evidence:
- DELTA R003 causal grammar;
- original DH-05 white paper;
- R006 DH05 extension status;
- Checkpoint 09H full decoupling;
- Checkpoint 09I partial-release tests.

Candidate evidence:
- 09Y provenance harvest;
- 09Z exact causal Stage-A replay;
- 10A later-January P50/P75/P90 anti-overfit validation.

## What supports the challenger

09Z materially improved Stage-A funnel parity:
- serial control total funnel error: **978**
- routed challenger: **782**
- improvement: **196 / 20.04%**
- executable trade-count error: 336 -> **335**
- S06 unchanged versus serial control.

10A then survived independent later-January robustness:
- P50: **+$0.08**, +1 trade, +1 win
- P75: **+$0.07**, +1 trade, +1 win
- P90: **+$0.04**, +1 trade, +1 win

So the architecture is causally valid and did not reverse direction out of sample.

## What blocks historical-semantic promotion

The original DH-05 grammar describes one failed-break event chain:

`IDLE -> PROBE -> FAILURE_CANDIDATE -> REENTRY -> RECLAIM_CONFIRMED -> FAILED_BREAK_CONFIRMED -> REVERSAL_REBREAK -> ENTRY_ELIGIBLE`.

The white paper also states:
- `ProbeAge = elapsed time since first cross`;
- accepted original breakouts are routed away from DH-05;
- expired probes go to EXPIRED, not automatically to reversal.

No pre-09Y source found in the durable corpus specifies the exact relation:

`max_probe_age_s < acceptance_tf_seconds`

as an ownership router or says that this relation releases the upstream probe generator at FAILURE_CANDIDATE while preserving an independent downstream failure episode.

Earlier causal evidence also cuts against promotion:
- 09H rejected **universal** FAILURE_CANDIDATE release as dramatically too early;
- 09I rejected REENTRY and RECLAIM release points and retained serial generator ownership for the active reconstruction.

09Y discovered the relative-duration router by harvesting the same Stage-A six-vector fingerprints. 10A shows that the architecture is robust, but robustness cannot prove what the missing historical helper actually did.

## Decision

**Do not promote 09Z as historical DH05 semantics.**

Retain it as a **robust non-promoting challenger architecture** because:
- it is reconstructible;
- it improves Stage-A parity materially;
- it survives later-January P50/P75/P90 no-harm validation.

Close further same-sample ownership-router recuts. Reopening this family requires genuinely independent provenance, not another Stage-A partition.

## Remaining parity frontier

09Z remaining aggregate stage errors:

| Stage | Absolute error |
|---|---:|
| probe | **449** |
| reversal | 62 |
| signal | 62 |
| failure | 56 |
| qualified | 49 |
| reentry | 37 |
| reclaim | 36 |
| accepted | 31 |

The dominant unresolved defect is therefore upstream **probe count / boundary lifecycle** rather than acceptance or failure conversion.

## Next bounded unit

`R037_DH05_PROBE_COUNT_RESIDUAL_PROVENANCE_AND_BOUNDARY_LIFECYCLE_RECONCILIATION`

Purpose:
- explain the signed six-vector probe residual without numeric retuning;
- inspect boundary lifecycle, stale-boundary replacement, same-boundary attempt identity, and causal boundary supersession;
- do not repeat width sweeps, universal ownership release, acceptance-clock routing, or already-rejected rearm families;
- use provenance first, then only a small preregistered causal replay if an independently reconstructible boundary-lifecycle hypothesis emerges.

No August. No SORB. No MQL5.

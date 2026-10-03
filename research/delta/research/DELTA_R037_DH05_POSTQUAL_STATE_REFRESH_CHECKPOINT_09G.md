# DELTA R037 — DH05 Post-Qualification Acceptance + State Refresh — Checkpoint 09G

**Status:** COMPLETE NEGATIVE QA / ATR REFRESH REJECTED  
**Unit:** R037_DH05_POST_QUAL_ACCEPTANCE_WITH_PER_ATTEMPT_STATE_REFRESH_PARITY_RECONSTRUCTION  
**Parent:** R037_DH05_EVENT_RESET_BOUNDARY_IDENTITY_CHECKPOINT_09F  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

The 09F chronology clue was retained as a diagnostic branch: an acceptance bar must complete strictly after causal probe qualification. This unit tested whether the remaining probe/lifecycle deficit came from when the event M5 ATR snapshot is refreshed.

No numeric vector changed.

Producer:
`research/delta/experiments/delta_r037_dh05_postqual_state_refresh_parity.py`

Commit:
`d31136a0d24b969aec902f77799b2b772499181a`

Blob:
`4135f21714c1a9a5181ffefd59422250f0aa10b9`

File SHA-256:
`1aaa7f3bdfab5efc9447c0e451f4d4c3f6b134af4ad77d23275a5f4a6790d115`

Official runtime output SHA-256:
`49c572e4ca1b0be8b93fe80bdcfbf9dcbcab856dec480884cfe2d49d4be432a6`

Stage-A ticks: **4,205,709**.

## Profiles

- CONTROL_09E: total error **1064**
- POST_QUAL_BASE: **978**
- POST_QUAL_REATTEMPT_ATR: **980**
- POST_QUAL_QUALIFICATION_ATR: **977**
- POST_QUAL_CURRENT_ATR_QUALIFY: **979**

The ATR-refresh variants are effectively equivalent to the 09F post-qualification branch.

Best ATR-refresh stage errors:
- probe ~644
- qualified ~55
- accepted **21**
- failure ~64
- reentry **32**
- reclaim ~37
- reversal ~62
- signal ~62

This means ATR refresh slightly refines accepted/reentry counts but does not restore lost probe coverage and does not produce a meaningful new six-vector parity improvement.

## Decision

**Reject ATR snapshot timing as the missing historical mechanism.**

Preserve the 09F post-qualification acceptance chronology clue, but do not freeze it yet.

The next mechanism is architectural rather than parametric: separate the **probe generator lifecycle** from the **failed-break episode lifecycle**, as already suggested by historical Checkpoint-09 evidence distinguishing failed-break episode state, generator signal events, duplicate eligibility, and executable admission.

## Next bounded unit

`R037_DH05_DECOUPLED_PROBE_GENERATOR_AND_FAILURE_EPISODE_PARITY_RECONSTRUCTION`

Test whether a qualified probe that becomes FAILURE_CANDIDATE releases the probe generator to observe subsequent causal same-boundary attempts while the failed-break episode continues independently toward reentry/reclaim/reversal.

No threshold retuning. No SORB. No August. No MQL5.

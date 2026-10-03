# DELTA R037 — DH05 Event Reset / Boundary Identity Parity — Checkpoint 09F

**Status:** COMPLETE MATERIAL CHRONOLOGY CLUE / STANDALONE CARRY-FORWARD FAIL  
**Unit:** R037_DH05_EVENT_RESET_AND_BOUNDARY_IDENTITY_PARITY_RECONSTRUCTION  
**Parent:** R037_DH05_PROBE_QUALIFICATION_LIFECYCLE_CHECKPOINT_09E  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB integrated replay:** NOT STARTED / BLOCKED

## Bounded question

With 09C + 09D + 09E frozen, test only:
1. whether a newly revealed M5 boundary identity becomes freshly eligible after the active event resolves; and
2. whether BREAK_ACCEPTED may use a completed acceptance bar whose end preceded causal probe qualification.

No numeric vector changed.

## Producer

Path:
`research/delta/experiments/delta_r037_dh05_event_reset_boundary_identity_parity.py`

Commit:
`3c210c1da8919f407c4d844fe791affe6ab09874`

Blob:
`47408a4e8188817ba7e6a2c147679d178dd0c3e5`

File SHA-256:
`10dc506f89ad8fe8f0c8ae495c93e1789791540ab6e815d14dae26d3dd2a5b2b`

Canonical January source SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**.

The committed Git blob was verified against the local execution bytes before compute. Runtime was externally bounded and completed normally.

Official runtime output SHA-256:
`381d201413cb5a238f26fb11e6d9ccc739bc12f9eb094900a0f87067732de305`

## Control

09E control reproduced exactly:
- probe abs error 525
- qualified 29
- accepted 157
- failure 170
- reentry 39
- reclaim 38
- reversal 53
- signal 53
- total 1,064.

## Fresh-boundary identity result

Refreshing eligibility merely because a newly revealed same-side M5 swing has a new identity is effectively neutral:

- probe+qualified error: 554 -> **555**
- first-five error: 920 -> **920**
- downstream: 144 -> **144**
- total: 1,064 -> **1,064**

This independently confirms the earlier Checkpoint-04 conclusion that boundary replacement/identity refresh is not the primary remaining parity defect.

## Post-qualification acceptance-bar result

A strong chronology clue was found.

Rule:
> BREAK_ACCEPTED may only be evaluated on an acceptance bar whose completed end timestamp is strictly later than the causal probe-qualification timestamp.

This prevents a probe from being accepted by a bar that was already complete before the probe qualified.

Aggregate effect:
- accepted abs error: **157 -> 24**
- failure abs error: **170 -> 63**
- reentry abs error: **39 -> 34**
- total error: **1,064 -> 978**

Selected vector examples:
- A03 accepted/failure: 247/759 -> **212/786**, target 207/797
- S06: 259/1347 -> **248/1351**, target 245/1358
- S09: 66/140 -> **40/161**, target 40/168
- S10: 222/1084 -> **205/1095**, target 202/1106
- S16: 81/49 -> **52/78**, target 43/92

This is strong evidence that the historical generator did not allow pre-qualification completed bars to satisfy acceptance.

## Why it is not frozen yet

The same rule keeps the event alive longer and therefore reduces available probe cycles:
- probe+qualified abs error worsens **554 -> 697**
- downstream error worsens **144 -> 160**

That violates the preregistered standalone carry-forward rule despite the large accepted/failure repair.

The combined fresh-boundary + post-qualification profile is nearly identical:
- total error **976**
- probe+qualified **696**
- downstream **160**

So boundary identity refresh does not repair the lost probe coverage.

## Decision

**Checkpoint 09F = MATERIAL ACCEPTANCE-CHRONOLOGY CLUE / STANDALONE PROMOTION FAIL.**

Preserve as diagnostic evidence:
- post-qualification completed-bar acceptance is highly likely to be part of the historical semantics;
- it must not yet replace 09E by itself;
- new boundary identity refresh is rejected as a meaningful repair.

Do not retune vectors, integrate SORB, access August, optimize economics, or begin MQL5.

## Next bounded unit

`R037_DH05_POST_QUAL_ACCEPTANCE_WITH_PER_ATTEMPT_STATE_REFRESH_PARITY_RECONSTRUCTION`

Test only reconstructible state-refresh semantics around a causal same-boundary re-attempt while retaining the 09F post-qualification acceptance rule as a diagnostic branch:
- refresh event ATR snapshot on a new re-attempt;
- refresh event ATR snapshot on qualification;
- keep original event ATR as control;
- measure whether accepted/failure gains can be preserved while restoring probe/qualification coverage.

No numeric threshold retuning.

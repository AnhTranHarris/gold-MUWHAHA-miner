# DELTA R037 — DH03-S06 Pending Event Identity / Rearm Boundary — Checkpoint 13F

**Status:** COMPLETE MATERIAL EVENT-IDENTITY CLUE / FULL PARITY NOT ACHIEVED  
**Unit:** R037_DH03_S06_PENDING_EVENT_IDENTITY_AND_REARM_BOUNDARY_PARITY_RECONSTRUCTION  
**Parent:** R037_DH03_S06_PENDING_VALIDITY_CHECKPOINT_13E  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Timeout recovery

This unit resumed from already-committed 13F preregistration, engine, and producer bytes after a ChatGPT message-delivery interruption. No preregistration or source work was repeated. The timeout recovery pointer was reconciled before compute.

The official replay used the GitHub Actions recovery snapshot from producer commit `5d36e2c6ed3f3968a20f804f85e75dcb5eaef479`. The 13F evidence, engine, and producer matched their exact committed Git blob SHAs locally before execution.

Canonical January source SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**

Official raw result SHA-256:
`210b275d8134a5619dcfd129e2210bdd6f4310776bac703f7a686eb2dbe77308`

Runtime: **10.90 s**  
Peak RSS: **698,704 KB**  
Bounded-runner exit: **0**

## Bounded question

The source wording requires LOCAL_RECLAIM through a **causally known fast pivot/reclaim level**, but does not state that the pivot must have been revealed only after the original pullback began.

13F therefore tested only source-compatible pivot ownership boundaries. No numeric threshold, pending TTL, exit, capital, August, SORB, or MQL5 change was permitted.

## Primary DROP_OCCUPIED result

Historical target:
**1,563 trades / 690 raw-positive wins / GP +151.82 / GL -490.75 / net -338.93 / DD 339.25**

- POST_ORIGINAL_PULLBACK_CONTROL: **1,513 / 674 / +137.12 / -476.26 / -339.14 / 339.14**
- ANY_CAUSAL_DIAGNOSTIC: **1,672 / 749 / +151.25 / -522.89 / -371.64 / 371.64**
- INHERITED_FIRST_ATTEMPT_ONLY: **1,610 / 716 / +144.63 / -506.92 / -362.29 / 362.29**
- INHERITED_FIRST_THEN_POST_REARM: **1,083 / 488 / +99.50 / -337.80 / -238.30 / 238.43**
- START_LATCH_FIRST_ATTEMPT: **747 / 342 / +69.10 / -228.16 / -159.06 / 159.91**

The formal leading source-compatible profile is **INHERITED_FIRST_ATTEMPT_ONLY**, with trade gap **+47** versus the strict control gap **-50**. It is a material state-placement clue, not a promotion: activity crosses the target and economics worsen.

## Localization

The historical target lies between the strict post-original-pullback population and the first-attempt inherited-pivot population. The missing behavior is therefore unlikely to be another numeric threshold or pending lifetime rule.

The next high-leverage causal question is whether a reclaim pivot is:
- consumable after it triggers one reclaim,
- reusable only within the same attempt,
- reusable across a fresh-exhaustion rearm,
- or retired when a newer causal pivot supersedes it.

Those are event-identity / ownership semantics, not parameter fitting.

## Decision

**Checkpoint 13F = MATERIAL CLUE / FULL PARITY FAIL.**

Preserve:
- frozen DH03-S06 vector `a3a086b7344c`;
- 13B S5 reclaim timing;
- 13C same-pullback fresh-exhaustion rearm;
- 13E full original-event pending validity as a causal secondary constraint;
- 13F evidence that a limited pre-pullback inherited pivot can materially alter population.

Do not promote INHERITED_FIRST_ATTEMPT_ONLY as historical truth.

Compact result:
`research/delta/reference/DELTA_R037_DH03_S06_EVENT_IDENTITY_REARM_CHECKPOINT_13F.json`

## Next bounded unit

`R037_DH03_S06_RECLAIM_LEVEL_CONSUMPTION_AND_PIVOT_REUSE_PARITY_RECONSTRUCTION`

Test only source-compatible reclaim-level consumption/reuse semantics. No threshold retuning.

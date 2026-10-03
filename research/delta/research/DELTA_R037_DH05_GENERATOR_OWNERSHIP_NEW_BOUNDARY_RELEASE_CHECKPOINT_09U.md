# DELTA R037 — Generator Ownership / New-Boundary Release — Checkpoint 09U

**Status:** COMPLETE NEGATIVE QA / NEW-BOUNDARY RELEASE INSUFFICIENT  
**Unit:** R037_DH05_GENERATOR_OWNERSHIP_NEW_BOUNDARY_RELEASE_PARITY_RECONSTRUCTION  
**Parent:** R037_DH05_CONDITIONAL_FAILURE_CLOCK_CHALLENGER_CHECKPOINT_09T  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Question

Can the upstream probe generator be released when a failure episode is created, while preventing duplicate concurrent ownership of that exact M5 swing boundary and allowing only a newly revealed causal M5 boundary identity to start another generator event?

This is the bounded middle ground between:
- serial generator ownership, which under-produces sparse vectors; and
- 09H immediate full decoupling, which massively over-produced S06/S10.

Boundary identity is the causal symmetric-width-2 M5 swing reveal index, not price alone. No numeric threshold changed.

## Provenance and crash safety

Producer:
`research/delta/experiments/delta_r037_dh05_generator_ownership_new_boundary_release_parity.py`

- producer commit: `2cc4fe9428a0632d3dc04a968c1d274cd03c287c`
- producer blob: `941d602ab57861f4d2a253390e6cb496e00f4ccd`
- canonical January SHA-256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- Stage-A ticks: **4,205,709**
- runtime result SHA-256: `d53b4b08e20228c9482c187fc9a4a5f44bf0e49b5d93e40eb0b5aad95af362d8`
- elapsed: **12.62 s**
- peak RSS: **697,832 KB**
- exit: **0**
- hard timeout: **120 s**
- fresh isolated Numba cache
- atomic result write

The frozen POST_QUAL control reproduced exactly before candidate scoring.

## Result

The candidate fails the carry-forward criterion.

Control:
- aggregate signal-count error: **338**
- aggregate latch trade-count error: **336**

New-boundary-release candidate:
- aggregate latch trade-count error: **377**
- total eight-stage funnel absolute error: **2,479**
- probe+qualified error: **1,214**
- first-five error: **2,038**
- downstream error: **441**

Only **6** new-boundary generator starts occurred while a prior failure episode remained active across all six vectors. Maximum concurrent failure episodes was **2**; no episode or signal buffer overflow occurred.

Candidate signals/trades:
- A03 **214 / 214** vs 306 historical trades
- S05 **9 / 9** vs 51
- S06 **688 / 686** vs 672 historical signals / 615 trades
- S09 **11 / 11** vs 119
- S10 **255 / 255** vs 206
- S16 **9 / 9** vs 24

S06 deteriorates to:
- **688 signals**
- **686 trades**
- **283 wins**
- **-$164.73**

Historical S06 remains:
- 672 signals
- 615 trades
- 307 wins
- -$101.08

## Interpretation

Newly revealed M5 boundary identities are simply too rare during the lifetime of an older failure episode to explain the preserved sparse-vector density. The mechanism also raises dense S06/S10 activity without materially repairing S05/S09/S16.

09H and 09S leave a different bounded architecture worth testing: the ownership mismatch is perfectly aligned with the already-frozen acceptance timeframe split. The two S5 vectors need suppression or near-serial behavior, while the four S15 vectors are the historically sparse family that benefited from decoupled ownership.

That is a categorical ownership hypothesis, not numeric tuning. It remains non-promoting until causal replay and anti-overfit validation.

## Decision

**Checkpoint 09U = QA PASS / NEGATIVE RESULT / NO SEMANTIC FREEZE.**

Reject:
- new-boundary-only generator release as the missing universal ownership mechanism.

Keep frozen:
- 09C boundary/attempt ledger;
- 09D acceptance displacement;
- 09E per-attempt probe clock;
- 09F post-qualification acceptance chronology;
- current failure-age clock;
- current R9/Coinexx execution controls.

## Next bounded unit

`R037_DH05_ACCEPTANCE_TF_ROUTED_GENERATOR_OWNERSHIP_CHALLENGER_REPLAY_NON_PROMOTING`

Predeclared architecture:
- acceptance_tf = S5 -> serial POST_QUAL ownership;
- acceptance_tf = S15 -> FAILURE_CANDIDATE generator release with independent downstream failure episodes;
- no numeric retuning;
- S06 economics are a veto;
- any material Stage-A improvement requires anti-overfit validation before semantic promotion.

No August. No SORB. No MQL5.

# DELTA R037 — DH05 Post-Signal Episode Persistence / Invalidation Parity — Checkpoint 09K

**Status:** COMPLETE NEGATIVE QA / TESTED PERSISTENCE RULES REJECTED  
**Unit:** R037_DH05_POST_SIGNAL_EPISODE_PERSISTENCE_AND_INVALIDATION_PARITY_RECONSTRUCTION  
**Parent:** R037_DH05_SIGNAL_MULTIPLICITY_ADMISSION_CHECKPOINT_09J  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Timeout recovery

The prior chat interruption did not corrupt durable DELTA state. The 09K producer had already been committed and its GitHub Actions durability gate had passed. The bounded Stage-A compute also completed locally before message delivery ended.

Recovery verified:
- committed producer blob: `60debec9c4c4e8f468a8a768a5949514c802da30`;
- local producer git blob: exact match;
- producer file SHA-256: `6dd2ced331abf671fe688eb8aa847c4af350691b1ee3d17ca3be3169a21463d8`;
- canonical January SHA-256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`;
- Stage-A ticks: **4,205,709**;
- bounded runtime: **26.13 s**, max RSS about **700 MB**, exit status **0**;
- runtime result SHA-256: `d41fbc1c6ba548017e7ef1a6f4b246350d6e0c9952e53fe36ad6544f870c2031`.

The completed result was therefore persisted instead of rerunning the same 4.2M-tick job.

## Bounded question

Can the historical trade-density gap be explained by extending the post-first-signal lifetime of the current failed-break episode while keeping upstream chronology, numeric vectors, and R9-style executable admission frozen?

Profiles included:
- one-shot 09F/09J control;
- signal-refresh-clock variants;
- persistence until original-boundary retake;
- transition rearm on reversal/bar-edge;
- one-position-only versus exit-tick observation latch.

## Result

No tested post-signal persistence rule deserves carry-forward.

The one-shot control has aggregate six-vector executable-trade-count error **336**.

The best profile remains the already-known weak 09J clue:

`BOUNDARY_RECYCLE_REARM__ONE_POSITION_ONLY`

with aggregate trade-count error **324**.

This does **not** materially improve on 09J and still leaves the sparse vectors far below their preserved historical trade counts:

- A03: **203 vs 306**
- S05: **9 vs 51**
- S09: **11 vs 119**
- S16: **7 vs 24**

S06 remains:
- generator signals **648** vs 672;
- trades **647** vs 615;
- wins **275** vs 307;
- net **-$149.42** vs -$101.08.

Long-lived signal-refresh and persist-until-rebreak rules overproduce badly:
- signal-refresh/reversal-toggle trade-count error: **7,279**;
- signal-refresh/bar-edge: **8,241**;
- persist-until-original-rebreak/reversal-toggle: **59,831**;
- persist-until-original-rebreak/bar-edge: **66,847**.

## Interpretation

The preserved fingerprint now points away from manufacturing more generator signals.

The stronger architectural hypothesis is different:

> A single causal DH05 generator signal may authorize more than one executable entry while an execution-side mandate remains valid.

That can explain why preserved historical trade counts can exceed the preserved signal-stage counts in A03/S05/S09/S16 without forcing the generator itself to emit thousands of extra signals.

This is distinct from 09J/09K signal multiplicity. The next unit must keep generator counts frozen and vary only execution-side mandate persistence/re-entry.

## Decision

**Checkpoint 09K = QA PASS / NEGATIVE RESULT / NO NEW SEMANTIC FREEZE.**

Keep frozen:
- 09C boundary + repeated same-boundary attempt ledger;
- 09D acceptance semantics;
- 09E per-attempt probe lifecycle clock;
- 09F post-qualification acceptance chronology as diagnostic branch;
- serial pre-reversal episode ownership;
- one-position-at-a-time R9 execution semantics.

Do not:
- retune vectors;
- integrate SORB;
- access August;
- optimize mature exits;
- begin MQL5.

## Next bounded unit

`R037_DH05_EXECUTABLE_MANDATE_MULTI_ENTRY_PARITY_RECONSTRUCTION`

Test only whether one frozen generator signal can produce multiple executable entries under causal mandate persistence / invalidation rules, without creating extra generator signals.

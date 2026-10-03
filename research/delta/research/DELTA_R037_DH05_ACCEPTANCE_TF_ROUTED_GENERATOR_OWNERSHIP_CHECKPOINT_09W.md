# DELTA R037 — Acceptance-Timeframe Routed Generator Ownership — Checkpoint 09W

**Status:** COMPLETE NEGATIVE QA / NON-PROMOTING ROUTER REJECTED  
**Unit:** R037_DH05_ACCEPTANCE_TF_ROUTED_GENERATOR_OWNERSHIP_CHALLENGER_REPLAY_NON_PROMOTING  
**Parent:** R037_DH05_GENERATOR_REVERSAL_CLOCK_RELEASE_CHECKPOINT_09V  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Recovery / timeout audit

The user-visible message-delivery timeout did not erase the scientific cursor. The branch already contained the preregistered 09W producer while `CURRENT_STATE.json` correctly remained at durable 09V. This is the intended crash-safe ordering: preregister/commit source first; advance state only after compute, Drive write-back, manifest and CI.

The exact committed 09W producer and both committed runtime dependencies were reconstructed locally and verified by Git blob identity before official compute.

## Bounded question

Test the predeclared categorical ownership challenger:

- `acceptance_tf = S5` -> retain serial POST_QUAL ownership.
- `acceptance_tf = S15` -> release upstream generator at FAILURE_CANDIDATE while the downstream failed-break episode continues independently.

No numeric vector was retuned. Stage-A only. No August.

## Provenance / crash safety

Producer:
`research/delta/experiments/delta_r037_dh05_acceptance_tf_routed_generator_ownership_challenger.py`

- producer commit: `a26e2edf376aae42b72a8bf11dfd25b0fb38619c`
- producer blob: `53d4cd2c74ef9cc46411458d269d7a0a597c2b5a`
- producer SHA-256: `e1c971ef8f4e586e24cc262475ebcdc2b01399cc47d4fa2953386d5994975e59`
- runtime helper blob: `328b16a80cf5bff58734a556561625adf89100ae`
- conditional-clock dependency blob: `0749a0f326ff0a81006f7234f5065963e26e8dab`
- canonical January SHA-256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- Stage-A ticks: **4,205,709**
- runtime result SHA-256: `fd1a0a546ddee8876bbedb85cc06078ffbf65d8ed8f863c787fe942d7294b250`
- elapsed: **10.74 s**
- peak RSS: **697,976 KB**
- hard process timeout: **120 s**
- fresh isolated Numba cache
- atomic JSON output
- exit code: **0**

The exact serial POST_QUAL control reproduced before the challenger was scored.

## Result

### Control

- total funnel absolute error: **978**
- aggregate executable trade-count absolute error: **336**

### Acceptance-TF routed challenger

- total funnel absolute error: **2,450**
- aggregate executable trade-count absolute error: **309**
- trade-count error improvement: **27**
- funnel error deterioration: **+1,472**
- max concurrent failure episodes: **5**
- episode overflow: **0**
- signal overflow: **0**

Routed signals:
- A03 **236**
- S05 **9**
- S06 **651**
- S09 **11**
- S10 **227**
- S16 **7**

Routed executable trades:
- A03 **219**
- S05 **9**
- S06 **649**
- S09 **11**
- S10 **227**
- S16 **7**

The architecture therefore gains a small amount of executable-count fit while destroying the state-funnel reconstruction. It fails the joint carry-forward rule.

## S06 interpretation

S06 remains on the serial S5 branch, so its routed result is identical to control:
**651 signals / 649 trades / 274 wins / -$150.35**.

Historical S06 remains:
**672 / 615 / 307 / -$101.08**.

The producer's S06-veto boolean correctly remains false because the router did not worsen S06 relative to its control. The challenger is rejected because total causal funnel parity becomes dramatically worse, not because of an S06 delta.

## Provenance correction discovered during recovery

Checkpoint 09S hard-coded:
`S16 acceptance_tf = 15, reversal_tf = 5`.

The current committed frozen `VECTORS` tuple used by the causal replays encodes:
`S16 acceptance_tf = 5, reversal_tf = 5`.

Therefore 09S's statement that acceptance-timeframe grouping was perfectly sign-separated is not reliable as written. This is a metadata/provenance defect in the historical diagnostic, not a new numeric result.

Critically, Checkpoint 09T already replayed the proposed router causally using the live frozen `VECTORS` tuple and rejected it. Thus the 09S S16 metadata defect does **not** invalidate the later 09T causal rejection.

## Decision

**Checkpoint 09W = QA PASS / NEGATIVE / NO SEMANTIC FREEZE.**

Reject the acceptance-timeframe-routed generator ownership challenger.

Do not run anti-overfit promotion testing because the candidate fails Stage-A joint parity before that gate.

## Next bounded unit

`R037_DH05_ACCEPTANCE_TF_METADATA_PROVENANCE_RECONCILIATION`

Purpose:
- formally reconcile the S16 acceptance-timeframe discrepancy;
- correct the research ledger without changing frozen live semantics;
- confirm which historical conclusions remain valid;
- then resume generator-ownership provenance from the corrected ledger.

No numeric retuning. No August. No SORB. No MQL5.

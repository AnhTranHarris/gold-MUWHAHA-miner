# DELTA R037 — DH05 Probe Residual / Boundary-Epoch Reconciliation — Checkpoint 10C

**Status:** COMPLETE STRONG NEGATIVE QA / BOUNDARY-EPOCH HYPOTHESIS REJECTED  
**Unit:** R037_DH05_PROBE_COUNT_RESIDUAL_PROVENANCE_AND_BOUNDARY_LIFECYCLE_RECONCILIATION  
**Parent:** R037_DH05_SHORT_PROBE_OWNERSHIP_PROVENANCE_PROMOTION_DECISION_CHECKPOINT_10B  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB integrated replay:** NOT STARTED / BLOCKED

## Recovery / timeout audit

The repeated chat-level `Message delivery timed out` condition did not roll DELTA science back. Live durable state was already at Checkpoint 10B and its GitHub rebuild gate passed. This unit therefore resumed the first incomplete 10B frontier rather than rerunning 09E–10B.

The repository now also emits a post-gate `delta-recovery-<commit>` GitHub Actions artifact. The artifact is created only after the DELTA rebuild gate passes and contains `CURRENT_STATE.json`, DELTA QA helpers, and the R037 producer/reference/report/manifest corpus. The first recovery artifact completed successfully in workflow run **37144583714**, artifact **11281772413**.

## Independent provenance

The original DH-05 white paper states that stale swing boundaries can manufacture false failure events. The historical R032 vector remains frozen as `boundary_source = M5 swing`; this checkpoint did **not** change source or width.

Preregistered semantic:

`LATEST_GLOBAL_SWING_EPOCH`

Only width-2 M5 swing boundaries in the most recently revealed causal swing epoch may seed a **new** upstream probe. An older opposite-side boundary is retired from new-probe eligibility. Active event boundary `L` and already-created downstream failure episodes are not rewritten.

The exact 09Z relative-duration ownership architecture remains frozen.

## Crash-safe official replay

Producer committed before compute:

`research/delta/experiments/delta_r037_dh05_probe_residual_boundary_epoch.py`

Producer commit: `68a480ce0486435bcb3ac8278a4985d20317b11c`  
Producer blob: `ba4767c2f0c66233c34d8d701c466f56ac381456`  
Producer SHA-256: `106f0f7d166106eefd23e2210a2a62b01faf107e9ad67dab98b8363ca77c56f9`

The official compute was executed from the commit-bound GitHub recovery artifact. Local Git blob hashes matched the committed producer and imported R037 helper blobs before compute.

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**

Runtime:
- wall: **15.19 s**
- peak RSS: **698,548 KB**
- hard subprocess timeout: **120 s**
- Python faulthandler: enabled
- fresh Numba cache: yes
- atomic result write: yes

The producer first reproduced the exact 09Z control:
- probe absolute error: **449**
- total funnel absolute error: **782**
- aggregate trade-count absolute error: **335**

## Result — decisive rejection

The candidate catastrophically over-retired valid probe opportunity:

| Metric | 09Z control | Latest-global epoch | Change |
|---|---:|---:|---:|
| Probe abs error | 449 | **23,124** | **+22,675 worse** |
| Total funnel abs error | 782 | **31,174** | **+30,392 worse** |
| Trade-count abs error | 335 | **805** | **+470 worse** |
| S06 economic veto | — | **TRIGGERED** | reject |

Stage errors for the candidate:
`23124 / 2525 / 409 / 2100 / 1299 / 679 / 519 / 519`

Stage order:
`probe / qualified / accepted / failure / reentry / reclaim / reversal / signal`.

Candidate six-vector funnels:

- A03: **2862/445/93/352/201/133/98/98**
- S05: **3300/153/12/141/36/14/6/6**
- S06: **1600/718/115/603/538/314/299/299**
- S09: **3321/107/18/89/34/23/8/8**
- S10: **2715/577/96/481/285/139/101/101**
- S16: **3268/67/22/45/22/14/5/5**

S06 produced **298 trades / 122 wins / -$71.93**, badly missing its historical ledger despite the smaller net-loss magnitude.

## Scientific interpretation

The stale-boundary warning was real provenance, but the strict global retirement interpretation is wrong.

The historical DH05 engine must permit **independent side-specific M5 boundary memory** to survive newer opposite-side swing revelations for substantially longer than `LATEST_GLOBAL_SWING_EPOCH` allows. Therefore the remaining signed probe residual cannot be repaired by globally collapsing high/low boundary identity to the newest swing epoch.

This closes:
- global latest-swing-only new-probe eligibility;
- global opposite-side boundary retirement on every newer swing epoch.

It does **not** justify retuning width, numeric thresholds, or the 09Z ownership router.

## Decision

**Checkpoint 10C = NEGATIVE QA PASS / HYPOTHESIS REJECTED.**

Do not carry `LATEST_GLOBAL_SWING_EPOCH` forward.

Compact result:
`research/delta/reference/DELTA_R037_DH05_PROBE_RESIDUAL_BOUNDARY_EPOCH_CHECKPOINT_10C.json`

Full local official result SHA-256:
`ca0bd310a146ea8fb50dd02075ae373852b890f723e090da264bec7ff7679596`

## Next bounded unit

`R037_DH05_PROBE_RESIDUAL_CAUSAL_ATTEMPT_IDENTITY_PROVENANCE_RECONCILIATION`

Purpose: inspect whether the remaining signed probe residual comes from how repeated crossings are grouped into causal same-boundary attempts rather than from boundary retirement. Use provenance first. Do not repeat boundary-width sweeps, universal release/rearm families, acceptance-clock routing, or the rejected latest-global boundary retirement rule.

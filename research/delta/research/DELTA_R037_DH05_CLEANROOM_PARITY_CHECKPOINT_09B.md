# DELTA R037 — DH05 Clean-Room Rebuild Parity Gate — Checkpoint 09B

**Status:** COMPLETE NEGATIVE QA / CLEAN-ROOM PRODUCER DOES NOT REPRODUCE CHECKPOINTS 03/08/09  
**Parent:** R032-C03_PLUS_DH02_S11_S08  
**Prior durable unit:** R037_DH05_DIAGNOSTIC_SOURCE_DURABILITY_RECOVERY_CHECKPOINT_09A  
**Unit:** R037_DH05_DIAGNOSTIC_ENGINE_CLEANROOM_REBUILD_AND_CHECKPOINT03_08_09_PARITY  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**SORB integration:** NOT STARTED / BLOCKED

## Source integrity

- Canonical January source SHA-256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`.
- Source gzip integrity: PASS.
- Stage-A ticks: **4,205,709**.
- Committed producer: `research/delta/experiments/delta_r037_dh05_cleanroom_parity.py`.
- Live producer blob SHA: `7200022dd9772383cc4d91edbbe167131603d6c7`.
- Producer alignment commit: `7698eb63125efac4e0797e4d1c780e5d1eece83e`.
- Result SHA-256: `518b6b556ccfc2c75f0bdee6298ee70a12d7db06649ee6df6feb558d0cbfe480`.

The live aligned producer gives the same parity counts as the bounded replay below.

## Required historical/checkpoint fingerprints

Checkpoint 03 / neutral:
- A03 187
- S05 9
- S06 617
- S09 9
- S10 206
- S16 8

Checkpoint 08:
- onebar M5: 187 / 9 / 617 / 9 / 206 / 8
- onebar reversal-TF ATR: 258 / 14 / 691 / 41 / 251 / 14
- threebar M5: 145 / 5 / 558 / 9 / 151 / 6
- threebar reversal-TF ATR: 247 / 10 / 672 / 41 / 225 / 14

Checkpoint 09:
- neutral wait-reentry: 282 / 54 / 653 / 11 / 317 / 22
- stage-normalized wait-reentry: 393 / 86 / 717 / 89 / 383 / 38

## Clean-room replay result

| Profile | A03 | S05 | S06 | S09 | S10 | S16 | Abs error |
|---|---:|---:|---:|---:|---:|---:|---:|
| onebar_m5 | 144 | 8 | 342 | 4 | 165 | 1 | 372 |
| onebar_rev_atr | 211 | 11 | 375 | 20 | 225 | 6 | 421 |
| threebar_m5 | 118 | 5 | 323 | 4 | 134 | 1 | 289 |
| threebar_rev_atr | 192 | 9 | 366 | 20 | 200 | 4 | 418 |
| neutral_wait_reentry | 0 | 23 | 2 | 0 | 2 | 0 | 1312 |
| stage_wait_reentry | 0 | 37 | 2 | 7 | 3 | 2 | 1655 |

**Parity: FAIL for every required profile.**

## Localization

This is not a rounding or downstream trade-admission mismatch. The neutral onebar profile already under-produces at the earliest funnel stage.

Checkpoint-03 probe counts:
- A03 6,731
- S05 7,875
- S06 3,470
- S09 7,748
- S10 6,496
- S16 7,870

Current clean-room probe counts:
- A03 1,848
- S05 2,981
- S06 1,510
- S09 2,520
- S10 1,924
- S16 3,484

Therefore the current reconstructed **M5 boundary / probe-eligibility lifecycle is not the same semantic engine that produced Checkpoint 03**. Continuing to tune reclaim, reversal efficiency, ATR, or signal admission on this producer would be invalid.

The immutable DH05 numeric vectors are not changed.

## Decision

1. Reject this clean-room producer as a parity continuation source.
2. Preserve Checkpoints 03–09 as durable salvage evidence; do not rerun them.
3. Do not execute Checkpoint 10.
4. Do not integrate R037-SORB.
5. Repair only the upstream M5 swing-boundary and same-boundary probe-eligibility semantics.
6. The exact historical DH05 numeric vector parameters remain frozen.

## Next bounded unit

`R037_DH05_BOUNDARY_SOURCE_AND_PROBE_ELIGIBILITY_PARITY_RECONSTRUCTION`

Scope:
- reconstruct only causal meanings of frozen `boundary_source = M5 swing` and same-boundary re-eligibility;
- reproduce the Checkpoint-03 **probe and qualified funnel counts first** before testing later reclaim/reversal stages;
- use all six vectors as a fingerprint;
- no numeric threshold retuning;
- no new economics optimization;
- no SORB;
- no August;
- no MQL5.

Stop the next unit immediately if a boundary interpretation cannot materially approach the preserved six-vector probe fingerprint.

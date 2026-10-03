# DELTA R037 — DH02-S08 Parent-Direction Provenance Decision — Checkpoint 12C

**Status:** COMPLETE PROVENANCE LIMITATION FREEZE  
**Unit:** R037_DH02_S08_PARENT_DIRECTION_PROVENANCE_DECISION  
**Parent:** R037_DH02_S08_CONTEXT_PLACEMENT_CHECKPOINT_12B  
**Vector:** DH02-S08 / `7c70b5304ff7`  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Question

Do surviving DH01/DH02 materials independently preserve the exact historical S08 parent-direction aggregation/veto algorithm strongly enough to justify more same-sample reconstruction?

## Preserved evidence

Surviving source material does preserve:
- DH02 uses M15/M30/H1 parent context via DH01;
- entry eligibility requires rebreak confirmation while context remains valid;
- immutable S08 requires `DH-01 parent direction`;
- R032 preserves a stable **71 incremental S08-owned entries** both with and without S11 present.

It does **not** preserve:
- the exact historical DH01 aggregation placement used by S08;
- the exact veto/reset algorithm;
- the original historical R005 specialist producer bytes.

Checkpoint 12B tested all bounded context placements available from surviving evidence. Every placement remained at **37 raw-positive winners**, while the historical S08 fixture contains **42**. Moving the same context condition therefore cannot reconstruct the missing winner population.

## Deterministic decision

The committed 12C producer is provenance-only and accesses no market ticks. All gates passed.

Freeze:
`DH02-S08 entry requires causally valid DH01 parent context at rebreak/entry eligibility.`

Retain only as a labelled source-compatible surrogate:
`REBREAK_ONLY_RAW_PARENT_DIRECTION_CONTINUOUS_DWELL`

Do **not** promote that surrogate as historical truth and do **not** claim exact S08 parity.

Stream disposition:
`PROVENANCE_LIMITED_SOURCE_COMPATIBLE_REBREAK_CONTEXT_NON_PROMOTING`

Further Stage-A parent-context recuts are closed because they would infer missing historical semantics from fit rather than reconstruct them from preserved source.

## Crash-safe execution

Producer:
`research/delta/experiments/delta_r037_dh02_s08_parent_direction_provenance_decision.py`

Producer commit:
`4b8b05f96c4cc5e1b7e982154645c4f978dfa72b`

Producer blob:
`fc11affc8f4ee426e655baf138f89b40f7753128`

Producer SHA-256:
`13deee00916f9db3fd79e48c928f1edae88805bfcb55ecdf2b424f5031ea64f3`

Evidence:
`research/delta/reference/DELTA_R037_DH02_S08_PARENT_DIRECTION_PROVENANCE_EVIDENCE_12C.json`

Evidence commit:
`b430849965b4f4f1cf04bd68bba970c49aff9ca9`

Evidence blob:
`63448cf3939f5c90ba0e017bfb251b933b179be5`

Evidence SHA-256:
`6aea5378d4231f5f28b9d580366d219a41ee5a303c82fb24cf6a4a149e17a30c`

Official deterministic replay:
- elapsed: **0.66 s**
- peak RSS: approximately **92.7 MB**
- result SHA-256: `0c2147239902c16a35999d31c3fb4e883db24ff29c89738748c3f720ac584595`
- raw ticks accessed: **NO**
- numeric retune: **NO**

## Decision

**Checkpoint 12C = S08 STREAM CLOSED AS PROVENANCE-LIMITED / NON-PROMOTING.**

Do not:
- run more same-sample S08 parent-context permutations;
- retune S08 numeric thresholds;
- access August;
- integrate SORB;
- optimize mature exits;
- begin MQL5.

## Next bounded unit

`R037_DH03_S06_CLEANROOM_PARITY_RECONSTRUCTION`

Reconstruct DH03-S06 from its immutable vector, surviving white paper/prereg/results artifacts, and canonical Stage-A tick chronology before any integrated R032 replay.

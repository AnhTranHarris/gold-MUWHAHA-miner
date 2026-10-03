# DELTA R037 — DH03-S06 Signal-Generator Residual Provenance Decision — Checkpoint 13H

**Status:** COMPLETE PROVENANCE LIMITATION FREEZE  
**Unit:** R037_DH03_S06_SIGNAL_GENERATOR_RESIDUAL_PROVENANCE_DECISION  
**Parent:** R037_DH03_S06_RECLAIM_LEVEL_CONSUMPTION_CHECKPOINT_13G  
**Raw ticks:** NOT ACCESSED  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Decision

Freeze the 13C strict reconstruction as the **best reconstructible DH03-S06 surrogate**, but do not promote it as exact historical truth.

Frozen surrogate:
`POST_PULLBACK_REARM_FRESH_EXHAUSTION_STRICT_POST_ORIGINAL_PULLBACK_PIVOT`

Historical target:
**1,563 trades / 690 raw-positive / GP +151.82 / GL -490.75 / net -338.93 / DD 339.25**

Best reconstructible surrogate:
**1,513 trades / 674 raw-positive / GP +137.12 / GL -476.26 / net -339.14 / DD 339.14**

Residual:
- trades: **-50**
- raw-positive wins: **-16**
- net: **-$0.21**
- drawdown: **-$0.11**

The 13F inherited-first profile remains a diagnostic upper bound only:
**1,610 trades / 716 raw-positive / net -362.29**.

## Provenance gates

All gates passed:

- historical `r005_specialists.py` and `dh03_results.jsonl` bytes remain unrecovered;
- the surviving DH03 white paper does not preserve the exact fast-pivot algorithm;
- it does not preserve exact reclaim-level ownership, same-pullback rearm, or pivot reuse/consumption mechanics;
- 13C reconstructs the historical economic scale extremely closely;
- 13F brackets the historical activity target but the inherited-first alternative worsens economics;
- 13G proves literal S5 edge-cross and one-use pivot consumption are much too restrictive;
- no independent exact historical algorithm was recovered;
- further same-Stage-A semantic recuts would become retrospective fitting.

## Frozen source-compatible DH03 grammar

Preserve:

- structural-priority M15/M30 parent;
- adverse S15 pullback;
- weakening S15/S30 counterflow;
- causally known S15 fast reclaim pivot;
- completed-S5 reclaim;
- later completed-S5 reacceleration;
- the original still-parent-valid pullback may causally rearm with fresh exhaustion.

Do **not** infer the residual 50 trades / 16 raw-positive winners from the January sample.

## Reproducibility

Evidence:
`research/delta/reference/DELTA_R037_DH03_S06_SIGNAL_GENERATOR_PROVENANCE_EVIDENCE_13H.json`

Producer:
`research/delta/experiments/delta_r037_dh03_s06_signal_generator_provenance_decision.py`

Producer commit:
`37c5d3eb002241a8081e166b252ccb126268dc2f`

Official result SHA-256:
`ea7945a0e08b4a4faeb5912752a4197bb0beadeac2ba221877e26b0f712f2188`

Runtime: **0.62 s**  
Peak RSS: **92,980 KB**

## Next bounded unit

`R037_R032_FULL_SPECIALIST_PARENT_PARITY_RECONSTRUCTION`

DH05, DH02-S11, DH02-S08, and DH03-S06 are now all closed at their source-supported/provenance-limited boundaries. The next task is to reconstruct the R032 specialist parent using the frozen non-specialist backbone plus each specialist's explicitly labeled best reconstructible surrogate, quantify the residual against the historical R032-C03 parent, and determine whether SORB integration can finally proceed.

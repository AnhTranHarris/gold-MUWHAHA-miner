# DELTA R037 — DH05 Active-Boundary Freeze QA — Checkpoint 04

**Status:** COMPLETE NEGATIVE QA / NOT THE PARITY MECHANISM  
**Parent:** R032-C03_PLUS_DH02_S11_S08  
**Prior checkpoint:** DELTA_R037_DH05_PARITY_STAGE_FUNNEL_CHECKPOINT_03  
**Unit:** R037_DH05_ACTIVE_M5_BOUNDARY_FREEZE_DIAGNOSTIC  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Hypothesis

A newly confirmed same-side M5 swing might be incorrectly replacing an active DH05 event boundary before the probe/failure/reentry/reclaim sequence resolves. Test the causal alternative: freeze the active boundary for the event, retain the newest same-side swing as pending, and apply it only after the event returns to IDLE.

No frozen DH05 numeric parameter changed.

## Result

Historical trade targets: A03 306 / S05 51 / S06 615 / S09 119 / S10 206 / S16 24.

Checkpoint-03 baseline trades:
A03 187 / S05 9 / S06 617 / S09 9 / S10 206 / S16 8.

Active-boundary-freeze trades:
A03 **189** / S05 **9** / S06 **625** / S09 **10** / S10 **208** / S16 **8**.

The change is tiny and does not repair the sparse A03/S05/S09/S16 population. It also moves the already-near/exact S06 and S10 densities away from their targets.

## Decision

**REJECT active-boundary replacement as the primary remaining parity defect.**

The current pointer remains inside the broader reentry/reclaim/reversal feature-semantic reconstruction, but the next bounded substep is narrowed to reclaim confirmation timing/buffer semantics.

## Next bounded substep

`R037_DH05_PARITY_RECLAIM_CONFIRMATION_CLOCK_AND_BUFFER_SEMANTICS`

Keep fixed:
- M5 ATR;
- current M5 swing width/fingerprint;
- causal same-boundary re-eligibility;
- separate probe/failure clocks;
- frozen vector thresholds.

Test only reconstructible causal interpretations of:
- which completed clock confirms reclaim (S1 vs S5 vs vector reversal clock);
- whether the reclaim buffer is required on the completed close itself or on the prior tick excursion followed by a completed close back on the pre-break side.

Use six-vector stage counts before economics.

## Diagnostic hashes

- source SHA-256: `011f197c59c25be23d25c0904fcdb5477bbee786fcb898162654a6c8fbd7ef4a`
- output SHA-256: `6cbfe686054181f8757e3eb63b6c67dbfbe6ee94f93eff71ee6e2335ac145687`

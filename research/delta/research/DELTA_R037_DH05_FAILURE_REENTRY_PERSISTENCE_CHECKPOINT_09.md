# DELTA R037 — DH05 Failure/Reentry Persistence QA — Checkpoint 09

**Status:** COMPLETE MATERIAL CHRONOLOGY CLUE / UNIVERSAL RULE FAILS PARITY  
**Unit:** R037_DH05_PARITY_FAILURE_REENTRY_PERSISTENCE_DIAGNOSTIC  
**Parent:** R032-C03_PLUS_DH02_S11_S08  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Question
When a qualified probe becomes a failure candidate before price has causally re-entered the pre-break side, does `max_failure_age_s` expire while waiting for reentry, or begin only once causal reentry occurs?

No numeric vector parameter was changed.

Two feature profiles were retained:
- NEUTRAL = event M5 ATR + one-bar directional efficiency;
- STAGE_NORM_3BAR = reversal-TF ATR + 3-bar directional efficiency (Checkpoint 08 parity hypothesis).

## Historical trade targets
A03 306 / S05 51 / S06 615 / S09 119 / S10 206 / S16 24.

## Neutral profile

Current bounded failure clock:
187 / 9 / 617 / 9 / 206 / 8.

Wait-for-reentry then start max-failure clock:
**282 / 54 / 653 / 11 / 317 / 22**.

Important:
- A03 improves to 282 vs 306.
- S05 improves to 54 vs 51.
- S16 improves to 22 vs 24.
- S09 remains 11 vs 119.
- S10 overshoots 317 vs 206.
- S06 moves away to 653 vs 615.

## Stage-normalized 3-bar profile

Current bounded failure clock:
247 / 10 / 672 / 41 / 225 / 14.

Wait-for-reentry then start max-failure clock:
393 / 86 / 717 / 89 / 383 / 38.

This moves S09 materially toward its target but overshoots most of the remaining family.

## QA conclusion
Failure/reentry clock anchoring is a genuine high-leverage semantic dimension, but neither universal interpretation reproduces the six-vector historical fingerprint.

The neutral wait-for-reentry interpretation independently puts A03/S05/S16 very near historical density, while S09/S10 demand different behavior. That pattern strongly argues against treating one more global threshold as the solution.

## Decision
Do not promote either persistence interpretation as historical parity. Preserve both as bounded evidence.

The next diagnostic must examine the missing separation between:
- failed-break episode state;
- generator signal events;
- duplicate/repeated signal eligibility;
- one-position-at-a-time executable admission.

## Next bounded substep
`R037_DH05_PARITY_SIGNAL_MULTIPLICITY_AND_EXECUTABLE_ADMISSION_DIAGNOSTIC`

Requirements:
1. instrument signal timestamps and episode IDs;
2. keep one-signal-per-failure as control;
3. test only reconstructible transition-based repeated-signal rules, never “signal every qualifying bar” without rearm;
4. replay one-position-at-a-time admission separately;
5. compare S06 672 generator / 615 executed gap and six-vector density;
6. no hindsight suppression and no parameter retuning.

## Diagnostic hashes
- source: `457ff3e13c3784911d5b0018d5515c29907661f1f97ce224183234182faaf48d`
- output: `dc122c8c300065f290f5b151ed5f390eacb69e49f2d2138e52e6cf0f37b914f8`

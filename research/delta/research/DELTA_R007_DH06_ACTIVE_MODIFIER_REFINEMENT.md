# DELTA R007 — DH-06 Active Modifier Refinement Results

**Status:** COMPLETE NEGATIVE REFINEMENT / OBSERVER SIGNAL PRESERVED  
**Parent:** `DELTA_004_COINEXX_LIKE_DUKASCOPY_RESEARCH_SURFACE`  
**Scope:** ENTRY + INITIAL-HOLD  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Purpose
Test whether R006's strong DH-06 observer separation could be converted directly into a causal post-entry action without reopening mature exit research.

## Control
R9 P75 Stage-A:
- 16,801 trades
- 7,351 winners
- gross loss -$5,343.02
- net -$3,768.25
- max balance DD $3,769.83

## Test
64 active-modifier variants were evaluated from DH06-S08, S06, A04, and S03.

Actions included:
- retreat exit;
- favorable breathing/freeze;
- classify-then-breathe/freeze;
- combined retreat/favorable actions;
- 1s and 3s principal checkpoints.

R9 entry, hard stop, and downstream scaffold were otherwise held fixed.

## Result
Best net result:
`R007B-DH06-S03-CLASSIFY_THEN_FREEZE_CURRENT-3000ms`

- 16,821 trades
- 6,274 winners
- GP +$1,794.01
- GL -$5,512.87
- net -$3,718.86
- DD $3,719.93
- net-loss improvement ~1.31%
- GL deteriorates ~3.18%

The second implementation pass reproduced the same practical conclusion.

## Decision
**STOP CURRENT POST-ENTRY ACTION MAPPING.**

DH-06 remains useful as a causal observer/context mechanism. The current generic mapping from favorable/retreat state to immediate exit or extra breathing room is not worth more local tuning.

This negative result shifts leverage earlier in the lifecycle: direction/ownership before fill.

## Provenance
- `r007_dh06_results.jsonl`: `3f80c1041d551b7f4688b6b5038b6f676366902c204521c4a29b7a8a52d9f90b`
- `r007b_dh06_results.jsonl`: `efc4026eb62d7cf33766aec3e936e92c34adb09afd75f9d53f098a9e426c5d19`

Drive:
https://docs.google.com/document/d/1IR_j1KR76QZNpwXnRqxtlHXq8gpbLvM0HiIuPEprVsY/edit

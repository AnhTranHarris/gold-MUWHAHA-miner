# DELTA R037 — DH05 Reversal Efficiency / Stage Normalization QA — Checkpoint 08

**Status:** COMPLETE MATERIAL CLUE / PARITY NOT ACHIEVED  
**Unit:** R037_DH05_PARITY_REVERSAL_EFFICIENCY_AND_STAGE_NORMALIZATION_FINGERPRINT  
**Parent:** R032-C03_PLUS_DH02_S11_S08  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Fixed conditions
Bar-body reversal displacement, close-buffer reclaim, vector reclaim/reversal clock, M5 ATR for probe/reclaim/event state, same-boundary re-eligibility, separate clocks and frozen vector thresholds remained fixed.

Only two reversal-stage semantics were crossed:
- directional efficiency = current completed reversal bar vs signed 3-bar completed path;
- reversal displacement normalization = event M5 ATR vs completed reversal-timeframe ATR(14).

## Historical trade targets
A03 306 / S05 51 / S06 615 / S09 119 / S10 206 / S16 24.
Historical S06 generator target is **672 signals -> 615 executed trades**.

## Trade/signal counts

**1-bar efficiency + event M5 ATR**
187 / 9 / 617 / 9 / 206 / 8.

**1-bar efficiency + reversal-TF ATR**
258 / 14 / 691 / 41 / 251 / 14.

**3-bar directional efficiency + event M5 ATR**
145 / 5 / 558 / 9 / 151 / 6.

**3-bar directional efficiency + reversal-TF ATR**
247 / 10 / **672** / 41 / 225 / 14.

## Material finding

The last interpretation generates **exactly 672 S06 signals**, equal to the authoritative historical S06 generator count, using a reconstructible causal rule with no parameter retuning.

This is a high-value semantic clue, but it is **not parity**:
- current diagnostic: 672 signals / 672 executed trades / 293 wins / -$147.77;
- historical fixture: 672 signals / 615 executed trades / 307 wins / -$101.08.
- A03/S05/S09/S10/S16 still miss their historical densities.

Checkpoint-01's rule remains controlling: exact 672 count alone cannot establish parity.

## Localization consequence

The six-vector funnel proves that reversal-feature semantics alone cannot repair the family:
- S09 historical target 119 is greater than the current 62 reentries / 41 reclaims in the stage-normalized branch, so a downstream reversal threshold cannot create enough unique events.
- A03 and S16 likewise remain upstream-constrained.
- the historical 672→615 S06 signal-to-trade gap is still missing.

The next unit must therefore separate:
1. failure/reentry persistence and event multiplicity;
2. generator signal production;
3. one-position-at-a-time executable admission/overlap.

## Decision
Carry **reversal-TF ATR + 3-bar directional efficiency** forward as a parity hypothesis only, not a frozen historical reconstruction. Do not alter numeric thresholds.

## Next bounded substep
`R037_DH05_PARITY_FAILURE_REENTRY_PERSISTENCE_AND_SIGNAL_ADMISSION_DIAGNOSTIC`

Requirements:
- retain both the neutral baseline and the 672-signal semantic hypothesis for comparison;
- instrument event/failure IDs and signal timestamps;
- determine whether historical-like density requires longer-lived failure episodes or repeated discrete signals from a confirmed failure state;
- replay one-position-at-a-time admission separately from generator production;
- reject any rule that merely manufactures 615 trades by hindsight suppression.

## Diagnostic hashes
- source: `d8f539ce46487dcb1d1940ff62f1cd9b332d0c0eb332a4563e216c5ddeac5fe9`
- output: `fa4383e736d87345cf47bc9c6ca4fe91d519ec222eae5c6930ff81ebb0f5df72`

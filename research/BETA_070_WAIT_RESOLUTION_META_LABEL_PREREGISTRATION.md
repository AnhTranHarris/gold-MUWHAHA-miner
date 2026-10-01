# BETA070 — WAIT Resolution Meta-Label

**Status:** PREREGISTERED / NOT TESTED  
**Parent:** BETA069 delayed causal candidate surface  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

BETA069 established a causal primary side after WAIT, but a raw strength threshold was either negative or too sparse. BETA070 separates the two decisions:

1. **Primary side:** direction of the observed WAIT displacement (continuation).
2. **Meta decision:** take or skip that delayed executable trade.

This is the exact direction-vs-bet separation used in meta-labeling methodology.

## Candidate bus

Every valid 1s, 3s, and 5s BETA069 continuation candidate is placed on one chronological executable-entry bus. A proposal rejected at 1s may reappear at 3s or 5s. Once a trade opens, later candidates are blocked until its fixed 30-second exit.

## Causal meta features

In addition to the original BETA065 proposal state:
- wait age;
- observed displacement and absolute displacement;
- delayed entry spread and spread change;
- resolution strength = |move| / spread;
- wait-window path efficiency;
- wait-window signed quote-pressure;
- wait-window tick intensity and RMS quote movement;
- direction/origin agreement;
- UTC time cyclic features.

All are available by the delayed observation; the order is executed one source ordinal afterward.

## Models

- calibrated LightGBM binary classifier for `P(delayed continuation PnL > 0)`;
- LightGBM regressor for delayed continuation realized PnL.

Classifier calibration uses only the last chronological 20% of FIT via isotonic regression. CAL is reserved for policy-threshold selection.

## Selection

A frozen policy needs ≥50 one-position CAL trades, net > 0, PF > 1, positive average, and an adjacent threshold with the same sign. Freeze before DIAGNOSTIC.

If this survives both CAL and DIAGNOSTIC, it becomes the first candidate suitable for the human-facing QA packaging stage—still research only and still not MQL5-authorized.

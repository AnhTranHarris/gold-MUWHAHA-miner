# BETA068 — Sequence-Resolved Direction × Friction

**Status:** PREREGISTERED / NOT TESTED  
**Parent:** BETA065 durable RIGHT-edge proposal surface  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

BETA067 showed that execution friction is highly predictable while 30-second direction is not. This unit changes only the causal representation used for direction/magnitude.

## Added causal sequence state

At each existing BETA065 proposal, append completed RIGHT-edge lag channels:
- 16 × 250 ms: midpoint return, quote pressure, spread, log tick count;
- 12 × 1 s: midpoint return, quote pressure, spread, log tick count;
- 6 × 5 s: midpoint return, quote pressure, spread, log tick count.

All lags are observable at the proposal timestamp; no future bar participates.

## Overlap-aware training

Thirty-second labels overlap heavily. FIT observations therefore receive inverse-square-root weights based on the number of proposals whose 30-second outcome windows overlap locally. This reduces domination by dense bursts without deleting opportunity clocks.

## Model arms

1. sequence direction classifier × magnitude regressor + friction model;
2. sequence signed-displacement regressor + friction model;
3. specialist-specific sequence direction classifier × magnitude regressor + shared friction model.

Use bounded LightGBM trees. This is still a reconstructible public algorithm; no opaque proprietary signal is introduced.

## Selection

FIT trains; CAL chooses a nonnegative reconstructed-EV threshold. At least 50 one-position trades, positive net, PF >1, positive average, and a positive neighboring threshold are required. Freeze before DIAGNOSTIC.

## Research basis

Recent MetaQuotes material explicitly treats temporal sequence models as appropriate when snapshot features miss path dependence, while also warning that complexity must demonstrate incremental decision value. Label-overlap/concurrency work likewise supports down-weighting dense overlapping samples. These are methodological anchors, not evidence of XAUUSD profitability.

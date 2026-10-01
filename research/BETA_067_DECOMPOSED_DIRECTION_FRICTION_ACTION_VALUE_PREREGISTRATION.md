# BETA067 — Decomposed Direction × Friction Action Value

**Date:** 2026-10-01  
**Parent:** BETA065 RIGHT-edge proposal/label surface  
**Status:** PREREGISTERED / NOT TESTED  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Exact decomposition

For the fixed 30-second BETA065 executable labels:

- `d = (LONG - SHORT) / 2`
- `friction = -(LONG + SHORT) / 2`
- therefore `LONG = d - friction`
- and `SHORT = -d - friction`

This algebra separates future midpoint displacement from round-trip execution friction. BETA066 failed when it tried to learn the combined after-cost action directly.

## Hypothesis

Direction/magnitude may be learnable even when absolute after-cost value is not. Predict the directional displacement and friction separately, then act only if the reconstructed expected executable value is positive enough.

## Preregistered arms

1. **DIRECT_D_PLUS_COST** — nonlinear regressor for signed 30s displacement plus separate friction regressor.
2. **PROB_MAG_PLUS_COST** — direction classifier + magnitude regressor + friction regressor; expected signed displacement = `(2p_up-1) * magnitude`.
3. **SPECIALIST_D_PLUS_COST** — specialist-specific signed-displacement regressors plus shared friction model.

All use low-capacity HistGradientBoosting models and the same BETA065 causal features plus deterministic ratios already declared in BETA066.

## Selection

Train only on FIT. CAL selects an action-value threshold from a small nonnegative grid. Candidate must execute at least 50 trades, have positive after-cost net, PF > 1, positive average trade, and a neighboring threshold with the same economic sign. Freeze before opening DIAGNOSTIC.

## Why this is not a stacked-filter workaround

There is no new technical confirmation chain. The decision remains one economic comparison: predicted directional movement versus predicted friction. SKIP wins when expected executable value is not positive.

## Human-facing QA contract

If this unit survives, preserve enough state to display: specialist, predicted 30s displacement, predicted friction, reconstructed LONG/SHORT EV, chosen action, threshold margin, spread, and realized diagnostic outcome.

## Method sources

MetaQuotes' recent financial-ML material explicitly separates primary direction from trade/no-trade meta-labeling and emphasizes transaction-cost-aware labels. That supports the decomposition methodology; it does not establish XAUUSD edge.

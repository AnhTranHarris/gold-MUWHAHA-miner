# BETA066 — Nonlinear 30-second causal action discrimination

**Date:** 2026-10-01  
**Parent:** BETA065 durable RIGHT-edge proposal surface  
**Status:** PREREGISTERED / NOT YET TESTED  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Why this unit exists

BETA065 established that the linear Ridge value surface could not justify a positive CAL action, but its 30-second hindsight capacity remained positive for MICRO250 and RETEST/RENEW populations. BETA066 asks a narrower question: can a low-capacity nonlinear model causally distinguish **LONG / SHORT / SKIP** from BETA065's already-preserved RIGHT-edge states?

This unit does **not** alter the proposal clocks, source chronology, fees, or 30-second executable labels.

## Target

For each BETA065 proposal at 30 seconds:
- LONG when the long executable label is positive and at least as large as short;
- SHORT when the short executable label is positive and larger than long;
- SKIP when neither action is positive.

Future values define training/evaluation labels only. They are never inference features.

## Preregistered model arms

1. pooled multiclass HistGradientBoosting;
2. specialist-specific multiclass HistGradientBoosting;
3. paired HistGradientBoosting regressors for LONG/SHORT executable value.

Use only BETA065 FIT to train. Hyperparameter search is deliberately bounded to shallow/low-leaf models. CAL selects the policy threshold with a minimum trade-count safeguard. DIAGNOSTIC is not read for model or threshold selection.

## Features

Start from the 28 durable BETA065 as-of features and deterministic interaction terms derived only from them, including action/origin alignment, direction-relative returns/pressure, and spread-normalized movement/range terms. No new raw market read is required.

## Policy and scheduler

Chronological one-position scheduler, fixed 30-second occupancy for attribution. A proposal may act only if the frozen model and threshold admit LONG or SHORT; otherwise SKIP. No post-hoc technical confirmation stack.

## Selection gate

CAL candidate must have:
- at least 50 executed trades;
- positive after-cost net;
- PF > 1.0;
- positive average trade;
- no use of DIAGNOSTIC in selection.

Prefer a threshold neighborhood with similar sign and trade retention rather than a single isolated optimum. The chosen candidate is frozen before DIAGNOSTIC is opened.

## Human-facing QA relevance

A surviving policy must emit action, confidence/value score, specialist, proposal side, spread, top contributing state fields, and explicit SKIP reason. BETA066 alone does not authorize MT5.

## Sources guiding methodology

- MetaQuotes probability-calibration guidance: financial classification calibration is distinct from discrimination and requires time-aware validation.
- MetaQuotes/ONNX examples: gradient-boosted models can later be transported if the feature contract and numerical parity are preserved.

These sources justify the modeling method, not XAUUSD profitability.

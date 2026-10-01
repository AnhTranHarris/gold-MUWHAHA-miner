# BETA072 — Structural State-Conditioned Value Router

**Status:** PREREGISTERED / NOT TESTED  
**Parent:** BETA071 structural event bus  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

BETA071 showed that the four transparent structural clocks are individually negative in aggregate on CAL. BETA072 does not loosen those clocks. It asks whether profitable structural states are distinguishable using only information already known when the event becomes executable.

The candidate surface is BETA071 deduplicated by causal event identity so FIRST_RETEST tolerance duplicates do not artificially reweight training.

Three bounded economic heads are evaluated independently at 30/60/120 seconds: realized-PnL regression, profitability classification, and a hurdle expected-value model that combines probability of profit with conditional win/loss magnitude. LightGBM complexity is deliberately bounded.

Features are the BETA071 causal state only: mechanism, level timeframe, side-relative breakout/retest/sweep/compression measurements, level age, ATR state, actual entry spread, recent side-relative 1s/5s movement, quote count, and UTC cyclic time. No future price or diagnostic-derived feature enters inference.

FIT trains the models. CAL alone selects horizon/arm/threshold. A candidate requires at least 50 one-position trades, net > 0, PF > 1, positive average, and a neighboring threshold or horizon with the same economic sign. The policy is serialized before DIAGNOSTIC is opened.

If a candidate survives DIAGNOSTIC, the resulting ledger must expose mechanism, causal level, model score/EV, threshold margin, entry spread, selected horizon, entry/exit quotes and realized PnL for human-facing QA.
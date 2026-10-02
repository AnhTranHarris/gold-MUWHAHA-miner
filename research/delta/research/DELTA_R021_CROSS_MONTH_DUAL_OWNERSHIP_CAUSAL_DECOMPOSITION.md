# DELTA R021 — Cross-Month DUAL Ownership Causal Decomposition

**Status:** PREREGISTERED HARVEST / NO NEW LIVE RULE  
**Parent:** R020 failure / R016-T06  
**Scope:** ENTRY + INITIAL-HOLD / DUAL OWNERSHIP RESEARCH  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Research question

Why does contextual KEEP help some months and hurt others?

Harvest every T06 DUAL event on P75 January–July with only causal decision-time features, plus offline KEEP/FLIP counterfactual outcomes.

## Features

- intended side
- T06 extreme state
- 100/250/500/1000ms impulse
- S15/M5/M15/M30/H1/H4 NetATR
- session
- milliseconds into minute
- M5 ATR
- spread
- fast-path efficiency
- C04-selector membership

Outcome labels are offline-only.

## Quant discipline

- month-blocked analysis
- feature quantile/bin stability
- 2D interactions
- leave-one-month-out rule stability
- worst-month delta / sign consistency
- minimum support
- shallow reconstructible rule hypotheses only
- no live change until separate preregistered raw-tick replay

Execution script:
`r021_dual_monthly_harvest.py`

SHA-256:
`e53f7edd26dedb88092bdcffaf92a2d41676e2d2788500593324b723b4da6cdf`

Drive:
https://docs.google.com/document/d/1hAWeJ0S1XR2RbpGEl5O1x-L_8pmIUOTJnBpxhjNT2tk/edit

Workbook:
- 36 R021 Dual Monthly Harvest
- 37 R021 Cross-Month Slices
- 38 R021 Rule Lab

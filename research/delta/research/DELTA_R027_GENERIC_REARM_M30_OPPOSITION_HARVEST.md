# DELTA R027 — Generic Rearm M30 Opposition Causal Harvest

**Status:** PREREGISTERED HARVEST / NO GOVERNOR TESTING  
**Parent:** R026 causal mechanism  
**Surface:** P75  
**Months:** January–July 2026  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Purpose

R026 showed that first generic same-minute rearms after M30 KEEP-owned exits are net toxic in every month and almost always oppose the still-dominant M30 state.

R027 tests whether that mechanism generalizes to **ordinary generic same-minute rearms that the current P01 + M30 KEEP-owned architecture still allows**.

This is observation only. R027 does not suppress or alter trades.

## Frozen path

Run exact P01 + M30 KEEP-owned architecture.

Harvest actual generic same-minute rearm entries whose predecessor was not owned, so the rearm is permitted to execute.

Record realized outcome under the frozen R9 lifecycle.

## Primary causal split

- OPPOSED: rearm-direction `M30NetATR <= -0.35`
- NOT_OPPOSED: rearm-direction `M30NetATR > -0.35`

## Preregistered descriptive bins

M30:
- <= -0.70
- > -0.70 to -0.35
- > -0.35 to 0
- >= 0 to 0.35
- > 0.35

Rearm ordinal:
- 1
- 2
- 3

Wait:
- <=250 ms
- 251–1000 ms
- 1001–3000 ms
- 3001–10000 ms
- >10000 ms

Prior PnL:
- <=0
- >0

Session uses existing causal session code.

## Research rule

R027 is harvest-only.

Any generalized rearm suppression/governor rule is `HYPOTHESIS_ONLY` until a later preregistered action replay unit.

## Execution source

`r027_generic_rearm_m30_harvest.py`

SHA-256:

`523cd9720ebeee404c44f85bdd93dfd0f49ffc772cf3d92b7629482c502427d3`

## Drive

Doc:
https://docs.google.com/document/d/1iVc319_PoOmw-CfkCDZAzZ735LYKKhjBIsmjwV6EvVw/edit

Workbook tabs:
- `50 R027 Prereg`
- `51 R027 Monthly Summary`
- `52 R027 Slice Matrix`

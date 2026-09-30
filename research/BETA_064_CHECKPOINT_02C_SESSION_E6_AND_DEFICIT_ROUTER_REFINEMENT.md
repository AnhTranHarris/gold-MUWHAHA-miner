# BETA064 CHECKPOINT 02C — Session-Conditioned E6 Refinement + Deficit-Router Expansion

**Date:** 2026-09-30  
**Parent:** BETA064 Major Checkpoint 02 — frozen control  
**Status:** PROMISING RESEARCH CHILD — NOT A NEW MAJOR CHECKPOINT  
**Scope:** ENTRY→HOLD only  
**Hold→Exit:** deferred  
**August:** sealed and not read

## Objective

Increase useful Entry→Hold opportunity coverage beyond the frozen 5,070-trade Major Checkpoint 02 while preserving the owner's >=85% monthly Entry→Hold survivability requirement.

Two tracks were tested in parallel:

1. session-conditioned E6 Value Reversion refinement;
2. ownership/capacity recovery for under-covered E5/E7/E9/E10/E12 cells.

## Community-mechanics cross-check

Reconstructible public mechanics consistently support session-aware VWAP/value, liquidity sweep/reclaim, volatility/structure filters, and DST-aware session handling as candidate state variables. No community performance claim was imported as evidence.

The child therefore tested:
- session-value displacement;
- excursion age;
- sweep/reclaim context;
- trend contamination;
- return-to-value velocity;
- spread/ATR burden;
- session age;
- short-horizon efficiency;
- higher-timeframe ownership proxies.

## Rejected branch — independent session-value reversion clock

A new session-anchored value-reversion clock was tested independently of the original E6 daily-value geometry.

Result: rejected.

The frozen Entry model rejected almost all candidates at production-like gates, and the surviving broad tail showed poor real Dukascopy Entry→Hold behavior.

This branch is not carried forward.

## E6 diagnostic refinement

The universal E6 desk was too coarse.

### New York E6 child rule

Keep the existing causal E6 setup, but require:

- `ps_b75 >= 0.920`
- `eff60 >= 0.30`
- `friction = spread / atr60 <= 0.14`
- session-value displacement in trade direction `>= -2.5`

Across the inspected Jan–Jul child pool this rule produced:
- 381 eligible proposals before ownership;
- 87.93% aggregate survivability;
- worst observed month >=85.57%.

### UK E6 child rule

Require:

- `ps_b75 >= 0.905`
- `eff60 >= 0.40`
- `eff300 <= 0.10`
- session-value displacement in trade direction `>= -4`

Across Jan–Jul:
- 281 eligible proposals before ownership;
- 86.83% aggregate survivability;
- worst observed month >=85.32%.

Interpretation:
- NY reversion needs efficient short-horizon return plus low friction and not-too-deep residual displacement.
- UK reversion benefits from strong immediate return but weak five-minute directional ownership.
- Australia did not produce a robust enough expansion rule and remains on the frozen parent threshold.

## Scheduling diagnostic

Simply reordering the frozen candidate pool by earliest finish increased total trades only from 5,070 to about 5,097.

Therefore the coverage deficit is not primarily a greedy scheduling bug.

## Deficit-router refinement

The child retains the frozen base router first.

For non-E6, non-E11 under-covered session-gap specialists:
- E5 VWAP Reclaim
- E7 Sweep/Reclaim
- E9 Level Break
- E10 Compression Release
- E12 Failed Expansion

a shared child authority of:

`ps_b75 >= 0.9145`

was tested.

E11 Kinetic Ignition remains on the original frozen session thresholds because E11 is already over-covered relative to the SYNTH condition-matched denominator.

Base ownership is unchanged.

Session precheck remains:
- `ps_b75 >= 0.89`
- `es_b75 >= 0.08`

Scheduling uses chronological earliest-finish ownership after base intervals are reserved.

## Result

| Month | Parent Ckpt-02 trades | Child trades | Child survivability | Child FP success | Diagnostic value |
|---|---:|---:|---:|---:|---:|
| Jan | 726 | **766** | **88.77%** | 61.75% | +$764.53 |
| Feb | 910 | **1,032** | **85.56%** | 58.04% | +$1,153.64 |
| Mar | 1,463 | **1,495** | **87.76%** | 60.40% | +$1,753.66 |
| Apr | 589 | **667** | **88.46%** | 61.02% | +$724.64 |
| May | 509 | **586** | **90.44%** | 64.16% | +$650.37 |
| Jun | 585 | **640** | **89.84%** | 62.34% | +$693.63 |
| Jul | 288 | **333** | **89.49%** | 59.16% | +$271.72 |
| **Total** | **5,070** | **5,519** | **88.20% weighted** | **60.77% weighted** | **+$6,012.18** |

Increment vs frozen parent:
- +449 Entry→Hold trades
- +8.86% trade count
- weighted survivability decreases modestly from 88.44% to 88.20%
- every month remains above 85%
- diagnostic path-resolution value rises from +$5,782.07 to +$6,012.18

## Condition-matched SYNTH coverage

The 71,810 SYNTH Entry→Hold denominator remains frozen.

Parent Major Checkpoint 02:
- session×specialist matched = 3,044
- condition-cell coverage = 4.24%

Checkpoint-02C child:
- session×specialist matched = **3,164**
- condition-cell coverage = **4.41%**

So the child recovers:
- +120 additional condition-matched opportunities
- while also increasing total real Entry→Hold trades by +449.

Most of the new trades still do not close the enormous E6 SYNTH gap, but the direction is positive.

## Scientific caveat

The 0.9145 child authority and the explicit NY/UK E6 rules were selected after inspection of Jan–Jul.

Therefore this is **not blind certification** and must not replace Major Checkpoint 02.

August remains sealed.

A leave-one-month-out robustness pass was initiated but not completed within this bounded unit. Until that is finished, this result remains a promising child rather than a new major checkpoint.

## Quant decision

Carry Checkpoint-02C forward as a research child.

Do not freeze it as a new Major Checkpoint yet.

Next work:
1. finish leave-one-month-out threshold/rule robustness;
2. measure which +120 condition-matched opportunities came from E5/E7/E9/E10/E12 vs E6;
3. search for additional causal E6 substates without lowering the monthly survivability floor;
4. continue to avoid E11 expansion because it is already condition-cell saturated;
5. preserve Hold→Exit deferral;
6. keep August sealed.

No MQL5 change.


## Leave-one-month-out robustness — completed

The fixed causal child rules were retained. For the shared non-E6/non-E11 authority, each held-out month used the most permissive threshold selected from the other six months while requiring every training month to remain >=85% survivability.

| Held-out month | Chosen authority | Held-out trades | Held-out survivability |
|---|---:|---:|---:|
| Jan | 0.9105 | 824 | 88.71% |
| Feb | 0.9100 | 1,156 | **84.95%** |
| Mar | 0.9105 | 1,613 | 87.54% |
| Apr | 0.9105 | 737 | 87.79% |
| May | 0.9105 | 638 | 90.28% |
| Jun | 0.9105 | 705 | 89.50% |
| Jul | 0.9105 | 375 | 89.33% |

Weighted held-out survivability: **87.86%** across **6,048** held-out trades.

Result:
- 6/7 held-out months pass >=85%;
- February misses by approximately 0.05 percentage point;
- therefore C02C remains **promising but not freeze-ready**.

The next refinement should target the February failure regime specifically through causal state discrimination, not by raising the universal threshold so high that the coverage gain disappears.

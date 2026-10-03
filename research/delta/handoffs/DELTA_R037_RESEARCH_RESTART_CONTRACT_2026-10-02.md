# DELTA R037 Research Restart Contract — Fresh Independent Opportunity Source

**Status:** NEXT RESEARCH UNIT / PREREGISTRATION FIRST  
**Control parent:** `R032-C03_PLUS_DH02_S11_S08`  
**Replay:** NOT STARTED  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  

## Problem

R032-C03 passes P50/P75 but is ~9 P90 trades short of the 80% trade-retention floor while retaining +$4.00 net headroom versus ordinary opposite-rearm control.

The next activity source must be independent, causal, and economically defensible.

## Independence requirements

A candidate is eligible only if it:
- can trigger without a just-closed trade;
- is not generic same-minute rearm;
- is not post-exit recentered bracket logic;
- is not DH02-A01 late-Jan recutting;
- is not current DH-04 late-Jan density recutting;
- uses only right-edge-known causal inputs;
- is reconstructible;
- has explicit ownership/collision behavior;
- has a quality thesis, not just “more trades.”

## Control architecture

R032-C03 =
R025 M30_KEEP_OWNED ownership
+ GLOBAL NO_REARM
+ DH03-S06
+ DH05-S06
+ DH02-S11
+ DH02-S08

This exact parent must remain the comparison control.

## First deliverable

Before any R037 replay:
1. fresh reconstructible public/community research where useful;
2. source provenance;
3. causal grammar;
4. exact inputs/timeframes/lookbacks/visibility;
5. overlap/ownership contract with R032-C03;
6. multivariate bounded search design;
7. immutable configs/vectors;
8. advancement/fail criteria;
9. Drive/GitHub/workbook preregistration.

## Default research design

Preserve R004/R005 principles:
- multivariate baskets;
- theory anchors;
- balanced categorical screening;
- Sobol/LHS or justified space-filling design;
- immutable full vectors;
- no outcome-adaptive edits inside a frozen batch;
- preserve failed vectors;
- crash-safe execution order.

## Advancement

Advance only if:
- independent contribution is nontrivial;
- activity improves;
- net/GL/DD do not materially worsen;
- winner contribution is not toxic;
- no starvation/deletion trick;
- cross-surface behavior is credible;
- complexity is justified.

Do not fit exactly nine hindsight trades.

## Stop

Stop/restructure if:
- activity is bought with toxic net/GL;
- source depends on exit/rearm;
- source duplicates a closed family;
- positive effect is an isolated micro-edge;
- OOS or cross-surface freeze invalidates it;
- repeated local recutting is required.

## Window/surfaces

Stage-A:
`[2026-01-01T00:00:00Z, 2026-01-18T12:00:00Z)`

Default:
`DUKAS_COINEXX_LIKE_P75`

Advancing candidates:
P50 / P75 / P90 / DUKAS_NATIVE as governed.

Later-Jan holdout must not be mined repeatedly.

## Durability

Work in microsteps:
A research -> persist.
B prereg -> persist.
C code -> persist.
D compute -> persist.
E decision/workbook -> persist.
F CURRENT_STATE last.

## Drive

Full contract:
https://docs.google.com/document/d/1yfAl6mANMqu__OB-dRM_8yoBa3XbX7day12-_r_Kn0c/edit

## Gate

R037 research/prereg READY.  
R037 replay NOT STARTED.  
No promoted candidate.  
No locks.  
August SEALED.  
MQL5 NOT AUTHORIZED.

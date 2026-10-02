# DELTA R034 — Later-January OOS A01 Pocket Validation

**Status:** COMPLETE — ALL FIXED R033 POCKETS FAIL OOS  
**Parent:** R032-C03  
**Surface:** P90  
**Holdout:** 2026-01-18T12:00:00Z through final January tick  
**Warmup:** 2026-01-14T00:00:00Z to holdout boundary, indicator/state only  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Frozen validation set

Seven R033 discovery pockets were frozen before validation:

1. P01 NESTED_S5_S15
2. P02 S5_EFF_DISP
3. P03 S1_TIME
4. P04 MICRO_M1
5. P05 MICRO1000_M30
6. P06 S1_S15
7. P07 H1_S5

No same-window promotion, threshold retuning, or post-holdout pocket invention was allowed.

## Holdout control

- R9 trades: 2,659
- R9 wins: 1,121
- R9 net: -$583.86
- R032-C03 parent trades: 2,115
- parent wins: 875
- parent trade retention: 79.5412%
- parent winner retention: 78.0553%
- parent net: -$500.16

## Results

| Pocket | Δ Trades | Δ Wins | Trade Retention | Δ Net vs Parent | Decision |
|---|---:|---:|---:|---:|---|
| P01 NESTED_S5_S15 | +8 | +4 | 79.8420% | -$0.81 | FAIL_OOS_NET |
| P02 S5_EFF_DISP | +9 | +4 | 79.8797% | -$1.98 | FAIL_OOS_NET |
| P03 S1_TIME | +6 | +0 | 79.7668% | -$3.55 | FAIL_OOS_NET |
| P04 MICRO_M1 | +6 | +2 | 79.7668% | -$1.63 | FAIL_OOS_NET |
| P05 MICRO1000_M30 | +2 | +0 | 79.6164% | -$1.17 | FAIL_OOS_NET |
| P06 S1_S15 | +4 | +2 | 79.6916% | -$0.94 | FAIL_OOS_NET |
| P07 H1_S5 | +11 | +4 | 79.9549% | -$3.68 | FAIL_OOS_NET |

## Decision

Every fixed R033 pocket worsens net out of sample.

The R033 leading NESTED_S5_S15 discovery pocket does not validate.

P07 comes closest to the 80% activity floor but still misses it while spending more net than the parent.

Therefore:
- no A01 pocket is promoted;
- DH02-A01 pocket threshold recutting is stopped;
- the next activity source must be independent of A01.

## Provenance

R034 result SHA-256:

`1d9788a257b707ba26b1b2bcebf621e5948f5680e1ec9869569a9133b744cf3e`

Google Doc:
https://docs.google.com/document/d/1zJFYYsTJc3Qrv10f-UtBiLwiBiQr8h5ypmIAmxz4cus/edit

Workbook tabs:
- `63 R034 Prereg`
- `64 R034 Results`

## Current gate

- promoted candidate: NONE
- metric lock: NONE
- A01 pocket refinement: STOP
- next: independent specialist density-source validation
- August: SEALED
- MQL5: NOT AUTHORIZED

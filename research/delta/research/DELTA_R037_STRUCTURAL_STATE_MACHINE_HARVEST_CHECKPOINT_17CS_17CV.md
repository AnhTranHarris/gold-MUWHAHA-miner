# DELTA R037 — Structural State-Machine Harvest — Checkpoint 17CS–17CV

**Status:** COMPLETE / NO STAGE-A SURVIVOR  
**Unit:** R037_HIGH_VALUE_STRUCTURAL_STATE_MACHINE_HARVEST_CHECKPOINT_17CS_17CV  
**Parent:** R037_XECTSB_LEADER_INDEPENDENT_LATER_JAN_VALIDATION_CHECKPOINT_17CR  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Question
Can either of two independent closed-bar structural grammars produce enough Stage-A supply and nonnegative direct 30-second economics without tuning?

Tested unchanged:
- R037-123NB-v1: confirmed width-3 1-2-3 reversal neckline break on M1 and M5.
- R037-MSnR-DBO-v1: source-described rolling A/V double-breakout staircase on M1 and M5.

Producer commit: `074eaca06b5dcebeb1d9b7c2b9ca570fc2e551e8`  
Producer blob: `7f8c5bafb9d4e23844764d4c5787fe7b0e1c90d6`  
Producer SHA-256: `d9827814b9bbabad867a01cdcc71451e1c48d6aa93f04d7b03c6e0cd8144596b`  
Result SHA-256: `cb2deae8dc8ef84d7bb0bd56a8be4fbd0ba85be1ed0236edf2f97cae3a59c600`  
Runtime: **6.863 s**

## Results
| Lane | Trades | Days | Wins | Net | Gate |
|---|---:|---:|---:|---:|---|
| 17CS 123NB M1 | 608 | 14 | 288 | -$104.96 | FAIL |
| 17CT 123NB M5 | 120 | 13 | 58 | -$22.26 | FAIL |
| 17CU MSnR DBO M1 | 942 | 14 | 422 | -$187.95 | FAIL |
| 17CV MSnR DBO M5 | 177 | 12 | 81 | -$34.02 | FAIL |

All four lanes pass activity supply and fail economics. This localizes the failure to **entry quality / immediate persistence**, not scarcity.

## Decision
Retire both families unchanged. No pivot-width sweep, scan-length sweep, timeframe rescue, side/session filter, ATR/EMA overlay, or exit rescue.

**Next:** `R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST`

Search priority remains genuinely independent XAUUSD entry classes with a causal event lifecycle and native short-horizon persistence.

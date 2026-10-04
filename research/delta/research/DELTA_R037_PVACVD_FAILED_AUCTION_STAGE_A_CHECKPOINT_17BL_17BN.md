# DELTA R037 — Previous-Day Volume Profile Failed Auction + CVD — Checkpoint 17BL–17BN

**Status:** COMPLETE / NO STAGE-A SURVIVOR  
**Parent:** R037_SVWAPR_STAGE_A_SCREEN_CHECKPOINT_17BK  
**Surface:** native S5/M1 tick-rooted signals → DUKAS_COINEXX_LIKE_P75 execution  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Official Stage-A result

| Profile | Trades | Days | Wins | Net |
|---|---:|---:|---:|---:|
| 17BL S5 price-only failed auction | 350 | 10 | 159 | -$72.29 |
| 17BM S5 + directional delta sign | 272 | 10 | 120 | -$59.55 |
| 17BN M1 + directional delta sign | 76 | 10 | 42 | -$10.09 |

S5 delta sign removed 78 trades and improved net by $12.74, but all three unchanged profiles remained negative.

## Durability

Producer commit: `1ac1e168216d89721e7316233415559d3738cd39`  
Producer blob: `49d3ac127b0698b16d65467ebd51befb6e52711c`  
Producer SHA-256: `ae6c6d90380f77b41d973539d824a25b726709a8d7ca03f0da2e671324b65b38`  
Official result SHA-256: `890c96a49e58780690ed7ef93797537a3d92f66f50e1aabad70495ec64846ea5`

The local execution bytes matched the committed Git blob exactly. Canonical January and the 4,205,709 Stage-A tick count were verified. Compute ran under a hard 120-second process timeout and atomic JSON replacement.

Workbook readback: `69 R037 Research Harvest!A169:H176` — PASS.

## Decision

**RETIRE PVACVD WITHOUT RESCUE.**

No row-size, value-area, delta-magnitude, timeframe, session, side, stop, trail, or hold retuning.

## Next

`R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST`

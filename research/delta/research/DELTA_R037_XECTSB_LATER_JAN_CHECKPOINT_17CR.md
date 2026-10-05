# DELTA R037 — XECTSB Independent Later-January Validation — Checkpoint 17CR

**Status:** COMPLETE / INDEPENDENT VALIDATION FAIL  
**Candidate:** 17CQ_M15_EMA9_21_TOUCH_SWING10  
**Parent:** R037_XAUUSD_EMA_CROSS_TOUCH_SWING_BREAK_STAGE_A_SCREEN_CHECKPOINT_17CP_17CQ  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Purpose

Validate the unchanged M15 XECTSB grammar that survived Stage-A at **20 trades / 10 days / 11 wins / +$0.68**.

No threshold, side, session, timeframe, or exit rescue was admitted.

Preregistration commit: `11bb98ec46eaf2d30e1a8bed872b696c0abd1922`

Validator commit: `f5395817cfbb08e0f237f6a50298f2998534f063`

Validator blob: `095b44e83272ef4cbfab850d9786e9a2f44711f7`

Validator SHA-256: `bba34e6176f66ab9e013a7c93fa469bf0370101fef33ef5d1fa6580071900e2b`

## Control gate

The committed Stage-A parent was hashed before execution and the Stage-A control reproduced exactly:

**20 trades / 10 days / 11 wins / +$0.68**

Only then was the later-January result allowed to persist.

## Independent later-January result

Economic window: 2026-01-18 12:00 UTC through end of January, with warmup from 2026-01-14.

Result:
- **20 trades**
- **10 distinct days**
- **7 official wins**
- gross profit **+$4.03**
- gross loss **-$7.62**
- direct net **-$3.79**
- zero spread rejects
- all 20 exits hit STOP.

Lifecycle: 49 crosses -> 41 touches -> 27 touch-breaks -> 20 entries.

## Decision

**RETIRE R037-XECTSB-v1 unchanged.**

Supply survived; economics did not. No post-result rescue.

Official result SHA-256:
`03cccb90eb3d34e69e3896b1a0b486c974b2380c0bbd7f48673d4b8d7f7ff191`

Workbook readback:
`69 R037 Research Harvest!A297:I303`

## Next

`R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST`

# DELTA R037 — XECTSB Stage-A Screen — Checkpoint 17CP–17CQ

**Status:** COMPLETE / M15 STAGE-A SURVIVOR  
**Unit:** R037_XAUUSD_EMA_CROSS_TOUCH_SWING_BREAK_STAGE_A_SCREEN_CHECKPOINT_17CP_17CQ  
**Family:** R037-XECTSB-v1  
**Parent:** R037_VCE_RAW_RELEASE_INDEPENDENT_LATER_JAN_VALIDATION_CHECKPOINT_17CO  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Source-grounded hypothesis

The preregistered source grammar was EMA9/21 cross -> later EMA9 touch -> later touch-candle break -> later completed close beyond the frozen pre-cross 10-bar swing. Opposite cross resets the lifecycle and only one entry is admitted per cross.

Every state transition must occur on a later completed bar than the prior transition. Same-bar retrospective ordering is prohibited.

Preregistration commit:
`2d5bc884d77e9ae6b327429ce28a0784928de925`

Producer:
`research/delta/experiments/delta_r037_xectsb_stage_a_17cp_17cq.py`

Producer commit:
`d10d553a141a510ff654fa221f7f3cdc5b223ecc`

Producer blob:
`19c9e12a54ef4c6dd89da4875a5d68d726288aa1`

Producer SHA-256:
`c26dc710879a86b9447dfaf2e236c4f3621151a3ab2a62d35aef8f34f44ae03e`

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**.

## Crash-safe recovery

The message-delivery timeout occurred after preregistration and producer durability. Recovery therefore resumed at the first incomplete phase only: bounded Stage-A compute.

The exact committed producer SHA-256 and canonical January SHA were verified before replay. The replay was constrained to 120 seconds and wrote output atomically. It completed normally in **4.315 seconds**.

## Results

| Lane | Trades | Days | Wins | Direct net | Decision |
|---|---:|---:|---:|---:|---|
| 17CP M5 | 76 | 11 | 37 | **-$14.88** | RETIRE |
| 17CQ M15 | 20 | 10 | 11 | **+$0.68** | ADVANCE |

M15 lifecycle diagnostics:
- 46 EMA9/21 crosses;
- 38 later EMA9 touches;
- 26 later touch-candle breaks;
- 20 completed swing-break entries;
- zero spread rejects.

## Decision

**Advance 17CQ_M15_EMA9_21_TOUCH_SWING10 unchanged to independent later-January validation.**

Do not rescue the M5 lane. Do not retune thresholds, add session/side filters, optimize exits, use August, or begin MQL5.

Official result SHA-256:
`7d941b248db91d42f7c56f1cf79b06efe5e037aedca85719d9b39333ac71c75b`

Workbook readback:
`69 R037 Research Harvest!A289:I296`

## Next

`R037_XECTSB_LEADER_INDEPENDENT_LATER_JAN_VALIDATION`

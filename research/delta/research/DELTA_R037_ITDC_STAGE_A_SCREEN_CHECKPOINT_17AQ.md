# DELTA R037 — Intrinsic-Time Directional Change Stage-A Screen — Checkpoint 17AQ

**Status:** COMPLETE / FAMILY RETIRED / NO RETUNE  
**Unit:** R037_INTRINSIC_TIME_DIRECTIONAL_CHANGE_STAGE_A_SCREEN  
**Parent:** R037_TCFH_STAGE_A_SCREEN_CHECKPOINT_17AP  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Question

Can the source-grounded intrinsic-time directional-change operator provide a viable 30-second XAUUSD entry source at the finest threshold in the cited real-tick study (0.02%)?

Two preregistered direction semantics were tested without threshold tuning:
1. **Overshoot continuation:** trade in the newly confirmed directional-change direction.
2. **Alpha first-unit contrarian:** trade against the newly confirmed move, representing only the first contrarian unit rather than the article's multi-unit cascade.

## Integrity

Prereg commit: `adccb54efa49aa4f91b9701ec5c393d51be25fa4`  
Producer: `research/delta/experiments/delta_r037_itdc_stage_a_17aq.py`  
Producer commit: `b6317dfd8cbe98616e2eb0e8e150a06ea9e1f522`  
Producer blob: `af3c5ac2d2533c97f14ef9b00ccaae69172d3dee`  
Producer SHA-256: `96b24dabb068cc7c8759fd2972cb208cd19e1cf7e0f9f651bb8fc705a58e7dee`  
Result SHA-256: `f34c5d187886da5be0a7e7fa0d56dee6b9dabce151b51084443a91cc7344dfcf`

The exact committed Git blob compiled locally before official compute. Canonical January SHA and 4,205,709 Stage-A ticks were verified. The official replay ran under the 120-second hard timeout with atomic result writing.

## Result

The operator emitted **26,782** events: 13,391 up and 13,391 down.

- **C01 continuation:** 26,590 trades / 12,082 official wins / gross profit +$2,933.83 / gross loss -$8,219.12 / **-$5,285.29 net**.
- **C02 first-unit contrarian:** 25,875 trades / 11,403 official wins / gross profit +$2,440.33 / gross loss -$8,535.11 / **-$6,094.78 net**.

Both families had overwhelming event supply and overwhelmingly failed the economic floor. More than 25,000 trades in each profile exited by STOP.

## Decision

**RETIRE R037-ITDC-v1 WITHOUT RETUNING.**

This is not a candidate for threshold rescue. The failure is too large to justify post-result delta fitting, side/session filtering, or exit tuning.

**Next:** `R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`.

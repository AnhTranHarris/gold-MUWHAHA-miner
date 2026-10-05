# DELTA R037 — XAUUSD Inside-Bar Continuation Stage-A Screen — Checkpoint 17CK-17CL

**Status:** COMPLETE / NO STAGE-A SURVIVOR  
**Unit:** R037_XAUUSD_INSIDE_BAR_CONTINUATION_STAGE_A_SCREEN_CHECKPOINT_17CK_17CL  
**Parent:** R037_CONTROLLED_PAUSE_CONTINUATION_STAGE_A_SCREEN_CHECKPOINT_17CI_17CJ  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Timeout recovery
The official result was durable in commit `b6d984e97479dbf008701055bb7ea9435b7f444f` before a message-delivery interruption stopped report/manifest/cursor closure. Recovery reran the exact committed producer under the bounded runner and reproduced the durable fingerprint.

Producer commit: `a2fe05cf918b0d57e0a74b29f7fd57105e7d80be`  
Producer blob: `a402aa9f98cce954da087e616363b36264115b51`  
Producer SHA-256: `0032a54fce6ca0d32f369c216436660b7f0f696cbfdc9180e4dd8bc3af06f003`  
Result SHA-256: `2875381fe02aa41a4399783b9c86d9ca053163df65f29fd2e77aa745ca7cb2af`

## Results
- **17CK M15:** 132 raw inside-bar patterns -> 3 quality-pass -> 2 trades across 2 days -> 2 wins -> **+$0.16**. Supply gate fails.
- **17CL H1:** 41 raw patterns -> 0 quality-pass -> 0 trades. Supply/economics gates fail.

The M15 2/2 result is retained only as a clue. Weakening the disclosed 80/50 filters after observing the result would be rescue tuning.

## Decision
**RETIRE R037-XIBC-v1 / NO POST-RESULT RESCUE.**

No threshold, timeframe, side, session, ATR, or exit rescue. No August. No MQL5.

## Next
`R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST`

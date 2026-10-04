# DELTA R037 — Impulse Exhaustion Reversal Stage-A Screen — Checkpoint 17BD

**Status:** COMPLETE / ECONOMICALLY POSITIVE BUT INSUFFICIENT SUPPLY / RETIRED  
**Unit:** R037_IMPULSE_EXHAUSTION_REVERSAL_STAGE_A_SCREEN  
**Family:** R037-IER-v1  
**Parent:** R037_SQRM_STAGE_A_SCREEN_CHECKPOINT_17BC  
**Surface:** native Dukascopy M5 signal / DUKAS_COINEXX_LIKE_P75 execution  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Preregistered question

Does a source-faithful M5 gold impulse-exhaustion pattern—unusually large full-bodied impulse followed immediately by an opposite candle closing through the impulse body—create executable 30-second reversal persistence?

Frozen before compute:
- M5 bars;
- 20-bar average-range lookback;
- impulse range >= 1.5x recent average range;
- impulse body >= 70% of full candle range;
- next candle must reverse direction and close beyond the prior impulse body;
- first executable P75 tick after confirmation;
- frozen 30-second DELTA execution lifecycle;
- no parameter/timeframe/session/side/exit rescue.

Preregistration commit: `9f4c17f6f9247f6bf492bfe39922fc0437aa69a7`  
Producer commit: `c26cb43511c3e63ded2ed4fab2bc469b293b9897`  
Producer blob: `98375b1c8f6fb93dad442314785f784535831ef9`  
Producer file SHA-256: `553286477fe728d1ae7e85d3ede687f7914bc0cba94129226a2dd856b3ee94ee`

The local execution copy reproduced the committed Git blob exactly before execution.

## Official Stage-A result

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**

- M5 bars: **3,036**
- raw signals: **5**
- executable trades: **5**
- distinct days: **5**
- long / short: **2 / 3**
- official wins: **4 / 5**
- gross profit: **+$1.07**
- gross loss: **$0.00**
- direct net: **+$1.02**
- exits: **5 STOP / 0 MAX_HOLD**

Compact result SHA-256:
`6b429647dcdff31d44c1d42333d58ad89a86dc4c4d0e88a4706390b6d3dfb189`

## Decision

The pattern is directionally interesting but **fails the preregistered minimum-supply gate** of 20 trades. Five trades cannot support advancement.

Therefore:

**RETIRE_IER_STAGE_A_NO_EXECUTABLE_SURVIVOR**

No parameter rescue, lower threshold, alternate timeframe, session split, side split, or exit retuning is permitted on Stage-A.

## Timeout recovery finding

This unit also confirms that the prior ChatGPT message-delivery interruption was not equivalent to research loss. The preregistration and producer had already been committed before the browser message failed. Recovery correctly resumed at the first missing durable phase—official compute—without repeating source harvest or producer construction.

The recovery pointer is now checkpointed after each durable phase, not only after final unit completion.

## Next

`R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`

Priority: harvest a structurally different, sufficiently frequent entry source rather than continuing low-supply reversal-threshold families.

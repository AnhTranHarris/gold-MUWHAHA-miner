# DELTA R037 — Session VWAP Pullback Reclaim Stage-A Screen — Checkpoint 17BK

**Status:** COMPLETE / NO STAGE-A SURVIVOR  
**Parent:** R037_CONTINUATION_FAST_HARVEST_CHECKPOINT_17BH_17BJ  
**Surface:** native completed M1/M5 midpoint bars → DUKAS_COINEXX_LIKE_P75 execution  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Fixed question

Can a session-reset, tick-volume-weighted VWAP trend-side first-touch reclaim produce sufficient causal 30-second XAUUSD edge under frozen DELTA execution, without post-result tuning?

The family was preregistered before compute at commit `464a536e3fe7b5249877218e628fc2f047a6a4ce`.

## Producer / timeout safety

Final producer:
`research/delta/experiments/delta_r037_svwapr_stage_a_17bk.py`

Final producer commit:
`f3de5dd5958feebf3c06f8b1a607de05db2974cb`

Final producer blob:
`674b1c903e2107163411fa0fc7799ac29b5b11ad`

File SHA-256:
`83a8bdab353259774cd251deb508d34b80a0da428deae9f63ab3cfefcbe3088b`

The exact committed blob was verified locally before the accepted compute. Two earlier execution attempts were rejected as tooling-only failures caused by newline serialization in the atomic writer; neither produced an accepted scientific result. The final producer compiled cleanly and the official replay ran under a hard 120-second OS timeout.

Canonical source SHA:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**.

## Results

| Profile | Trades | Days | Wins | Net | Decision |
|---|---:|---:|---:|---:|---|
| London M1 first-touch reclaim | 11 | 8 | 6 | -$2.95 | FAIL |
| New York M1 first-touch reclaim | 14 | 10 | 5 | -$3.60 | FAIL |
| London M5 first-touch reclaim | 13 | 9 | 8 | -$0.61 | SUPPLY FAIL |
| New York M5 first-touch reclaim | 12 | 9 | 8 | +$0.20 | SUPPLY FAIL |

No profile met the preregistered **>=20 trades / >=5 distinct days / nonnegative direct net** advance gate.

Official result SHA-256:
`a9ee9321222786135b272084eaa5689b119569e5f096bbdd04bd973e919ed1ea`

## Interpretation

The family does not qualify as an executable candidate. The useful meta-harvest clue is narrower: slowing from M1 to M5 materially improved direct economics, and New York M5 became slightly positive, but the confirmation grammar collapsed supply below the required floor.

That clue may inform the mechanism class selected for the next independent source harvest, but it does **not** authorize sigma/session/side/timeframe/exit rescue on SVWAPR.

## Decision

**RETIRE SVWAPR 17BK WITHOUT RESCUE.**

No sigma retuning, session-window changes, side/day filtering, extra timeframe variants, mean-reversion inversion, stop/trail/hold optimization, August access, or MQL5 translation.

Workbook readback:
`69 R037 Research Harvest!A161:H168` — PASS.

## Next

`R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST`

Select a distinct source-grounded mechanism using the completed R037 meta-harvest. Favor mechanisms combining a meaningful price/liquidity anchor with delayed causal confirmation while rejecting already exhausted raw indicators, naked breakouts, generic candlestick geometry, and touch-only microstructure.

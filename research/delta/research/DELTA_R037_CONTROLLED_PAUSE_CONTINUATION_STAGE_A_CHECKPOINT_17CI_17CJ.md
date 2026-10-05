# DELTA R037 — Controlled-Pause Continuation Stage-A Screen — Checkpoint 17CI–17CJ

**Status:** COMPLETE / NO STAGE-A SURVIVOR  
**Parent:** R037_VCE_QIM_CONFIRMATION_STAGE_A_SCREEN_CHECKPOINT_17CE_17CH  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Purpose

Test two previously untested source-grounded continuation families selected specifically for natural XAUUSD supply and controlled-pause timing rather than another generic oscillator.

Preregistration:
`research/delta/reference/DELTA_R037_CONTROLLED_PAUSE_CONTINUATION_PREREG_17CI_17CJ.json`  
Commit: `0c779b1cf94a9d4b29b3e5c0ea5a0b7f94b17409`

Producer:
`research/delta/experiments/delta_r037_controlled_pause_continuation_17ci_17cj.py`  
Commit: `79ef49f6936d22b0ab3b0166934247f0f4dd99cc`  
Blob: `55e1b29b76ed3cd039e3e7d96c482a6291c2d6e9`  
SHA-256: `da6fae9a5b165a0ee5f4c4b542db0e8f8ec89f00dba0e1643be19b0a4e82cdaa`

The local producer's Git blob matched the committed GitHub blob exactly before official compute. The bounded runner completed in **6.240 seconds**.

## Results

| Lane | Trades | Days | Wins | Direct net | Decision |
|---|---:|---:|---:|---:|---|
| 17CI SuperTrend pullback/rebound M5 | 39 | 10 | 19 | **-$5.72** | RETIRE |
| 17CJ NR7 M30 session breakout | 34 | 11 | 14 | **-$4.37** | RETIRE |

Both families pass the activity/day gates and therefore provide a clean economic rejection rather than a supply failure.

17CI diagnostics: **78** qualifying pullbacks, **39** completed confirmation signals.  
17CJ diagnostics: **82** NR7 bars, **44** armed zones, **34** triggers, **10** expiries.

## Interpretation

The 30-second Miner objective does not reward these source-default continuation grammars under frozen P75 economics. This is stronger evidence than a zero-signal result because both families had enough native event supply to test the intended hypothesis.

Do not rescue through:
- SuperTrend factor/ATR retuning;
- NR7 timeframe/session/offset changes;
- side or weekday filtering;
- exit tuning;
- August;
- MQL5.

Official result SHA-256:
`45db038715b6d239930e86f3a5b138324db0460552576dc8a1e3ec58cbcc56ad`

## Next

`R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST`

Bias: prioritize public source families explicitly tested on XAUUSD and event-defined continuation/retest mechanics, preferably with enough native event supply to avoid another rare-pattern dead end.

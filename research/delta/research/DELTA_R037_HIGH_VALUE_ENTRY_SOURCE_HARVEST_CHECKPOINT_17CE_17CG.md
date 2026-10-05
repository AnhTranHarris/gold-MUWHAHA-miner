# DELTA R037 — High-Value Entry Source Harvest — Checkpoint 17CE–17CG

**Status:** COMPLETE / NO EXECUTABLE SURVIVOR  
**Parent:** R037_BREAKER_BLOCK_RETEST_STAGE_A_SCREEN_CHECKPOINT_17CC_17CD  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Purpose

Screen three independent, source-grounded continuation families with adequate expected XAUUSD event supply. All rules were preregistered before producer code and official compute. No post-result threshold, timeframe, side, session, or exit rescue was allowed.

Preregistration commit: `248b3628ef3d3a357ff4272286e48292f4490f34`

Producer:
`research/delta/experiments/delta_r037_high_value_entry_harvest_17ce_17cg.py`

Producer commit:
`062ff64772b8b90d67298aac171b7d7b07d09fd6`

Producer blob:
`e559fd825f86334cf6a5e018f823e00531c3b15d`

Producer SHA-256:
`b4b8342b63c8ebcae1519f7d8d5f859d34d5f37ac60f9a3d3b349b85ea85aed1`

Official bounded compute runtime: **5.938 seconds**.

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**.

## Results

| Lane | Trades | Days | Wins | Direct net | Decision |
|---|---:|---:|---:|---:|---|
| 17CE Kumo + AO M5 | 64 | 11 | 25 | **-$15.45** | RETIRE |
| 17CF EMA13/50 + OBV reclaim M1 NY | 40 | 8 | 16 | **-$9.78** | RETIRE |
| 17CG Darvas M5 | 4 | 3 | 3 | **+$0.46** | RETIRE — supply fail |

The Kumo/AO and EMA/OBV families both had sufficient activity but materially negative 30-second persistence under frozen P75 execution.

Darvas produced positive direct net, but only four trades over three days. It therefore fails the fixed activity gate and cannot be promoted or rescued by changing timeframe/defaults after observing the result.

## Decision

**RETIRE 17CE–17CG. NO SURVIVOR.**

Do not rescue through:
- parameter retuning;
- timeframe changes;
- session/side filtering;
- exit optimization;
- August;
- MQL5.

The result strengthens the existing map: simple trend-stack or cloud confirmation is insufficient by itself, while highly selective structural breakouts may show quality but often fail Miner supply requirements.

Result SHA-256:
`2f909cbe54d8b8c690154fe704625bc398e0356cb5e35d3b7b3fe7fc08f98e82`

## Next

`R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST`

Bias: event-defined continuation after compression/pullback/reclaim with native supply, rather than another generic oscillator or rare multi-leg pattern.

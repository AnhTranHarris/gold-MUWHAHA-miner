# DELTA R037 — Squeeze-Range Breakout Retest — Checkpoint 17CM–17CN

**Status:** COMPLETE / NO STAGE-A SURVIVOR  
**Unit:** R037_SQUEEZE_RANGE_BREAKOUT_RETEST_STAGE_A_SCREEN_CHECKPOINT_17CM_17CN  
**Family:** R037-SRBRT-v1  
**Parent:** R037_XAUUSD_INSIDE_BAR_CONTINUATION_STAGE_A_SCREEN_CHECKPOINT_17CK_17CL  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Why this family was admitted

The completed R037 corpus repeatedly showed that high-information entry candidates require both native supply and a durable event anchor. The BB/Keltner volatility-compression release was one of the strongest near-positive clues: 27 direct entries, 20 official wins, and +$0.71 under frozen 30-second execution.

Public reconstructible logic also supports a breakout lifecycle in which the compression range is retained after release and the first retest/hold is used as confirmation instead of chasing the initial breakout. This checkpoint therefore tested that lifecycle as a new family without changing the previously observed VCE thresholds.

## Frozen preregistration

Preregistration commit:
`038d1750aaf510cd2929f7301f46af2a994d9d90`

Producer:
`research/delta/experiments/delta_r037_squeeze_range_breakout_retest_17cm_17cn.py`

Producer commit:
`17958c71ddb2133d993fa9a3a8a08177bb2d3248`

Producer blob:
`599cac3a5fdfa302695f3af13e88a25c25932a2b`

Producer SHA-256:
`b462fb6e12248d5740f3bff332f4ec8358ef44bde97ea059c08e51581ed033fe`

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**.

The producer used the committed crash-contained DELTA runner with a 120-second wall-clock boundary, exact Git-blob verification, isolated Numba cache, process-group cleanup and atomic JSON replacement.

## Source grammar

Both lanes used:
- M5 Bollinger Bands 20 / 2.0 inside Keltner Channel EMA20 ± 1.5×ATR20 as compression;
- the full contiguous squeeze-segment high/low as the locked range;
- first later completed M5 close outside the locked range as breakout;
- no entry on the breakout itself;
- first causal retest and hold of the broken locked-range edge;
- invalidation if a new M5 squeeze began before retest or price completed beyond the opposite locked edge.

The only preregistered difference was confirmation timeframe:
- **17CM:** completed M5 retest/hold.
- **17CN:** completed M1 retest/hold.

No post-result threshold, side, session, timeframe or exit rescue was permitted.

## Results

Breakout supply was healthy: **69 squeeze segments, 69 locked ranges, 56 breakouts** (32 bullish / 24 bearish).

| Lane | Trades | Days | Wins | Direct net | Result |
|---|---:|---:|---:|---:|---|
| 17CM M5 retest | 38 | 11 | 18 | **-$6.11** | FAIL economics |
| 17CN M1 retest | 43 | 11 | 22 | **-$6.36** | FAIL economics |

The source grammar therefore solved supply but not executable persistence.

The important negative finding is that the earlier **raw BB/KC release clue remained materially stronger** than waiting for the locked-range retest: the raw release produced 27 trades / 20 wins / +$0.71, while both delayed-retreat lanes were negative.

## Decision

**RETIRE R037-SRBRT-v1 unchanged.**

Do not rescue through:
- threshold adjustment;
- another confirmation timeframe;
- side or session filtering;
- exit optimization;
- August;
- MQL5.

Official result SHA-256:
`caf430d9dce0ff28584f67d0568ec24b9921fd95f25c5227bc6f1aff8fd86939`

Workbook readback:
`69 R037 Research Harvest!A274:I281`

## Next

`R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST`

Admission bias: evidence-led structures with demonstrated native XAUUSD supply and near-neutral/positive direct persistence. Prefer candidates that attack the quality/supply frontier already visible in the R037 harvest rather than another generic indicator family.

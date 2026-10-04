# DELTA R037 — One-Sided Spread-Shock Mean Reversion — Checkpoint 17AU

**Status:** COMPLETE / NO EXECUTABLE SURVIVOR / RETIRED  
**Unit:** R037_ONE_SIDED_SPREAD_SHOCK_MEAN_REVERSION_STAGE_A_SCREEN  
**Parent:** R037_QIM_STAGE_A_SCREEN_CHECKPOINT_17AT  
**Surface:** native Dukascopy BBO signal / Coinexx-like P75 execution  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Result

The source-grounded hypothesis was that an ask-only outward quote shock could identify a SELL mean-reversion event, and a bid-only outward quote shock a BUY event. Three preregistered timing semantics were tested without shock-size thresholds or parameter fitting: immediate fade, first-narrow confirmation, and full pre-shock-spread restoration.

The family is far too dense and economically invalid:

| Profile | Signals | Trades | Wins | Net |
|---|---:|---:|---:|---:|
| C01 immediate fade | 471,000 | 93,374 | 42,204 | **-$19,895.30** |
| C02 first narrow | 155,047 | 46,472 | 21,237 | **-$9,510.14** |
| C03 full restore | 84,152 | 34,876 | 16,017 | **-$7,067.97** |

There were 471,000 shock episodes in Stage-A. Median peak native-spread expansion was 40 raw units. First narrowing occurred quickly when it occurred: median 101 ms, p90 554 ms. That microstructural mean reversion is real as a quote-state phenomenon, but it is too common and too small to overcome the independent P75 executable spread and frozen 30-second lifecycle.

## Integrity

- prereg commit: `1c2896ff2d5602282c25c88a62d9e528eb69d15b`
- producer commit: `7a66e2134b59959d6b75b7f5806ea9006dfc45c9`
- producer blob: `31b41ab74e5779476254a8f6e7e1e606f1ed9181`
- producer SHA-256: `036deca4eb3876c39f03f5ec5a8073927874a47184fa57dbb1ec778690c5cf9e`
- official result SHA-256: `921e15b1d1b49e4c0dccc3e91820f9fbe934ac1e3ac921e7bafecb13b9f078af`
- canonical January SHA and 4,205,709 Stage-A ticks verified
- exact local Git blob matched committed producer before compute
- Python compilation passed
- official compute completed under 120-second hard process timeout
- atomic result output

## Decision

**RETIRE_OSSMR_STAGE_A_NO_EXECUTABLE_SURVIVOR.**

Do not rescue with shock-size, ATR, percentile, session, side, weekday, QIM/OFI or exit filters.

The next source family must be sparse **by its native event definition**, not made sparse after observing Stage-A.

**Next:** `R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`

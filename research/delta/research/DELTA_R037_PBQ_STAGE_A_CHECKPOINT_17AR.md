# DELTA R037 — Microtrend Pullback Quality Stage-A Screen — Checkpoint 17AR

**Status:** COMPLETE / NO SURVIVOR / FAMILY RETIRED  
**Unit:** R037_MICROTREND_PULLBACK_QUALITY_STAGE_A_SCREEN  
**Parent:** R037_ITDC_STAGE_A_SCREEN_CHECKPOINT_17AQ  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Purpose

Test the preregistered MQL5 Market Microstructure Part 8/Part 9 microtrend + pullback-quality family on canonical January Stage-A without parameter rescue, session/side filters, exit tuning, or post-result threshold selection.

## Crash-safe execution

- prereg commit: `50970048c0c6bcc448f9f95b8c02daaff26bd581`
- producer commit: `924c3a12a1969e3f986558c4dd69855e99e6f453`
- producer blob: `f6e86f2aab111599f03eae56830e5217c56f93e1`
- local reconstructed Git blob matched the committed producer exactly before compute
- canonical January SHA: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- Stage-A ticks: **4,205,709**
- official compute bounded by hard 120-second process timeout
- result written atomically
- result SHA-256: `843947f7fdd0040e9c761efa4035b621697d423de36b3d66db1ebb56a4734225`

## Results

| Profile | Trades | Official wins | Gross profit | Gross loss | Net |
|---|---:|---:|---:|---:|---:|
| C01_BINARY_HEALTHY | 1,644 | 751 | +$165.95 | -$507.88 | **-$341.93** |
| C02_PERSISTENT_HEALTHY | 570 | 259 | +$49.44 | -$176.46 | **-$127.02** |
| C03_PERSISTENT_SHALLOW | 4,998 | 2,333 | +$517.24 | -$1,489.08 | **-$971.84** |

All profiles passed supply but failed the economic gate. No ordinary or strong survivor exists.

## Decision

**RETIRE_PBQ_STAGE_A_NO_SURVIVOR.**

Do not rescue with:
- EMA/ATR/threshold/lookback sweeps
- composite-score posthoc thresholding
- session / weekday / side filters
- exit tuning
- August data
- MQL5 translation

The family is information-redundant with recent trend/pullback failures and does not justify more compute.

## Next

`R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`

Priority is a genuinely different information source, not another cosmetic trend/pullback variation.

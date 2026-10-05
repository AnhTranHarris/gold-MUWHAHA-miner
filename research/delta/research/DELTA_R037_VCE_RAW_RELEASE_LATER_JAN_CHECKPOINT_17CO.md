# DELTA R037 — VCE Raw Release Independent Later-January Validation — Checkpoint 17CO

**Status:** COMPLETE / INDEPENDENT VALIDATION FAIL  
**Candidate:** R037-VCE-C03_BBKC_RELEASE  
**Parent:** R037_SQUEEZE_RANGE_BREAKOUT_RETEST_STAGE_A_SCREEN_CHECKPOINT_17CM_17CN  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Purpose

This was a high-information validation of one of the strongest near-positive Stage-A clues in the completed R037 corpus. The original BB/Keltner release produced **27 trades / 20 official wins / +$0.71**. No threshold, session, side, momentum, queue-imbalance, retest or exit adjustment was admitted.

The question was simple: does the exact raw release grammar survive an independent later-January holdout?

## Frozen grammar

- M5.
- Prior completed bar: Bollinger Bands 20/2.0 fully inside Keltner Channel EMA20 ±1.5×ATR20.
- Current completed bar: squeeze releases and close is beyond the current Keltner channel.
- Entry at the first executable P75 tick after the completed release bar.
- Spread <=25 points.
- Frozen 0.01-lot / $0.30 stop / +$0.10 trail arm / $0.03 trail / 30-second max hold.
- No post-result rescue.

Preregistration commit:
`105243f7bede082a37012c85de75bb8f0f1c1c63`

Producer:
`research/delta/experiments/delta_r037_vce_raw_release_later_jan_17co.py`

Producer commit:
`cf4f07ad6064927200443ba1aa948c8e3817f2f2`

Producer blob:
`1914f7cd48f9bad10a853556cfe2c6fdad94d266`

Producer SHA-256:
`8d1ba5b5daf70ca7b915f224583c7b4eee2c30439709988506651abd6cf71b7d`

## Crash-safe validation gate

Before the holdout could be persisted, the producer had to reproduce the original Stage-A control exactly.

It did:

**27 trades / 11 days / 20 wins / +$0.71**

This eliminates implementation drift as an explanation for the holdout outcome.

The official process used the committed bounded runner, exact Git-blob verification and atomic result replacement. It completed normally under the 120-second wall-clock limit.

## Independent later-January result

Warmup:
2026-01-14 00:00 UTC onward, with no economic entries before the holdout.

Economic holdout:
2026-01-18 12:00 UTC through the final January tick.

Result:

- **28 trades**
- **11 distinct days**
- 18 long / 10 short
- **10 official wins**
- gross profit **+$3.97**
- gross loss **-$12.74**
- direct net **-$9.05**
- all 28 exits hit STOP under the frozen 30-second execution.

The fixed supply gates passed. The economics gate failed decisively.

Win concentration collapsed from **20/27 = 74.1%** in Stage-A to **10/28 = 35.7%** in the holdout.

## Decision

**RETIRE R037-VCE-C03_BBKC_RELEASE unchanged.**

Do not rescue with:
- QI025 or other queue-imbalance thresholds;
- momentum or EMA filters;
- session/side filtering;
- another retest interpretation;
- exit optimization;
- August;
- MQL5.

The preserved Stage-A +$0.71 result was not robust to an adjacent independent window.

Official result SHA-256:
`c6cf1b2360e0694d74683100bf04c8db867b559fb49ffd407b56173268181a39`

Workbook readback:
`69 R037 Research Harvest!A282:I288`

## Next

`R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST`

The next family must be independent of the now-retired VCE/compression-release branch and should have source-grounded native XAUUSD supply before compute.

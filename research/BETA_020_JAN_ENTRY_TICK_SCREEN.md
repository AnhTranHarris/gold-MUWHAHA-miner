# BETA020 — January Tick-Level Entry Discovery Screen (BETA018/BETA019)

**Status:** bounded exploratory RESEARCH ONLY; no breakthrough promotion, no new MQL5 or EA, no BETA baseline approval. **August 2026 SEALED.** Tested 2026-09-29 on independent `beta` lineage.

## Tick source and parity scope
- Original Dukascopy January XAUUSD Bid/Ask source `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz`; compressed SHA-256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`; 9,135,062 ordered original quote ticks, first 2026-01-01T23:00Z, last 2026-01-30T21:59Z.
- All 16 tick-built frame bucket identities counted for January. Independent Bid/Ask OHLC + tick-count aggregation agreed across all 16 time-bucket resolutions on January 2's 336,704 source ticks (17th layer is raw TICK). **This is NOT completion of the outstanding BETA005 full-month feature-cache-value certification.**
- Original Bid/Ask execution and $0.02 modeled fee for each 0.01-lot (one-ounce) trade; horizon labels use first actual quote at/after 3/5/15/30 seconds with stale-quote exclusion. Future labels never used by signal features. Source was read through gzip EOF; no generated tick series used.

## Cohort 1 — previous completed M1 range, one first crossing per M1
One frozen prior completed-minute boundary origin; every variant evaluated on same independent origin cohort. Prototype variants are simplified public-mechanism ablations, **not the full BETA019 production state machines**.

| Variant | Triggered entries | 5s after-cost precision | Correct 5s entries | Illustrative $100k account net |
|---|---:|---:|---:|---:|
| First break control | 24,160 | 11.844% | 2,767 | -$10,000.04 (floor) |
| Fast acceptance | 22,021 | 10.394% | 2,219 | -$10,000.36 (floor) |
| Retest/rebreak | 18,060 | 10.282% | 1,804 | -$10,000.02 (floor) |
| Sweep/reclaim | 19,652 | 10.414% | 1,979 | -$10,000.53 (floor) |
| Two-leg rebreak | 12,705 | 10.594% | 1,310 | -$9,262.05 |
| Compression + fast | 5,355 | 8.860% | 453 | -$3,770.17 |

All after-cost mean 5s entry markouts negative; first four scenario accounts reached the $90k static equity floor. Higher survival of the low-turnover variants is **not** counted as an edge because correct opportunities were lost and net stayed negative.

## Cohort 2 — right-confirmed M5 fractal structural break
A five-bar M5 pivot is visible only after its two right-hand M5 bars complete. Found 750 high and 782 low confirmed pivots; generated 3,681 first structural crossings. Deduplicated 235 overlapping same-quote candidate timestamps across tested families before the final report.

| Variant | Triggered entries | 5s after-cost precision | Correct 5s entries | Illustrative $100k account net |
|---|---:|---:|---:|---:|
| First structural crossing | 3,681 | 11.603% | 414 | -$2,591.20 |
| Completed M1 body acceptance | 1,120 | 15.335% | 167 | -$797.51 |
| First retest/rebreak | 2,951 | 11.220% | 322 | -$2,051.41 |
| Completed M1 wick sweep/reclaim | 1,536 | 10.865% | 162 | -$1,245.60 |
| Fast-or-retest dual | 3,222 | 11.611% | 364 | -$2,262.68 |
| <=$0.50 spread-gated dual | 224 | 16.667% | 36 | -$98.18 |

Completed-body acceptance improves precision by 3.732 percentage points but **loses 247 of 414 correct events**; the cost gate deletes even more true opportunities. The dual path retains about 88% of positives but barely improves precision.

## Scientific / governance caveats
- Same tick feed, preliminary January-discovery, not a pristine future holdout. No validation on February–July; no August access.
- 10 bounded QA assertion groups passed for source-prefix invariance (6,956 historical M1 events), no backdated M5 pivots, next-tick closed-candle signals, duplicate-timestamp removal, and fee/balance accounting.
- The $100k account figures are **illustrative only**: the actual BETA015 `PropRiskGuard` has not been invoked in this prototype; verified Coinexx broker-open flags, complete broker session/calendar mapping, stop/fill/slippage parity and point-in-time news calendar are not available. Model uses its fixed capital/lot, one position, $4k/$5k daily and $90k overall constraints with a quote-presence/NY-rollover proxy. **Do not call these policy-certified funded returns or MT5 results.**
- BETA018 frozen research HOLD/EXIT geometry used ($0.30 stop, $0.10 activation, $0.03 trailing gap, max 30s); no HOLD/EXIT tuning.
- No exact source-equivalent R09_BETA001 reproduction was performed in this new event cohort. Do not compare headline results against original Coinexx R9 MT5 or claim SYNTH parity.
- The script source and complete numeric JSON are separately generated in the associated ChatGPT research handoff. This Markdown is a concise durable research checkpoint, not a source-code implementation or approved strategy.

**Decision: NO PROMOTION.** BETA005's full materialized 17-layer cache parity remains the first incomplete certification unit. Next research is BETA015 exact policy guard + independently frozen event ledger, then separate within-structure quote-imbalance timing and true confirmed swing break/retest/CHoCH; evaluate accuracy **and absolute positives/retention**, not filter win rate in isolation. Only owner authorizes August and candidate MQL5.

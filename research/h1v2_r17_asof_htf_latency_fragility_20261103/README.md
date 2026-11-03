# R17 — Four-Month Source-Exact H1V2 Broker-Adaptive As-Of HTF Latency Research (2026-11-03)

**NONDEPLOYABLE EXPERIMENT — NOT AN ENTRY PREDICTOR, NOT COINEXX FULL-FOUR-MONTH CERTIFICATION.**

This directory is strictly additive research to the original Gold MUWHAHA Miner / XAUUSD H1V2 pipeline. The repository's original H1V2, R9 v2, R11, R12–R16 sources, model checkpoints and negative experiment receipts were **not modified**. R16 parent is pinned to `0bb5f28567680dc2ef92a9ea6ceb01a0aa6975fd`.

## Why this experiment is distinct

The source-exact R11 audit proved 246 exact R9 SYNTH-active hour quotas impossible under its own fixed 30-second strict-favorable-and-safe horizon and first-250ms Dukascopy admission contract. Later original R16 dynamic first-touch research increased hindsight quarter and hour capacity by changing the **actual modeled lifetime** and candidate timestamp universe, but at a frozen 100ms fill delay, its widened spread quote execution had 175,503 successful and 61,005 unsuccessful completed signals (74.2059465%, below the owner's >=80% criterion). R16 original source, results and full 140 delayed scenarios are immutable controls.

R17 asks whether strictly as-of multi-scale directional alignment, spread compression/EMA and 3-second Bid/Ask coherent motion explain this latency vulnerability, WITHOUT inventing a new look-ahead action side or silently relaxing risk. The original R16 future-selected entry timestamp and BUY/SELL side are **frozen** and *future informed*; ONLY gate observables are as-of at the candidate quote. Therefore this is a falsifiable **retrospective admission filter**, never a new real-time model. It is deliberately not a replacement for R16.

## Actual complete source population

Four original source Dukascopy months: 2026-01/02/06/07 with 9,135,062 / 7,538,339 / 8,201,406 / 7,415,841 quotes (32,290,648 total), exact previously verified source SHA. All 11,520 UTC 15-minute quarters, 2,880 UTC hours, original R9 SYNTH UTC-clock-aligned volume reference and zero-reference periods retained.

Eight predeclared conditions applied to each of five original R16 lanes (BASE_250_1500, DENSE_1500, WIDE_REQUOTE_4000, BUDGETED_MULTI_REGIME, FULL_WIDE_DENSE_DIAGNOSTIC), 160 month×lane×gate experiments:

- ALL_FUTURE_SELECTED_CONTROL
- ORIGINAL_SPREAD_1500
- CURRENT_SPREAD_LE_300S_EMA
- SPREAD_RELIEF_080_AND_3S_FLOW
- HTF_15M_1H_SIDE_ALIGNED
- HTF_15M_1H_4H_SIDE_ALIGNED
- BROKER_ADAPTIVE_HTF_COST_GATE
- HTF_ALIGNED_AND_ORIGINAL_SPREAD

Past-only reference anchors: last actual observed quote with timestamp <= candidate timestamp minus 15m, 1h or 4h. Source prices are first observed paired Bid and Ask and original integer 0.001 USD units; no midpoint execution. Original as-of quote spread EMAs and 3s flow are inherited from exact frozen R16 source. Delayed action is filled at first actual source quote >= signal+100ms and subject to <=1000ms freshness and original source permitted executable spread; original +$0.10 net after nominal $0.02 fee, zero -$0.10 opening-liquidation adverse through full30, failed position 30s occupation, positive early first-observed TP release. Re-run one-position occupancy after *each* filter, not retained busy outcomes from an unfiltered route. A source-gap incomplete full target is censored, never labeled good.

## Falsification and evidence

Every R17 tested condition fails to jointly match original active 15m/hour source R9 quotas and original >=80% completion strict correctness at 100ms in all four months. Most naive 15m/1h/4h direction gates fail even to improve strict accuracy: on WIDE_REQUOTE_4000, unfiltered 74.21% and 1,943/7,521 active quarters jointly >=original count and >=80% strict; 15m+1h 73.47% and 787/7,521; 15m+1h+4h 73.61% and 500/7,521. Source spread-relief+3s-flow yields 68.53% and only 2/7,521 quarters.

No frozen model, independently selected BUY/SELL/WAIT, true Coinexx 4-month paired source quotes or actual account execution P&L was produced. July is historically exposed and not blind OOS. Do not promote any hindsight cardinality or filter precision to deployable alpha.

## Source, exact executable verification, complete no-summary artifacts

`src/r17_asof_htf_latency.py` — original full quote-ordinal, past-only anchor mechanism and 100ms independent filtered replay.
`tests/test_r17_asof.py` — five deterministic/adversarial tests (past-only anchors, later source mutation invariance, side/spread/flow fail-closed contracts).
`verify_r17_source_exact.py` — independent raw quote/source SHA, all source entry ordinals, 4×40 records, complete original quarter rows and selected delayed price/fill checks.
`build_r17_full_artifacts.py` — four atomic month archives, manifest/member hashes, full report and the 460,800 quarter×gate row preservation.
`FULL_UNABRIDGED_R17_FOUR_MONTH_SOURCE_REPORT_20261103.md` — exact complete original source report; original Drive source preserves same full 38,728 bytes. Do not replace with this README.

**Verified MT5_EXPAND parent folder:** https://drive.google.com/drive/folders/1vpHz_U-eVFyiC4Tf6YLgFlCK3HN3vP7L
**Original full R17 unabridged report:** https://drive.google.com/file/d/1HxVJR6e3wpGgnjEChHEhtyWELGfLMwTm/view
**R17 complete source/results ZIP:** https://drive.google.com/file/d/1Mrw_O2JYaw8-Wid22R7O-buzvSMxKouK/view
**All 460,800 quarter-level source rows:** https://drive.google.com/file/d/1IiMQ5YIbkx7RAeyGbLVkM2NqER9-t6VR/view
**All 160 complete month×lane×gate records:** https://drive.google.com/file/d/1hTbJH9Lpv2Cwe8CTncZ5pLvHsJ8eo-vT/view
**All SHA and immutable manifest:** https://drive.google.com/file/d/1pDsWTQG5rLYfdlviLz-n1NIOflY8sjz0/view
**Month ZIPs:** Jan https://drive.google.com/file/d/1wXW6fi5b3JnJk7unyEttBDliKjXz-QZK/view ; Feb https://drive.google.com/file/d/1fMXgHbp9SfR4ZA-vIrErwBL8x0SIZt44/view ; Jun https://drive.google.com/file/d/1MBObTZvwr_5PH5ovgYET0bcO7HJrurTj/view ; Jul https://drive.google.com/file/d/1WD7_0z80k_vO74Z8CNKDRd5AN8IXWl9l/view.
**Append-only source/execution recovery log:** https://docs.google.com/document/d/1iVv1tAmJlBWhNfXMcw2N50VEVIFrawMObGOzyfUGWmI/edit
**Original exact audit:** https://docs.google.com/document/d/1n8Zd37SH3k2mNYpCERHsGSeR5GL-vDNLDv780Bv5-Do/edit
**Original R16 source baseline:** https://github.com/AnhTranHarris/gold-MUWHAHA-miner/tree/carson/h1v2-r16-broker-adaptive-fullcalendar-20261103

Original full source ZIP member SHA/CRC, original raw quotes, and unit and independent tests were checked locally. MT5_EXPAND upload metadata was returned but original remote bytes have NOT been independently re-downloaded/re-hashed; do not claim otherwise.

## Next distinct scientific research (NOT already tested)

Use same-clock **Coinexx** January/February/June/July full actual paired bid/ask tick exports to compare actual spread and quote-arrival domains, not synthetic quota counts as substitutes. Design a **broker-relative spread-concession hazard + sequential WAIT value + latency/requote survival model** with all decision features strictly as-of and BUY/SELL calibrated independently, explicit full 15m/1h/4h feature context but no naive directional agreement admission. Train on purged chronological periods, freeze threshold and compare new matched broker heldout period and as-of one-position economic replay, actual dynamic R9 close/fees/costs/risk. No 80% validation by failing hours avoidance, no free widened spread, no broker-live authorization.


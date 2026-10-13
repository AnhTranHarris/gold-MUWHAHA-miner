# GRID0266 — Original Coinexx R9 REAL vs Dukascopy Bid/Ask compatibility, 2026-10-13

Research-only original market-quote comparison. Does not claim live Coinexx broker fill parity or a trading performance edge. Original V1 branch remains `delta-A-alpha` (no new branch), J0183 unchanged; August sealed.

## Actual original data sources

- [Owner R9 REAL/SYNTH six-part archive folder](https://drive.google.com/drive/folders/1CidEgLMNVfgBZg6UYLYqcanc0oqgt9Vj): 6+6 original split `csv.gz` pieces. REAL original compressed source 762,236,183 bytes; prior [original full source reconstruction research record](https://drive.google.com/file/d/1qWF6U_0F9gnKliuW8D7XXGYRKJNAI4zG/view) documents full source SHA256 `ad82ee99ba60f6c7dcc5b85654971fecb9f4a5047dc6f97aa97083b3c60a663c`, 56,608,185 rows, 149 UTC partitions, decompressed SHA256 `244e9fb2851de497a0a863584c34e634de3f1d79e77d0146556a8da1f2ee9d9c`. **Existing archival verification**, not re-run this turn.
- [R9 REAL ordered daily research folders](https://drive.google.com/drive/folders/1sArmKh3mTsH_8h69WNT92Vjsk4g0P-WJ), [31-column schema](https://drive.google.com/file/d/1IkIbuyiwc2C3BeONsqlfUULNenPwS0gd/view), [daily hashes/counts](https://drive.google.com/file/d/1hUH0X600m7V3Nz4gBdT2gw3wAClXnmQx/view).
- [2026-04-15 original Coinexx R9 REAL daily gzip](https://drive.google.com/file/d/1lQLFR9tizv0yRU426EfSu3s90uxO0F2O/view): 7,181,851 bytes, 365,469 raw original logger rows. Checked full-file SHA256 matches Drive manifest: `b2e4cac86bd0ce5255699b39d4ee1b43649deb25fd3d6608b9a297fa95f43441`.
- Local existing original Dukascopy `XAUUSD_DUKAS_2026_04_ticks.csv(3).gz`, pre-verified source monthly SHA256 `30375098f62aed6cabc32ec6b67c57c20baec9b6d9be1ce0a204e09806c1ec0f`; filtered original UTC day April 15 — 272,265 ordered Bid/Ask rows, no full-month re-export.
- Original user MT5 tester REAL XLSX verified Coinexx-Demo Build 6182, XAUUSD M1 Jan–Jul, deposit USD 100,000, leverage 1:500, History Quality 99% real ticks, 56,608,185 tick observations, 236,647 completed trades, net loss $50,285.28. This is **tester run configuration**, not proof of live or present Coinexx contract/margin.

## Direct 2026-04-15 as-of comparison

Coinexx REAL: **365,469 ordered rows**, zero reversed timestamps, zero reversed Bid/Ask, zero mismatch of original text timestamp to UTC milliseconds, zero mismatch of logged 0.01 USD spread points with quotes. Median spread **$0.20**; observed initial first minute spread **$1.92**, so never impose constant $0.20.

Dukascopy: **272,265 ordered rows**, zero reversed timestamps, zero reversed Bid/Ask. Median spread **$0.62**, p90 $0.79, p99 $1.264 for this source day. These are *independent provider* quotes, not Coinexx fills.

As-of last Dukascopy observation <= Coinexx quote timestamp (never interpolate future), freshness <=1,000ms: 294,188 matched pairs (80.496% of Coinexx ticks). Median as-of quote age 174 ms. Median Coinexx minus Dukascopy midpoint **+$7.6865/oz**, median absolute midpoint difference **$11.44/oz**, median differences vary greatly by hour and sign. This is not evidence of universal broker price offsets. **Never co-mingle raw price levels, replace one feed's bid/ask with the other, or assume a global spread or fixed clock shift.**

**R9 logger events:** one-day counts `ENTRY_BUY` 794, `ENTRY_SELL` 784, `REARM` 1,565, `TRAIL_MOVE` 1,993, `EXIT_MAX_HOLD` 28, `QUALITY_REJECT_BUY` 67,254, `QUALITY_REJECT_SELL` 64,893, `MINUTE_START` 1,373, `NONE` 226,785. These are **EA logger event annotations, NOT MT5 DEAL_ADD transaction receipts**, and do not establish filled order count or broker cash.

## Implementation contract, fixed now

Actual active current repository code `research/delta_a_alpha/implementation/v1_grid_dual_feed_replay_0266.py`: separate strict parser for full Coinexx REAL/SYNTH 31-column logger and canonical Dukascopy five columns; integer 0.001 USD price quantization and original UTC millisecond chronology, duplicate ms kept in file order. 0.01 observed R9 point-price used solely to audit original logged `spread` arithmetic, **not** as verified symbol tick-size/contract specification. Original R9 event and gate flags remain metadata only. No August reads.

`FourSessionV1.bind_research_feed` provides a feed-locked current engine research replay gate before the first quote; no switching between Dukascopy/Coinexx or REAL/SYNTH in one portfolio; active current cumulative G0 router and separate hardened evidence port untouched. Session-tradability callback explicitly research/hypothetical; shadow fills never become verified deal credit. R9 historical spread, time and modeled execution costs remain feed-local.

**Limitations:** Only one original Coinexx daily file was replayed in this turn; all original Jan-Jul Coinexx days are located and previously reconstructed/validated but not rerun. Historical 2026 R9 REAL tester quotes do not certify *present* Coinexx live symbol `trade_contract_size`, freeze/stops level, account mode, dynamic commission, financing, or trade transaction ACKs. Symbol metadata/DEAL_ADD receipts still require real read-only MT5 evidence for EA build. Comparison numbers are not strategy profitability results.

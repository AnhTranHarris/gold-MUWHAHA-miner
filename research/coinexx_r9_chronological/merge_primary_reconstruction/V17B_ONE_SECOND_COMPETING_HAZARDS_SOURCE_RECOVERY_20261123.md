# R9 HybridGate V17B — exact executable entry-only research checkpoint, 2026-11-23

**Research status: volume PASSED, historical entry alignment FAILED; no trading EA or execution profitability claims. Original R9 v1.90 and all frozen datasets unchanged.**

## Read actual sources — not this summary

**[V17B complete 28-file executable archive, MT5_EXPAND](https://drive.google.com/file/d/1CmrDlTKlO4WcCfb3wJebXaGaB_PPgs7L/view)**

ZIP exact SHA-256: `6bfe8cb1815680bb324df4cf6fb4137a68ddca0b9e29868ad3d7d105d9ddad34`, 3,153,555 bytes; 27 individual payload SHA-256 and ZIP CRC checks PASS. Contains **actual** original V14 C++ research parent, V16 causal market state core, new C++17/zlib 1-second event extractor, Python nine-month preparation/fit/model scoring/online source-only replay/QA code, frozen first/rearm LightGBM models, exact nine-month 287,770 candidate entry ledger, original V16 source-only entry stream, research MT5 read-only information probe, source hashes, and rejected threshold sweeps. The code's own [README_SOURCE_EXACT_V17.md](https://drive.google.com/file/d/1CmrDlTKlO4WcCfb3wJebXaGaB_PPgs7L/view) must be read within the ZIP. No raw Coinexx tick logs or frozen merged trade ledgers copied.

Canonical original MQL5: `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5`, immutable blob `7eecb5f1947017a01ce85b2520725de54749e523` on `carson/mt5-r9-hybrid-gate-certification`. Actual NEW merged Jan 2026 and Feb–Sep 2026 outcome-aligned ZIPs are the primary entry clock+direction training labels (272,352 historical legs). Original chronological Coinexx monthly gzip Jan–Sep tick sources 72,129,347 quotes, 9/9 SHA256 verified, are the only source for online inference features.

## Concrete V17B result

| Entry-only source-derived model | 9m signals | ±2s correct side | ±5s correct side | ±15s correct side | ±30s correct side |
|---|---:|---:|---:|---:|---:|
| Prior V16 event plus original V15F fallback | 277,582 | 51,894 | 101,108 | 146,142 | 178,851 |
| **New V17B one-second rank-flexible competing hazards + V16 fallback** | **287,770** | **53,384** | **102,681** | **148,895** | **182,699** |

The V17B first/rearm hazard models were fitted on bounded month-stratified **all-nine-month in-sample** observations; 1-second source-timed extractor processed 14,796,838 candidate market-state snapshots (not merged target event snapshots). All 9/9 months satisfy >=90% and <=110% of frozen monthly entry count (actual 103.9%–108.4%); same-side ±5s historical coverage is only **37.70%** of 272,352, thus target-aligned entry reconstruction **NOT ACHIEVED**.

9/9 source gzip fingerprints reconciled. January 1.2m-quote source-prefix 252,673 observations byte-identical against full quote replay. The **independent online source-only replay** did not access any merged ledger target records, generated 287,770 exact fixed-policy rows; SHA256 of its CSV `68c6564be1e8b6dff0d1a4c0556007d1ca28c6f9f37a9b8dce9c9a9f23d0e36a`. Separate QA reads the merge only to count one-to-one same-direction matches. Event hazards gained 1,573 ±5s matches versus V16 but relied on prior V16 fallback for 254,547 of 287,770 signals; **not a breakthrough**.

## Major source-data observation (independent advanced indicators)

January's first 400,000 original Coinexx rows have last=0, volume=0, volume_real=0. The quote-only stream carries no recorded MQL5 market book or actual matched-trade tape. Higher-order quote indicators (bipower jump statistic, variance ratio, quote-event imbalance proxies, quote duration CV, direction change, CUSUM, wavelet transforms) may enrich functional encoding but **do not add physically independent traded volume or book depth**.

**Genuinely independent advanced inputs** must be historically synchronized and recorded: real broker Depth of Market via MarketBookGet/OnBookEvent if provider supports it; COMEX gold futures executed trades and MBO/L2 depth; publication-time-aligned macro release surprises; independently timestamped dollar/rates/futures cross-asset updates. **NONE of these independent series is contained in the current merged/Coinexx TickLogger source.** No fake historical DOM or cumulative dollar delta is permitted. The kit includes a read-only MQL5 live capability probe (not compiled or executed in MetaEditor).

## Next actionable design investigation

The V16 rank role windows (first 0–14s, second 15–42s) conflict with original entries (59,686 first after second14; 11,347 second before 15; 12,052 second after 42). V17B permits first/rearm decisions throughout the minute; a V17 source-only fallback gating/WAI T policy screen was also performed and rejected where it reduced ±5s alignment. Next solve the missing **economic information and source-observed entry event** problem: evaluate independently recorded DOM/GC tradeflow and lead/lag against original merged historical entry directions if such historical data exists; never assume live probe gives January–September history. Preserve R9 minute-cycle/S1 architecture. No holding/exits/real account replay or native MT5 certification yet.

**Rollback:** this branch adds only the source checkpoint; canonical source remains immutable and full executable V17B is recoverable from MT5_EXPAND archive.

# R9 v2 high-volume UNTRAINED entry baseline — complete source-exact 2026 Jan/Feb/Jun/Jul

**Purpose:** Preserve the full native-month historical evidence, before Bayesian/NP fitting or optimization. Both brokers separately. This is a verified copy/independent revalidation of complete chronological runs performed in the preceding checkpoint; it is **not** a claim that 64.5m ticks were recalculated in this checkpoint. No sampling, estimation, or scaling of monthly results.

**Version boundary:** The high-volume event-stream *research specialist lane* is NOT a fitted Bayesian/Neyman–Pearson classifier, though it uses the same source-v2 rolling clocks, 250 ms event evaluation and unchanged R9-style lifecycle assumptions. The freeze is the GitHub branch `carson/r9-v2-high-volume-event-stream-repair-20261101`. Full code, not any summary, is packaged in every broker/month checkpoint. No MQL5 compile, no broker fill simulation, no live deployment.

**Contract:** Every broker/month must execute at least 85% of the identical calendar month's R9 SYNTH completed trades; BUY/SELL proposals are not counted. Trade count is a constraint, not a permission to lose money. Results fail the profitability criterion in all eight cases.

**Cost and risk:** 0.01 lot XAUUSD (price P&L in dollar-like units under an assumed 100-ounce standard lot); fixed $0.02 cost each completed trade; executable bid/ask reference marks and no slippage, stop-level, margin/capital limits or liquidity impact. These results are idealized research paths, NOT deployable account P&L. The $0.02 fee is NOT verified as the actual Coinexx broker commission. An undercapitalized EA could not sustain these modeled losses.

**Data:** Full original monthly Coinexx/Dukascopy tick files are reused by SHA-256. They are not duplicated in each checkpoint. Source file hashes are explicitly embedded. The R9 SYNTH reference month counts came from the original seven-month historical SYNTH teacher extract; SYNTH does not enter runtime decisions.

**Independent verification:** Each saved ledger was read end-to-end; closing price, direction, fixed fee, realized P&L, time order, concurrency, counts, full tick input checksum, original source blob and 85% volume gate were checked. No missing months.

**Monthly scores**

| Feed | Month | R9 SYNTH | V2 completed | Volume floor | Win% | PF | Mean net/trade | Net USD |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| coinexx | 2026-01 | 27,980 | 414,938 | 23,783 | 41.685 | 0.3551 | -0.26570 | -110,247.14 |
| coinexx | 2026-02 | 33,523 | 477,916 | 28,495 | 41.289 | 0.4502 | -0.23278 | -111,247.03 |
| coinexx | 2026-06 | 31,801 | 387,283 | 27,031 | 43.206 | 0.3323 | -0.22019 | -85,277.59 |
| coinexx | 2026-07 | 24,382 | 312,856 | 20,725 | 42.883 | 0.2962 | -0.21588 | -67,539.02 |
| dukascopy | 2026-01 | 27,980 | 238,644 | 23,783 | 24.317 | 0.0857 | -0.79909 | -190,697.44 |
| dukascopy | 2026-02 | 33,523 | 236,293 | 28,495 | 22.706 | 0.0903 | -0.98574 | -232,923.60 |
| dukascopy | 2026-06 | 31,801 | 235,139 | 27,031 | 26.430 | 0.0934 | -0.65620 | -154,297.77 |
| dukascopy | 2026-07 | 24,382 | 177,943 | 20,725 | 21.460 | 0.0628 | -0.70856 | -126,083.79 |

**Verdict:** Trade throughput succeeds in all eight source-months, but economic behavior is unacceptable. This is a pretraining baseline only. Both the original strict BNP/NP path and the amended throughput lane remain distinct, preserved, and NOT promoted.

## Durable Google Drive exact-binary checkpoints

### COINEXX

- 2026-01: [R9_V2_FULLMONTH_COINEXX_2026_01_EXACT.zip](https://drive.google.com/file/d/1H-gXk65lGq1vYYZZ0syPTD9gUEfuLCOM/view) · 760c44f8a12c4be0fca969aaffdf1771270e0fd68335c55d03126bdda90cf3ab · 414,938 trades · $-110,247.14 modeled net.
- 2026-02: [R9_V2_FULLMONTH_COINEXX_2026_02_EXACT.zip](https://drive.google.com/file/d/1nCf6uL6flSDtAzW6viyAaMYacxGnLnMF/view) · 9f249a28c05149534cd31bb9924705d63faecd03cbe967239fb1dc0d5cfca6ba · 477,916 trades · $-111,247.03 modeled net.
- 2026-06: [R9_V2_FULLMONTH_COINEXX_2026_06_EXACT.zip](https://drive.google.com/file/d/1eHonseZjVg-S5otCW8lDpv-8zgypxUI4/view) · 8045544bdf640ae127bbbe621d128c49be19ebed55dc3796919254dc72f3d9f2 · 387,283 trades · $-85,277.59 modeled net.
- 2026-07: [R9_V2_FULLMONTH_COINEXX_2026_07_EXACT.zip](https://drive.google.com/file/d/1I5UZdpVOD06-IdY36Mnl3EWXQ1L-EhH0/view) · 462a50ec56475a6d236d5287fc5e87d0e98b8732ecd92e40ceb4a7067d5fefb7 · 312,856 trades · $-67,539.02 modeled net.
### DUKASCOPY

- 2026-01: [R9_V2_FULLMONTH_DUKASCOPY_2026_01_EXACT.zip](https://drive.google.com/file/d/17fQThQQtguqX15HNv3OGCt49saI3VTs7/view) · ef55db8fbd9e65a0c5d67c6bd730c4ea8b1d92590d5b4ee70091e479ecad5bd4 · 238,644 trades · $-190,697.44 modeled net.
- 2026-02: [R9_V2_FULLMONTH_DUKASCOPY_2026_02_EXACT.zip](https://drive.google.com/file/d/1HVahgCQmbOWsIy5tLRFvqXExAaWWePuL/view) · b5744797245e6bec6aa99612a685212028fbb031b0d4ff43b653b6b58a5c00ce · 236,293 trades · $-232,923.60 modeled net.
- 2026-06: [R9_V2_FULLMONTH_DUKASCOPY_2026_06_EXACT.zip](https://drive.google.com/file/d/1LRc8H7VGShSecdnFuFgKb6uvIxX2XC-A/view) · 23a84a821dc09e5af78df661ef31c2e41c94f7de3321b5e98959fb51e38095ea · 235,139 trades · $-154,297.77 modeled net.
- 2026-07: [R9_V2_FULLMONTH_DUKASCOPY_2026_07_EXACT.zip](https://drive.google.com/file/d/1gHxihyyi5E2HzOrO0lo5CuqcVXRqXxG0/view) · 40ed7fe84deaefc5fa8513ef2725c9ffe694ec05d7b9fd4b8d74c868ec0ceac0 · 177,943 trades · $-126,083.79 modeled net.

The eight checkpoint ZIPs contain the actual complete compressed ledgers and full v2/repair source; the Google Doc/README is a navigation aid, not a substitute for those files.

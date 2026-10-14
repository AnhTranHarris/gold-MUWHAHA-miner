# New Coinexx R9 $100-source reference — Jan-only extracted benchmark (2026-10-14)
**Owner-provided authoritative source folder:** https://drive.google.com/drive/folders/1S0erLKfFpqQUVHHIHDql72PgsH6vQrMF?usp=drive_link
**Research scope:** January 2026 only on delta-A-alpha; previous R9 SYNTH comparator remains archived; no full V1 rewrite, no J0183 advancement, no trading deployment.

## Original user designation
> Carson, I have made severval mt5 reports, and ticklogger from the coinexx mt5 tester for R9 ... all these reaports have a starting captial of 100, and severval timeframe, of one minute, 5 minute, onr hour, etc, etc, etc. These files will be the new r9 Performance, and tick-level trade per trade performance

## Original unchanged source identities / SHA-256
- M1 HybridGate `MT5_100__M1_GoldMuwahahaMiner_R9_HybridGate.xlsx`; [original](https://drive.google.com/file/d/1jASxs5gn3e1rzwGxlE-178aN07_5ksHE/view), SHA256 `f9315c35bde962135785a0fb8fd268251086e9bebe27f5789757c69cfb38819d`. **Exact-source January Deals extraction completed.**
- M5 HybridGate `MT5_100__M5_GoldMuwahahaMiner_R9_HybridGate.xlsx`; [original](https://drive.google.com/file/d/1Fq5eku142DxoRpvBtqddR2xgbhOz4h_T/view), SHA256 `3237dfe2ebec41c0cf0699dfa65dcff1020f94869ed099b5e109b7377459face`.
- H1 HybridGate `MT5_100__H1_GoldMuwahahaMiner_R9_HybridGate.xlsx`; [original](https://drive.google.com/file/d/1nTbW7Y-bvYQO2IDHjQmLcEiFSHO5AET5/view), SHA256 `76f478220a910a1fbc1a0fff3c0d9141617d109a25c6a9075a6806883f07adfd`.
- M1 TickLogger `MT5_100_M1_GoldMuwahahaMiner_R9_TickLogger.xlsx`; [original](https://drive.google.com/file/d/1d6V3fHltXl7l2V8Wlu1BD-ubb78Qypnn/view), SHA256 `2590b6d2b254d97a1b5a516be263bd64f4e81d92277b7114dbddefe1b96d55c2`, input `InpRunLabel=SYNTH`, `InpLogEveryTick=true`. **The workbook is the Strategy Tester report, not confirmed tick-by-tick CSV.**
- Native MT5 tester file `GoldMuwahahaMiner_R9_TickLogger.XAUUSD.M1.20260101_20260930.0.8FCE35016BF60C001E3583010AF9D1F4.tst`; [original](https://drive.google.com/file/d/1flmMwK4umM7v5tLAr1_zQb0REurW-bn_/view), 303,581,440 bytes. Unable to retrieve raw via connected Drive due to current 268,435,456-byte download ceiling; native content structure/checksum NOT VERIFIED.

## Inspectable report facts
All four .xlsx Strategy Tester reports: **Coinexx-Demo Build 6231, USD, XAUUSD, $100 deposit, 1:500 leverage, 0.01 lot, original R9 M5 ATR(14), Jan1–Sep30 date interval**. They report the same aggregate 272,352 trades, +$360,693.05 net, gross profit +$381,418.88, gross loss −$20,725.83, PF18.403069, 86.72% winning, 69,609,920 tester ticks, notwithstanding different chart TF/bar counts. Treat as distinct report SOURCE FILES but **DO NOT COUNT AS FOUR INDEPENDENT PERFORMANCE RUNS** unless event-level identity is independently proven. Source says History Quality 100%; actual `Every tick` vs `Every tick based on real ticks` mode is not established by headers alone.

## New exact January 2026 benchmark, sourced from M1 HybridGate Deals
27,980 completed unique in/out cycles, net realized +$41,520.82, 24,368 profitable closes (87.0908%), gross winning +$43,348.69, gross losing −$1,827.87, PF23.71541, recorded total commission −$559.60 already incorporated in gross winning/loss accounting, no swaps. $100 initial balance plus +$41,520.82 net = $41,620.82 last reported January close cash. Source-native trade timestamp resolution is seconds. **21/21 active tester report date buckets positive and 10/31 zero-close dates.** All 27,980 trade price/commission/cash cycles paired, zero orphan/overlap/mismatch, exact balance identity. Closed-balance drawdown $3.40 computed from deal closes; do not claim floating equity DD from that statistic.
January ISO-week close-date net/trades:
- 2026-W01: +$1,027.95 / 1,083
- 2026-W02: +$5,332.33 / 5,828
- 2026-W03: +$5,817.38 / 6,095
- 2026-W04: +$7,692.42 / 6,587
- 2026-W05: +$21,650.74 / 8,387
These sum to 27,980 trades and $41,520.82. Period buckets use **tester report timestamps**, not independently established Coinexx-vs-Dukascopy UTC time parity. Future comparison requires explicit broker clock alignment.

**Crucial:** These January figures are NUMERICALLY IDENTICAL to the older recorded R9 SYNTH January reference. The new file gives us a first-party preserved report plus 27,980 exact tester deal cycles, but not an independently confirmed new profitable edge.

## Original source-preserving derived reference (same owner Drive folder)
- [Complete source-linked January 27,980-trade CSV+hourly/daily/weekly QA+deterministic extractor ZIP](https://drive.google.com/file/d/1fEaAqOkA2jg3aGiTxDduQh7hCHhQl3Yl/view) SHA256 `16753f61feb320d45ed8c769b276407b5fc83c057acde3a04c62bc9fb5dafdc4`, size 939,342 bytes, uploaded/readback verified.
- [Full source/QC manifest](https://drive.google.com/file/d/1wMt3SZjPiTi-KGIizrmVNQs5jRgrg8Pa/view), uploaded/readback verified.

This is an additive SOURCE CUSTODY / PERFORMANCE BENCHMARK registration: older immutable reports never deleted, no candidate promoted, original R9 OVERFIT hindsight labels still separate from MT5 SYNTH report and original Dukascopy causal replay, the sealed August Dukascopy data remains sealed, and scientific state J0183 is unchanged.

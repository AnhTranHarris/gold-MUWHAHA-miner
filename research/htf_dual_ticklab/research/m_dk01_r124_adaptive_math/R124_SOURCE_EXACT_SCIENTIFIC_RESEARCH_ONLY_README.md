# R124 — Adaptive 10-clock technical mathematics / four training cycles / reciprocal broker holdout
**2026-10-29; UNAPPROVED research only. Not ready for MT5 demo or live vetoes.**
Original source F401 R00-054 FILTER08; original M-DK-01 OPEN; 21/39 owner historical research-stage acceptances unchanged, G01–G09 OPEN.

## Original engine and data dependency
Reuse existing source-lock and *unchanged* dual Python Coinexx+Dukascopy tick replays: pinned infrastructure ca4b58aec597174b6f6d18ab2f36cba6836e4f4c, R120 250/500ms+multi-session and M1/M5/M15/H1 as-of law; R121/R122 original source reader and original F395 event masks. Approved 8 Jan/Feb/June/July source CSV.GZ gzip SHA checked at feature extraction: 2,574,251 fixed t0 signals (1,208,071 correct; 1,366,180 incorrect/neutral). Coinexx UTC -120min Jan/Feb, -180min Jun/Jul; Dukascopy UTC unchanged.

## New high-information feature family
Original full native tick-derived 10 clock observed-only *completed* OHLC 250ms/500ms/1s/5s/15s/30s/M1/M5/M15/H1. Never make up empty bars; t_quote<t0 and completed bucket strictly older than current decision bucket. 180D model input = 16 per-clock causal advanced math channels (SMA ATR13/34 true range, EMA13/37/89, SMA17/55, Bollinger23/47 squeeze+z, preceding observed completed-bar Fib61 rank/confluence, KAMA13 ER adaptive average, fixed-gain alpha-beta Kalman-style innovation, confirmed reversal greater than 1.1ATR, ATR-normalized move), +14 nonlinear clock interaction and original side, +6 UTC session covariates. Not a rebuild of replay or raw event engine. **Custom Python mathematical variants are not yet proven equivalent to MT5 native iATR/iMA/iBands/iAMA; G07 remains OPEN.**

## Independent eight-cell empirical results (all eight sums include own historical FIT/CAL contaminated portions, diagnostic ONLY)
| Cycle | FIT/CAL | Wrong veto | Good veto | Chronological later-month wrong/good |
|---|---|---:|---:|---:|
| C1 | Jan early FIT / Jan late CAL | 18,611 | 6,841 | Feb+June+July 5,208 /3,263 |
| C2 | Jan+early Feb FIT / later Feb CAL | 18,728 | 5,896 | June+July 1,028 /511 |
| C3 | Jan+Feb+early June FIT / later June CAL | 32,875 | 11,887 | July 3,081 /1,422 |
| C4 | **Jan/Feb/June/July sampled FIT across both brokers** | **NOT SCORED** | **NOT SCORED** | Freeze model for future truly unseen month; 321,784 sampled rows |

**C5 reciprocal broker-held-out frozen transfer:** one broker Jan+early Feb FIT and later Feb CAL, score opposite broker all Jan/Feb/June/July; reverse. Original eight independent cells **16,573 wrong veto / 8,399 correct lost**; June/July chronologically later **1,578 /927**. This is broker-held-out but ALL four target months previously historically project exposed, hence NOT virgin blind forward. C1–C4 train across both brokers, not broker-blind.

C1–C3 24 exact original event masks and C5 eight heldout full masks independently SHA/archive recounted against unmodified original F395 t0/index/side/truth. **3/3 synthetic ten-clock causality tests PASS**; **4/4 Jan real-source exact native-prefix tests PASS** on both brokers. July-only frozen 3-cycle vote: 2-of-3 559 wrong/252 good, 3-of-3 61/39. No original per-session G05 4,178 quota full rerun, native MQL5 G07, future G08 or account fill/equity G09.

## Portable binary and authoritative source receipt
Local complete 63-member ZIP `XAUUSD_F401_R124_ADAPTIVE_INDICATORS_FOUR_CYCLES_BROKERBLIND_UNAPPROVED_20261029.zip`, **81,890,905 bytes**, SHA256 `88f0ccd1a78f51aa2fed5532730e557ce2f5d62bee32afafa75031d76574f287`; 63 ZIP CRC and 62 member hashes PASS. Includes original source adapters, executable feature/training/heldout/audit Python, four chronological multi-source model weights, 2 broker-heldout model weights, 32 exact-event masks, JSON original recount, extensive negative evidence and 9KB original complete scientific report. Does NOT duplicate immutable raw source gzip or ~1.8GB regenerable features. **Cloud ZIP binary MT5_EXPAND /01 upload not verified; this GitHub README is not a substitute for executable source.** Local user artifact provided by ChatGPT.

## Scientific decision
No variant gets near **>400,000 wrong veto** and **<10,000 good lost** (required >40:1). R124 failed tested configurations, not all adaptive quant math. Original same-month teacher and F395 +15s shadow remain hindsight only, NEVER t0 live filter. Park current C1–C5, preserve negatives. Future work require different information-source mechanism (actual causal sequential regime state, correct rescue and cross-broker transfer) and untampered prospective month; do not brute-force close EMA/SMA spans or self-approve a checklist objective. PRIMARY Drive READONLY; MT5_EXPAND /02 owner-approved untouched. 

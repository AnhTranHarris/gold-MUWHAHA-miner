# F340 Coinexx August 2026 — approved historical research's frozen-source, out-of-training-month classifier diagnostic

**August 2026 Coinexx REAL broker bid/ask ticklogger** approved source-only, original pinned 58,362,261-byte `XAUUSD_MT5_BROKER_2026_08_ticks_ALL.csv.gz` SHA256 `8e337d18377c318de17ceb72d46bbfc976a29cef4571dfa3457d3ac7fc0e1c17`, registered in original source_registry at locked v0.3 replay HEAD `ca4b58aec597174b6f6d18ab2f36cba6836e4f4c`. No re-built tick replay. Source first quote 2026-08-02 22:00:01.451 UTC, last 2026-08-31 20:59:55.098 UTC; raw 7,468,061 quotes. Broker wallclock converted exactly once −180 min to UTC.

## Frozen source-native pipeline

- Original exact 2026 Jan-trained R00-054 `lgb_oracle_weighted` direction ML model + source-original Feb frozen thresholds; exact reference Python source `build_native_features.py` 43 original feature columns and independent expert states, entry frozen original `models_coinexx_jan_only.joblib` SHA256 `e4a488d1d8bbc373d2952f7f6053c39f40dba6db0b51c21632d80ab5848a7a39`; no August refit. First observed native quote per populated UTC 5s bucket **EXTENDED FROM AUTHOR-RECORDED March–May method** (August itself does NOT contain archived R00-040 ancestor IDs).
- **Frozen implementation-side parity reference:** same original model applied to original May native feature+expert archived records reproduces **all 345,324 May original event BUY/SELL decisions exactly**; zero side mismatch. This validates original side implementation before moving out-of-fit into August without changing entry-direction model.
- Frozen F323 124D as-of t0 source/HTF+32s-matured previous-event state; F332 native observed 5/10/15s quote path 54D =178D, decision only after 15s **while order still pending**, F332 broker 127-leaf55-round 3class source-fitted JanFebJunJul original model SHA `b5b45ce047cf1f61d129e0594f65c26051345a1fba4e2f21543262b3c6aa0d25` cutoff **0.8035776155306835** locked before August outcome scoring. No peeking forward beyond each decision time.
- Frozen source truth: side-relative midpoint at first original native quote within [t0+30,t0+32 sec), >= thresholds 0.10 as original; future outcome *label only*, not inference feature. Class=0 correct, 1 opposite, 2 neutral/missing.

## Observed August source-label separation (NOT full F340 parent cascade)

**347,256 original generated R00 source events:** 155,786 original correct; 149,708 opposite; 41,762 neutral. **56,262 wrong/neutral veto** (52,478 opposite +3,784 neutral), **4,862 correct veto**, **11.57178:1 incorrect-to-correct veto**, correct retention **96.87905%**, incorrect rejection **29.38424%**. BUY 208,647; SELL 138,609. Original August event/day and UTC session source-exact receipts preserved. No threshold optimization on August.

Historical owner-approved **F340 four-month gross 334,622 wrong versus 37,091 correct =9.02:1** compared only to original F234→F330 t+5 eligible subset. **Exact F234/F330 August keeper masks are NOT present/recovered**: August 56,262/4,862 is frozen **all-event standalone classifier**, not comparable as incremental F340, and not the whole trading system. No original August R9 completed-trade exact quota ledger, no native MT5 order fills, spread/slippage/margin/cost/shared equity, G01–G09 or deployable EA approvals. Original 39 checkbox count remains 17/39 historical-approved (8 M + 5 S + 9 G open).

**Execution-price negative evidence:** quote-paired 15-second hypothetical long ask→30s bid, short 15s bid→30s ask. 328,685 pairs; mean −$0.199337/oz all, kept 270,030 mean −$0.202355/oz, veto 58,655 mean −$0.185441/oz. These are independent overlapping hypothetical quote-price observations, **not filled MT5 real cash P&L**, and show historical label discrimination is not executable positive alpha at the delayed decision clock.

**Temporal label:** August is outside fitted JanFebJunJul and model freeze predates evaluation. Historical August file/source may have been previously accessed by other research; **cannot certify globally virgin blind data or full OOS system** without exposure audit. Do not tune against August or claim profitable execution. Preserve negative evidence.

## Reproducible original archive and continuation

Full original 21-member portable code/source/frozen weights/score data/recount/manifest ZIP **4,746,877 bytes SHA256 `3a8a9974b7ccad3c1e9a1cb7273a9aaa5e39fe7bbedad7ad66219f6f0b111e79`**, ZIP CRC and 20 member SHA-size manifest PASS. Uploaded and independently metadata-verified MT5_EXPAND (PRIMARY attempted and returned 403 so no PRIMARY binary claim):
https://drive.google.com/file/d/1ia5rr3tztXqD3A_3Qcoiz5m0Q8H9wLdW/view

Original official raw Coinexx August ticklogger source https://drive.google.com/file/d/1NUluzcABKwwYQgBtO_wRbYBYOW7gG494/view . PRIMARY canonical append-only historical forensic log https://docs.google.com/document/d/1cYkw43LC5Ot-V686onwQS5cDZRKPyw1T1T6MvbFVSCA/edit .

**NEXT:** recover original August F234 and F330 parent event masks using original source contracts without reimplementing tick engine; if impossible leave conditional F340 unscored. Genuinely untouched fully sealed forward OOS plus exact native MT5 filled shared-capital profit/risk is still required for production. No model owner promotion beyond original historic F340 and no engine defect ticket.

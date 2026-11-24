# V19 — R9 HybridGate stateful merged-entry queue, exact source recovery 2026-11-23

**RESEARCH CHECKPOINT — NO PROMOTION. V17B GOVERNING ENTRY-ONLY CONTROL REMAINS UNCHANGED.** This checkpoint is not a native MQL5 EA, not a broker or funded-account backtest, and not a nine-month profit reconstruction.

## Mandatory sources — DO NOT REPLACE WITH THIS SUMMARY

**[MT5_EXPAND full V19 C++17/Python/model/QA source archive](https://drive.google.com/file/d/1N06L9qSi-cqHKGylWbJd5-lZ7Bw-bo2w/view)**

- Archive: `R9_HYBRIDGATE_ENTRY_V19_STATEFUL_QUEUE_SOURCE_20261123.zip`; SHA-256 `1943ce9a3b2f6b6e9619d7f185cd61c55210b42aa0909cd5804af9124dd0dde9`; 8,565,469 bytes; 57 ZIP members, all 56 payload SHA-256 and ZIP CRC verified. Full actual C++17 engine including source-exact V17/V16/V14 R9 parents, Python sampling/training/inference/queue arbiters, four fitted LightGBM model texts, source-only nine-month proposal ledgers, attribution/scorecard CSVs and regression tests. No original raw tick or full merged historical files duplicated.
- **READ `V19/README_SOURCE_EXACT_V19.md` and full source files inside archive**; this GitHub note is an index and rollback pointer, NOT an executable source substitute.
- Original R9 v1.90 MQL5 path `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5`, original blob SHA `7eecb5f1947017a01ce85b2520725de54749e523` unchanged on branch `carson/mt5-r9-hybrid-gate-certification`.
- Frozen authoritative **NEW** Jan merged R9+Coinexx historical ledger ZIP and Feb–Sep merged ZIP, **272,352 mapped historical entries**, remain the ONLY OFFLINE supervised entry targets. Original nine monthly Coinexx TickLogger gzip sources 72,129,347 ordered source quotes remain the inference market data. All 9/9 gzip SHA256 and 2/2 original merged ZIP SHA256 independently verified this pass.

## Exact missing-entry diagnosis

V17B accepted CONTROL: 287,770 source-only proposals and 102,681 one-to-one correct-side ±5s matched frozen entries. Among all 272,352 frozen entries: 102,681 matched; 31,609 nearby wrong-side/matching conflict; **138,055 had no proposal within five seconds**; seven nearby same-side but greedy-unpaired. Source-timed V19 queue 4,314,519 evaluation events from source ticks; January 26,504/27,980 frozen entries had an event within ±5s, including 16,424/17,791 originally missed V17B entries. That coverage was measured retrospectively, and does NOT constitute executable capture.

R9-native source-only event queue: minute-origin quote, original 10-second completed-S1 impulse, qualified impulse memory, 20-cent pullback, 8-cent reversal/reclaim, opposite-side prior pulse, directional-change flips, quote renewal, spread narrowing, 5s compression/momentum conflict and bounded later event opportunities. `V19/src/v19_stateful_queue_candidates.cpp` performs streaming source-quote C++17/zlib tick traversal. Entry classifiers use 3-class NONE/BUY/SELL first/recovery hazards trained on all nine frozen months with **target timestamps and sides as offline labels ONLY**. Both initial and recovered entry proposals are chosen chronologically using only pre-entry source state.

## Completed on-policy *ENTRY ONLY* nine-month graded comparison

| Policy | proposals | ±2s correct-side | ±5s correct-side | ±15s correct-side | ±30s correct-side | 90% monthly count floor |
|---|---:|---:|---:|---:|---:|---|
| V17B unchanged control | 287,770 | 53,384 | 102,681 | 148,895 | 182,699 | PASS 9/9 |
| V19A added R9-state queue events | 288,193 | 53,648 | 102,762 | 149,044 | 183,094 | PASS 9/9 |
| V19B high-confidence early WAIT | 288,188 | 53,636 | 102,737 | see source scorecard | see source scorecard | PASS 9/9 |
| V19C conditional late recovery | 287,766 | 53,385 | 102,664 | see source scorecard | see source scorecard | PASS 9/9 |

**V19A only +81 ±5s matches for +423 extra proposals, with worse precision per proposal. Do NOT promote V19.** ±5s coverage of original 272,352 frozen entries remains ≈37.73%, not near 90%. V19B/C did not improve on V19A. All are heavy full-nine-month in-sample research results, no funded entries/fills/holds/exits/profit claims.

New source-derived late-rearm evidence: of the 10,476 V17B-missed second entries in seconds 30–34 with ≤5s preceding queue state, 5,316 had queue stage 3 reclaim and 4,385 had an opposed preceding R9 pulse. A separate recovery-time predictor had in-sample early/late discrimination AUC 0.698; acting on it through the source-only queue did not improve ±5s entry matching. Minute-open first-entry early/late AUC ≈0.605, likewise insufficient.

## QA / continuation

- Independently re-extracted this ZIP to a clean workdir, compiled C++17/zlib and replayed first 1.2 million original January quotes; 70,469 emitted source events byte-identical to full-month prefix. No future source suffix needed.
- `replay_v19A_without_merge.py`: independently produced all **288,193** V19A timestamps and directions from source-only event scores plus frozen source-only V17B control; exact integer-column parity with full original V19A generated ledger, without reading the frozen merged targets. SHA256 source-only generated ledger `aeda7632448e3b8e86ce21006efea408f7b9ce465abd8dbafa83ab2b4f7c19c7`.
- Regression receipt and 9/9 original Coinexx gzip + 2/2 merged reference archive hashes inside full ZIP.
- Previous rejected V18 14-quote-proxy source work remains isolated; none of its models silently replaces V17B here.
- Original production R9 MQL5 untouched. **Native MetaEditor and MT5 Strategy Tester real-tick certification not yet done**. Native `OnTick` events may be coalesced; exact tick-history processing is required for eventual parity.

## Next action, not yet complete

Research a **sequence-level optimal-stopping controller** for FIRST/WAIT/RECOVER entry choice using the original frozen historical entry sequences as OFFLINE training labels, while all runtime decisions use only Coinexx source quotes and completed source candles. Unlike generic per-event classification, the controller must quantify the option value of reserving a minute-slot for a later state without hindsight online. Preserve full nine-month source QA, per-month >=90% entry-volume floors and one-to-one same-side timestamp matching. Do NOT add fictitious broker depth or realized trade tape. Do NOT restart data warehouse, change approved EA, or present hindsight-selected mapped trades as executable outcomes.

**ROLLBACK:** the new V19 branch is an additive documentation-only child of the original V17B control. Exact working V19 source + model weights are in the checksum-pinned Drive ZIP, not in this GitHub documentation file.
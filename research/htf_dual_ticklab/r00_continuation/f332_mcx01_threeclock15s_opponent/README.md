# F332 — Three-clock XAUUSD bid/ask quote-path wrong-signal veto (research only)
Date: 2026-10-22. **OWNER UNAPPROVED; M-CX-01 STILL OPEN; G01–G09 OPEN; NO MT5 DEMO/LIVE.** Canonical owner original checklist remains **17/39 historical accepted F01–F17**. No accepted-components folder copy.

## Exact lineage
Parent **F331** research HEAD `43c52c0ceab030b2bc6194ba32bbd7acdc763f96`; pinned dual Coinexx/Dukascopy source-native UTC replay dependency `ca4b58aec597174b6f6d18ab2f36cba6836e4f4c`. Original tick/source time Coinexx JanFeb wallclock -120m, JuneJuly -180m; Dukascopy already UTC. Eight original SHA-pinned XAUUSD month tapes JanFebJuneJuly 2026. Immutable 2,574,251 original t0 R00-054 event IDs, sides, and native signed midpoint outcomes first quote in t+30 to t+32 seconds. F234 original parent preserved; no teacher current-event labels/scores in predictor input.

## Why different from earlier F315–F330
The same-month FILTER08 Coinexx January 450tree 255leaf 93 feature fitted teacher vetoes 86,336 bad/5 correct on **the same January it was trained/scored** (5 score overlays, 105 monthly in-sample policies); this is hindsight and not live alpha. F332 is a genuinely different **pending until t0+15000ms** structural model, not a t0 filter. A **178-dimensional** as-of quote state = 124 original strict t0 past-only quote/side/completed HTF features + 42 source-native quote marks across 5/10/15s observable windows + 12 quote acceleration / side/HTF nonlinear interactions, trained in a 3-class LightGBM correct/opposite/neutral mode. It can only decide at t+15s, not at t0.

High-capacity 511leaf105round pilot and 255leaf80round 120k four-month attempt exceeded available compute budgets; original logs preserved, no engine defect. Resource-bounded but information-rich 127leaf55round 3-class completed. Pilot Coinexx Jan first70+Feb first60 40s-purged fit, February late40 source exposed calibrated q750: **25,892 bad /3,740 good =6.923:1**, q850 **16,245 /1,361=11.936:1**, q900 **10,586/600=17.644:1**. This qualified owner-directed >1.5 exploration trigger, not signoff.

## Four-month in-sample fit, all eight source cells
Each original broker separately trains Jan/Feb/June/July first80% original event sequence with 40s embargo, 12,000 deterministic chronologically spaced original F234 keep examples per cell, 48k events/broker. Training-output q750/850/900/950/975 thresholds frozen, no later20 target month label tuning. Later20 is **fit-disjoint but previously historically research-exposed** and not true blind. Original Coinexx **full four-month F234-parent** events scored with exact original F330 t+5 source-shadow veto overlap. Original Dukascopy **late20** subset of all four months scored with broker-fitted model and cross-broker frozen Coinexx model; full Dukascopy source mask remains unscored due resource, so no 8-full-month gate certification.

At q850 among all **eight** later20 broker-month fit-disjoint source subsets:
- **55,950 originally bad veto /4,949 originally correct lost = 11.305:1**; 52,927 opposite and 3,023 neutral.
- Each of eight original cells ratio >=7.978:1. q750 87,465/12,543=6.973:1; q900 39,005/2,564=15.213:1; q950 20,126/879=22.896:1; q975 10,103/276=36.605:1.
- Independent CX trained model on DK July late20 at its own q850 training cutoff 3,722 bad veto /245 correct loss =15.19:1; exploratory cross-broker but no unseen date.
- Coinexx Jan FULL original F234-source veto at q850 33,554 wrong /3,324 good lost, still only 38.9% of teacher's 86,336 fitted bad-veto volume; combined F234+F330+F332 source-shadow correct kept 163,004/181,869=89.6271%, bad veto 53,216/163,496=32.5488%: **no 90% bad gate** and no original immediate-t0 teacher numerical parity.

All eight saved score vectors reverified against original F330 parent event IDs, source t, side, truth and training-threshold classwise count; exact original q850 55,950/4,949 preserved in independent receipt.

## Scientific limits and next
Quotes observable up to t+15 sec still subject to same-millisecond OnTick arrival ordering; original [t+30,t+32) label scored against t0 source mid, not executable 15s ask/bid entry; no real fill, order cancellation, spread+latency, margin, $100/$200 solvency or account P&L, no 4,178 source supply retest, no final exact F17 P05 combination. All Jan–Sep 2026 globally research-exposed, no genuine blind March/April/May claimed. Need paired complete-EA native tick/MT5 executable residual, split by broker×session×closed M15/H1, and cooperative F331 t+5 correct-rescue before approval. No original checklist changes.

## Permanent original research archive and readbacks
**Portable complete 57-member research ZIP** (Python code, both broker fitted model weights, 8 original late20 score vectors with 4 full CX source scores, eight source manifests/receipts, original immutable historical grids, high-capacity timeout logs, independent parity test, original source adapter Python, full forensic audit and research report):
`F332_MCX01_THREE_CLOCK_QUOTE_OPPONENT_LATE20_EIGHT_CELL_RESEARCH_ONLY_20261022.zip`
**13,965,120 bytes, SHA256 `1355e8c821f691e36b66d573e9f9d4ea22e1e0b6095b01bb38b98b841e35fab5`**, ZIP CRC and 56 member SHA/length manifest checks PASS.

- **MT5_EXPAND full original binary archive:** https://drive.google.com/file/d/11xZvX5D9Yn15-avKMDKhtrxKdWtFvoxJ/view
- **PRIMARY full written scientific receipt:** https://drive.google.com/file/d/1TBfhx0DMMByAmazvbfgC_SADo4gRvzmx/view
- **PRIMARY append-only 4-month forensic log:** https://docs.google.com/document/d/1cYkw43LC5Ot-V686onwQS5cDZRKPyw1T1T6MvbFVSCA/edit
- **PRIMARY original 39-objective owner checklist:** https://docs.google.com/document/d/1i2GyLfwVFvyjxB-sNaOwkS6kzZLSWTsijGXaA9qJou0/edit

The attempted 13.96MB ZIP upload to PRIMARY returned HTTP403; original full binary is independently preserved at MT5_EXPAND. This GitHub branch contains **the research README**, not model binary ZIP. No false GitHub binary sync claim.

Community reconstructible logic scout: [SelectiveNet](https://proceedings.mlr.press/v97/geifman19a.html), [official code](https://github.com/geifmany/SelectiveNet), [River ADWIN](https://github.com/online-ml/river/blob/main/river/drift/adwin.py), [finlab CV concepts](https://github.com/landtml/finlab-ml), official [MQL5 NewTick queue warning](https://www.mql5.com/en/docs/event_handlers/ontick). No external quote feeds, third-party trading strategies or pretrained model code imported.

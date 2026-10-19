# R00-054 FAILURE-02 — research continuation, 2026-10-19

**Original baseline remains protected:** original R00-054 `lgb_oracle_weighted`, January-trained per-broker models, source-native 5s event universe, original 30–32s +/-$0.10 direction label, and both verified tick replay engines. **No live MT5 release. No exit/holding/P&L research.**

## Exact ancestor
Parent `carson/htf-r00-054-entry-filter-20261019`, commit `6d063a0ff22f3eec5bb1f1d2ebef583fb163b226`. This branch is an additive original research receipt. No source or models from ancestors have been rewritten.

## Original four-month study
- Authorized original January/February/June/July 2026 Coinexx and Dukascopy monthly native bid/ask derived feature-cache ZIPs; source tape hashes checked in original research and original event vector + native 30s labels checked in current scoring code. Coinexx Jan/Feb -120min / Jun/Jul -180min relative to raw server wall timestamps, Dukascopy UTC native.
- Jan fit, February only policy selection/freeze, June/July historically EXPOSED transfer, not blind.
- June/July protected original `KEEP_ALL`: 1,231,388 event candidates, 548,099 correctly directed (44.5107%), 530,177 opposite and 153,112 neutral/missing.
- Four independently trained January meta specialists from causal **existing preserved** tick-derived features: `micro_response` (25 features), `published_structure` (23 completed-timeframe features), `matured_feedback` (23, all past-label feedback delayed +32s), `cooperative_all` (71). Each original specialist has a separate hypothesis and ablation; existing R00-054 specialist emission states are reused, not reimplemented. This pilot did **not** reconstruct raw bid-only/ask-only tick-order sequencing or true published swing/pivot state machines.
- 36 predeclared February veto policies: 4 experts x 8 bottom-quantile thresholds + 3 cooperative mean policies + KEEP_ALL. FEB elected `COOP_MEAN_0.050`, SHA-256 of freeze JSON `7706355c783aec07740bbfcb4678b1d394602963f341efd3b8cd4474844f4283` (check against packaged original JSON).
- February election removed 21,028 wrong directions versus losing 11,646 correct, preserving 95.68% correct Coinexx / 96.58% Dukascopy. This was BEFORE June/July scoring.

## Frozen June/July transfer
| broker/month | original correct/events | frozen accepted correct/events | incorrect removed | correct lost | percent correct retained |
|---|---:|---:|---:|---:|---:|
| Coinexx June | 142,224/312,004 | 136,884/298,132 | 8,532 | 5,340 | 96.25% |
| Coinexx July | 143,362/321,069 | 130,903/289,355 | 19,255 | 12,459 | **91.31% FAIL** |
| Dukascopy June | 132,105/297,035 | 126,683/280,773 | 10,840 | 5,422 | 95.90% |
| Dukascopy July | 130,408/301,280 | 122,114/275,832 | 17,154 | 8,294 | **93.64% FAIL** |

**Frozen total: 516,584 correct / 1,144,092 accepted, precision 45.153%**, versus baseline 548,099 / 1,231,388, precision 44.511%. Removed 55,781 wrong but sacrificed 31,515 correct. No breakthrough (+0.64 absolute precision pp); July per broker correct-signal retention below 95% protective research gate. **NOT PROMOTED. Do not trade.** KEEP_ALL remains the elected MT5 entry foundation.

Original source-month R9 hourly misses = 2 coincident Coinexx June boundary mismatches for both KEEP_ALL and selected, no newly failed hours in this pilot. Full continuous-UTC daily/week/month recertification was NOT performed here and must not be claimed. Other June/July candidate rows are explanatory exploratory observations, NEVER retrospectively chosen as if frozen February.

## Forensic discoveries (descriptive, not standalone forward-validated veto rules)
- Across both June/July broker observations: quote-rate >=4 native quote updates/sec over previous 10s: 340,815 correct / 733,722 = 46.45%; quiet: 207,284 / 497,666 = 41.65%.
- Fixed 13–17 UTC: 106,389 / 226,151 = 47.04%; fixed 22–00 UTC: 37,666 / 93,342 = 40.35%.
- Both completed M15/H1 body signs aligned: 111,645/251,572 = 44.38%; both opposed: 173,519/382,639 = 45.35%. Do not claim HTF body agreement itself predicts original side correctly.
- Simple blanket quiet/time veto would remove massive already correct event supply.

## Causal discipline
The added label-feedback state is based on **past original events whose future diagnostic result matured by t+32s**. Adversarial mutation of current/future labels confirmed no effect on earlier features. Original cached features, original reference timestamps/sides and +30s labels identity-checked in all eight source months. Source original January base forecaster was itself fitted on January (meta-training must be interpreted in-sample). Original event frequencies cannot be equated to simultaneously fundable positions.

## Independent sources used as hypothesis generators (never presumed proven gold alpha)
- MetaQuotes: https://www.mql5.com/en/docs/series/copyticks
- TradingView confirmed bars/repainting: https://www.tradingview.com/pine-script-docs/concepts/repainting/
- ForexFactory XAUUSD phase sequencing: https://www.forexfactory.com/thread/1397686-xauusd-timing-model
- Academic order-book imbalance on US equities (NOT a CFD gold result): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1712822
- MQL5 trade meta-labeling: https://www.mql5.com/en/articles/9138
- MQL5 purged CV: https://www.mql5.com/en/articles/20059
- Reddit trading meta-labeling methods: https://www.reddit.com/r/algotrading/comments/1lnm48w/meta_labeling_for_algorithmic_trading_how_to/
- Myfxbook current sentiment not a historically aligned authorized feature: https://www.myfxbook.com/community/outlook/XAUUSD

## Exact original local research package
`R00_054_FAILURE02_EXECUTED_RESEARCH_20261019.zip`, 23 files, CRC PASS, SHA256 `ff4d97a246b87eaa9a789d360c5ad0c40299ac338c99620235d6d41a3f96d35f`, includes complete **runnable Python** `run_failure_detector_02.py`, adversarial `test_causality.py`, `source_event_error_forensics.py`, 8 trained models .joblib, selection/plan JSON, all 36 policy Feb/Jun/Jul results, original baseline error-state ledger, exact per-file SHA256 manifest and full logs. Large immutable original R00-054 source-native cache ZIPs remain in the existing separately verified Drive archives.

Cloud binary duplicate of the 23-file package is **NOT verified** by this commit; no fictitious upload is claimed. Previous MT5_EXPAND/PRIMARY seven-month R00-054 originals remain where pinned.

## NEXT RESEARCH — frozen design proposal, not an executed result
Use approved raw Coinexx and Dukascopy tick tapes for new **bid-only/ask-only/joint quote chronology**, spread/repricing persistence, and published confirmed structural sweep/reclaim state. Encode separate lifecycle resets (ARM/CONFIRM/VALID/EXPIRE/COOLDOWN/REARM). Train **three-outcome** `correct / opposite / neutral` meta-oracles rather than binary good/bad. Purged Jan chronological fitting, February-only freeze, report exposed June–July and R9 correct-signal floors at each UTC hour/day/week/month, never hide lost correct entries. Reserve true future month for genuinely blind test. No engine rebuild, holding, exit, execution or P&L until separately authorized.

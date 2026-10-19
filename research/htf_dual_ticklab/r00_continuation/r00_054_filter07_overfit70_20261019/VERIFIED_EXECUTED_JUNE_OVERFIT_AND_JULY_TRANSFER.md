# R00-054 FILTER07 — completed additive deliberate-overfit direction filter

**Date:** 2026-10-19. **DO NOT PROMOTE AS EXECUTABLE OR BLIND PERFORMANCE.**

**Lineage:** protected original R00-054 `lgb_oracle_weighted` source-tick initial BUY/SELL emitter. The parent research head is `f05028d3b50a93c77847206d32a0518af56bc574` on `carson/htf-r00-054-failure-ordered-quote-filter05-20261019`. This branch is a direct descendant, and all original primary EA, replay engines, source records and previous data are unchanged.

**Human requirement:** build 70% intentionally overfitted second-stage veto for R00-054, preserving R9 SYNTH benchmark correct-signal counts hourly/daily, learn combinations and later verify in truly new blind months. Scope: 2026 January/February/June/July authorized original Coinexx & Dukascopy quotes, each independently; no hold/exit/PnL.

## Verified work (complete)

- Two source-specific binary June-fitted LightGBM models; two additional separate three-class correct/opposite/neutral models. Input 93 causal-at-decision columns: original 43 past-only tick and completed M1/M5/M15/H1, 15 ordered BID/ASK update features, 4 expert states, side-relative returns and expert agreement, session cyclical time, and 6 matured earlier outcomes (>32s old). Original labels used in June **model training**, not in current-decision input; outcome dependence is intentionally overfit.
- 200 predeclared policy/threshold June experiments across 5 score families and 20 acceptance rules per broker. June selected 40th-percentile score veto for each broker, using June labels, preserving incumbent signal side and timestamp. Policies performing an entire-hour top-K score rank were evaluated retrospectively only and are **not executable causal live filters**.
- Original fixed +30..32s first observed future midpoint signed movement >$0.10 correctness; no future label treated as tradable immediate information; all neutral/missing count wrong.

| Original-source June in-sample overfit | Coinexx | Dukascopy |
|---|---:|---:|
| Original R00-054 correct candidates | 142,224 | 132,105 |
| Retained correct | **142,214** | **132,095** |
| Total accepted | 187,202 | 178,221 |
| Apparent precision | **75.9682%** | **74.1187%** |
| Incorrect rejected | **124,792** | **118,804** |
| Eligible R9 90%-of-trade-count hours | **497/497** | **497/497** |
| Eligible R9 90%-of-trade-count days | **27/27** | **26/26** |

**Combined two independent June evaluations: 274,309/365,423 = 75.0662%, 243,596 original incorrect signals rejected; 994/994 matched R9 hours, 53/53 days; only 20 correct signals lost.** This proves June in-sample overfit capability, not forecasting.

Frozen threshold applied without July retuning on historically exposed July:
- Coinexx 120,377 correct / 266,898 accepted = 45.1022%; 506/506 eligible hours, 28/28 days.
- Dukascopy 110,487 / 250,527 = 44.1018%; 504/504 hours, 27/27 days.
- The original 70% fit did NOT transfer to July. Neither July nor any previous months are genuinely untouched blind holds.

## Mechanism discovery with deterministic family ablations

In the June fitted models, the most important group by score perturbation is original past price/confirmed HTF geometry, followed by ordered quote responses and matured feedback; session and four already-existing expert-state votes add much less. This does not prove causal predictability. In historical July transfer model AUC was 0.51638 on Coinexx and 0.52378 on Dukascopy; disturbing price/HTF group reduces AUC 0.01412/0.01575, ordered bid/ask 0.00024/0.00314, matured-feedback 0.00194/0.00937. These point toward a NEW independently published structural-phase specialist, sequence-aware quote-side specialist and strict matured-feedback lifecycle. Reject raw feature importance as standalone deployment proof.

**NEXT:** retain the original R00-054 entry machine unchanged. Engineer separate ARM -> CONFIRM -> RELEASE/VETO -> EXPIRE -> COOLDOWN -> REARM specialist lifecycles for (1) nonrepainting completed M1/M5/M15/H1 sweep/reclaim/retest, (2) one-sided BID/ASK quote update hazard and staleness, (3) mature prior-label reliability, (4) source-specific session/regime. Train auxiliary models with strictly purged chronological January OOF primary predictions, February-only policy freeze, June/July historically exposed check. Evaluate correct retained, wrong rejected, neutral vs opposite, all eligible per-hour/day R9 supply, and NO RETIMING. Genuinely blind certification requires a newly authorized unseen quote month and exact SHA file pin. No independent executable trades inferred.

## Byte-exact preservation

Two independently created Google Drive copies of **same source ZIP**:
- PRIMARY: https://drive.google.com/file/d/1dOUVcoK-Po_vF3TCUcCAAcWM5KNZOwo5/view
- MT5_EXPAND: https://drive.google.com/file/d/1uqqCcQ3w06Lx5MKKmKCqyqy-tQ91J-hB/view
- Name: `R00_054_FILTER07_OVERFIT70_RESEARCH_PRESERVATION_20261019.zip`, bytes **24,440,706**, original local SHA-256 **37bad631740128b0aafe0a7044331939aaea4d2106067b2203e788a265b2965d**; ZIP CRC and all manifest member SHA hashes locally PASS; Drive upload succeeded and both remote file IDs and byte sizes were retrieved, but this commit makes **no independent remote SHA digest assertion**.
- Complete unmodified executable research helper `run_filter07.py`, SHA-256 `8be70aea913821591c6483216ee981d754c0cc1643aa6eae31b75f949414aa84`; `run_family_ablation.py`, SHA `1d413f9d7792be9c9d6617500d548621a5794ebf7eca2937e2d9f585252c2090`. Both archived intact within ZIP.
- All 4 model joblibs, 200 complete June candidate results, 2 frozen July scores with event timestamps/outcome array, explicit ablations, logs, hash manifest and FULL original research receipt. Prior FILTER06 checkpoint included as immutable nested original.
- R00-054 original models/full raw source are NOT bundled here: they remain preserved at the original approved Drive and GitHub references. Do not claim this small additive package is raw source data.

**Relevant secondary source concepts (not independent validation):** MetaQuotes CopyTicks (bid/ask flags) https://www.mql5.com/en/docs/series/copyticks ; MetaQuotes meta labeling https://www.mql5.com/en/articles/22274 ; TradingView completed HTF/nonrepainting https://www.tradingview.com/pine-script-docs/concepts/repainting/ ; ForexFactory sweep/retest anecdotal https://www.forexfactory.com/thread/post/15768588 ; Reddit meta-labeling discussion https://www.reddit.com/r/algotrading/comments/1lnm48w/meta_labeling_for_algorithmic_trading_how_to/ .

**Guardrails:** Cumulative original investor/governor/source laws continue binding FULL VERBATIM. This additive receipt is a locator, not a replacement summary. No original code was modified, no failed hypothesis deleted or retroactively promoted, no backtester rebuilt.

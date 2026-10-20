# R00-054 FILTER08 — Four-month 70% deliberate overfit research (2026-10-19)

**Research status:** All eight broker-month SAME-LABEL-FIT experiments completed, original R00-054 core and Coinexx/Dukascopy tick replay READ ONLY. **Not** a single month-independent deployable classifier, not blind validation, no profit/execution/hold/exit research.

## Exact lineage and original evidence
- Elected original R00-054 high-volume `lgb_oracle_weighted` BUY/SELL timestamp and side unchanged.
- Parent branch `carson/htf-r00-054-failure-ordered-quote-filter05-20261019` at exact parent SHA `f05028d3b50a93c77847206d32a0518af56bc574`. Earlier FILTER06/07 and the seven-month verification preserved and unchanged.
- Registered ORIGINAL native Jan/Feb/Jun/Jul source gzip files rehashed **8/8 PASS**: Coinexx JanFeb UTC -120 min, JunJul UTC -180 min; Dukascopy UTC native. Original event arrays, quote-order features and immutable +30..32s midpoint $0.10 directional labels reused; no engine reconstruction.
- Method: historical per-broker per-month LightGBM meta-correctness model **trained and evaluated on those SAME labels**; 93 causal-at-emission features from original completed M1/M5/M15/H1 geometry, trailing returns/efficiency, quote-change chronology, mature older labels, expert states, session/regime; first stage original direction NEVER reversed or retimed.
- June original fitted binary models REUSED from FILTER07 unchanged. Other six added secondary fits. 5 predeclared cooperative probability recipes × 21 quantile levels = **105 policies per broker-month, 840 historical policy evaluations**. Historical score/threshold selection used same period outcomes and is intentionally contaminated.

## Full preserved in-sample fitted result

| Month | Broker | Original correct | Retained correct | Emitted after filter | Apparent precision | Matched eligible R9 hours | Matched days |
|---|---|---:|---:|---:|---:|---:|---:|
| January | Coinexx | 181869 | 181864 | 259024 | 70.2113% | 480/480 | 26/26 |
| January | Dukascopy | 178642 | 178635 | 249427 | 71.6181% | 480/480 | 26/26 |
| February | Coinexx | 155538 | 155533 | 221993 | 70.0621% | 458/458 | 24/24 |
| February | Dukascopy | 143923 | 143896 | 202864 | 70.9323% | 458/458 | 24/24 |
| June | Coinexx | 142224 | 142221 | 202802 | 70.1280% | 497/497 | 27/27 |
| June | Dukascopy | 132105 | 132102 | 185647 | 71.1576% | 497/497 | 26/26 |
| July | Coinexx | 143362 | 143356 | 200668 | 71.4394% | 506/506 | 28/28 |
| July | Dukascopy | 130408 | 130404 | 180768 | 72.1389% | 504/504 | 27/27 |

**Aggregate, descriptively only (two independent broker evaluations):** Original 2,574,251 signals / 1,208,071 correct (46.9290%). Same-month overfit selected 1,703,193 emitted / **1,208,011 correct = 70.9263%**. 870,998 known incorrect signals rejected (63.7543% of incumbent bad events); **60** already-correct signals rejected. These successes are historical *fit capacity* and not out-of-sample evidence.

**Strict extra verification on continuous UTC calendar** across requested Jan, Feb, Jun, Jul: each broker independently passes **1,939/1,939 eligible R9 hours, 103/103 UTC dates, 18/18 ISO weeks, 4/4 months** for >=90%-of-original-R9 SYNTH correctly directed signal *count*. Zero-signal R9 reference hours are not silently omitted. R9 completed SYNTH positions are a quota benchmark, never misrepresented as real executed correct wins. No joint account interpretation.

## Mechanism discovery from accurate original fine-grained feature mapping

LightGBM **in-sample fitted gain shares**, not causality:
- Coinexx: side-relative past returns 13.4%; other multiple-horizon returns 12.4%; actual ordered bid/ask quote response 11.3%; genuinely matured earlier event feedback 9.4%; prior **completed M1** geometry 9.3%, completed **M5** 8.0%, **M15** 6.9%, **H1** 5.9%.
- Dukascopy: ordered bid/ask quote response 14.5%; side-relative returns 12.8%; other multiple-horizon returns 11.9%; matured prior feedback 9.3%; completed M1/M5/M15/H1 geometry 8.6%/7.3%/6.3%/5.5%.

These recurring high-gain information families, plus conditional broker/session quote intensity, specify the next independent **neutral/no-opportunity** and **opposite-direction** hazard specialists. Independently reset ARM→CONFIRM→VETO/RELEASE→EXPIRE→COOLDOWN→REARM per specialist; use publication-safe structural sweep/reclaim/displacement/retest, strictly prior 32s-matured shadow outcomes, and quote-side irregular tick sequences. Require evidence of genuinely independent incremental contribution with explicit ablations.

## Preservation / reproducibility

**Immutable complete user-deliverable portable ZIP:** `R00_054_FILTER08_FOUR_MONTH_70PCT_OVERFIT_RESEARCH_20261019.zip`, **51,096,243 bytes**, SHA-256 `7edaddf30f3a19cafd364a270333c6f87962960233f9d10ccbfb6e2a3b23b2ad`. ZIP CRC verified; 52 archive members and 50 member-hash manifest entries independently checked. It includes original additive executable `run_four_month_70pct_overfit.py`, finalizer, independent feature-family analyst, eight full score vectors and historical kept masks, SIX newly trained persisted model joblibs plus June parent references, 840-row per-model policy grids, all feature-gain tables, 8/8 raw source SHA receipt, original event-input hashes, full R9 hour/day/week/month panels, complete evidence manifest, multi-specialist next mechanism contract, and source links. The six added models do not replace the underlying R00-054 original fit. Underlying raw market data and June model originals remain at earlier pinned research locations.

**Cloud status:** No new remote copy of this ZIP is claimed unless its content hash is actually checked in Drive. GitHub is a provenance / continuation receipt; full binary models are in separate download archive, not this Markdown blob.

**Next fit policy:** A single MONTH-INDEPENDENT causal filter must be trained January with purged chronological OOF (particularly primary January in-sample leakage), frozen on February, evaluated separately June/July as HISTORICALLY EXPOSED. For truly BLIND tests require an untouched newly source-approved tick month with explicit SHA registry. The present 70.93% same-label-fit result is NOT transferable accuracy, and cannot justify MT5 release. No funded volume/fills or exit/P&L examined.

## External engineering hypothesis sources (not empirical evidence)
- MetaQuotes CopyTicks bid/ask fields and change flags https://www.mql5.com/en/docs/series/copyticks
- MetaQuotes secondary meta-label classifier https://www.mql5.com/en/articles/22274
- Regime/ADX and dynamic bandwidth interaction https://www.mql5.com/en/articles/22754 and https://www.mql5.com/en/articles/22755
- TradingView confirmed HTF publication and repainting limitations https://www.tradingview.com/pine-script-docs/concepts/repainting/
- Structure/reclaim/CHOCH hypotheses https://www.tradingview.com/script/MJJ6BOnb-Liquidity-Sweep-Market-Structure-ICT-SMC/

**DO NOT restart the confirmed R00-054 quote engine, do not refit the June parent by default, do not overwrite older evidence, and do not promote same-month fitted precision to a blind-month result.**

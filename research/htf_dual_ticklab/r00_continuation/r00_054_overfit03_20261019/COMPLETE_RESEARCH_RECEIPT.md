# R00-054 Overfit-03: Preserved Signal Failure-Oracle Discovery

**Recorded date:** 2026-10-19. **STATUS: DELIBERATE IN-SAMPLE OVERFIT / NOT PROMOTED.**

This is a direct continuation of the human-elected R00-054 initial-direction foundation. The protected January-trained R00-054 LightGBM ensemble, original signal dates/sides, future-label definition, source allowlist, established Coinexx & Dukascopy Python replay, and previous immutable experiment results are unchanged. No MT5 EA code/position execution, hold, exit, fill, P&L, margin or fund survivability is inferred.

## What was explicitly requested and tested

The user requested deliberate overfitting *for mechanism discovery* before returning to locked pre-registered research and eventually truly blind new months. We fitted two **separate source-specific high-capacity LightGBM meta-correctness models**, one for Coinexx and one for Dukascopy, against the **already known June and July future direction correctness labels**. Each fits a deterministic every-seventh-event subset of both months. Original event-clock labels are **+30s to +32s first-real-quote midpoint > +$0.10 in chosen direction; neutral/missing wrong**. Data are quote updates (not centralized traded volume). Only historical bid/ask-quote-derived existing causal state is used as predictors. Deliberately fitting June and July disqualifies all June/July success numbers as predictive validation. The remainder of those months is highly correlated through shared quote paths and overlapping 30-second target windows; treating that remainder as unseen would also be misleading.

**Approved input scope:** January, February, June and July 2026, original source month ZIPs from the two authorized feeds. The two February files are used only for backward-time reliability diagnostics in this experiment. Source arrays are the byte-preserved original R00-054 native event caches and `FROZEN_R00_054_EVENTS_*` event ledgers from prior validated seven-month recovery. Original R00-054 and R9 datasets are never written. Every event timestamp matches original, and correctness is regenerated and verified against the original side and d30. A large-model label used after the fact to score its own fitting sample is **not** a real-time trade-filter rule.

## Features and submodels

88 causal at-decision fields drawn from: 43 original R00-054 past-quote/volatility/completed-timeframe features; 12 side-relative returns; four original independent specialist state signals; six UTC session/day-week encoding fields; 15 signed price-response/spread/intensity and completed-body/range interaction features; eight strictly **already matured** correctness-history fields (+32s cutoff, lookbacks 2m, 10m, 60m). Features indicate quote intensity, **not traded volume**. A high-capacity GBDT model has 520 trees, max 127 leaves, min child 7, learning rate .13. This is intentionally too powerful for sparse, highly correlated exposure, serving only a failure-map discovery experiment.

All per-broker untouched original base decisions are held constant. The filter only drops bad candidate sides (never reverses or retimes one).

## Exact recorded findings

Original JUNE+JULY total (two independent broker evaluations, not a single account): **1,231,388 events; 548,099 correct = 44.5107%**, 530,177 opposite and 153,112 neutral/missing.

Deliberate memorization accuracy on its own *subset of fitted exposed events*: **Coinexx 99.607%, Dukascopy 99.750%**; corresponding ROC AUC about 0.99997 and 0.99999. This is NOT OOS. On all June/July labeled events from the same months, AUC about 0.660–0.661 (Coinexx) and 0.667–0.668 (Dukascopy); even these scores share fitted months and correlated outcomes.

**Backward time diagnostics:** February unseen by this auxiliary overfit model but itself historically exposed: Coinexx AUC **0.5062**, Dukascopy **0.5049**. **Cross-broker application** to the other feed's June/July events: Coinexx June **0.5277**, July **0.5274**; Dukascopy June **0.5363**, July **0.5348**. These are weak, not independent forward holdout.

### June+July *exposed fitting-month* threshold frontier

| Threshold on known-month score distribution | Emitted | Correct retained | Correct retained vs R00-054 | Apparent accuracy | Incorrect removed | Eligible R9 hours passing | UTC days passing |
|---|---:|---:|---:|---:|---:|---:|---:|
| No filter | 1,231,388 | 548,099 | 100.0% | 44.51% | 0 | 2,000/2,002 | 106/106 |
| Bottom 30% of *fitted-sample* score | 1,125,942 | 530,413 | 96.77% | 47.11% | 87,760 | 2,000/2,002 | 106/106 |
| Bottom 40% | 1,062,608 | 513,289 | 93.65% | 48.30% | 133,970 | 2,000/2,002 | 106/106 |
| Bottom 50% | 932,134 | 468,792 | 85.53% | 50.29% | 219,947 | 2,000/2,002 | 106/106 |
| Bottom 60% | 178,724 | 128,803 | 23.50% | 72.07% | 633,368 | 1,550/2,002 | 102/106 |
| Bottom 70% | 86,440 | 72,079 | 13.15% | 83.39% | 668,928 | 373/2,002 | 5/106 |

**IMPORTANT source-month boundary caveat:** This audit explicitly uses UTC June/July hourly/day reference keys available in the two month-specific caches: 2,002 historical eligible UTC hour rows and 106 UTC days. The original R00-054 source-month scoreboard contains 2,006 reference hours / 110 source-calendar days from accounting cutovers; those four extra hours / four extra days are not silently certified. The original seven-month continuous-UTC replay resolves quote continuity, but this overfit audit must not claim its own 2,002-row result proves the full 2,006. The *two* baseline already-missing/misaligned hours persist for all cutoffs; threshold bottom 50 introduces zero additional misses in the tested 2,002 hours.

**OVERFIT03 should not be used to filter real trades or promoted to the EA.** The apparently attractive 50.29% filter was chosen and evaluated on fitted exposed months and fails to generalize in separate February and cross-broker checks. The >80% high-confidence filter loses nearly 87% of correct signals and fails the great majority of R9 reference hourly/daily floors.

## Actionable discovery, without pretending to have found tradable alpha

The top two brokers' feature-gain rankings both place **matured-feedback clock/state**, **past quote-path/activity features (original positions 09/10/11)** and **M1/M5 body-to-range geometry** very highly. These are only **hypotheses** because overfit GBDT feature-gain rankings are unstable, correlated, and especially susceptible to memorizing calendar structure. Raw quote-side actual event ordering, nonrepainting swing publication transitions, and explicit neutral-versus-opposite label separation are still absent from these cached 88 features.

### Candidate multi-facade mechanism architecture for new FROZEN research

1. **Quote-sequence specialist:** From approved historical *raw* bid and ask ticks at or before the decision, reconstruct the last 16/32/64/128 actual updates, `bid-only` / `ask-only` / dual quote-change ordering, stale-side residence, alternating quote bursts, spread response, compression and absorption. Use the original tick reader; quote-update flags may be consulted only when their semantics and provenance are actually present. No synthetic order volume.
2. **Publication-safe structure specialist:** M1/M5/M15/H1 swing/range pivots with a strict **pivot-publication timestamp**, completed-bar-only breakout/sweep/reclaim/retest phase clocks and state resets; no future pivot or unfinished HTF candle.
3. **Session/market-regime specialist:** Explicit UTC broker-corrected Asian, London, NY/overlap & rollover episodes, opening-range context, time-varying volatility/spread and quote intensity, independently gated by known-at-entry state. Quote intensity != traded volume.
4. **Error-class specialists:** Three-outcome independent model: original R00-054 correct, opposite-side trend, neutral/no-opportunity; a separate mature-label feedback specialist, not a supervised model receiving its own future label.
5. **Cooperative policy arbiter:** Two-stage AND/OR/veto based on phase transitions, confidence **calibrated per broker and session**. Every specialist `ARM -> CONFIRM -> EMIT or VETO -> EXPIRE -> COOLDOWN -> REARM`; count its independent contribution, correct retained/wrong rejected, regret, and original whole-engine hourly/daily R9 correct supply.

These mechanisms require newly computed causal raw tick features in the already established engines; they cannot be declared discovered profitable factors merely because overfit feature importance favors an existing compressed proxy. A high-capacity overfit discovery model is useful to map the upper known-data fit, not to establish transferable filtering.

## Community/practitioner and official references (hypothesis sources, not validation)

- MetaQuotes tick documentation, quotes/flags semantics: https://www.mql5.com/en/docs/series/copyticks
- MetaQuotes meta-labeling secondary gate (EURUSD research, not this XAUUSD experiment): https://www.mql5.com/en/articles/22274
- MetaQuotes 2026 market-microstructure regime classification (NQ, not XAUUSD): https://www.mql5.com/en/articles/22940
- TradingView confirmed higher-timeframe and repainting caveats: https://www.tradingview.com/pine-script-docs/concepts/repainting/
- TradingView session-sweep-phase illustrated *open-source concepts*, not performance evidence: https://www.tradingview.com/script/UIjbHPKk-Daily-Sweep-Pro-liquidity-raid-and-fair-value-gap-entries/
- ForexFactory breakout failure/session response discussion (anecdotal, not independently backtested on this gold feed): https://www.forexfactory.com/thread/post/15612222
- Reddit /r/algotrading meta-labeling experience (anecdotal): https://www.reddit.com/r/algotrading/comments/1lnm48w/meta_labeling_for_algorithmic_trading_how_to/
- Myfxbook real-time XAUUSD sentiment is **not a dated historical archive**, so is not joined to 2026 quotes: https://www.myfxbook.com/community/outlook/XAUUSD

## Next preregistered continuation

Keep original JAN R00-054 model fitted, FEB-only policy frozen (if auxiliary training uses January, avoid training meta labels from un-cross-fitted January R00-054 predictions to prevent in-sample stacking contamination). JUN/JUL already exposed, report transparently as historical transfer not blind. Before any blind month test, require NEW user-authorized independent real-tick source month with exact SHA-256, deterministic Coinexx UTC conversion QA, and **one single frozen policy** chosen without its outcomes. No net profit/holds/exits until the investor explicitly changes the research phase.

## Files and reproduction

`R00_054_FAILURE_OVERFIT03.py` — exact executable exploratory helper, saved unchanged. `audit_hourly_and_crossbroker.py` — original R9 hours/days and crossbroker reproduction audit. `FROZEN_DISCOVERY_PLAN.json`; two auxiliary source-specific `EXPOSED_OVERFIT03_*_MODEL.joblib`; full event-quantile score table; complete wrong/rejected confusion counts; ranked feature-gain tables; per-broker score and crossing diagnostics; every failed hour CSV; full stdout. All file hashes in `COMPLETE_ARTIFACT_SHA256_MANIFEST.json`. Original authorized monthly raw tick files, original R00-054 model ZIPs, archived R9 benchmark and original prior research artifacts remain externally referenced at their immutable original paths, NOT duplicated.
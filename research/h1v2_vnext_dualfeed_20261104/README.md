# H1V2 VNext — source-ordinal dual-feed causal entry research (2026-11-04)

**Research only.** This is a new additive Python entry/exit experiment, **not** a modified R9 EA, profitable trading claim, MetaTrader integration, licensed dealer fill, or blind OOS. All eight source months Jan/Feb/Jun/Jul 2026 have already been inspected in prior research and are contaminated for genuine blind OOS. Historical source risk/operations/news availability are UNKNOWN.

## Frozen source ancestry and locations

- Base GitHub commit: `f439e870cc7f1abaeb47aa2172140c424e31c05f` from `carson/h1v2-r23h7-broker-session-ordinal-hazards-20261104`. Original code is not overwritten.
- Original exact first-passage engine: `research/h1v2_r23_hourly_causal_20261104/frozen_r24_archive/source/r24_firstpass_engine.py`; sourced from full 72-member archived R24 ZIP SHA256 `1afb2d42244aa911c580148ff7cfe349a674e28e5c36e7ed328dfec329af0e84`, CRC PASS. New code imports `build_tree` and `first_crossing`, rather than rebuilding them.
- Full 2026 raw Dukascopy and Coinexx-linked MT5 source months MUST be independently SHA-verified before replay. Seven of the eight MT5/Dukas source receipts are in `src/vnext.py` literal SHA table, with eight total original hashes. They are original source data, not deliverables intended for a public git repository.
- Original complete R9 SYNTH *UTC-aligned* quarter quota comes from the original R23 DUKAS 4month result ZIP, the `A1_TP050_STOP100_H60_CAP4000_Q8` scenario **only for R9 reference mapping**, not as future-trade selection or a model feature. Expected month sums `[27980,33523,31758,24324]` and 11,520 full quarter rows; 7,521 reference-active quarters, 1,917 active hours per source.
- MT5 exporter `time_msc` is corrected by original historic convention UTC offset +02h Jan/Feb and +03h Jun/Jul. June source tail uses July broker file with explicit >15s quote gap and +60s halo. Historical dealer offset is not independently confirmed live here; source clock contract is identical to original R24 reconstruction.

## Three competing creative mechanisms — predeclared; not post-selected

1. **C1 — BROKER-SCALED STRUCTURAL RECLAIM:** 15s alignment against 60s/300s trend, 3s counter-pullback, 300s continuous quote freshness, source-specific spread-relative signal amplitude, endogenous adverse stop and TP, 30s MT5 or 60s Dukascopy *time-to-exit maximum* (NOT required full H minhold). Need nonzero net reward under actual bid/ask liquidation, not simply an attractive signal.
2. **C2 — DUAL-BIDASK IMPULSE:** concordant 3/15/60-second exact prefix-only directional movement, source-relative spread and bid/ask leadership, event-rate gate, regime-normalized TP/STOP, 30/90s dynamic horizon.
3. **C3 — MULTI-AXIS HYDRA:** compare the as-of scores of C1, C2 and 900s/3600s HTF-aligned trend continuity lane; choose best only if a *historically blind* prefix-score threshold is met, otherwise WAIT. Broker-conditional quote cap, market quote intensity–dependent horizon 15/30/90s and spread + realized past-motion standardized barriers.

**Important:** These are hypothesis generators, not trained LightGBM models. Thresholds are predeclared manual research parameters. No optimization/training advantage is claimed. No future-knowledge teacher filtering or R9 quota enters the side/horizon/WAIT decisions. First positive results need model fitting with time-frozen calibration, negative control and truly unseen OOS.

## Execution and evidence contract

Raw full observed Bid/Ask quote ordinals sorted by UTC ms, never invent a quote or use next-same-millisecond ordinal for feature calculation. Eligible first-observed 1-second quote after >15s source gap and complete 300s fresh history, source-specific decision spread cap $8 Dukascopy/$4 MT5. Entry fill at **first truly observed quote at/after signal+100ms**, with at most 1000ms staleness and first-observed fill spread cap; reject otherwise. BUY ask entry → bid exit, SELL bid entry → ask exit, fee .02 source quoted price, explicit additional each-leg slippage optional. First TP/STOP crossing reuses original R24 segment-tree primitive. Enforce one position and actual exit quote across UTC quarter/hour/day. Gap >15s is censored/unknown; restart after fresh source epoch is an **optimistic research assumption**, NOT a certified broker-flat state. Label every admission TARGET_FIRST, STOP_FIRST, TIMEOUT, CENSORED, UNFILLED; retain negative results, WAIT and 0-reference periods.

Original R9 SYNTH target is a benchmark only. Count *completed* actual source quote fills per UTC quarter/hour/day against original exact reference. Full quarter/hour/day and month result CSV plus all source signal/fill/exit ordinal trace NPZ are written for every independent source-month-cycle; daily and monthly accounting cannot mask hourly/quarter precision. Correctness numerator = TP first, denominator = TP first + STOP first + timeout (all completed exits; no censored/unfilled or WAIT credited). Strict joint pass requires completed_count >= R9 exact source reference AND >=80% target-first completed precision. Source `net_quote_raw_sum` = total realized liquidation quote price minus fee; raw unit .001 XAUUSD; **not broker $ or cash net**. If later route has a larger stop and negative expectancy, no strategy is approved.

Run from a cloned repo with Python 3.11+ numpy,pandas,numba,pytest and source `.csv.gz` data present under `H1V2_VNEXT_DATA_ROOT` (default `/mnt/data`), R23 original complete quota ZIP in same folder, and original frozen R24 first-passage module in the parent research folder. For local standalone artifact testing, extract only `source/r24_firstpass_engine.py` from the original R24 archive into `/mnt/data/h1v2_vnext/frozen_r24/source/` and SHA-verify original zip before use.

```sh
python -m pytest -q research/h1v2_vnext_dualfeed_20261104/tests
python -m compileall -q research/h1v2_vnext_dualfeed_20261104/src
python research/h1v2_vnext_dualfeed_20261104/src/vnext.py --source DUKASCOPY_RAW --month 01
python research/h1v2_vnext_dualfeed_20261104/src/vnext.py --source MT5_BROKER_EXPORT --month 01
# Repeat each source and months 02,06,07, one source-month at a time.
```

Do **not** rerun old R23H7 negatives, S7 E00–E11 already completed, or mark this research a valid causal-trading edge until model evaluation confirms both target quality and executed broker economics across complete per-source original UTC calendars. Proven history includes full 60s hold mathematical bottleneck (3010/7521 quarter and 665/1917 hour conditional full-R9-volume+80%-held-success impossible), which DOES NOT apply to current horizon-*maximum* first-TP exits.

## Recovery and stop conditions

MT5_EXPAND lab folder: https://drive.google.com/drive/folders/1uLg9BJcGN4FCtgTKKg76T0Zyt2OV98me

Append-only Drive journal: https://docs.google.com/document/d/1qPzKQkrfY6zawdfzOrd868tYs3HZMEoO_qQTwEFoiQA/edit

Original audit V06 index: https://docs.google.com/document/d/14RX77MER6XIPKfSaHfWs8kybl9AmjQ0rjbdDPfTT8Ls/edit

Each completed source×month×cycle has exact `RESEARCH_RECEIPT.json`, full 15m/hour/day/month rows and raw ordinal trace. In any timeout restart from its last source-month atomic receipt; never rewrite prior historical negative results or change risk assumptions under the same experiment identifier. **Stop** on source/ZIP hash drift, impossible quote ordinal, reference calendar mismatch, source tick disorder, training leakage, missing original full source, source time gap with unknown position resolution, or CI/test failures.

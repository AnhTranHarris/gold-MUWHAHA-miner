# XAUUSD HTF R04 — Cost-Aware Lifecycle / Original Experiment Provenance

**Study ID:** XAU-HTF-20261016-R04-COST-AWARE-MULTIREGIME  
**Status:** RESEARCH_ONLY / NOT_PROMOTED / TRADING_OFF  
**Ancestor:** `carson/htf-six-specialist-discovery-r03` @ `5109546c75bc7151a5e1bdfd953020b7982eca3c`  
**Verified R04 engineering predecessor:** `9d6b7731aa51cb0af6ed84312151b623bc1297e2`, successful GitHub Actions regression run 38983349790.

## Immutable original experiment package

MT5_EXPAND / 04_EXPERIMENT_RESULTS_AND_VALIDATION:  
https://drive.google.com/file/d/1MvXmNKFw_qHVL6ztjKd0BuNbvLapxbMt/view

- **Archive file:** XAUUSD_HTF_R04_Cost_Aware_Multi_Regime_Research.zip
- **Byte count:** 459788
- **Archive SHA-256:** `9d9289f5a8ede31a7140ca0b245528bedfcf5bd21416ca774e732b185c8b9ddf`
- **File count:** 44
- **Verification:** uploaded using MT5_EXPAND account; fetched back; SHA-256 match; ZIP CRC pass.
- Contains original Python Numba replay research, LightGBM model and research scripts, all 180 native-tick training candidates, 120 quote-markout diagnostics, 30 completed fixed-latency tick execution scenarios, per-trade ledgers and complete internal SHA manifest. One Dukascopy February full execution subtask was interrupted; do not invent its result.
- Original four source tapes remain read-only in PRIMARY Drive: Coinexx Jan/Feb, Dukascopy Jan/Feb, using the immutable registered names/hashes and Coinexx -120 minute UTC correction.

## New versioned engineering capability

- `htf_ticklab/engine.py`: accepted source-compatible update with non-relaxing protective-stop modification, requested on current tick, executed no sooner than later eligible quote plus modeled latency; broker level checked at acknowledgement; stale close and stop modifications are bound to the originating funded position sequence and canceled when that position exits; original entry-specialist identity retained.
- `htf_ticklab/economic_exit.py`: new opt-in `CostAwareLifecycle` wrapper around `SharedSignalArbiter`, calculating prospective *quote-side* net after commissions and modeled exit slippage before trailing; specialist-specific max hold and ATR-aware non-backward stop logic. Requires executable broker stop geometry at later quote. No live account order code.
- `tests/test_economic_exit.py`: causal positive-long/short trail, latency acknowledgement, broker stop-distance rejection, stale stop prevention and max-hold regression.
- The prior single-position no-trade baseline, source allowlist and original R9 reference remain unchanged.

## Measured research, distinguished by execution level

In the January 13–30 Coinexx *hypothetical* 30s quote-side markout study, January2–12-trained entry-quality classifier threshold .55, minimum 5 seconds between proposals yielded 219 selected events, +164.85 summed USD after assumed costs. This is not an executed trade ledger.

In separate later-tick, explicit stop/target/latency replay, the comparable Coinexx group with $100 seed, 2.0-price-unit protective stop, 4.0 target and 45s max hold yielded **121 completed simulated round trips, +$2.78, maximum marked drawdown $34.40**. Signal selection and exit geometry were explored against already inspected data. It is NOT a full-EA success: throughput is far below R9 benchmark, drawdown breaches capital preservation intent, and a January-frozen model did not transfer positively to February. Dukascopy at threshold .55 yielded no accepted opportunity. No investor certification or broad robust positive edge exists. Zero-trade cells are not scored as success.

## Next optimization work

Optimize a **shared-funded** R04 six-specialist signal/exit system jointly across cost, quote-activity states, RSI kinetics, ATR regimes, causal Fibonacci geometry, QWAP acceptance, S1/S5 quote flow, specialist exits, opposite-side rearming, and quote-availability. Use a Pareto multiobjective optimizer prioritizing actual feasible positive after-cost trade throughput **and** $100/$200 capital protection. Archive every candidate and accepted improvement in monthly Google Drive research. For scored comparison: one integrated S vs one integrated S' in each independent broker, $100/$200 and 0/250/1000ms, cumulative January through July; full P&L, gross loss, minute/hour/day/week/month, full marked equity and margin, and exact SHA-pinned original source. No calendar month hardcoded live routing. No MQL5/live deployment until Python whole-EA acceptance and owner authorization.

Do not describe this archive pointer or a passing code test as evidence of profitable trading.

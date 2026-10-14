# GRID0300–0306 | January 2026 original Dukascopy tick-level hourly-risk research
**Date:** 2026-10-14. **Status:** RESEARCH-ONLY, NOT ACCEPTED, NOT PROMOTED. Owner QC pending; official J0183 unchanged.

## Governing authority — original sources (NOT superseded)
- Full V1 whitepaper: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/delta-A-alpha/research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt
- Full ratified owner conversation: https://docs.google.com/document/d/1J9d_P4ooCnNmcxPwG1F178aE4ktpkLrFclcyQPaJ8k/edit
- Full unabridged January–July roadmap: https://docs.google.com/document/d/1PcaksxuiayFXVW3QtKfzitARvQj6NyL4IIbGhG8K9z4/edit
- Binding anti-summary law: https://docs.google.com/document/d/1eG5F76uvm9M-1JXs4LvAaTzPEurU5l4Pgj2sUUelc1o/edit
- January read-first source/QC law: https://docs.google.com/document/d/15psoEliXaPEXJr22cKlJb4OGmWo26j3Eu8GlTtH26Kw/edit
- Owner Dukascopy/R9 roles: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/delta-A-alpha/research/delta_a_alpha/governance/OWNER_20261013_VERBATIM_DUKASCOPY_TICK_CANDLES_R9_REFERENCE_LOCK.md
- Latest original prior GRID0293–0299 archive: https://drive.google.com/file/d/1NDa5PQIMuCM0e4RBdAUQsCOYdPyRyB_l/view

## Locked test contract
- XAUUSD Jan **9,135,062 original ordered UTC Bid/Ask ticks** in `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz`, original SHA-256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`. Do not substitute another feed, midpoint, synthetic candles or hypothetical spread for execution.
- Preserved GRID0297 parent192 fully funded *modeled* Watchdog source and GRID0291 online per-source loss-pause/NY16 cap. Original code/helper bytes remain unchanged.
- Research model: fixed **0.01 lot = 1 oz**, hypothetical **$100,000** starting cash, 500:1 hypothetical margin, **$0.20** modeled roundtrip, **250ms** to first executable subsequent quote, one market entry per original quote tick, one shared portfolio, no Martingale, no future markout in the entry decision.
- R9 SYNTH reference **+$41,520.82 / 27,980 completed January**, plus 21 date-matched daily and five ISO-week cash/velocity/risk target ledgers. R9 OVERFIT remains offline teacher only; **all six 75% dimensions NOT MEASURED**.
- `MAX_HOURLY_DD`: each UTC hour starts a new equity peak; observe every original Bid/Ask tick, and calculate the maximum `peak equity minus later equity` within that hour. Daily outcome: maximum of that day's 24 hourly drawdowns. Both realized cash and open float enter equity. A new-entry lock CANNOT close existing risk or enforce a hard stop; results always show observed overshoot. No month/date/performance-reference label is a runtime input.
- Research test profile `G0256_G2224_PARENT_PRESSURE400`: original source `coverage_gc0` cap 256, `coverage_gc2` cap 224, previously proved NY16/source loss pause and paid WD, and **as-of pressure at USD 400 within UTC hour** reduces new WD parent capacity to 64. Original parent earn-before-renewal and shared global cap remain.

## New units / distinct research developments
- GRID0300: integrate quote-by-quote **as-of hourly equity marking** with event-exact scheduled original quote closes, current open book, immediate spread mark on fills; gated current-hour new entry and a softer funded parent pressure cap. The hard lock 150/300/600 often substantially lowered profit or failed January monthly net despite DD reduction. Several locked cases still exceeded nominal DD threshold due already-open positions. No claim of guaranteed cap.
- GRID0301: combine hour-entry lock at wider thresholds (900/1500/2400), soft parent thresholds (50/100/200/400/800/1200), different parent pressure caps. Broad period acceptance remains unachieved; entry locks tend to suppress profitable volume.
- GRID0302: independent vectorized/Numba reconstruction of the **same original quote-equity path** from just observed funded entry/exit indices and prices. Source-level adverse-hour diagnosis found 254 live `coverage_gc2` positions in worst 2026-01-26 16:00 UTC window and 227 `coverage_gc0` positions in the prior 15:00 window. Source inventories—not the already capped WD parent population—were the new limiting risk mechanism.
- GRID0303: **source-specific physical concurrency caps** (gc0, gc2 individually and jointly), preserving the existing owner-frozen L0–L7 layering. Broad simultaneous caps reduce needed cash opportunities, but *source-specific* caps plus parent hourly pressure improve worst-hour DD while maintaining positive month/day/week cash.
- GRID0304: 36 combinations of gc0/gc2 caps and hourly parent pressure, all full original tick portfolio replays. Produce non-dominated in-sample profit/worst-hour-DD Pareto frontier without a calendar rule. Exact per-variant daily+weekly outcome, gross losses, tick DD and immutable source metadata in attached JSON.
- GRID0305: **64 independently passing source and read-only outcome QC assertions**, including original tick hash, chronological Bid/Ask, exact every-trade settled fee, one-entry-per-tick, ledger daily/week cash reconciliation, and independent all-quote hourly floating DD for two Pareto candidates plus a 300 cash risk diagnostic.
- GRID0306: independently repeated original-tick capital scenario $100/$200/$300/$500 at unchanged 0.01 lot and fixed original portfolio logic; $100/$200/$300 tests show material initial equity depletion, so **small-account survivability NOT CERTIFIED** even when historical monthly net is positive. See JSON for exact stress results.

## Empirical measured results — same ORIGINAL source / January, no acceptance

| Case | Month net | Completed | Profitable days | Profitable weeks | R9 same-day net hits | R9 same-week net hits | Gross loss | Max UTC-hour floating DD | Full-tick equity DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Frozen previous GRID0297 parent192 reference | +$53,391.28 | 7,659 | 21/21 | 5/5 | 9/21 | 4/5 | -$3,024.50 | $8,140.74* | $8,140.74 |
| GRID0304 **risk-minimized** gc0=216/gc2=216/parentPressure400 | +$42,611.78 | 6,835 | 21/21 | 5/5 | 8/21 | 3/5 | -$2,996.52 | $3,394.75 | $4,886.85 |
| GRID0304 **balanced research** gc0=256/gc2=224/parentPressure400 | +$46,574.51 | 7,378 | 21/21 | 5/5 | 8/21 | 3/5 | -$3,035.63 | $3,554.71 | $5,046.81 |

*The $8,140.74 historical baseline max whole-tick DD is also the intra-UTC-hour drawdown reproduced by GRID0300 with the identical source population. Improvement of the balanced version on maximum hourly DD: **56.33%**, at the cost of lower net and fewer trades.*

**Selection:** prefer the balanced GRID0304 `G0256_G2224_PARENT_PRESSURE400` as a **candidate for further research only** because it preserves more monthly profit margin: modeled +$5,053.69 above the R9 SYNTH month-net reference. The smaller gc216/gc216 variant has less DD but only +$1,090.96 monthly net margin before any realistic additional slippage/spread/broker divergence. **Neither passes January source/owner QC or R9 per-day/per-week/trade-volume gates.**

### Critical January unsolved gap
- W01 / 2026-01-02 remains **+$896.705 / 75 completed** against original R9 SYNTH **+$1,027.95 / 1,083**. Coverage source parent streams still fail to reconstruct high-velocity early-Jan trading; this requires new ORIGINAL reconstructible as-of mechanism(s), not further parent-cap tuning.
- Above balanced profile matches **8/21 individual R9 daily net targets, 3/5 weekly net targets**, and **7,378/27,980** monthly velocity. No R9 OVERFIT 75% scoring and no original Jan–Jul one-engine cumulative integration.
- Original historical candidate-source population was preselected in earlier GRID0272/0276 research. Current causal funding/admission and real-tick settlement **do not fully regenerate** candidate opportunities endogenously in `FourSessionV1`. Therefore this is **NOT a complete leak-free independent source generator nor forward demonstration**.
- No brokerage slippage/fees/contract/margin certification; positive results from hypothetical 100k do not prove $100–$300 deployment. Risk rules require owner-approved comparisons and month-blind forward regression before promotion; no production code touched.

## Community research, reconstruction ideas only (not empirical strategy validation)
- MQL5 exact intra-hour/equity drawdown governor concept: https://www.mql5.com/en/articles/23732 and https://www.mql5.com/en/articles/22833
- MQL5 volatility and grid adverse exposure; important limit of triangular loss formula: https://www.mql5.com/en/articles/21833
- Chinese FMZ reconstructible dynamic gold grid triple regime controls: https://www.fmz.com/strategy/530403; existing oscillator/grid source logic still not validated on our original XAUUSD Jan ticks.
- Chinese FMZ dynamic movable grid: https://www.fmz.com/strategy/540533
- ForexFactory community documented MT5 grid intra-bar drawdown/stop-out discrepancy: https://www.forexfactory.com/thread/post/15835327
- Reddit practitioner as-of multi-strategy risk budgeting and real-time floating-equity marks: https://www.reddit.com/r/algotrading/comments/1rtwnfm/approaches_to_risk_management_and_order_size/

## Exact reproduction and required archive
Unzip the attached ZIP into `/mnt/data` while preserving `jan_continuation_20261013/` and `jan_recovery_20261013/` original directory names. Place the exact original January Dukascopy source `.gz` separately at `/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz` and verify SHA. The ZIP contains **unchanged complete predecessor source archives** plus new source scripts, full JSON results and independent QC source. Original tick gzip (68,690,420 bytes) is not duplicated.

```bash
export OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=4
python /mnt/data/jan_continuation_20261013/grid0300_hourly_equity_governor.py
python /mnt/data/jan_continuation_20261013/grid0301_hourly_pressure_frontier.py
python /mnt/data/jan_continuation_20261013/grid0302_hourly_source_attribution.py
python /mnt/data/jan_continuation_20261013/grid0303_causal_coverage_source_caps.py
python /mnt/data/jan_continuation_20261013/grid0304_coverage_hourly_pareto_refinement.py
python /mnt/data/jan_continuation_20261013/grid0305_hourly_independent_acceptance_qc.py
python /mnt/data/jan_continuation_20261013/grid0306_low_capital_survivability_diagnostic.py
```

**Owner decision:** `PENDING`. Not integrated; not accepted; scientific cursor `J0183` unchanged, trading OFF, August SEALED. Future research must preserve this checkpoint, the full original sources and all failures, and prioritize true early-month source density + overall hour-level risk and cash consistency without dates/oracle teacher as features.


---
### Exact originals and durable cross-references
- Unmodified original source / full JSON trade-day-week-hour results / 64-pass independent QC archive: https://drive.google.com/file/d/15CEC7m5sil3hdwhzZowmyZ99d8-nxZfT/view
- Exact research archive SHA-256: `60295a03f9f4e2d954229f92d3f0ad7ca5992a625c9879e689ac7c5dd32b7717`
- Google Drive same full report: https://drive.google.com/file/d/19iDex6wd6o0DB-Mxkh_N98wpUzNN-vLI/view
- Original newly written Python research source: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/tree/delta-A-alpha/research/delta_a_alpha/monthly_progressive_roadmap_20261013/2026-01_JANUARY/experiments/GRID0300_0306_SOURCE_CODE
- Original prior GRID0293–0299 source remains protected. Active FourSessionV1 and J0183 were not promoted or modified.

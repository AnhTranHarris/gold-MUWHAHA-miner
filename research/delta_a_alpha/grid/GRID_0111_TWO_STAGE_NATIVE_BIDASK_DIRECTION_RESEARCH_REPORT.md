# GRID0111 — Reproducible Original-Quote Two-Stage Causal Side Election (research only)

2026-10-10 Chicago | Gold MUWHAHA delta-A-alpha | Parent J0109, J0110 handoff-only; preregistration GitHub commit 05f0d9f564d948417c3bc9123f593ebeaee69c4d. No funded trades or MT5 EA changes.

## Scope, original scientific baselines and explicit non-promotion

Frozen GRID0108 grid_event_economic_geometry.event_scan, real original Jan-Jul Dukascopy Bid/Ask quotes (57,527,562), fresh per-month source-native replay using the preserved event geometry: gap=max(0.75,1.5*causal spread EWMA alpha=.001), 7s cooldown; original as-of K5 has K2>=2 broad/K4>=4 nested thresholds, with byte-identical original raw source preserved. Script uses the original K5 floating price computations to reproduce all seven official raw K2/K4 monthly counts. T0 crossing only creates a virtual candidate; T1 is a later source quote. No sessions, HTF, L1-L7, physical orders, R9 strategies, Martingale or August.

Seven-month baseline GRID0108 demonstrated an UNSIGNED future movement lift on 150/150 eligible weekdays and 1943/3332 eligible hours, not a causal sign edge. Retain its entire original logic. The new GRID0111 prospective sign candidates do not transform the previous unsigned result into profit.

## Result: all 23 predeclared method/tier/threshold variants negative at every 30/120/600 second pooled horizon; no scientifically promotable sign selector.

All 23 strategies were evaluated over all seven months: 161 method-months, three fixed markout horizons, nine local tests passed. No candidate had positive seven-month weighted mean or a positive-mean month at the tested horizons. All fixed-quote-side calculations enter BUY at Ask, SELL at Bid, mark at future opposite quote side and deduct hypothetical 0.02 USD roundtrip once. This is an offline fixed-horizon source quote markout, NOT realized PnL or broker execution. Full failures preserved in monthly JSON and method aggregate CSV.

| Month | Original ticks | Raw grid crossings | K2 | K4 | K2 Race T1 f40 | K2 Race 120s avg $ | K4 Race 120s avg $ | Failed escape then reclaim 120s avg $ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
01 | 9,135,062 | 55,732 | 42,782 | 31,674 | 40,192 | -0.7956 | -0.7940 | -0.8190 |
02 | 7,538,339 | 53,958 | 41,233 | 30,190 | 38,614 | -1.0787 | -1.0834 | -1.0921 |
03 | 9,433,179 | 79,343 | 63,870 | 49,826 | 61,719 | -0.8277 | -0.8119 | -0.7908 |
04 | 7,470,570 | 51,781 | 38,774 | 27,536 | 36,004 | -0.7578 | -0.7501 | -0.6948 |
05 | 8,333,165 | 51,402 | 39,185 | 28,345 | 36,511 | -0.6386 | -0.6447 | -0.5955 |
06 | 8,201,406 | 57,277 | 43,510 | 31,838 | 40,879 | -0.6230 | -0.6189 | -0.6079 |
07 | 7,415,841 | 40,952 | 28,593 | 18,723 | 25,567 | -0.6926 | -0.7083 | -0.6732 |


## Best relative (but still failing) horizons — not selected models

| Horizon | Lowest-loss among tested methods (post-hoc rank only) | Valid T1 quote tests | Weighted after-cost mean $ per 1oz quote-path | Months positive |
|---|---|---:|---:|---:|
| 30s | K2_CONT_F200 | 221,358 | -0.7756 | 0/7 |
| 120s | K4_RECLAIM_F200 | 166,761 | -0.7566 | 0/7 |
| 600s | K2_RECLAIM_F200 | 223,442 | -0.7305 | 0/7 |

K2_RACE_F400 has 279486 unique raw two-stage T1 events over seven months, with 3300 of the fixed 3332 eligible UTC hours supported by >=5 quote-valid 120s events, but only 60 UTC hours with positive signed average; 32 baseline hours unsupported. Raw event count is NOT a qualified same-day trade gate, nor could a standalone layer make such a funded trade claim.

Note original K2 and K4 totals in this run: 297947 and 218132. Controls match the frozen original monthly event supply.

## Reproducible execution/label design

1. Original GRID0108 event_scan emits immutable T0 at observed quote, original sign and causal EWMA gap. Original read_raw preserves int64 timestamp in ms UTC and native Bid/Ask scaled 1000. For K5 denominator use original event calculations (bid/1000+ask/1000)/2 and ask/1000-bid/1000 to preserve source boundary values. First quote before T0-300s is found with searchsorted right minus one; events before full 300s use original known first-quote bootstrap, not future values.

2. Each predeclared event has two virtual sign hypotheses. T1 on observed subsequent quote only: Continuation crossing f*gap, counter-cross/reclaim f*gap, first-response race; and an explicit failed-escape first then reclaim state. Fractions 0.20, 0.40, 0.65; first signal deadline 15s and failed-escape 30s. 250/1000ms drift controls. Duplicate same-T1 quote collisions retain the earlier T0.

3. Mark 30/120/600s from actual T1. Select first quote at or after horizon, reject if more than 10s late. BUY quote markout=(future Bid-current Ask)/1000-.02; SELL=(current Bid-future Ask)/1000-.02. No midpoint fill or double subtraction of spread; no broker slippage in primary numbers. Separate extra .10/.25 hypothetical slippage and T1+250/1000ms delayed source quote sensitivity in monthly JSON; nontrading sensitivity.

4. Offline first-passage +$1 favorable vs -$1 wrong-way 120sec barrier measured with ordered executable quote sides after entry and fee, never used to select T1. The reported first-passage event counts and delayed markouts are included for K2/K4 race f40 per month. No position holding, stop/TP, profit factor, equity/drawdown, physical liquidation or MT5 performance simulated.

5. Full frozen 3332 eligible original UTC weekday hours are preserved as explicit rows for every variant, including unsupported and negative signed hours; complete per-month hours CSVs and observed UTC days CSVs included. Claimed May-Jul OOS: NONE; all seven original months previously inspected; August sealed. No valid truly unseen certification sample.

## Why not promote / next creative hypotheses, distinct roles

The first post-crossing directional response generally occurs while the immediate quote friction remains significant; mechanistic state transitions of this kind alone did not overcome all-in quote costs. The negative 30s/120s/600s outcomes persisted even across simpler vs compound escape/reclaim variants, so changing only those response thresholds is low priority. The source exchange/quote feed does not expose a reliable centralized XAUUSD market-by-order queue; cannot invent order-book imbalance.

Next research direction, **HYPOTHESIS ONLY, not tested here**: cost-recovery-first grid admission using actual quote-side break-even frontier and rate of net progress at T1 (rather than only midpoint gap); inventory-free virtual rung persistence/unique-cell first touch and failed reclaim; bounded quote freshness; cross-scale endogenous grid-state trajectory (2s/10s/60s price pressure, NO sessions/time-clock routing), with enter-or-abstain calibrated to preserve all-hour and daily supply. Explicitly study whether waiting for a successful side-correct provisional recovery state improves net markout or merely purchases old favorable displacement at a worse quote. New structured feature family requires a separate pre-registration and source-native test, not a stealth mutation of this experiment. If consistently negative, deeper structural context likely needed, but owner has not yet authorized unlocking L1.

## Related reconstructible public inspiration and limitations

- Creator grid source: https://github.com/MegaJoctan/omegafx-youtube-shared-files/tree/main/Python%20Grid%20Bot — only virtual opportunity ancestry, no no-stop inventory or sizing.

- Chinese MQL5 retest-with-confirmation state machine: https://www.mql5.com/zh/articles/18486 — uses opening-range sessions in its example; do NOT import session clock as a strategy variable at pre-L1, only translate later-quote confirmation state concept.

- Japanese MQL5 failed-breakout reversal: https://www.mql5.com/ja/articles/18259 — quoted educational mechanism, no XAUUSD edge certification.

- Open-source TradingView boundary failure and retest state: https://www.tradingview.com/script/ZUAYemgd-Supply-and-Demand-Zones-Flux-Charts/ — concepts only, no full order book or verified profitability.

- Reddit backtest spread concern: https://www.reddit.com/r/algotrading/comments/1fxtvhv/ — community discussion of avoiding optimistic midpoint fills, anecdotal research context.

## Immutable governance and durable assets

Same branch delta-A-alpha only; current accepted GRID0104+K2/K4 baseline unchanged; last completed science J0109 until J0111 research artifacts and machine state synchronously promoted; no MT5 build. This artifact is reproducible in source bundle: grid0111_two_stage.py, test_grid0111.py, GRID0111_PREREG.md, original frozen GRID0108 ancestor code, 7 per-month complete JSON, 7 hourly CSV, 7 daily CSV, complete aggregate CSV, log, and SHA256 manifest. The bundle intentionally does NOT copy the enormous source ticks, which remain protected in the original Google Drive/Project sources; no August.

## Permanent source/evidence URLs
- Complete raw-code/test/month-hour-day ZIP (SHA256 3b17d810c88f6853e922feb9028beb2aa8b161d933f6152b8a541bc7f1f324b3): https://drive.google.com/file/d/1hvw_Dr5x3hO5sOzTHPPbxbFJDhKBnv5B/view
- Readable Drive research report: https://drive.google.com/file/d/1fdEjryegXSighJRtxiAOOuzMIXOo7gRD/view
- Pre-registered original study on same branch: research/delta_a_alpha/grid/GRID_0111_GRID_NATIVE_TWO_STAGE_DIRECTION_PREREG_20261010.md

# R9 v1.93 Hourly Profitability, Execution, Portfolio Risk Audit
Date: 2026-11-13. READ-ONLY source audit. No EA source modification or live-trading authorization.

## Source pins
Experimental v1.93 base HEAD: d5bde60f55992cd8799bed85bba68efedbf9aff2.
EA source blob: ac8b45b5483268c940402d8963fb63970b19b75d.
Governor source blob: 7e457e1ad5b3a39038a3556857307e193f6248ef.
M1 indicator source blob: cedba0205d198e8f9fb63b67137fd09b111a4be2.
Cash geometry source blob: e4474b60a2febc1c30dfa365454462cde4585bf6.
Protected-by-policy critical rollback v1.90 original commit: 8729a6345655a7b4ea31facc81982004ee2b8921.
All work exclusively uses Coinexx historical Bid/Ask and quote timestamps, NEVER Dukascopy.
MT5_EXPAND historical audit workbook: https://docs.google.com/spreadsheets/d/1qgbADLGVuvf6K-XICsUdfeLVVhd31zZk/edit
Causal 60s quote first-passage research: https://drive.google.com/file/d/1FbwO3lj6RWBKMLcGwggnmUqH_Hdc5UgQ/view
237-feature training audit: https://drive.google.com/file/d/1iZoV2Hp0enANtux-LDLMHpuBQIneqUeo/view

## Verified historical performance: NOT v1.93
The older v1.90 SYNTHETIC MT5 M1 Jan-Sep workbook reports 272,352 completed trades, 192 active dates, 4,361 active hour/date intervals, total net USD 360,693.05, average net USD1.32436 per trade, net USD82.70879 per active hour, win rate 86.6816%, average hold 17.2413 seconds. Thirteen trades held beyond 30 seconds; max hold 176,426 seconds (~49 hours). This is synthetic tester performance, not real-tick or funded certification. No v1.93 hour-by-hour trade ledger or fully verified compilation exists.

All 23 broker-clock-hour aggregate buckets with actual trades have POSITIVE summed net PnL over all historic dates. This does NOT imply each of the 4,361 actual hour/date instances was profitable. The workbook does not directly list the sign of every individual hour/date PnL interval. Entry-hour buckets, not future-exit buckets, are appropriate for causal scheduling.
Entry hour, count, net USD/trade: 06 9,282 0.95487; 07 8,136 1.00546; 12 10,771 1.06093; 13 9,835 1.10348; 15 15,355 1.49632; 16 17,253 1.75106; 17 17,204 1.75443; 01 8,730 1.74708; 23 5,902 1.17109. 23h entry cohort mean hold 52s due unusual overnight exposure.
By month avg USD/trade: Jan 1.484, Feb 1.975, Mar 1.847, Apr 1.208, May 1.022, Jun 1.112, Jul 0.913, Aug 1.001, Sep 0.954. The broad deterioration from February/March to July/September warrants conditional market regime diagnosis; do not simply exclude hours based on development-exposed data.
Stop-coded exit group n=247,411, avg net USD1.26243, avg hold 15.197s; timeout/other n=24,941, avg net USD1.93869, avg hold 37.515s including outliers. Stop-coded exits include winning trailing stops: the label is not loss classification.

## Source-level findings — ranked
P0: The previously trained high 5-second ROC-AUC model is NOT in v1.93 trade routing. Entry is still minute bracket + M5 ATR + completed S1 quality. Rescue via ADX/EMA M1 is OFF. Cash USD1.75 target is an optional DIAGNOSTIC log OFF by default, not a position TP or optimization policy. Exits still original 0.10 activation, 0.03 trail, nominal 30s timeout. Better AUC therefore cannot yet cause higher traded USD/hour.

P0: Gross-loss governor ON by default, base daily 4% first-observed equity, capped at 12% of daily anchor, +25% gross-profit recycling subject to cap. Consumption equals gross realized losing deals + all negative trading cash charges + negative floating PnL across ALL positions. Entry reserves another projected stop-loss + USD0.25. Halt is sticky for the day. On USD100 start, upper hard cap USD12. Illustration only: 180 losses of USD0.50 would consume USD90 before fees, incompatible with maintaining the old >1,000-trades-per-day tester count. Do NOT solve by lifting hard limits without verified risk capacity. Poor early-hour trades could block the historically strong later-hour 16/17 buckets.

P0: OnTick quote coalescence and synchronous broker trade requests permit missing quote events relative to source-ordinal replay. Risk refresh periodically reselects EVERY deal since broker midnight using HistorySelect; it also refreshes on deal-dirty. This repeated all-day scan scales with deal count and may increase latency and missed entries. No latency/event loss histogram yet. Investigate as testable mechanism, not an observed speed measurement.

P1: Governor keyed by account-login + calendar day in TERMINAL globals, not cross-terminal shared, nor atomic CAS; first-attached EA equity can be the daily anchor rather than actual midnight equity. Separate terminals can independently permit losses. Confirm account mode, broker clock, restart and multi-chart behavior.
P1: OnTradeTransaction handler observes own entry deal only; it is NOT a complete open, partial, closing, reversal, reentry and rejected-fill state machine. Accepted request retcodes still include PLACED, DONE_PARTIAL and NO_CHANGES as if a completed position exists. Fix before demo. First matching magic/symbol position only.
P1: New 1s timer requests 30s closes even without a symbol tick, but closed market, terminal outage, broker rejection and Strategy Tester TimeTradeServer==TimeCurrent cannot guarantee hard <=30 sec. Tester and on-terminal event behavior must be compared.
P1: Trailing stop broker freeze level is not explicitly checked; repeated PositionModify requests compete with OnTick processing. Broker-side SL remains price contingent, not guaranteed exit fill.
P1: Insufficient reason-coded counters for ENTRY vetoes, history failures, margin veto, gross budget denial, no fresh indicator, order retcode and what later happened to refused qualified entry. Thus observed hour PnL is unidentifiable in v1.93 without new compact instrumentation.
P2: Existing M1 ADX/DI/EMA/ATR context is causal using completed bars but relatively slow for 1–5sec quote decisions. Fixed arbitrary score 0.45*DI + 0.35*EMA slope + 0.20*Bid impulse is untrained. If enabled rescue bypasses ALL failures of original completed-second S1 gate rather than an approved subset.
P2: Commission USD0.20 cash assumed for shadow target differs from USD0.25 reserve per trade. Neither is empirically calibrated to broker deal history.

## Existing AUC diagnostics are NOT execution profitability
Coinexx quote-only M60 source contains 72,129,347 raw quote rows, 303,934 R9 entry times. Last, volume, volume_real are ZERO throughout. Baseline 155 features mean pooled five-second AUC .738513, original R9 side .723175 in previously research-exposed May-Sep. 182-capacity model mean pooled .739491, original side .723976. 237 joint feature model pooled .739282, original side .723715; 55 new interactions did not beat capacity-only. NO model directly routes v1.93 trades. No new gross-loss-protected net USD/hour result exists.
Earlier original-R9-time hypothetical fixed +0.50/-0.30 quote barrier test found 103,066/303,934 (33.91%) adverse-first in 1s, 231,131/303,934 (76.05%) adverse-first in 15s, median spread quoted gold $0.20. These labels DO NOT model actual R9 moving trailing stops or cash brokerage; never equate them with actual stop-outs or $ losses.

## Next exact mathematical experiments (not repetitions of old feature sweeps)
A. Hourly real-time monetizable opportunity = expected FILLED trades in next hour times expected NET cash per filled trade, conditional on session, spread, real quote volatility, time since prior trade and account stop risk. Use the full chronological account occupancy ledger, not just favorable hypothetical labels.
B. Competing hazards with TRUE R9 moving stop and deadline: S(t)=exp(-integral(lambda_goal+lambda_stop+lambda_timeout)); target-first cumulative incidence = integral_0^T S(t)*lambda_goal(t)dt. Convert quote-side Bid/Ask fills and exits to validated account currency, all fees included. Estimate goal, stop, timeout as three separate economic outcomes; evaluate first 1,3,5,10,15,30 seconds.
C. Value of WAIT (no more than predeclared 1–3s): max of expected net BUY, expected net SELL, and conditional option to wait net of missed opportunity. New delayed entry must use its NEW Ask/Bid, trailing and account occupancy, not the original candidate future label.
D. Adaptive harvest-versus-runner: choose liquidation now or continuation using remaining trade lifespan and hazard-conditioned expected net cash, including gross loss budget opportunity cost. Trailing distance max(broker stop + tick, alpha*prior spread, beta*prior realized sigma_1s) with training-only frozen constants; broker freeze constraints must be respected. This is more relevant than duplicating 237 old classifier features.
E. Hourly soft risk velocity: expected gross loss in the upcoming hour estimated by block resampling of PRIOR session-matched days, incorporate fees, number of attempts and correlated loss clusters. Allocate risk to conditional utility while respecting the absolute daily and equity hard stops; if target volume exceeds budget, label INFEASIBLE rather than bypass risk.
F. Per-hour and per-session outcome confidence intervals MUST be day-blocked; mixed hourly PnL and win probabilities are nonstationary and may suffer severe in-sample selection. Metrics include gross loss (account), actual time weighted equity exposure, after-cost USD/trade and USD/hour, trade-volume retention, turnover and CVaR 95% of hourly losses.

## Coinexx-only indicator hierarchy
1. TICK-LEVEL QUOTE PROXIES (high-value diagnostic): causal bid/ask spread zscore / spread shock-recovery half-life, quote event-count intensity, two-sided quote revision coordination, realized variance, quote freshness and 1s directional persistence. These are quote events, never actual order flow, executed volume, depth or VPIN.
2. NATIVE MT5 iATR M1/M5 + iStdDev M1 (price variability, stop feasibility); iADX or iADXWilder + DI (trend persistence vs chop); iAMA or iFrAMA on completed M1/M5 (adaptive trend, compare incremental value to existing EMA); iBands width if useful (usually redundant with StdDev). NONE alone predict net price-side fills at 5s.
3. iVolumes(...,VOLUME_TICK) is quote/bar update count, NOT real traded volume. iOBV(VOLUME_TICK) and iMFI(VOLUME_TICK) recycle the same activity proxy and cannot supply missing true volume or L2 quote sizes; lower priority, conditional ablation only.
4. NOT VALID as historical Coinexx indicators: true L2 order-book imbalance, signed trade order-flow imbalance, actual-volume VWAP, VPIN, true depth-based microprice or dealer fills/commission. Only historical Bid/Ask quote sequence is available.

## Validation order, preserving research and storage
1. Extract existing small trade audit and the prior frozen R9 candidate set. First measure clock-hour candidate count, true v1.93 gross-budget/margin veto count, filled count, actual after-cost hourly trade ledger, indicator-ready/fail, MFE/MAE and trailing/timeout reason; count reason codes without writing a full repeated tick file.
2. Implement governor optimization, broker state reconciliation, bracket/stop/time correctness ONLY on a new isolated patch branch with rollback pinned. Source exact replay against existing Coinexx ticklogger only, including equal-millisecond source ordinal. Do NOT regenerate tick archives, multiple gigabytes of features or re-run failed feature families.
3. Compare base v1.90, protected correctness-only EA, conditional hazard quote-side utility, adaptive exits and separately optional indicator rescue. Every group must disclose actual trade retention, USD/hour, gross loss, mean <=30s, tail hold, margin, worst day, max drawdown and stop-gap outcomes. Jan-Sep research-exposed; a truly unseen subsequent Coinexx period required before prospective promotion.
4. MetaEditor compile and Coinexx real-tick MT5 tests were NOT performed in this audit; no executable profitability claim is justified.

## MetaQuotes documentation
https://www.mql5.com/en/docs/event_handlers/ontick
https://www.mql5.com/en/docs/event_handlers/ontimer
https://www.mql5.com/en/docs/dateandtime/timetradeserver
https://www.mql5.com/en/docs/trading/historyselect
https://www.mql5.com/en/docs/trading/ordercalcprofit
https://www.mql5.com/en/docs/trading/ordercalcmargin
https://www.mql5.com/en/docs/indicators
https://www.mql5.com/en/docs/globals

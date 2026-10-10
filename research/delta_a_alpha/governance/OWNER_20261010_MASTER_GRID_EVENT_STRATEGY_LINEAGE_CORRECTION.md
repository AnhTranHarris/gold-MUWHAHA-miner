# Delta-A-alpha — OWNER CORRECTION: MASTER GRID-EVENT OPPORTUNITY GENESIS, NOT R9 SIGNAL REPLICATION
Date: 2026-10-10
Classification: **READ-ONLY ORIGINAL-SOURCE REVIEW AND GOVERNANCE. NO ENGINE CODE PORT, NO NEW TRADING TEST, NO PROMOTION.**

## Owner's latest message (verbatim)
Sorry Carson i stop you mid reply. The reason i ju t realized i did not tell you what htf/scalping master trading stragety it uses that each layer was designed to improve.  

From previous designs of gamma, beta, alpha, and even delta signal generations was all based on a reversed engineered "gold hunter v8" and through various mutations we landed on the r9 gamma hybrid gate which we turned into a mt5 ea. Which is where we get the r9 real data based on the mt5 bactest setting of "every tick based on real tick" and r9 syth mt5 backteat setting "every tick". Please review the gamma branch, and from the chat notes things started to degrade quickly.  From our finding in delta, and delta-alpha we quickly realized that r9 real generated too many unreliable trade signals, (buy/sell) opportunities, when we examined r9 syth and we have difficulty finding metrics for trade entry accuracy and trade direction.  Sometime during the R9-delta research we discovered this YouTube creator prmoting a high accuracy trading bot system, we exmined the grid trading stragety and it yeild better signal and trade direction when we compared it to r9 real, and we decided to drop r9 as a whole path to be closed but we keep r9 syth as what a high perform stragety should perform. 

I am including the youtube link and the transcript for the youtube video 
https://youtu.be/4WQEoQxsJMc?is=6uV0vrr637l5AAjQ

And he even provide a link for his python code at https://github.com/MegaJoctan/omegafx-youtube-shared-files/tree/main/Python%20Grid%20Bot

## Corrected strategy lineage
1. Older **Gold Hunter V8** proprietary behavior inspired a clean-room minute stop/OCO/bracket reconstruction. We do not possess authenticated original Gold Hunter V8 proprietary source.
2. The reconstructed architecture evolved into R9 Gamma HybridGate MT5 EA; existing immutable R9 backtests are the **SYNTH ('Every tick')** and **REAL ('Every tick based on real ticks')** performance references. They are **not** entry-direction ground truth, executable profit guarantees, or a required master generator for the clean V1.
3. Gamma-01 historical experiment added STMR session/MTF grid **as a separate sidecar**, inconsistent with the owner's intended ONE fully integrated vertical opportunity/quality funnel when treated as an ultimate architecture. It is historical only, not an implementation to import.
4. Owner states the strategic R9-origin path was closed and the newer grid-oriented opportunity concept became the intended research basis. Retain R9 SYNTH as **performance target only**; R9 REAL remains diagnostic evidence of REAL/SYNTH divergence. Do not demand matching R9 order directions as the V1 acceptance test.
5. The clean V1 whitepaper, new October owner corrections, and Jan/Feb contaminated research deletion remain binding; historical Gamma, BETA, DELTA and GRID-001 files are archaeology, **not** permissible automatic code, parameters or acceptance metrics.

## Source-exact tutorial mechanism
Creator: Omega J Msigwa (Omegafx) tutorial https://youtu.be/4WQEoQxsJMc
Source repository: https://github.com/MegaJoctan/omegafx-youtube-shared-files/tree/main/Python%20Grid%20Bot
Observed original Git blobs (2026-10-10):
- Python Grid Bot/grid_bot.py: 1d5efa140b363941e7360bd0ae85ac7e04d0ecaa
- Python Grid Bot/grid_bot_backtest.py: 3d4f66a2e57397c15876df795a629488b6278a7c
- Python Grid Bot/grid_bot_optimization.py: fd69caaa878643fcbe26070ae120e213d67b44ff
Mechanism: look back H1 48 bars for rolling high and low. BUY candidate after current price retreats one grid gap below prior high; SELL candidate after rising one gap above prior low. Later same-side placements anchor on most recent opened same-side position, one-gap TP. This is **contrarian geometric event generation**, NOT proven buy/sell directional forecasting. Actual source applies `ticks.ask` to both trigger comparisons; BUY fill uses Ask, SELL uses Bid. Strict causal completed-bar treatment must be rebuilt for any independent faithful approximation.

### Critical source limitations
- Creator's live `grid_bot.py` calls `count_positions(which_mt5.POSITION_TYPE_BUY)` and `last_position(which_mt5.POSITION_TYPE_BUY)` without required `which_mt5` argument, producing a runtime TypeError on that branch. Do not import live script verbatim.
- Grid bar cache updates only when `tick.time % PeriodSeconds(H1) == 0`; sparse ticks need explicit completed-bar rollover rather than equality to exact hour.
- Source H1 `copy_rates_from_pos(...,0,...)` includes current forming bar. Protect against future OHLC pollution if a simulation supplies bar-completed values ahead of event time.
- Creator's backtester runs **US500** using `1 minute OHLC` mode; the optimizer uses the same family and **Optuna maximizes net P/L in-sample**. No source-proven XAUUSD REAL tick execution/direction accuracy.
- No-stop positions store adverse excursion as floating equity loss; backtest code uses **2x loss-dependent Martingale** and can hold many open positions. Both violate current clean V1 hard rules. Video's high closed win rate is NOT 95% predictive entry-direction accuracy.

## Historical project source evidence: forensics, not new accepted clean-model results
[GRID-001 reconstruction](../grid/GRID_001_SOURCE_RECONSTRUCTION.md) already recognized rolling-extreme contrarian grid as a dense event generator.
[GRID-001-F](../grid/GRID_001_F_STAGE_A_REPORT.md) historical **modeled DUKAS_COINEXX_LIKE_P75** experiment yielded 20,678 closes, 98.87% close wins, +$3,755.85 net, **~$20,077.56 equity DD / 250 simultaneous positions**, failing $100-$300 survivability.
[GRID-001-S](../grid/GRID_001_S_STAGE_A_SCREEN_01_REPORT.md) tested 12 bounded variants: all negative; best net -$2,301.82 / PF0.7817. Historical conclusion: **reject no-stop physical averaging grid, explore reconstructible grid CROSSING EVENTS**. Because previous owner explicitly invalidated old Jan/Feb model lineage, these numbers are source archaeology only, NEVER promoted to a clean current performance baseline.
[Gamma-01 STMR ClockFix savepoint](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/carson/r9-gamma-01-stmr-clockfix/docs/R9_GAMMA/GAMMA_01_STMR_MT5_VALIDATED_SAVEPOINT_20261006.md): grid-only historical Coinexx result 2,582 closes, +$579.60, PF~1.205, **31.25% win rate**; far below R9 SYNTH volume and economics. This is not itself evidence of better direction-classification accuracy.
[BETA035 source archaeology](../../BETA_035_GOLD_HUNTER_V8_ORDER_STATE_AND_REAL_SYNTH_FORENSIC.md): same Gold Hunter V8-like reconstructed rules turn out differently on REAL versus SYNTH tick sequences; do not infer the SYNTH reference entries are correct ground-truth directions.
[DELTA003 execution parity](../../delta/DELTA_003_COINEXX_R9_PARITY_REPORT.md): R9 REAL logger exactly reconciled for January (31,915 trades, -$6,651.62 net), and native Dukascopy spread was much wider than Coinexx logger; do not compare feed-specific counts without validating executable broker conditions.

## Mandatory correction to January fidelity audit
**Pause the current audit's objective of mimicking R9 SYNTH's exact entry sign and timestamp.** Revise only after owner review to compare the NEW independently generated grid-event population with:
- R9 benchmark DAILY/hourly trade-count distribution and ≥75% daily qualified opportunity coverage, not signal imitation.
- Price-aligned feed / UTC ↔ server reporting clocks, session and completed HTF geometry.
- Candidate event density (unique per tick/price zone), candidate BUY/SELL mix, after-cost direction quality at predeclared forward executable horizons, compared with opposite action or abstention. Do not call R9's direction a 'correct' target label.
- Shared L3–L7 causal filtering: the role of each layer in correcting bad direction, reducing risk, warning/recovering or cutting failed trades, with true inventory occupancy and small-account feasibility, only after all layers are functioning jointly.
- Detect vs qualify vs feasible order vs actual funded fill, rejected reason, gross loss, full quote-equity DD, max concurrent, latency sensitivity. No profitable conclusion from grid close-win rate.
- Exit/hold optimization remains outside the currently interrupted entry-quality audit.

**Critical: No reconstructed creator-derived trading rule is promoted or wired into the active clean V1 merely by documenting this owner clarification.** The current J0101 prototype and January audit samples are NOT revalidated or approved by this source review.

Full owner-ratified whitepaper: `research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt`.
Full continuing owner chat: https://docs.google.com/document/d/1J9d_P4ooCnNmcxPwG1F178aE4ktpkLrFclcyQPaQJ8k/edit

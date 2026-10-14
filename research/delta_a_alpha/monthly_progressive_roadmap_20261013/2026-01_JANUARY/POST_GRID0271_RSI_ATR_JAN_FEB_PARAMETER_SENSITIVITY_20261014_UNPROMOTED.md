# JAN–FEB ORIGINAL DUKASCOPY RSI/ATR PERIOD SENSITIVITY — R8 MICRO REBASE
Date: 2026-10-14
Branch: delta-A-alpha (existing only).
State: UNPROMOTED / no profitable micro-funded strategy, no MT5 deployment, owner J0183 unchanged, August SEALED.

## User research request
Determine optimal RSI and ATR settings when applying indicators to R8 and R9 and whether a learning RSI/ATR layer can guide high-frequency trades, profit exits and virtual grid spacing without overfitting.

## Scientific answer
No RSI/ATR setting is verified optimal. The earlier January RSI(7)/ATR(14) screens lost money. A fresh exact-source tick sensitivity study varied RSI(5,7,9,14) and ATR(7,14,21) for three separate RSI-source strategies, 7 frozen period pairs, both separately funded $100/$200 accounts and January/February resets (7x3x2x2 = 84 source-locked chronological simulations). **0/84 yielded positive realized monthly net profit**. The former best January R8 source approximation after fee-aware trade exit remained negative ($100 start, -$15.724, 63 closes). Faster RSI creates more raw signals but did not make the funded physical trading profitable.

This is quantitative **sensitivity analysis** (not verified optimizer ranking) based on the same original Python trade simulator and 250ms simulated execution delay. January is already inspected/in-sample; February is a cross-month robustness comparison, NOT untouched final certification.

## Original tick source
- JAN: 9,135,062 original UTC Bid/Ask rows, gzip SHA256 d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5.
- FEB: 7,538,339 original UTC Bid/Ask rows, gzip SHA256 ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d.
- Python: original source `daa_post0271_micro_rsi_atr_research.py` with frozen RSI branches 3,4,5; supplemental source `daa_post0271_rsi_atr_period_sensitivity_20261014.py` computes prior *completed* candle features (Wilder RSI and Wilder ATR) and supplies variant-specific arrays. No future candle, oracle, synthetic MT5 prices, or R9 hindsight execution labels supplied.
- Research assumptions only: starting account $100/$200; fixed 0.01-lot=1oz ASSUMED; 1:500 leverage ASSUMED; actual Dukascopy opposing Bid/Ask modeled fills at first observed quote >=250ms after signal; $0.20 modeled cash roundtrip per trade; physical singleton; 20% cash margin reserve; 2s signal TTL; 5/min cap; 60%-initial-equity new-entry halt (not certified broker stopout). Broker session/contract/fill verification is absent.

## Results: 21 strategy-period combinations per account/month
| Original month / starting cash | Positively profitable configurations | Approx closed trades per simulation | Least losing tested example |
|---|---:|---:|---|
| Jan 2026 / $100 | 0/21 | 24–68 | S5 RSI5/ATR7 reignition, -$37.060, 54 trades, PF0.3735 |
| Jan 2026 / $200 | 0/21 | 55–105 | S5 RSI14/ATR21 exhaustion, -$76.681, 69 trades, PF0.1299 |
| Feb 2026 / $100 | 0/21 | 12–61 | S5 RSI7/ATR14 reignition, -$34.493, 12 trades, PF0.1359 |
| Feb 2026 / $200 | 0/21 | 46–97 | S5 RSI7/ATR14 exhaustion, -$76.730, 75 trades, PF0.4631 |

Least losing is NOT best/acceptable: all strategies reached their initial-capital threshold and ceased opening positions. Any inferred profit-factor optimum based on this negative research family would be fabricated.

## Independent exact quote ledger audit
- 84 summary account months and **4,754 simulated physical-shadow closes**, all reconciliation totals and per-trade `side*(observed_exit-opposing_entry) - 0.20` cash PnL PASS.
- Independent re-read Jan/Feb compressed original source: **9,508/9,508 exact original entry/exit UTC-ms Bid/Ask price legs matched**, zero mismatches. Position overlap=0 for every funded account stream. The exported ledger lacks signal-known timestamps, so the lag constraint is enforced by the simulator's exact code but not audited independently by this quote-only check.
- These are historical backtest arithmetic results, not Coinexx execution proofs.

## Provisional settings for NEXT creative hypotheses, NOT proven performance
- R8 microstructure: retain the exact R8 completed-M5 ATR14 native reference (with original session-dependent 1.75–2.50 USD M5 ATR floor) as frozen control; investigate S1 RSI5/7 and S5 RSI7/9 solely as *additional source/state features* with prior S15 ATR7/14/21 for cost/volatility context, not hard-coded universal R8 entry vetoes.
- Six virtual grid speed roles: S1 RSI5/7 for acceleration; S5 RSI7/9 for turn/re-ignition; S15 RSI9/14 and S30 RSI9/14 for rotation-versus-trend context; M1 RSI14 and ATR14 for local structure; M5/H1 RSI14–21 and M5 ATR14/21 for HTF volatility/risk context. The same RSI 'period' means different elapsed time on different bars.
- R9 SYNTH is a separately preserved offline whole-portfolio profit/gross loss/DD/trade volume/PF benchmark; R9 OVERFIT is historical teacher only. No R9-specific RSI optimization was run in this study and no R9 teacher feature is permitted in live signals.
- Proposed finite state virtual grid: causal RSI slope/hysteresis determines continuation vs verified sweep/reclaim; normalized completed ATR/cost ratio determines if sufficient price movement exists to pay actual spread+fee+slippage; rung geometry frozen for completed auction and reset only on new predeclared state; 0.01 lot physical singleton initially; all profits/loses/position occupancy and active hours fed into conservative offline context statistics. No martingale.
- Learning must be walk-forward/closed-trade-only with minimum sample safeguards, decayed conditional expectation, shrinkage to baseline, and shadow testing before any owner QC. Never optimize daily volume by accepting losses. Priority research score: actual net USD per trading day, then robust funded closed trades per trading day subject to positive expectancy and account survival; preserve investor PF>=30 and hourly win>75% as unsatisfied goals.
- MT5 parity hazard: Python uses Wilder-smoothed ATR, whereas MT5's standard iATR may use a rolling/SMA-like true range average. Verify exact period+formula and shift=1 as-of value against native reference before any cross-platform claim.

## Exact recoverable artifact pointers
Exact sources and all 4,754 close rows, 84 result rows, daily partitions, independently re-run quote-check script, provenance and SHA256 file manifest were packaged as:
`DAA_POST_GRID0271_RSI_ATR_20261014_COMPLETE_RESEARCH_PACKAGE.zip` with SHA256
`f53027da85a738ad8dae98ce9d8be695f8591623ca81da9b4678a69765fb2ef8` (**conversation attachment only; not GitHub or Google Drive, do not claim otherwise**).
Readable report:
`DAA_POST_GRID0271_RSI_ATR_PARAMETERS_20261014_REPORT.md` (conversation file). These exact-source bytes must be retained externally before relying on this GitHub pointer for future reruns.

## Controls unchanged
Previous original GRID0271, GRID0272+ archived failed experiments, exact R8 MQL5, R9 SYNTH historic controls, owner whitepaper, CURRENT_STATE.json (J0183), and live trading disabled. Do NOT promote any experimental settings, modify executable engine, or restart irrelevant historical screens.

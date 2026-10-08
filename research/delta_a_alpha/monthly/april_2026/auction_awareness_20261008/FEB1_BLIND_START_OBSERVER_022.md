# Unit 022 — February 1 Blind-Start V1 L2 Opportunity-Supply Replay

**Status: OBSERVER REPLAY COMPLETE; V1 FINANCIAL A/B NOT AVAILABLE.** No source-V1 rule selection or MT5 order path was changed. Owner-paused May untouched. August sealed.

## Precise decision
Use January 2026 *only* as training/warmup, with February 1 00:00 UTC as hypothetical live starting instant. Fit the existing eight-feature completed-M5 opportunity-supply logistic solely on **383 matured January hourly examples**. Do not refit Jan-frozen weights during February–April. As distinct experimental comparator, permit weekly-expanding refits only with already-matured outcomes; thirteen safe refit points. Signals never read month/day/hour as predictors.

## February–April results (independent of order generation)
| Month | Eligible hourly forecasts | Actual 2+ $10 M5-bar opportunity rate | JAN_FROZEN AUC | JAN_FROZEN positive alerts p>=0.5 | Precision of alerts | WEEKLY_EXPANDING AUC |
|--|--:|--:|--:|--:|--:|--:|
| February | 373 | 53.89% | 0.8860 | 143 | 93.01% | 0.8870 |
| March | 408 | 60.54% | 0.8452 | 190 | 87.89% | 0.8496 |
| April | 396 | 32.32% | 0.7916 | 50 | 78.00% | 0.8039 |

Total 1,177 forecasts. First eligible February 2 12:00 UTC after continuous completed M5 warmup. Historical retrospective choice of forecasting design means this is chronologically sound fitting, **not prospectively pre-registered independent validation**.

## Economic/velocity gate truth
The L2 observer is **observe-only** and by itself changes zero decisions. True baseline V1 + L2 conditional result is mathematically identical to a hypothetical executable baseline, but the historical artifacts do not contain the one immutable, tick-originating fully executable V1 L0–L8 model needed to observe the baseline economics. Current EA has no order-send. January/February/March profit research frontiers are optimized using each month's historical outcomes; cannot paste those into one February-start backtest. Do **not** report missing data as $0 or as evidence that net, PF, win rate, velocity, equity DD pass/fail.

**Feb, Mar, Apr V1+L2 actual funded trades/net/gross profit/gross loss/PF/win/expectancy/trade velocity/balance drawdown/equity DD/margin survivability: all UNVERIFIED.**

Canonical R9 SYNTH historical reference, *not a backtest of new V1*: Feb +$66,213.65/33,523 trades; Mar +$75,698.63/40,985 trades; Apr +$38,353.96/31,758 trades. R9 REAL: Feb -$7,331.21/35,394 trades; Mar -$7,255.59/40,297; Apr -$7,029.40/33,613; these differences warn strongly against inferring historical synthetic performance will carry to executable raw quotes.

## Exact reproducible checkpoint
All scripts, exact M5 source-derived feature events, model weights, hourly forecasts, daily/weekly/monthly scorecards, source SHA provenance, dated report and archive in project Library:

`/xauusd-trading-bot/delta-A-alpha/monthly/april_2026/vertical-grid-136/feb1-blind-start-v1-l2-observer-022/`

Especially `DAA_FEB1_V1_L2_OBSERVER_ECONOMIC_GATES_022.xlsx`: Read First, Daily, Weekly, Monthly, Economic Gates, R9 Reference Only. `DAA_FEB1_BLIND_L2_REPLAY_022.tar.gz` full reproducible observer bundle, `DAA_FEB1_BLIND_START_REPLAY_022_REPORT.md` scientific report, `FROZEN_JAN_ONLY_MODEL_FEB_START.json` actual January-fitted weights and scales. SHA256 and Python compilation validated; 13/13 adaptive training checkpoints use matured outcomes.

**Next necessary work for financial answer:** implement single predeployment frozen V1 full tick-causal order generator from original January source logic and safe broker-realistic pricing; measure exact paired control (observer does nothing) vs prespecified governor (can change renewal/capacity) from first February tradable tick through April with fixed 0.01, physical cap and equity/margin. Do not promote governor using February–April retrospective threshold selection.

## Preserved status
This note is in an isolated research branch. No change to production `delta-A-alpha` branch, frozen April-136 achievements, May scientific cursor or sealed August.

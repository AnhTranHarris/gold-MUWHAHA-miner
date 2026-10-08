# DAA Feb 1 blind deployment — L2 Opportunity Supply Observer 022

**Scientific status:** COMPLETE MARKET-AWARENESS REPLAY ONLY. **Not a unified executable V1 trading backtest.** Owner May 137 paused, August sealed.

**Authoritative durable research Library:** `/xauusd-trading-bot/delta-A-alpha/monthly/feb_apr_2026/feb1_v1_observer_022/`

Files: `DAA_FEB1_BLIND_START_REPLAY_022_REPORT.md`, `DAA_FEB1_BLIND_L2_REPLAY_022.tar.gz`, `DAA_FEB1_BLIND_V1_L2_DAILY_WEEKLY_MONTHLY_022.xlsx`, `DAA_FEB1_BLIND_OBSERVER_022_RESULTS.json`, `FROZEN_JAN_ONLY_MODEL_FEB_START.json`, `JAN_APR_TICK_DERIVED_COMPLETED_M5_EVENTS.npz`, complete per-hour CSV and daily/weekly/monthly scorecards, source SHA and Python replay.

Archive SHA256: `9e4faaef514bc2ac58428f79d651e86e446b0c527cf343f5489af3e59edb1038`. Read-only GitHub Jan-only model mirror: [FROZEN_JAN_ONLY_MODEL_FEB_START_022.json](./FROZEN_JAN_ONLY_MODEL_FEB_START_022.json).

## Deployment protocol
- Jan 1–31: **prior-only learning period**, no scored orders or forecasts.
- Feb 1 00:00 UTC: hypothetical blind deployment starts with **383 Jan-matured** training labels.
- Feb 2 12:00 UTC: first eligible live market-character forecast once 144 recent completed M5 bars pass continuity gate.
- Feb–Apr: January-frozen model used unchanged; second mode weekly refits on strictly matured historical labels. No April-specific settings, future market labels or calendar month trading feature.
- Decision target: at least two of next twelve 5-minute bars have range >= $10.
- Forecast L2 may inform L1/L3/L4/L5/L6/L7/L8 in **shadow/observe-only mode**. It never funds trades, enters positions, changes lot size, or manipulates existing V1 mechanics.

## Monthly outcomes

| Month | Frozen Jan model AUC | Frozen Jan Brier | Jan-model expected high supply | Actual high supply | Weekly refit AUC |
|:--|--:|--:|--:|--:|--:|
| Feb | 0.8860 | 0.1430 | 48.70% | 53.89% | 0.8870 |
| Mar | 0.8452 | 0.1672 | 51.79% | 60.54% | 0.8496 |
| Apr | 0.7916 | 0.1701 | 29.32% | 32.32% | 0.8039 |
| **Overall** | **0.8562** | **0.1605** | **43.25%** | **48.94%** | **0.8602** |

Total **1,177** forecasts / 576 high-supply hours. 13 online weekly model fits had no label maturity violations. Original Jan–Apr data hashes verified.

## Financial limitation

The preserved V1 MQL5 EA is an **observe-only skeleton with NO trade path**. January/February/March research profit fronts are outcome-selected each month; there is no one January-frozen complete V1 trading algorithm to run across February, March and April in an executable quote-first-touch simulator. Accordingly the report has **no trading net, trade count, PF, gross losses or drawdown**; these fields are `null`, not $0. This limitation is independent of model availability on Feb 1. To make an economic A/B test requires a genuinely unified order generator for L0–L8 with fixed 0.01 lot, costs/margin/heat and first-touch quote execution. **Do not fabricate month-spliced profit.**

**No merge to active `delta-A-alpha`, no EA edits, April 136 unchanged, May paused.** Branch `delta-A-alpha-feb1-blind-l2-20261008` is a separate recoverable research checkpoint only.
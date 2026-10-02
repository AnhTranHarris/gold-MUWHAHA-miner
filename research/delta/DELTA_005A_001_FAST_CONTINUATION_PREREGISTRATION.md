# DELTA 005A-001 — Historical Tick-Flow Entry Simulation

Status: PREREGISTERED
Scope: historical Python simulation only
Focus: entry selection + initial-hold diagnostics
Live/MT5 deployment: prohibited
August 2026: sealed

## Window
Stage-A UTC interval:
[2026-01-01T00:00:00.000Z, 2026-01-18T12:00:00.000Z)

Default historical surface:
DUKAS_COINEXX_LIKE_P75

## Question
Measure whether adding causal short-window tick-direction flow to the preserved R9-style entry state improves the historical entry/initial-hold diagnostic surface without changing the downstream R9-style lifecycle.

## Reconstructible public logic
MQL5 tick-buffer/flow article:
https://www.mql5.com/en/articles/19290

Tick-count flow:
flow(W) = (up_ticks(W) - down_ticks(W)) / (up_ticks(W) + down_ticks(W))

Kaufman efficiency references, used only as provenance for the already-existing R9 efficiency concept:
https://www.tradingview.com/script/dneYi7kK-Efficiency-Ratio-Kaufman/
https://www.tradingview.com/script/7imltc5K-Kaufman-Efficiency-Ratio-KER/

## Preserved parent state
The parent control remains the verified R9-style Stage-A reconstruction:
- frozen minute midpoint boundaries
- completed-S1 quality state
- completed-M5/session eligibility state
- one simulated position at a time
- preserved stop/trailing/max-duration/rearm rules

## Entry experiment
When an R9-style historical opportunity exists, the simulated entry is delayed until tick flow agrees with the direction while the original opportunity remains valid.

BUY flow condition:
fast_flow >= fast_threshold
and slow_flow >= slow_threshold

SELL mirrors the sign.

The opportunity expires if the relevant boundary is no longer accepted, the minute resets, or the preserved state makes it unavailable.

## Frozen sweep
Fast windows ms: 250, 500, 1000
Slow windows ms: 1000, 3000
Fast thresholds: 0.00, 0.10, 0.20, 0.30, 0.40
Slow thresholds: 0.00, 0.10, 0.20
Total configurations: 90

No new thresholds are added until this sweep is saved and reviewed under GOV-013.

## Downstream behavior
No mature-hold, exit-harvest, target, or high-profit mechanism is optimized in this unit. Downstream lifecycle stays frozen for comparability.

## Required historical diagnostics
- parent opportunities
- simulated entries
- completed simulated trades
- winning-trade count
- gross positive/negative outcome
- net outcome
- balance-drawdown statistic
- activity retention
- survival beyond 1/3/5/10/15 seconds
- MFE/MAE at 1/3/5/10/15 seconds where supported
- entry direction split

## Decision
This is a screening experiment, not a deployment decision. The next formula change must follow a saved leverage analysis. Sub-10-point incremental goal progress triggers the previously frozen creative-escalation rule unless a narrow high-sensitivity region is demonstrated.

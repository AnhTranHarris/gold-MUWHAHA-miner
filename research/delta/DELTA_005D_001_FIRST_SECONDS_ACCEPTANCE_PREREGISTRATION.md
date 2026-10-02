# DELTA 005D-001 — First-Seconds Acceptance / Early Invalidation

**Status:** PREREGISTERED  
**Mode:** historical Python simulation only  
**Focus:** ENTRY + INITIAL-HOLD  
**Mature Holding-Trade + Exit + High-Profit optimization:** OUT OF SCOPE  
**Stage-A:** [2026-01-01T00:00:00Z, 2026-01-18T12:00:00Z)  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**August:** SEALED

## Why this unit exists

DELTA_005A, 005B, and 005C changed entry ownership but did not materially improve first-seconds persistence.

005D therefore leaves the parent R9-style entry opportunity set intact and changes only the first-seconds acceptance state.

## Public reconstructible concepts

Breakout/reclaim community implementations emphasize that a break must prove it can hold a structural level rather than treating the raw cross as sufficient:
- https://www.tradingview.com/script/glll4xvz-VWAP-Reclaim/
- https://www.tradingview.com/script/GWlCTx9w-Reclaim-Breakout-Planner-AGPro-Series/

Kaufman Efficiency Ratio hysteresis implementations use a stronger threshold to establish state and a weaker threshold to maintain state:
- https://www.tradingview.com/script/2Ghnhfqg-Kaufman-Efficiency-Ratio-Gate-NovaLens/
- https://www.tradingview.com/script/LBJiEUcY-Adaptive-Trend-Shield-Kaufman-ER-EMA/

DELTA reconstructs only the disclosed causal concepts; public performance claims are not imported.

## Parent

Original verified R9-style Stage-A control on DUKAS_COINEXX_LIKE_P75:
- all original R9-style entries remain available;
- completed-S1 entry efficiency threshold remains >0.70;
- original $0.30 stop / +$0.10 trail activation / $0.03 trail / 30-second max-duration / rearm behavior remains after the initial-acceptance window.

## Initial-hold invalidation rule

During only the first `guard_ms` after entry, early invalidation may occur when ALL conditions are true.

For a BUY:
1. executable Bid loses the frozen BUY boundary by at least `failure_depth`;
2. 250ms and 1000ms tick-count flow are both negative;
3. current completed-S1 efficiency is below `maintenance_efficiency_floor`.

SELL mirrors the rule.

When invalidated, the historical simulation closes at the current executable quote. The standard R9 observation/rearm state continues causally on subsequent ticks.

After the guard window expires, 005D becomes identical to the frozen parent lifecycle.

## Frozen grid

Guard windows:
- 1000 ms
- 3000 ms
- 5000 ms

Boundary-loss depth:
- $0.00
- $0.02
- $0.05
- $0.10

Maintenance efficiency floor:
- 0.30
- 0.50
- 0.65

Total configurations: 36.

Fast/slow flow windows are fixed at 250ms / 1000ms sign-only because DELTA_005A showed threshold/window micro-tuning was not the high-leverage formula.

## Diagnostics

For every configuration:
- trades;
- winners;
- gross profit/loss;
- net;
- max balance drawdown;
- early invalidation count;
- early invalidation average P/L;
- early invalidation loss saved relative to full $0.30 stop proxy;
- trade/winner retention vs parent;
- 1/3/5/10/15s survival;
- MFE/MAE where supported;
- rearm count.

## Decision rule

The desired result is not simply fewer losses.

A useful initial-hold mechanism should materially reduce loss/drawdown while preserving the entry opportunity surface and avoiding large winner destruction.

After the sweep, GOV-013 leverage analysis decides whether to:
- retain an acceptance state;
- restructure the acceptance formula;
- split acceptance by specialist/session;
- abandon early invalidation.

No mature-trade exit or high-profit optimization is permitted in this unit.

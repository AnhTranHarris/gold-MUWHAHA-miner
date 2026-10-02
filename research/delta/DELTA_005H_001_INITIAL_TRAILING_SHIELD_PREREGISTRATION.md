# DELTA 005H-001 — Initial Trailing Shield

**Status:** PREREGISTERED
**Mode:** historical Python simulation only
**Focus:** ENTRY + INITIAL-HOLD
**Mature Holding-Trade + Exit + High-Profit:** frozen / out of scope
**Stage-A:** [2026-01-01T00:00:00Z, 2026-01-18T12:00:00Z)
**Surface:** DUKAS_COINEXX_LIKE_P75
**August:** SEALED

## Why this unit exists

DELTA_005A through 005G tested entry selection, retest/reversal routing, forensic persistence states, delayed recovery entries, and hard first-seconds validation. None produced a large Entry + Initial-Hold improvement.

The remaining high-leverage mechanical question is whether R9's early trailing behavior itself is terminating viable trades.

R9 activates trailing after only +$0.10 favorable movement and then keeps the stop only $0.03 behind executable price.

## Reconstructible community support

MQL5 Bootstrap IV documents fixed, periodic, and ATR trailing helpers and explains volatility-adaptive trailing:
https://www.mql5.com/en/articles/23882

MQL5 Trailing Engine article explicitly notes that a fixed tight trail can stop breakout trades on the first retracement and motivates trade-type-specific trailing:
https://www.mql5.com/en/articles/23618

MQL5 Zone Recovery RSI implementation delays trailing until a minimum profit condition is reached to prevent premature stop adjustments:
https://www.mql5.com/en/articles/16705

DELTA imports only reconstructible mechanics, not public performance claims.

## Parent entry and hard stop

All original R9-style entries remain unchanged.

The hard initial stop remains fixed at $0.30 for every cell.

No stop widening occurs in this unit.

## Experimental variable

Trailing remains disabled until BOTH are true:
1. elapsed time since entry >= shield_ms;
2. favorable excursion >= trail_activation_price.

Once enabled, the trail distance remains the original R9 $0.03.

Trailing never moves backward.

The 30-second max-hold remains unchanged.

## Frozen grid

Initial trailing shield:
- 0 ms
- 1000 ms
- 3000 ms
- 5000 ms
- 10000 ms

Trail activation:
- $0.10
- $0.20
- $0.30
- $0.50

Trail distance:
- fixed at $0.03

Total configurations: 20.

The cell 0ms / $0.10 is the exact parent-control cell and must reproduce the verified Stage-A parent.

## Required diagnostics

For every configuration:
- trades;
- winners;
- gross profit/loss;
- net;
- max balance drawdown;
- average hold;
- hard-stop exits;
- trailing-stop exits;
- max-hold exits;
- trail moves;
- 1/3/5/10/15s survival;
- winner retention vs parent;
- gross-loss/drawdown change.

## Desired shape

The purpose is to determine whether early fixed trailing is a principal cause of short REAL-like holding duration.

Promising regions should:
- materially improve 5s/10s/15s survival;
- preserve or increase winners;
- avoid catastrophic gross-loss/drawdown expansion;
- show a broad neighboring region, not one isolated cell.

This unit does not optimize final harvest/exit profit.

If trailing delay creates longer-lived positions but downstream profit remains unharvested, that belongs to the later Holding-Trade + Exit + High-Profit phase.

August remains sealed.

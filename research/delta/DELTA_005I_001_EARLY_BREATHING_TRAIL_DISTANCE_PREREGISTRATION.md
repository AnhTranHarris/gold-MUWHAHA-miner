# DELTA 005I-001 — Early Breathing Trail Distance

**Status:** PREREGISTERED  
**Mode:** historical Python simulation only  
**Focus:** ENTRY + INITIAL-HOLD  
**Mature Holding-Trade + Exit + High-Profit:** frozen / out of scope  
**Stage-A:** [2026-01-01T00:00:00Z, 2026-01-18T12:00:00Z)  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**August:** SEALED

## Why this unit exists

DELTA_005H established that R9's early fixed trailing is a real Initial-Hold bottleneck.

Raising trail activation from +$0.10 to +$0.30 materially increased 5s/10s/15s survival and average hold, but also worsened gross loss because the frozen downstream lifecycle was not yet harvesting the additional persistence.

005I tests a narrower protective-mechanics hypothesis:

**keep the original +$0.10 activation, but temporarily give the trade more breathing room by using a wider trail distance during only the first seconds, then revert to R9's original $0.03 trail.**

## Parent

All original R9-style entries remain unchanged.

Hard initial stop remains $0.30.

Trail activation remains +$0.10.

R9 mature trail distance remains $0.03 after the early breathing window.

Max hold remains 30 seconds.

No mature exit/harvest/high-profit optimization is permitted.

## Frozen grid

Early breathing window:
- 0 ms
- 1000 ms
- 3000 ms
- 5000 ms
- 10000 ms

Early trail distance:
- $0.03
- $0.05
- $0.10
- $0.20

Total configurations: 20.

Parent control:
- 0 ms early window
- $0.03 early trail distance

## Mechanics

Once favorable excursion reaches +$0.10:

- if elapsed time < early_window_ms, trailing uses early_trail_distance;
- once elapsed time >= early_window_ms, trailing uses the original R9 $0.03 distance;
- trailing never moves backward;
- hard stop remains active throughout.

This isolates whether **distance**, rather than activation timing alone, can preserve early breakout breathing room while restoring protection quickly.

## Required diagnostics

For every cell:
- trades;
- winners;
- gross profit/loss;
- net;
- max balance drawdown;
- average hold;
- trail moves;
- hard-stop exits;
- trailing-stop exits;
- max-hold exits;
- 1s / 3s / 5s / 10s / 15s survival;
- winner retention;
- gross-loss change;
- drawdown change.

## Desired shape

A useful region should preserve much of 005H's survival gain while causing materially less gross-loss/winner deterioration than simply delaying or weakening protection for long periods.

Broad neighboring improvement is preferred over an isolated best cell.

## Next-step rule

After the 20-cell sweep:
1. persist raw results;
2. create the per-test 2D matrix Sheet;
3. run GOV-013 leverage diagnosis;
4. only then decide whether trail distance merits refinement or whether another Initial-Hold mechanism should be tested.

Holding-Trade + Exit + High-Profit remains deferred.

August remains sealed.

# DELTA 005M-001 — Trail Ratchet Step / Frequency

**Status:** PREREGISTERED
**Mode:** historical Python simulation only
**Focus:** ENTRY + INITIAL-HOLD
**Mature Holding-Trade + Exit + High-Profit:** frozen / out of scope
**Stage-A:** [2026-01-01T00:00:00Z, 2026-01-18T12:00:00Z)
**Surface:** DUKAS_COINEXX_LIKE_P75
**August:** SEALED

## Derivation

DELTA_005H proved that delaying tight trailing activation from +$0.10 to +$0.30 materially improves initial-hold persistence.

DELTA_005I showed that globally widening the trail distance is lower leverage.

DELTA_005K and 005L showed that additional stop-level tightening can recover some gross loss, but it also converts too many recoverable 005H paths into exits.

A remaining untested trailing dimension is **ratchet step / update frequency**.

Public MQL5 implementations explicitly separate:
- trailing activation;
- trailing distance;
- trailing step;
- update frequency/state.

References:
- https://www.mql5.com/en/articles/495
- https://www.mql5.com/en/articles/22614
- https://www.mql5.com/en/articles/23618

DELTA imports only the reconstructible mechanics.

## Fixed parent

All original R9-style entries remain unchanged.

Hard stop:
- $0.30

Continuous trail:
- activation +$0.30
- distance $0.03

Max hold:
- 30 seconds

No staged protection locks are used in this unit.

## Ratchet-step rule

The first trail update may occur once favorable excursion reaches +$0.30.

After a trail update, another update is allowed only when BOTH are true:

1. favorable executable price has advanced by at least `trail_step_price` beyond the price reference used for the previous trail update;
2. at least `min_update_interval_ms` has elapsed since the previous trail update.

The stop never loosens.

A step of $0.00 and interval 0ms reproduces the 005H every-tick ratchet.

## Frozen 5×4 grid

Trail step:
- $0.00
- $0.03
- $0.05
- $0.10
- $0.15

Minimum update interval:
- 0 ms
- 250 ms
- 500 ms
- 1000 ms

Total variants: 20.

## Required diagnostics

For every cell:
- trades;
- winners;
- gross profit/loss;
- net;
- max balance drawdown;
- average hold;
- trail-move count;
- hard-stop / trail-stop / max-hold exits;
- 1/3/5/10/15s survival;
- winner retention vs R9 and 005H;
- net/gross-loss change vs 005H;
- survival change vs 005H.

## Desired shape

A useful ratchet step/frequency should preserve most or all of 005H's winner count while retaining or improving its survival and reducing unnecessary trail churn.

Broad neighboring cells matter more than one isolated optimum.

## Phase boundary

No entry logic, mature hold, harvest, profit target, or final exit rule changes.

Holding-Trade + Exit + High-Profit remains deferred.

August remains sealed.

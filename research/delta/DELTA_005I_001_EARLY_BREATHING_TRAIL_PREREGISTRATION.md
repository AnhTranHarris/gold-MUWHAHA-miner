# DELTA 005I-001 — Early Breathing Trail Distance

**Status:** PREREGISTERED
**Mode:** historical Python simulation only
**Focus:** ENTRY + INITIAL-HOLD
**Mature Holding-Trade + Exit + High-Profit:** frozen / out of scope
**Stage-A:** [2026-01-01T00:00:00Z, 2026-01-18T12:00:00Z)
**Surface:** DUKAS_COINEXX_LIKE_P75
**August:** SEALED

## Derivation

DELTA_005H established that the original +$0.10 activation / $0.03 fixed trail is an Initial-Hold bottleneck.

Permanently delaying activation increases survival but also weakens protection too long.

005I therefore tests temporary breathing room:
- keep original +$0.10 activation;
- widen the trail only during a bounded early window;
- after the early window, revert immediately to the original $0.03 trail.

## Parent mechanics held fixed

- all original R9-style entries;
- hard stop: $0.30;
- trail activation: +$0.10;
- max hold: 30 seconds;
- same rearm/order/state logic.

## Experimental mechanics

For elapsed time < early_window_ms:
trail distance = early_trail_distance.

For elapsed time >= early_window_ms:
trail distance = $0.03.

The stop may only improve; it never moves backward.

## Frozen grid

Early breathing windows:
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

The 0ms / $0.03 cell is the exact parent-control cell.

## Required diagnostics

- trades / wins;
- gross profit / gross loss / net;
- max balance drawdown;
- average hold;
- hard-stop exits;
- trail-stop exits;
- max-hold exits;
- trail moves;
- 1/3/5/10/15s survival;
- winner retention;
- survival gain per unit of gross-loss deterioration.

## Desired shape

Prefer broad regions that improve first-seconds survival while keeping:
- winner retention high;
- gross-loss deterioration below active warning/hard-floor limits;
- net/drawdown near or better than parent.

This remains an Initial-Hold experiment only.

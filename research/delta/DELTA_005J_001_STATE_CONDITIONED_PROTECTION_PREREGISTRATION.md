# DELTA 005J-001 — State-Conditioned Initial Protection

**Status:** PREREGISTERED
**Mode:** historical Python simulation only
**Focus:** ENTRY + INITIAL-HOLD
**Mature Holding-Trade + Exit + High-Profit:** frozen / out of scope
**Stage-A:** [2026-01-01T00:00:00Z, 2026-01-18T12:00:00Z)
**Surface:** DUKAS_COINEXX_LIKE_P75
**August:** SEALED

## Derivation

DELTA_005E discovered a broad accepted-consolidation state:
- original boundary remains accepted;
- completed-S1 range has cooled/compressed.

DELTA_005H showed that looser early trail activation materially improves 5s/10s/15s survival.

DELTA_005I showed that global trail-distance widening is lower leverage.

005J combines the useful state and the useful mechanic.

## Parent mechanics

All original R9-style entries remain unchanged.
Hard stop remains $0.30.
Mature trail remains activation +$0.10 / distance $0.03.
Max hold remains 30 seconds.
Rearm/order/state semantics remain unchanged.

## Universal observation grace

For the first 1000 ms after entry, trailing is disabled for all trades.

The hard $0.30 stop remains active.

This brief grace is required so the causal accepted-consolidation state can be observed before the trail has already tightened irreversibly.

## State classification at 1000 ms

For a trade still open at the first tick at/after 1000 ms:

BUY accepted-consolidation requires:
- executable Bid remains at least min_acceptance above the frozen entry boundary;
- completed-S1 range <= range_ceiling;
- regime/spread gate remains open.

SELL mirrors the condition using Ask.

No future tick is used.

## Conditional protection

If accepted-consolidation is true:
- use a looser trail activation threshold until protection_end_ms from entry;
- trail distance remains $0.03.

If accepted-consolidation is false:
- immediately revert to baseline +$0.10 activation / $0.03 distance after the 1s observation grace.

After protection_end_ms:
- all trades revert to baseline +$0.10 / $0.03.

Stops never move backward.

## Frozen grid

S1 range ceilings:
- $0.50
- $0.75
- $1.00

Minimum boundary acceptance:
- $0.00
- $0.05

Accepted-state trail activation:
- $0.20
- $0.30
- $0.50

Protection end:
- 3000 ms
- 5000 ms
- 10000 ms

Total configurations: 54.

Observation grace is fixed at 1000 ms.

## Required diagnostics

For every configuration:
- trades / wins;
- accepted-state classifications;
- non-accepted classifications;
- gross profit / gross loss / net;
- max balance drawdown;
- average hold;
- hard-stop / trail-stop / max-hold exits;
- 1/3/5/10/15s survival;
- winner retention;
- accepted-state trade contribution where available;
- survival gain per unit of gross-loss deterioration.

## Desired shape

Prefer broad regions with:
- material 5s/10s survival gain;
- winner retention above active protection thresholds;
- gross-loss deterioration below active warning/hard-floor limits;
- improved or near-parent net/drawdown.

This is an Initial-Hold mechanism test only.

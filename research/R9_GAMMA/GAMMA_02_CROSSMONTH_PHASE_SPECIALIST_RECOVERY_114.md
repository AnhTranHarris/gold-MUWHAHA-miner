# GAMMA-02 — Cross-Month Phase Specialist Recovery 114

**Status:** RECOVERED / DURABLE / CHRONOLOGICAL VALIDATION COMPLETE THROUGH JULY  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Recovered diagnostics

### 110 scale-free activity diagnostics

Completed Jan-Jul. Result: normalized short-vs-baseline tick-activity ratios describe tape scale but do not by themselves restore the inactive Apr-Jul regimes. Absolute 103 thresholds remain non-transferable.

### 111 exact state-signature diagnostics

Confirmed that frozen 103/104 state families are sparse or negative in Apr-Jul when used with the old renewal behavior.

### 112 cross-month 10-minute phase map

Continuous month-scoped diagnostics show substantial positive phase/state renewal pockets still exist in Apr-Jul even when 103/104 stands aside.

Representative positive diagnostic cells:
- Apr 17:40 fully aligned short: ~+$7.7K / 7.4K child trades
- May 17:50 long pullback state: ~+$10.0K / 15.3K
- Jun 16:00 fully aligned short: ~+$7.0K / 21.0K
- Jul 16:20 fully aligned short: ~+$2.4K / 6.4K

These are diagnostic cells, not additive portfolio claims.

### 113 phase-scout router

Partial Jan-Mar only. Current configuration is REJECTED:
- Feb approximately -$818 / 26.7K trades / PF <1
- Mar approximately -$51.5K / 34.2K / PF ~0.384
Do not extend this exact router to Apr-Jul.

## April discovery -> forward validation

A mechanical April specialist was selected using only April:
- exact UTC hour, 10-minute bin, completed H4/H1/M15/M5 state, and direction;
- minimum 500 child trades;
- positive April net >= $250;
- PF >= 1.15;
- choose the better preregistered q050 vs q125 renewal geometry per exact phase/state cell;
- one shared chronological child cap 703.

Full April-selected set:
- April: +$15,910.93 / 37,887 trades / PF 1.769
- Frozen May: -$14,231.24 / 49,049 / PF 0.745
Disposition: full set rejected.

## Transferable 17:00 subset

The failure is isolated to 16 UTC. The 17 UTC subset was selected in April, then frozen unchanged.

- April discovery: **+$11,880.59 / 22,848 trades**
- May frozen validation: **+$16,977.84 / 30,378**
- June frozen validation: **+$5,597.73 / 18,428 / PF 1.389**
- July frozen validation: **-$1,381.53 / 6,555 / PF 0.778**

Scientific interpretation:
- 17 UTC phase/state renewal is a genuine Apr-Jun transferable specialist family.
- July is a regime break and must be handled by a separate specialist/router rather than weakening the Apr-Jun engine.
- This supports the parallel-specialist architecture already established by 103/104 (Jan-Feb) and 109 (March).

## Current architecture by chronology

1. Jan-Feb: rolling-activity renewal specialist 103/104.
2. March: failed-ignition reverse specialist 109.
3. Apr-Jun: April-discovered frozen 17 UTC phase specialist 114.
4. July: unresolved / next specialist discovery target.
5. August: sealed.

## Persistent Library

/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/post-crossover-recovery/phase-specialists-110-114/

## Next unit

GAMMA_02_JUNE_DISCOVERY_JULY_VALIDATION_115

Rules:
- use June only to discover a July candidate;
- freeze before July replay;
- preserve 103/104, 109, and 114 unchanged;
- no August access;
- no MQL5 build yet;
- R9 SYNTH remains the hard target.
# GAMMA-02 — June Discovery / July Validation 115

**Status:** MAJOR CROSS-MONTH TRANSFER BREAKTHROUGH  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## June-only discovery

Using only June 112 phase-map data, select exact phase/state cells mechanically:
- minimum 500 child trades;
- positive June net >= $250;
- PF >= 1.15;
- choose best preregistered q050/q125 geometry per exact state/phase;
- one chronological child cap 703.

June full specialist:
- **+$17,097.73**
- **54,700 trades**
- PF **1.3814**
- expectancy **+$0.31257/trade**

## Frozen July validation

Same June-selected rules, no retuning:
- **+$2,253.09**
- **16,534 trades**
- PF **1.1552**
- expectancy **+$0.13627/trade**

Source attribution:
- June-selected 16 UTC subset in July: **+$4,059.01 / 11,028 trades / PF 1.4957 / +$0.3681 expectancy**
- June-selected 17 UTC subset in July: -$1,805.92 / 5,506 / PF 0.7148

Disposition:
- retain the **16 UTC June-discovered subset** as the July specialist;
- reject the 17 UTC subset for July;
- do not retune the July specialist on July.

## Chronological Jan-Jul architecture

1. Jan-Feb: rolling-activity renewal specialist 103/104.
2. March: failed-ignition reverse specialist 109.
3. Apr-Jun: April-discovered frozen 17 UTC phase specialist 114.
4. July: June-discovered frozen 16 UTC phase specialist 115.
5. August: sealed.

Using the frozen specialist assigned to each month, the current sequential Jan-Jul research ledger is approximately:
- Jan +$43,959.75 / 28,119 trades
- Feb +$43,937.72 / 28,221
- Mar +$2,067.33 / 807
- Apr +$11,880.59 / 22,848
- May +$16,977.84 / 30,378
- Jun +$5,597.73 / 18,428
- Jul +$4,059.01 / 11,028
- **Total net: +$128,479.97**
- **Total trades: 139,829**

Against canonical R9 SYNTH Jan-Jul (+$309,122.85 / 219,342 trades):
- current chronological net capture is ~41.6% of SYNTH;
- current chronological trade count is ~63.7% of SYNTH.

This is not yet one unified live router certification and does not imply equivalent PF/win-rate across every month. It is a chronological specialist research architecture with no future-month retuning inside each validation step.

## Exact artifacts

Persistent Library:
/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/post-crossover-recovery/phase-specialists-110-114/

- gamma02_june_discovery_july_validation_115.py
- gamma02_june_discovery_july_validation_115.json

## Next unit

GAMMA_02_UNIFIED_CAUSAL_SPECIALIST_ROUTER_116

Objective:
- replace month-specific assignment with a causal router based on activity/state/phase features already earned;
- reproduce the specialist handoff without using month labels;
- preserve positive Jan-Jul chronology;
- then run exact equity-DD and MT5 only after the router is frozen.
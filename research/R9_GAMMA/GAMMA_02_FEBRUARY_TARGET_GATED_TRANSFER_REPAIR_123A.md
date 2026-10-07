# GAMMA-02 — February Target-Gated Transfer Repair 123A

**Status:** COMPLETE TRANSFER SCREEN — JANUARY FAMILIES DO NOT SOLVE FEBRUARY AT REQUIRED SCALE  
**Date:** 2026-10-07  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Why this unit exists

Router-122 QA proved the earlier February 103/104 result was warmup leakage. This unit re-tests already-earned January specialist families with explicit target-month entry gating.

Warmup ticks may initialize completed-bar state only. No warmup-period entry may be admitted or counted.

## Clean February transfer results

### Target-gated 083 renewal family
- +$4,193.52
- 7,020 trades
- PF 1.8911
- 91.25% win
- +$0.5974 expectancy
- ~164s average hold

### Dynamic watchdog 119
- **+$8,766.07**
- **19,456 trades**
- PF 1.5227
- 91.85% win
- +$0.4506 expectancy
- ~78.9s average hold

This is the strongest clean inherited transfer in this screen, but still far below the hard R9-SYNTH objective.

### Persistent NY17-short 116
- -$282.71
- 21,756 trades
- PF 0.9901
- approximately flat/negative

Rejected as February repair.

### Fast-quantum family
Target-gated February search over NY17 windows/displacement/quantum:
- best net observed ~+$8,759.75 / 4,238 trades / PF 2.53 / +$2.07 expectancy with q=$4;
- smaller q=$0.50 can exceed ~18K trades and ~95.8% wins but expectancy collapses to ~+$0.30 and PF ~1.83.

Conclusion: January's extraordinary fast-quantum economics do not transfer to February unchanged.

### Rolling-activity family
Corrected target-month activity distributions are materially lower than the January thresholds.

Best N=64 legal result:
- +$5,691.83
- 6,534 trades
- PF 2.9057
- 93.27% wins
- +$0.8711 expectancy

N=8/N=16 blocks were also completed and do not materially exceed the N=64 result.

### Target-gated reverse renewal
A 120-second block was tested after explicit target gating.
Best result in that block:
- about +$366 / 687 trades
- PF ~1.53

Rejected as primary February repair.

## Scientific conclusion

The problem is no longer a target-gate bug. February is a genuinely different state distribution.

The inherited January families preserve positive edge but top out around +$8-9K in legal February replay. That is not sufficient for the hard goal.

Therefore the next unit is **February-native causal discovery**, using the same allowed primitives:
- completed HTF state/signature;
- session/subphase;
- favorable displacement;
- causal activity/renewal;
- exact Bid/Ask;
- no month label in any eventual deployable router.

Month identity may be used only as the discovery dataset partition.

## Durable artifacts

Persistent Library:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/february-repair-123/`

Contains target-gated 083, watchdog119, persistent116, fast-quantum screen, activity N8/N16/N64, and reverse-renewal block.

## Next

`GAMMA_02_FEBRUARY_NATIVE_STATE_DISCOVERY_124`

Goals:
1. identify February's strongest legal hour/state/direction cells;
2. map short/medium/long markout by cell;
3. build a February specialist only from reconstructible causal state features;
4. backcast that specialist to January and later validate March;
5. do not use calendar-month identity in deployable routing.

R9 SYNTH remains the hard target.

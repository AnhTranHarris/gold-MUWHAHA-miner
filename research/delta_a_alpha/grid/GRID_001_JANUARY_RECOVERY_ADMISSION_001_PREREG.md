# GRID-001 January Recovery Admission 001 — Preregistration

**Unit:** `DAA_GRID_001_JANUARY_RECOVERY_ADMISSION_001`  
**Status:** FROZEN BEFORE COMPUTE

## Question

At the exact timestamp where an A10/A15 continuation event hits EARLY_THESIS_FAILURE, can causal path information distinguish:

- **FLIP ONCE** into the opposite direction;
- **RETIRE** the event?

Blind recovery is already rejected. This unit tests admission only.

## Parent contract

Reuse exactly:
- A10 and A15 adaptive lattices;
- continuation entry;
- +0.25 gap proof-of-life;
- -0.50 gap early failure;
- five-minute original event horizon;
- one opposite recovery leg with ±1.00 original event gap;
- no horizon reset;
- fixed 0.01;
- no Martingale;
- no second flip.

## Label

For each early-failure event:

`RECOVERABLE = recovery_leg_net > 0`

This is a research label only.

Economic evaluation is primary:
- selected recovery leg adds its realized PnL;
- unselected event retires at the early-failure exit.

## Causal features allowed at failure timestamp

Compact first pass only:

1. **time_to_failure_ms**
2. **failure_speed_gap_per_second**
3. **failure_overshoot_gap_fraction**
4. adaptive **event_gap_usd**
5. crossing direction
6. recovery-aligned signed displacement over:
   - 1s
   - 5s
   - 15s
   - 30s
   - 60s
7. path length over the same windows
8. directional efficiency:
   `abs(net displacement) / path length`
9. recovery-aligned path efficiency:
   signed displacement divided by path length

All features must use ticks at or before the failure timestamp.

No session, news, macro, specialist, or future parent-state categories in this unit.

## Discovery tools

### A. Univariate structural bins

Inspect deciles/coarse bins for:
- time-to-failure;
- failure speed;
- overshoot;
- recovery-aligned 5s / 15s / 30s movement;
- directional efficiency;
- gap size.

Purpose: find monotonic or knee-like mechanisms.

### B. Shallow decision tree microscope

One tree per lattice:
- trained only on chronological discovery segment;
- max depth <= 3;
- minimum leaf >= 100 early-failure events;
- no hyperparameter sweep.

The tree is a microscope, not a production model.

Any useful split must be translated back into human-readable causal rules before promotion.

### C. Fixed probability gates

If the tree produces probabilities, evaluate a tiny preregistered gate set:
- 0.55
- 0.60
- 0.65

Threshold choice is made on discovery only; validation is untouched.

## Anti-overfit split

Use the same chronological split as prior January units:
- first 2/3 of January tick index = discovery;
- final 1/3 = validation.

## Required comparisons

For A10/A15:
- RETIRE baseline;
- BLIND RECOVERY reference;
- selected recovery;
- impossible selective oracle ceiling.

Report:
- selected recovery count/share;
- recovery-leg PF and expectancy among selected;
- combined net/PF/expectancy;
- gross loss;
- discovery and validation;
- gap to oracle ceiling.

## Advancement

A recovery-admission mechanism advances only if:
- it beats RETIRE economically in discovery and validation;
- selected recovery-leg PF > 1 in validation;
- the advantage is not dependent on one tiny leaf or knife-edge threshold;
- rule can be expressed causally and reconstructed without the discovery model.

If the model can classify but no simple causal structure survives, retain it only as evidence that additional state is missing.

No threshold/feature mining beyond this preregistered pass.

August sealed. Main `delta` read-only. MQL5 unauthorized.

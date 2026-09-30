# BETA064-R1B1 — H4 Structural Entry + Regime-Conditioned Hold Specialist

**Date:** 2026-09-30  
**Branch:** `beta`  
**Status:** RESEARCH CHECKPOINT — POSITIVE SPECIALIST, NOT WHOLE-SYSTEM PROMOTION — NO MQL5 AUTHORIZATION — AUGUST SEALED

## Purpose

This bounded unit implements the first empirical transformation of the BETA064 two-floor architecture:

`ENTRY specialist -> thesis packet -> HOLD specialist -> shared executable lifecycle`

The objective was not to add more correlated heads. It was to recover a genuinely orthogonal Entry mechanism, then improve its post-fill lifecycle with a Hold specialist.

## What failed first

A broad 12-desk January screen was built from the Dukascopy XAUUSD tick corpus using a causal one-second screening cache.

Prototype desks:
- Macro structural trend
- Structural pullback/reacceleration
- Session ORB
- VWAP trend pullback
- VWAP break/reclaim
- Statistical value reversion
- Sweep/reclaim
- Level bounce
- Level break/acceptance
- Compression/expansion
- Kinetic ignition
- Failed expansion/contradiction

Path-aware executable labels used observed Ask for BUY, Bid for SELL, opposite executable quote for liquidation, and the existing $0.02 BETA research fee.

No broad prototype desk produced positive calibration expectancy. FIT-only activation tightening did not rescue them. Specialist-local HistGradientBoosting value models improved some selection — especially Level Bounce — but none crossed positive executable expectancy.

This rejected the idea that simply increasing five generic specialists to twelve generic specialists would solve BETA064.

## Recovery from historical reconstructible mechanisms

The historical project record identified a slower structural P5 family. Rather than inherit old P/L, the current R10 source was inspected to recover exact public/project geometry:

- H1: completed 5-bar breakout, ATR14, current ATR / prior-20 ATR mean <= 1.20, 1.5 ATR catastrophe stop, trail activates only after +0.25 ATR MFE, 1.0 ATR trail, 12h max hold.
- H4: completed 6-bar breakout, ATR14, current ATR / prior-20 ATR mean <= 2.00, 1.5 ATR catastrophe stop, trail activates only after +0.25 ATR MFE, 1.0 ATR trail, 24h max hold.

All structure and ATR inputs use completed bars.

## Fresh Jan-Jul one-second executable replay

The first rough H4 implementation was rejected after an ownership bug was detected: it allowed overlapping H4 positions. That result was not accepted.

The corrected P5 reconstruction was then replayed one position at a time.

### H1

- 310 trades
- Net: **-$345.76**
- PF: **0.891**
- Win rate: 39.4%

H1 did not transfer under the current stricter BETA Dukascopy/execution contract and is pruned from the current Entry floor.

### H4 baseline

- 145 trades
- Net: **+$518.88**
- PF: **1.305**
- Win rate: 51.0%

Monthly net:
- Jan +$214.22
- Feb -$52.04
- Mar +$144.33
- Apr -$16.48
- May +$227.25
- Jun -$41.96
- Jul +$43.56

This is the first current BETA064 Entry specialist in this cycle with positive aggregate executable expectancy.

### Naive H1 + H4 combination

One-position H4-priority merged replay:

- 390 trades
- Net: **+$155.74**
- PF: **1.039**

Naive combination materially degraded the H4 sleeve.

Conclusion: independent specialists require ownership/routing. More specialists is not automatically more edge.

## Hold-specialist refinement

A bounded Hold policy family was tested. The useful mechanism was **failed ignition**, not wider runner trailing.

Initial hypothesis:
after a structural entry has been open for a fixed age, if it has never achieved a small favorable excursion and is currently red, continuation value may be poor.

A one-minute screening neighborhood identified the useful region around:
- age 45–60 minutes;
- MFE hurdle around 0.10 ATR.

The one-second executable confirmation changed the ranking, so the one-minute screen was not accepted as final evidence.

### Failure discovered

Applying failed ignition to every H4 state at 60 minutes improved some months but badly damaged March. Inspection showed the Hold rule was liquidating several **late-igniting high-volatility H4 trends** that subsequently became large winners.

The Hold problem therefore separates into two trajectory regimes:

1. quiet/normal-vol structural breakout: weak first-hour ignition is informative;
2. high-vol structural breakout: late ignition is common enough that the same early-failure rule is destructive.

## Regime-conditioned Hold ownership

Predeclared causal state already available at entry:

`VR = completed H4 ATR14 / mean(previous 20 completed H4 ATR14)`

The refined rule applies the 60-minute failed-ignition specialist only when:

- `VR <= 1.20`
- position age >= 60 minutes
- observed MFE since fill < 0.10 ATR
- current executable P/L is negative

For `VR > 1.20`, the trade remains under the original slow-ignition H4 lifecycle.

The 1.20 boundary was chosen from the development/calibration side of the campaign; May-Jul was not used to choose it. A local VR neighborhood was checked to make sure the phenomenon was not a single-point spike.

## Frozen one-second Jan-Jul result

### H4 baseline
- 145 trades
- **+$518.88**
- PF **1.305**

### H4 + regime-conditioned failed-ignition Hold specialist (VR <= 1.20)
- 146 trades
- **+$766.37**
- PF **1.532**
- Win rate 50.0%
- Net improvement: **+$247.49 / +47.70%** versus the same H4 Entry baseline

Monthly net:
- Jan +$187.34
- Feb +$177.55
- Mar +$164.25
- Apr -$16.48
- May +$227.25
- Jun -$17.11
- Jul +$43.56

The Hold specialist repairs February without destroying March and preserves positive July. April and June remain slightly negative.

A wider VR threshold (1.50–1.60) produced higher full-period net, but it was not selected because the project must not use May-Jul to optimize the threshold after inspection. The VR<=1.20 checkpoint is therefore the scientifically cleaner frozen candidate.

## Quant interpretation

This is evidence for the two-floor architecture.

The useful specialist is not another directional predictor. It answers:

> Given an H4 structural breakout that has already been entered, is weak first-hour development evidence of thesis failure in this volatility regime?

The answer is state-dependent.

A single global Hold rule was inferior to:
- **FAILED_IGNITION_HOLD** for quiet/normal H4 states;
- **SLOW_IGNITION_TOLERANCE** for high-volatility H4 states.

That is exactly the kind of post-fill ownership BETA064 was missing.

## Limitations / next gate

This is a one-second causal executable replay derived from the raw Dukascopy tick corpus, not yet a full original-tick same-millisecond barrier-order certification.

Therefore:
- do not promote to official BETA EA;
- do not create MQL5;
- do not call this a broker-certified result;
- exact raw-tick replay remains required before final specialist promotion;
- the result is too low-frequency to solve the whole BETA039 economic deficit by itself.

## Next bounded experiment

Build a fresh **multiscale acceptance/sweep Entry desk** from the reconstructible 1m/3m/5m/10m/20m boundary hierarchy, but treat simultaneous scale activity as structured state rather than independent votes.

Then:
1. evaluate path-aware executable Entry value;
2. preserve H4 as an independent positive structural desk;
3. attach specialist-specific thesis packets;
4. route post-fill trajectories through Hold specialists;
5. merge only after each desk shows unique executable value;
6. exact raw-tick confirm any surviving candidate;
7. keep August SEALED.

No official MQL5 work is authorized by this checkpoint.

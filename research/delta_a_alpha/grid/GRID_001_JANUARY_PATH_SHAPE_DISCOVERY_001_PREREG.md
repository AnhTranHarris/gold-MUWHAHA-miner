# GRID-001 January Path-Shape Discovery 001 — Preregistration

**Unit:** `DAA_GRID_001_JANUARY_PATH_SHAPE_DISCOVERY_001`  
**Status:** FROZEN BEFORE COMPUTE

## Purpose

Determine whether the elastic grid event contains enough **causal post-crossing path structure** to distinguish:
- continuation;
- mean reversion;
- abstention.

A tree ensemble may be used only as a discovery microscope. It is not a promotion candidate.

## Frozen clock

Use the retained January elastic clock:
- alpha = 0.50;
- completed-M1 ATR14 spacing;
- $1 floor / $8 cap;
- $0.25 quantization;
- 10% hysteresis;
- P75 execution surface;
- no physical averaging.

## Observation windows

Two bounded causal windows:
- 3 seconds;
- 10 seconds.

Physical/shadow entry occurs only after the observation window.

## Allowed path-shape features

Computed only from ticks inside the causal observation window:
- final direction-normalized displacement;
- maximum continuation excursion;
- maximum reclaim excursion;
- path length;
- directional efficiency;
- path range;
- zero/reclaim recross count;
- sign-change count;
- tick count.

Context available at event time:
- active elastic gap;
- virtual same-side stack depth;
- event direction;
- completed-M1 parent efficiency/direction over 15m, 60m, and 240m.

No session/news/time-of-day/calendar features.

## Labels

At delayed executable entry, evaluate both:
- MR;
- CONT.

Each uses:
- fixed 0.01 economics;
- $1 TP;
- $1 adverse bound;
- 5-minute horizon after delayed entry;
- $0.02 round-trip commission.

Oracle label:
- CONT if CONT PnL > MR PnL and CONT > 0;
- MR if MR PnL > CONT PnL and MR > 0;
- ABSTAIN if both <= 0.

## Split

Same frozen chronological split:
- first 2/3 January ticks = discovery/training;
- final 1/3 = validation only.

## Discovery microscope

Use a bounded ExtraTrees/RandomForest-style ensemble with fixed seed only to measure whether feature information exists.

Report:
- validation classification accuracy/balanced accuracy;
- economic PnL/PF if the predicted class were followed;
- acceptance rate;
- feature importance;
- comparison to always-CONT delayed baseline.

If validation evidence exists, fit a shallow tree afterward only to extract candidate rules.

If the ensemble itself cannot materially beat the delayed always-CONT baseline on validation, reject this feature family and do not tune the model.

No production ML promotion is authorized.

August sealed. Main delta read-only. MQL5 unauthorized.

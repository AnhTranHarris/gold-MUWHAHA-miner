# DELTA R015 — Confidence-Tiered R010 Ownership Preregistration

**Status:** PREREGISTERED / NOT EXECUTED  
**Parent:** R014 exact rounded R010 Jan–Jul validation  
**Scope:** ENTRY + INITIAL-HOLD  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Fixed base rule

```
I250 <= -0.55 OR H1NetATR > 0.35
```

Moderate base-condition events:
- flip the R9 intended side;
- assign reversal ownership;
- suppress generic opposite-side same-minute rearm after owned exit.

## Extreme tier

Only the extreme subset may be skipped.

H1 extreme levels:
- 0.70
- 1.05
- 1.40

Micro extreme levels:
- -0.75
- -0.90

Extreme forms:
- OR: H1 extreme OR micro extreme
- AND: H1 extreme AND micro extreme
- H1_ONLY
- MICRO_ONLY

Total configurations: 24.

If base condition is false: keep R9 side.
If base condition true but extreme false: flip.
If base condition true and extreme true: skip that event and suppress the rest of the current M1 opportunity.

## Evaluation

Surfaces:
- P50
- P75
- P90

Robustness floors:
- minimum trade retention >= 80%
- minimum winner retention >= 80%

Selection:
- Pareto/non-dominated comparison on worst-surface net-loss, gross-loss, and drawdown improvement;
- no single net-profit argmax;
- no adaptive threshold changes;
- exact Jan–Jul replay required for any survivor before a stronger claim.

The earlier timed-out confidence-tier script/result is ignored and contributes no result or selected parameter.

Workbook:
`26 R015 Tier Prereg`

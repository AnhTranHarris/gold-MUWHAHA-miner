# DELTA R017 — Ownership Branch Attribution Preregistration

**Status:** PREREGISTERED / NOT EXECUTED  
**Parent:** R016 / R015-T06  
**Scope:** ENTRY + INITIAL-HOLD  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**GOV-018:** NOT ACTIVATED

## Frozen thresholds

Base R010 ownership:
- MICRO trigger: `I250 <= -0.55`
- H1 trigger: `H1NetATR > 0.35`

Mutually exclusive classes:
- `MICRO_ONLY`: micro true, H1 false
- `H1_ONLY`: H1 true, micro false
- `DUAL`: both true

R016 extreme override remains frozen:
- `H1NetATR > 0.70 AND I250 <= -0.90`
- extreme action: **SKIP + suppress rest of current M1**

## Branch actions

For each non-extreme class, independently assign one of:
- KEEP: original R9 side + normal R9 rearm
- FLIP: opposite side + reversal ownership + suppress generic same-minute rearm after owned exit
- SKIP: no entry + suppress remainder of current M1

Full causal factorial:
- 3 MICRO_ONLY actions
- 3 H1_ONLY actions
- 3 DUAL actions
- total **27 configurations**

The R016/T06 canonical control is:
- MICRO_ONLY = FLIP
- H1_ONLY = FLIP
- DUAL = FLIP
- extreme DUAL override = SKIP

## Evaluation

Stage-A surfaces:
- P50
- P75
- P90
- NATIVE diagnostic

Robustness floors on P50/P75/P90:
- trade retention >= 80% vs R9
- winner retention >= 80% vs R9

Selection:
- retain non-dominated configurations on worst-surface net-loss, gross-loss, drawdown improvement, trade retention, and winner retention;
- native surface remains a diagnostic/promotion blocker but is too sparse to define the modeled-surface retention floor;
- exact Jan–Jul replay only for Stage-A Pareto survivors.

No thresholds may change inside R017.
No action may be invented after results.
No GOV-018 synthesis is activated.

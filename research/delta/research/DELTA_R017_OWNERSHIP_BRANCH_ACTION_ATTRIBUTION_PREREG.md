# DELTA R017 — Ownership Branch Action Attribution Preregistration

**Status:** PREREGISTERED / NOT EXECUTED  
**Parent:** R016-T06  
**Scope:** ENTRY + INITIAL-HOLD / DIRECTION OWNERSHIP  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Frozen thresholds

- Base micro trigger: `I250 <= -0.55`
- Base H1 trigger: `H1NetATR > 0.35`
- Extreme dual: `H1NetATR > 0.70 AND I250 <= -0.90`
- Extreme dual action: `SKIP_CURRENT_M1` in every configuration

## Non-extreme branch classes

- MICRO_ONLY: micro base trigger only
- H1_ONLY: H1 base trigger only
- DUAL: both base triggers, not extreme dual
- NONE: neither; ordinary R9 remains frozen

## Actions

- KEEP: original R9 side + ordinary R9 rearm
- FLIP: reversed side + owned no-rearm
- SKIP: no entry + suppress rest of current M1

MICRO_ONLY, H1_ONLY and DUAL each take one of KEEP/FLIP/SKIP.

Total factorial: **27 configurations**.

R017-B14 = R016/T06 canonical control: FLIP / FLIP / FLIP, with extreme dual fixed SKIP.

## Evaluation

Primary surfaces: P50/P75/P90.  
Native: diagnostic only.

Floors:
- >=80% R9 trade retention
- >=80% R9 winner retention

Selection:
- non-dominated worst-surface net-loss, gross-loss and drawdown improvement
- no single net-profit argmax
- no threshold changes
- no post-result action invention
- exact Jan-Jul only for Stage-A survivors

## Drive

Prereg Doc:
https://docs.google.com/document/d/12KGv3-gEEbP5XgUWb1ZjKjpqKPICtsF8RTHTyscljG8/edit

Workbook tab:
`29 R017 Branch Prereg`

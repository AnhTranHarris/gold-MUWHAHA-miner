# DELTA R019 — DUAL Toxicity Harvest and Contextual KEEP Preregistration

**Status:** HARVEST COMPLETE / FOUR CONFIGURATIONS PREREGISTERED  
**Parent:** R016-T06 / R017-B14  
**Scope:** ENTRY + INITIAL-HOLD / DIRECTION OWNERSHIP  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Finding

P75 Stage-A DUAL harvest contains 754 events:
- 455 current T06 extreme skips
- 299 current non-extreme flips

Counterfactual FLIP mean:
- current extreme/skipped: -$0.1404
- current non-extreme/flipped: -$0.1981

The current extreme definition does not rank DUAL toxicity optimally.

## Offline chronological harvest

On non-extreme DUAL events:

`abs(H4NetATR)>1.0` -> KEEP instead of FLIP:
- train +$9.89
- validation +$4.31
- test +$1.07

`abs(H4NetATR)>1.0 OR M30NetATR<-1.0`:
- train +$10.10
- validation +$4.31
- test +$3.10

Outcome labels are offline-only and forbidden as live inputs.

## Frozen configurations

- C01: |H4|>1 -> KEEP + normal R9 rearm
- C02: |H4|>1 -> KEEP + owned no-rearm
- C03: |H4|>1 OR M30<-1 -> KEEP + normal R9 rearm
- C04: |H4|>1 OR M30<-1 -> KEEP + owned no-rearm

All other branches remain R016/T06.

Primary replay: P50/P75/P90. Native diagnostic only.

Advance only if:
- trade retention >=80% R9 on every modeled surface
- winner retention >=80% R9
- net beats T06 on all P50/P75/P90
- no >5% GL/DD deterioration vs T06
- no threshold changes after results

## Drive

https://docs.google.com/document/d/1HR7_ycMXib5tyJLPbnlX96VlcIjXDFK7mTfzFt80Wqo/edit

Workbook tabs:
- 31 R019 Dual Harvest
- 32 R019 Prereg
- 33 R019 Results

## Provenance

DUAL harvest SHA-256:
`a8a541651c82c3a3536b15334b179b0eb96662a54cb17b4bc07aae94e84ffac1`

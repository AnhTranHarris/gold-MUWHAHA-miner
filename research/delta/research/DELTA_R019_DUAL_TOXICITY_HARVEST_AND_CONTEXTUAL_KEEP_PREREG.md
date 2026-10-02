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

## Raw-tick replay result

All four frozen configurations were executed on P50/P75/P90 plus Native diagnostic without threshold or action changes.

- C01: fails because P90 net/gross loss deteriorate vs T06.
- C02: passes all modeled-surface gates.
- C03: fails because P90 net/gross loss deteriorate vs T06.
- C04: passes all gates and dominates C02 on P50/P75/P90.

### R019-C04 modeled-surface summary

| Surface | Trade ret. | Winner ret. | Δ Net vs T06 | Δ Net-loss % | Δ GL % | Δ DD % |
|---|---:|---:|---:|---:|---:|---:|
| P50 | 84.0367% | 88.8445% | +$18.15 | +0.6678% | +0.3083% | +0.6675% |
| P75 | 84.1557% | 89.3212% | +$17.37 | +0.5981% | +0.2787% | +0.5979% |
| P90 | 80.0067% | 83.4891% | +$7.78 | +1.3832% | +0.8001% | +1.3832% |

Native remains sparse/diagnostic; C04 improved T06 by $0.609 but absolute winner retention remains only 58.82%.

**Decision:** C04 is the sole R019 survivor and advances to exact Jan–Jul P75 monthly validation. No promotion, no metric lock.

## Result provenance

- execution script: `f4a6b87d9be11bab65aa8f11fc501df43526f59cc2c47c86bef553f9358ded11`
- P50: `291915f42fd48ae30de5bbad74bbc2113aecf9b607d8b8a605b71a3b888cf2fd`
- P75: `972d06a94f25cf51a546fb67de2f75001a44a96ebb7e7fa116eb01f2f7c0335b`
- P90: `9420bedc87fa6c89dcd5b341aa48ec983d11901d9702f9c16ab929e08fdd660d`
- Native: `3a268747bb207ac15bd12a6f68c25c99ba76f30b8a91c8926e2f3437a89e4dce`


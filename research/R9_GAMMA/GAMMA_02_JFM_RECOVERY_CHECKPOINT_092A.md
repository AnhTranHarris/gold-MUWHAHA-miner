# GAMMA-02 — J/F/M Recovery Checkpoint 092A

**Status:** RECOVERED FROM RUNTIME AFTER UI TIMEOUTS — DURABLE  
**Parent January candidate:** `GAMMA02_083_CHILD_CAP_703`  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## January frozen crossover

The exact January child-cap-703 candidate remains:
- +$48,766.62 net
- 32,862 trades
- PF 19,585.99
- win rate 99.9026%
- +$1.483982 expectancy/trade
- 14.6021s average hold
- exact tick-level equity DD $10,348.16
- min total equity $99,043.55 on $100K research balance

It crosses the exact January R9 SYNTH vector on all six target metrics.

## 088 — exact margin research model

Under the research assumption:
- XAUUSD contract size = 100 oz per 1.00 lot
- fixed ticket = 0.01
- leverage = 1:500

At 703 simultaneous tickets:
- maximum modeled margin: **$6,878.50**
- max margin / $100K initial balance: **6.8785%**
- approximate minimum margin level using certified minimum equity and maximum margin: **~1,439.9%**

This is operationally comfortable under the assumption, but exact Coinexx terminal symbol-spec confirmation remains required before MT5 deployment.

## Frozen February — no retuning

`GAMMA02_083_FROZEN_FEBRUARY_001`

- **+$52,960.14**
- 39,882 trades
- PF 12.2479
- win 98.3802%
- +$1.32792 expectancy
- 40.894s average hold
- equity DD $18,978.55
- minimum equity $99,043.55

February remains strongly profitable, but no longer crosses every R9-SYNTH January metric.

## Frozen March — regime failure

`GAMMA02_083_FROZEN_MARCH_001`

- **-$9,480.91**
- 6,727 trades
- PF 0.3376
- win 87.7806%
- -$1.40938 expectancy
- 257.23s average hold
- equity DD $11,361.05

March is the first genuine chronological failure and is retained as a hard regime test.

## 089 — J/F/M failure decomposition

The key difference is not merely direction. March still contains many nominally correct short parents, but the fast quantum renewal structure collapses:

January:
- early median hold ~0.97s; late median ~2.99s
- early quantum-like 26,345/26,453
- late quantum-like 22,796/23,013

February:
- early median ~0.97s; late ~3.64s
- quantum-like remains dominant

March:
- early median hold **8.83s**, p90 ~1,472s
- late median **28.88s**, p90 ~1,800s
- early nonquantum/losses 601
- late nonquantum/losses 221
- expectancy turns negative in both desks

This identifies a causal research target: detect whether a parent has entered the fast quantum-renewal regime **before** unleashing the full child swarm.

## 090 — parent ignition gate

A 2-second parent ignition test:
- Jan +$40,664 / 27,567 trades
- Feb +$42,205 / 30,612
- Mar **-$4,056 / 3,201**

It materially reduces March damage but gives up too much Jan/Feb capture.

## 091 — scout/unlock

A stricter 1-second scout:
- Jan +$13,444
- Feb +$13,244
- Mar **-$1,287**

Again, March damage is reduced, but the binary gate destroys too much profitable multiplicity.

## Current conclusion

Binary gate = rejected.

The next hypothesis is **staged ignition**:

1. open a small fixed scout tranche from an otherwise-qualified parent;
2. observe whether the first quantum renewals succeed within a short causal window;
3. if success rate / renewal count crosses a threshold, unlock the remaining child capacity immediately;
4. if not, stop after the small scout tranche;
5. no future information, no loss-dependent sizing, no averaging down.

Goal:
- preserve most January/February child multiplicity;
- sharply reduce March dead-regime exposure;
- retain fixed 0.01 ticket sizing.

## Exact durable recovery folder

Library:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/post-crossover-recovery/jfm-validation/`

Contains exact 088, frozen Feb/Mar, 089, 090 and 091 artifacts/helpers.

## Next unit

`GAMMA_02_STAGED_IGNITION_092`

No completed <=091 unit should be rerun.

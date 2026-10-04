# DELTA R037 — Lee–Mykland Jump Fade — Checkpoint 17AX

**Status:** COMPLETE / NO EXECUTABLE SURVIVOR / RETIRED  
**Parent:** R037_DCOS_STAGE_A_SCREEN_CHECKPOINT_17AW  
**August:** SEALED | **MQL5:** NOT AUTHORIZED

## Test

A single preregistered M1 Lee–Mykland jump detector was tested with **K=603**, a 1% Gumbel critical value **β=4.6001**, and one source-motivated profile only: **fade the completed jump sign** at the first executable P75 tick after the M1 close.

No K/significance/sampling-frequency sweep, continuation rescue, session/side filter, overlay, or exit tuning was allowed.

## Result

- completed M1 bars: **15,180**
- statistically extreme jumps: **58** (~4.14/day)
- distinct trading days: **13**
- trades: **58**
- official wins: **21**
- gross profit: **+$6.96**
- gross loss: **-$21.85**
- direct net: **-$15.47**
- exits: **58 STOP / 0 MAX_HOLD**
- median jump statistic: **7.9493**
- median absolute jump return: **16.37 bps**
- median inter-event gap: **2,880 s**

The family is sufficiently sparse and the jump magnitude is economically nontrivial, but immediate 30-second fade behavior does not survive the frozen P75 execution lifecycle.

## Integrity

- prereg commit: `d7896da5f43d146fe95c703013013ccebc4db87c`
- producer commit: `e2bb64c479e7d22cd24fedc34b1667328ebc6a14`
- producer blob: `f376dfecb4cbdbf08648cf74ec103400e04210f4`
- producer SHA-256: `fc7b7c8ae960d899dac018bd57898bc2bb7c617a60155e0ecd527eabf04d6104`
- official result SHA-256: `1a585c0d9240ca3eef67b7452fdf75bac1507b2b519085da82296a6d76f52380`
- canonical January hash/tick count PASS
- exact local Git blob verification PASS
- hard process timeout 120 s
- atomic result output PASS

## Decision

**RETIRE_LMJF_STAGE_A_NO_EXECUTABLE_SURVIVOR.**

Do not rescue with parameter or execution tuning.

**Next:** `R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`

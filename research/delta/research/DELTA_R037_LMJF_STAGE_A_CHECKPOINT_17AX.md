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

- prereg commit: `8acec24b7ccf3bbbf30f5733fe45ccefa3b73a83`
- producer commit: `9ef4e75f841371e2b32ee98e6322e2c12b7c3b24`
- producer blob: `ae777b4d6f4b7fa28dfcfed85634c0901848dd1e`
- producer SHA-256: `0a2acdb38a965836ab93e26c9780e1afa017a779e95f3aa331e24d5e4bde9e94`
- official result SHA-256: `243f27fc455a2da44329e4e4b769cc7b1e99f9e33bd3073ff77a78f0c85308d2`
- canonical January hash/tick count PASS
- exact local Git blob verification PASS
- hard process timeout 120 s
- atomic result output PASS

## Decision

**RETIRE_LMJF_STAGE_A_NO_EXECUTABLE_SURVIVOR.**

Do not rescue with parameter or execution tuning.

**Next:** `R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`

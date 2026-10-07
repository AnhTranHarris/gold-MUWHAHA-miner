# Gold MUWHAHA Miner — R9 STMR XMonth MT5 Certification

This branch is the **R9-rooted Coinexx certification build** for the Delta-A-alpha session/timeframe grid candidate.

## R9 control retained unchanged

- `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5`
- `Experts/GoldMuwahahaMiner_R9_TickLogger.mq5`

Branch parent: `carson/r9-tick-logger@23b85ca774efa43acbcb2006fc5e88ce5ac08bf0`.

## Candidate

`Experts/GoldMuwahahaMiner_R9_STMR_XMonth_001.mq5`

Candidate research identity: `STMR_XMONTH_SUBPHASE_001`.

The file contains explicit `[EDIT-00]` through `[EDIT-07]` maintenance markers so future repairs can be localized.

## First gate

Compile the candidate in MetaEditor and require **0 errors, 0 warnings**. A Windows helper is provided:

`tools/compile_r9_stmr.cmd`

Then run Coinexx Strategy Tester using **Every tick based on real ticks**.

Full instructions: `docs/R9_STMR_XMONTH_SUBPHASE_001_MT5_CERTIFICATION.md`.

Do not load an old R9 `.set` file into the STMR candidate. The scientific grid geometry is compiled into the EA; only clock/execution/diagnostic plumbing is exposed as inputs.

# R9 STMR XMonth 001 — Carson Maintenance Map

This file exists to prevent future repair work from mutating unrelated strategy behavior.

## Immutable lineage

- R9 parent branch: `carson/r9-tick-logger`
- R9 parent commit: `23b85ca774efa43acbcb2006fc5e88ce5ac08bf0`
- R9 control blob: `7eecb5f1947017a01ce85b2520725de54749e523`
- R9 logger blob: `5c7655cd3357f9126e8bffd97c34374dfb29f83e`
- STMR candidate file: `Experts/GoldMuwahahaMiner_R9_STMR_XMonth_001.mq5`
- STMR candidate blob at initial R9-root commit: `daa754c8fcd035915660ccc00274a6003d135ea9`

Do not edit the two historical R9 control files on this certification branch. Create a new child branch if R9 itself must change.

## EA edit markers

Search the candidate source for:

- `[EDIT-00]` — R9 lineage / certification identity.
- `[EDIT-01]` — server-time to UTC plumbing and frozen session windows.
- `[EDIT-02]` — completed-bar EMA engine.
- `[EDIT-03]` — lattice anchor, cell crossings and first-touch memory.
- `[EDIT-04]` — semantic sleeve classification, funded list and subphase gates.
- `[EDIT-05]` — TP/SL and 300-second lifecycle.
- `[EDIT-06]` — broker order execution and exact ticket binding.
- `[EDIT-07]` — decision logger / diagnostics.

## Change discipline

Changes under EDIT-01, EDIT-02, EDIT-03, EDIT-04 or EDIT-05 can alter research economics. Re-run the ordered-tick Python comparator before promoting them.

EDIT-06 may be changed for broker/API correctness only if the signal/lifecycle semantics remain unchanged. Any change in fill assumptions, stop anchoring, execution order, partial-fill behavior or position-cap semantics is scientific and needs re-certification.

EDIT-07 is diagnostic only; it must never control entries or exits.

## Deliberately absent legacy R9 mechanisms

Do not add these during the first certification:

- R9 minute bracket;
- R9 S1 velocity/efficiency/range gate;
- R9 ATR regime gate;
- R9 adaptive ATR thresholds;
- R9 trailing stop;
- R9 same-minute opposite rearm;
- R9 DST session router.

Those mechanisms remain available in the untouched R9 control. Adding them to STMR creates a new hybrid experiment.

## Failure flags

A scientifically usable run requires:

- `bindFail = 0`
- `volumeMismatch = 0`
- no order failures caused by unsupported broker stop geometry
- no non-hedging account rejection
- no position-cap breach above 3

If any flag is non-zero, diagnose execution before tuning the strategy.

## Rollback

The untouched R9 parent is always recoverable at:

`carson/r9-tick-logger@23b85ca774efa43acbcb2006fc5e88ce5ac08bf0`

The earlier Delta-A-rooted MT5 prototype remains forensic reference only:

`r9-stmr-xmonth-subphase-001-mt5-cert-20261006`

Do not use its branch ancestry as the R9 production lineage.

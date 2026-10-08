# Delta-A-alpha — Vertical Grid System V1 MT5 Unit 004
## Watchdog / Regime Renewal

**Status:** IMPLEMENTATION CONTRACT  
**Parent:** unit 003 hourly/Asia route proposals  
**Execution:** observe-only campaign/admission state

## Objective

Port the causal Watchdog-119 campaign-admission mechanics into the V1 EA without enabling funded orders.

## Frozen mechanics

Watchdog parent cells are keyed by:
- UTC day;
- New York local hour;
- New York local 10-minute subphase;
- completed H4/H1/M15/M5 state;
- crossing direction.

Eligibility:
- H4/H1 aligned and non-flat;
- crossing direction aligned with H4;
- New York local hour 12 or 13.

Admission:
1. first parent in a cell is the scout and is admitted;
2. later parents remain locked;
3. four consecutive already-realized renewal outcomes with PnL > 0 and hold <= 60s unlock the cell;
4. a losing or slow realized renewal resets streak and immediately relocks.

Renewal geometry:
- 10-minute bins 0-4: 1.19 price units;
- bin 5: 1.10;
- default max renewal layer: 30.

Unit 004 does not manufacture or execute renewal children yet. It provides the durable causal state and the outcome-update API that later lifecycle/execution units will call.

## Causality

Only realized outcomes may change gate state.
No future hold/PnL/MFE/MAE is available at parent admission.
Month/date labels are not strategy inputs.

## Acceptance

- exact scout/unlock/relock semantics;
- exact NY-local 12-13 window;
- DST-aware NY-local conversion;
- exact 1.19/1.10 subphase geometry;
- state attached to the originating genealogy event;
- no order-send path;
- deterministic CI QA pass.

## Next unit

`DAA_VERTICAL_GRID_SYSTEM_V1_MT5_NATIVE_ROUTING_AND_RECOVERY_005`

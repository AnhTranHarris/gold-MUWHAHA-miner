# Delta-A-alpha — Vertical Grid System V1 MT5 Skeleton Certification 007

**Status:** CERTIFICATION CONTRACT  
**Scope:** units 001-006 as one coherent observe-only MT5 decision skeleton  
**Economic claim:** NONE  
**MetaEditor compile:** still required after this certification

## Certification objective

Verify that the current EA contains the complete frozen V1 decision spine in the correct order:

1. ordered tick / historical clock normalization;
2. session-specific grid geometry;
3. finite session-local lattice + event genealogy;
4. completed H4/H1/M15/M5 birth state;
5. Asia vs London/overlap/NY route proposals;
6. Watchdog/regime renewal state;
7. trend-within-trend native classification;
8. bounded wrong-direction recovery shadow;
9. proposal arbitration;
10. global/session/layer heat governance;
11. deterministic diagnostics.

## Hard safety conditions

- fixed 0.01 lot default/enforcement;
- no Martingale;
- no loss-dependent sizing;
- no order-send path;
- execution input default false;
- month/date labels not used as strategy inputs;
- August remains sealed in project governance.

## CI

The certification workflow runs:
- unit 001 architecture QA;
- unit 002 session/genealogy QA;
- unit 003 hourly/Asia route QA;
- unit 004 Watchdog QA;
- unit 005 native/recovery QA;
- unit 006 arbiter/heat QA;
- aggregate skeleton QA.

## Pass meaning

A pass means the **decision skeleton** is internally consistent and crash-recoverable.

It does NOT mean:
- MQL5 compilation has been proven;
- MT5 execution parity has been proven;
- Jan-Jul economics have been reproduced in MT5;
- broker/live deployment is authorized.

## Next unit after PASS

`DAA_VERTICAL_GRID_SYSTEM_V1_MT5_METAEDITOR_COMPILE_AND_PARITY_008`

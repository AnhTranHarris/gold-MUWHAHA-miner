# Delta-A-alpha — Vertical Grid System V1 MT5 Unit 008
## MetaEditor Compile and Python↔MT5 Diagnostic Parity

**Status:** NEXT ENGINEERING GATE  
**Frozen skeleton:** `delta-A-alpha-v1-mt5-skeleton-certified`  
**Frozen skeleton commit:** `c81539633a0becc0dfe053f84ef80e6462848cd5`  
**EA:** `Experts/GoldMuwahahaMiner_DeltaAAlpha_V1.mq5`

## Purpose

Certify the already-built V1 decision skeleton before Jan–Jul strategy tuning.

No alpha change is permitted in this unit.

## Gate A — MetaEditor compilation

Required:
- compile the exact frozen skeleton source;
- zero compile errors;
- every warning reviewed and recorded;
- no strategy logic edits while repairing syntax/build issues;
- any required build-only repair must be documented and regression-checked against the frozen skeleton.

## Gate B — deterministic diagnostic replay

Run the EA in Strategy Tester with order execution still disabled.

At minimum compare representative windows from:
- Asia;
- London;
- overlap;
- New York;
- late New York;
- a session handoff;
- a Watchdog scout/unlock/relock sequence where reproducible;
- a failed-ignition recovery observation where reproducible.

Compare MT5 diagnostic rows against Python reference for:

1. server-time -> UTC normalization;
2. session classification;
3. session gap/geometry;
4. completed H4/H1/M15/M5 state;
5. cycle generation/restart reason;
6. grid cell crossing;
7. event ID ordering / one-event-per-tick behavior;
8. duplicate suppression;
9. route ID/direction/hour/subphase;
10. Watchdog cell/scout/admission/gate/streak/renewal gap;
11. native mode/direction;
12. recovery-watch start/failure/opposite proposal;
13. arbiter owners/direction/conflict;
14. global/session/layer governor reason.

## Gate C — parity tolerances

Categorical states must match exactly.

Timestamp:
- exact UTC millisecond where the source tick permits;
- no session/hour/subphase mismatch is acceptable.

Price:
- use broker tick-size normalization;
- any tolerated difference must be documented before economics are interpreted.

## Gate D — no execution authority

Unit 008 remains observe-only.
No Buy/Sell/PositionOpen path may be added.

## Pass condition

Only after compile + diagnostic parity pass may the project begin the Jan–Jul V2/V3 refinement campaign on top of V1.

The tuning campaign may adjust layer mechanics/parameters but must preserve:
- V1 fallback branch;
- V1 vertical order;
- month/date labels as evaluation-only;
- fixed 0.01 research lot;
- no Martingale/loss-dependent sizing;
- August sealed unless owner explicitly changes scope.

## After parity

Recommended next scientific campaign:

`DAA_VERTICAL_GRID_SYSTEM_V2_JAN_JUL_MONTHLY_REFINEMENT_001`

That campaign should tune month-by-month while repeatedly replaying all previously accepted months, with later small-capital survivability added as a separate versioned layer.

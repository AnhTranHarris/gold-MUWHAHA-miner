# Delta-A-alpha — Vertical Grid System V1 MT5 Implementation 001 Report

**Status:** COMPLETE ENGINEERING SHELL / STATIC CONTRACT VERIFIED  
**EA:** `Experts/GoldMuwahahaMiner_DeltaAAlpha_V1.mq5`  
**Economic claim:** NONE  
**Order-send path:** NONE in unit 001  
**MetaEditor compile:** PENDING owner/local or future compiler environment

## What unit 001 establishes

The MQL5 source now carries the V1 orchestration order as code:

1. ordered tick / Coinexx historical server→UTC normalization;
2. session-specific grid geometry;
3. completed H4/H1/M15/M5 EMA state using shift 1 only;
4. London/overlap/New York high-volume layer interface plus separate Asia geometry;
5. Watchdog/regime interface;
6. trend-within-trend routing interface;
7. wrong-direction recovery interface;
8. account-level heat/capital governor;
9. deterministic CSV diagnostics.

The unit is deliberately observe-only. It cannot place a trade even if `InpExecutionEnabled` is changed, because no Buy/Sell/PositionOpen call exists yet.

## Safety contract

- fixed 0.01 lot is enforced at initialization;
- no Martingale;
- no loss-dependent sizing;
- no unbounded averaging;
- global max-position input is present before execution exists;
- completed-bar MTF state is separated from tick execution;
- session/DST clock normalization is explicit and logged.

## Static QA

Readback static QA passed:
- all required layer functions present;
- orchestration order correct;
- no order-send functions present;
- V1 manifest starts at ordered ticks and ends at portfolio heat/capital governor;
- MT5 authorization is recorded in the V1 manifest.

This does not substitute for MetaEditor compilation.

## Next unit

`DAA_VERTICAL_GRID_SYSTEM_V1_MT5_SESSION_GEOMETRY_AND_EVENT_GENEALOGY_002`

The next unit ports:
- session-local anchors;
- finite lattice/cycle ownership;
- first-touch event genealogy;
- one supplemental physical proposal per tick;
- observe-only London-open/rollover behavior;
- exact session-specific geometry interfaces.

No hourly high-volume or recovery layer may send orders until this lower layer passes parity.

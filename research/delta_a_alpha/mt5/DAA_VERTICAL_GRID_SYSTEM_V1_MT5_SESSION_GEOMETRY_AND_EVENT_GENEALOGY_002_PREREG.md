# Delta-A-alpha — Vertical Grid System V1 MT5 Unit 002
## Session Geometry and Event Genealogy

**Status:** IMPLEMENTATION CONTRACT  
**EA:** `Experts/GoldMuwahahaMiner_DeltaAAlpha_V1.mq5`  
**Execution:** observe-only; no order-send path  
**Parent:** `DAA_VERTICAL_GRID_SYSTEM_V1_MT5_IMPLEMENTATION_001`

## Objective

Port the first profit-bearing system prerequisite without yet enabling orders:

```text
ordered tick
→ session-specific geometry
→ finite session-local cycle
→ first-touch event genealogy
→ completed H4/H1/M15/M5 birth snapshot
```

The output of unit 002 is a deterministic stream of owned grid events that later
hourly/Watchdog/native/recovery layers can route.

## Required mechanics

### Session-local lattice
Base V1 geometry:
- Asia: $0.75
- London: $1.00
- overlap: $0.75
- New York: $1.50
- late New York: $0.50
- London open: observe-only base geometry
- rollover: observe-only

Each active session/cycle owns its own anchor and gap.

### Finite ownership
A new cycle is created on:
1. initial startup;
2. session handoff;
3. geometry change;
4. maximum configured cycle age.

A cycle restart clears first-touch ownership and the active genealogy.

### First-touch genealogy
A crossing can manufacture at most one supplemental session-grid event per market tick.

The event records:
- unique event ID;
- cycle generation;
- birth UTC milliseconds;
- session;
- prior cell;
- crossed cell;
- landing cell;
- crossing direction;
- crossed boundary;
- completed H4/H1/M15/M5 state at birth.

Recrossing the same owned cell in the same direction during the same cycle is a duplicate and does not create another event.

If a single market tick jumps multiple cells, unit 002 records only the first crossed
boundary. It does not retroactively manufacture the skipped cells.

### Causality
- completed timeframe states use shift 1 only;
- month/date/week labels are not execution inputs;
- no future outcome is consulted;
- no order is opened in unit 002.

## Acceptance

Unit 002 passes only if:
- V1 source order remains intact;
- session cycle restart is explicit;
- first-touch ownership is explicit;
- event birth snapshots are durable in active memory and diagnostics;
- one-event-per-tick rule is explicit;
- no Buy/Sell/PositionOpen path exists;
- deterministic reference QA passes.

## Next unit

`DAA_VERTICAL_GRID_SYSTEM_V1_MT5_HOURLY_HARVEST_AND_ASIA_GEOMETRY_003`

That unit may consume unit-002 events but still must pass parity before funded execution is enabled.
